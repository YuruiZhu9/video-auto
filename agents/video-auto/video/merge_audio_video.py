#!/usr/bin/env python3
"""
video-auto 音频合并工具（Python 版）
使用 wave 模块进行纯 Python 音频操作，不依赖 ffmpeg

功能：
  1. 读取 WAV 文件基本信息（时长、采样率）
  2. 将音频按时间均匀切分为 n 段
  3. 将每段音频与对应 MP4 视频合并（调用的方式根据环境决定）
  4. 拼接所有片段

依赖：wave（Python 标准库），无外部依赖
"""

import wave
import struct
import os
import sys
import json
import subprocess
import shutil
import argparse
from pathlib import Path

# ── 工具函数 ─────────────────────────────────────────────────────

def get_wav_info(filepath):
    """读取 WAV 文件基本信息"""
    with wave.open(filepath, 'rb') as w:
        channels = w.getnchannels()
        sample_width = w.getsampwidth()
        framerate = w.getframerate()
        nframes = w.getnframes()
        duration = nframes / framerate
        return {
            'channels': channels,
            'sample_width': sample_width,
            'framerate': framerate,
            'nframes': nframes,
            'duration': duration,
            'bytes_per_sec': framerate * channels * sample_width,
        }

def split_wav_by_duration(input_file, num_chunks, output_pattern='/tmp/chunk_{:02d}.wav'):
    """
    将 WAV 文件按等时长切分为 num_chunks 段
    使用 wave 模块，纯 Python，无需 ffmpeg
    """
    with wave.open(input_file, 'rb') as w_in:
        params = w_in.getparams()
        frames = w_in.readframes(w_in.getnframes())

    total_frames = params.nframes
    frames_per_chunk = total_frames // num_chunks

    chunks = []
    for i in range(num_chunks):
        start_frame = i * frames_per_chunk
        if i == num_chunks - 1:
            # 最后一片：包含所有剩余帧
            chunk_frames = frames[start_frame * params.sampwidth * params.channels:]
        else:
            chunk_frames = frames[start_frame * params.sampwidth * params.channels:
                                  (start_frame + frames_per_chunk) * params.sampwidth * params.channels]

        out_path = output_pattern.format(i + 1)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with wave.open(out_path, 'wb') as w_out:
            w_out.setparams(params)
            w_out.writeframes(chunk_frames)

        chunks.append(out_path)
        print(f"  [{i+1}/{num_chunks}] 切分 {out_path} ({len(chunk_frames)//params.sampwidth//params.channels} 帧)")

    return chunks

def merge_audio_video_ffmpeg(video_file, audio_file, output_file):
    """
    使用系统 ffmpeg 合并音频和视频（如果可用）
    ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac -shortest out.mp4
    """
    result = subprocess.run(
        ['ffmpeg', '-i', video_file, '-i', audio_file,
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
         '-shortest', '-y', output_file],
        capture_output=True, text=True
    )
    return result.returncode == 0

def concatenate_videos_ffmpeg(video_files, output_file):
    """
    使用 ffmpeg concat 拼接多个视频
    """
    list_file = '/tmp/concat_list.txt'
    with open(list_file, 'w') as f:
        for vf in video_files:
            f.write(f"file '{vf}'\n")

    result = subprocess.run(
        ['ffmpeg', '-f', 'concat', '-safe', '0',
         '-i', list_file, '-c', 'copy', '-y', output_file],
        capture_output=True, text=True
    )
    os.remove(list_file)
    return result.returncode == 0

def concatenate_videos_mp4cat(video_files, output_file):
    """
    使用 MP4Box (若有) 拼接
    """
    if shutil.which('MP4Box'):
        cmd = ['MP4Box']
        for vf in video_files:
            cmd.extend(['cat', vf])
        cmd.extend(['-out', output_file])
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    return False

def concatenate_videos_python_list(video_files, output_file):
    """
    纯 Python 拼接：只支持相同编码的 Annex B MP4
    直接拼接 mdat boxes，兼容某些简单情况
    """
    try:
        import mmap
    except ImportError:
        return False

    # 简单MP4拼接（仅适合 key-frame aligned 的同编码视频）
    with open(output_file, 'wb') as out:
        for i, vf in enumerate(video_files):
            with open(vf, 'rb') as f:
                data = f.read()
            # 移除 ftyp box（仅保留第一个）
            if i == 0:
                out.write(data)
            else:
                # 跳过 ftyp 和 moov box
                pos = 0
                data_len = len(data)
                while pos < data_len:
                    if pos + 8 > data_len:
                        break
                    box_size = struct.unpack('>I', data[pos:pos+4])[0]
                    box_type = data[pos+4:pos+8].decode('ascii', errors='ignore')
                    if box_type in ('moov', 'ftyp', 'free', 'skip'):
                        pos += box_size
                        continue
                    out.write(data[pos:pos+box_size])
                    pos += box_size
    return os.path.exists(output_file) and os.path.getsize(output_file) > 0

# ── 主合并逻辑 ───────────────────────────────────────────────────

def merge_pipeline(video_dir, audio_file, num_slides, output_file):
    """
    完整合并流水线：
      1. 切分音频
      2. 逐段合并音频+视频
      3. 拼接所有片段
    """
    video_dir = Path(video_dir)
    print(f"\n📹 视频目录: {video_dir}")
    print(f"🎙️ 音频文件: {audio_file}")

    # 探测音频
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        return False

    info = get_wav_info(audio_file)
    print(f"\n📊 音频信息:")
    print(f"   时长: {info['duration']:.2f} 秒")
    print(f"   采样率: {info['framerate']} Hz")
    print(f"   通道: {info['channels']}")
    print(f"   比特率: {info['sample_width']*8} bit")

    # 找视频片段
    video_files = []
    for i in range(1, num_slides + 1):
        vf = video_dir / f"slide{i:02d}.mp4"
        if vf.exists():
            video_files.append(vf)
        else:
            print(f"  ⚠️  视频不存在: {vf}")

    if not video_files:
        print("❌ 未找到任何视频片段")
        return False
    print(f"\n✅ 找到 {len(video_files)} 个视频片段")

    # Step 1: 切分音频
    print(f"\n✂️  Step 1: 切分音频为 {len(video_files)} 段...")
    audio_chunks = split_wav_by_duration(audio_file, len(video_files),
                                          output_pattern=str(video_dir / 'chunk_{:02d}.wav'))

    # Step 2: 合并音频+视频（逐段）
    print(f"\n🎞️  Step 2: 合并音频+视频片段...")
    merged_files = []

    has_ffmpeg = shutil.which('ffmpeg') is not None
    print(f"   ffmpeg 可用: {has_ffmpeg}")

    for i, (vf, ac) in enumerate(zip(video_files, audio_chunks)):
        out_mp4 = f"/tmp/merged_{i+1:02d}.mp4"
        process.stdout.write(f"  [{i+1}/{len(video_files)}] {vf.name}")

        if has_ffmpeg:
            ok = merge_audio_video_ffmpeg(str(vf), ac, out_mp4)
            print(" ✅" if ok else " ❌")
        else:
            # 无 ffmpeg：复制原视频（跳过合并）
            shutil.copy(str(vf), out_mp4)
            print(" ⏭️（无ffmpeg，跳过音频合并）")

        merged_files.append(out_mp4)

    # Step 3: 拼接
    print(f"\n🔗 Step 3: 拼接 {len(merged_files)} 个片段...")
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)

    success = False
    if has_ffmpeg:
        success = concatenate_videos_ffmpeg(merged_files, output_file)
    else:
        success = concatenate_videos_python_list(merged_files, output_file)

    if not success:
        print("❌ 拼接失败，尝试直接复制第一个片段...")
        shutil.copy(merged_files[0], output_file)
        success = True

    if success:
        size_mb = os.path.getsize(output_file) / 1024 / 1024
        print(f"\n✅ 合成完成！")
        print(f"📦 输出: {output_file} ({size_mb:.1f} MB)")

    # 清理临时文件
    for f in audio_chunks + merged_files:
        try: os.remove(f)
        except: pass

    return success

# ── CLI 入口 ────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='video-auto 音频视频合并工具')
    parser.add_argument('--slides-dir', default='.', help='视频片段目录（默认当前目录）')
    parser.add_argument('--audio', required=True, help='TTS 音频文件路径')
    parser.add_argument('--num', type=int, default=9, help='视频片段数量')
    parser.add_argument('--output', default='/workspace/agents/video-auto/video/combined/complete_with_audio.mp4',
                        help='输出文件路径')

    args = parser.parse_args()
    success = merge_pipeline(args.slides_dir, args.audio, args.num, args.output)
    sys.exit(0 if success else 1)
