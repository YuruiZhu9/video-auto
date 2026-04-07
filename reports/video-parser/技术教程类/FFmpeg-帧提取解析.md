# 技术教程类 - FFmpeg 帧提取 + 图片分析方案

## 核心工具/API

- **FFmpeg**：开源视频处理工具，提取帧
  - 提取单帧：`ffmpeg -i input.mp4 -ss 00:01:30 -vframes 1 output.jpg`
  - 批量截帧：`ffmpeg -i input.mp4 -vf "fps=1" frames/%04d.jpg`（每秒1帧）
  - 按时间点截帧：`-ss 00:05:00`
- **OpenClaw video-frames Skill**：封装 FFmpeg 截帧脚本
  - 脚本路径：`{baseDir}/scripts/frame.sh`
  - 用法：`frame.sh /path/video.mp4 --time 00:00:10 --out /tmp/frame.jpg`
- **images_understand**：分析提取的帧图片
  - 支持批量处理最多 20 张图片
  - 可指定分析维度（OCR、界面元素、代码识别）

## 步骤流程

### 完整流程：视频 → 帧提取 → 图片分析 → 结构化输出

```
1. 视频信息检查
   ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 input.mp4

2. 关键帧提取
   # 按时间点提取
   ffmpeg -i input.mp4 -ss 00:02:30 -vframes 1 -q:v 2 frame_2m30s.jpg
   
   # 批量等间隔提取（每30秒一帧）
   ffmpeg -i input.mp4 -vf "fps=0.033" keyframes/%04d.jpg
   
   # 每5分钟提取一帧，适合长教程
   ffmpeg -i input.mp4 -vf "fps=0.0033" keyframes/%04d.jpg

3. 图片批量分析（images_understand）
   → 传入多张帧图片，prompt="识别界面中的代码、操作步骤和技术要点"

4. 结构化整合
   → 结合 Whisper 转录文本 + 帧图片分析 → 完整教程结构化输出
```

## 适用场景

- ✅ **操作演示类教程** - 界面变化频繁，需要截图配合
- ✅ **代码演示视频** - 识别帧中的代码片段（配合 OCR）
- ✅ **需要图文对照** - 教程文章配图、PPT 素材提取
- ✅ **长视频分段** - 按时间戳截帧，快速定位内容位置
- ✅ **"这张图发生了什么"类问题** - 用 frame.sh 截特定时间点

## 避坑指南

- ⚠️ **视频编码格式**：优先用 `.mp4`/`.mkv`，`.avi` 可能需要转码
  - 转码：`ffmpeg -i input.avi -c:v libx264 -crf 23 output.mp4`
- ⚠️ **截帧时间点不准**：`-ss` 放在 `-i` 之前可加速（但时间戳可能偏移）
  - 正确顺序：`ffmpeg -ss 00:01:00 -i input.mp4 -vframes 1 out.jpg`
- ⚠️ **批量截帧文件太多**：建议先检查视频时长，估算合适帧率
- ⚠️ **JPG vs PNG**：快速预览用 JPG，UI 细节用 PNG（无损）
- ⚠️ **图片分析 token 消耗**：maxChars 限制内使用，避免超长输出

## 参考链接

- [FFmpeg 截帧官方文档](https://ffmpeg.org/ffmpeg.html#Main-options)
- [video-frames Skill](/app/openclaw/skills/video-frames/SKILL.md)
- [images_understand 工具](/app/openclaw/tools/videos_understand)
