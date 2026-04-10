# 技术教程类 - FFmpeg 关键帧提取解析方案

## 核心工具/API

- **FFmpeg**
  - 官网：https://ffmpeg.org
  - 类型：开源 CLI 工具（C 语言编写）
  - 功能：视频解码、帧提取、转码、剪辑
  - 特点：跨平台，零依赖，功能最全

- **OpenCV（Python）**
  - 文档：https://docs.opencv.org/
  - 功能：视频读取、帧处理、关键帧检测
  - 配合 FFmpeg 使用效果最佳

- **keyframe-scout（PyPI）**
  - PyPI：https://pypi.org/project/keyframe-scout/
  - 功能：专为 VLM/LLM 优化的智能关键帧提取
  - 特点：自适应算法，自动选择最有信息量的帧

- **image_synthesize + videos_understand（OpenClaw 内置）**
  - 功能：帧图 → 多模态 LLM 分析 → 结构化输出

## 步骤流程

### 方案A：FFmpeg 基础帧提取
```bash
# 提取第 N 帧（精确）
ffmpeg -i video.mp4 -vf "select=eq(n\,300)" -vframes 1 frame.jpg

# 等间隔提取（每10秒一帧）
ffmpeg -i video.mp4 -vf "fps=0.1" frames/%04d.jpg

# 提取所有关键帧（I帧）
ffmpeg -i video.mp4 -vf "select='eq(pict_type,PICT_TYPE_I)'" \
  -vsync vfr frames/keyframe_%04d.jpg

# 从关键帧列表提取（更精确）
ffprobe -select_streams v:0 -show_frames video.mp4 \
  | grep pkt_pts_time \
  | grep -B1 "key_frame=1" > keyframes.txt
```

### 方案B：FFmpeg + Python 关键帧提取
```python
import subprocess
import re

def get_keyframe_times(video_path):
    """用 ffprobe 获取所有关键帧时间戳"""
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_frames", "-show_entries", "frame=pkt_pts_time,key_frame",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    times = []
    lines = result.stdout.strip().split("\n")
    for i, line in enumerate(lines):
        if "key_frame=1" in line:
            # 找前面一行的时间戳
            for j in range(i-1, -1, -1):
                if "pkt_pts_time=" in lines[j]:
                    time = lines[j].split("=")[1]
                    times.append(float(time))
                    break
    return times

def extract_keyframes(video_path, output_dir="keyframes/"):
    """提取视频所有关键帧"""
    times = get_keyframe_times(video_path)
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for i, t in enumerate(times):
        ts = f"{int(t//3600):02d}:{(int(t%3600)//60):02d}:{t%60:.3f}"
        out = f"{output_dir}kf_{i:04d}_{ts.replace(':','-')}.jpg"
        subprocess.run([
            "ffmpeg", "-ss", ts, "-i", video_path,
            "-vframes", "1", "-q:v", "2", out
        ], check=True)
    
    return times

extract_keyframes("/path/to/video.mp4")
```

### 方案C：OpenCV 智能关键帧提取
```python
import cv2
import numpy as np

def extract_smart_keyframes(video_path, max_frames=20, threshold=30):
    """基于帧间差异的智能关键帧提取"""
    cap = cv2.VideoCapture(video_path)
    
    prev_frame = None
    keyframes = []
    frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if prev_frame is not None:
            diff = cv2.absdiff(gray, prev_frame)
            mean_diff = diff.mean()
            
            if mean_diff > threshold:
                keyframes.append((frame_idx, frame.copy()))
        
        prev_frame = gray
        frame_idx += 1
        
        # 限制最大帧数
        if len(keyframes) >= max_frames:
            break
    
    cap.release()
    return keyframes

# 保存关键帧
keyframes = extract_smart_keyframes("video.mp4", max_frames=15)
for idx, frame in keyframes:
    cv2.imwrite(f"keyframes/frame_{idx:04d}.jpg", frame)
```

### 方案D：keyframe-scout 智能提取
```bash
pip install keyframe-scout

# 基本用法（为 VLM 优化）
keyframe-scout /path/to/video.mp4 --output-dir ./frames --max-frames 10

# 指定策略
keyframe-scout /path/to/video.mp4 \
  --strategy scene_change \
  --output-dir ./frames

# 配合时间戳输出
keyframe-scout /path/to/video.mp4 \
  --output-dir ./frames \
  --json-metadata metadata.json
```

## 适用场景

- ✅ 技术教程：需要截取代码演示画面
- ✅ 架构图/流程图展示的章节识别
- ✅ PPT 类演示视频的幻灯片提取
- ✅ 视频摘要生成（选代表帧）
- ✅ 多模态 LLM 分析前的预处理
- ✅ 开源项目 demo 视频关键操作提取

## 避坑指南

- **坑1：关键帧太少（视频压缩太狠）**
  - 解决：降低阈值 `threshold=15` 或改用固定间隔提取
  - 监控 `ffprobe -show_frames` 输出中 key_frame=1 的数量

- **坑2：关键帧太多（原始视频是关键帧压缩）**
  - 解决：改用场景切换检测：`select='eq(pict_type,PICT_TYPE_I)'`
  - 或后处理过滤：相邻关键帧间隔 < 2秒 合并

- **坑3：提取速度慢**
  - 解决：先seek再解码：`ffmpeg -ss 10 -i video.mp4 -vframes 1 out.jpg`
  - 注意顺序：`-ss` 必须在 `-i` 之前（快速seek）

- **坑4：输出图片太大**
  - 解决：指定分辨率压缩：`ffmpeg -i video.mp4 -vf "scale=1280:-1" -vframes 1 out.jpg`
  - 或质量参数：`-q:v 2`（1=最高质量，31=最低）

- **坑5：特定格式无法解码**
  - 解决：检查 ffprobe 支持：`ffprobe -formats`
  - .webm 用 `libvpx`，.mov 用 `libx264`

## 参考链接

- FFmpeg 官方：https://ffmpeg.org
- FFmpeg 关键帧提取 CSDN：https://blog.csdn.net/agito_cheung/article/details/145864851
- keyframe-scout PyPI：https://pypi.org/project/keyframe-scout/
- OpenCV 视频处理：https://docs.opencv.org/
- VideoPipe 视频分析框架：https://github.com/xxxspirit/video_pipe
