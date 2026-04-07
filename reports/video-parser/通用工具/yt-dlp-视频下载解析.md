# 通用工具 - yt-dlp 视频下载与字幕提取

## 核心工具/API

- **yt-dlp**：开源视频下载工具，支持 1700+ 网站
  - 下载视频：`yt-dlp URL`
  - 提取字幕：`yt-dlp --write-subs --write-auto-subs --sub-lang zh-Hans URL`
  - 提取音频：`yt-dlp -x --audio-format mp3 URL`
  - 下载特定格式：`yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" URL`

## 步骤流程

```
1. 安装 yt-dlp
   pip install -U yt-dlp

2. 查看可用格式和字幕
   yt-dlp --list-subs "https://www.youtube.com/watch?v=VIDEO_ID"

3. 下载视频 + 字幕
   yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" \
          --write-subs --write-auto-subs \
          --sub-lang zh-Hans,en \
          -o "%(title)s.%(ext)s" \
          "VIDEO_URL"

4. 纯音频下载（配合 Whisper）
   yt-dlp -x --audio-format mp3 "VIDEO_URL"

5. 下载完成后用 Whisper 转录或 videos_understand 分析
```

## 适用场景

- ✅ **B站 / YouTube / 抖音视频下载** → 后续解析
- ✅ **提取硬字幕 / 软字幕** → 直接获得文字内容
- ✅ **提取纯音频** → Whisper 转录
- ✅ **下载特定画质** → 节省存储空间

## 避坑指南

- ⚠️ **版权内容**：仅用于个人学习，遵守相关法规
- ⚠️ **B站需要 cookies**：部分视频需登录态，`--cookies-from-browser chrome`
- ⚠️ **字幕为空**：视频可能没有字幕，只能靠 Whisper 转录
- ⚠️ **下载失败**：检查网络，或尝试加 `--no-check-certificates`
