# ffmpeg 帧提取与视频预处理

> 工具来源：OpenClaw video-frames skill（内置 ffmpeg）  
> 官方文档：https://ffmpeg.org  
> 更新时间：2026-04-08

---

## 核心工具/API

- **ffmpeg**：开源跨平台视频处理工具，OpenClaw 内置
- **frame.sh 脚本**：OpenClaw video-frames skill 封装脚本
- **OpenClaw exec**：通过 shell 调用 ffmpeg 命令

---

## 步骤流程

### 基础流程：提取单帧

```bash
# 方法1：使用 video-frames skill 的 frame.sh 脚本
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg

# 方法2：指定时间戳提取
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg

# 方法3：直接使用 ffmpeg
ffmpeg -i video.mp4 -ss 00:00:10 -vframes 1 frame.jpg
```

### 进阶流程：批量关键帧提取

```bash
# 每隔 10 秒提取一帧
ffmpeg -i video.mp4 -vf "fps=0.1" frames_%04d.jpg

# 从视频中提取特定场景段（01:00-01:30）
ffmpeg -i video.mp4 -ss 00:01:00 -to 00:01:30 -c:v libx264 clip.mp4

# 提取所有关键帧（I-frames），适合场景变化检测
ffmpeg -i video.mp4 -vf "select='eq(pict_type,PICT_TYPE_I)'" -vsync vfr frames_%04d.png

# 从多个时间点提取（脚本循环）
for t in 00:00:05 00:00:30 00:01:00 00:02:00 00:05:00; do
  ffmpeg -i video.mp4 -ss $t -vframes 1 "frame_${t//:/}.jpg"
done
```

### 预处理流程：视频格式转换与压缩

```bash
# 转换为 H.264 编码的 MP4（兼容性最佳）
ffmpeg -i input.avi -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4

# 压缩到指定大小（100MB 以内）
ffmpeg -i input.mp4 -fs 100MB output.mp4

# 旋转/翻转视频
ffmpeg -i input.mp4 -vf "transpose=1" output.mp4    # 顺时针旋转90°
ffmpeg -i input.mp4 -vf "transpose=2,transpose=2" output.mp4  # 旋转180°

# 提取音频轨道
ffmpeg -i video.mp4 -vn -acodec libmp3lame -b:a 192k audio.mp3
ffmpeg -i video.mp4 -vn -acodec copy audio.aac      # 无损提取
```

### 音频分离（为 Whisper 准备）

```bash
# 提取 WAV 格式（Whisper 兼容性最好）
ffmpeg -i video.mp4 -acodec pcm_s16le -ar 16000 -ac 1 audio.wav

# 提取 MP3 并压缩（适合长音频）
ffmpeg -i video.mp4 -vn -acodec libmp3lame -b:a 32k audio.mp3
```

---

## 适用场景

| 场景 | 推荐命令 |
|------|----------|
| 教程视频关键步骤截图 | `fps=0.1` 或固定时间点 |
| 代码演示视频（需要OCR）| 高质量 PNG 关键帧 |
| 提取字幕/对白 | 先分离音频，再送 Whisper |
| 缩略图生成 | 固定时间点 + 缩放裁剪 |
| 场景变化检测 | 关键帧提取 `select='eq(pict_type,PICT_TYPE_I)'` |
| 长视频分段 | `-ss` + `-to` 切割 |

---

## 避坑指南

### ⚠️ 时间戳定位问题
**问题**：`ffmpeg -ss` 放在 `-i` 之前 vs 之后，速度差异巨大  
**解决**：`-ss` 在前（输入前）为快速定位，在后为精确定位但慢

```bash
# 快速但可能有几帧误差（推荐用于长视频）
ffmpeg -ss 00:01:00 -i video.mp4 -vframes 1 frame.jpg

# 精确定位（慢，适合短片段）
ffmpeg -i video.mp4 -ss 00:01:00 -vframes 1 frame.jpg
```

### ⚠️ 中文字体/字幕乱码
**问题**：提取的帧中中文字符显示为方块  
**解决**：安装中文字体并指定 fontconfig

```bash
# 查找可用字体
fc-list :lang=zh

# 指定字幕流
ffmpeg -i video.mp4 -map 0:s:0 subtitles.srt
```

### ⚠️ 长视频内存溢出
**问题**：一次性处理大视频可能导致内存问题  
**解决**：分段处理 + 使用 `-threads` 限制并发

```bash
ffmpeg -i long_video.mp4 -threads 4 -ss 00:05:00 -to 00:10:00 clip.mp4
```

### ⚠️ 帧率过高导致文件过大
**问题**：提取大量帧时磁盘空间爆炸  
**解决**：控制采样率 + 输出 JPEG 压缩

```bash
# 每5秒1帧，JPEG质量85%
ffmpeg -i video.mp4 -vf "fps=0.2,scale=1280:-1" -q:v 5 frames_%04d.jpg
```

---

## 参考链接

- ffmpeg 官方文档：https://ffmpeg.org/ffmpeg.html
- OpenClaw video-frames skill：`/app/openclaw/skills/video-frames/SKILL.md`
- frame.sh 脚本路径：`{openclaw_dir}/scripts/frame.sh`
