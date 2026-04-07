# [开源项目演示类] - Whisper系列音频转录解析

## 核心工具/API

| 工具 | 语言 | 特点 | 适用场景 |
|------|------|------|---------|
| **Whisper** | Python (OpenAI) | 精度高，支持99语言 | 通用转录 |
| **WhisperX** | Python | 时间轴对齐，段落分割 | 需时间戳场景 |
| **whisper.cpp** | C/C++ | 轻量，量化版可CPU运行 | 低资源环境 |
| **Buzz** | Python + Tkinter | 图形界面，跨平台 | 非程序员用户 |
| **Whisper-Finetune** | Python | 中文微调版 | 中文内容优化 |

## 步骤流程

### 1. 安装 Whisper（Python版）

```bash
pip install openai-whisper
# 或安装最新开发版
pip install -U openai-whisper
```

### 2. 基础转录命令

```bash
# 基础转录（自动检测语言）
whisper video.mp4 --model medium

# 指定语言 + 保存各种格式
whisper video.mp4 \
  --model medium \
  --language Chinese \
  --output_format json,txt,srt,vtt

# 时间戳分段（WhisperX更优）
whisper video.mp4 \
  --model medium \
  --word_timestamps True

# 翻译为英文
whisper video.mp4 --model medium --task translate
```

### 3. WhisperX 精确时间轴

```bash
pip install whisperx

# WhisperX 核心功能
import whisperx

# 加载模型
model = whisperx.load_model("medium", device="cuda")

# 转录（带时间戳）
audio = whisperx.load_audio("video.mp3")
result = model.transcribe(audio)

# 对齐（段落+词级别时间戳）
model_a, metadata = whisperx.load_align_model(language_code="zh")
result = whisperx.align(result["segments"], model_a, metadata, audio, device="cuda")

# Diarization（说话人分离，需额外安装）
import whisperx
diarize_model = whisperx.DiarizationPipeline(use_auth_token="YOUR_HF_TOKEN")
diarize_segments = diarize_model(audio)
result = whisperx.assign_word_speaker(diarize_segments, result)
```

### 4. whisper.cpp 轻量方案

```bash
# 安装（推荐使用预编译二进制）
wget https://github.com/ggml-org/whisper.cpp/releases/latest/download/whisper-bin-x64
chmod +x whisper-bin-x64

# 下载模型
./whisper-bin-x64 download-ggml-model base

# 转录
./whisper-bin-x64 -m models/ggml-base.bin -f samples/jfk.wav

# 实时录音转录（stream模式）
./whisper-bin-x64 -m models/ggml-base.bin -t 8 --step 0 --length 30000 -c
```

### 5. Whisper + 视频解析完整管道

```python
import whisper
import whisperx
import cv2
import json
from pathlib import Path

def parse_video_whisper(video_path, output_dir="/workspace/video_analysis"):
    """完整视频解析管道：Whisper转录 + 帧采样 + 结构化输出"""
    
    Path(output_dir).mkdir(exist_ok=True)
    
    # Step 1: 提取音频
    import subprocess
    audio_path = f"{output_dir}/audio.mp3"
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "libmp3lame", audio_path, "-y"
    ], check=True)
    
    # Step 2: WhisperX 转录（带时间戳）
    model = whisperx.load_model("medium", device="cuda")
    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio)
    
    # 对齐
    model_a, metadata = whisperx.load_align_model(language_code="zh")
    result = whisperx.align(result["segments"], model_a, metadata, audio, device="cuda")
    
    # Step 3: 按转录段落提取对应关键帧
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    structured = []
    for seg in result["segments"]:
        # 找到该段落对应的视频帧
        ts_start = seg["start"]
        cap.set(cv2.CAP_PROP_POS_MSEC, ts_start * 1000)
        ret, frame = cap.read()
        if ret:
            frame_path = f"{output_dir}/frame_{ts_start:.0f}s.jpg"
            cv2.imwrite(frame_path, frame)
        
        structured.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"],
            "key_frame": frame_path if ret else None
        })
    
    cap.release()
    
    # Step 4: 输出结构化结果
    output_file = f"{output_dir}/structured_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 解析完成，共 {len(structured)} 个段落")
    return structured
```

## 适用场景

- ✅ GitHub 项目README配套的Demo视频
- ✅ 开源项目演示/操作指南视频
- ✅ 技术演讲/Conference Talk 录音
- ✅ 播客和有声内容
- ✅ 需要提取代码演示步骤的视频

## 避坑指南

### ⚠️ 问题1：中文转录错字率高
**解决方案**：
- 使用 Whisper-Finetune 中文微调版（https://github.com/yeyupiaoling/Whisper-Finetune）
- 或切换到 `large-v3` 模型（准确率提升明显）
- 手动后处理：正则清理语气词/重复词

### ⚠️ 问题2：whisper.cpp 质量不如原版
**解决方案**：
- 使用更大的量化模型（ggml-medium.bin 而非 ggml-base.bin）
- large-v3 量化版（q8_0）效果接近原版
- 牺牲速度换质量：`./whisper-bin -m models/ggml-large.bin ...`

### ⚠️ 问题3：说话人分离不准确
**解决方案**：
- WhisperX Diarization 依赖 pyannote-audio 需申请HuggingFace Token
- 简单场景直接按时间段落划分即可
- 复杂多人对话建议人工标注校正

### ⚠️ 问题4：长音频OOM（显存不足）
**解决方案**：
- 分段处理：每10分钟一切
- 使用CPU模式：`device="cpu"`（慢但稳定）
- 减小模型：`whisperx.load_model("small", device="cuda")`

## 参考链接

- OpenAI Whisper: https://github.com/openai/whisper
- WhisperX: https://github.com/m-bain/whisperX
- whisper.cpp: https://github.com/ggml-org/whisper.cpp
- Buzz (GUI): https://github.com/chidiwilliams/buzz
- Whisper-Finetune: https://github.com/yeyupiaoling/Whisper-Finetune
