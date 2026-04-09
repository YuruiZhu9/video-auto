# 技术教程类 - OpenClaw 内置 Skill 解析

> 适合对象：技术教程、操作演示类视频，需要提取语音/字幕/关键步骤

---

## 方法一：summarize 命令（推荐 · 一键搞定）

### 核心工具
- **工具**：summarize（OpenClaw 内置 Skill，`summarize.sh`）
- **说明**：快速总结 URL、YouTube 视频、本地文件，支持字幕提取和 AI 总结
- **安装**：`brew install steipete/tap/summarize`

### 步骤流程
```
1. 确定视频 URL（如 YouTube 链接）
2. 一键执行：summarize "https://youtu.be/xxx" --youtube auto
3. 等待 AI 自动完成字幕提取 + 总结
4. 如需纯字幕：加 --extract-only 参数
5. 输出 txt/srt 格式的字幕稿
```

### 适用场景
- YouTube / B站 等平台教程视频
- 需要快速了解视频讲了什么
- 只需要文字记录，不需要视频帧

### 避坑指南
- ⚠️ 字幕依赖平台是否开放字幕接口，部分视频可能失败
- ⚠️ 长视频（>1小时）总结较长，建议加 `--length short` 限制长度
- ⚠️ 设置 `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` 环境变量

---

## 方法二：video-frames Skill（FFmpeg 驱动）

### 核心工具
- **工具**：FFmpeg（OpenClaw 内置 Skill）
- **Skill 路径**：`/app/openclaw/skills/video-frames/SKILL.md`
- **说明**：按帧号或时间戳提取视频中的单帧图片

### 步骤流程
```
1. 确认 ffmpeg 已安装（系统依赖）
2. 提取第一帧（缩略图）：frame.sh video.mp4 --out /tmp/frame.jpg
3. 指定时间戳截取：frame.sh video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
4. 获取视频信息：ffmpeg -i video.mp4（查看总时长/帧率/分辨率）
```

### 适用场景
- 需要视频关键画面的截图
- 生成视频封面/缩略图
- 截取某个具体时间点展示的操作画面

### 避坑指南
- ⚠️ 时间格式：使用 `--time HH:MM:SS` 标准格式
- ⚠️ 分享用途用 `.jpg`，高清用途用 `.png`
- ⚠️ 若要批量提取帧，参考 `video-frames-skill`（clawhub 安装版）

---

## 方法三：openai-whisper Skill（本地语音转文字）

### 核心工具
- **工具**：Whisper CLI（OpenAI 开源模型）
- **Skill 路径**：`/app/openclaw/skills/openai-whisper/SKILL.md`
- **说明**：本地离线将视频/音频转录为文字

### 步骤流程
```
1. 从视频提取音频：ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav
2. 选择模型并转录：
   - whisper audio.wav --model medium --output_format txt --output_dir .
   - whisper audio.wav --model base --output_format srt --output_dir .
3. 得到 .txt（纯文字稿）或 .srt（带时间轴字幕）
```

### 模型选择建议
| 模型 | 速度 | 准确率 | 适用场景 |
|------|------|--------|---------|
| tiny | 最快 | 一般 | 快速预览 |
| base | 快 | 尚可 | 普通英语/中文 |
| small | 中等 | 较好 | 日常内容 |
| medium | 慢 | 高 | 专业术语 |
| large | 最慢 | 最高 | 高要求场景 |

### 适用场景
- 无字幕的教程视频本地转录
- 会议录音/播客转文字
- 需要带时间轴的字幕文件（用于视频剪辑）

### 避坑指南
- ⚠️ 首次运行自动下载模型到 `~/.cache/whisper`，需留足空间
- ⚠️ 中文视频推荐 medium 以上模型，小模型中文识别差
- ⚠️ 音频质量差会导致识别率大幅下降，先预处理降噪

---

## 方法四：summarize --extract-only（字幕提取专用）

### 核心工具
- **工具**：summarize + yt-dlp
- **说明**：不调用 AI，直接提取平台字幕文本

### 步骤流程
```
1. 提取 YouTube 字幕：summarize "https://youtu.be/xxx" --youtube auto --extract-only
2. 提取 B站 字幕：summarize "https://www.bilibili.com/video/xxx" --extract-only
3. 输出纯字幕文本文件
```

### 适用场景
- 只需要字幕文本，不需要 AI 总结
- 后续自行用 LLM 处理字幕
- 大批量提取积累语料库

### 避坑指南
- ⚠️ 仅限有字幕的视频，无字幕视频返回空
- ⚠️ 部分视频有硬字幕（烧录在画面中）无法提取，需用 Whisper

---

## 方法对比

| 方法 | 速度 | 字幕质量 | 帧提取 | 总结 | 推荐指数 |
|------|------|---------|--------|------|---------|
| summarize | 快 | 依赖平台 | ❌ | ✅ | ⭐⭐⭐⭐⭐ |
| video-frames | 快 | ❌ | ✅ | ❌ | ⭐⭐⭐⭐ |
| whisper | 慢 | 高（本地） | ❌ | ❌ | ⭐⭐⭐⭐ |
| summarize --extract | 快 | 中 | ❌ | ❌ | ⭐⭐⭐ |

---

## 参考链接
- OpenClaw summarize Skill：`/app/openclaw/skills/summarize/SKILL.md`
- OpenClaw video-frames Skill：`/app/openclaw/skills/video-frames/SKILL.md`
- OpenClaw whisper Skill：`/app/openclaw/skills/openai-whisper/SKILL.md`
- summarize 官方文档：https://summarize.sh
- Whisper GitHub：https://github.com/openai/whisper
