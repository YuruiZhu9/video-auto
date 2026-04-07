# 开源项目演示类 - yt-whisper 解析

## 核心工具/API

| 工具 | 作用 | 说明 |
|------|------|------|
| **yt-dlp** | YouTube 视频下载 | 获取视频直链或下载到本地 |
| **OpenAI Whisper** | 语音识别 | 将音频转写为文字 |
| **Python** | 环境 | Python 3.7+，一条命令驱动全流程 |

## 步骤流程

```
输入：YouTube 视频URL
         │
         ▼
┌─────────────────────────────────┐
│  yt-dlp 提取视频音频流           │
│  yt-dlp -f best "URL" -o -     │
│  管道输出到 FFmpeg 处理          │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  FFmpeg 音频转码                │
│  ffmpeg -i - -vn audio.mp3      │
│  从 yt-dlp 输出流直接转码        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Whisper 模型推理               │
│  whisper-medium(audio.mp3)      │
│  输出 VTT / SRT / TXT 字幕文件   │
└─────────────────────────────────┘
```

## 安装步骤

```bash
# 1. 安装 yt-whisper（自动安装 yt-dlp + whisper）
pip install git+https://github.com/m1guelpf/yt-whisper.git

# 2. 安装 FFmpeg（如未安装）
# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg

# MacOS
brew install ffmpeg

# Windows (使用 Chocolatey)
choco install ffmpeg
```

## 使用流程

### 基本用法（一行命令）

```bash
# 生成 VTT 字幕文件
yt_whisper "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 指定输出格式（支持: vtt, srt, txt, json）
yt_whisper "URL" --output_format srt
```

### 模型选择

```bash
# 默认 small 模型（适合英语）
yt_whisper "URL"

# medium 模型（推荐非英语，中文效果好）
yt_whisper "URL" --model medium

# large 模型（最高精度，需要更多显存）
yt_whisper "URL" --model large

# 各语言专用模型（.en 后缀，仅英语但更快）
yt_whisper "URL" --model medium.en
```

### 翻译功能

```bash
# 将字幕翻译为英语
yt_whisper "URL" --task translate

# 示例：中文视频 → 英文字幕
yt_whisper "https://www.youtube.com/watch?v=XXXXX" --task translate --model medium
```

### 查看所有可用选项

```bash
yt_whisper --help
```

## 适用场景

- ✅ **YouTube 字幕生成**：为任何 YouTube 视频自动生成字幕文件
- ✅ **视频内容提取**：获取视频的文字内容，用于分析/存档
- ✅ **多语言翻译**：将外语视频翻译成英文字幕
- ✅ **无障碍辅助**：为视频添加字幕提升可访问性
- ✅ **快速转录**：一行命令，无需复杂配置
- ❌ **Bilibili**：需要使用 yt-dlp 单独处理
- ❌ **本地视频**：需要 yt-dlp 先下载，建议用 FFmpeg + Whisper 直接处理

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| YouTube 视频无法下载 | 地区限制或视频被删 | 使用 VPN 或 `--geo-bypass` 参数 |
| 中文识别质量差 | small 模型对中文支持弱 | 使用 `--model medium` 或 `--model large` |
| 模型下载失败 | 网络问题 | 设置镜像或手动下载模型到 `~/.cache/whisper` |
| 内存不足 | 模型太大 | 使用 `tiny` 或 `base` 模型 |
| 输出文件为空 | 网络中断或视频无声音 | 检查网络，确认视频有音轨 |

### 国内优化

```bash
# 设置 HuggingFace 镜像（国内下载 Whisper 模型）
export HF_ENDPOINT="https://hf-mirror.com"

# 同时设置代理（如果需要）
export HTTPS_PROXY="http://127.0.0.1:7890"

# 再运行
yt_whisper "URL" --model medium
```

## 项目信息

| 项目 | 信息 |
|------|------|
| GitHub | https://github.com/m1guelpf/yt-whisper |
| Stars | ~1.4k |
| 许可证 | MIT |
| 依赖 | yt-dlp, openai/whisper, ffmpeg |
| Python 版本 | 3.7+ |

## 进阶用法

### 批量处理多个视频

```bash
# 将视频URL列表存入 videos.txt，每行一个URL
# 逐个处理
while read url; do
  yt_whisper "$url" --model medium
done < videos.txt
```

### 指定输出路径

```bash
# 指定输出目录
yt_whisper "URL" --output_dir ./subtitles/

# 指定输出文件名
yt_whisper "URL" --output_filename "my_video"
```

### 高级 yt-dlp 参数透传

```bash
# 透传 yt-dlp 参数（字幕格式、画质等）
yt_whisper "URL" --ytdlp_opts "--format bestaudio --no-playlist"
```

## 适用视频类型

| 视频类型 | 推荐模型 | 备注 |
|---------|---------|------|
| 英语短视频（<10min） | `small` | 速度最快 |
| 英语长视频 | `medium` | 精度更好 |
| 中文视频 | `medium` | 中文需较大模型 |
| 多语言混合 | `large` | 复杂内容选最大 |
| 音质差的视频 | `medium/large` | 大模型更鲁棒 |

## 参考链接

- GitHub: https://github.com/m1guelpf/yt-whisper
- OpenAI Whisper: https://openai.com/research/whisper
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- FFmpeg: https://ffmpeg.org/
