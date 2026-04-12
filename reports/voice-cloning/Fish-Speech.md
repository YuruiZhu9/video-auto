# Fish Speech / OpenAudio 部署与使用指南

> ⚠️ **品牌升级通知（2025年内）**：Fish Speech 已正式更名为 **OpenAudio**，GitHub 仓库 `fishaudio/fish-speech` 保持不变，但新模型以 OpenAudio 品牌发布。详情见 [`OpenAudio-S1/README.md`](OpenAudio-S1/README.md)。

> Fish Audio 出品 | 10 秒零样本克隆 | 支持 20+ 语言

---

## 1. 简介

Fish Speech 是 Fish Audio 团队开发的开源 TTS 模型，采用 VQ-GAN + LLM 技术路线，无需传统音素对齐即可实现零样本克隆。

**核心特性：**
- 🎯 仅需 **10 秒**音频即可零样本克隆
- 🌍 支持 **20+ 语言**
- ⚡ 推理速度快（无音素对齐步骤）
- 🔧 高度可控，支持多音字、跨语言
- 📦 提供在线服务和本地部署

---

## 2. 在线体验

**官网：** https://fish.audio/zh-CN/

- 每天免费生成 50 次
- 支持声音模型选择和自定义克隆
- 无需安装，直接使用

---

## 3. 本地部署

### 环境要求

```
- Python >= 3.10
- GPU: NVIDIA >= 4GB VRAM
- CUDA >= 11.8
- 磁盘: ~10GB（模型文件）
```

### 安装

```bash
# 克隆项目
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech

# 创建环境
conda create -n fish-speech python=3.10
conda activate fish-speech

# 安装依赖
pip install -r requirements.txt

# 安装 fish-speech
pip install -e .

# 下载预训练模型
python -m fish_audio.tool.download_model --model-name "fish-speech-1.4"
# 或选择 1.5 版本
python -m fish_audio.tool.download_model --model-name "fish-speech-1.5"
```

### Docker 部署

```bash
# GPU 版本
docker compose up -d
# 访问 http://localhost:7860

# CPU 版本（慢）
docker compose -f docker-compose.cpu.yaml up -d
```

---

## 4. 声音样本准备

### 音频要求

| 参数 | 要求 |
|------|------|
| 格式 | WAV、MP3、AAC |
| 时长 | **10-90 秒**（推荐 30 秒） |
| 采样率 | 16kHz 或 44.1kHz |
| 音质 | 清晰无噪音 |

### 录音建议

```text
✅ 推荐：
- 安静室内录音
- 内容多样化：不同句子、不同情绪
- 30 秒左右最佳
- 语速自然

✅ 文本内容示例：
"今天天气真好，我们一起去公园散步吧。"
"人工智能技术正在改变我们的生活方式。"
"很高兴认识大家，我是 Fish Speech。"
```

---

## 5. 使用方法

### 5.1 WebUI

```bash
python tools/webui.py
# 访问 http://localhost:7860
```

**WebUI 功能：**
- 上传参考音频
- 输入要合成的文本
- 调整语速、音量等参数
- 生成并下载音频

### 5.2 Python API

```python
from fish_audio import FishSpeech

# 初始化
model = FishSpeech("fish-speech-1.5")

# 零样本克隆
result = model.generate(
    text="今天天气真好，我们一起去公园散步吧。",
    reference_audio="path/to/your_audio.wav",
    reference_text="今天天气真好，我们一起去公园散步吧。",  # 参考音频文本
)

# 保存
result.save("output.wav")

# ============ 高级参数 ============
result = model.generate(
    text="今天天气真好！",
    reference_audio="path/to/your_audio.wav",
    reference_text="参考音频对应的文本",
    
    # 生成参数
    max_tokens=2048,
    top_k=50,
    top_p=0.9,
    temperature=0.7,
    
    # 语音控制
    speaker_id=0,
    speed=1.0,
    prompt_language="zh",  # 参考音频语言
    inference_language="zh",  # 生成语言
)
```

### 5.3 命令行推理

```bash
# 零样本推理
python -m fish_audio.inference \
  --text "今天天气真好，我们一起去公园散步吧。" \
  --reference_audio path/to/your_audio.wav \
  --reference_text "参考音频的文本内容" \
  --output output.wav

# 批处理
python -m fish_audio.inference \
  --text "今天天气真好" \
  --audio_folder path/to/reference_audios/ \
  --output_folder path/to/output/
```

### 5.4 微调训练（可选）

```bash
# 准备训练数据
python tools/prepare_data.py \
  --dataset_path /path/to/your/dataset \
  --output_path /path/to/processed/data \
  --num_workers 4

# 开始训练
python tools/train.py \
  --config configs/finetune.yaml \
  --exp_name my_voice \
  --data_path /path/to/processed/data

# 训练完成后使用微调模型
python -m fish_audio.inference \
  --model path/to/finetuned/model \
  --text "要合成的文本" \
  --reference_audio path/to/your_audio.wav
```

---

## 6. 常见问题

### Q1: 与 CosyVoice 相比有何优势？

| 方面 | Fish Speech | CosyVoice |
|------|------------|----------|
| 技术路线 | VQ-GAN + LLM | 自回归 Transformer |
| 推理速度 | ⚡ 更快 | 中等 |
| 中文效果 | 好 | 极好 |
| 跨语言 | 更强 | 一般 |
| 指令控制 | 一般 | 丰富 |

**结论：** 跨语言合成选 Fish Speech，中文专属选 CosyVoice。

### Q2: 推理显存不足？

```bash
# 使用量化版本
python -m fish_audio.inference \
  --text "文本" \
  --reference_audio "ref.wav" \
  --quantize 8bit  # 8bit 量化，降低显存占用
```

### Q3: 音质不佳？

1. 确保参考音频质量好（清晰无噪音）
2. 尝试不同的参考音频
3. 增加参考音频时长（30-60 秒）

---

## 7. 与 OpenClaw Skills 集成

```python
# fish_speech_tool.py
from fish_audio import FishSpeech

_fish_model = None

def get_fish_model():
    global _fish_model
    if _fish_model is None:
        _fish_model = FishSpeech("fish-speech-1.5")
    return _fish_model

def fish_speech_clone(
    text: str,
    ref_audio: str,
    ref_text: str = None,
    output_path: str = "output.wav",
) -> str:
    """
    使用 Fish Speech 零样本克隆
    
    Args:
        text: 要合成的文本
        ref_audio: 参考音频路径
        ref_text: 参考音频对应的文本（可选）
        output_path: 输出路径
    
    Returns:
        生成的音频文件路径
    """
    import os
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    model = get_fish_model()
    
    if ref_text is None:
        ref_text = text  # 使用相同文本
    
    result = model.generate(
        text=text,
        reference_audio=ref_audio,
        reference_text=ref_text,
    )
    
    result.save(output_path)
    return output_path
```
