# 📚 视频解析方法知识库

> 本知识库由**视频解析方法总结Agent**自动维护  
> 更新时间：2026-04-09

---

## 📂 目录结构

```
video-parser/
├── README.md（本索引文件）
├── 技术教程类/
│   ├── OpenClaw-Skill解析.md
│   ├── Python工具解析.md
│   └── AI大模型视频理解.md
└── 行业分享类/
│   └── 行业视频结构化提取.md
└── 开源项目演示类/
    └── 开源项目演示视频解析.md
```

---

## 🎯 解析方法总览

| 方法 | 核心工具 | 适用场景 | 难度 |
|------|---------|---------|------|
| 字幕/音频转录 | Whisper / summarize | 含语音的技术教程 | ⭐ |
| 关键帧提取 | FFmpeg / video-frames-skill | 视觉密集型内容 | ⭐⭐ |
| AI多模态理解 | Gemini / GPT-4V / Video Analyzer | 深度内容分析 | ⭐⭐⭐ |
| 开源框架管道 | VideoPipe / yt-dlp | 自动化大规模处理 | ⭐⭐⭐ |

---

## 🔄 更新记录

| 日期 | 更新内容 |
|------|---------|
| 2026-04-09 | 初始化知识库，建立三大分类框架 |

---

## 💡 使用建议

- **快速了解视频内容** → `summarize` 命令（一键）
- **提取精确帧/截图** → `video-frames` Skill（FFmpeg）
- **获取完整字幕稿** → `summarize --youtube --extract-only`
- **深度视觉分析** → `video-analyzer`（Whisper + Vision模型）
- **批量自动化处理** → VideoPipe 框架

---

## 🛠️ 开源项目演示类

| 方法 | 核心工具 | 适用场景 | 推荐指数 |
|------|---------|---------|---------|
| 快速帧提取 | yt-dlp + video-frames-skill | Demo 视频批量分析 | ⭐⭐⭐⭐ |
| 结构化分析 | VideoPipe 框架 | CV 类 Demo 定量统计 | ⭐⭐⭐ |
| 一键总结 | summarize | 快速了解 Demo 内容 | ⭐⭐⭐⭐⭐ |
