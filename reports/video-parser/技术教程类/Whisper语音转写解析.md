# 技术教程类 - Whisper 语音转写解析方案

## 核心工具/API

- **OpenAI Whisper CLI（本地）**
  - 安装：`brew install openai-whisper`
  - 模型：`tiny / base / small / medium / large / turbo`
  - 特点：无需 API Key，离线可用，首次下载模型

- **OpenAI Whisper API（云端）**
  - 端点：`POST https://api.openai.com/v1/audio/transcriptions`
  - 模型：`whisper-1`
  - 特点：速度快，质量稳定，按分钟计费

- **WhisperX（增强版）**
  - GitHub：https://github.com/m-bain/whisperX
  - 特点：词级时间戳 + 说话人分离 + 自动标点
  - 适合：技术教程需要精确时间对应

## 步骤流程

### 方案A：Whisper CLI 本地转写
```bash
# 基础转写（输出 txt）
whisper /path/to/video.mp4 --model medium --output_format txt --output_dir .

# 带时间轴字幕（SRT）
whisper /path/to/video.mp4 --model medium --output_format srt --output_dir .

# 翻译为英文
whisper /path/to/audio.m4a --task translate --output_format txt

# 指定语言（加速）
whisper /path/to/video.mp4 --language zh --model small
```

### 方案B：Whisper API 转写（curl）
```bash
# 基础调用
curl -X POST https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@/path/to/audio.m4a" \
  -F "model=whisper-1"

# 带语言和提示
curl -X POST https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@/path/to/audio.m4a" \
  -F "model=whisper-1" \
  -F "language=zh" \
  -F "prompt=这是一个Python技术教程视频"
```

### 方案C：WhisperX 精确时间戳转写
```python
import whisperx

# 1. 转写
model = whisperx.load_model("medium", device="cuda")
audio = whisperx.load_audio("video.mp4")
result = model.transcribe(audio)

# 2. 对齐（词级时间戳）
model_a, metadata = whisperx.load_align_model(language_code="zh")
result = whisperx.align(result["segments"], model_a, metadata, audio, device="cuda")

# 3. 说话人分离（Diarization）
diarize_model = whisperx.DiarizationPipeline(use_auth_token="HF_TOKEN")
diarize_segments = diarize_model(audio)
result = whisperx.assign_word_speakers(diarize_segments, result)
```

### 方案D：完整 Pipeline（视频→转写→结构化）
```python
import subprocess
import whisper

# Step 1: 提取音频
subprocess.run([
    "ffmpeg", "-i", "video.mp4", "-vn",
    "-acodec", "libmp3lame", "-q:a", "2",
    "audio.mp3"
])

# Step 2: Whisper 转写
model = whisper.load_model("medium")
result = model.transcribe("audio.mp3")

# Step 3: 输出结构化 JSON
import json
with open("transcript.json", "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

## 适用场景

- ✅ 本地视频无字幕（无法联网获取字幕时）
- ✅ 会议录音/播客内容提取
- ✅ 现场演示视频（YouTube 无官方字幕）
- ✅ 多语言视频翻译转写
- ✅ 需要词级时间戳的技术教程拆解
- ✅ 说话人识别区分的技术分享

## 避坑指南

- **坑1：模型太大，内存不足**
  - 解决：本地用 `tiny` / `base` 快速测试，确认后再用 `medium`
  - WhisperX 可在 CPU 上运行（慢但省显存）

- **坑2：中文识别质量差**
  - 解决：显式指定 `--language zh`，避免模型误判语言
  - 对于专有名词，用 `--prompt` 参数提供上下文

- **坑3：长音频超时**
  - 解决：Whisper CLI 默认处理长音频；API 有 25MB 限制
  - 长视频先切分：`ffmpeg -i video.mp4 -ss 0 -t 600 audio_part1.mp3`

- **坑4：背景音乐干扰**
  - 解决：提取音频时先降噪：`ffmpeg -i video.mp4 -af "highpass=f=200,lowpass=f=3000" audio.wav`
  - 或用 demucs 分离人声：`demucs --name htdemucs_mmi audio.mp3`

- **坑5：Whisper API 费用高**
  - 解决：本地运行 Whisper CLI 完全免费
  - OpenAI API 按分钟计费，合理规划调用

## 参考链接

- Whisper 官方：https://github.com/openai/whisper
- WhisperX：https://github.com/m-bain/whisperX
- Whisper C++ 高性能版：https://github.com/Const-me/Whisper
- OpenAI Transcriptions API：https://platform.openai.com/docs/guides/speech-to-text
