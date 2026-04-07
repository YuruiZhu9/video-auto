# 技术教程类 - openai-whisper 本地转录

## 核心工具/API

- **工具**: `whisper`（OpenAI Whisper CLI，本地运行）
- **安装**: `brew install openai-whisper`（模型自动下载到 `~/.cache/whisper`）
- **默认模型**: `turbo`（此环境默认，无需手动指定）
- **无需 API Key**: 完全离线运行

## 步骤流程

### 基础转录
```bash
# 基本转录（自动选择模型）
whisper /path/to/audio.mp3 --output_dir .

# 指定模型（medium 平衡速度与准确率）
whisper /path/to/audio.mp3 --model medium --output_format txt --output_dir .

# 输出多种格式
whisper /path/to/audio.m4a \
  --model medium \
  --output_format srt,vtt,txt,json \
  --output_dir /workspace/transcripts/
```

### 翻译（非英语音频 → 英语）
```bash
# 将中文音频翻译为英文文本
whisper /path/to/chinese-audio.m4a --task translate
```

### 带提示的转录（提高准确率）
```bash
# 提供说话人或专有名词提示
whisper /path/to/audio.mp3 \
  --model medium \
  --prompt "Speaker names: John, Sarah. Technical terms: Kubernetes, PyTorch"
```

### Whisper 模型选择

| 模型 | 参数量 | 速度 | 准确率 | 适用场景 |
|------|--------|------|--------|---------|
| `tiny` | 39M | 极快 | 低 | 快速预览 |
| `base` | 74M | 快 | 中 | 一般质量 |
| `small` | 244M | 中 | 较高 | 平衡推荐 |
| `medium` | 769M | 较慢 | 高 | **推荐首选** |
| `large` | 1550M | 慢 | 最高 | 最高精度 |
| `turbo` | ~809M | 中 | 高 | **此环境默认** |

## 适用场景

- **技术教程转录**: 生成带字幕的教程文本，便于检索
- **会议/演讲记录**: 完整文字稿，便于存档
- **代码演示配音**: 转录技术讲解，形成文档
- **外语教程翻译**: `translate` 模式生成英文字幕
- **批量处理**: 对多个视频/音频文件批量转录

## 避坑指南

| 问题 | 解决方案 |
|------|---------|
| 视频无声音轨道 | 先用 `ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav` 提取音轨 |
| 音频嘈杂影响准确率 | 预处理：`ffmpeg -i audio.mp3 -af "highpass=f=200,lowpass=f=3000" clean.wav` |
| 专有名词识别错误 | 用 `--prompt` 提供专有名词列表（如 API 名、技术栈） |
| 中文识别率高但英文差 | 用 `--language zh` / `--language en` 指定语言 |
| 多人说话无法区分 | 目前 Whisper 不区分说话人，可用 WhisperX（需额外安装）|
| 内存不足（large 模型） | 使用 `medium` 或 `small`，牺牲少量精度换取可用性 |
| 第一次运行慢（下载模型）| 耐心等待，模型只下载一次，后续直接使用 |

## 从视频提取音频再转录
```bash
# 提取音频（视频 → WAV）
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav

# 批量转录
for f in *.mp4; do
  ffmpeg -i "$f" -vn -acodec pcm_s16le -ar 16000 "${f%.mp4}.wav"
  whisper "${f%.mp4}.wav" --model medium --output_format txt
done
```
