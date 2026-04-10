# 视频解析方法总结 - 总索引

> 🤖 维护者：视频解析方法总结Agent
> 📅 更新日期：2026-04-10
> 📁 版本：v1.0

---

## 📂 目录结构

```
video-parser/
├── README.md                      ← 本文件
├── 技术教程类/
│   ├── OpenClaw-Skill解析.md      ← OpenClaw 内置技能解析
│   ├── Whisper语音转写解析.md      ← Whisper 本地/API 方案
│   ├── yt-dlp视频解析.md          ← yt-dlp 下载+字幕提取
│   └── FFmpeg关键帧提取解析.md     ← FFmpeg 帧提取方法
├── 行业分享类/
│   ├── 多模态LLM解析.md            ← GPT-4o/Gemini 视频理解
│   └── 视频结构化框架解析.md        ← VideoPipe 等框架
└── 开源项目演示类/
    ├── keyframe-scout解析.md       ← 智能关键帧提取
    └── 完整Pipeline方案.md          ← 端到端解析流程
```

---

## 🎯 解析维度总览

| 维度 | 描述 |
|------|------|
| 核心工具 | 用到的技术手段（API/CLI/框架） |
| 步骤流程 | 从视频到结构化输出的完整流程 |
| 适用场景 | 什么类型的视频适合该方法 |
| 避坑指南 | 常见问题和注意事项 |
| 参考链接 | 相关文档/工具链接 |

---

## 📊 方法对比速查表

| 方法 | 适合视频类型 | 离线 | 难度 | 速度 | 费用 |
|------|------------|------|------|------|------|
| OpenClaw summarize (YouTube) | YouTube视频 | ❌ | ⭐ | 快 | 免费 |
| OpenClaw video-frames + LLM | 任意视频 | ✅ | ⭐⭐ | 中 | API费 |
| Whisper 本地转写 | 任意音频 | ✅ | ⭐⭐ | 慢 | 免费 |
| yt-dlp 字幕提取 | YouTube/多平台 | ❌ | ⭐ | 快 | 免费 |
| FFmpeg 关键帧 | 任意视频 | ✅ | ⭐⭐ | 快 | 免费 |
| GPT-4o/Gemini 多模态 | 任意视频 | ❌ | ⭐⭐ | 中 | API费 |
| keyframe-scout | 任意视频 | ✅ | ⭐⭐ | 中 | 免费 |

---

## 🔄 执行流程建议

### 流程1：YouTube 视频快速解析（推荐）
```
summarize "YouTube_URL" --youtube auto --extract-only
→ 自动获取字幕/转写 → LLM 总结
```

### 流程2：本地视频完整解析
```
1. FFmpeg 提取关键帧（video-frames skill）
2. Whisper 本地转写（openai-whisper skill）
3. 多模态 LLM 理解（GPT-4o/Gemini）
4. 结构化输出（JSON/Markdown）
```

### 流程3：技术教程深度解析
```
1. yt-dlp 下载 + 字幕提取
2. WhisperX 精确时间戳转写
3. 结构化拆分（章节/步骤/代码片段）
4. 知识库录入
```

---

*本索引会随新增方法持续更新*
