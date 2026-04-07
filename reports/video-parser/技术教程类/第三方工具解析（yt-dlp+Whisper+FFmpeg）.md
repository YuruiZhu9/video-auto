# 技术教程类 - 第三方工具解析（yt-dlp + Whisper + FFmpeg）

## 核心工具/API

- **yt-dlp**：开源多平台视频下载器，支持 B站/YouTube/抖音等 1000+ 平台，可提取字幕、元信息、缩略图
- **FFmpeg**：开源音视频处理引擎，支持格式转换、裁剪、合并、提取音频、添加水印等
- **Whisper**（OpenAI）：开源语音识别模型，支持 99 种语言，提供时间戳，可本地运行
- **Faster-Whisper**：Whisper 的 C++ 高性能实现，速度快 4~5 倍，内存占用更低
- **@steipete/summarize**：OpenClaw Skill，封装了视频/音频/网页/PDF 总结能力，支持 YouTube 视频

---

## 步骤流程

### 全链路方案（下载 → 提取 → 分析 → 输出）

```
第1步：yt-dlp 下载视频 + 字幕
第2步：FFmpeg 提取音频（Whisper 用）
第3步：Whisper 生成逐字稿（含时间戳）
第4步：videos_understand 分析视频画面
第5步：合并文字稿 + 视频分析 → 结构化输出
```

### 详细命令

#### 第1步：yt-dlp 下载（含字幕）
```bash
# 下载 B站视频 + 自动字幕
yt-dlp \
  --write-subs --write-auto-subs --sub-langs "zh-Hans,zh-Hant,en" \
  --sub-format "srt" \
  -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  -o "%(title)s.%(ext)s" \
  "https://www.bilibili.com/video/BVxxxx"

# 下载 YouTube 视频
yt-dlp \
  --write-subs --write-auto-subs \
  -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" \
  -o "%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=xxxxx"
```

#### 第2步：FFmpeg 提取音频
```bash
# 提取音频（Whisper 推荐格式）
ffmpeg -i "视频.mp4" -vn -acodec libmp3lame -q:a 2 "音频.mp3"

# 或提取为 WAV（Whisper 最高精度）
ffmpeg -i "视频.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 "音频.wav"

# 视频按时间分段（超长视频处理）
ffmpeg -i "长视频.mp4" -ss 00:00 -t 600 -c copy "第1段.mp4"
```

#### 第3步：Whisper 语音识别
```bash
# 安装（pip）
pip install openai-whisper

# 基本用法（自动选择模型）
whisper "音频.mp3" --language Chinese --model medium

# Faster-Whisper（推荐，速度更快）
pip install faster-whisper
python -c "
from faster_whisper import WhisperModel
model = WhisperModel('medium', device='cpu', compute_type='int8')
segments, _ = model.transcribe('音频.mp3', language='zh', word_timestamps=True)
for seg in segments:
    print(f'[{seg.start:.2f}s-{seg.end:.2f}s] {seg.text}')
"
```

#### 第4步：@steipete/summarize Skill
```bash
# 安装
npm i -g @steipete/summarize   # 或 brew install steipete/tap/summarize

# 总结 YouTube 视频
summarize "https://www.youtube.com/watch?v=xxxxx" --provider anthropic

# 总结本地视频文件
summarize "/path/to/video.mp4" --provider openai

# 提取视频关键帧/幻灯片
summarize "/path/to/video.mp4" --slides --provider anthropic
```
> ⚠️ 需要配置 API Key（OPENAI_API_KEY / ANTHROPIC_API_KEY 等）

---

## 适用场景

| 场景 | 推荐工具组合 |
|------|------------|
| B站/YouTube 技术教程批量下载分析 | yt-dlp + Whisper + videos_understand |
| 纯离线环境（无网络） | FFmpeg + Whisper（本地模型） |
| 需要精确时间戳字幕 | yt-dlp（写字幕）+ Whisper（逐句时间戳） |
| YouTube 视频快速总结 | @steipete/summarize（一条命令） |
| 超长视频（>2小时）处理 | FFmpeg 分段 + 批量 Whisper + videos_understand |
| 提取代码截图/幻灯片 | FFmpeg 截帧 + summarize --slides |

---

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| yt-dlp 下载 B站失败（需要登录） | 视频需要 cookie 认证 | 用浏览器插件获取 cookies.json，传入 `--cookies cookies.txt` |
| Whisper 中文识别不准 | 模型太小/音频质量差 | 用 `medium` 或 `large-v3` 模型；先降噪 `ffmpeg -af denoise` |
| FFmpeg 内存爆炸 | 视频过大 | 先用 `ffprobe` 查看信息，用 `-threads 4` 限制并发 |
| Whisper 输出时间戳不准 | 音频中有静音 | 用 VAD（语音活动检测）预处理：`whisper --vad-filter true` |
| @steipete/summarize 安装失败 | arm64 架构限制 | 使用 npm 全局安装替代 Homebrew：`npm i -g @steipete/summarize` |
| 下载字幕为空 | 平台不提供字幕 | 改用 Whisper 从音频生成字幕（最可靠） |
| B站下载画质低 | 默认只下载免费画质 | 登录后用 cookie 下载，或指定 ` -f "bestvideo+bestaudio"` |

---

## 参考链接

- yt-dlp GitHub：https://github.com/yt-dlp/yt-dlp
- Whisper GitHub：https://github.com/openai/whisper
- Faster-Whisper：https://github.com/guillawekorchuk/faster-whisper
- FFmpeg 官方：https://ffmpeg.org/
- @steipete/summarize（ClawHub）：https://clawhub.ai/kn70pywhg0fyz996kpa8xj89s57yhv26/summarize
