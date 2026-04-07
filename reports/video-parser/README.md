# 视频解析方法知识库

> 🤖 视频解析方法总结Agent | 更新时间：2026-04-06

---

## 📁 目录结构

```
video-parser/
├── README.md                    ← 你在这里
├── 索引与总览.md                ← 方法索引与快速对照
│
├── 技术教程类/
│   ├── FFmpeg+summarize解析法.md   ← FFmpeg帧提取 + summarize总结
│   └── OpenClaw视频理解Skill解析.md ← video-learn + videos_understand
│
├── 行业分享类/
│   └── 行业分享视频解析方法.md       ← 演讲/峰会/KOL分享内容提取
│
├── 开源项目演示类/
│   └── 开源项目演示解析方法.md       ← GitHub Demo/工具演示/Conference
│
└── 社媒内容类/
    └── MCP-parse-video解析法.md     ← 抖音/快手/小红书/B站链接解析
```

---

## 🛠️ 方法总表

| # | 方法名 | 核心工具 | 适合视频类型 | 难度 | 免费？ |
|---|--------|---------|------------|------|--------|
| 1 | 帧提取法 | FFmpeg | 技术教程/开源演示 | ⭐ | ✅ |
| 2 | 快速总结法 | summarize CLI | 各类视频 | ⭐ | ✅ |
| 3 | 多模态深度理解 | videos_understand | 各类视频 | ⭐⭐ | ✅ |
| 4 | MCP链接解析 | parse_video MCP | 社媒平台 | ⭐ | ✅ |
| 5 | Whisper转写 | Whisper | 有音频视频 | ⭐⭐ | ✅ |
| 6 | OpenClaw Skill | video-learn | YouTube/B站 | ⭐ | ✅ |

---

## 🚀 快速决策树

```
输入视频类型
│
├─ 平台分享链接（抖音/快手/小红书/B站）
│   └→ MCP parse_video → videos_understand → 内容报告
│
├─ YouTube链接
│   └→ summarize --youtube auto → videos_understand
│
├─ 本地视频文件（技术教程）
│   └→ ffmpeg提取帧 → videos_understand → 结构化知识提取
│
├─ 行业分享/演讲
│   └→ summarize → videos_understand → 观点+案例整理
│
└─ 开源项目演示
    └→ videos_understand（操作还原）→ ffmpeg截图 → 完整演示报告
```

---

## 📊 工具能力对照表

| 能力 | FFmpeg | summarize | videos_understand | MCP parse_video | Whisper |
|------|--------|-----------|-------------------|-----------------|---------|
| 提取视频帧 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 总结要点 | ❌ | ✅ | ✅ | ❌ | ❌ |
| 深度内容理解 | ❌ | ⚠️ | ✅ | ❌ | ❌ |
| 解析平台链接 | ❌ | ⚠️ | ❌ | ✅ | ❌ |
| 语音转文字 | ❌ | ✅ | ❌ | ❌ | ✅ |
| 下载无水印视频 | ❌ | ⚠️ | ❌ | ✅ | ❌ |
| 视频格式转换 | ✅ | ❌ | ❌ | ❌ | ❌ |

✅ 完全支持 | ⚠️ 部分支持/需要配置 | ❌ 不支持

---

## 🔄 常见组合方案

### 方案1：5分钟快速了解（内容量≤10分钟）
```
summarize "URL" --youtube auto --length medium
```

### 方案2：深度学习模式（教程/演讲，≥30分钟）
```
summarize --extract-only + videos_understand + ffmpeg切分精华片段
```

### 方案3：社媒素材采集（抖音/小红书）
```
MCP parse_video → download.py → videos_understand → 内容分析报告
```

### 方案4：开源项目演示还原
```
videos_understand（操作步骤还原）→ ffmmpeg提取关键帧 → 演示步骤文档
```

---

## 📝 维护记录

| 日期 | 更新内容 |
|------|---------|
| 2026-04-06 | 初始化知识库，整理5大类解析方法 |
