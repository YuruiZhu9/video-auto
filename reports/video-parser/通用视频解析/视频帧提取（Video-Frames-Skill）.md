# 通用视频解析 - 视频帧提取（Video Frames Skill）

## 核心工具/API

| 工具 | 类型 | 说明 |
|------|------|------|
| **Video Frames Skill** | OpenClaw Skill | 封装了 ffmpeg 的帧提取逻辑，触发词触发后自动执行 |
| **FFmpeg** | 底层依赖 | 实际执行视频帧提取的 CLI 工具 |

---

## 触发词

以下任一描述均可触发该技能：

- 「视频帧提取」
- 「视频缩略图生成」
- 「视频关键帧获取」
- 「ffmpeg 视频提取」
- 「视频画面提取」

---

## 步骤流程

### 方式一：通过 OpenClaw 对话触发（推荐）

```
用户：帮我提取这个视频的第10秒画面
OpenClaw → 调用 video-frames skill → 返回帧图片
```

### 方式二：直接执行脚本

```bash
# 提取第一帧
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg

# 提取指定时间点的帧
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg

# 根据帧序号提取（从0开始）
{baseDir}/scripts/frame.sh /path/to/video.mp4 --index 0 --out /tmp/frame0.png
```

---

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--time` | 指定时间点，格式：时:分:秒 | `--time 00:01:30` |
| `--index` | 指定帧序号，从0开始 | `--index 0`（第一帧）|
| `--out` | 输出文件路径，支持 jpg/png | `--out /tmp/frame.jpg` |

---

## 输出格式对比

| 格式 | 使用场景 | 特点 |
|------|----------|------|
| `.jpg` | 快速分享、缩略图 | 文件小，画质损失小 |
| `.png` | UI展示、二次编辑 | 无损压缩，画质最高 |

---

## 适用场景

- ✅ **视频缩略图生成**：为视频内容生成预览封面
- ✅ **关键帧定位**：分析某个时间点的视频画面内容
- ✅ **AI 视觉分析**：提取帧后送入 VLM（GPT-4o/Claude Vision）分析画面内容
- ✅ **内容审核**：截取视频特定帧进行人工审核
- ✅ **与音频转录配合**：在 Whisper 转录的时间点截取对应画面

---

## 避坑指南

### ⚠️ 安装前置依赖

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

### ⚠️ 时间格式注意

- ffmpeg 的 time 格式为 `HH:MM:SS`，不是 `SS` 或 `MM:SS`
- 错误：`--time 10`（❌）→ 正确：`--time 00:00:10`（✅）
- 对于毫秒支持：`00:00:10.500`

### 💡 配合 AI 分析的典型流程

```
1. Whisper 转录 → 得到时间戳文字稿
2. 根据时间戳，用 Video Frames 提取对应画面
3. 将画面 + 文字送入 GPT-4o → 生成带画面的视频总结
```

---

## 安装命令

```bash
# 通过 clawhub 安装（推荐）
npx clawhub@latest install video-frames

# 或者手动下载
# GitHub: https://github.com/openclaw/skills（搜索 video-frames）
# 下载 video-frames-1.0.0.zip
```

---

## 参考链接

- ClawHub 页面：https://clawhub.ai/steipete/video-frames
- 作者：steipete（Peter Steinberger）
- FFmpeg 官网：https://ffmpeg.org/
