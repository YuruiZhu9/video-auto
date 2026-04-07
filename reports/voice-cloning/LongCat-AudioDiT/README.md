# LongCat-AudioDiT — 美团开源波形潜空间扩散TTS

> **发布方：** 美团（Meituan）LongCat 团队
> **发布时间：** 2026年3月（arXiv: 2603.29339）
> **模型地址：** https://github.com/meituan-longcat/LongCat-AudioDiT
> **HuggingFace：** https://huggingface.co/meituan-longcat/LongCat-AudioDiT-3.5B
> **许可证：** MIT License（代码 + 权重）

---

## 一、核心亮点

- **🎯 零样本声音克隆全场最高相似度**：在权威 Seed 基准测试中，LongCat-AudioDiT-3.5B 的说话人相似度（SIM）达 **0.818**（中文），超越字节 Seed-TTS（SOTA）
- **🏗️ 创新架构**：直接在**波形潜空间（Waveform Latent Space）**做扩散生成，无需梅尔频谱等中间表示，避免误差累积
- **📊 双规格可选**：1B 参数（轻量）/ 3.5B 参数（顶配），适配不同硬件条件
- **🔧 自适应投影引导（APG）**：替代传统无分类器引导（CFG），简化训练-推理不匹配问题
- **MIT 全开源**：代码 + 权重均可商用，无专利壁垒

---

## 二、技术架构

### 2.1 核心创新

| 创新点 | 说明 |
|--------|------|
| **Waveform Variational Autoencoder (Wav-VAE)** | 将音频编码为波形潜码，而非传统梅尔频谱 |
| **Diffusion Backbone** | 非自回归扩散式生成，支持并行推理 |
| **Adaptive Projection Guidance (APG)** | 自适应投影引导，替代 CFG，消除训练-推理不匹配 |
| **无需多阶段流水线** | 端到端训练，无需高质量人工标注数据集 |

### 2.2 模型规格

| 规格 | 参数 | 适用场景 |
|------|------|----------|
| LongCat-AudioDiT-1B | 10亿 | 轻量部署，RTX 3090 及以上 |
| LongCat-AudioDiT-3.5B | 35亿 | 最高质量，SOTA 效果，显存要求更高 |

### 2.3 推理精度需求

| 规格 | 精度 | 显存估算 |
|------|------|----------|
| 1B | bf16 | ~8-10GB |
| 3.5B | bf16 | ~20-24GB |
| 3.5B | 量化版（int8/int4） | ~12-14GB |

---

## 三、零样本声音克隆性能

### Seed 基准测试对比

| 模型 | 中文 CER (%) ↓ | 中文 SIM ↑ | 英文 WER (%) ↓ | 英文 SIM ↑ | 中文困难样本 SIM ↑ |
|------|--------------|-----------|--------------|-----------|------------------|
| **LongCat-AudioDiT-3.5B** | **1.09** | **0.818** | **1.50** | **0.786** | **0.797** |
| LongCat-AudioDiT-1B | 1.18 | 0.812 | 1.78 | 0.762 | 0.787 |
| Seed-DiT | 1.18 | 0.809 | 1.73 | 0.790 | — |
| GT（真实录音） | 1.26 | 0.755 | 2.14 | 0.734 | — |

> **解读：** LongCat-AudioDiT-3.5B 在 Speaker Similarity（SIM）指标上全面超越 Seed-DiT，同时 CER/WER 也更低。中英文双榜 SOTA。

---

## 四、支持的语音与语言

| 类别 | 支持情况 |
|------|----------|
| **中文（ZH）** | ✅ 完全支持，SIM 最高 |
| **英文（EN）** | ✅ 完全支持 |
| **中文困难样本（ZH-Hard）** | ✅ 专项优化，SIM 0.797 |
| **多语言** | ❌ 当前版本仅中英文（v1） |
| **跨语言克隆** | ❌ 暂无，参考音频与合成语言需一致 |
| **情感控制** | ✅ 支持语气/风格变化（通过扩散采样参数调节） |

---

## 五、声音样本准备要求

### 5.1 音频规格

| 项目 | 推荐值 |
|------|--------|
| **格式** | WAV（推荐）或 MP3 |
| **采样率** | 24kHz（模型原生） |
| **时长** | 5~30秒（零样本克隆参考音频） |
| **环境** | 安静、无混响、无背景音乐 |
| **内容** | 清晰普通话/英语朗读，避免唱歌/喊叫 |

### 5.2 文本内容建议

- 5~30秒自然语速朗读内容
- 句子完整，避免超长单句
- 避免重复词汇或无意义内容
- 建议 3~10 个不同句子，覆盖不同语调

---

## 六、推理使用指南

### 6.1 环境安装

```bash
# 克隆仓库
git clone https://github.com/meituan-longcat/LongCat-AudioDiT.git
cd LongCat-AudioDiT

# 创建环境（推荐 conda）
conda create -n longcat-tts python=3.10
conda activate longcat-tts

# 安装依赖
pip install torch torchaudio
pip install -r requirements.txt
```

### 6.2 零样本克隆推理

```python
# from huggingface_hub import snapshot_download
# snapshot_download(repo_id="meituan-longcat/LongCat-AudioDiT-3.5B", local_dir="./models/LongCat-AudioDiT-3.5B")

import torch
from models import build_model, audio_utils

# 加载模型（3.5B 版本，高质量）
model = build_model(
    model_name="LongCat-AudioDiT-3.5B",
    device="cuda" if torch.cuda.is_available() else "cpu"
)

# 准备参考音频和文本
ref_audio_path = "your_reference.wav"  # 5~30秒参考音频
text = "这是一段测试文本，用于克隆声音。"  # 待合成文本

# 零样本声音克隆
output_audio = model.clone_and_synthesize(
    ref_audio=ref_audio_path,
    text=text,
    guidance_scale=1.0,  # APG引导强度，可调
    num_inference_steps=10,  # 扩散步数，越高质量越好越慢
)

# 保存输出
audio_utils.save_wav(output_audio, "output.wav")
```

### 6.3 高级参数

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `guidance_scale` | APG 引导强度，越高越接近参考音色 | 0.8~1.2 |
| `num_inference_steps` | 扩散去噪步数，越高质量越慢 | 10~20 |
| `speed` | 语速倍率 | 0.8~1.2 |
| `seed` | 随机种子（可复现） | 整数 |

---

## 七、与 OpenClaw Skills 集成

### 7.1 模型选择决策

```
是否有中英文零样本声音克隆需求？
│
├─ 是 ── 优先质量 ──→ LongCat-AudioDiT-3.5B（SIM全场最高）
│   │                   优先速度 ──→ LongCat-AudioDiT-1B
│   │
│   └─ 有高显存（24GB+） ──→ 3.5B（最佳效果）
│       低显存（10GB） ──→ 1B
│
└─ 否 ── 需多语言 ──→ CosyVoice 3.0 / Qwen3-TTS
    需情感控制 ──→ Higgs Audio V2.5
    需阿拉伯语 ──→ Silma TTS
    需日语 ──→ Irodori-TTS
```

### 7.2 OpenClaw Skill 调用示例

```python
# /workspace/skills/voice-clone-assistant/SKILL.md 中扩展集成

def longcat_voice_clone(text: str, ref_audio_path: str, model_size: str = "1B"):
    """
    LongCat-AudioDiT 零样本声音克隆
    - text: 待合成文本
    - ref_audio_path: 参考音频路径（5~30秒）
    - model_size: "1B"（轻量）或 "3.5B"（顶配）
    """
    import torch
    from models import build_model, audio_utils

    model = build_model(
        model_name=f"LongCat-AudioDiT-{model_size}",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )

    audio = model.clone_and_synthesize(
        ref_audio=ref_audio_path,
        text=text,
        guidance_scale=1.0,
        num_inference_steps=12,
    )

    output_path = "/tmp/longcat_output.wav"
    audio_utils.save_wav(audio, output_path)
    return output_path

# 使用示例
result = longcat_voice_clone(
    text="欢迎使用语音克隆功能，这段音频来自美团 LongCat-AudioDiT。",
    ref_audio_path="/workspace/audio/my_voice.wav",
    model_size="1B"  # RTX 3090 适用
)
```

---

## 八、常见问题与解决

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 音色相似度低 | APG 参数过低 | 提高 `guidance_scale` 至 1.2~1.5 |
| 推理速度慢 | 扩散步数过多 | 减少 `num_inference_steps` 至 6~8 |
| 显存不足（OOM） | 3.5B 模型过大 | 切换至 1B 版本，或使用量化版本 |
| 中文发音错误 | 罕见字词 | 增加参考音频时长或提供音素标注 |
| 音频含噪声 | 参考音频质量差 | 使用 UVR5 降噪预处理参考音频 |

---

## 九、与其他方案对比

| 维度 | LongCat-AudioDiT-3.5B | CosyVoice 3.0 | Qwen3-TTS | Fish Audio S2 Pro |
|------|----------------------|---------------|-----------|------------------|
| **SIM（中文）** | **0.818 ✅全场最高** | ~0.80 | ~0.80 | ~0.79 |
| **SIM（英文）** | **0.786 ✅全场最高** | ~0.78 | ~0.77 | ~0.76 |
| **语言数** | 中英 2种 | 9+18方言 | 10语言 | 80+语言 |
| **零样本克隆** | ✅ | ✅ | ✅ | ✅ |
| **MIT/Apache 商用** | ✅ MIT | ✅ Apache-2.0 | ✅ Apache-2.0 | ❌ 非商用 |
| **中文SIM** | **0.818 SOTA** | 高 | 高 | 中等 |
| **模型规格** | 3.5B | 0.5B | 1.7B | 未公开 |
| **代码开源** | ✅ | ✅ | ✅ | ✅ |
| **特色** | 波形潜空间扩散，SIM全场最高 | 阿里开源，稳定可靠 | 自然语言音色控制 | RLHF情感丰富 |

> **结论：** 如果你的核心需求是**最高声音相似度**且**中英双语**场景，LongCat-AudioDiT-3.5B 是当前最优选择（SOTA）。若需要更多语言、情感控制或极低延迟，应选择其他方案。

---

## 十、适用场景推荐

- ✅ **最高相似度需求**：有声书配音、视频解说，声音真实度优先
- ✅ **中英双语内容**：跨境电商、国际视频配音
- ✅ **语音助手/客服**：高质量音色克隆，提升品牌辨识度
- ✅ **短剧/短视频**：声音逼真度要求高的口播内容
- ❌ **阿拉伯语/日语**：选 Silma TTS / Irodori-TTS
- ❌ **极低延迟（<100ms）**：选 Qwen3-TTS / ChatTTS v2
- ❌ **超长上下文**：选 TADA（700秒）/ CosyVoice 3.0
