# F5-TTS — 扩散Transformer免训练语音合成

## 基本信息

| 项目 | 信息 |
|------|------|
| GitHub | https://github.com/SWivid/F5-TTS |
| Stars | ⭐ **13.8k** |
| 最新版本 | v1.1.15（2025-12-21）|
| 许可证 | MIT（代码）+ CC-BY-NC（预训练模型）|
| 中文支持 | ✅ 良好 |
| 声音克隆 | ✅ 参考音频合成（无需训练）|

## 核心亮点

- 🚀 **免训练合成**：只需提供参考音频 + 参考文本，无需任何训练
- ⚡ **扩散Transformer架构**：最新架构，音质自然
- 🌐 **多语言**：原生支持多语言合成
- 💻 **硬件友好**：支持 NVIDIA / AMD / Intel GPU 和 Apple Silicon
- 🐳 **Docker 部署**：一行命令完成部署
- ⚙️ **分块推理**：支持长文本分块生成，降低显存占用

## 技术原理

F5-TTS 基于 **扩散Transformer（Diffusion Transformer）** 架构：
- 输入：参考音频 + 参考文本 + 待合成文本
- 过程：扩散模型逐步去噪生成音频
- 输出：高保真语音

相比传统 TTS，F5-TTS 不需要针对特定音色进行训练，直接从参考音频中提取音色特征进行合成。

## 声音样本准备要求

| 项目 | 要求 |
|------|------|
| 音频格式 | WAV（推荐）|
| 推荐时长 | **5-30 秒**（越长合成越准确）|
| 采样率 | 16kHz - 48kHz |
| 录音环境 | 安静、无混响 |
| 参考文本 | **必须有**（可留空由 ASR 自动转录，但需额外显存）|

### 录音技巧
1. **时长选择**：30秒最佳，5秒最低可用
2. **内容匹配**：参考音频内容与合成内容语言相同效果更好
3. **质量要求**：清晰、无噪声、无回声
4. **情感覆盖**：覆盖不同情感可提升合成自然度

## 安装与使用

### 方法 1：pip 安装（⭐推荐）
```bash
pip install F5TTS
```

### 方法 2：源码安装
```bash
git clone https://github.com/SWivid/F5-TTS && cd F5-TTS && pip install -e .
```

### 方法 3：Docker
```bash
docker compose -f docker/docker-compose.yaml up
```

## 使用方法

### 命令行推理（⭐最简单）
```bash
f5-tts_infer-cli \
    --model F5TTS_v1_Base \
    --ref_audio "my_voice.wav" \
    --ref_text "这是参考音频对应的文本内容。" \
    --gen_text "要合成的语音内容，效果非常自然。"
```

### Python API
```python
from f5_tts import F5TTS

model = F5TTS(model_name="F5TTS_v1_Base")

# 免训练合成
audio = model.generate(
    text="今天天气真不错，我们出去散步吧。",
    ref_audio="my_voice.wav",
    ref_text="今天天气真不错，我们出去散步吧。",
)
audio.save("output.wav")
```

### WebUI
```bash
python app.py
# 浏览器打开 http://localhost:7860
```

## 性能基准

| 模型 | 并发 | 平均延迟 | RTF (PyTorch) | RTF (TRT-LLM) |
|------|------|---------|---------------|---------------|
| F5-TTS Base (Vocos) | 1 | - | 0.1467 | 0.0402 |
| F5-TTS Base (Vocos) | 2 | 253ms | 0.0394 | - |

> 测试环境：单张 L20 GPU，16 NFE（噪声函数评估步数）

## 与 OpenClaw Skills 集成

```python
from f5_tts import F5TTS
import uuid, os

_f5_model = None

def get_f5_model():
    global _f5_model
    if _f5_model is None:
        _f5_model = F5TTS(model_name="F5TTS_v1_Base")
    return _f5_model

def f5_tts_clone(text, ref_audio, ref_text, output_dir="/workspace/audio"):
    """
    F5-TTS 免训练语音合成 - OpenClaw Skill
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{uuid.uuid4().hex}.wav")
    model = get_f5_model()
    audio = model.generate(text=text, ref_audio=ref_audio, ref_text=ref_text)
    audio.save(output_path)
    return output_path
```

## 常见问题与解决

| 问题 | 解决方案 |
|------|----------|
| 合成质量不够好 | 增加参考音频时长至30秒；确保参考文本准确 |
| 音色偏差大 | 确保参考音频和生成文本语言一致 |
| 显存不足 | 使用分块推理（chunk inference）；减小 NFE |
| 长文本合成效果差 | 使用分块推理模式 |
| CPU 推理太慢 | 建议使用 GPU；Apple Silicon 可用 MPS 加速 |

## 最佳实践

1. **参考音频选择**：优先选择 30 秒高质量录音
2. **参考文本**：手动标注比 ASR 自动转录更准确
3. **语言一致性**：参考音频语言与合成文本语言一致时效果最佳
4. **NFE 参数**：默认 16 即可，降低可提速但质量略降
5. **分块推理**：长文本（>200字）建议开启分块
