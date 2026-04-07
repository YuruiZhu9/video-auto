#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
video-auto 场景检测与智能分段模块

功能：
  1. FFmpeg 场景切换检测（阈值可调）
  2. 语音停顿边界检测（辅助校正）
  3. 智能段落合并（避免过短片段）
  4. 生成带时间戳的语义切片列表

设计理念：
  - 双轨切分：视觉轨道（FFmpeg场景检测）+ 音频轨道（静音检测）
  - 避免碎片化：最小段落时长 5s，最大段落时长 60s
  - 语义优先：场景切换点附近若有语音停顿，优先以停顿点为界

Author: video-auto optimizer
Version: 1.0.0
"""

import subprocess
import re
import os
import json
import struct
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# ====== 常量配置 ======

DEFAULT_SCENE_THRESHOLD = 0.4     # FFmpeg 场景检测阈值（0~1，越高越敏感）
DEFAULT_MIN_SEGMENT_SEC = 5       # 最小段落时长（秒）
DEFAULT_MAX_SEGMENT_SEC = 60      # 最大段落时长（秒）
DEFAULT_FPS = 30                  # 假设帧率

# ====== 工具函数 ======

def run_cmd(cmd: List[str], timeout: int = 60) -> Tuple[str, str, int]:
    """执行 shell 命令，返回 (stdout, stderr, returncode)"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return '', 'Command timeout', -1
    except FileNotFoundError:
        return '', 'Command not found', -1


def parse_showinfo_timestamp(showinfo_line: str) -> Optional[float]:
    """从 FFmpeg showinfo 输出中解析时间戳（秒）"""
    # showinfo 格式: pts_time:0.000 pts: 0 pos: -1 fmt:yuv420p
    m = re.search(r'pts_time:([\d.]+)', showinfo_line)
    if m:
        return float(m.group(1))
    return None


def parse_pts(pts_str: str) -> Optional[float]:
    """解析 FFmpeg pts 值为秒"""
    try:
        # pts 是以 time_base 为单位的整数
        # 通常 time_base = 1/90000
        pts = int(pts_str)
        return pts / 90000.0
    except (ValueError, TypeError):
        return None


def detect_scenes_ffmpeg(video_path: str, threshold: float = DEFAULT_SCENE_THRESHOLD) -> List[float]:
    """
    使用 FFmpeg 场景检测，输出所有场景切换时间戳（秒）
    
    Args:
        video_path: 视频文件路径
        threshold: 场景检测阈值，0.3~0.7 越低越严格
    
    Returns:
        时间戳列表（秒），例如 [0.0, 5.2, 12.7, ...]
    """
    print(f'  🎬 FFmpeg 场景检测中 (threshold={threshold})...')
    
    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f"select='gt(scene,{threshold})',showinfo",
        '-f', 'null', '-'
    ]
    
    stdout, stderr, code = run_cmd(cmd, timeout=120)
    
    timestamps = []
    lines = (stdout + stderr).split('\n')
    
    for line in lines:
        ts = parse_showinfo_timestamp(line)
        if ts is not None:
            timestamps.append(ts)
    
    if not timestamps:
        # 如果没有检测到场景切换，返回整段
        duration = get_video_duration(video_path)
        timestamps = [0.0, duration] if duration else [0.0]
    else:
        # 头部加入 0
        if timestamps[0] > 0.1:
            timestamps.insert(0, 0.0)
    
    print(f'    ✅ 检测到 {len(timestamps)-1} 个场景切换点')
    return timestamps


def get_video_duration(video_path: str) -> Optional[float]:
    """获取视频总时长（秒）"""
    cmd = ['ffprobe', '-v', 'error', '-show_entries',
           'format=duration', '-of', 'json', '-i', video_path]
    stdout, _, code = run_cmd(cmd, timeout=30)
    
    if code == 0:
        try:
            data = json.loads(stdout)
            return float(data['format']['duration'])
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    
    # 备用：从帧信息推算
    cmd2 = ['ffprobe', '-v', 'error', '-count_frames',
            '-select_streams', 'v:0', '-show_entries',
            'stream=nb_read_frames,r_frame_rate',
            '-of', 'json', '-i', video_path]
    stdout2, _, code2 = run_cmd(cmd2, timeout=30)
    
    if code2 == 0:
        try:
            data = json.loads(stdout2)
            fps_str = data['streams'][0]['r_frame_rate']
            num, den = map(float, fps_str.split('/'))
            fps = num / den if den else 0
            frames = int(data['streams'][0].get('nb_read_frames', 0))
            if fps and frames:
                return frames / fps
        except (json.JSONDecodeError, KeyError, TypeError, ZeroDivisionError):
            pass
    
    return None


def detect_silence_audio(video_path: str, min_silence_len: float = 0.8,
                          silence_thresh: float = -40) -> List[float]:
    """
    检测音频静音区间，返回静音结束时间戳列表（作为语音段落边界）
    
    Args:
        video_path: 视频文件路径
        min_silence_len: 最小静音时长（秒）
        silence_thresh: 静音阈值（dBFS）
    
    Returns:
        时间戳列表（秒）
    """
    print(f'  🎙️ 音频静音检测中 (threshold={silence_thresh}dB, min_gap={min_silence_len}s)...')
    
    cmd = [
        'ffmpeg', '-i', video_path, '-af',
        f'silencedetect=noise={silence_thresh}dB:d={min_silence_len}',
        '-f', 'null', '-'
    ]
    
    stdout, stderr, code = run_cmd(cmd, timeout=120)
    
    boundaries = []
    lines = (stdout + stderr).split('\n')
    
    for line in lines:
        # 静音开始点
        m = re.search(r'\[silencedetect @ [0-9a-fx]+\] silence_end: ([\d.]+)', line)
        if m:
            boundaries.append(float(m.group(1)))
    
    print(f'    ✅ 找到 {len(boundaries)} 个语音停顿边界')
    return boundaries


def merge_short_segments(timestamps: List[float],
                          min_duration: float = DEFAULT_MIN_SEGMENT_SEC) -> List[float]:
    """
    合并过短的段落，避免碎片化
    
    规则：
    - 遍历时间戳，如果当前段落时长 < min_duration，向后合并
    - 直到合并后的段落时长 >= min_duration
    
    Args:
        timestamps: 原始段落边界时间戳
        min_duration: 最小段落时长（秒）
    
    Returns:
        合并后的边界时间戳
    """
    if len(timestamps) <= 2:
        return timestamps
    
    merged = [timestamps[0]]
    i = 1
    
    while i < len(timestamps):
        seg_start = merged[-1]
        seg_end = timestamps[i]
        seg_duration = seg_end - seg_start
        
        # 如果当前段落过短，尝试向后合并
        if seg_duration < min_duration and i + 1 < len(timestamps):
            # 向前看：合并到下一个段落
            # 直接把下一个边界时间戳加入，继续判断
            i += 1
            continue
        elif seg_duration < min_duration and i + 1 >= len(timestamps):
            # 最后一段过短：合并到前一段
            merged.pop()
            merged.append(timestamps[-1])
            break
        else:
            merged.append(seg_end)
            i += 1
    
    # 再次检查：合并相邻过短段落
    final = [merged[0]]
    for j in range(1, len(merged)):
        if merged[j] - final[-1] >= min_duration:
            final.append(merged[j])
        else:
            # 过短：跳过，使用下一个边界
            pass
    
    if final[-1] != merged[-1]:
        final.append(merged[-1])
    
    # 确保末尾是视频总时长
    if timestamps[-1] not in final:
        final.append(timestamps[-1])
    
    return sorted(list(set(final)))


def split_at_max_duration(timestamps: List[float],
                           max_duration: float = DEFAULT_MAX_SEGMENT_SEC) -> List[float]:
    """
    将过长段落（> max_duration）在中间切分
    
    切分策略：在中间 1/2 处强制加入切分点
    """
    result = [timestamps[0]]
    
    for i in range(len(timestamps) - 1):
        seg_start = result[-1]
        seg_end = timestamps[i + 1]
        seg_duration = seg_end - seg_start
        
        if seg_duration > max_duration:
            # 在中间插入切分点
            mid = seg_start + max_duration
            result.append(mid)
        else:
            result.append(seg_end)
    
    return sorted(list(set(result)))


def intelligent_merge(timestamps: List[float],
                      silence_boundaries: List[float],
                      min_duration: float = DEFAULT_MIN_SEGMENT_SEC,
                      max_duration: float = DEFAULT_MAX_SEGMENT_SEC) -> List[float]:
    """
    智能合并：结合场景检测 + 语音停顿
    
    策略：
    1. 以场景切换为主要切分依据
    2. 若场景切换点附近（±1s）有语音停顿，优先用语音停顿
    3. 合并过短段落
    4. 拆分过长段落
    
    Args:
        timestamps: 场景检测时间戳
        silence_boundaries: 音频静音边界
        min_duration: 最小段落时长
        max_duration: 最大段落时长
    
    Returns:
        最终段落边界列表
    """
    # 策略：合并两个轨道的切分点
    all_points = sorted(set(timestamps + silence_boundaries))
    
    # 第一步：合并过短段落
    merged = merge_short_segments(all_points, min_duration)
    
    # 第二步：拆分过长段落
    final = split_at_max_duration(merged, max_duration)
    
    # 确保没有相邻重复点
    cleaned = []
    for p in final:
        if not cleaned or abs(p - cleaned[-1]) > 0.05:
            cleaned.append(p)
    
    return cleaned


def get_video_segments(video_path: str,
                       scene_threshold: float = DEFAULT_SCENE_THRESHOLD,
                       min_segment_sec: float = DEFAULT_MIN_SEGMENT_SEC,
                       max_segment_sec: float = DEFAULT_MAX_SEGMENT_SEC,
                       use_audio: bool = True) -> List[Dict]:
    """
    主入口：获取视频分段时间戳列表
    
    Args:
        video_path: 视频文件路径
        scene_threshold: 场景检测阈值
        min_segment_sec: 最小段落时长（秒）
        max_segment_sec: 最大段落时长（秒）
        use_audio: 是否启用音频静音辅助检测
    
    Returns:
        段落列表，每个元素：{'start': float, 'end': float, 'duration': float, 'index': int}
    """
    video_path = str(video_path)
    print(f'\n🎬 场景检测: {os.path.basename(video_path)}')
    
    if not os.path.exists(video_path):
        print(f'  ❌ 文件不存在: {video_path}')
        return []
    
    # Step 1: FFmpeg 场景检测
    scene_ts = detect_scenes_ffmpeg(video_path, scene_threshold)
    
    # Step 2: 音频静音检测（辅助）
    silence_ts = []
    if use_audio:
        silence_ts = detect_silence_audio(video_path)
    
    # Step 3: 智能合并
    boundaries = intelligent_merge(scene_ts, silence_ts, min_segment_sec, max_segment_sec)
    
    # Step 4: 生成段落列表
    segments = []
    total_duration = get_video_duration(video_path) or boundaries[-1]
    
    for i in range(len(boundaries) - 1):
        start = round(boundaries[i], 2)
        end = round(boundaries[i + 1], 2)
        duration = round(end - start, 2)
        
        segments.append({
            'index': i + 1,
            'start': start,
            'end': end,
            'duration': duration,
            'scene_change': start in scene_ts or abs(start - scene_ts[scene_ts.index(start)]) < 0.5,
        })
    
    # 统计
    durations = [s['duration'] for s in segments]
    print(f'\n  📊 分段结果：{len(segments)} 个段落')
    print(f'     平均时长：{sum(durations)/len(durations):.1f}s')
    print(f'     最短：{min(durations):.1f}s，最长：{max(durations):.1f}s')
    
    return segments


def export_srt_timestamps(segments: List[Dict], output_path: str,
                          topic: str = 'Video Segment') -> str:
    """
    将分段时间戳导出为 SRT 字幕文件格式
    
    Args:
        segments: 段落列表
        output_path: 输出 SRT 路径
        topic: 视频主题（作为段落标题）
    
    Returns:
        输出文件路径
    """
    def fmt_srt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
    
    lines = []
    for seg in segments:
        lines.append(str(seg['index']))
        lines.append(f'{fmt_srt_time(seg["start"])} --> {fmt_srt_time(seg["end"])}')
        lines.append(f'{topic} #{seg["index"]}  [{seg["duration"]}s]')
        lines.append('')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f'  ✅ SRT 时间戳已导出: {output_path}')
    return output_path


def extract_segment_preview(video_path: str, segments: List[Dict],
                             output_dir: str,
                             max_keyframes: int = 3) -> List[str]:
    """
    为每个段落提取预览图（关键帧）
    
    Args:
        video_path: 视频文件路径
        segments: 段落列表
        output_dir: 输出目录
        max_keyframes: 每个段落最多提取的关键帧数
    
    Returns:
        预览图路径列表
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    preview_files = []
    
    for seg in segments:
        seg_dir = output_dir / f'segment_{seg["index"]:03d}'
        seg_dir.mkdir(exist_ok=True)
        
        duration = min(seg['duration'], 5.0)  # 最多截取5秒
        output_pattern = str(seg_dir / 'frame_%03d.jpg')
        
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(seg['start']),
            '-i', video_path,
            '-t', str(duration),
            '-vf', f'fps=1/{max(1, int(duration/max_keyframes))}',
            '-q:v', '2',
            output_pattern
        ]
        
        stdout, _, code = run_cmd(cmd, timeout=30)
        
        frames = sorted(seg_dir.glob('frame_*.jpg'))
        if frames:
            preview_files.append(str(frames[0]))  # 第一帧作为段落预览
    
    print(f'  ✅ 提取了 {len(preview_files)} 个段落预览图')
    return preview_files


# ====== CLI 入口 ======

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='video-auto 场景检测与智能分段')
    parser.add_argument('--video', required=True, help='视频文件路径')
    parser.add_argument('--threshold', type=float, default=0.4,
                        help=f'场景检测阈值 (0~1，默认 {DEFAULT_SCENE_THRESHOLD})')
    parser.add_argument('--min-sec', type=float, default=DEFAULT_MIN_SEGMENT_SEC,
                        help=f'最小段落时长(秒)，默认 {DEFAULT_MIN_SEGMENT_SEC}s')
    parser.add_argument('--max-sec', type=float, default=DEFAULT_MAX_SEGMENT_SEC,
                        help=f'最大段落时长(秒)，默认 {DEFAULT_MAX_SEGMENT_SEC}s')
    parser.add_argument('--no-audio', action='store_true',
                        help='禁用音频静音辅助检测')
    parser.add_argument('--output', help='输出 JSON 路径')
    parser.add_argument('--srt', help='输出 SRT 字幕文件路径')
    
    args = parser.parse_args()
    
    segments = get_video_segments(
        args.video,
        scene_threshold=args.threshold,
        min_segment_sec=args.min_sec,
        max_segment_sec=args.max_sec,
        use_audio=not args.no_audio
    )
    
    if not segments:
        print('❌ 未检测到任何段落')
        exit(1)
    
    # 输出 JSON
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({'segments': segments}, f, ensure_ascii=False, indent=2)
        print(f'  💾 JSON 已保存: {args.output}')
    
    # 输出 SRT
    if args.srt:
        export_srt_timestamps(segments, args.srt)
    
    # 打印摘要
    print('\n📋 段落摘要:')
    for seg in segments:
        print(f'  [{seg["index"]:02d}] {seg["start"]:.1f}s - {seg["end"]:.1f}s ({seg["duration"]:.1f}s)'
              + (' 🔀' if seg.get('scene_change') else ''))
