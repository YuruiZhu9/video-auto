# UniVoice — ASR+TTS 统一架构语音模型

> 🤖 免费语音克隆方案Agent | 2026-03-27 新增

---

## 基本信息

| 项目 | 内容 |
|------|------|
| **模型名称** | UniVoice |
| **GitHub** | https://github.com/gwh22/UniVoice |
| **Hugging Face** | UniVoice-TTS: https://huggingface.co/guanwenhao/univoice-tts<br/>UniVoice-All: https://huggingface.co/guanwenhao/univoice-all |
| **论文** | https://arxiv.org/pdf/2510.04593 |
| **License** | **MIT License**（完全免费可商用） |
| **发布时间** | 2025年（arXiv: 2510.04593） |
| **GitHub Stars** | 111 |
| **核心创新** | ASR+TTS 统一架构 · Flow-Matching · 连续表示 |

---

## 核心定位

UniVoice 是一个**创新性的统一架构模型**，将自动语音识别（ASR）和文本转语音（TTS）融合在同一个 LLM 框架中，实现"听"与"说"能力的双向迁移。与传统分离式 TTS 不同，UniVoice 通过连续表示（而非离散语音 Token）避免信息丢失，在零样本声音克隆任务上达到或超越单一任务模型。

---

## 技术架构

| 组件 | 技术详情 |
|------|----------|
| **LLM 基座** | SmolLM2-360M（3.6亿参数）——业界最小的 LLM 基座之一 |
| **技术路线** | Flow-Matching（流匹配）声音生成（非自回归扩散） |
| **核心创新** | 双注意力机制（Dual Attention） |
| **表示方式** | 连续表示（continuous representations），非离散 Token |
| **总参数量** | ~0.4B + 组件（极轻量） |

### 双注意力机制（关键创新）

```
ASR任务（语音→文本）: 因果掩码（Causal Mask）
TTS任务（文本→语音）: 双向注意力（Bidirectional Attention）
```

这个设计有效缓解了自回归模型与 Flow-Matching 模型之间的内在分歧，让同一个模型既能"听懂"也能"说"。

### 文本前缀条件语音填充（Text-prefix-conditioned Speech Infilling）

这是 UniVoice 实现零样本声音克隆的核心技术——通过文本前缀引导，实现高保真零样本声音克隆，无需针对目标音色进行微调。

---

## 性能表现

| 任务 | 表现 |
|------|------|
| **ASR（语音识别）** | 达到或超越同期单一任务 ASR 模型 |
| **零样本 TTS（声音克隆）** | 达到或超越同期单一任务 TTS 模型 |
| **统一建模** | 一个模型同时搞定听和说，无缝切换 |

---

## 支持能力

### ✅ 核心功能
- **零样本声音克隆**：10-30秒参考音频即可克隆音色
- **ASR 语音识别**：同一模型完成语音转文字
- **语音续写**：给定前文音频，续写后续语音
- **语音编辑**：修改音频中的特定内容
- **跨语种能力**：利用 ASR 预训练知识实现跨语言克隆

### ❌ 局限性
- **SmolLM2 基座较小**：360M 参数的 LLM 在文本理解上弱于 Qwen/Llama
- **推理速度**：Flow-Matching 非实时（扩散过程）
- **中文支持**：开源版本以英文为主，中文能力待测

---

## 硬件要求

| 项目 | 要求 |
|------|------|
| **GPU** | CUDA 兼容 GPU |
| **CUDA 版本** | ≥ 11.8 |
| **Python** | ≥ 3.10 |
| **显存估算** | ~2-3GB（0.4B 模型，极轻量） |
| **推荐环境** | conda 虚拟环境 |

---

## 快速开始

### 安装

```bash
git clone https://github.com/gwh22/UniVoice.git
cd UniVoice
conda env create -f environment.yaml
conda activate univoice
```

### 推理使用

```bash
# ASR 任务（语音识别）
sh scripts/infer_asr.sh

# TTS 任务（语音合成 + 克隆）
sh scripts/infer_tts.sh
```

### Python API

```python
import torch
from univoice import UniVoiceTTS

# 加载模型
model = UniVoiceTTS.from_pretrained("guanwenhao/univoice-tts")
model.eval()

# 零样本克隆生成
audio = model.generate(
    text="今天天气真不错！",
    ref_audio="my_voice.wav",  # 参考音频（10-30秒）
)

# ASR 语音识别
text = model.recognize(audio_file="input.wav")

# 保存
audio.save("output.wav")
```

---

## 训练（微调）

```bash
# 全量训练（ASR + TTS 联合）
sh scripts/train_all.sh

# 或分别训练
sh scripts/train_asr.sh  # ASR 专项
sh scripts/train_tts.sh  # TTS 专项
```

---

## 与其他方案对比

| 维度 | UniVoice | CosyVoice 3.0 | Qwen3-TTS | F5-TTS |
|------|----------|----------------|-----------|--------|
| **架构** | ASR+TTS 统一 | LLM-TTS | LLM-TTS | 自回归扩散 |
| **克隆方式** | 零样本 | 零样本+微调 | 零样本 | 零样本 |
| **基座模型** | SmolLM2-360M | Qwen2-0.5B | Qwen3 | 原创 |
| **参数量** | ~0.4B | ~0.5B-1B | ~1.7B | 未公开 |
| **中文支持** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **推理速度** | ⭐⭐⭐（非实时） | ⭐⭐⭐⭐⭐（150ms） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **License** | MIT | Apache 2.0 | Apache 2.0 | MIT |
| **独特优势** | 统一架构·极轻量 | 阿里背书·最强中文 | 3秒克隆·自然语言描述 | 2秒克隆·最快 |

---

## 适用场景

### ✅ 适合的场景
- **需要同时 ASR+TTS 的产品**：如对话机器人、语音交互系统
- **低显存环境**：0.4B 参数极轻量，2-3GB 显存可运行
- **研究用途**：统一架构创新，适合学术研究
- **MIT 商用**：完全免费商用，无版权风险

### ❌ 不适合的场景
- **实时语音应用**：Flow-Matching 扩散过程较慢
- **高保真中文配音**：以英文为主，中文待验证
- **精确声音克隆**：克隆质量可能不如 CosyVoice/Qwen3-TTS

---

## OpenClaw 集成思路

```python
# OpenClaw TTS 集成示例（伪代码）
import subprocess

def generate_speech_univoice(text: str, ref_audio: str) -> str:
    """通过 UniVoice 生成克隆语音"""
    cmd = f"""
    python -c "
    from univoice import UniVoiceTTS
    model = UniVoiceTTS.from_pretrained('guanwenhao/univoice-tts')
    audio = model.generate(text=\\"{text}\\", ref_audio=\\"{ref_audio}\\")
    audio.save('/tmp/univoice_output.wav')
    "
    """
    subprocess.run(cmd, shell=True)
    return "/tmp/univoice_output.wav"

# 调用
audio_path = generate_speech_univoice(
    text="你好，欢迎使用 UniVoice！",
    ref_audio="reference.wav"
)
```

---

## 常见问题

| 问题 | 解答 |
|------|------|
| Q: UniVoice 和传统 TTS 有什么本质区别？ | A: 传统 TTS 只做"说"，UniVoice 同时会"听"——ASR+TTS 统一架构让两个任务互相增强 |
| Q: 0.4B 参数够用吗？ | A: 作为 TTS 够用，但文本理解能力弱于大模型，可能影响复杂句子的韵律 |
| Q: 支持中文克隆吗？ | A: 模型具备多语言能力，但开源版本主要验证了英文，中文效果待实测 |
| Q: 推理速度如何？ | A: Flow-Matching 扩散过程较慢，不适合实时场景，适合离线内容生成 |

---

## 总结评分

| 维度 | 评分 | 说明 |
|------|------|------|
| **语音质量** | ⭐⭐⭐ | 高质量但略低于 CosyVoice/IndexTTS |
| **中文支持** | ⭐⭐ | 主要英文，中文待验证 |
| **克隆能力** | ⭐⭐⭐ | 零样本克隆支持，但非最优 |
| **推理速度** | ⭐⭐ | Flow-Matching 非实时 |
| **轻量化** | ⭐⭐⭐⭐⭐ | 0.4B 参数全场最轻，2-3GB 显存 |
| **License** | ⭐⭐⭐⭐⭐ | MIT，完全免费商用 |
| **综合推荐** | ⭐⭐⭐ | **学术价值高，适合有 ASR+TTS 双需求的研究者** |

---

> **一句话总结**：UniVoice 是极具创新性的 ASR+TTS 统一架构模型（MIT，0.4B 参数极轻量），在学术上意义重大，适合需要"听+说"双能力的产品；对于追求克隆质量或推理速度的生产环境，仍推荐 CosyVoice 3.0 或 Qwen3-TTS。
