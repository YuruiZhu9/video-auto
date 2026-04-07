---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9eca94ff056f86664115ab83809e5ee7
    PropagateID: 9eca94ff056f86664115ab83809e5ee7
    ReservedCode1: 30450220335386e12d3493888f3e4c0abc9b3bd2d36806e8dbb57ffcb0a57c3a0e68f0a3022100b797d51c530861f9477daed24784d67175af484d9ef9354425a8a4fc9a2ecde7
    ReservedCode2: 3046022100c222abfb07b87179c1d9cfe6c502be6a63a7e6a9442fa568a01ab1bf22839bed022100b35dda4d10b47a9aa2315ed07fa3270040692dc676e8cd373eae652532470a2a
---

# 🤖 TTS 模型库

> 收录主流 Text-to-Speech 开源模型，持续追踪体验与性能
> 最后更新：2026-04-02

---

## 📦 Kokoro TTS 🤍 新收录

**Kokoro-82M** 是由 hexgrad（Hugging Face 团队成员）开源的轻量级 TTS 模型，以 82M 参数在 **TTS Spaces Arena 中排名第一**，击败了参数规模大 5-15 倍的竞品。

**GitHub**: https://github.com/hexgrad/kokoro
**模型地址**: https://huggingface.co/hexgrad/Kokoro-82M
**中文优化版**: https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh

---

### 🎯 核心参数

| 指标 | 数值 |
|------|------|
| 参数量 | **82M** |
| 模型大小 | ~165MB |
| 输出采样率 | 24kHz WAV |
| 许可协议 | **Apache 2.0**（可商用） |
| 架构基础 | StyleTTS 2 |
| 训练数据 | < 100 小时 |
| TTS Arena 排名 | **#1** |

---

### 🌐 支持语言

| 代码 | 语言 | 备注 |
|------|------|------|
| `a` | 美式英语 | 默认 |
| `b` | 英式英语 | |
| `e` | 西班牙语 | |
| `f` | 法语 | |
| `h` | 印地语 | |
| `i` | 意大利语 | |
| `j` | 日语 | 需安装 misaki[ja] |
| `p` | 巴西葡萄牙语 | |
| `z` | 中文普通话 | 需安装 misaki[zh] |

---

### 🎤 中文音色（v1.1-zh 版本 · 8种）

| 音色 ID | 性别 | 风格 | 推荐场景 |
|---------|------|------|---------|
| `zf_xiaobei` | 女 | 温柔甜美 | 有声书、客服 |
| `zf_xiaoni` | 女 | 清亮活泼 | 短视频配音 |
| `zf_xiaoxiao` | 女 | 成熟稳重 | 新闻播报 |
| `zf_xiaoyi` | 女 | 专业正式 | 教程讲解 |
| `zm_yunjian` | 男 | 青春活力 | 游戏角色 |
| `zm_yunxi` | 男 | 温柔细腻 | 有声小说 |
| `zm_yunxia` | 男 | 成熟稳重 | 企业宣传 |
| `zm_yunyang` | 男 | 浑厚有力 | 纪录片旁白 |

> v1.1-zh 还额外包含 100+ 预设音色，中文音色由「龙猫数据」专业标注。

---

### ✅ 用户体验总结

**优势：**
- 🏆 **TTS Arena 第一名**，小模型逆袭大模型
- ⚡ **82M 参数**，CPU 可跑，推理极快（150ms 首包）
- 💰 **Apache 2.0**，完全免费可商用
- 🌏 **8 种语言**，中文支持持续完善（v1.1-zh）
- 🎙️ **多音色切换**，无需额外训练，一个模型打全场
- 📦 **安装极简**：`pip install kokoro soundfile`
- 🍎 **Mac MPS 加速**，Apple Silicon 原生支持
- 🔧 **ONNX/Triton 支持**，可进一步优化推理
- 🔊 **支持语音克隆**：加载自定义 voice.pt 即可复刻音色
- 🇨🇳 中文多音字处理**优于大多数同级别模型**

**短板：**
- ⚠️ **中英混合内容**：英文部分吐字不清，中文 v1.1-zh 已改善但仍有局限
- ⚠️ **数字朗读**：早期版本不支持中文数字，v1.1-zh 已部分修复
- ⚠️ **音频长度**：默认最长 30 秒，长文本需分批处理
- ⚠️ **停顿控制**：无法精细控制生成音频中间停顿
- ⚠️ **量化问题**：WebGPU 量化后可能无法使用
- ⚠️ **下载困难**：HuggingFace 下载需网络支持
- ⚠️ **专业术语**：多音字可能读错，需用拼音标注修正

---

### 📊 与主流 TTS 方案横向对比

| 方案 | 参数量 | 克隆速度 | 中文效果 | 商用许可 | 适合场景 |
|------|--------|---------|---------|---------|---------|
| **Kokoro-82M** 🤍 | 82M | ~3秒 | ⭐⭐⭐⭐ | Apache 2.0 ✅ | 轻量实时、多语言、定制音色 |
| CosyVoice 3（阿里） | 0.5B | 3秒 | ⭐⭐⭐⭐⭐ | 开源免费 | 中文最强、情感控制 |
| XTTS-v2（Coqui） | 467M | 6秒 | ⭐⭐⭐ | MPL 2.0 | 语音克隆 |
| MetaVoice | 1.2B | 即时 | ⭐⭐⭐ | 开源免费 | 英文为主 |

---

### 🛠️ 快速上手

**安装（Python）：**
```bash
pip install "kokoro>=0.9.4" soundfile
apt-get -qq -y install espeak-ng

# 中文支持
pip install "misaki[zh]>=0.8.2"

# 下载中文音色包
wget https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh/resolve/main/samples/make_zh.py
python make_zh.py
```

**生成中文语音（Python）：**
```python
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code='z')  # 中文

generator = pipeline("你好，欢迎使用 Kokoro TTS。", voice='zf_xiaobei', speed=1)

for i, (gs, ps, audio) in enumerate(generator):
    sf.write(f'{i}.wav', audio, 24000)
```

**API 服务化（FastAPI 示例）：**
```python
from fastapi import FastAPI
from kokoro import KPipeline
import soundfile as sf
import io

app = FastAPI()
pipeline = KPipeline(lang_code='z')

@app.post("/tts")
def tts(text: str, voice: str = "zf_xiaobei"):
    audio_out = []
    for _, _, audio in pipeline(text, voice=voice):
        audio_out.extend(audio.tolist())
    buffer = io.BytesIO()
    sf.write(buffer, audio_out, 24000, format="WAV")
    return {"audio": buffer.getvalue()}
```

---

### 🔮 未来可关注方向

- C++ SDK 已完成（Windows 适配）→ Android / OpenHarmony 移植进行中
- Rockchip 芯片 + RKNPU 端侧推理路线
- v1.2+ 版本对中英混合内容的持续改进

---

### 📌 结论与适用建议

**推荐场景：**
- 个人开发者 / 小团队需要快速集成 TTS
- 需要多语言支持（尤其是英/日/法/西）
- 对模型体积敏感，需要 CPU 部署或边缘设备运行
- 中文为主，对音色数量有要求（v1.1-zh 100+ 音色）
- 预算有限，需要完全免费可商用方案

**不推荐场景：**
- 需要高质量中英混合内容播报（选择 CosyVoice 3）
- 对情感控制要求高（选择 CosyVoice 3）
- 需要超长音频一次性生成（需分批）

---

> 🤍 **综合评价**：Kokoro 是目前最值得关注的轻量级 TTS 选手。在 82M 参数的极小体积下实现了与 467M XTTS 正面对抗甚至胜出的质量，加上 Apache 2.0 商用许可，对个人开发者和小型团队来说是性价比最高的选择。中文支持随 v1.1-zh 版本大幅改善，但中英混合场景仍有提升空间，适合中文为主或英文为主的应用。

---

## 📦 其他收录模型

> 待扩展
