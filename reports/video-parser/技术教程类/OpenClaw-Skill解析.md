# 技术教程类 - OpenClaw Skill 解析方案

## 核心工具/API

- **summarize（OpenClaw Skill）**
  - 功能：URL/YouTube/本地文件 summarization + 字幕提取
  - 依赖：`summarize` CLI（brew 安装）
  - 模型支持：OpenAI GPT / Anthropic Claude / Google Gemini / xAI
  - YouTube 字幕：支持自动 fallback（Apify token）

- **video-frames（OpenClaw Skill）**
  - 功能：从视频提取单帧/缩略图
  - 依赖：`ffmpeg`
  - 支持时间戳指定、帧索引指定

- **videos_understand（OpenClaw 内置工具）**
  - 功能：多模态 LLM 视频理解
  - 支持：视频文件路径 / URL
  - 最大10个视频并发分析

## 步骤流程

### 方案A：YouTube 技术教程（summarize）
```bash
# 快速总结
summarize "https://youtu.be/VIDEO_ID" --youtube auto

# 仅提取字幕/转写（不总结）
summarize "https://youtu.be/VIDEO_ID" --youtube auto --extract-only

# 指定长度
summarize "https://youtu.be/VIDEO_ID" --youtube auto --length long

# 本地 PDF/文件
summarize "/path/to/slides.pdf" --model google/gemini-3-flash-preview
```

### 方案B：本地视频帧提取（video-frames）
```bash
# 提取第一帧
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg

# 指定时间戳
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:05:30 --out /tmp/frame-5min.jpg

# 按帧索引提取
{baseDir}/scripts/frame.sh /path/to/video.mp4 --index 0 --out /tmp/frame0.png
```

### 方案C：本地视频深度理解（videos_understand）
```python
# OpenClaw 内置工具调用
videos_understand(
  videos_info=[
    {
      "file": "/path/to/video.mp4",
      "prompt": "请详细描述这个技术教程视频的核心内容、关键步骤和代码要点"
    }
  ]
)
```

## 适用场景

- ✅ YouTube 技术教程/课程视频
- ✅ 技术分享会议录像
- ✅ 开源项目 README 配套视频
- ✅ API 文档演示视频
- ✅ 工具使用教程（SaaS / CLI / 框架）

## 避坑指南

- **坑1：YouTube 无字幕**
  - 解决：设置 `APIFY_API_TOKEN` 作为 fallback，summarize 会自动切换
  - 注意：部分视频确实无字幕（直播回放、老视频），需手动转写

- **坑2：视频太长被截断**
  - 解决：summarize 默认有输出 token 限制，长视频先 `--extract-only` 获取完整内容
  - 再分段发送给 LLM 分析

- **坑3：ffmpeg 未安装**
  - 解决：macOS `brew install ffmpeg`，Linux `apt install ffmpeg`
  - OpenClaw 会提示安装，但手动安装更可控

- **坑4：视频格式不支持**
  - 解决：FFmpeg 支持几乎所有格式；videos_understand 支持 mp4/webm/avi
  - .mkv 等特殊格式用 FFmpeg 转码：`ffmpeg -i input.mkv -c copy output.mp4`

- **坑5：API Key 未设置**
  - 解决：设置环境变量 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY`
  - 或配置 `~/.summarize/config.json`

## 参考链接

- OpenClaw summarize Skill：https://summarize.sh
- OpenClaw video-frames Skill：https://ffmpeg.org
- OpenClaw videos_understand：内置工具（无需安装）
