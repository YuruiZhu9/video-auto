# 技术教程类 - OpenClaw Skill 解析方案

## 核心工具/API

- **summarize（Skill）**：OpenClaw 内置视频/URL 总结工具，支持 YouTube 自动字幕提取
  - 功能：快速提取视频核心内容，生成结构化摘要
  - 依赖：`summarize` CLI（brew 安装）
  - 支持模型：OpenAI / Anthropic / xAI / Google Gemini
- **videos_understand（内置工具）**：多模态视频理解，支持批量分析
  - 功能：直接理解视频内容，返回结构化文本描述
  - 支持最长 10 个视频并行分析
- **audios_understand（内置工具）**：音频内容分析
  - 功能：提取音频中的语音、背景音、音乐等元素
- **video-frames（Skill）**：FFmpeg 关键帧提取
  - 功能：从视频中抽取单帧或指定时间点的画面
  - 依赖：FFmpeg

---

## 步骤流程

### 方案一：summarize Skill（YouTube 教程类）

```
1. 确定视频 URL（YouTube / 通用链接）
2. 调用 summarize CLI：
   summarize "https://youtu.be/xxxx" --youtube auto --extract-only
   （--extract-only 仅提取字幕，不做总结，适合长视频）
3. 如需深度理解：
   summarize "https://youtu.be/xxxx" --youtube auto --length long
4. 输出：时间戳 + 字幕文本 / 结构化摘要
```

### 方案二：videos_understand（本地/URL 教程类）

```
1. 获取视频文件或 URL
2. 构造分析 prompt（如"请提取这个技术教程视频的核心知识点、步骤和代码片段"）
3. 调用 videos_understand：
   videos_understand([{
     file: "video.mp4",
     prompt: "作为技术教程分析师，请提取：1) 主题 2) 核心知识点列表 3) 操作步骤 4) 代码/命令"
   }])
4. AI 返回结构化分析结果
```

### 方案三：video-frames + images_understand（需精细视觉分析）

```
1. 用 FFmpeg 按时间间隔抽帧：
   ffmpeg -i video.mp4 -vf "fps=1/30" frames/%04d.jpg
   （每30秒抽一帧）
2. 批量调用 images_understand 分析关键帧：
   images_understand([{
     file: "frames/0001.jpg",
     prompt: "这段视频在讲什么？列出关键操作步骤"
   }])
3. 汇总各帧分析结果，生成完整教程解析
```

---

## 适用场景

- ✅ 技术教程类视频（编程教学、软件操作、工具使用）
- ✅ 知识分享类视频（概念讲解、原理说明）
- ✅ 有字幕/配音的教学视频
- ✅ 需要提取代码片段、操作步骤的教程
- ✅ 快速了解视频核心内容（5分钟内判断是否值得深入）

---

## 避坑指南

### ⚠️ 坑1：YouTube 自动字幕质量不稳定
- **问题**：自动字幕可能有错别字、时间轴不准
- **解决**：优先选择有官方字幕的视频；结合 `audios_understand` 验证关键术语

### ⚠️ 坑2：长视频超 Token 限制
- **问题**：超过模型上下文窗口时，内容被截断
- **解决**：
  - 用 `--extract-only` 提取字幕文本，手动分段
  - 分时间段多次调用 `videos_understand`

### ⚠️ 坑3：summarize CLI 模型配置缺失
- **问题**：未配置 API Key 时默认模型可能不支持中文
- **解决**：配置 `~/.summarize/config.json`，指定 `google/gemini-3-flash-preview`（免费额度大，支持中文）

### ⚠️ 坑4：FFmpeg 抽帧内存占用高
- **问题**：高分辨率视频大量抽帧会导致内存溢出
- **解决**：先用 `-vf scale=1280:720` 降分辨率再抽帧；控制帧率 `fps=1/60`

---

## 参考链接

- OpenClaw summarize Skill：`/app/openclaw/skills/summarize/SKILL.md`
- OpenClaw video-frames Skill：`/app/openclaw/skills/video-frames/SKILL.md`
- Whisper API 文档：https://developers.openai.com/api/docs/guides/speech-to-text
- GPT-4o-transcribe 指南：https://help.apiyi.com/gpt-4o-transcribe-apiyi-free-trial.html
