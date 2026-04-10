# 技术教程类 - yt-dlp 视频解析方案

## 核心工具/API

- **yt-dlp**
  - GitHub：https://github.com/yt-dlp/yt-dlp
  - 类型：开源 CLI 工具（Python）
  - 支持：YouTube、B站、抖音、Twitter 等 1700+ 平台
  - 特点：持续活跃更新，支持字幕提取、元数据获取

- **yt-dlp-transcripts（Python 库）**
  - PyPI：https://pypi.org/project/yt-dlp-transcripts/
  - 功能：批量提取视频信息 + 字幕/转写

- **yt_dlp_transcript（Python 脚本）**
  - GitHub：https://github.com/kkensuke/yt_dlp_transcript
  - 功能：提取字幕 + 转换为 Markdown + AI 总结

- **YouTubeTranscriptApi（Python 库）**
  - 功能：直接获取 YouTube 字幕（无需下载视频）
  - 限制：仅支持 YouTube，自动字幕可能有误差

## 步骤流程

### 方案A：yt-dlp CLI 快速提取字幕
```bash
# 查看可用字幕格式
yt-dlp --list-subs "https://youtu.be/VIDEO_ID"

# 下载字幕（自动选择最优格式）
yt-dlp --write-subs --sub-langs "zh-Hans,en" \
  --skip-download --convert-subs srt \
  "https://youtu.be/VIDEO_ID"

# 下载字幕（手动字幕优先，自动字幕降级）
yt-dlp --write-subs --write-auto-subs \
  --sub-langs "zh-Hans" --skip-download \
  "https://youtu.be/VIDEO_ID"

# 下载视频 + 字幕
yt-dlp --format "best[height<=720]" \
  --write-subs --sub-langs "zh-Hans" \
  "https://youtu.be/VIDEO_ID"

# 仅获取元数据（不下载）
yt-dlp --dump-json "https://youtu.be/VIDEO_ID"
```

### 方案B：yt_dlp_transcript Python 脚本
```bash
# 安装
pip install yt_dlp_transcript

# 提取并转换为 Markdown
yt_dlp_transcript "https://youtu.be/VIDEO_ID" -o output.md

# 带 AI 总结（需 OPENAI_API_KEY）
yt_dlp_transcript "https://youtu.be/VIDEO_ID" -o output.md --summarize
```

### 方案C：YouTubeTranscriptApi Python
```python
from YouTubeTranscriptApi import YouTubeTranscriptApi

# 提取字幕（手动优先）
transcript = YouTubeTranscriptApi.get_transcript(
    "VIDEO_ID",
    languages=["zh-Hans", "zh"]
)

# 转为纯文本
text = "\n".join([item["text"] for item in transcript])
print(text)

# 保留时间戳
for item in transcript:
    print(f"[{item['start']:.2f}s] {item['text']}")
```

### 方案D：yt-dlp-transcripts 批量提取
```python
from yt_dlp_transcripts import ChannelVideos

# 获取频道所有视频 + 字幕
channel = ChannelVideos("UCxyz_channel_id")
for video in channel.videos:
    transcript = video.fetch_transcript()
    print(f"{video.title}: {len(transcript)} 字")
```

### 方案E：B站视频解析
```bash
# B站视频下载 + 字幕
yt-dlp --write-subs --write-auto-subs \
  --sub-langs "zh-CN" \
  "https://www.bilibili.com/video/BV1xx411c7XD"

# 获取 B站 字幕（弹幕转字幕思路）
yt-dlp --write-info-json "https://www.bilibili.com/video/BV1xx411c7XD"
# 然后解析 JSON 中的弹幕和字幕信息
```

## 适用场景

- ✅ YouTube 技术教程（字幕质量高）
- ✅ B站 视频教程（中文字幕/弹幕）
- ✅ 多平台视频批量获取元数据
- ✅ 需要下载视频后进行本地分析
- ✅ 字幕 + 视频双重获取

## 避坑指南

- **坑1：YouTube 字幕被屏蔽**
  - 解决：优先 `--write-subs`（手动字幕），再降级 `--write-auto-subs`（自动字幕）
  - 自动字幕常有误差，建议用 Whisper 重新转写

- **坑2：视频下载被限速**
  - 解决：用 `--format "best[height<=720]"` 限制画质节省时间
  - B站建议：`--format "flv[height<=480]" / "mp4[height<=720]"`

- **坑3：字幕格式乱码**
  - 解决：指定编码 `--encoding utf-8`，或转换格式 `--convert-subs srt`
  - 中文乱码用：`--sub-langs "zh-Hans"` 明确语言

- **坑4：视频需要登录才能访问**
  - 解决：cookies 导出浏览器登录状态：`--cookies-from-browser chrome`
  - 或手动导出 cookies.txt：`--cookies cookies.txt`

- **坑5：yt-dlp 更新后语法变化**
  - 解决：定期 `pip install -U yt-dlp` 更新
  - 生产环境固定版本：`pip install yt-dlp==2024.x.x`

## 参考链接

- yt-dlp 官方：https://github.com/yt-dlp/yt-dlp
- yt-dlp-transcripts：https://pypi.org/project/yt-dlp-transcripts/
- yt_dlp_transcript：https://github.com/kkensuke/yt_dlp_transcript
- YouTubeTranscriptApi：https://github.com/jdepoix/youtube-transcript-api
