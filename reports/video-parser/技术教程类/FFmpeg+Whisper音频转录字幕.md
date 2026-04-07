# 技术教程类 - FFmpeg+Whisper音频转录字幕方案

## 核心工具/API

| 工具 | 作用 | 备注 |
|------|------|------|
| **FFmpeg 8.x** | 音频提取 + Whisper滤镜调用 | 必须8.x版本才内置Whisper |
| **Whisper.cpp / Whisper模型** | 语音识别→文本/字幕 | 支持99种语言，含中文优化 |
| **Silero VAD**（可选） | 语音活动检测，过滤静音 | 提升转录准确率 |
| **CUDA**（可选） | GPU加速 | 需要NVIDIA显卡 |

---

## 步骤流程

### 方案一：FFmpeg内置Whisper滤镜（最简）

```bash
# 1. 下载 FFmpeg 8.x（https://ffmpeg.org/download.html）
# 2. 下载 Whisper 模型（base/medium/large）
wget https://raw.githubusercontent.com/ggml-org/whisper.cpp/master/models/download-ggml-model.sh
chmod +x download-ggml-model.sh
./download-ggml-model.sh base   # 或 medium / large-v3

# 3. 一行命令转录为SRT字幕
ffmpeg -i input.mp4 \
  -vn \
  -af "whisper=model=./models/ggml-base.bin:language=auto:queue=3:format=srt:use_gpu=true" \
  -f null -
```

### 方案二：Python Whisper（更灵活）

```bash
# 1. 安装依赖
pip install openai-whisper ffmpeg-python

# 2. 提取音频
ffmpeg -i input.mp4 -vn -ar 16000 -ac 1 audio.wav

# 3. Whisper转录
whisper audio.wav --model medium --language Chinese --output_format srt
```

### 方案三：高质量流水线（推荐技术教程）

```bash
# 步骤1：提取音频（16kHz单声道，Whisper推荐格式）
ffmpeg -i tutorial.mp4 -vn -ar 16000 -ac 1 -c:a pcm_s16le audio.wav

# 步骤2：VAD预处理（过滤静音片段）
whisper audio.wav --model medium \
  --language zh \
  --output_format json \
  --initial_prompt "这是一段技术教程视频，请准确转录专业术语"

# 步骤3：生成带时间戳的Markdown摘要
python parse_whisper_json.py --input result.json --output tutorial-notes.md
```

---

## 适用场景

- ✅ **技术教程视频**：提取操作步骤、命令、代码片段
- ✅ **会议/播客录音**：转写+时间戳，便于回溯
- ✅ **多语言视频**：生成双语字幕
- ✅ **本地视频处理**：无需上传，保护隐私
- ✅ **批量处理**：脚本循环处理整个文件夹

---

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| FFmpeg报错"找不到whisper滤镜" | FFmpeg版本<8.x | 升级到FFmpeg 8.x |
| GPU不可用（CUDA报错） | 驱动问题或无NVIDIA卡 | 加参数 `use_gpu=false` |
| 中文识别不准 | 模型太小或音频质量差 | 换用 `medium`/`large-v3`；指定 `language=zh` |
| 专业术语错误 | 通用模型缺乏垂直知识 | 用 `--initial_prompt` 提供领域背景 |
| 长音频内存溢出 | `queue` 参数过大 | 减小 `queue=3~5`，或分段处理 |
| 无声片段太多 | 视频含大量背景音乐 | 启用VAD：`vad_model=ggml-silero-v5.bin:vad_threshold=0.6` |

### 模型选择建议

| 场景 | 推荐模型 | 大小 | 速度 |
|------|----------|------|------|
| 快速预览/实时 | tiny / base | ~39~142MB | ⚡极快 |
| 日常转录（中文） | medium | ~1.5GB | 🐢较慢 |
| 高质量/专业术语 | large-v3 | ~3.1GB | 🐢🐢慢 |
| 平衡之选 | medium-q5_0（量化） | ~1.5GB | ⚡🐢中等 |

---

## 参考链接

- FFmpeg Whisper滤镜文档：https://ffmpeg.org/ffmpeg-filters.html#toc-whisper-1
- Whisper.cpp：https://github.com/ggml-org/whisper.cpp
- Whisper官方：https://github.com/openai/whisper
- FFmpeg下载：https://ffmpeg.org/download.html
