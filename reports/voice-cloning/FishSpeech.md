# Fish Speech — 开源最强零样本克隆 TTS

---

## 基本信息

| 项目 | 信息 |
|------|------|
| GitHub | https://github.com/fishaudio/fish-speech |
| Stars | ⭐ **24.4k** |
| 最新版本 | v1.5.1（2025-05-31）|
| 许可证 | Apache 2.0（代码）+ CC-BY-NC-SA-4.0（模型）|
| 中文支持 | ✅ 极佳 |
| 声音克隆 | ✅ 支持零样本（10-30秒）|

---

## 核心亮点

- 🏆 **TTS-Arena2 排行榜 #1**（当前开源最强）
- ⚡ **极速推理**：RTX 4090 上实时因子约 **1:7**（生成速度是实时速度7倍）
- 🎯 **零样本克隆**：仅需 10-30 秒音频即可克隆声音，无需任何训练
- 🌐 **多语言**：中文、英语、日语、韩语、法语、德语、阿拉伯语、西班牙语
- 💻 **GPU 可选**：S1-mini（0.5B）版本 1GB VRAM 可运行，部分功能支持 CPU

---

## 声音样本准备要求

| 项目 | 要求 |
|------|------|
| 音频格式 | WAV / MP3 / FLAC |
| 推荐时长 | 零样本：10-30秒；精细克隆：1-5分钟 |
| 采样率 | 16kHz - 48kHz |
| 录音环境 | **安静、无回声、无背景音乐** |
| 音频质量 | 建议 128kbps 以上 |
| 参考文本 | 零样本时必须有对应文本；微调时可自动对齐 |

### 录音建议
1. 使用手机或专业麦克风，在安静房间录制
2. 朗读清晰，语速适中，覆盖不同情感（陈述、疑问、感叹）
3. 避免口水音、喷麦、背景噪音
4. 音频时长不够时，可多段拼接（推荐同一人的多段音频）

---

## 安装与使用

### 安装
```bash
git clone https://github.com/fishaudio/fish-speech
cd fish-speech
pip install -r requirements.txt
```

### 模型下载（首次运行自动下载）
```bash
# 完整版 S1 (4B参数)
python -c "from fish_speech.models import FishSpeech; FishSpeech.from_pretrained('fishaudio/fish-speech-1-s1')"

# 轻量版 S1-mini (0.5B参数，1GB VRAM)
python -c "from fish_speech.models import FishSpeech; FishSpeech.from_pretrained('fishaudio/fish-speech-1-s1-mini')"
```

### Python API — 零样本克隆（推荐）
```python
from fish_speech import FishSpeech

model = FishSpeech("fishaudio/fish-speech-1-s1")

# 仅需10-30秒参考音频
result = model.generate(
    text="今天天气真不错，我们出去走走吧。",
    reference_audio="my_voice.wav",
    reference_text="今天天气真不错，我们出去走走吧。",  # 参考音频对应的文本
)
result.save("output.wav")
print("✅ 音频已生成: output.wav")
```

### WebUI（可视化界面）
```bash
python tools/webui.py
# 浏览器打开 http://localhost:7860
```

### 命令行推理
```bash
python fish_speech/inference.py \
    --text "要合成的文本" \
    --reference_audio my_voice.wav \
    --reference_text "参考音频文本" \
    --output output.wav
```

---

## 微调（可选，提升克隆质量）

如果零样本效果不够好，可以用少量数据微调：

### 数据准备
```bash
# 将音频和文本放入 datasets/ 目录
# 目录结构：
# datasets/
#   ├── speaker1/
#   │   ├── audio1.wav
#   │   ├── audio1.txt
#   │   ├── audio2.wav
#   │   └── audio2.txt

# 自动处理数据对齐
python tools/prepare_dataset.py \
    --input ./datasets \
    --output ./processed
```

### 微调训练
```bash
python fish_speech/train.py \
    --model-name fish-speech-1-s1 \
    --train-data ./processed \
    --epochs 100 \
    --batch-size 8 \
    --gradient-accumulation-steps 2 \
    --output-dir ./checkpoints
```

### 使用微调模型
```python
model = FishSpeech("./checkpoints/final_model")
result = model.generate(
    text="使用微调模型合成的语音，效果更好。",
    reference_audio="my_voice.wav",
    reference_text="...",
)
```

---

## 与 OpenClaw Skills 集成

### 集成方案 1：Python subprocess 调用

```python
import subprocess
import json
import uuid
import os

def fish_speech_clone(text, ref_audio_path, ref_text, output_dir="/workspace/audio"):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{uuid.uuid4().hex}.wav")
    
    cmd = [
        "python", "fish_speech/inference.py",
        "--text", text,
        "--reference_audio", ref_audio_path,
        "--reference_text", ref_text,
        "--output", output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and os.path.exists(output_path):
        return output_path
    else:
        raise Exception(f"Fish Speech 推理失败: {result.stderr}")

# 使用示例
audio_path = fish_speech_clone(
    text="你好，我是用你的声音合成的。",
    ref_audio_path="/workspace/voice_samples/user_voice.wav",
    ref_text="你好，这是我的参考音频。"
)
```

### 集成方案 2：Python API 直接调用

```python
from fish_speech import FishSpeech
import uuid

model = FishSpeech("fishaudio/fish-speech-1-s1")

def generate_voice_clone(text, ref_audio, ref_text):
    output = f"/workspace/audio/{uuid.uuid4().hex}.wav"
    result = model.generate(
        text=text,
        reference_audio=ref_audio,
        reference_text=ref_text,
    )
    result.save(output)
    return output

# 存储模型实例供复用
_voice_model = None

def get_voice_model():
    global _voice_model
    if _voice_model is None:
        _voice_model = FishSpeech("fishaudio/fish-speech-1-s1")
    return _voice_model
```

---

## 常见问题与解决

| 问题 | 解决方案 |
|------|----------|
| 音色相似度不够 | 使用微调模式；增加参考音频时长（推荐2-5分钟） |
| 显存不足（OOM） | 使用 S1-mini 版本（0.5B），1GB VRAM 可运行 |
| 英文好中文差 | 使用中文微调底模：`fishaudio/bilingual-zh-en-s1` |
| 生成速度慢 | 使用量化版本（INT8/INT4）；S1-mini 速度更快 |
| 文本有错字 | 检查参考文本是否准确，ASR 识别错误的文本需手动修正 |
| 无参考文本 | 可留空，模型会尝试自动转录（效果可能下降）|

---

## 性能对比

| 模型 | WER | CER | Speaker Distance | 显存需求 |
|------|-----|-----|-----------------|---------|
| S1 (4B) | 0.8% | 0.4% | 0.332 | 6GB+ |
| S1-mini (0.5B) | 1.1% | 0.5% | 0.380 | 1GB+ |

> TTS-Arena2 综合排名第一，超越所有其他开源 TTS 模型
