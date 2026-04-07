# 行业分享类 — 视频内容 AI 提取方案

## 核心工具/API

- **videos_understand（内置多模态 LLM）**：直接上传视频或传 URL，LLM 输出结构化总结
- **summarize（YouTube 专用）**：无需下载，提取字幕或生成摘要，适合 B站/YouTube 行业分享
- **Whisper API**：将行业分享视频语音转文字，再喂给 GPT-4o 等 LLM 提取关键观点
- **Bilibili API / B站下载器**：解析 B站视频下载，获取字幕和弹幕信息

## 步骤流程

### 方法 A：videos_understand 直接分析

```
1. videos_understand 上传本地视频文件（mp4/avi/webm）
   prompt: "提取演讲的核心观点、主要论据、数据引用，按以下结构输出：
           【主题】【核心观点1-3】【关键数据】【金句摘录】"
2. LLM 自动分析音视频内容，输出结构化文本
```

### 方法 B：YouTube/B站行业分享提取

```
# 用 summarize 提取字幕
summarize "https://youtu.be/VIDEO_ID" --youtube auto --extract-only -o transcript.txt

# 用 summarize 直接生成摘要
summarize "https://youtu.be/VIDEO_ID" --model google/gemini-3-flash-preview --length medium

# 对于 B站视频（需下载后处理）
yt-dlp "https://www.bilibili.com/video/BVxxx" -o "video.mp4"
ffmpeg -i video.mp4 -vn audio.mp3
whisper audio.mp3 --model medium
```

### 方法 C：弹幕 + 字幕双轨提取（B站专用）

```
# yt-dlp 下载 B站视频时自动下载字幕
yt-dlp --write-subs --write-auto-subs --sub-lang zh-Hans,en \
       "https://www.bilibili.com/video/BVxxx" -o "video.%(ext)s"

# 弹幕提取（B站弹幕为 XML 格式）
yt-dlp --dump-json "https://www.bilibili.com/video/BVxxx" | jq "...comments"
```

## 适用场景

- 行业峰会、大咖演讲（如 OpenAI DevDay、CVPR 等）
- 产品发布会（苹果 WWDC、Google I/O 等）
- 商业洞察分享（36氪、虎嗅等媒体视频）
- 创业分享、投资人观点（Y Combinator、TechCrunch 等）
- B站知识区 Up 主内容存档

## 避坑指南

- **长视频分段**：行业分享常超过 30 分钟，建议按话题分段处理（用 Whisper 时间戳切分）
- **多语言识别**：英文分享指定 `--language en`，中文指定 `--language zh`，避免误识别
- **videos_understand 限制**：最大支持约 10 分钟视频，超长视频建议先切片
- **B站弹幕提取**：弹幕数量庞大，建议只提取高赞弹幕（按 like 数排序）
- **敏感内容**：部分行业分享涉及商业机密，输出结果注意保密

## 参考链接

- Bilibili API 文档：https://github.com/SocialSisterYi/bilibili-API-collect
- videos_understand 工具：内置于 OpenClaw，支持批量视频分析
- summarize CLI：https://summarize.sh
