# -*- coding: utf-8 -*-
"""
Voice API Routes — FastAPI 语音控制路由
GET  /api/v1/voice/speak       — TTS 语音合成
POST /api/v1/voice/recognize   — 语音识别（Whisper）
POST /api/v1/voice/execute      — 语音 → 识别 → 理解 → 执行
GET  /api/v1/voice/sessions     — 活跃会话列表
POST /api/v1/voice/sessions/{user_id} — 创建/续期会话
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional
import io

from .auth import require_permission

# ─────────────────────────────────────────────
# Pydantic 模型
# ─────────────────────────────────────────────

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"       # alloy / echo / fable / onyx / nova / shimmer
    model: Optional[str] = "tts-1"
    speed: Optional[float] = 1.0


class TTSResponse(BaseModel):
    audio_b64: str
    format: str = "mp3"
    duration_sec: Optional[float] = None


class RecognizeRequest(BaseModel):
    audio_b64: str
    provider: Optional[str] = "whisper_api"  # whisper_api / whisper_local


class RecognizeResponse(BaseModel):
    text: str
    provider: str
    confidence: float = 1.0
    wake_word_detected: bool = False
    stripped_text: Optional[str] = None


class ExecuteRequest(BaseModel):
    text: Optional[str] = None       # 文本命令（直接执行）
    audio_b64: Optional[str] = None  # 或上传音频
    user_id: Optional[str] = None    # 微信/钉钉 openid


class ExecuteResponse(BaseModel):
    status: str                       # task_spawned / ignored / ready / error
    intent: str
    confidence: float
    task_id: Optional[str]
    text: str
    tts_available: bool = False


# ─────────────────────────────────────────────
# 路由注册
# ─────────────────────────────────────────────

def register_voice_blueprint(
    router: APIRouter,
    get_voice_handler,
    get_nl_interpreter,
    get_openclaw_client,
):
    """
    注册语音路由
    由 server.py 在启动时调用，注入依赖获取器
    """

    # ── TTS ──────────────────────────────────
    @router.post("/api/v1/voice/speak", response_model=TTSResponse)
    async def tts_speak(
        req: TTSRequest,
        _: dict = Depends(require_permission("READWRITE")),
    ):
        """
        文字转语音（Text-to-Speech）
        返回 MP3 音频 Base64
        """
        voice_handler = get_voice_handler()
        if not voice_handler:
            raise HTTPException(503, "Voice handler not configured")

        try:
            if hasattr(voice_handler.config, "tts_api_key"):
                voice_handler.config.tts_voice = req.voice or voice_handler.config.tts_voice
                voice_handler.config.tts_model = req.model or voice_handler.config.tts_model

            audio_bytes = await voice_handler.speak_async(req.text)
            import base64
            audio_b64 = base64.b64encode(audio_bytes).decode()

            return TTSResponse(
                audio_b64=audio_b64,
                format="mp3",
            )
        except Exception as e:
            raise HTTPException(500, f"TTS failed: {e}")

    # ── 语音识别 ──────────────────────────────
    @router.post("/api/v1/voice/recognize", response_model=RecognizeResponse)
    async def voice_recognize(
        req: RecognizeRequest,
        _: dict = Depends(require_permission("READWRITE")),
    ):
        """
        语音识别（STT），支持 Whisper API / 本地 Whisper
        """
        voice_handler = get_voice_handler()
        if not voice_handler:
            raise HTTPException(503, "Voice handler not configured")

        try:
            import base64
            audio_data = base64.b64decode(req.audio_b64)
            command = voice_handler.recognize(audio_data)

            wake_word_ok = voice_handler.detect_wake_word(command.text)
            stripped = voice_handler.strip_wake_word(command.text) if wake_word_ok else command.text

            return RecognizeResponse(
                text=command.text,
                provider=command.provider,
                confidence=command.confidence,
                wake_word_detected=wake_word_ok,
                stripped_text=stripped if wake_word_ok else None,
            )
        except Exception as e:
            raise HTTPException(500, f"Recognition failed: {e}")

    # ── 语音执行 ─────────────────────────────
    @router.post("/api/v1/voice/execute", response_model=ExecuteResponse)
    async def voice_execute(
        req: ExecuteRequest,
        _: dict = Depends(require_permission("READWRITE")),
    ):
        """
        语音命令 → 识别 → 自然语言解析 → 执行任务
        支持纯文本或音频 Base64
        """
        voice_handler = get_voice_handler()
        nl = get_nl_interpreter()
        client = get_openclaw_client()

        try:
            # 从文本或音频获取命令
            if req.text:
                command = voice_handler.recognize(
                    req.text.encode("utf-8"), filename="text.txt"
                ) if False else None  # 跳过，直接用文本
                # 文本直接构建 VoiceCommand
                from .voice_handler import VoiceCommand
                cmd = VoiceCommand(text=req.text, provider="text_input")
            elif req.audio_b64:
                import base64
                audio_data = base64.b64decode(req.audio_b64)
                cmd = voice_handler.recognize(audio_data)
            else:
                raise HTTPException(400, "Either 'text' or 'audio_b64' required")

            # 创建/续期会话
            user_id = req.user_id or "default"
            voice_handler.touch_session(user_id)

            # 执行
            result = voice_handler.execute(
                command=cmd,
                nl_interpreter=nl,
                openclaw_client=client,
            )

            return ExecuteResponse(
                status=result.get("status", "unknown"),
                intent=result.get("intent", "unknown"),
                confidence=result.get("confidence", 0.0),
                task_id=result.get("task_id"),
                text=cmd.text,
                tts_available=bool(voice_handler.config.tts_api_key),
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Voice execute failed: {e}")

    # ── 会话管理 ──────────────────────────────
    @router.get("/api/v1/voice/sessions")
    async def list_sessions(
        _: dict = Depends(require_permission("ADMIN")),
    ):
        """列出活跃会话（Admin）"""
        voice_handler = get_voice_handler()
        if not voice_handler:
            return {"sessions": []}
        return {"sessions": voice_handler._sessions}

    @router.post("/api/v1/voice/sessions/{user_id}")
    async def touch_session(
        user_id: str,
        _: dict = Depends(require_permission("READWRITE")),
    ):
        """创建或续期用户会话"""
        voice_handler = get_voice_handler()
        if not voice_handler:
            raise HTTPException(503, "Voice handler not configured")
        session = voice_handler.create_session(user_id)
        return {"user_id": user_id, "session": session}

    return router
