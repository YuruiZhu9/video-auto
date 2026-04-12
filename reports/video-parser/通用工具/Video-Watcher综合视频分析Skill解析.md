# Video Watcher — ClawHub视频综合分析工具

> 🤖 分类：通用工具/第三方Skill
> 📅 更新日期：2026-04-12
> 📌 来源：ClawHub（`clawhub.ai/skills/video-watcher`）
> ⭐ 热度：新兴工具（2026-02-24发布）

---

## 核心工具/API

| 工具 | 功能描述 | 角色 |
|------|---------|------|
| **yt-dlp** | 视频下载，支持YouTube/B站等多平台 | 媒体获取 |
| **FFmpeg** | 音频提取、截图捕获、格式转换 | 媒体处理 |
| **OpenAI Whisper** | 语音转文本，支持多模型大小 | 语音转录 |
| **AI代理** | 集成OpenClaw原生AI能力进行总结 | 智能分析 |

---

## 步骤流程

### 完整Pipeline（5步）

```
视频URL → yt-dlp下载 → FFmpeg音频提取 → Whisper转录 → AI总结
```

### 详细步骤

**1. 安装依赖**
```bash
brew install yt-dlp ffmpeg openai-whisper
```

**2. 安装Skill（ClawHub）**
```bash
npx clawhub@latest install video-watcher
```

**3. 分析视频**
```bash
./scripts/analyze.sh "https://youtube.com/watch?v=VIDEO_ID"
```

**完整命令语法：**
```bash
./scripts/analyze.sh "URL" [output-dir] [frame-interval] [whisper-model]
```

**参数说明：**
- `output-dir`：输出目录（默认 `./outputs`）
- `frame-interval`：截图间隔秒数（默认30秒）
- `whisper-model`：Whisper模型（base/medium/large）

**4. 生成字幕**
```bash
# 自动生成SRT字幕文件
./scripts/analyze.sh "URL" --srt
```

**5. AI总结**
```bash
./scripts/summarize.sh ./outputs/transcript.txt
# 或通过OpenClaw
cat outputs/transcript.txt | openclaw ask "Summarize this"
```

---

## 输出数据结构

| 资产 | 路径 | 描述 |
|------|------|------|
| 视频文件 | `outputs/video.mp4` | 原始视频下载 |
| 音频文件 | `outputs/audio.mp3` | 提取的音轨 |
| 文本转录 | `outputs/transcript.txt` | 纯文本转录 |
| 字幕文件 | `outputs/transcript.srt` | 带时间戳的SRT字幕 |
| 截图帧 | `outputs/frames/` | 指定间隔的截图 |

---

## 配置文件

```json
{
  "whisper_model": "medium",
  "frame_interval": 30,
  "output_dir": "./outputs"
}
```

---

## 适用场景

- **尽职调查视频分析**：投资研究视频自动结构化
- **在线课程笔记生成**：大学讲座自动生成结构化笔记
- **播客存档与摘要**：播客内容文本化与归档
- **技术教程文档化**：截图+转录构建技术文档
- **会议记录索引**：会议视频转录与知识管理

---

## 避坑指南

### 问题1：Whisper模型选择
- **问题**：大模型转录慢，小模型精度差
- **解决**：
  - 快速测试 → `base`
  - 日常使用 → `medium`（推荐，平衡速度与精度）
  - 最高精度 → `large`

### 问题2：截图间隔设置
- **问题**：30秒间隔可能错过关键内容
- **解决**：
  - 代码演示类视频 → 10-15秒
  - 演讲/讲座 → 30-60秒
  - 快速切换演示 → 5秒

### 问题3：长视频处理超时
- **问题**：超过1小时的视频处理时间过长
- **解决**：分段落处理，或使用 `--timestamps` 提取关键段落

### 问题4：音频提取失败
- **问题**：某些视频没有独立音轨
- **解决**：检查视频格式，`ffmpeg -i video.mp4` 查看音轨信息

---

## 与现有知识库工具对比

| 维度 | Video Watcher | summarize | yt-dlp+Whisper | videos_understand |
|------|--------------|-----------|----------------|-------------------|
| 视频下载 | ✅ yt-dlp | ❌ | ✅ yt-dlp | ❌ |
| 音频提取 | ✅ FFmpeg | ❌ | ✅ FFmpeg | ❌ |
| 语音转录 | ✅ Whisper | ✅ | ✅ Whisper | ✅ |
| 字幕生成 | ✅ SRT | ❌ | ✅ | ❌ |
| 截图捕获 | ✅ 间隔截图 | ❌ | ❌ | ❌ |
| AI总结 | ✅ 集成 | ✅ | 需额外配置 | ✅ |
| 安装复杂度 | 低（一键） | 低 | 中（多步） | 无需安装 |

---

## 核心价值

**Video Watcher 是现有知识库工具链的最佳封装方案：**
1. 一键安装，`npx clawhub@latest install video-watcher`
2. 完整Pipeline，无需手动拼接yt-dlp+FFmpeg+Whisper
3. 截图捕获功能，补充其他工具的空缺
4. 配置灵活，支持自定义输出目录和模型大小
5. 可与OpenClaw原生AI深度集成

**推荐用法**：作为视频解析的"一键启动器"，再用`summarize`或`videos_understand`做深度总结。

---

## 参考链接

- ClawHub：https://clawhub.ai/skills/video-watcher
- 安装命令：`npx clawhub@latest install video-watcher`
- GitHub：zedit42（作者）
- 发布日期：2026-02-24
