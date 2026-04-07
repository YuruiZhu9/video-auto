# 技术教程类 - FFmpeg 帧提取解析

## 核心工具/API

- **FFmpeg**：开源多媒体处理工具，用于视频帧提取、缩略图生成、场景检测
  - 首页：https://ffmpeg.org
  - OpenClaw Skill：`/app/openclaw/skills/video-frames/SKILL.md`
  - 安装：`brew install ffmpeg`（macOS）
  - OpenClaw 封装脚本：`{baseDir}/scripts/frame.sh`

- **OpenClaw frame.sh 封装**：
```bash
{baseDir}/scripts/frame.sh /path/video.mp4 --out /tmp/frame.jpg        # 第一帧
{baseDir}/scripts/frame.sh /path/video.mp4 --time 00:00:10 --out /tmp/frame.jpg  # 指定时间戳
```

## 步骤流程

### 1. 提取单个帧（指定时间）
```bash
# 提取第10秒的帧
ffmpeg -ss 00:00:10 -i input.mp4 -frames:v 1 -q:v 2 output.jpg
```

### 2. 提取多个均匀分布的帧（用于概览）
```bash
# 将视频分成 N 段，每段提取1帧
ffmpeg -i input.mp4 -vf "select='not(mod(n\,100))',scale=640:-1" -vsync vfr frame_%03d.jpg
```

### 3. 场景变化自动检测提取（ffmpeg + sed）
```bash
# 利用 ffprobe 获取关键帧时间戳
ffprobe -select_streams v:0 -show_frames -show_entries frame=pict_type,pkt_pts_time input.mp4 2>/dev/null | grep -E "pkt_pts_time|I.frame" > keyframes.txt
```

### 4. 生成缩略图拼图（视频概览）
```bash
ffmpeg -i input.mp4 -vf "fps=1/10,scale=320:-1,tile=10x1" overview.jpg
# 每10秒一帧，拼成一行缩略图
```

### 5. 提取音频（供 Whisper 转录）
```bash
ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 output.mp3
ffmpeg -i input.mp4 -vn -acodec pcm_s16le audio.wav  # 无压缩
```

### 6. 获取视频元数据
```bash
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

## 适用场景

- ✅ **技术教程视频**：提取关键操作界面的截图，供 OCR 分析代码/命令
- ✅ **长视频分段**：配合 `videos_understand` 做多帧分析
- ✅ **制作缩略图拼图**：快速了解视频内容结构
- ✅ **提取音频**：为 Whisper 转录准备输入
- ✅ **无网络下载视频**：本地处理，不依赖在线 API

## 避坑指南

### ❌ 常见问题 1：提取的帧画面模糊
**原因**：`ffmpeg` 默认编码质量低；或时间戳在 GOP 之间
**解决**：
- 用 PNG 替代 JPG：`output.png`
- 加 `-q:v 1` 或 `-quality high`
- 使用关键帧时间：`ffmpeg -i input.mp4 -ss 10 -vframes 1 -q:v 2 output.jpg`（`-ss` 放前面更精确）

### ❌ 常见问题 2：提取帧太多/太少
**原因**：fps 参数设置不合理
**解决**：先查看视频时长 `ffprobe -v quiet -show_entries format=duration -of csv=p=0 input.mp4`，按需计算 fps

### ❌ 常见问题 3：音频提取失败（视频编码问题）
**原因**：视频使用特殊编码（如 m3u8 流媒体、DRM 加密）
**解决**：先转码 `ffmpeg -i input.m3u8 -c copy output.mp4` 再提取音频

### ❌ 常见问题 4：跨平台编码兼容性
**原因**：输出视频在 Windows/Linux 播放异常
**解决**：统一用 H.264 编码：`ffmpeg -i input.avi -c:v libx264 -crf 23 -c:a aac output.mp4`

## 场景检测脚本（进阶）

```bash
#!/bin/bash
# detect_scenes.sh - 检测视频场景变化点
VIDEO="$1"
OUTPUT_DIR="${2:-./scenes}"
mkdir -p "$OUTPUT_DIR"

# 使用 ffprobe 提取I帧时间戳
ffprobe -select_streams v:0 -show_frames -show_entries frame=pict_type,pkt_pts_time \
  -of csv=p=0 "$VIDEO" 2>/dev/null | awk -F',' '/I.frame/{print $2}' | while read ts; do
  ffmpeg -ss "$ts" -i "$VIDEO" -frames:v 1 -q:v 2 "${OUTPUT_DIR}/scene_$(echo $ts | tr '.' '_').jpg" 2>/dev/null
done
echo "检测完成，场景帧保存在 $OUTPUT_DIR"
```

## 参考链接

- FFmpeg 官网：https://ffmpeg.org
- OpenClaw Skill：`/app/openclaw/skills/video-frames/SKILL.md`
- 封装脚本：`{baseDir}/scripts/frame.sh`
