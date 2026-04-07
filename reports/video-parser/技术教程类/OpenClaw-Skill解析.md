# 技术教程类视频 - OpenClaw Skill解析

## 核心工具/API

| 工具 | 功能描述 | 路径/命令 |
|------|----------|----------|
| **videos_understand** | 内置LLM视频理解，支持批量分析 | 工具直接调用 |
| **summarize** | YouTube/B站直解析，提取字幕/摘要 | `summarize "<url>" --youtube auto` |
| **openai-whisper** | 本地Whisper CLI转录，无需API Key | `whisper audio.mp3 --model medium` |
| **openai-whisper-api** | OpenAI Whisper API转录（需Key） | `transcribe.sh audio.m4a --json` |
| **video-frames** | ffmpeg关键帧提取，截图分析 | `frame.sh video.mp4 --time HH:MM:SS` |
| **yt-dlp** | 音视频下载，支持1800+网站 | `/app/.venv/bin/yt-dlp <url>` |

---

## 步骤流程

### 方案A：一站式LLM理解（推荐⭐⭐⭐）
```
1. 获取视频URL或本地路径
2. 调用 videos_understand(video_url=url, prompt="提取技术教程的关键步骤、代码片段、命令要点")
3. LLM输出结构化技术要点
```

### 方案B：字幕转录 + LLM分析（适合长视频）
```
1. yt-dlp -x --audio-format mp3 <video-url>    # 提取音频
2. whisper audio.mp3 --model medium --output_format srt  # 生成字幕
3. videos_understand(video_file="audio.srt", prompt="按技术步骤整理要点")  # LLM分析
```

### 方案C：关键帧 + 图像分析（适合GUI操作教程）
```
1. frame.sh tutorial.mp4 --time 00:02:00 --out frame1.jpg   # 提取关键帧
2. frame.sh tutorial.mp4 --time 00:05:30 --out frame2.jpg
3. images_understand(images=[{file:"frame1.jpg", prompt:"描述界面和操作"}])
4. 汇总所有截图分析结果
```

### 方案D：summarize CLI（最快）
```
summarize "https://youtu.be/xxxx" --youtube auto --extract-only
summarize "https://youtu.be/xxxx" --youtube auto --length medium
```

---

## 适用场景

- **编程教学**：Python/JS/AI框架教学视频，提取代码片段和命令
- **工具使用**：OpenClaw Skill开发、CLI工具教程
- **GUI操作演示**：截图 + 语音双通道分析
- **长课程**：分段转录 + 分段理解
- **无字幕视频**：whisper强制转录

---

## 避坑指南

### 问题1：视频无法访问/被平台限流
**解决方案**：
- 使用 `yt-dlp --list-subs <url>` 先检查字幕 availability
- 设置UA或Cookie：`yt-dlp --user-agent "..." --cookies-from-browser chrome`
- fallback到 `summarize` 的 Apify 模式：`--youtube auto`（需 APIFY_API_TOKEN）

### 问题2：whisper转录速度慢
**解决方案**：
- 小模型加速：`--model tiny`（最快）或 `--model base`（平衡）
- GPU优先：确保CUDA可用，`nvidia-smi` 检查
- 分段处理：先 `yt-dlp` 分段下载，再逐段转录

### 问题3：videos_understand 有时长限制
**解决方案**：
- 超过限制时，先用 `whisper` 转文字，再用 LLM 分析文字稿
- 或截取视频精华片段：`ffmpeg -ss 00:10:00 -i video.mp4 -t 00:05:00 -c copy clip.mp4`

### 问题4：技术教程含大量代码，字幕识别不准
**解决方案**：
- 使用 `openai-whisper-api` 的 `--prompt` 参数注入上下文：`--prompt "Python, PyTorch, OpenAI API, Hugging Face"`
- 或在 `videos_understand` prompt 中明确要求"精确转录代码片段"

---

## 参考链接

- OpenClaw Skill - video-frames: `/app/openclaw/skills/video-frames/SKILL.md`
- OpenClaw Skill - whisper: `/app/openclaw/skills/openai-whisper/SKILL.md`
- OpenClaw Skill - summarize: `/app/openclaw/skills/summarize/SKILL.md`
- yt-dlp 文档: `https://github.com/yt-dlp/yt-dlp`
- Whisper 论文: `https://openai.com/research/whisper`
