# CosyVoice 3.0 部署与使用指南

> 阿里通义实验室 FunAudioLLM 团队出品 | 支持 9 种语言 18+ 方言

---

## 1. 简介

CosyVoice 是阿里通义实验室开源的语音生成大模型，最新版本为 **CosyVoice 3.0**（2025-12-15 发布）。

**核心特性：**
- 🎯 仅需 **3-10 秒**音频样本即可克隆相似音色
- 🌏 支持 **9 种语言**（中、英、日、韩、粤等）
- 🎛️ 支持 **指令控制**（语速、情感、音量）
- 🔓 Apache 2.0 完全开源可商用
- ⏱️ 支持 **实时流式** 推理

---

## 2. 声音样本准备

### 音频要求

| 参数 | 要求 |
|------|------|
| 格式 | WAV（推荐）、MP3、M4A |
| 时长 | **3-10 秒**（最短 3 秒，推荐 5-10 秒） |
| 采样率 | 16kHz 或 22.05kHz |
| 声道 | 单声道（Mono） |
| 音质 | 清晰无噪音，人声突出 |

### 录音建议

```
✅ 推荐：
- 安静室内，无背景音乐
- 使用手机/麦克风录制即可
- 内容：清晰朗读 3-10 句中文句子
- 语速自然，不要刻意放慢或加快

❌ 避免：
- 回声/混响明显的房间
- 背景有电视、空调、风扇噪音
- 录音距离过远（声音太小）
- 情绪过于激动的语音
```

### 文本内容建议

```text
建议朗读以下类型的句子：

1. 日常对话类：
   "今天天气真好，我们一起去公园散步吧。"
   "这个项目的进度需要加快，下周要给客户演示。"

2. 多音字覆盖：
   "银行存折的正确读法是 jìng 不是 zhēng。"
   "重庆的朝天门码头风景非常壮观。"

3. 英文句子（用于英文克隆）：
   "Hello, how are you doing today?"
   "The quick brown fox jumps over the lazy dog."
```

---

## 3. 本地部署

### 环境要求

```
- Python >= 3.8
- GPU: NVIDIA (推荐 RTX 3060 以上)
- 显存: >= 6GB（完整模型）
- 内存: >= 16GB
- 磁盘: 约 15GB（模型文件）
```

### 方式一：ModelScope 下载（推荐国内用户）

```bash
# 1. 安装 modelScope
pip install modelscope

# 2. 下载模型和代码
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice

# 3. 创建 conda 环境
conda create -n cosyvoice python=3.10
conda activate cosyvoice

# 4. 安装依赖
pip install -r requirements.txt
pip install -r requirements_enhance.txt

# 5. 下载预训练模型（通过 ModelScope）
python -m CosyVoice.download --model_name CosyVoice-300M
python -m CosyVoice.download --model_name CosyVoice-300M-SFT
python -m CosyVoice.download --model_name CosyVoice-300M-Instruct
```

### 方式二：Hugging Face

```bash
# 模型下载
git lfs install
git clone https://huggingface.co/FunAudioLLM/CosyVoice-300M
git clone https://huggingface.co/FunAudioLLM/CosyVoice-300M-SFT
git clone https://huggingface.co/FunAudioLLM/CosyVoice-300M-Instruct
```

---

## 4. 使用方法

### 4.1 Python API 调用

```python
# cosyvoice_inference.py
import torch
from cosyvoice import CosyVoice, CosyVoice2

# CosyVoice 2.0（推荐，3.0 正式版待发布）
cosyvoice = CosyVoice2('CosyVoice-300M-SFT', load_in_cache=True)

# 方法一：使用预设音色（无需参考音频）
# SFT 模式 - 使用预训练音色
output = cosyvoice.inference_sft(
    '今天天气真好，我们一起去公园散步吧。',
    '中文女声',  # 中文男声/中文女声/英文女声/英文男声
)
output.save('output_sft.wav')

# 方法二：使用自定义音色（音色克隆）
cosyvoice_icl = CosyVoice2('CosyVoice-300M', load_in_cache=True)

# 使用参考音频克隆音色
output = cosyvoice_icl.inference_zero_shot(
    '今天天气真好，我们一起去公园散步吧。',
    'path/to/your_reference_audio.wav',  # 参考音频路径
    'custom_speaker',  # 自定义名称
)
output.save('output_clone.wav')

# 方法三：指令控制（Instruct 模式）
cosyvoice_instruct = CosyVoice2('CosyVoice-300M-Instruct', load_in_cache=True)

output = cosyvoice_instruct.inference_instruct(
    '今天天气真好，我们一起去公园散步吧。',
    'path/to/your_reference_audio.wav',
    '请用开心的语气朗读这段话，语速稍快。',
)
output.save('output_instruct.wav')
```

### 4.2 WebUI 启动

```bash
# 启动 WebUI（单卡）
python webui.py --port 8080

# 启动 WebUI（多卡）
python webui.py --port 8080 --gpu 0,1

# 访问 http://localhost:8080
```

### 4.3 命令行推理

```bash
# SFT 模式（使用预设音色）
python CosyVoice/cli/cosyvoice-cli.py \
  --model CosyVoice-300M-SFT \
  --text "今天天气真好，我们一起去公园散步吧。" \
  --ref_audio None \
  --output output.wav

# Zero-shot 模式（自定义音色克隆）
python CosyVoice/cli/cosyvoice-cli.py \
  --model CosyVoice-300M \
  --text "今天天气真好，我们一起去公园散步吧。" \
  --ref_audio path/to/your_audio.wav \
  --output output.wav

# Instruct 模式（指令控制）
python CosyVoice/cli/cosyvoice-cli.py \
  --model CosyVoice-300M-Instruct \
  --text "今天天气真好，我们一起去公园散步吧。" \
  --ref_audio path/to/your_audio.wav \
  --instruction "请用开心的语气朗读" \
  --output output.wav
```

---

## 5. CosyVoice 3.0 新特性

**2025-12-15 发布的 CosyVoice 3.0 主要更新：**

| 特性 | 说明 |
|------|------|
| 语言支持 | 9 种语言 + 18+ 方言 |
| 发音修补 | 自动修正易错字发音 |
| 指令控制增强 | 更细腻的情感/风格控制 |
| 跨语言合成 | 用中文参考音频生成英文语音 |
| 推理速度 | 提升约 30% |

```python
# CosyVoice 3.0 新 API（待正式版发布后更新）
cosyvoice3 = CosyVoice3('CosyVoice-3.0')

# 更精细的控制
output = cosyvoice3.inference(
    text='今天天气真好',
    ref_audio='path/to/ref.wav',
    instruct='用温柔的语气，语速中等',
    language='zh',  # auto/zh/en/ja/ko/yue
)
```

---

## 6. 常见问题

### Q1: 克隆声音不相似？

**解决方案：**
1. 参考音频质量要好，清晰无噪音
2. 尝试不同的参考音频（不同内容）
3. 时长控制在 5-10 秒效果最佳
4. 可以尝试多个参考音频片段

### Q2: 生成速度慢？

**解决方案：**
1. 使用 GPU 推理（推荐 RTX 3060+）
2. 使用 `load_in_cache=True` 预加载模型
3. 安装 `flash-attn` 加速：`pip install flash-attn`
4. 使用流式推理减少等待感

### Q3: 英文发音不准确？

**解决方案：**
1. CosyVoice 3.0 对英文支持更好
2. 确保参考音频是英文（跨语言克隆效果有限）
3. 使用 CosyVoice-300M-Instruct 进行指令修正

### Q4: 如何部署 API 服务？

```python
# fastapi_inference.py
from fastapi import FastAPI
from pydantic import BaseModel
import base64
from cosyvoice import CosyVoice2

app = FastAPI()
cosyvoice = CosyVoice2('CosyVoice-300M-SFT', load_in_cache=True)

class TTSRequest(BaseModel):
    text: str
    speaker: str = '中文女声'

@app.post('/tts')
async def tts(request: TTSRequest):
    output = cosyvoice.inference_sft(request.text, request.speaker)
    output.save('/tmp/output.wav')
    with open('/tmp/output.wav', 'rb') as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    return {'audio': audio_b64}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)
```

---

## 7. 与 OpenClaw Skills 集成

### 方案一：通过命令行调用

```python
# /workspace/skills/voice-tts/SKILL.md 或相关技能中调用

def synthesize_speech(text: str, ref_audio: str, output_path: str):
    """调用 CosyVoice 生成语音"""
    import subprocess
    
    cmd = [
        'python', 'CosyVoice/cli/cosyvoice-cli.py',
        '--model', 'CosyVoice-300M',
        '--text', text,
        '--ref_audio', ref_audio,
        '--output', output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return output_path if result.returncode == 0 else None
```

### 方案二：作为 OpenClaw Agent 工具

```python
# 在 OpenClaw Skills 中注册为工具函数
import json
import wave
import io
from cosyvoice import CosyVoice2

cosyvoice = CosyVoice2('CosyVoice-300M', load_in_cache=True)

def cosyvoice_clone(text: str, ref_audio_path: str) -> str:
    """
    使用 CosyVoice 克隆音色生成语音
    输入: text (str) - 要转换的文本
          ref_audio_path (str) - 参考音频文件路径
    输出: WAV 音频文件路径
    """
    output_path = f'/workspace/tts_output/{uuid.uuid4().hex}.wav'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    result = cosyvoice.inference_zero_shot(text, ref_audio_path, 'temp')
    result.save(output_path)
    return output_path
```

---

## 8. 在线体验

| 平台 | 链接 | 说明 |
|------|------|------|
| 官网 | https://cosyvoice.net/ | 在线克隆体验 |
| ModelScope | https://www.modelscope.cn/models/AIDub/CosyVoice/summary | 模型下载 |
| HuggingFace | https://huggingface.co/FunAudioLLM/CosyVoice-300M | 模型下载 |
| 阿里云百炼 | https://help.aliyun.com/zh/model-studio/cosyvoice-large-model-for-speech-synthesis/ | API 服务 |
