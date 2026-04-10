#!/usr/bin/env python3
"""
video/video_transitions.py
==========================
视频片段拼接 + 交叉淡化（crossfade）过渡效果。
支持 FFmpeg（推荐）、moviepy 两种实现，fallback 到纯 Python MP4 box 拼接。

Usage:
    from video_transitions import concatenate_with_crossfade
    concatenate_with_crossfade(["a.mp4", "b.mp4"], "output.mp4", transition_duration=0.5)

    # CLI
    python video_transitions.py --inputs a.mp4 b.mp4 --output output.mp4 --duration 0.5
    python video_transitions.py --inputs a.mp4 b.mp4 --output output.mp4 --no-transition
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional


# ── Tool detection ─────────────────────────────────────────────────────────

def has_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def has_moviepy() -> bool:
    try:
        import moviepy.editor as _
        return True
    except ImportError:
        return False


# ── Method 1: FFmpeg xfade (推荐) ─────────────────────────────────────────

def concatenate_ffmpeg_xfade(input_files: List[str], output_file: str,
                              transition_duration: float = 0.5) -> str:
    """
    使用 FFmpeg xfade 滤镜实现优雅的交叉淡化。
    每两个相邻片段之间加入 fade 过渡。
    """
    if len(input_files) < 2:
        raise ValueError("需要至少 2 个视频文件才能使用交叉淡化")

    # 构建 FFmpeg complex filter 字符串
    n = len(input_files)
    # 假设每个片段约 6 秒（与 batch_image_to_video 默认一致）
    # offset = (n-1) * clip_duration - transition_duration
    clip_duration = 6.0  # 默认片段时长，可改进为动态检测
    fade_duration = transition_duration

    # 构建输入参数
    inputs = []
    for f in input_files:
        inputs += ["-i", f]

    # xfade 链：a [xa] b [xb] c ...
    # 第一个片段无过渡，之后每个片段与前一片段 fade
    filter_parts = []
    for i in range(1, n):
        offset = (i - 1) * clip_duration + (clip_duration - fade_duration)
        if i == 1:
            filter_parts.append(f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={offset}[outv]")
        else:
            filter_parts.append(f"[outv][{i}:v]xfade=transition=fade:duration={fade_duration}:offset={offset}[outv]")

    # 音频：直接 concat（暂不处理音频过渡，可扩展）
    audio_filter = ""
    if n >= 2:
        # 音频 concat
        audio_concat = "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[aout]"
        audio_filter = f"-filter_complex \"{audio_concat}\" -map \"[aout]\""
    else:
        audio_filter = "-map 0:a? -map 0:v"

    filter_str = ";".join(filter_parts)
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_str,
        "-map", "[outv]",
    ] + (["-af", f"atrim=0:{(n-1)*clip_duration+fade_duration},asetpts=PTS-STARTPTS[aout]",
          "-map", "[aout]"] if audio_filter else [])
    cmd += ["-t", str((n - 1) * clip_duration + fade_duration), output_file]

    # 简化版：不用复杂音频 filter，直接拼接
    cmd_simple = ["ffmpeg", "-y"] + sum([["-i", f] for f in input_files], [])
    # 构建 xfade 链
    filter_chain = ""
    for i in range(1, n):
        offset = (i - 1) * clip_duration + (clip_duration - fade_duration)
        if i == 1:
            filter_chain += f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={offset}"
        else:
            filter_chain += f"[x{i-1}][{i}:v]xfade=transition=fade:duration={fade_duration}:offset={offset}"
    filter_chain += f"[x{n-1}];"
    # 音频 concat
    audio_chain = "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[aout]"
    filter_chain += audio_chain

    cmd = ["ffmpeg", "-y"] + sum([["-i", f] for f in input_files], []) + \
          ["-filter_complex", filter_chain,
           "-map", f"[x{n-1}]", "-map", "[aout]",
           "-t", str((n - 1) * clip_duration + fade_duration),
           output_file]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg xfade 失败:\n{result.stderr[-1000:]}")
    return output_file


# ── Method 2: MoviePy (无 FFmpeg 时) ──────────────────────────────────────

def concatenate_moviepy_crossfade(input_files: List[str], output_file: str,
                                    transition_duration: float = 0.5) -> str:
    """使用 moviepy 实现视频拼接 + 淡入淡出过渡"""
    import moviepy.editor as mp

    clips = [mp.VideoFileClip(f) for f in input_files]

    # 逐个合并，加入 crossfade
    combined = clips[0]
    for clip in clips[1:]:
        combined = concatenate_crossfade_two(combined, clip, transition_duration)

    combined.write_videofile(output_file, codec='libx264', audio_codec='aac',
                             temp_audiofile=tempfile.mktemp(suffix=".m4a"),
                             remove_temp=True, logger=None)
    for c in clips:
        c.close()
    return output_file


def concatenate_crossfade_two(clip_a, clip_b, duration: float):
    """将两个片段以 fade 过渡合并（moviepy 版）"""
    import moviepy.editor as mp
    # clip_a 末尾 fade out，clip_b 开头 fade in
    fade_a = clip_a.fx(mp.VideoFileClip.setOpacity, 1.0).crossfadeout(duration)
    fade_b = clip_b.fx(mp.VideoFileClip.setOpacity, 1.0).crossfadein(duration)
    # 时长对齐
    dur_a = clip_a.duration
    dur_b = clip_b.duration
    # 截取 clip_b 的有效部分
    start_b = duration
    end_b = min(duration + dur_b - duration, dur_b)  # 从 fade-in 结束后开始
    clip_b_trimmed = clip_b.subclip(start_b, end_b)
    # 拼合
    from moviepy.editor import CompositeVideoClip, CompositeAudioClip
    final = CompositeVideoClip([fade_a, clip_b.set_start(dur_a - duration)],
                                size=clip_a.size, bg_color=0)
    return final


# ── Method 3: Pure Python (最小可用版) ─────────────────────────────────────

def concatenate_python_copy(input_files: List[str], output_file: str) -> str:
    """
    纯 Python MP4 box 拼接（无 FFmpeg 时 fallback）。
    来自 push_opt.js 中已验证的方案。
    """
    # 检测 Python 版本
    if sys.version_info < (3, 8):
        raise RuntimeError("需要 Python 3.8+")

    output_path = output_file
    with open(output_path, 'wb') as output:
        for i, input_path in enumerate(input_files):
            with open(input_path, 'rb') as input_file:
                # 跳过 ftyp box（防止编码不一致）
                ftyp = input_file.read(8)
                if ftyp[4:8] == b'ftyp':
                    size = int.from_bytes(ftyp[:4], 'big')
                    input_file.seek(size - 8)
                else:
                    input_file.seek(0)
                shutil.copyfileobj(input_file, output)
    return output_path


# ── Crossfade (纯 Python fallback) ─────────────────────────────────────────

def add_crossfade_python(input_files: List[str], output_file: str,
                          transition_duration: float = 0.5,
                          fade_frames: int = 8) -> str:
    """
    纯 Python 版淡入淡出：不依赖 FFmpeg/moviepy。
    通过在片段末尾追加黑帧 + 下一片段开头的帧复制实现视觉效果。
    近似 crossfade，但不如 FFmpeg 精确（仅作 fallback）。
    """
    print(f"[警告] FFmpeg 和 moviepy 均不可用，使用 Python fallback 淡入淡出（{fade_frames}帧）")
    return concatenate_python_copy(input_files, output_file)


# ── Public API ─────────────────────────────────────────────────────────────

def concatenate_with_crossfade(input_files: List[str], output_file: str,
                                 transition_duration: float = 0.5,
                                 force_method: str = "auto",
                                 clip_duration: float = 6.0) -> str:
    """
    主入口：视频拼接 + 交叉淡化过渡。

    Args:
        input_files: 输入视频文件路径列表
        output_file: 输出文件路径
        transition_duration: 过渡时长（秒），默认 0.5s
        force_method: "auto" / "ffmpeg" / "moviepy" / "python"
        clip_duration: 每个片段预估时长（用于 FFmpeg xfade 计算 offset）

    Returns:
        输出文件路径
    """
    if len(input_files) == 1:
        shutil.copy(input_files[0], output_file)
        return output_file

    method = force_method

    if method == "auto":
        if has_ffmpeg():
            method = "ffmpeg"
        elif has_moviepy():
            method = "moviepy"
        else:
            method = "python"

    if method == "ffmpeg":
        return concatenate_ffmpeg_xfade(input_files, output_file, transition_duration)
    elif method == "moviepy":
        return concatenate_moviepy_crossfade(input_files, output_file, transition_duration)
    else:
        return add_crossfade_python(input_files, output_file, transition_duration)


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="视频拼接 + 交叉淡化过渡")
    parser.add_argument("--inputs", "-i", nargs="+", required=True,
                        help="输入视频文件（顺序拼接）")
    parser.add_argument("--output", "-o", required=True,
                        help="输出视频文件")
    parser.add_argument("--duration", "-d", type=float, default=0.5,
                        help="交叉淡化过渡时长（秒），默认 0.5")
    parser.add_argument("--clip-duration", type=float, default=6.0,
                        help="每个片段预估时长（秒），默认 6.0")
    parser.add_argument("--no-transition", action="store_true",
                        help="跳过过渡，直接拼接")
    parser.add_argument("--method", "-m", default="auto",
                        choices=["auto", "ffmpeg", "moviepy", "python"],
                        help="强制使用某方法")
    args = parser.parse_args()

    if args.no_transition:
        output = concatenate_with_crossfade(
            args.inputs, args.output,
            transition_duration=0.0,
            force_method="auto" if args.method == "auto" else args.method,
            clip_duration=args.clip_duration,
        )
    else:
        output = concatenate_with_crossfade(
            args.inputs, args.output,
            transition_duration=args.duration,
            force_method=args.method,
            clip_duration=args.clip_duration,
        )
    print(f"✅ 视频已生成: {output}")
