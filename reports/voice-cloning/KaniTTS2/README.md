# KaniTTS-2 — 3GB显存即可运行的语音克隆TTS

> 🤖 免费语音克隆方案Agent | 2026-03-27 新增

---

## 一、模型概览

| 指标 | 数值 |
|------|------|
| **发布时间** | 2026年2月11日 |
| **开发团队** | NineNineSix (nineninesix-ai) |
| **参数量** | **400M**（v1: 350M） |
| **架构** | LFM2（Causal Language Model） |
| **输出采样率** | 22050 Hz |
| **最大生成时长** | ~40秒（3000 tokens） |
| **克隆方式** | Speaker Embedding（WavLM编码器） |
| **最低样本** | **10-20秒**参考音频 |
| **显存需求** | **3GB**（最低门槛之一） |
| **推理速度** | GPU: 2-5秒生成10秒音频 |
| **开源协议** | **Apache 2.0** |
| **GitHub** | [nineninesix-ai/kani-tts-2](https://github.com/nineninesix-ai/kani-tts-2) |
| **HuggingFace** | [nineninesix/kani-tts-2-pt](https://huggingface.co/nineninesix/kani-tts-2-pt) |

---

## 二、核心亮点

### 🧠 基于语言模型的TTS架构
- 告别传统自回归Transformer
- 像GPT一样预测"下一个音频帧"
- Frame-level Position Encoding 解决长文本连贯性

### 🎤 说话人嵌入克隆
- 基于 **WavLM** 的说话人编码器
- 提取128维说话人向量
- 支持任意参考音频（自动重采样至16kHz）

### 🌐 多语言支持
- 英文 (en_US) — nineninesix/kani-tts-2-en
- 法语 (fr_FR)
- 德语 (de_DE)
- 预训练模型：nineninesix/kani-tts-2-pt（支持多语言）

### 🔧 可定制训练
- 提供**从零预训练代码框架**
- 支持SFT + LoRA微调
- 可自定义音色和语言

---

## 三、技术规格

| 参数 | 数值 |
|------|------|
| Speaker Embedding 维度 | 128 |
| Text Vocab Size | 64400 |
| Audio Token Codes | 4通道 × 4032码本 = 16128个音频token |
| Audio Codec | NVIDIA NeMo NanoCodec（0.6kbps, 12.5fps） |
| Learnable RoPE | ✅ 每层频率缩放 |
| Alpha Range | [0.5, 2.0] |

---

## 四、适用场景

| 场景 | 适配度 |
|------|--------|
| 低显存环境（3GB即可） | ⭐⭐⭐⭐⭐ |
| 实时对话系统 | ⭐⭐⭐⭐ |
| 多语言TTS | ⭐⭐⭐⭐ |
| 定制音色训练 | ⭐⭐⭐⭐⭐ |
| 研究/预训练实验 | ⭐⭐⭐⭐⭐ |

---

## 五、安装与使用

### 安装

```bash
pip install kani-tts-2
pip install -U "transformers==4.56.0"
```

### 基础推理

```python
from kani_tts import KaniTTS

model = KaniTTS('nineninesix/kani-tts-2-en')
audio, text = model("Hello, this is a test of the KaniTTS system.")
model.save_audio(audio, "output.wav")
```

### 语音克隆

```python
from kani_tts import KaniTTS, SpeakerEmbedder

# 加载模型和说话人编码器
model = KaniTTS('nineninesix/kani-tts-2-en')
embedder = SpeakerEmbedder()

# 提取说话人向量（10-20秒参考音频）
speaker_embedding = embedder.embed_audio_file("my_voice.wav")

# 生成克隆语音
audio, text = model(
    "This is my cloned voice speaking!",
    speaker_emb=speaker_embedding
)
model.save_audio(audio, "cloned.wav")
```

### 生成参数

```python
audio, text = model(
    "Expressive speech with adjusted parameters.",
    speaker_emb=speaker_embedding,
    temperature=0.8,      # 越低越确定（0.5-1.5）
    top_p=0.95,           # 核采样阈值
    repetition_penalty=1.1,
    max_new_tokens=3000   # 控制生成长度
)
```

---

## 六、与主流方案对比

| 方案 | 参数量 | 显存需求 | 克隆样本 | 开源协议 |
|------|--------|----------|----------|----------|
| **KaniTTS-2** | 400M | **3GB** | 10-20秒 | Apache 2.0 |
| Qwen3-TTS | 1.7B | 4-6GB | 3秒 | Apache 2.0 |
| CosyVoice 3.0 | 500M | 4GB | 3-10秒 | Apache 2.0 |
| ChatTTS v2 | ~200M | 2-4GB | 无需克隆 | MIT |
| LuxTTS | 小 | **1GB** | 3秒 | Apache 2.0 |
| GPT-SoVITS v4 | 330M | 6GB+ | 5-10分钟 | 开源 |

**结论**：KaniTTS-2以3GB显存提供了LLM-based TTS的完整能力，同时提供从零预训练代码，是追求可定制性的开发者的首选。

---

## 七、常见问题

| 问题 | 解决 |
|------|------|
| 显存不足 | KaniTTS-2仅需3GB，但需要bf16精度 |
| 生成时间太长 | 确认使用GPU，CPU推理约20-60秒/10秒音频 |
| 中文支持 | 使用预训练模型`kani-tts-2-pt`，效果有限 |
| 说话人向量提取失败 | 参考音频需≥10秒，模型默认`nineninesix/speaker-emb-tbr` |
| 最大生成长度 | 约40秒（3000 tokens），超长文本需分段 |

---

## 八、开源协议

**Apache 2.0** — 完全开源，可商用，附从零预训练代码。

---

## 九、相关资源

- [GitHub仓库](https://github.com/nineninesix-ai/kani-tts-2)
- [预训练模型](https://huggingface.co/nineninesix/kani-tts-2-pt)
- [英文模型](https://huggingface.co/nineninesix/kani-tts-2-en)
- [预训练框架](https://github.com/nineninesix-kani-tts-2-pretrain)
- [完整指南](https://zimage.run/zh/blog/kani-tts-2-complete-guide)（中文）
