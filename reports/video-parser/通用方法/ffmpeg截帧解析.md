# 通用方法 - ffmpeg 截帧解析

> 适用于：所有本地视频的视觉内容提取、缩略图生成、关键帧抓取

## 核心工具/API

- **ffmpeg**：开源多媒体处理工具，支持视频截帧、转码、音频提取
- **OpenClaw video-frames Skill**：封装了常用截帧命令的便捷脚本
- **MediaInfo**：视频元数据查看（编码格式、时长、帧率等）

## 步骤流程

### 1. 查看视频基本信息
```bash
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4
```

### 2. 提取单帧图片
```bash
# 提取第一帧
ffmpeg -i video.mp4 -vf "select=eq(n\,0)" -vframes 1 first_frame.jpg

# 按时间戳截取（00:01:30 位置）
ffmpeg -i video.mp4 -ss 00:01:30 -vframes 1 frame_1m30s.jpg

# 高质量截帧（避免压缩伪影）
ffmpeg -i video.mp4 -ss 00:01:30 -vframes 1 -q:v 1 frame_hq.jpg
```

### 3. 批量提取关键帧（每 N 秒一帧）
```bash
# 每 10 秒提取一帧
ffmpeg -i video.mp4 -vf "fps=1/10" frames/frame_%04d.jpg

# 每 30 秒提取一帧
ffmpeg -i video.mp4 -vf "fps=1/30" frames/frame_%04d.jpg
```

### 4. 提取场景切换帧（关键帧）
```bash
# 用 select 滤镜检测场景变化
ffmpeg -i video.mp4 -vf "select='gt(scene,0.3)',showinfo" -vsync 0 frames/scene_%04d.jpg

# 限制最多提取 N 张
ffmpeg -i video.mp4 -vf "select='gt(scene,0.4)',showinfo" -vsync 0 -vframes 20 frames/scene_%04d.jpg
```

### 5. 生成缩略图拼图（网格预览）
```bash
# 4x3 网格，12 张缩略图拼成一张
ffmpeg -i video.mp4 -vf "select=not(mod(n\,100)),scale=320:180,tile=4x3" -vsync 0 thumbnail_grid.jpg
```

### 6. 提取音频
```bash
# 提取音频流
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3

# 提取高保真音频（wav）
ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav

# 截取片段
ffmpeg -i video.mp4 -ss 00:05:00 -to 00:10:00 -vn audio_clip.wav
```

### 7. 视频转码/压缩
```bash
# H.264 压缩
ffmpeg -i video.mp4 -c:v libx264 -crf 23 -c:a aac -b:a 128k output.mp4

# 提取 GIF（用于简短演示）
ffmpeg -i video.mp4 -ss 00:00:05 -to 00:00:10 -vf "fps=10,scale=480:-1:flags=lanczos" output.gif
```

## 适用场景

- **技术教程类视频**：提取代码截图、界面截图
- **开源项目演示**：提取关键步骤截图
- **B站/YouTube 视频下载后**：用 ffmpeg 截帧做本地分析
- **长视频降采样**：批量截帧后用 LLM 批量分析
- **生成缩略图网格**：快速预览视频内容结构

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 截帧一片黑 | 视频是关键帧间隔大的格式 | 用 `-skip_frame nokey` 跳到下一个关键帧 |
| 图片模糊 | 缩放算法差 | 用 `scale=1280:720:flags=lanczos` 提升质量 |
| 截帧位置不准确 | `-ss` 位置不准 | 将 `-ss` 放在 `-i` **之前**（输入寻址更快更准） |
| 批量截帧太多 | fps 设得太小导致图片爆炸 | 先用 `ffprobe` 确认时长，合理设置 fps |
| 中文文件名乱码 | 系统编码问题 | 转换前：`export LANG=zh_CN.UTF-8` |
| 场景切换帧不准 | 阈值 `scene` 设太高 | 从 `0.3` 开始调，过滤太严格时降低阈值 |
| GPU 加速不可用 | 未安装 NVENC/AMF | 用 CPU：`ffmpeg -i video.mp4 -c:v libx264 ...` |

## OpenClaw video-frames Skill 快捷命令

```bash
# 安装后（需 ffmpeg）
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
```

## 参考链接

- ffmpeg 官方：https://ffmpeg.org
- 场景检测文档：https://ffmpeg.org/ffmpeg-filters.html#select_002c-settb
- OpenClaw video-frames Skill：内置于 `/app/openclaw/skills/video-frames/`
