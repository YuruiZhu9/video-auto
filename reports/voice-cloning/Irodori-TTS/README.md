# Irodori-TTS — 日语 Flow Matching 语音合成

> 🤖 本次Agent执行新增 | 日语 TTS 新方案

---

## 基本信息

| 项目 | 详情 |
|------|------|
| **发布者** | Aratako（独立开发者） |
| **GitHub** | https://github.com/Aratako/Irodori-TTS |
| **HuggingFace** | https://huggingface.co/aratako/Irodori-TTS-500M |
| **参数量** | 500M |
| **架构** | Rectified Flow Diffusion Transformer（RF-DiT）+ DACVAE 连续潜码 |
| **专注语言** | 日语（日本語） |
| **许可证** | 开源（详见 HuggingFace） |

---

## 核心技术特点

### 1. 基于 Echo-TTS 架构
- 架构与训练设计大量参考 **Echo-TTS**
- 使用 **DACVAE**（Differential Audio Coder with Variational Autoencoder）连续潜码表征
- 区别于离散 Tokenizer（如 SoundStorm/RQVAE），保留更完整的声学信息

### 2. Rectified Flow Diffusion（整流流扩散）
- 采用 **RF-DiT**（Rectified Flow Diffusion Transformer）生成模型
- 相比传统 Diffusion：推理更快（更少步数即可收敛）
- 相比 AR（自回归）模型：支持并行生成，无误差累积问题

### 3. 日语原生优化
- 专门针对日语（日本語）训练和优化
- 支持日语假名（ひらがな・カタカナ）、汉字、罗马字混合输入
- 日语特有的音素处理（拨音/浊音/长音精确建模）

---

## 性能参数

| 指标 | 数值 | 说明 |
|------|------|------|
| 参数量 | 500M | 中等规模，兼顾质量与速度 |
| 采样率 | 24kHz | 高保真输出 |
| 日语覆盖 | ✅ 完全支持 | 假名/汉字/罗马字均可 |
| 零样本克隆 | ✅ 支持 | 5-30秒参考音频 |
| 实时因子（RTF） | 待测试 | 需硬件实测 |

---

## 安装与使用

### GitHub 安装
```bash
git clone https://github.com/Aratako/Irodori-TTS.git
cd Irodori-TTS
pip install -e .
```

### HuggingFace 下载
```python
from huggingface_hub import snapshot_download

# 下载模型权重
model_dir = snapshot_download(repo_id="aratako/Irodori-TTS-500M")
```

### 推理示例
```python
from IrodoriTTS import IrodoriTTS

model = IrodoriTTS(model_dir="path/to/model")

# 日语文本输入（假名）
japanese_text = "こんにちは、音声合成の世界へようこそ"
audio = model.generate(text=japanese_text)
model.save(audio, "output.wav")

# 日语汉字+假名混合
mixed_text = "今日は天気が良いですね"
audio = model.generate(text=mixed_text)
model.save(audio, "output2.wav")

# 声音克隆（参考音频）
audio = model.generate(
    text=" 새로운 목소리로合成してみましょう",  # 日语
    ref_audio="japanese_speaker.wav"  # 5-30秒参考音频
)
```

---

## 适用场景

| 场景 | 推荐度 | 说明 |
|------|--------|------|
| 日语内容创作 | 🥇 首选 | 日语原生优化，专业级输出 |
| 日语动画/游戏配音 | ⭐⭐⭐⭐ | 情感表达可根据参考音频迁移 |
| 日语有声书 | ⭐⭐⭐⭐ | 零样本克隆，无需大量训练数据 |
| 日语语音助手 | ⭐⭐⭐⭐ | 快速推理，低延迟 |
| 中文克隆 | ❌ 不适用 | 不支持中文 |
| 阿拉伯语克隆 | ❌ 不适用 | 不支持阿拉伯语 |

---

## 与其他日语 TTS 对比

| 模型 | 日语支持 | 参数量 | 克隆 | RTF | 许可证 |
|------|---------|--------|------|------|--------|
| **Irodori-TTS** | ✅ 原生日语 | 500M | ✅ | 待测 | 开源 |
| CosyVoice 3.0 | ✅ 日语+中文 | 500M | ✅ | ~0.15 | Apache 2.0 |
| ChatTTS | ✅ 日语（有限） | 200M | ❌ | ~0.1 | Apache 2.0 |
| F5-TTS | ✅ 日语（部分） | 350M | ✅ | ~0.15 | Apache 2.0 |

**推荐**：日语内容创作推荐 **CosyVoice 3.0**（多语言支持更强）；若追求日语气质纯正且有定制需求，可尝试 **Irodori-TTS**。

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 模型无法下载 | 使用 `huggingface-cli download` 或镜像站 |
| 日语发音不自然 | 检查输入文本编码，确保使用 Unicode |
| 克隆不像 | 参考音频质量要好，建议 10-30 秒无混响清晰人声 |
| 中文无法合成 | 该模型仅支持日语，不支持中文 |

---

## 总结

**Irodori-TTS** 是一款专注于日语的 500M 参数 Flow Matching TTS 模型，基于 Echo-TTS 架构改进，使用 DACVAE 连续潜码。它为日语内容创作者提供了新的开源选择。

**场景一句话推荐**：
> 日语内容创作且需要本地化定制？选 Irodori-TTS 500M（基于 Echo-TTS，DACVAE 潜码，日语原生优化）。

---

*本报告由免费语音克隆方案Agent自动生成（2026-04-01）*
