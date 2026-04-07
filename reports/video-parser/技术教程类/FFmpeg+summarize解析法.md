# 技术教程类 - FFmpeg帧提取 + summarize总结

## 核心工具/API

| 工具 | 功能描述 |
|------|---------|
| **FFmpeg** | 视频帧提取、片段剪辑、格式转换、字幕烧录 |
| **summarize CLI** | 快速总结URL/YouTube/本地文件内容 |
| **videos_understand** | 多模态大模型深度理解视频内容 |
| **Whisper** | 语音转字幕，支持多语言 |

## 步骤流程

### Step 1：获取视频
```bash
# 方式A：MCP解析平台链接（无需下载）
# 调用 parse_video MCP工具，传入分享链接

# 方式B：yt-dlp下载YouTube
yt-dlp -f "best[height<=720]" -o "%(title)s.%(ext)s" "URL"

# 方式C：ffmpeg直接读取网络流
ffmpeg -i "https://..." -t 60 -c copy snippet.mp4
```

### Step 2：提取关键帧（FFmpeg）
```bash
# 提取第一帧（封面）
ffmpeg -i tutorial.mp4 -vf "select=eq(n\,0)" -vframes 1 cover.jpg

# 提取指定时间戳帧
ffmpeg -i tutorial.mp4 -ss 00:05:30 -vframes 1 keyframe.jpg

# 均匀抽取10帧（用于概览）
ffmpeg -i tutorial.mp4 -vf "fps=10/duration" -q:v 2 thumb%03d.jpg

# 切分精华片段（时间范围）
ffmpeg -i tutorial.mp4 -ss 00:10:00 -t 00:05:00 -c copy segment.mp4
```

### Step 3：快速总结（summarize）
```bash
# YouTube视频总结
summarize "https://youtu.be/xxxxx" --youtube auto

# 提取字幕/文字稿
summarize "https://youtu.be/xxxxx" --youtube auto --extract-only

# 指定长度
summarize "URL" --length medium --model google/gemini-3-flash-preview
```

### Step 4：深度内容理解（videos_understand）
```
输入：视频文件路径或URL
提示词：分析这个技术教程视频，提取：
  1. 视频主题和难度级别
  2. 主要知识点列表（带时间戳）
  3. 代码/命令示例
  4. 关键配图说明
  5. 学习建议
```

## 适用场景

- 编程教学视频（Python/JS/AI等）
- 工具使用教程（Photoshop/FFmpeg/ Blender等）
- 软件安装配置教程
- 学术/科研方法演示视频
- 技能培训/认证备考视频

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 字幕乱码 | 编码格式不对 | 加 `-encodings all` 或用 `ffprobe` 查看编码 |
| 视频太长 summarzie 超时 | token限制 | 先 `ffmpeg -ss 0 -t 300` 切前5分钟 |
| Whisper转写慢 | CPU太慢 | 用 `whisper --model medium --device cuda` |
| 提取帧太多磁盘爆满 | fps设置过高 | 控制 `fps=1` 或 `fps=0.5` |
| 平台链接解析失败 | 短链或分享文案格式 | 复制完整分享文案（包含链接部分） |

## 参考链接

- FFmpeg官方：https://ffmpeg.org
- summarize CLI：https://summarize.sh
- Whisper：https://github.com/openai/whisper
- OpenClaw video-frames skill：`/app/openclaw/skills/video-frames/SKILL.md`
