# Qwen3-TTS 部署与使用指南

> 适用版本：2026年1月发布版 | 难度：⭐⭐（较易）

---

## 1. 概述

Qwen3-TTS 是阿里Qwen团队2026年1月发布的开源多语言文本转语音模型，在零样本语音克隆、自然语言声音描述、情感控制方面达到了开源SOTA水平。

**适用场景：**
- 零样本语音克隆（3秒参考音频）
- 自然语言声音设计（"a warm elderly man"）
- 多语言内容生成（中文/英文/日文/韩文等）
- LLM对话语音合成

---

## 2. 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| Python | 3.8+ | 3.10 |
| GPU | GTX 1080 | RTX 3090/4090/5090 |
| 显存 | 6GB（0.6B模型4GB） | 8GB+ |
| 内存 | 8GB | 16GB+ |
| 磁盘 | 10GB | 20GB+ |

**模型规格对比：**
| 模型 | 参数量 | 显存要求 | 生成速度（RTX 4090） | 质量 |
|------|--------|----------|---------------------|------|
| Qwen3-TTS-1.7B-Base | 1.7B | 6-8GB | 实时 | 最高 |
| Qwen3-TTS-0.6B-Base | 0.6B | 4-6GB | 实时 | 高 |
| Qwen3-TTS-1.7B-VoiceDesign | 1.7B | 6-8GB | 实时 | 最高（含声音设计） |
| Qwen3-TTS-1.7B-CustomVoice | 1.7B | 6-8GB | 实时 | 最高（含自定义音色） |

---

## 3. 安装步骤

### 3.1 基础安装

```bash
# 1. 创建虚拟环境
conda create -n qwen3-tts python=3.10 -y
conda activate qwen3-tts

# 2. 安装PyTorch（CUDA 12.8）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

# 3. 安装Qwen3-TTS
pip install qwen3-tts

# 4. （可选）安装FlashAttention（提速2-3倍）
pip install -U flash-attn --no-build-isolation
```

**国内镜像安装：**
```bash
# 使用清华/阿里云pip镜像
pip install qwen3-tts -i https://pypi.tuna.tsinghua.edu.cn/simple

# 模型下载使用HuggingFace镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### 3.2 验证安装

```python
from qwen3_tts import Qwen3TTS
print("Qwen3-TTS 安装成功！")
```

---

## 4. 推理使用

### 4.1 Web界面启动

```bash
# 启动本地Web服务
qwen-tts-demo Qwen/Qwen3-TTS-12Hz-1.7B-Base \
  --no-flash-attn \
  --ip 0.0.0.0 \
  --port 8000

# 访问 http://localhost:8000 使用Web界面
```

### 4.2 Python推理

```python
from qwen3_tts import Qwen3TTS
import soundfile as sf
import numpy as np

# 加载模型（首次会自动下载）
model = Qwen3TTS(
    model_path="Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    quantize="int8"  # int8量化，减少显存占用
)

# === 模式1：直接生成（使用模型默认音色） ===
audio = model.generate(
    text="你好，我是Qwen3-TTS，今天天气真不错！",
    language="auto"  # 自动检测语言
)
sf.write("output_default.wav", audio, 24000)

# === 模式2：自然语言描述声音 ===
audio = model.generate(
    text="欢迎收听本期节目，今天我们来聊聊AI的发展。",
    voice="a warm and friendly middle-aged male radio host"  # 自然语言描述
)
sf.write("output_described.wav", audio, 24000)

# === 模式3：零样本克隆 ===
audio = model.generate(
    text="这段文字将以参考音频的音色呈现。",
    ref_audio="ref_voice.wav"  # 3秒参考音频
)
sf.write("output_cloned.wav", audio, 24000)

# === 模式4：带语速控制 ===
audio = model.generate(
    text="这是一个较快的播报语速。",
    ref_audio="ref_voice.wav",
    speed=1.5  # 1.0=正常，>1.0=更快
)
sf.write("output_fast.wav", audio, 24000)
```

### 4.3 CLI工具（Simon Willison）

```bash
# 安装
pip install uv

# 使用自然语言描述声音
uv run https://tools.simonwillison.net/python/q3_tts.py \
  "Hey there, this is a pirate voice!" \
  -i "gruff pirate voice" \
  -o pirate.wav

# 使用参考音频克隆
uv run https://tools.simonwillison.net/python/q3_tts.py \
  "今天我们来测试一下克隆效果。" \
  -r reference.wav \
  -o cloned.wav
```

---

## 5. 性能基准测试

**测试环境：RTX 3090 | 生成35秒音频**

| 模型 | 耗时 | RTF（实时因子） |
|------|------|-----------------|
| Qwen3-TTS-1.7B | 44秒 | ~1.26 |
| Qwen3-TTS-0.6B | 30秒 | ~0.86 |
| Qwen3-TTS-1.7B + FlashAttn | 实时 | <1.0 |
| GPT-SoVITS v2（对比） | 90秒+ | ~3.0 |

---

## 6. 微调训练（CustomVoice）

**适用场景：** 需要训练专属音色，适合长期固定角色使用

### 6.1 训练数据准备

```bash
# 目录结构
data/
├── speaker_001/
│   ├── audio_001.wav
│   ├── audio_002.wav
│   └── ...
└── metadata.csv

# metadata.csv格式
audio_path,duration,transcript
speaker_001/audio_001.wav,5.2,今天天气真好
speaker_001/audio_002.wav,8.1,欢迎收听我们的节目
```

**数据要求：**
- 时长：建议30分钟以上
- 采样率：16kHz+
- 质量：安静、清晰、无混响

### 6.2 训练命令

```bash
python finetune.py \
  --model_path Qwen/Qwen3-TTS-12Hz-1.7B-Base \
  --train_data data/ \
  --output_dir checkpoints/ \
  --epochs 10 \
  --batch_size 4 \
  --learning_rate 1e-4
```

### 6.3 使用微调后模型

```python
model = Qwen3TTS(
    model_path="checkpoints/final_model",
    quantize="int8"
)
audio = model.generate(
    text="这是经过微调后的专属音色。",
    ref_audio=None  # 不需要参考音频
)
```

---

## 7. 与OpenClaw集成

### 7.1 方案一：Python脚本调用

```python
# /workspace/voice-cloning/qwen3_tts_infer.py
import sys
import soundfile as sf
from qwen3_tts import Qwen3TTS

def generate_speech(text, ref_audio=None, voice_desc=None, output_path="output.wav"):
    model = Qwen3TTS(
        model_path="Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        quantize="int8"
    )
    
    kwargs = {"text": text, "language": "auto"}
    if ref_audio:
        kwargs["ref_audio"] = ref_audio
    elif voice_desc:
        kwargs["voice"] = voice_desc
    
    audio = model.generate(**kwargs)
    sf.write(output_path, audio, 24000)
    return output_path

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "你好，这是测试音频。"
    ref_audio = sys.argv[2] if len(sys.argv) > 2 else None
    output = sys.argv[3] if len(sys.argv) > 3 else "/workspace/voice-cloning/output.wav"
    generate_speech(text, ref_audio, output_path=output)
```

**OpenClaw exec调用：**
```bash
cd /workspace/voice-cloning
python qwen3_tts_infer.py "今天我们来测试一下Qwen3-TTS的克隆效果" \
  "ref-audio/my-voice.wav" \
  "results/test.wav"
```

### 7.2 方案二：FastAPI服务

```python
# /workspace/voice-cloning/api_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import soundfile as sf
import base64
from qwen3_tts import Qwen3TTS
import io

app = FastAPI()
model = Qwen3TTS("Qwen/Qwen3-TTS-12Hz-1.7B-Base", quantize="int8")

class TTSRequest(BaseModel):
    text: str
    ref_audio_b64: str | None = None
    voice_desc: str | None = None

@app.post("/tts")
async def tts(request: TTSRequest):
    ref_audio = None
    if request.ref_audio_b64:
        audio_bytes = base64.b64decode(request.ref_audio_b64)
        ref_audio = "temp_ref.wav"
        with open(ref_audio, "wb") as f:
            f.write(audio_bytes)
    
    kwargs = {"text": request.text, "language": "auto"}
    if ref_audio:
        kwargs["ref_audio"] = ref_audio
    elif request.voice_desc:
        kwargs["voice"] = request.voice_desc
    
    audio = model.generate(**kwargs)
    
    buffer = io.BytesIO()
    sf.write(buffer, audio, 24000, format="WAV")
    return {"audio_b64": base64.b64encode(buffer.getvalue()).decode()}
```

---

## 8. 常见问题FAQ

**Q：首次运行很慢？**
A：首次会自动下载模型（约3-5GB），建议提前准备好网络或使用镜像。

**Q：显存不足？**
A：使用 `--quantize int8` 量化，显存占用减少约50%。

**Q：中文发音不自然？**
A：确保使用中文语言模型（默认auto即可），或显式设置 `language="zh"`。

**Q：如何固定音色不每次变化？**
A：对于生成模式，可固定随机种子；对于克隆模式，使用相同的参考音频即可。

**Q：支持实时流式推理吗？**
A：当前版本主要是非流式输出（先生成完整音频），流式正在开发中。

---

## 🆕 CustomVoice-oQ8 量化版（社区版，2026-04-12 新增）

| 指标 | 数据 |
|------|------|
| 模型名 | `beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8` |
| 参数量 | **~0.5B**（原始 1.7B，8位量化）|
| 上传者 | beaupi（社区）|
| HuggingFace | [beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8](https://huggingface.co/beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8) |
| 许可证 | Apache 2.0（继承官方）|
| 适用场景 | **CPU 推理 / 低显存设备** |
| 原版对照 | Qwen3-TTS-12Hz-1.7B-CustomVoice（1.7B → 量化后 ~0.5B）|

### 特点
- 参数量缩减约 **70%**（1.7B → 0.5B），适合 CPU 或 4GB 以下显存
- 保留 9 种预置音色（Vivian、Serena、Uncle_Fu 等）+ 指令控制风格
- 8-bit 量化版，推理速度更快

### 下载
```bash
huggingface-cli download beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8 --local-dir ./model
```

### 使用
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8")
tokenizer = AutoTokenizer.from_pretrained("beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8")
```
