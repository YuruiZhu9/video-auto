# 开源项目演示类 - 完整解析 Pipeline 方案

## 核心理念

开源项目 demo 视频的核心解析目标：
1. **代码演示**：演示了什么功能/操作
2. **架构展示**：系统设计/界面布局
3. **关键命令**：可复现的安装/运行命令
4. **技术亮点**：用了什么新框架/工具/特性

## 推荐 Pipeline

### 阶段1：预处理（视频 → 素材）
```bash
# 1. 音频提取
ffmpeg -i demo.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3

# 2. 关键帧提取（10帧）
keyframe-scout demo.mp4 --output-dir ./frames --max-frames 10

# 3. 有字幕优先提取字幕
yt-dlp --write-auto-subs --sub-langs zh-Hans,en \
  --skip-download demo.mp4
```

### 阶段2：转写（音频 → 文字）
```python
import whisper

model = whisper.load_model("medium")
result = model.transcribe("audio.mp3", language="zh")

# 保存带时间戳的字幕
with open("transcript.srt", "w") as f:
    whisper.decode(model, result)
    # 输出 SRT 格式
```

### 阶段3：分析（文字+帧 → 结构化）
```python
# 用 LLM 分析字幕 + 帧
analysis_prompt = """
这是一个开源项目的演示视频。请提取：
1. 演示的核心功能（用 bullet list）
2. 所有可复现的命令（用 code block）
3. 系统架构/界面截图描述
4. 使用的技术栈/工具
5. 视频时间戳 → 对应功能点的映射表

字幕内容：
{subtitle_text}

请用中文回答。
"""
```

## 完整脚本示例

```python
#!/usr/bin/env python3
"""开源项目演示视频解析 Pipeline"""

import subprocess
import os
import json
import whisper
import cv2

def parse_demo_video(video_path, output_dir="demo_output/"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 音频提取
    print("📢 提取音频...")
    subprocess.run([
        "ffmpeg", "-i", video_path, "-vn",
        "-acodec", "libmp3lame", "-q:a", "2",
        f"{output_dir}audio.mp3"
    ], check=True)
    
    # 2. 关键帧提取
    print("🖼️ 提取关键帧...")
    frames = extract_smart_keyframes(video_path, max_frames=10)
    for idx, frame in frames:
        cv2.imwrite(f"{output_dir}frame_{idx:04d}.jpg", frame)
    
    # 3. Whisper 转写
    print("🎙️ 音频转写...")
    model = whisper.load_model("medium")
    result = model.transcribe(f"{output_dir}audio.mp3", language="zh")
    
    with open(f"{output_dir}transcript.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 4. 生成结构化报告（调用 LLM）
    print("🤖 LLM 结构化分析...")
    # ... 调用 videos_understand 或 GPT-4o API
    
    return f"{output_dir}analysis.md"

def extract_smart_keyframes(video_path, max_frames=10):
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = max(1, total // max_frames)
    keyframes = []
    prev_gray = None
    
    for i in range(max_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * interval)
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_gray is None or cv2.absdiff(gray, prev_gray).mean() > 15:
                keyframes.append((i * interval, frame.copy()))
                prev_gray = gray
    cap.release()
    return keyframes

if __name__ == "__main__":
    output = parse_demo_video("/path/to/demo.mp4")
    print(f"✅ 解析完成：{output}")
```

## 适用场景

- ✅ GitHub 项目 README 配套 demo 视频
- ✅ 工具/框架发布会的演示录像
- ✅ 开源社区线上分享的实操演示
- ✅ API 文档配套的操作演示视频
- ✅ Hackathon 项目展示视频

## 避坑指南

- **坑1：demo 视频语速快，信息密集**
  - 解决：增加关键帧数量（15-20帧），捕捉每个操作切换
  - Whisper 用 medium 模型，base 可能漏掉术语

- **坑2：代码演示区域小，帧提取效果差**
  - 解决：视频先裁剪到代码区域：`ffmpeg -i video.mp4 -vf "crop=1280:720:0:0" cropped.mp4`

- **坑3：命令一闪而过**
  - 解决：Whisper 转写时设置 `"word_timestamps": True`
  - 精确找到命令出现的时间点，截取对应帧

## 参考链接

- keyframe-scout：https://pypi.org/project/keyframe-scout/
- Whisper：https://github.com/openai/whisper
- yt-dlp：https://github.com/yt-dlp/yt-dlp
- FFmpeg：https://ffmpeg.org/
- OpenClaw videos_understand：内置工具
