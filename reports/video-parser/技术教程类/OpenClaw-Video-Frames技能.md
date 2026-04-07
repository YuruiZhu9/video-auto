# 技术教程类 - OpenClaw Video Frames 视频帧提取技能

## 核心工具/API

| 工具 | 作用 | 备注 |
|------|------|------|
| **FFmpeg** | 帧提取核心引擎 | 需提前安装 |
| **video-frames Skill** | OpenClaw封装脚本 | 作者：steipete（Peter Steinberger） |
| **frame.sh 脚本** | 关键帧提取入口 | 支持时间戳/帧序号指定 |

---

## 步骤流程

### 安装技能

```bash
# 通过 clawhub 安装
npx skills add steipete/video-frames

# 或手动下载：https://clawhub.ai/steipete/video-frames
```

### 提取第一帧（封面/缩略图）

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg
```

### 提取指定时间点的帧

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
```

### 提取指定帧序号

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --index 0 --out /tmp/frame0.png
```

### 全参数说明

```
frame.sh <视频文件> [--time 时:分:秒] [--index 帧序号] --out /保存路径/文件名
```

| 参数 | 说明 | 常用值 |
|------|------|--------|
| `--time` | 指定时间点提取帧 | `00:00:05` |
| `--index` | 指定帧序号（从0开始） | `0`, `30`, `300` |
| `--out` | 输出路径（必填） | 支持 `.jpg` / `.png` |

---

## 适用场景

- ✅ **技术教程封面图**：提取视频开头/关键操作画面
- ✅ **缩略图生成**：自动生成视频预览图
- ✅ **步骤记录**：提取教程每个操作节点的画面
- ✅ **内容审核**：快速预览视频关键帧判断内容类型
- ✅ **素材收集**：从演示视频中截取素材帧

---

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 脚本运行报错 | 未安装FFmpeg | macOS: `brew install ffmpeg`；Ubuntu: `sudo apt install ffmpeg` |
| 输出模糊 | jpg格式压缩损耗 | 使用 `.png` 格式获得无损画质 |
| `--index` 取值不准 | 不同视频帧率不同 | 先用 `ffprobe` 查看帧率：`ffprobe -v error -select_streams v -count_frames -read_intervals 1%#1 -show_entries stream=r_frame_rate -of csv=p=0 input.mp4` |
| 时间点找不到帧 | 视频时长<指定时间 | 先用 `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4` 确认时长 |

### 格式选择建议

| 输出用途 | 推荐格式 | 原因 |
|----------|----------|------|
| 快速预览/分享 | `.jpg` | 文件小，便于传播 |
| UI缩略图/二次处理 | `.png` | 无损压缩，保留细节 |
| 批量生成 | `.jpg -q:v 80` | 控制文件大小 |

---

## 参考链接

- 技能主页：https://clawhub.ai/steipete/video-frames
- FFmpeg官网：https://ffmpeg.org
- 技能文档：https://www.w3cschool.cn/openclaw_skills_manual/openclaw-skills-steipete-video-frames.html
