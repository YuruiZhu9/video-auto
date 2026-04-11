# 开源项目演示类 — FFmpeg + Whisper 本地解析方案

## 核心工具/API

- **FFmpeg**：开源音视频处理瑞士军刀，用于提取音频流、视频帧、时间戳切片
- **OpenAI Whisper**（本地）：离线音频转写模型，支持 99+ 语言，中文识别准确率极高
- **Python + whisper**：`pip install openai-whisper` 或 `pip install faster-whisper`（加速版）
- **yt-dlp**：`/app/.venv/bin/yt-dlp` 已安装，用于下载在线演示视频
- **videos_understand / images_understand**：OpenClaw 内置多模态理解，补充 Whisper 的视觉分析能力

---

## 步骤流程

### 完整工作流（推荐）

```
阶段1：视频获取
  ├─ 本地视频 → 直接进入阶段2
  └─ 在线视频 → yt-dlp 下载 → 阶段2

阶段2：音频提取
  ├─ ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
  └─ 提取 WAV（Whisper 推荐输入格式）

阶段3：Whisper 转写
  ├─ 命令行：whisper audio.wav --model medium --language zh
  ├─ Python API：whisper.transcribe("audio.wav")
  └─ faster-whisper（推荐）：速度提升 2-3 倍，内存占用更低

阶段4：结构化输出
  ├─ 时间戳对齐：Whisper 输出带 timestamp 的 SRT/VTT 字幕
  ├─ 分段整理：按语义分段 + LLM 总结
  └─ 命令提取：正则匹配命令行代码片段
```

### FFmpeg 音频提取

```bash
# 标准提取（16kHz 单声道 WAV，Whisper 最优格式）
ffmpeg -i demo.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav

# 快速剪切（只提取前30分钟，节省处理时间）
ffmpeg -i demo.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 -t 1800 audio.wav

# 提取音频为 MP3（体积更小，但识别准确率略低）
ffmpeg -i demo.mp4 -vn -acodec libmp3lame -ab 128k audio.mp3
```

### Whisper 模型选择

| 模型 | 参数量 | 内存需求 | 速度 | 中文准确率 | 推荐场景 |
|------|--------|----------|------|------------|----------|
| `tiny` | 39M | ~1GB | 极快 | 一般 | 快速测试 |
| `base` | 74M | ~1GB | 快 | 良好 | 日常使用 |
| `small` | 244M | ~2GB | 中等 | 优秀 | **推荐首选** |
| `medium` | 769M | ~5GB | 较慢 | 极佳 | 高质量需求 |
| `large` | 1550M | ~10GB | 慢 | 最佳 | 最高精度 |

**faster-whisper（推荐）**：使用 CTranslate2 加速，比标准 Whisper 快 2-4 倍
```bash
pip install faster-whisper
```

```python
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.wav", beam_size=5)

for segment in segments:
    print(f"[{segment.start:.1f}s - {segment.end:.1f}s] {segment.text}")
```

### 命令行代码提取（正则方案）

```python
import re

# Whisper 输出示例
transcript = """
今天我们来演示这个开源项目，首先克隆仓库
git clone https://github.com/example/repo.git
cd repo
pip install -r requirements.txt
然后启动服务
python app.py --port 8080
"""

# 提取所有命令行
command_pattern = r'(git\s+\w+|pip\s+install|npm\s+\w+|python\s+\S+|docker\s+\w+|curl\s+\S+|wget\s+\S+)'
commands = re.findall(command_pattern, transcript, re.IGNORECASE)
print(commands)

# 提取 URL
url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
urls = re.findall(url_pattern, transcript)
print(urls)
```

### 视频帧提取（配合视觉分析）

```bash
# 均匀采样：每60秒一帧
ffmpeg -i demo.mp4 -vf "fps=1/60" frame_%03d.jpg

# 按时间戳提取关键帧（如视频时间轴标注的节点）
ffmpeg -ss 00:05:30 -i demo.mp4 -frames:v 1 -c:v png frame_5m30s.png

# 生成缩略图网格（便于快速浏览整个视频内容）
ffmpeg -i demo.mp4 -vf "select=not(mod(n\,300)),scale=320:180,tile=4x4" thumbs.jpg
```

---

## 适用场景

- ✅ 开源项目 GitHub README 配套演示视频
- ✅ 技术博主的产品 Demo、功能演示视频
- ✅ 命令行工具使用教程（Whisper 识别命令行效果极佳）
- ✅ 会议录像、工作坊录屏
- ✅ 需要离线处理、不想发送数据到第三方的场景
- ✅ 需要高准确率中文转写的场景（Whisper 中文能力很强）
- ✅ 批量处理多个视频的自动化流水线

---

## 避坑指南

- **Whisper 环境依赖**：OpenClaw 环境中未预装 Whisper，需手动安装：
  ```bash
  pip install faster-whisper  # 推荐，比标准版快 2-4 倍
  ```
- **内存不足**：`large` 模型需要 10GB+ 内存，生产环境推荐 `small` 或 `medium`
- **音频质量差**：背景音乐/多人同时说话会显著降低准确率，建议先分离人声：
  ```bash
  # 用 spleeter 分离人声（需额外安装）
  spleeter separate -i audio.wav -o output/
  ```
- **长音频处理**：Whisper 对超长音频（>3小时）支持有限，建议先按静音段落切分
- **中文+英文混合**：Whisper 在混合语言场景表现良好，但 prompt 指定语言可提升准确率
- **视频文件编码问题**：部分编码格式（如 rmvb）ffmpeg 无法直接处理，需先转码：
  ```bash
  ffmpeg -i input.rmvb -c:v libx264 -c:a aac output.mp4
  ```
- **yt-dlp 下载失败**：B站等平台需要登录 Cookie，方案：
  ```bash
  # 使用浏览器 Cookie（推荐）
  yt-dlp --cookies-from-browser chrome "https://bilibili.com/video/BVxxx"
  ```

---

## 参考链接

- OpenAI Whisper 官方：<https://github.com/openai/whisper>
- faster-whisper（加速版）：<https://github.com/guillaumekln/faster-whisper>
- FFmpeg 官方：<https://ffmpeg.org>
- yt-dlp（视频下载）：<https://github.com/yt-dlp/yt-dlp>
- spleeter（人声分离）：<https://github.com/deezer/spleeter>
- video-frames Skill：`/app/openclaw/skills/video-frames/SKILL.md`
