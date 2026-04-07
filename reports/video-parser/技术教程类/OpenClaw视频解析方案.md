# [技术教程类] - OpenClaw视频帧提取 + Whisper转录方案

## 核心工具/API

- **video-frames Skill**：OpenClaw 内置，基于 `ffmpeg` 的视频帧提取工具
  - 脚本路径：`/app/openclaw/skills/video-frames/scripts/frame.sh`
  - 支持按时间戳（`--time`）或帧序号（`--index`）精确提取单帧
  - 输出格式：`.jpg`（快速分享）或 `.png`（高保真 UI 帧）
- **openai-whisper Skill**：本地 Whisper CLI，无需 API Key
  - 支持模型：turbo（默认）/ small / medium / large
  - 输出格式：`.txt` / `.srt` / `.json`
  - 任务类型：transcribe / translate
- **openai-whisper-api Skill**：OpenAI Whisper API 版本，需 `OPENAI_API_KEY`
  - 脚本：`/app/openclaw/skills/openai-whisper-api/scripts/transcribe.sh`
  - 支持 `--language` / `--prompt` 参数
- **summarize Skill**：支持直接解析 YouTube/B站视频链接
  - 命令：`summarize "<url>" --youtube auto --extract-only`
  - 自动转录 + AI 总结，无需 yt-dlp 手动下载

## 步骤流程

1. **提取字幕/转录文本**
   - 方案A（本地无API）：`whisper video.mp4 --model medium --output_format srt`
   - 方案B（有APIKey）：`transcribe.sh audio.m4a --model whisper-1 --language zh`
   - 方案C（链接直达）：`summarize "https://youtu.be/xxx" --youtube auto --extract-only`

2. **提取关键帧**
   - 按时间戳提取：`frame.sh video.mp4 --time 00:05:30 --out /tmp/frame.jpg`
   - 批量采样：循环调用或写脚本批量导出（如每30秒一帧）

3. **AI 视觉分析帧内容**
   - 将帧图发送给视觉模型（GPT-4o / Claude / Gemini）做内容描述
   - 用 `images_understand` 工具批量分析

4. **结构化输出**
   - 将时间轴字幕 + 帧描述整合为 Markdown 结构
   - 可导出 JSON 格式便于后续自动化处理

## 适用场景

- 编程教学视频（Python/AI/ML 类）步骤拆解
- 工具使用教程的结构化笔记
- 技术大会演讲的精华提炼
- 软件功能演示的分段标注

## 避坑指南

- **字幕下载失败**：B站/抖音视频需先下载，summarize Skill 对 B站支持好，抖音可能需 yt-dlp 先下载再用 Whisper 转录
- **Whisper 模型选择**：小模型速度快但中文识别准确率低；推荐 medium 或 large 模型做中文教程
- **帧提取时间点**：教程视频节奏快，建议按字幕时间戳定位，而非均匀采样
- **长视频处理**：超过 1 小时的视频建议分段处理，避免单次 LLM 调用 token 超限

## 参考链接

- OpenClaw video-frames Skill：`/app/openclaw/skills/video-frames/SKILL.md`
- OpenClaw Whisper Skill：`/app/openclaw/skills/openai-whisper/SKILL.md`
- OpenClaw summarize Skill：`/app/openclaw/skills/summarize/SKILL.md`
- FFmpeg 官方：https://ffmpeg.org
- Whisper 项目：https://github.com/openai/whisper
