# 技术教程类 - yt-dlp + Whisper 本地转录方案

> 最后更新：2026-03-21

## 概述

yt-dlp + Whisper 组合是当前最主流的本地视频转录方案，支持 YouTube、B站、抖音等几乎所有主流平台。本方案完全本地运行，无需付费 API，适合需要处理敏感内容或批量任务的场景。

---

## 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| **yt-dlp** | 多平台视频/音频下载，支持 1800+ 网站 |
| **FFmpeg** | 音频提取、格式转换、视频处理 |
| **Whisper（本地CLI）** | OpenAI 开源语音识别，无需 API key |
| **faster-whisper** | Whisper 加速版，支持 GPU |

---

## 快速开始

### 1. 安装依赖

```bash
# yt-dlp
pip install yt-dlp

# FFmpeg（macOS）
brew install ffmpeg

# FFmpeg（Linux）
sudo apt install ffmpeg

# Whisper
pip install openai-whisper

# faster-whisper（推荐 GPU 用户）
pip install faster-whisper
```

### 2. 下载视频（YouTube）

```bash
# 下载视频 + 自动字幕
yt-dlp --write-auto-subs --sub-langs zh-Hans,en \
  -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=xxxxx"

# 仅音频（节省空间）
yt-dlp -x --audio-format mp3 \
  -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=xxxxx"
```

### 3. 下载视频（B站）

```bash
# 下载含弹幕视频（需登录 cookies）
yt-dlp --write-subs --write-auto-subs --sub-langs zh-Hans \
  --cookies-from-browser chrome \
  -o "%(title)s.%(ext)s" "https://www.bilibili.com/video/BVxxxxx"

# 无需登录（画质受限）
yt-dlp --write-auto-subs --sub-langs zh-Hans \
  -o "%(title)s.%(ext)s" "https://www.bilibili.com/video/BVxxxxx"
```

### 4. 转录音频

```bash
# 本地 Whisper（免费）
whisper audio.mp3 \
  --model medium \
  --language zh \
  --output_format txt \
  --output_dir ./transcripts

# 使用 faster-whisper（更快）
python -c "
from faster_whisper import WhisperModel
model = WhisperModel('medium', device='cuda')
segments, _ = model.transcribe('audio.mp3', language='zh')
with open('transcript.txt', 'w') as f:
    for seg in segments:
        f.write(f'{seg.start:.2f}s - {seg.end:.2f}s: {seg.text}\n')
"
```

### 5. 结合 LLM 总结

```bash
# 提取关键信息
cat transcript.txt | llm "总结以下技术分享内容，提取：1)主题 2)核心观点 3)关键技术点 4)实践建议"

# 分段总结长文本
cat transcript.txt | llm "将以下内容按时间顺序分为几个部分，每个部分给出小标题和摘要"
```

---

## 完整工作流

```
输入：视频URL
  ↓
① yt-dlp 下载（视频/音频）
  ↓
② FFmpeg 提取音频（mp3/m4a）
  ↓
③ Whisper 转录（时间戳文字稿）
  ↓
④ LLM 总结（结构化笔记）
  ↓
输出：文字稿 + 摘要 + 知识点
```

---

## 适用场景

- ✅ B站/YouTube 技术分享视频完整文字稿提取
- ✅ 多平台视频批量转录处理
- ✅ 敏感内容本地处理（不上传云端）
- ✅ 需要时间戳的精确内容定位
- ✅ 播客/访谈视频转文字
- ✅ 会议记录实时转录

---

## 避坑指南

### 问题1：B站下载画质受限或失败
**原因**：B站需要登录态才能下载高画质
**解决方案**：
```bash
# 导出浏览器 cookies（Chrome/Firefox）
yt-dlp --cookies-from-browser chrome \
  --write-auto-subs --sub-langs zh-Hans \
  "https://www.bilibili.com/video/BVxxxxx"

# 或手动提供 cookies.txt
yt-dlp --cookies cookies.txt -o "%(title)s.%(ext)s" "URL"
```

### 问题2：中文识别不准
**解决方案**：
- 明确指定语言：`--language zh`
- 使用更大的模型：`large-v3` 效果最佳
- 提供上下文 prompt：
  ```bash
  whisper audio.mp3 --model medium \
    --language zh \
    --initial_prompt "这是一个关于Python编程的技术教程视频"
  ```

### 问题3：转录速度太慢
**解决方案**：
- 使用 faster-whisper 替代原生 Whisper
- 在 GPU 上运行（CUDA）
- 选择更小的模型（base/tiny）做快速预览

### 问题4：音频损坏或无声音
**解决方案**：
```bash
# 先检查音频流
ffprobe -i input.mp4

# 重新编码音频
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 output.wav
```

### 问题5：Whisper 模型下载慢
**解决方案**：
```bash
# 模型路径：~/.cache/whisper
# 手动下载：https://openaipublic.azureedge.net/main/whisper/models
# 下载 large-v3 模型到本地后指定路径
whisper audio.mp3 --model_path /path/to-large-v3.pt
```

---

## 高级用法

### 批量处理脚本

```bash
#!/bin/bash
# batch_transcribe.sh

INPUT_DIR="./videos"
OUTPUT_DIR="./transcripts"
MODEL="medium"
LANG="zh"

mkdir -p "$OUTPUT_DIR"

for file in "$INPUT_DIR"/*.{mp4,mp3,m4a}; do
  [ -e "$file" ] || continue
  filename=$(basename "$file")
  echo "Processing: $filename"
  
  # 提取音频
  if [[ "$file" == *.mp4 ]]; then
    ffmpeg -i "$file" -vn -acodec libmp3lame -q:a 2 "$OUTPUT_DIR/temp.mp3" -y
    audio_file="$OUTPUT_DIR/temp.mp3"
  else
    audio_file="$file"
  fi
  
  # Whisper 转录
  whisper "$audio_file" \
    --model "$MODEL" \
    --language "$LANG" \
    --output_format txt \
    --output_dir "$OUTPUT_DIR"
  
  # 清理临时文件
  rm -f "$OUTPUT_DIR/temp.mp3"
  
  echo "Done: ${filename}.txt"
done
```

### 使用 Whisper API（无需本地模型）

```bash
# 通过 OpenClaw 内置脚本
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a \
  --model whisper-1 \
  --language zh \
  --out /tmp/transcript.txt \
  --prompt "技术教程，包含 Python 和机器学习相关内容"
```

### 生成字幕文件（SRT/VTT）

```bash
# 生成 SRT 字幕（带时间戳）
whisper audio.mp3 --model medium --language zh --output_format srt

# 生成 VTT 字幕（网页字幕格式）
whisper audio.mp3 --model medium --language zh --output_format vtt
```

---

## 工具对比

| 方案 | 费用 | 速度 | 隐私 | 中文效果 | 适用场景 |
|------|------|------|------|----------|----------|
| yt-dlp + 本地 Whisper | 免费 | 中等（GPU快） | 高 | ⭐⭐⭐⭐⭐ | 批量/敏感内容 |
| yt-dlp + Whisper API | API费用 | 快 | 中 | ⭐⭐⭐⭐ | 偶尔使用 |
| summarize 工具 | API费用 | 快 | 中 | ⭐⭐⭐⭐ | 快速总结 |
| videos_understand | 使用内置配额 | 中 | 中 | ⭐⭐⭐⭐ | 深度理解 |

---

## 参考链接

- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp B站支持文档](https://github.com/yt-dlp/yt-dlp#supported-sites)
- [OpenAI Whisper](https://openai.com/research/whisper)
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [OpenClaw openai-whisper Skill](/app/openclaw/skills/openai-whisper/SKILL.md)
- [OpenClaw openai-whisper-api Skill](/app/openclaw/skills/openai-whisper-api/SKILL.md)
