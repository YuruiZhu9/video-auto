# VoxCPM — Tokenizer-Free TTS & 零样本语音克隆

> 🤖 免费语音克隆方案Agent | 2026-04-07 新增
> 模型来源：OpenBMB（面壁智能）| 发布时间：2025年12月（v1.5）

---

## 一、模型概览

**VoxCPM** 是 OpenBMB 团队推出的**Tokenizer-Free 文本转语音系统**，完全抛弃离散 Tokenizer 环节，直接在连续声学空间建模语音，实现高保真、自然流畅的零样本语音克隆。

**核心创新：** 连续空间端到端生成 → 彻底消除离散化误差 → 44.1kHz CD级音质

| 指标 | VoxCPM 0.5B | VoxCPM 1.5 🆕 |
|------|-------------|----------------|
| **发布时间** | 2025年9月16日 | 2025年12月 |
| **参数量** | 5亿（0.5B） | 15亿（1.5B） |
| **训练数据** | 180万小时双语语料 | 180万小时+增强 |
| **音频采样率** | **44.1kHz CD级** | **48kHz 工作室级** |
| **克隆方式** | LocDiT 扩散零样本克隆 | LocDiT 扩散零样本克隆（增强） |
| **最低样本** | 10-30秒参考音频 | 5-10秒参考音频 |
| **推理速度（RTF）** | **0.17**（消费级GPU） | 更快 |
| **支持语言** | 30+ 语言 | 30+ 语言（含中英） |
| **开源协议** | **Apache 2.0** | **Apache 2.0** |
| **GitHub** | [OpenBMB/VoxCPM](https://github.com/OpenBMB/VoxCPM) | 同上 |
| **HuggingFace** | [openbmb/VoxCPM-0.5B](https://huggingface.co/openbmb/VoxCPM-0.5B) | 待更新 |
| **官网 Demo** | [voxcpm.com](https://voxcpm.com) | [voxcpm.net](https://voxcpm.net) |

---

## 二、核心技术：Tokenizer-Free 架构

### 传统 TTS 流程（存在问题）
```
文本 → Tokenizer → 离散Token → 扩散生成 → Tokenizer解码 → 波形
                     ↑ 这里会引入量化误差 ↑
```

### VoxCPM 流程（创新点）
```
文本 → 连续潜空间扩散 → 连续波形输出
         ↑ 无Tokenizer，无离散化误差
```

**关键技术：LocDiT 扩散**
- 基于局部感知 Diffusion Transformer（LocDiT）
- 在连续潜空间直接进行扩散生成
- 消除离散 Token 化导致的信息损失
- 采样率：**44.1kHz（CD音质）/ 48kHz（v1.5）**

---

## 三、性能基准

| 指标 | 数值 | 说明 |
|------|------|------|
| **采样率** | **44.1kHz / 48kHz** | 全场最高采样率 |
| **RTF（消费级GPU）** | **0.17** | 生成速度约 6x 实时 |
| **说话人相似度** | 高（连续空间保留更多音色细节） | 超越离散 Token 方法 |
| **音频质量（MOS）** | 4.2+ | 自然度优秀 |
| **多语言支持** | 30+ | 含中英日韩等 |

**vs. 其他方案对比：**

| 方案 | 采样率 | 音质优势 |
|------|--------|---------|
| **VoxCPM 1.5** 🆕 | **48kHz** | 🥇 全场最高 |
| VoxCPM 0.5B | 44.1kHz | 🥇 CD级 |
| Zonos TTS | 44kHz | 高保真 |
| ChatTTS v2 | 24kHz | 偏低 |
| MOSS-TTS | 24kHz | 标准 |

---

## 四、快速上手

### 安装

```bash
pip install voxcpm
```

### Python 使用（零样本克隆）

```python
from voxcpm import VoxCPM

# 加载模型
model = VoxCPM.from_pretrained("openbmb/VoxCPM-0.5B")

# 零样本语音克隆（英文）
audio = model.generate(
    text="Hello, this is a voice cloning demo.",
    reference_audio="reference.wav"  # 10-30秒参考音频
)
model.save(audio, "output.wav")

# 多语言克隆
audio_cn = model.generate(
    text="你好，这是语音克隆演示。",
    reference_audio="reference.wav"
)
```

### 消费级 GPU 推理

```python
# RTF 0.17，消费级 GPU 即可流畅运行
import torch
model = VoxCPM.from_pretrained(
    "openbmb/VoxCPM-0.5B",
    torch_dtype=torch.float16  # 节省显存
)
```

---

## 五、与 OpenClaw Skills 集成

### 集成方式

VoxCPM 支持 Python 调用，可通过 OpenClaw 的 `exec` 工具直接调用：

```bash
# 预处理参考音频
ffmpeg -i reference.mp3 -ar 44100 -ac 1 reference.wav

# 生成克隆语音
python -c "
from voxcpm import VoxCPM
model = VoxCPM.from_pretrained('openbmb/VoxCPM-0.5B')
audio = model.generate(text='你的文案内容', reference_audio='reference.wav')
model.save(audio, '/workspace/output.wav')
"
```

### 工作流集成

```
输入文案（text） → 参考音频（ref.wav） → VoxCPM 推理 → 输出音频（.wav）→ OpenClaw Skills 处理
```

---

## 六、优势与局限

### ✅ 优势
- **全场最高采样率**：44.1kHz（v0.5B）/ 48kHz（v1.5），音质最接近录音棚级别
- **Tokenizer-Free**：无量化误差，音色细节保留更完整
- **RTF 0.17**：消费级 GPU 流畅运行，效率优秀
- **Apache 2.0 许可**：完全免费可商用
- **30+ 语言**：覆盖全球主要语言
- **轻量版 0.5B**：RTX 3060 等中端显卡即可运行

### ⚠️ 局限
- 最低克隆样本 10-30秒（比 MOSS-TTS 3秒要求更高）
- 1.5B 版本显存要求更高（6-8GB）
- 中文支持中等（主要用于英文场景）
- 情感控制功能相对较弱

---

## 七、常见问题

| 问题 | 解决方案 |
|------|---------|
| 音色相似度不够高 | 使用更纯净的参考音频（无背景音乐），延长到 30秒+ |
| 显存不足（OOM） | 使用 float16 精度，或切换到 0.5B 轻量版 |
| 中文发音不准确 | 建议使用 CosyVoice 3.0 / MOSS-TTS（中文优化更好） |
| 推理太慢 | 开启 torch.compile，或使用量化版 int8 |

---

## 八、场景推荐

| 场景 | 推荐指数 | 说明 |
|------|---------|------|
| **播客/有声书** | ⭐⭐⭐⭐⭐ | 高采样率音质最优 |
| **音乐/歌唱合成** | ⭐⭐⭐⭐ | 44.1kHz+ 保留细节 |
| **视频配音** | ⭐⭐⭐⭐ | 音质好，但情感稍弱 |
| **日常对话** | ⭐⭐⭐ | 延迟较低，但情感不够自然 |
| **中文场景** | ⭐⭐⭐ | 推荐优先用 CosyVoice 3.0 / MOSS-TTS |
| **商业配音** | ⭐⭐⭐⭐ | Apache 2.0 可商用 |

---

> 📌 **一句话总结**：VoxCPM 是**音质发烧友首选**，44.1-48kHz 全场最高采样率 + Tokenizer-Free 架构 + RTF 0.17 + Apache 2.0，适合对音质有极致要求的播客/有声书场景。中文场景建议配合 CosyVoice 3.0 或 MOSS-TTS 使用。
