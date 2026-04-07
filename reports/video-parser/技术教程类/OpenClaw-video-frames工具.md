# 技术教程类 - OpenClaw video-frames 工具

## 核心工具/API

- **ffmpeg**: 强大的开源视频处理工具，用于提取视频帧
- **video-frames Skill**: OpenClaw封装的ffmpeg工具，简化帧提取流程

## 步骤流程

1. **安装ffmpeg**
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt install ffmpeg`

2. **提取第一帧**
   ```bash
   {baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg
   ```

3. **指定时间戳提取帧**
   ```bash
   {baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
   ```

4. **使用ffmpeg直接提取**
   ```bash
   ffmpeg -i input.mp4 -ss 00:00:10 -vframes 1 output.jpg
   ```

## 适用场景

- 技术教程视频中提取代码截图
- 提取演示视频的关键步骤截图
- 生成视频缩略图
- 检查视频内容（debug用）

## 避坑指南

- **问题**: 提取的帧是黑色/空白
  - **解决**: 确认视频已解码完成，使用 `--ss` 在输入之前定位可提升准确性

- **问题**: 输出图片模糊
  - **解决**: 使用 `.png` 格式而非 `.jpg`，或使用更高质量的编码参数

- **问题**: 视频太长，定位困难
  - **解决**: 先用 `ffprobe` 查看视频时长和关键帧信息

## 参考链接

- [FFmpeg官方文档](https://ffmpeg.org)
- [OpenClaw video-frames Skill](./../../app/openclaw/skills/video-frames/SKILL.md)
