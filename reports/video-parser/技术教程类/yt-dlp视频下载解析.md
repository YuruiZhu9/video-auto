# [技术教程类] - yt-dlp视频下载解析

## 核心工具/API

| 工具 | 说明 |
|------|------|
| **yt-dlp** | 功能强大的命令行视频下载器，支持1000+网站 |
| **ffmpeg** | 音视频处理底座，yt-dlp依赖其合并流 |
| **aria2** | 可选的多线程下载加速器 |

## 步骤流程

### 1. 安装与环境准备

```bash
# 安装 yt-dlp（推荐最新版本）
pip install -U yt-dlp

# 安装 ffmpeg（必须）
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg

# 验证安装
yt-dlp --version
ffmpeg -version
```

### 2. 基础下载命令

```bash
# 通用格式下载
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID"

# 指定格式（视频+音频合并）
yt-dlp -f "bestvideo+bestaudio/best" "URL"

# 仅下载音频（适合播客/音乐）
yt-dlp -x --audio-format mp3 "URL"

# 指定输出路径和文件名
yt-dlp -o "/workspace/video/%(title)s.%(ext)s" "URL"
```

### 3. 高级参数（技术教程场景）

```bash
# 仅下载1080P及以下（节省空间）
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" URL

# 下载并自动添加字幕
yt-dlp --write-subs --write-auto-subs --sub-lang zh-Hans,en URL

# 仅提取字幕（不下载视频）
yt-dlp --skip-download --write-subs --sub-lang zh-Hans URL -o "subtitle.%(ext)s"

# 下载B站视频（含弹幕/字幕）
yt-dlp "https://www.bilibili.com/video/BVxxxxx" \
  --write-description --write-info-json

# 下载课程章节视频（指定时间范围）
yt-dlp --download-sections "*00:05:00-00:15:00" URL
```

### 4. Python API 调用

```python
import yt_dlp

def download_video(url, output_path="/workspace/video"):
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'writesubtitles': True,
        'writeinfojson': True,  # 导出视频元信息
        'progress_hooks': [hook]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info

def hook(d):
    """进度回调"""
    if d['status'] == 'downloading':
        pct = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        print(f"\r下载中: {pct} | 速度: {speed}", end="")
    elif d['status'] == 'finished':
        print(f"\n下载完成: {d['filename']}")
```

### 5. 结合视频解析工作流

```python
import subprocess

def video_to_analysis_pipeline(url, work_dir="/workspace/video_parser"):
    """完整管道：下载 → 提取音频 → 转录 → OCR"""
    import whisper
    import cv2
    import os
    
    os.makedirs(work_dir, exist_ok=True)
    video_file = f"{work_dir}/input.mp4"
    
    # Step 1: 下载视频
    subprocess.run([
        "yt-dlp", "-f", "bestvideo[height<=720]+bestaudio",
        "-o", video_file, url, "--no-playlist"
    ], check=True)
    
    # Step 2: Whisper 转录
    model = whisper.load_model("small")
    result = model.transcribe(video_file)
    transcript_file = f"{work_dir}/transcript.txt"
    with open(transcript_file, "w") as f:
        f.write(result["text"])
    
    # Step 3: 帧采样供 OCR
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count, interval = 0, int(fps * 10)  # 每10秒一帧
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % interval == 0:
            frame_path = f"{work_dir}/frame_{frame_count}.jpg"
            cv2.imwrite(frame_path, frame)
            frames.append(frame_path)
        frame_count += 1
    
    print(f"✅ 解析完成！")
    print(f"   视频文件: {video_file}")
    print(f"   转录文本: {transcript_file}")
    print(f"   关键帧: {len(frames)} 帧")
    return {"transcript": transcript_file, "frames": frames}
```

## 适用场景

- ✅ 技术教程视频离线缓存（方便反复观看解析）
- ✅ 批量下载课程系列视频
- ✅ 提取视频字幕和描述信息（用于索引/检索）
- ✅ 分段下载课程重点章节
- ✅ B站/YouTube等主流平台的课程视频获取

## 避坑指南

### ⚠️ 问题1：下载速度极慢（YouTube等）
**解决方案**：
- 使用 aria2c 后端加速：`pip install yt-dlp[yt-dlp-noconcurrentsegmentdownload]`（实际上yt-dlp已内置多线程）
- 指定更多线程：`--concurrent-fragments 8`
- 换用国内镜像站或其他可访问源

### ⚠️ 问题2：ffmpeg 缺失导致合并失败
**错误信息**：`Unable to merge formats`
**解决方案**：
```bash
# 确认 ffmpeg 已安装并可用
which ffmpeg
ffmpeg -version

# 如缺失，重新安装
sudo apt install ffmpeg
# 或下载静态编译版
wget https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
```

### ⚠️ 问题3：某些视频格式播放受限
**解决方案**：
- 使用 `-f best` 降低格式要求，让 yt-dlp 自适应
- 或强制下载 mp4：`--merge-output-format mp4`
- 检查视频是否需要登录：`--cookies-from-browser chrome`

### ⚠️ 问题4：B站等国内平台下载失败
**解决方案**：
- B站视频需要 SESSDATA cookie 认证
- 使用浏览器插件获取 cookie 后：
```bash
yt-dlp --add-header "Cookie: SESSDATA=YOUR_SESSDATA" "B站URL"
```
- 或使用专门的 B站下载工具（如bilibili-downloader）作为补充

## 参考链接

- yt-dlp 官方文档：https://github.com/yt-dlp/yt-dlp
- yt-dlp 支持网站列表：https://github.com/yt-dlp/yt-dlp/blob/master/docs/supportedsites.md
- FFmpeg 下载：https://ffmpeg.org/download.html
