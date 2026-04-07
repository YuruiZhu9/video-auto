# 开源项目演示类视频 - 项目Demo解析

## 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| **videos_understand** | LLM理解项目演示全流程 |
| **video-frames (ffmpeg)** | 提取关键操作帧（代码编辑/终端命令/效果展示） |
| **images_understand** | 分析IDE截图、终端输出、UI效果 |
| **whisper** | 转录演示者讲解（配合代码操作） |
| **yt-dlp** | 下载GitHub Release/YouTube Demo视频 |

---

## 步骤流程

### 开源项目Demo标准解析流程

```
1. 下载视频
   yt-dlp <demo-video-url>

2. 场景化帧提取
   ┌─────────────────────────────────────────────┐
   │ 时间点         │ 提取内容          │ 用途    │
   ├─────────────────────────────────────────────┤
   │ 00:00:xx       │ 项目首页/Logo      │ 项目定位│
   │ 00:02:00       │ README/介绍页      │ 项目概述│
   │ 00:05:00       │ 安装/配置过程      │ 快速上手│
   │ 00:10:00       │ 核心功能演示       │ 功能拆解│
   │ 00:15:00       │ 代码编辑特写       │ 实现细节│
   │ 00:20:00       │ 终端输出/日志      │ 运行验证│
   │ 00:25:00       │ UI/效果展示        │ 体验评估│
   │ 00:30:00       │ 项目总结/对比      │ 价值判断│
   └─────────────────────────────────────────────┘

3. 图像批量分析
   images_understand(images=[
     {file:"frame-intro.jpg", prompt:"描述这是什么项目，有哪些亮点"},
     {file:"frame-install.jpg", prompt:"列出安装步骤和关键命令"},
     {file:"frame-code.jpg", prompt:"转录这段代码的核心逻辑"},
     {file:"frame-output.jpg", prompt:"描述输出结果，判断是否符合预期"}
   ])

4. 整体评估
   videos_understand(
     video_file=<local-path>,
     prompt="这是一个开源项目演示视频。请按以下格式输出评估报告：\n1.项目概述 2.核心功能 3.技术亮点 4.快速上手路径 5.与同类项目对比 6.是否值得跟进"
   )
```

---

## 适用场景

- **GitHub Repo Demo**：README中嵌入的演示视频
- **Product Hunt 首发**：新产品演示视频
- **技术博主评测**：对比测评类Demo视频
- **官方宣传片**：了解项目定位和使用方式
- **Conference Demo**：顶会Demo视频

---

## 解析维度清单

| 维度 | 提取内容 |
|------|----------|
| **项目定位** | 这个项目解决什么问题？ |
| **核心功能** | 列出主要功能点和演示效果 |
| **技术栈** | 用到了哪些技术/框架？ |
| **代码质量** | 代码结构、可读性、架构设计 |
| **易用性** | 安装配置复杂度，文档质量 |
| **差异化** | 与同类开源项目相比的优势 |
| **社区活跃度** | 结合GitHub信息判断（star/fork/contributor）|

---

## 避坑指南

### 问题1：Demo视频节奏快，关键操作一闪而过
**解决方案**：
- 使用 `ffmpeg` 慢速播放提取帧：`ffmpeg -ss 00:10:00 -i video.mp4 -frames:v 1 -r 0.1 frame.jpg`
  （`-r 0.1` 表示每秒0.1帧，即10秒提取1帧）
- 使用 `frame.sh --index N` 按帧号精确定位

### 问题2：终端输出文字小，难以OCR识别
**解决方案**：
- 先放大：`ffmpeg -i terminal.jpg -vf scale=3840:2160 terminal_hd.jpg`
- 用 `images_understand` 并指定 `"prompt": "请仔细辨认这段终端输出的内容"`
- 或用 Tesseract OCR 提取文本：`tesseract terminal.jpg stdout`

### 问题3：视频中代码语法高亮导致OCR误识别
**解决方案**：
- 依赖 `images_understand` 的自然语言理解能力（不依赖OCR）
- 明确 prompt：`"这是一段代码截图，请转录完整代码"`

### 问题4：如何评估项目的工程价值（不仅是功能）？
**解决方案**：
- 结合帧分析看代码架构设计
- 观察是否有测试、CI/CD、文档
- 留意作者是否提及设计决策和权衡（trade-offs）

---

## 参考链接

- OpenClaw Skill - video-frames: `/app/openclaw/skills/video-frames/SKILL.md`
- OpenClaw Skill - videos_understand: 内置工具文档
- ffmpeg 文档: `https://ffmpeg.org/ffmpeg.html`
- yt-dlp: `https://github.com/yt-dlp/yt-dlp`
