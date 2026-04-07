# 开源项目演示类 - FFmpeg 命令行

## 核心工具/API

- **ffmpeg**: 完整的跨平台音视频处理工具集
- **ffprobe**: 视频元信息查看工具

## 步骤流程

### 基础信息查看

1. **查看视频详细信息**
   ```bash
   ffprobe -v quiet -print_format json -show_format -show_streams video.mp4
   ```

2. **查看视频时长、分辨率、编码**
   ```bash
   ffprobe video.mp4
   ```

### 视频帧提取

1. **提取单帧**
   ```bash
   # 提取第10秒的一帧
   ffmpeg -ss 00:00:10 -i input.mp4 -vframes 1 output.jpg
   
   # 提取第一帧
   ffmpeg -i input.mp4 -vframes 1 first_frame.jpg
   ```

2. **批量提取关键帧**
   ```bash
   # 每秒提取一帧
   ffmpeg -i input.mp4 -vf "fps=1" frame_%04d.jpg
   
   # 每隔10秒提取一帧
   ffmpeg -i input.mp4 -vf "fps=0.1" frame_%04d.jpg
   ```

3. **提取关键帧（I帧）**
   ```bash
   ffmpeg -i input.mp4 -vf "select='eq(pict_type,I)'" -vsync vfr keyframe_%04d.jpg
   ```

### 音视频提取

1. **提取音频**
   ```bash
   # 提取为MP3
   ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 output.mp3
   
   # 提取为WAV
   ffmpeg -i input.mp4 -vn -acodec pcm_s16le output.wav
   ```

2. **提取视频（无音频）**
   ```bash
   ffmpeg -i input.mp4 -an -vcodec copy output_video.mp4
   ```

### 视频转码与压缩

1. **转换为不同格式**
   ```bash
   # 转为H.264编码的MP4
   ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4
   
   # 转为WebM（VP9）
   ffmpeg -i input.mp4 -c:v libvpx-vp9 -c:a libopus output.webm
   ```

2. **压缩视频**
   ```bash
   # 高压缩率
   ffmpeg -i input.mp4 -c:v libx264 -crf 28 -c:a aac -b:a 128k output.mp4
   
   # 指定目标文件大小
   ffmpeg -i input.mp4 -fs 10M -c:v libx264 -c:a aac output.mp4
   ```

3. **调整分辨率**
   ```bash
   # 缩放到720p
   ffmpeg -i input.mp4 -vf scale=-2:720 output.mp4
   
   # 缩放到480p
   ffmpeg -i input.mp4 -vf scale=-2:480 output.mp4
   ```

### 视频剪辑

1. **剪切片段**
   ```bash
   # 从1分10秒开始，截取30秒
   ffmpeg -ss 00:01:10 -i input.mp4 -t 30 -c copy output.mp4
   ```

2. **拼接视频**
   ```bash
   # 先创建文件列表
   echo "file 'part1.mp4'" > filelist.txt
   echo "file 'part2.mp4'" >> filelist.txt
   
   # 拼接
   ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
   ```

### 添加字幕

1. **硬字幕（烧录进视频）**
   ```bash
   ffmpeg -i input.mp4 -vf "subtitles=subtitle.srt" output.mp4
   ```

2. **软字幕（独立轨道）**
   ```bash
   ffmpeg -i input.mp4 -i subtitle.srt -c copy -c:s mov_text output.mp4
   ```

## 适用场景

- 开源项目演示视频的帧提取
- 视频格式转换和压缩
- 提取代码演示的关键画面
- 视频内容的预处理

## 常用参数速查

| 参数 | 说明 |
|------|------|
| `-i` | 输入文件 |
| `-ss` | 开始时间 |
| `-t` | 持续时间 |
| `-vframes` | 提取帧数 |
| `-c:v` | 视频编码器 |
| `-c:a` | 音频编码器 |
| `-vf` | 视频过滤器 |
| `-crf` | 质量控制（值越小质量越高） |

## 避坑指南

- **问题**: 提取的帧方向不对
  - **解决**: 检查视频的旋转信息，使用 `-vf "transpose=1"` 旋转

- **问题**: 视频编码问题导致处理失败
  - **解决**: 先用 `-c:v copy -c:a copy` 复制流，不重新编码

- **问题**: 中文字体显示异常
  - **解决**: 指定字体路径，如 `-vf "subtitles=file.srt:force_style='FontName=SimHei'"`

- **问题**: 处理大文件内存不足
  - **解决**: 使用 `-threads` 指定线程数，或分段处理

## 进阶技巧

### 视频信息JSON输出

```bash
ffprobe -v quiet \
  -print_format json \
  -show_format \
  -show_streams \
  video.mp4 | jq '.format.duration, .streams[0].width, .streams[0].height'
```

### 提取视频缩略图（16:9比例）

```bash
ffmpeg -i input.mp4 \
  -vf "scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2" \
  thumbnail.jpg
```

### 循环播放GIF

```bash
ffmpeg -i input.mp4 -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 output.gif
```

## 参考链接

- [FFmpeg官方文档](https://ffmpeg.org/documentation.html)
- [FFmpeg Wiki](https://trac.ffmpeg.org/wiki/)
- [OpenClaw video-frames Skill](./../../app/openclaw/skills/video-frames/SKILL.md)
