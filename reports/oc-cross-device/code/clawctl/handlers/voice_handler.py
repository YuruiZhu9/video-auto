# -*- coding: utf-8 -*-
"""
Voice Handler — 语音控制模块
支持多种语音输入后端：Whisper（本地）/ 微信语音 / 系统 TTS

功能：
- 语音 → 文本（STT）via Whisper API / OpenAI Whisper / 微信 Recognition
- 自然语言解析（复用 NLInterpreter）
- 命令执行 + 结果语音播报（TTS）
- 流式音频响应（WebRTC / PCM）
"""

import base64
import hashlib
import json
import threading
import time
import wave
import io
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    import requests


class VoiceProvider(Enum):
    WHISPER_API = "whisper_api"       # OpenAI Whisper API
    WHISPER_LOCAL = "whisper_local"   # 本地 Whisper 模型
    WECHAT = "wechat"                 # 微信语音识别（已集成在 wechat_handler）
    GOOGLE_TTS = "google_tts"         # Google TTS
    WECHAT_TTS = "wechat_tts"         # 微信 TTS


@dataclass
class VoiceCommand:
    """语音命令结构"""
    text: str                    # 识别出的文本
    provider: str                # 识别后端
    confidence: float = 1.0      # 置信度
    intent: str = ""             # 解析出的意图
    params: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)   # 原始响应


@dataclass
class VoiceConfig:
    """语音配置"""
    provider: str = VoiceProvider.WHISPER_API.value
    whisper_api_key: str = ""
    whisper_model: str = "whisper-1"
    whisper_base_url: str = "https://api.openai.com/v1"

    # TTS 配置
    tts_provider: str = "openai"
    tts_api_key: str = ""
    tts_model: str = "tts-1"
    tts_voice: str = "alloy"

    # Whisper 本地模型（使用 faster-whisper 或 openai-whisper）
    whisper_local_model: str = "base"

    # 关键词触发（用于本地唤醒词，如 "小M"）
    wake_word: str = "小M"
    wake_word_timeout: float = 10.0   # 唤醒词检测超时（秒）


class VoiceHandler:
    """
    统一语音控制处理器

    使用方式：
    ---------
    # 方式1：Whisper API 语音识别
    handler = VoiceHandler(config=VoiceConfig(
        provider="whisper_api",
        whisper_api_key="sk-xxx",
    ))
    result = handler.recognize_from_file("voice.wav")
    handler.execute(result, nl_interpreter=my_nl)

    # 方式2：微信语音（配合 WeChatHandler 使用）
    # 微信已内置语音识别，直接将 msg.recognition 传入
    result = VoiceCommand(text=msg.recognition, provider="wechat")
    handler.execute(result, nl_interpreter=my_nl)

    # 方式3：本地 Whisper（离线可用）
    handler = VoiceHandler(config=VoiceConfig(
        provider="whisper_local",
        whisper_local_model="base",
    ))

    # TTS 语音播报结果
    audio = handler.speak("任务已完成，正在通知你...")
    """

    def __init__(
        self,
        config: Optional[VoiceConfig] = None,
        nl_interpreter: Optional[Callable] = None,
        openclaw_client: Optional[object] = None,
        on_result_callback: Optional[Callable] = None,
    ):
        self.config = config or VoiceConfig()
        self._nl = nl_interpreter
        self._client = openclaw_client
        self._on_result = on_result_callback

        # 活跃会话（openid → 唤醒状态）
        self._sessions: dict[str, dict] = {}
        self._sessions_lock = threading.Lock()

    # ─────────────────────────────────────────────
    # 语音识别（STT）
    # ─────────────────────────────────────────────

    def recognize(self, audio_data: bytes, filename: str = "audio.wav") -> VoiceCommand:
        """
        通用识别入口：根据配置的后端自动选择识别方式

        Args:
            audio_data: WAV/PCM/MP3 原始音频字节
            filename: 文件名（用于 API 识别）

        Returns:
            VoiceCommand：识别结果
        """
        provider = self.config.provider

        if provider == VoiceProvider.WHISPER_API.value:
            return self._recognize_whisper_api(audio_data, filename)
        elif provider == VoiceProvider.WHISPER_LOCAL.value:
            return self._recognize_whisper_local(audio_data)
        else:
            raise ValueError(f"Unknown voice provider: {provider}")

    def recognize_from_file(self, path: str) -> VoiceCommand:
        """从文件路径识别（本地文件）"""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")
        return self.recognize(p.read_bytes(), filename=str(p.name))

    def recognize_from_base64(self, b64_audio: str) -> VoiceCommand:
        """从 Base64 编码的音频识别"""
        data = base64.b64decode(b64_audio)
        return self.recognize(data, filename="audio.b64")

    def _recognize_whisper_api(
        self, audio_data: bytes, filename: str
    ) -> VoiceCommand:
        """通过 OpenAI Whisper API 识别"""
        api_key = self.config.whisper_api_key
        if not api_key:
            raise ValueError("whisper_api_key is required")

        url = f"{self.config.whisper_base_url.rstrip('/')}/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}

        files = {
            "file": (filename, io.BytesIO(audio_data), "audio/wav"),
        }
        data = {"model": self.config.whisper_model, "language": "zh"}

        if HAS_HTTPX:
            import asyncio
            raise RuntimeError(
                "Use recognize_whisper_api_async() for async usage, "
                "or ensure requests is available"
            )
        else:
            resp = requests.post(
                url, headers=headers, files=files, data=data, timeout=30
            )

        if resp.status_code != 200:
            raise RuntimeError(f"Whisper API error: {resp.status_code} {resp.text}")

        result = resp.json()
        return VoiceCommand(
            text=result.get("text", "").strip(),
            provider=VoiceProvider.WHISPER_API.value,
            confidence=result.get("confidence", 1.0),
            raw=result,
        )

    async def _recognize_whisper_api_async(
        self, audio_data: bytes, filename: str
    ) -> VoiceCommand:
        """异步识别（httpx）"""
        api_key = self.config.whisper_api_key
        url = f"{self.config.whisper_base_url.rstrip('/')}/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}

        files = {
            "file": (filename, io.BytesIO(audio_data), "audio/wav"),
        }
        data = {"model": self.config.whisper_model, "language": "zh"}

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, files=files, data=data)

        if resp.status_code != 200:
            raise RuntimeError(f"Whisper API error: {resp.status_code} {resp.text}")

        result = resp.json()
        return VoiceCommand(
            text=result.get("text", "").strip(),
            provider=VoiceProvider.WHISPER_API.value,
            confidence=result.get("confidence", 1.0),
            raw=result,
        )

    def _recognize_whisper_local(self, audio_data: bytes) -> VoiceCommand:
        """本地 Whisper 识别（需安装 faster-whisper 或 whisper）"""
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            try:
                import whisper
            except ImportError:
                raise ImportError(
                    "Local Whisper not available. "
                    "Install: pip install faster-whisper  or  pip install openai-whisper"
                )

        model_name = self.config.whisper_local_model

        # 写入临时文件（Whisper 需要文件路径）
        tmp = f"/tmp/voice_{int(time.time()*1000)}.wav"
        Path(tmp).write_bytes(audio_data)

        try:
            if "faster_whisper" in dir():
                model = WhisperModel(model_name, compute_type="int8")
                segments, _ = model.transcribe(tmp, language="zh")
                text = " ".join(seg.text for seg in segments)
            else:
                model = whisper.load_model(model_name)
                result = whisper.transcribe(model, tmp, language="zh")
                text = result["text"]
        finally:
            Path(tmp).unlink(missing_ok=True)

        return VoiceCommand(
            text=text.strip(),
            provider=VoiceProvider.WHISPER_LOCAL.value,
            confidence=1.0,
        )

    # ─────────────────────────────────────────────
    # 唤醒词检测
    # ─────────────────────────────────────────────

    def detect_wake_word(self, text: str) -> bool:
        """
        检测文本是否包含唤醒词
        支持中英文唤醒词 + 模糊匹配
        """
        if not self.config.wake_word:
            return True  # 无唤醒词配置，直接通过
        ww = self.config.wake_word.lower()
        t = text.lower().strip()

        # 精确匹配 / 前缀匹配（"小M帮我..."）
        if ww in t or t.startswith(ww):
            return True

        # 去掉标点再试
        import re
        t_clean = re.sub(r"[^\w\u4e00-\u9fff]", "", t)
        ww_clean = re.sub(r"[^\w\u4e00-\u9fff]", "", ww)
        return ww_clean in t_clean or t_clean.startswith(ww_clean)

    def strip_wake_word(self, text: str) -> str:
        """从文本中移除唤醒词"""
        ww = self.config.wake_word.lower()
        t = text.lower().strip()
        import re
        t_clean = re.sub(r"[^\w\u4e00-\u9fff]", "", t)
        ww_clean = re.sub(r"[^\w\u4e00-\u9fff]", "", ww)

        if ww_clean in t_clean:
            result = t_clean.replace(ww_clean, "").strip()
            return text[len(ww):].strip() if text.lower().startswith(ww) else result
        return text

    # ─────────────────────────────────────────────
    # 命令执行
    # ─────────────────────────────────────────────

    def execute(
        self,
        command: VoiceCommand,
        nl_interpreter: Optional[Callable] = None,
        openclaw_client: Optional[object] = None,
    ) -> dict:
        """
        执行语音命令：解析意图 → 执行 → 记录

        Args:
            command: VoiceCommand 识别结果
            nl_interpreter: 自然语言解析器
            openclaw_client: OpenClaw 客户端

        Returns:
            执行结果 dict
        """
        nl = nl_interpreter or self._nl
        client = openclaw_client or self._client

        text = command.text

        # 唤醒词检测
        if not self.detect_wake_word(text):
            return {
                "status": "ignored",
                "reason": "wake_word_not_detected",
                "text": text,
            }

        # 去掉唤醒词
        text = self.strip_wake_word(text)
        if not text:
            return {
                "status": "ignored",
                "reason": "empty_after_strip",
                "text": command.text,
            }

        # 自然语言解析
        if nl:
            parsed = nl(text) if callable(nl) else nl.parse_natural_command(text)
            intent = parsed.get("intent", "unknown")
            params = parsed.get("params", {})
            confidence = parsed.get("confidence", 1.0)
        else:
            intent = "unknown"
            params = {}
            confidence = 1.0

        # 状态/帮助类：直接返回（不触发 agent）
        if intent in ("status", "help"):
            return {
                "status": "ready",
                "intent": intent,
                "confidence": confidence,
                "response": "直接响应",
                "text": text,
            }

        # 触发 OpenClaw
        task_id = f"voice-{int(time.time())}"
        try:
            if client:
                client.spawn_agent(
                    task=parsed.get("description", text),
                    source="voice",
                    task_id=task_id,
                    params=params,
                )
        except Exception as e:
            return {"status": "error", "error": str(e), "text": text}

        result = {
            "status": "task_spawned",
            "intent": intent,
            "confidence": confidence,
            "task_id": task_id,
            "text": text,
            "params": params,
        }

        if self._on_result:
            try:
                self._on_result(result)
            except Exception:
                pass

        return result

    # ─────────────────────────────────────────────
    # TTS 语音合成
    # ─────────────────────────────────────────────

    def speak(self, text: str) -> bytes:
        """
        文本转语音（TTS），返回 WAV 格式音频字节

        Returns:
            WAV 音频字节数据
        """
        provider = self.config.tts_provider

        if provider == "openai":
            return self._speak_openai(text)
        elif provider == "google":
            return self._speak_google(text)
        elif provider == "wechat":
            # 微信 TTS（需企业号权限）
            return self._speak_wechat_tts(text)
        else:
            raise ValueError(f"Unknown TTS provider: {provider}")

    def _speak_openai(self, text: str) -> bytes:
        """OpenAI TTS → 返回 WAV"""
        api_key = self.config.tts_api_key
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.config.tts_model,
            "voice": self.config.tts_voice,
            "input": text[:1000],  # TTS 限制
        }

        if HAS_HTTPX:
            import asyncio
            raise RuntimeError("Use speak_async() for async usage")
        else:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)

        if resp.status_code != 200:
            raise RuntimeError(f"TTS API error: {resp.status_code} {resp.text}")

        # OpenAI 返回 mp3，需要转 WAV
        mp3_data = resp.content
        return self._mp3_to_wav(mp3_data)

    async def speak_async(self, text: str) -> bytes:
        """异步 TTS"""
        import asyncio
        provider = self.config.tts_provider
        if provider != "openai":
            return self.speak(text)

        api_key = self.config.tts_api_key
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.config.tts_model,
            "voice": self.config.tts_voice,
            "input": text[:1000],
            "response_format": "mp3",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=payload)

        if resp.status_code != 200:
            raise RuntimeError(f"TTS API error: {resp.status_code} {resp.text}")

        return self._mp3_to_wav(resp.content)

    def _speak_google(self, text: str) -> bytes:
        """Google TTS → WAV"""
        try:
            from gtts import gTTS
        except ImportError:
            raise ImportError("pip install gtts")

        mp3_io = io.BytesIO()
        tts = gTTS(text=text, lang="zh")
        tts.write_to_fp(mp3_io)
        mp3_io.seek(0)
        return self._mp3_to_wav(mp3_io.read())

    def _speak_wechat_tts(self, text: str) -> bytes:
        """
        微信 TTS（需微信提供 TTS 能力，或使用企业版接口）
        这里用讯飞/百度 TTS 作为替代方案
        """
        # 暂用系统 say 命令（macOS）或外部 TTS API
        raise NotImplementedError(
            "WeChat TTS requires third-party integration. "
            "Use openai or google TTS instead."
        )

    @staticmethod
    def _mp3_to_wav(mp3_data: bytes) -> bytes:
        """MP3 → WAV 转换（需 pydub）"""
        try:
            from pydub import AudioSegment
        except ImportError:
            # 无 pydub：直接返回 mp3 bytes（播放器可识别）
            return mp3_data

        audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        return wav_io.getvalue()

    # ─────────────────────────────────────────────
    # 会话管理（多用户）
    # ─────────────────────────────────────────────

    def create_session(self, user_id: str, metadata: dict = None) -> dict:
        """创建语音会话"""
        with self._sessions_lock:
            self._sessions[user_id] = {
                "created_at": time.time(),
                "last_active": time.time(),
                "wake_word_active": False,
                "metadata": metadata or {},
            }
        return self._sessions[user_id]

    def get_session(self, user_id: str) -> Optional[dict]:
        return self._sessions.get(user_id)

    def touch_session(self, user_id: str):
        """更新会话活跃时间（超时清理）"""
        with self._sessions_lock:
            if user_id in self._sessions:
                self._sessions[user_id]["last_active"] = time.time()

    def cleanup_stale_sessions(self, max_age_seconds: float = 3600):
        """清理过期会话"""
        now = time.time()
        with self._sessions_lock:
            stale = [k for k, v in self._sessions.items()
                     if now - v["last_active"] > max_age_seconds]
            for k in stale:
                del self._sessions[k]
            return len(stale)
