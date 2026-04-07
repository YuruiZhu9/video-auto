# 技术教程类 - FFmpeg + Whisper 二阶段法视频理解

## 核心工具/API

| 工具 | 作用 | 说明 |
|------|------|------|
| **FFmpeg** | 音视频处理 | 提取音频、转换格式、剪辑 |
| **Whisper** (OpenAI) | 语音识别 | 将音频转为文字，支持多语言 |
| **transformers** (HuggingFace) | 模型加载 | pipeline 方式调用 Whisper |
| **ffmpeg-python** | FFmpeg Python绑定 | 代码中调用 FFmpeg（可选） |

### 可选进阶工具

| 工具 | 优势 | 适用场景 |
|------|------|----------|
| **Faster-Whisper** | 速度比原版快 2-4 倍 | 生产环境批量处理 |
| **WhisperX** | 含时间戳对齐 + 词语级时间 | 需要精确时间戳的场景 |
| **FFmpeg 8.0** | 原生集成 Whisper | 命令行直接调用，无需 Python |

## 步骤流程

```
本地视频文件 (.mp4 / .mkv / .avi)
         │
         ▼
┌────────────────────────────────┐
│  阶段一：FFmpeg 音频提取         │
│  ffmpeg -i video.mp4            │
│       -vn                       │  禁用视频
│       -acodec libmp3lame       │  转MP3
│       -ar 44100                │  采样率
│       output.mp3               │
└────────────────┬───────────────┘
                 │
                 ▼
┌────────────────────────────────┐
│  阶段二：Whisper 音频转写        │
│  pipeline(                      │
│    task="automatic-speech-",    │
│    model="whisper-medium"       │
│  )(output.mp3)                  │
└────────────────┬───────────────┘
                 │
                 ▼
         结构化文本输出
         │
         ▼（可选）
    LLM 进一步分析总结
```

### 完整代码示例

```python
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 国内镜像
os.environ["CUDA_VISIBLE_DEVICES"] = "0"             # 指定GPU

from transformers import pipeline
import subprocess

def extract_audio(input_file, output_file):
    """使用 FFmpeg 提取音频"""
    cmd = [
        'ffmpeg', '-i', input_file,
        '-vn', '-acodec', 'libmp3lame',
        '-ar', '44100', '-ac', '2',
        output_file
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ 音频已提取: {output_file}")

def speech2text(audio_file, model_size="medium"):
    """使用 Whisper 转写"""
    transcriber = pipeline(
        task="automatic-speech-recognition",
        model=f"openai/whisper-{model_size}"
    )
    result = transcriber(audio_file)
    return result["text"]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", "-v", required=True)
    parser.add_argument("--audio", "-a", default="output.mp3")
    parser.add_argument("--model", "-m", default="medium")
    args = parser.parse_args()

    extract_audio(args.video, args.audio)
    text = speech2text(args.audio, args.model)
    print("📝 视频文本内容：\n" + text)
```

### FFmpeg 8.0 原生方案（无需 Python）

```bash
# FFmpeg 8.0 内置 Whisper 滤镜，一条命令搞定
ffmpeg -i input.mp4 -filter_complex "whisper=model=medium" output.txt
```

## Whisper 模型选择

| 模型 | 参数量 | 显存需求 | 速度 | 推荐场景 |
|------|--------|----------|------|----------|
| **tiny** | 39M | ~1GB | ⚡最快 | 快速测试 |
| **base** | 74M | ~1GB | ⚡快 | 日常使用 |
| **small** | 244M | ~2GB | 🔄中等 | 兼顾速度与精度 |
| **medium** | 769M | ~5GB | 🐢较慢 | **推荐基线**，中文效果好 |
| **large** | 1550M | ~10GB | 🐢最慢 | 最高精度，专业场景 |

> ⚠️ 推荐使用 `openai/whisper-medium` 作为中文视频的基线模型，large 模型对中文提升有限但速度慢很多。

## 适用场景

- ✅ **本地视频文件**：mp4、mkv、avi、mov 等任意格式
- ✅ **无网络依赖**：离线即可完成转写
- ✅ **隐私敏感内容**：视频不上传，安全性高
- ✅ **结合 LLM 分析**：转写文本后可输入大模型做结构化总结
- ✅ **批量处理**：Python 脚本循环处理大量视频
- ❌ **在线视频URL**：需要先下载，优先考虑 yt-dlp

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| FFmpeg 无法安装 | FFmpeg 不支持 pip 安装 | `apt-get install ffmpeg` 或从官网下载 |
| 中文识别效果差 | 模型太小或未使用 large 模型 | 使用 `medium` 以上模型，指定中文模型 |
| 显存不足 (CUDA OOM) | 模型太大，显存不够 | 使用 `tiny`/`base` 模型，或 CPU 推理 |
| 网络下载模型失败 | HF 被墙 | 设置 `HF_ENDPOINT=https://hf-mirror.com` |
| 长音频截断 | Whisper 默认最大30分钟 | 使用 `WhisperX` 或分段处理 |
| 音频质量差导致转写错误 | 视频编码问题 | 先用 `ffmpeg -i video.mp4 -vn output.wav` 转码 |

### 国内镜像配置

```python
# HuggingFace 模型下载镜像（必须）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 指定GPU
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# 加速包（可选）
pip install -U transformers accelerate
```

## 进阶方案

### Faster-Whisper（推荐生产使用）

```python
from faster_whisper import WhisperModel

model = WhisperModel("medium", device="cuda", compute_type="float16")
segments, info = model.transcribe("audio.mp3", beam_size=5)

for segment in segments:
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
```

### WhisperX（带时间戳）

```bash
pip install whisperx
whisperx audio.mp3 --model medium --align_model WAV2VEC2_ASR_LANG_CMNDICTIONS --compute_type float16
```

## 参考链接

- OpenAI Whisper 官方: https://openai.com/research/whisper
- HuggingFace 模型: https://huggingface.co/openai/whisper-medium
- FFmpeg 下载: https://ffmpeg.org/download.html
- Faster-Whisper: https://github.com/guillaumekln/faster-whisper
- WhisperX: https://github.com/m-bain/whisperX
- FFmpeg+Whisper 教程: https://cloud.tencent.com/developer/article/2443981
