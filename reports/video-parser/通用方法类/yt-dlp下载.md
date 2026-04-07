# 通用方法 - yt-dlp 视频下载

## 核心工具/API

- **工具**: `yt-dlp`（已安装在 `/app/.venv/bin/yt-dlp`，v2024.12.23）
- **支持平台**: YouTube、Bilibili、微博、Twitter/X、抖音、知乎视频等 1700+ 站点
- **特点**: 开源、持续更新、支持代理、可调用后处理器

## 步骤流程

### 基本下载
```bash
# 下载最高画质
yt-dlp "https://youtu.be/dQw4w9WgXcQ"

# 下载指定格式（最佳视频+音频）
yt-dlp -f "bv+ba/best" "URL"

# 下载为 MP4
yt-dlp --merge-output-format mp4 "URL"

# 下载字幕
yt-dlp --write-subs --write-auto-subs --sub-langs zh,en "URL"

# 仅下载字幕（不下载视频）
yt-dlp --write-subs --skip-download "URL"
```

### 高级用法
```bash
# 使用代理
yt-dlp --proxy "http://127.0.0.1:7890" "URL"

# 限速（避免被封）
yt-dlp -r 1M "URL"

# 下载播放列表
yt-dlp --playlist-start 1 --playlist-end 10 "PLAYLIST_URL"

# 输出模板（自定义文件名）
yt-dlp -o "%(title)s-%(id)s.%(ext)s" "URL"

# 截图（下载时生成缩略图）
yt-dlp --write-thumbnail "URL"

# 查看可用格式
yt-dlp -F "URL"
```

### 与其他工具组合
```bash
# 下载 → 提取音频 → Whisper 转录
yt-dlp -x --audio-format mp3 "VIDEO_URL"
whisper "audio.mp3" --model medium --output_format txt

# 下载 → 提取帧 → 图片分析
yt-dlp "VIDEO_URL"
ffmpeg -i video.mp4 -vf "fps=1/10" frames/frame_%03d.jpg  # 每10秒1帧
```

## 适用场景

- **视频需要本地处理**: 下载后才能用 whisper/ffmpeg 等工具处理
- **需提取字幕**: 大量视频批量提取字幕文本
- **多平台视频获取**: 一个工具搞定所有常见视频平台
- **离线分析**: 网络不稳定时的提前缓存

## 避坑指南

| 问题 | 解决方案 |
|------|---------|
| YouTube 下载失败（网络） | 加 `--proxy` 使用代理 |
| 画质选择错误 | 先用 `-F` 查看可用格式，再 `-f` 指定 |
| 被识别为机器人 | 加 `--user-agent` 和 `--sleep-requests` |
| 下载太慢 | 用 `-r 2M` 限速，或分时间段下载 |
| B站视频加密 | 尝试 `--extractor-args "bilibili:chunk_size=4096"` |
| 无字幕 | 用 `--write-auto-subs` 自动生成，或下载后用 whisper 转录 |
| B站登录内容 | 使用 `--cookies-from-browser chrome` 复用浏览器 Cookie |

## 下载格式速查

```bash
# 最佳画质（自动选择）
yt-dlp "URL"

# 最高画质 MP4（通常最优）
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" "URL"

# 仅音频（MP3）
yt-dlp -x --audio-format mp3 "URL"

# 指定分辨率
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" "URL"
```

## 平台特殊参数

| 平台 | 常用参数 |
|------|---------|
| YouTube | `--cookies`、`--proxy`、`-f best` |
| Bilibili | `--cookies-from-browser`、`--sub-lang zh-Hans` |
| 微博 | `--no-check-certificates` |
| 抖音/TikTok | `--windows-tabstep`（避免文件名问题）|
| 小红书 | 部分支持，视具体视频页 URL 而定 |
