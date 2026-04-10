#!/usr/bin/env python3
"""
video/whisper_subtitle.py
=========================
用 OpenAI Whisper API（或本地 whisper-ctranslate2）生成精准 SRT 字幕。
替代 scene_detector.py 的视觉+音频信号时间轴，提升字幕准确率。

Usage:
    from whisper_subtitle import generate_srt
    generate_srt("input.mp4", "output.srt", model="base")

    # CLI
    python whisper_subtitle.py --input input.mp4 --output output.srt --model base
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# ── SRT format helper ──────────────────────────────────────────────────────

def format_timestamp(seconds: float) -> str:
    """将秒数转换为 SRT 时间码格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments: list, output_path: str):
    """将 Whisper 段落写入 SRT 文件（与 scene_detector.py 格式完全兼容）"""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")


# ── Audio extraction ────────────────────────────────────────────────────────

def extract_audio(video_path: str, audio_path: str = None) -> str:
    """从视频提取音频（临时文件）"""
    if audio_path is None:
        audio_path = tempfile.mktemp(suffix=".wav")
    # 优先用 FFmpeg，其次 moviepy
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
             "-ar", "16000", "-ac", "1", audio_path],
            check=True, capture_output=True
        )
        return audio_path
    except FileNotFoundError:
        pass  # FFmpeg 不可用，尝试 moviepy
    try:
        import moviepy.editor as mp
        audio = mp.AudioFileClip(video_path)
        audio.write_audiofile(audio_path, codec='pcm_s16le', fps=16000, nbytes=2)
        return audio_path
    except Exception as e:
        raise RuntimeError(f"无法从视频提取音频（ffmpeg/moviepy 均不可用）: {e}")


# ── Whisper API ────────────────────────────────────────────────────────────

def transcribe_with_api(audio_path: str, api_key: str, model: str = "whisper-1",
                         language: str = "zh") -> list:
    """调用 OpenAI Whisper API（$0.006/分钟，便宜）"""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("请安装 openai: pip install openai")

    client = OpenAI(api_key=api_key)
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model=model,
            file=f,
            response_format="verbose_json",
            language=language,
        )
    # 转换 OpenAI verbose_json 格式 → 统一段落格式
    segments = []
    for seg in getattr(transcript, "segments", []):
        segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text,
        })
    # 如果没有 segments 字段（兼容旧接口）
    if not segments and hasattr(transcript, "text"):
        segments.append({
            "start": 0.0,
            "end": 30.0,
            "text": transcript.text,
        })
    return segments


# ── Local Whisper ──────────────────────────────────────────────────────────

def transcribe_locally(audio_path: str, model: str = "base",
                       language: str = "zh") -> list:
    """使用本地 whisper-ctranslate2 模型（免费，需 pip install whisper-ctranslate2）"""
    try:
        from whisper_ctranslate2 import WhisperCTTranslate2
    except ImportError:
        raise RuntimeError(
            "本地 Whisper 不可用，请安装: pip install whisper-ctranslate2\n"
            "或设置环境变量 OPENAI_API_KEY 使用云端 Whisper API"
        )

    whisper = WhisperCTTranslate2(model_name=model)
    result = whisper.transcribe(audio_path, language=language)
    return result.get("segments", [])


# ── Main API ────────────────────────────────────────────────────────────────

def generate_srt(video_or_audio: str, output_srt: str,
                 model: str = "base",
                 api_key: str = None,
                 language: str = "zh",
                 method: str = "auto") -> str:
    """
    生成 SRT 字幕文件。

    Args:
        video_or_audio: 视频或音频文件路径
        output_srt: 输出的 SRT 路径
        model: whisper 模型（"base"/"small"/"medium" 本地，或 "whisper-1" API）
        api_key: OpenAI API Key（可选，环境变量 OPENAI_API_KEY 也可）
        language: 语种代码（"zh"中文，"en"英文）
        method: "api" / "local" / "auto"（auto 自动选择）

    Returns:
        输出 SRT 文件路径
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY")

    # Step 1: 提取音频
    ext = Path(video_or_audio).suffix.lower()
    if ext in (".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"):
        audio_path = extract_audio(video_or_audio)
        cleanup_audio = True
    else:
        audio_path = video_or_audio
        cleanup_audio = False

    try:
        # Step 2: 转写
        if method == "local":
            segments = transcribe_locally(audio_path, model=model, language=language)
        elif method == "api":
            if not api_key:
                raise ValueError("使用 Whisper API 需要设置 OPENAI_API_KEY 环境变量")
            segments = transcribe_with_api(audio_path, api_key, model=model, language=language)
        else:  # auto
            if api_key:
                segments = transcribe_with_api(audio_path, api_key, model=model, language=language)
            else:
                segments = transcribe_locally(audio_path, model=model, language=language)
    finally:
        if cleanup_audio and os.path.exists(audio_path):
            os.remove(audio_path)

    # Step 3: 写入 SRT
    write_srt(segments, output_srt)
    return output_srt


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Whisper 字幕生成工具")
    parser.add_argument("--input", "-i", required=True, help="视频或音频文件")
    parser.add_argument("--output", "-o", required=True, help="输出 SRT 路径")
    parser.add_argument("--model", "-m", default="base",
                        help="模型：base/small/medium(本地) 或 whisper-1(API)")
    parser.add_argument("--language", "-l", default="zh",
                        help="语种：zh/en/...")
    parser.add_argument("--method", default="auto",
                        choices=["auto", "api", "local"],
                        help="auto=自动选择，api=OpenAI API，local=本地模型")
    parser.add_argument("--api-key", help="OpenAI API Key（可选，环境变量也可用）")

    args = parser.parse_args()
    output = generate_srt(
        video_or_audio=args.input,
        output_srt=args.output,
        model=args.model,
        api_key=args.api_key,
        language=args.language,
        method=args.method,
    )
    print(f"✅ 字幕已生成: {output}")
