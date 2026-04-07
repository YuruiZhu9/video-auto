# Silma TTS v1 — 双语阿拉伯语/英语轻量语音克隆

> 🤖 本次Agent执行新增 | 发布于 2026-03-13

---

## 基本信息

| 项目 | 详情 |
|------|------|
| **发布团队** | SILMA AI（沙特阿拉伯AI公司） |
| **发布时间** | 2026-03-13（初始提交），2026-03-15（最新更新） |
| **参数量** | 150M |
| **架构** | F5-TTS 扩散架构（Rectified Flow Diffusion） |
| **GitHub** | https://github.com/SILMA-AI/silma-tts |
| **HuggingFace** | https://huggingface.co/silma-ai/silma-tts |
| **许可证** | 代码：MIT License · 模型权重：Apache-2.0 License |
| **Demo** | https://huggingface.co/spaces/silma-ai/silma-tts-v1-demo |

---

## 核心技术特点

### 1. 双语原生支持（阿拉伯语 + 英语）
- **阿拉伯语（阿拉伯语）**：原生级别流利度（Fusha/MSA，现代标准阿拉伯语）
- **英语**：原生级别流利度
- **双语混读**：同一句文本中无缝切换两种语言
- **Tashkeel（阿拉伯语变音符号）**：完整支持 Arabic diacritics（تَشْكِيل），精确控制发音

### 2. 极轻量 + 极速推理
- 仅 **150M 参数**（全场最轻量级 TTS 之一）
- RTF（实时因子）≈ **0.12**（RTX 4090），即 1 秒音频仅需 0.12 秒生成
- 支持低资源环境部署（消费级 GPU 即可）

### 3. 即时声音克隆
- 支持通过参考音频克隆任意音色
- 与 F5-TTS v1.1.7 完全兼容，继承 F5-TTS 的零样本克隆能力

### 4. 高级文本处理
- **NeMo Text Processing**（NVIDIA）用于文本规范化（Text Normalization）
- **CATT**（abjadai/catt）用于为阿拉伯语文本添加 Tashkeel 变音符号
- 处理阿拉伯语特殊字符（如 Hamza、Tanween 等）无压力

---

## 性能对比

| 指标 | Silma TTS | F5-TTS（原始） | 说明 |
|------|-----------|--------------|------|
| 参数量 | 150M | ~350M | 轻量 50%+ |
| RTF（RTX 4090） | ~0.12 | ~0.15 | 更快 |
| 阿拉伯语支持 | ✅ 原生级 | ❌ 弱 | 显著优势 |
| 英语支持 | ✅ 原生级 | ✅ | 相当 |
| 双语混读 | ✅ | ❌ | 显著优势 |
| Tashkeel 支持 | ✅ | ❌ | 显著优势 |
| 即时克隆 | ✅ | ✅ | 相当 |
| 许可证 | Apache 2.0 | Apache 2.0 | 均为商用友好 |

---

## 安装与使用

### pip 一键安装
```bash
pip install silma-tts
# 需要 ffmpeg：apt install ffmpeg 或 brew install ffmpeg
```

### 从源码安装
```bash
git clone https://github.com/SILMA-AI/silma-tts.git
cd silma-tts
pip install -e .
```

### Gradio 演示界面
```bash
silma-tts-app
# 自动启动 Web 界面
```

### Python API 推理
```python
from silma_tts import SilmaTTS

model = SilmaTTS()

# 阿拉伯语文本（带 Tashkeel）
arabic_text = "اَلسَّلَامُ عَلَيْكُمْ وَرَحْمَةُ اللهِ وَبَرَكَاتُهُ"
audio = model.generate(text=arabic_text, ref_audio=None)

# 英语文本
english_text = "Hello, welcome to the voice cloning demonstration."
audio = model.generate(text=english_text, ref_audio=None)

# 克隆声音（参考音频）
audio = model.generate(
    text="今天天气真好！",
    ref_audio="reference_voice.wav"
)

model.save(audio, "output.wav")
```

### 声音克隆
```python
from silma_tts import SilmaTTS

tts = SilmaTTS()

# 使用参考音频克隆声音
audio = tts.generate(
    text="مرحبا بالعالم",  # 阿拉伯语
    ref_audio="speaker_reference.wav"  # 参考音频，5-30秒
)
tts.save(audio, "cloned_arabic.wav")

audio = tts.generate(
    text="Welcome to the future of speech synthesis",
    ref_audio="speaker_reference.wav"
)
tts.save(audio, "cloned_english.wav")
```

---

## 适用场景

| 场景 | 推荐度 | 说明 |
|------|--------|------|
| 阿拉伯语内容创作 | 🥇 首选 | 原生级阿拉伯语支持，无竞品 |
| 阿英双语内容 | 🥇 首选 | 唯一支持阿英无缝混读的开源模型 |
| 快速原型开发 | 🥇 首选 | 150M + RTF 0.12，最轻量选择之一 |
| 低资源环境 | 🥇 首选 | 消费级 GPU 即可，无需服务器级算力 |
| 阿拉伯语语音助手 | 🥇 首选 | Tashkeel + 变音符号，精确发音控制 |
| 通用英语 TTS | ⭐⭐⭐⭐ | 可用，但不是最佳（CosyVoice3/Qwen3-TTS 更好） |
| 中文克隆 | ❌ 不推荐 | 不支持中文 |

---

## 与 F5-TTS 的关系

Silma TTS 基于 F5-TTS 架构，**不是独立创新**，但做了关键改进：

```
F5-TTS（原始）
├─ 通用 TTS（中英）
├─ 350M 参数
└─ 阿拉伯语支持弱

Silma TTS v1（定制优化版）
├─ 专注阿拉伯语 + 英语双语
├─ 150M 参数（精简 57%）
├─ 阿拉伯语 Tashkeel 完整支持
├─ NeMo 文本规范化
└─ 商用友好许可证
```

**优势**：相比直接用 F5-TTS，Silma TTS 对阿拉伯语场景有专门优化，更轻更快。

**劣势**：只能做阿拉伯语/英语，不能做中文等其他语言。

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 阿拉伯语发音不准 | 使用 Tashkeel（带变音符号的阿拉伯文）输入 |
| 安装失败 | 确保已安装 ffmpeg：`apt install ffmpeg` |
| 克隆声音不像 | 减少参考音频背景噪音，使用 10-30 秒清晰人声 |
| 生成速度慢 | RTX 4090 可达 RTF 0.12；CPU 较慢（不推荐） |
| 中文无法合成 | 该模型仅支持阿拉伯语和英语，不支持中文 |

---

## 总结

**🥇 适用推荐**：所有需要阿拉伯语 TTS + 克隆的场景——这是目前**唯一**的高质量开源阿拉伯语 TTS 模型（基于 F5-TTS 但专门优化）。

**场景一句话推荐**：
> 需要阿拉伯语语音合成或阿英双语内容？选 Silma TTS v1（150M，RTF 0.12，Apache 2.0）。

---

*本报告由免费语音克隆方案Agent自动生成（2026-04-01）*
