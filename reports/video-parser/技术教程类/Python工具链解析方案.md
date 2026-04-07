# [技术教程类] - Python 工具链解析方案

## 核心工具/API

- **yt-dlp**：视频下载 + 元数据解析
  - 支持 1800+ 网站（B站、YouTube、抖音、小红书等）
  - 可直接提取字幕：`--write-subs --skip-download`
  - 合并音视频流：`--merge-output-format mp4`
- **FFmpeg**：视频处理瑞士军刀
  - 音频提取：`ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav`
  - 视频分段：`ffmpeg -i video.mp4 -ss 00:05:00 -to 00:10:00 clip.mp4`
  - 关键帧采样：配合 Python/OpenCV 批量提取
- **Whisper.cpp**：轻量级本地 Whisper（C++ 实现）
  - 支持 GGML 格式模型，CPU 可运行
  - 实时转录或批量文件处理
- **OpenCV (cv2)**：Python 视频帧提取
  - 按帧号/时间批量提取关键帧
  - 支持帧差法自动检测场景切换
- **video-analyzer（GitHub 开源）**：Llama3.2 Vision + Whisper 端到端方案
  - 自动提取关键帧 + 音频转录 + 视觉分析 → JSON 输出
  - 支持 Ollama 本地推理，无需 API Key
- **HearSight（GitHub 开源）**：智能音视频内容分析
  - 多语言字幕生成 + 内容结构化分析

## 步骤流程

### 方案A：yt-dlp + Whisper 经典组合

1. **下载视频或提取字幕**
   ```bash
   # 下载B站视频
   yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]" -o "%(title)s.%(ext)s" <url>
   
   # 直接提取字幕（B站）
   yt-dlp --write-subs --write-auto-subs --sub-lang zh-Hans --skip-download -o "%(title)s" <url>
   ```

2. **提取音频**
   ```bash
   ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
   ```

3. **Whisper 转录**
   ```bash
   whisper audio.wav --model medium --language Chinese --output_format srt
   ```

4. **字幕 + 视频 → 结构化笔记**
   - 按 SRT 时间戳切分视频片段
   - 每段发给 LLM 生成摘要

### 方案B：video-analyzer 一体化（推荐）

```bash
# 安装
git clone https://github.com/byjlw/video-analyzer.git
cd video-analyzer
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
brew install ffmpeg

# 启动 Ollama（本地推理）
ollama serve

# 分析视频
video-analyzer tutorial.mp4
```

输出包含：元数据 + 音频转录 + 逐帧分析 + 整体描述（JSON 格式）

## 适用场景

- 需要完整保留视频内容的深度分析
- 无网络依赖的本地离线处理
- 批量处理多个教程视频
- 需要生成结构化数据的后续自动化流程

## 避坑指南

- **yt-dlp 版本更新**：建议定期 `pip install -U yt-dlp`，B站接口经常变化
- **FFmpeg 音频格式**：Whisper 推荐 16kHz 单声道 PCM，某些视频需先重采样再转录
- **video-analyzer 内存**：Llama3.2 Vision 11B 模型需 16GB+ 显存，建议用 Ollama 量化版本（q4_0）
- **B站下载限速**：B站有请求频率限制，批量下载需加 `--sleep-interval`
- **字幕时间轴对齐**：部分视频字幕与音频存在毫秒级偏移，需用 FFmpeg 的 `-itsoffset` 校正

## 参考链接

- yt-dlp GitHub：https://github.com/yt-dlp/yt-dlp
- video-analyzer GitHub：https://github.com/byjlw/video-analyzer
- HearSight GitHub：https://github.com/li-xiu-qi/HearSight
- FFmpeg Whisper 过滤器（FFmpeg 8.0+）：内置 whisper.cpp 集成
