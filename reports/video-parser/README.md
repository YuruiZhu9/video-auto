# 视频解析方法总结 - 索引

> 📅 更新日期：2026-04-11
> 🤖 维护者：视频解析方法总结Agent

---

## 📁 目录结构

```
video-parser/
├── README.md（本文档）
├── 技术教程类/
│   ├── OpenClaw-Skill解析.md
│   ├── Whisper语音转写解析.md
│   └── FFmpeg关键帧提取解析.md
├── 行业分享类/
│   ├── YouTube视频解析.md
│   └── GPT-4o多模态视频理解.md
└── 开源项目演示类/
    ├── OpenCV关键帧提取解析.md
    └── 智能视频摘要系统.md
```

---

## 🎯 解析方法总览

| 方法 | 核心工具 | 适用场景 | 难度 |
|------|---------|---------|------|
| 语音转写解析 | Whisper / summarize | 有语音的技术教程 | ⭐ |
| 关键帧+AI分析 | FFmpeg + GPT-4V | 视觉信息丰富的视频 | ⭐⭐ |
| 多模态端到端 | GPT-4o / Claude | 快速结构化理解 | ⭐ |
| 开源自主方案 | OpenCV + LLM | 私有化部署/定制 | ⭐⭐⭐ |

---

## 🔥 快速选择指南

**场景1：YouTube技术教程**
→ 首选：`summarize` Skill（OpenClaw内置）
→ 备选：Whisper + GPT-4 二次加工

**场景2：本地视频，视觉信息密集**
→ 首选：`videos_understand`（OpenClaw内置多模态理解）
→ 备选：FFmpeg抽帧 → images_understand → 结构化输出

**场景3：需要实时/大批量处理**
→ 首选：Whisper API + LLM pipeline
→ 备选：本地 Whisper + Ollama 本地模型

**场景4：开源可控，要求私有化**
→ FFmpeg + OpenCV + 本地 Whisper + 开源LLM（如Qwen、DeepSeek）

---

## 🛠️ OpenClaw 内置工具速查

| 工具名称 | 功能 | 使用门槛 |
|---------|------|---------|
| `videos_understand` | AI视频内容理解 | 直接可用 |
| `audios_understand` | 音频内容分析 | 直接可用 |
| `video-frames` (Skill) | FFmpeg抽帧 | ffmpeg可用 |
| `summarize` (Skill) | YouTube/URL视频摘要 | summarize CLI |

---

*持续更新中...*

---

## 📋 本次更新内容（2026-04-11）

### 新增文档

| 分类 | 文档 | 核心方法 |
|------|------|---------|
| 技术教程类 | OpenClaw-Skill解析.md | summarize + videos_understand + video-frames |
| 技术教程类 | Whisper语音转写解析.md | Whisper/GPT-4o-transcribe 完整 Pipeline |
| 技术教程类 | FFmpeg关键帧提取解析.md | FFmpeg/FFmpeg+OpenCV/scene-detect |
| 行业分享类 | GPT-4o多模态视频理解.md | GPT-4o/Gemini/智谱GLM-4V 全方案 |
| 开源项目演示类 | OpenCV智能关键帧提取.md | 光流法/直方图/镜头检测 |
| 开源项目演示类 | 智能视频摘要系统.md | 完整 Pipeline 架构代码 |
