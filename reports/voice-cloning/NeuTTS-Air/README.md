# NeuTTS Air — 全球首个端侧即时语音克隆 TTS

> 🤖 免费语音克隆方案Agent | 新增于 2026-03-27

---

## 基本信息

| 项目 | 信息 |
|------|------|
| **GitHub** | https://github.com/neuphonic/neutts-air |
| **HuggingFace** | https://huggingface.co/neuphonic |
| **Stars** | ⭐ **5.1k**（GitHub） |
| **最新版本** | Pre-release（2025-10 开源） |
| **参数规模** | **0.5B（~360M 活跃参数）** |
| **许可证** | ✅ **Apache 2.0（NeuTTS-Air）** |
| **中文支持** | ❌ 仅英文 |
| **声音克隆** | ✅ 支持（**3-15秒**参考音频） |

---

## 核心亮点

- 🏆 **全球首个端侧即时语音克隆模型**：无需云端，手机/电脑/树莓派均可运行
- ⚡ **实时推理**：中端设备即可实时合成
- 🔒 **隐私优先**：所有处理在本地完成，数据不离开设备
- 🎙️ **极速克隆**：仅需 **3-15秒** 参考音频即可克隆任意音色
- 💾 **极致轻量**：仅需 **2GB RAM**，Qwen 0.5B 大语言模型骨干
- 🛡️ **内置水印**：所有输出音频嵌入 Perth 感知水印，可追溯来源

---

## 技术规格

| 参数 | 值 |
|------|-----|
| **基座模型** | Qwen 0.5B LLM |
| **音频编解码器** | NeuCodec（50Hz 神经音频编解码，单码本） |
| **活跃参数量** | ~360M（含emb ~552M） |
| **上下文窗口** | 2048 tokens（~30秒音频含prompt） |
| **推理格式** | GGML / GGUF（设备端优化） |
| **参考音频** | 3-15秒，单声道，16-44kHz WAV |
| **许可证** | Apache 2.0（NeuTTS-Air） |
| **水印** | Perth（Perceptual Threshold）感知水印 |

### 推理速度基准

| 设备 | 推理速度 |
|------|---------|
| Galaxy A25 5G（手机） | 20-45 tokens/s |
| AMD Ryzen 9 HX 370 | 119-221 tokens/s |
| iMac M4 16GB | 111-195 tokens/s |
| **RTX 4090** | **16,194-19,268 tokens/s** |

---

## 工作原理

```
1. 参考音频处理 → 分析 3-15秒 参考音频，提取音色特征
2. 文本理解 → 通过 Qwen 0.5B 语言模型处理输入文本
3. 语音合成 → 使用 NeuCodec 50Hz 神经编解码器生成语音码
4. 音频输出 → 实时生成带 Perth 水印的最终音频
```

---

## 安装

### 方式一：Python pip（一键安装）

```bash
pip install neuTTS
```

### 方式二：从源码构建

```bash
git clone https://github.com/neuphonic/neutts-air.git
cd neutts-air
pip install -e .
```

### 方式三：HuggingFace Spaces 在线体验

```
https://huggingface.co/spaces/neuphonic/neutts-air
```

---

## 推理示例

### Python API（基础用法）

```python
from neuTTS import NeuTTS

# 初始化模型（自动下载）
model = NeuTTS()

# 语音合成
audio = model.tts(
    text="Hello, this is a test of NeuTTS Air voice cloning.",
    ref_audio="my_voice.wav",  # 3-15秒参考音频
    ref_text="This is my voice." # 参考音频对应文本（可选）
)

# 保存音频
audio.save("output.wav")
```

### 命令行推理

```bash
# 基本用法
neuTTS "Hello, how are you today?" -r ref_voice.wav -o output.wav

# 指定语言
neuTTS "Hola, como estas?" -r ref_voice.wav -o output.wav -l es

# 批量处理
neuTTS --batch input_texts.txt -r ref_voice.wav -o output_dir/
```

### GGUF 量化版本（设备端最优）

```bash
# 下载 Q8 GGUF 版本（体积更小，速度更快）
# 从 GitHub Release 页面下载对应平台的量化模型

# 本地加载 GGUF 模型
from neuTTS import NeuTTSGGUF

model = NeuTTSGGUF(
    model_path="./neuTTS-Air-Q8.gguf",
    tokenizer_path="./tokenizer.json"
)

audio = model.tts(
    text="Running on device with GGUF quantization!",
    ref_audio="ref.wav"
)
audio.save("output.wav")
```

---

## 适用场景

| 场景 | 说明 |
|------|------|
| **无障碍工具** | 为视障用户用家人声音朗读（完全本地，保护隐私） |
| **内容创作** | 视频配音、多角色语音生成（本地运行，无需网络） |
| **嵌入式设备** | 智能家居、有声玩具（树莓派即可运行） |
| **隐私敏感场景** | 医疗、金融语音交互（数据不出本地设备） |
| **个人语音助手** | 用自己声音作为 AI 助手音色 |

---

## 与其他方案对比

| 特性 | NeuTTS Air | Kokoro-82M | Pocket TTS | ChatTTS |
|------|-----------|------------|------------|---------|
| **克隆方式** | 即时克隆（3秒） | 预设音色 | 任意音频 | 无需克隆 |
| **参数量** | 0.5B | 82M | 100M | 未公开 |
| **设备要求** | 2GB RAM | ~0.5GB | CPU 可用 | GPU 优选 |
| **语言** | 仅英文 | 中文+英文 | 仅英文 | 中英 |
| **许可证** | Apache 2.0 | Apache 2.0 | MIT | 开源 |
| **设备端运行** | ✅ 完全支持 | ✅ ONNX优化 | ✅ | ❌ |
| **水印** | Perth 水印 | 无 | 无 | 无 |

---

## 优势与局限

### ✅ 优势
- **真正端侧**：唯一支持完全离线运行的即时语音克隆模型
- **极速克隆**：3秒参考音频即可，无需微调训练
- **Apache 2.0**：NeuTTS-Air 完全开源免费商用
- **极低门槛**：2GB RAM 即可实时运行，普通手机/电脑无压力

### ❌ 局限
- **仅英文**：当前版本不支持中文（社区多语言支持开发中）
- **水印限制**：所有输出带 Perth 水印，不适合完全无痕场景
- **克隆精度**：相比深度微调方案（如 GPT-SoVITS），音色相似度略低
- **实时交互**：最长 ~30秒单次生成，长文本需分段

---

## 资源链接

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/neuphonic/neutts-air |
| HuggingFace | https://huggingface.co/neuphonic |
| 在线演示 | https://huggingface.co/spaces/neuphonic/neutts-air |
| 官网 | https://neuphonic.com |

---

*本报告由免费语音克隆方案Agent自动生成，基于 2026-03 最新信息。*
