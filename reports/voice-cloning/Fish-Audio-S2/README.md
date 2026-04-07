# Fish Audio S2 / S2 Pro — 最具表现力的开源 TTS

> 🤖 免费语音克隆方案Agent | 新增于 2026-03-26

---

## 基本信息

| 项目 | 信息 |
|------|------|
| **GitHub** | https://github.com/fishaudio/fish-speech |
| **HuggingFace** | https://huggingface.co/fishaudio/s2-pro |
| **Stars** | ⭐ **24.4k**（GitHub） |
| **最新版本** | **S2 Pro（2026-03-09）** |
| **参数规模** | **5B（Dual-AR：4B Slow AR + 400M Fast AR）** |
| **许可证** | ⚠️ **研究/非商用免费；商业使用需单独授权** |
| **中文支持** | ✅ Tier 1（最优支持） |
| **声音克隆** | ✅ 支持（10-30秒参考音频） |

---

## 核心亮点

- 🏆 **2026年3月发布，表现力最强开源 TTS**
- ⚡ **超低延迟**：Time-to-first-audio ~100ms（H200 单卡）
- 🌐 **80+ 语言**：Tier 1 中文/英文/日语最优
- 🎛️ **精细控制**：15,000+ 标签，粒度达单词级别
- 🎭 **情感表达**：`[laughing]` `[angry]` `[whisper]` `[singing]` 等自由文本标签
- 📖 **长文本生成**：支持流式推理，RTF（实时因子）0.195

---

## 技术架构：Dual-AR（双自回归）

S2 Pro 采用创新的 **Dual-Autoregressive** 架构：

```
输入文本 → Slow AR (4B) → 主要语义码 → Fast AR (400M) → 9个残差码 → 音频重建
                ↑                                    ↑
           沿时间轴预测                         同步预测细节
```

- **Slow AR**：沿时间轴运行，预测主要语义码（本征）
- **Fast AR**：每步同步生成9个残差码，重建细节（高速）
- 类似 LLM 的架构使 SGLang 等推理优化可直接复用

---

## 精细控制标签（Inline Control）

S2 Pro 的核心优势：在文本中嵌入自然语言标签，即时控制输出语音。

### 支持标签（部分）

| 标签类型 | 示例 |
|----------|------|
| 情感 | `[excited]` `[sad]` `[angry]` `[surprised]` |
| 音量 | `[volume up]` `[volume down]` `[loud]` `[low volume]` |
| 音调 | `[pitch up]` `[whisper]` `[screaming]` |
| 特殊效果 | `[echo]` `[singing]` `[laughing tone]` |
| 停顿 | `[pause]` `[short pause]` |
| 非言语 | `[inhale]` `[exhale]` `[clearing throat]` `[audience laughter]` |
| 口音 | `[with strong accent]` |

### 使用示例

```python
# 生成带情感标签的语音
text = "你好！[excited] 今天真是个好日子！[laughing] 我们出发吧！"
# S2 Pro 会自动理解并合成对应情感

# 耳语场景
text = "[whisper] 我有一个秘密要告诉你..."

# 自然停顿
text = "首先，[pause] 我们需要准备数据，[pause] 然后开始训练。"
```

---

## 声音样本准备要求

| 项目 | 要求 |
|------|------|
| 音频格式 | WAV / MP3 / FLAC |
| 推荐时长 | 零样本克隆：10-30秒 |
| 采样率 | 16kHz - 48kHz |
| 环境要求 | 安静、无回声、无背景音乐 |
| 内容 | 建议有对应文本，支持自动识别 |

### 录制建议
1. 在安静房间录制，手机或专业麦克风均可
2. 朗读清晰，语速适中，覆盖不同情感
3. 避免口水音、喷麦
4. 多段音频可拼接使用

---

## 安装与使用

### 安装
```bash
git clone https://github.com/fishaudio/fish-speech
cd fish-speech
pip install -r requirements.txt
```

### 使用 SGLang 推理（S2 Pro 推荐）
```python
from sglang import sglang_launcher

# 启动 SGLang 服务
launcher = sglang_launcher("fishaudio/s2-pro")
launcher.start()

# 发送请求
response = launcher.generate(
    text="[excited] 欢迎使用 Fish Audio S2 Pro！",
    max_tokens=1024,
    temperature=0.8,
)
audio = response["audio"]
```

### 零样本克隆推理
```python
from fish_speech.models import FishAudioS2

model = FishAudioS2.from_pretrained("fishaudio/s2-pro")

# 带音色克隆
wav = model.generate(
    text="今天天气真好，我们去公园散步吧。",
    ref_audio="my_voice.wav",      # 参考音频（10-30秒）
    ref_text="这是参考音频对应的文本"  # 可选
)
```

### WebUI 体验
```bash
# 访问 https://fish.audio/ 直接体验（每日免费次数）
```

---

## 与其他方案对比

| 维度 | Fish S2 Pro | Qwen3-TTS | CosyVoice2 | ChatTTS v2 |
|------|-------------|-----------|-----------|-----------|
| 发布时间 | 2026-03 | 2026-01 | 2024-08 | 2025-03 |
| 参数量 | 5B | 1.7B | 0.5B | 未公开 |
| 克隆样本 | 10-30秒 | 3秒 | 3秒 | 无需（生成式） |
| 情感控制 | 标签精细控制 | 自然语言描述 | 指令控制 | 种子控制 |
| 延迟 | ~100ms | 毫秒级 | 毫秒级 | 毫秒级 |
| 语言数量 | 80+ | 10+ | 20+ | 中英双语 |
| **商业授权** | **需单独授权** ⚠️ | Apache 2.0 ✅ | Apache 2.0 ✅ | Apache 2.0 ✅ |
| 中文质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## ⚠️ 重要：商业授权说明

Fish S2 Pro 采用 **Fish Audio Research License**：

| 使用场景 | 是否免费 |
|----------|----------|
| 研究用途 | ✅ 免费 |
| 非商业项目 | ✅ 免费 |
| 商业产品/服务 | ❌ **需要单独授权** |
| 联系邮箱 | business@fish.audio |

> 💡 如果你计划用于商业项目，请先联系 Fish Audio 获取商业授权。
> 对于个人项目或研究，Fish S2 Pro 是目前表现力最强的开源选择。

---

## 适用场景

✅ **适合的场景：**
- 有声书（精细情感控制）
- 虚拟主播（丰富的情感/动作标签）
- 研究/非商业项目（表现力最强）
- 多语言配音（80+语言）

❌ **不太适合的场景：**
- 商业产品（需要授权，可能有成本）
- 追求完全免费（存在许可证限制）
- 边缘设备部署（5B模型较大）

---

## 资源链接

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/fishaudio/fish-speech |
| S2 Pro 模型卡 | https://huggingface.co/fishaudio/s2-pro |
| 技术报告 | https://arxiv.org/abs/2603.08243 |
| 在线体验 | https://fish.audio/ |
| 技术博客 | https://fish.audio/blog/fish-audio-open-sources-s2/ |

---

*本报告由免费语音克隆方案Agent生成，基于2026年3月最新信息。*
