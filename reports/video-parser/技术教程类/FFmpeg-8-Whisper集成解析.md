# FFmpeg 8.0 Whisper集成 — 视频背景音自动转文字

> 🤖 维护：视频解析方法总结Agent  
> 📅 新增日期：2026-03-29  
> 🔗 来源：FFmpeg官方 / IT之家 / 多媒体新青年

---

## 核心工具/API

- **FFmpeg 8.0**（内置Whisper滤镜）：多媒体框架，集成OpenAI Whisper语音识别
- **whisper.cpp**：Whisper模型的C/C++实现，性能高效
- **ffmpeg命令行**：纯命令行，无需Python环境

---

## 步骤流程

### 方式一：FFmpeg内嵌Whisper过滤（FFmpeg 8.0+）

```bash
# 基础用法：视频音频自动转SRT字幕
ffmpeg -i input.mp4 \
  -vn \
  -af "whisper=model=./models/ggml-base.bin:language=auto:format=srt" \
  -f null -

# 指定英文，输出JSON结构化
ffmpeg -i input.mp4 \
  -vn \
  -af "whisper=model=./models/ggml-medium.bin:language=en:format=json" \
  output.json

# 指定中文，自动检测
ffmpeg -i input.mp4 \
  -vn \
  -af "whisper=model=./models/ggml-large.bin:language=zh:format=srt" \
  output.srt
```

### 方式二：分步骤处理（兼容FFmpeg 7.x）

```bash
# Step 1: 提取音频
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav

# Step 2: Whisper.cpp转录
./main -m ./models/ggml-medium.bin -f audio.wav -of output --language zh

# Step 3: 生成带时间戳字幕
./main -m ./models/ggml-medium.bin -f audio.wav --output-srt
```

### 方式三：Python调用whisper.cpp

```python
import subprocess

def transcribe_with_whisper_cpp(video_path, model_size="medium"):
    # 提取音频
    audio_path = "/tmp/audio.wav"
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        audio_path
    ], check=True)
    
    # Whisper转录
    result = subprocess.run([
        "./whisper.cpp/main",
        "-m", f"./whisper.cpp/models/ggml-{model_size}.bin",
        "-f", audio_path,
        "--language", "zh",
        "--output-srt"
    ], capture_output=True, text=True)
    
    return result.stdout

transcript = transcribe_with_whisper_cpp("video.mp4", model_size="medium")
```

---

## 适用场景

- **长视频批量转录**：直接在FFmpeg管道中完成，无需Python中间层
- **直播/录播音频处理**：实时流或本地视频的一站式音频→字幕
- **服务器端部署**：无GPU环境下 whisper.cpp 性能优异（支持CUDA加速）
- **与其他FFmpeg滤镜链结合**：降噪→Whisper→输出，一步到位

---

## 避坑指南

| 问题 | 解决方案 |
|------|----------|
| FFmpeg 8.0尚未发布（截至2025年8月为预览版） | 可用 whisper.cpp 代替，命令兼容 |
| whisper模型文件下载慢 | 手动下载：`wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin` |
| 中文识别不准 | 指定`language=zh`，使用 medium 或 large 模型 |
| 音频含强背景音乐干扰 | 先降噪：`ffmpeg -i input -af "afftdn=nf=-25" clean.wav` 再转录 |
| SRT时间戳不对齐 | 检查采样率是否为16000Hz（Whisper要求） |

---

## 参考链接

- FFmpeg Whisper滤镜官方文档：https://ffmpeg.org/ffmpeg-filters.html#whisper
- whisper.cpp GitHub：https://github.com/ggerganov/whisper.cpp
- IT之家报道：https://www.ithome.com/0/875/832.htm
