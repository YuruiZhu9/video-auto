# OmniVoice — 全语言零样本语音克隆

> ⏰ **新鲜度**：2026-04-12 第13次执行更新（2026-04-01 发布，GitHub Stars 2.5k，**v0.1.3 于 4月7日发布**）

---

## 一句话评价

> **600+语言覆盖，RTF 0.025（比实时快40倍），Apache-2.0开源，Diffusion语言模型架构** —— 史上语言覆盖最广的开源零样本TTS。

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **发布机构** | k2-fsa + Xiaomi |
| **发布时间** | 2026年4月1日 |
| **arXiv** | [2604.00688](https://arxiv.org/abs/2604.00688) |
| **GitHub** | [k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice)（**2.5k⭐，v0.1.3 于 2026-04-07 发布**） |
| **HuggingFace** | [k2-fsa/OmniVoice](https://huggingface.co/k2-fsa/OmniVoice) |
| **在线Demo** | [HuggingFace Space](https://huggingface.co/spaces/k2-fsa/OmniVoice) |
| **许可证** | Apache-2.0 |
| **训练数据** | 581k小时多语言数据（全部开源数据整理） |

---

## 核心技术

### 架构：Diffusion Language Model

OmniVoice 采用**扩散语言模型风格**的离散非自回归（NAR）架构：

1. **直接文本→声学Token映射**：无需传统两阶段管道（text-to-semantic-to-acoustic），直接从文本生成多码本（multi-codebook）声学Token
2. **全码本随机掩码策略（Full-codebook random masking）**：高效训练策略
3. **预训练LLM初始化**：从预训练大语言模型初始化，确保卓越的可理解性（intelligibility）

### 600+语言支持

- 零样本（Zero-shot）TTS：只需3-10秒参考音频即可克隆任意语言/方言声音
- 覆盖中文方言（四川话、陕西话等）、英语口音（美式、英式等）
- 开源数据整理，581k小时训练数据

### 推理速度

| 指标 | 值 |
|------|-----|
| **RTF（实时因子）** | 低至 **0.025** |
| **速度** | 比实时快 **40倍** |
| **加速选项** | `num_step=16`（默认32步）|
| **音频采样率** | 24 kHz |
| **推荐参考音频** | 3-10秒 |

---

## 核心功能

### 1. 语音克隆（Voice Clone）
```python
from omnivoice import OmniVoice
import torch

model = OmniVoice.from_pretrained(
    "k2-fsa/OmniVoice",
    device_map="cuda:0",
    dtype=torch.float16
)

output = model.generate(
    text="你好，欢迎使用OmniVoice语音克隆。",
    ref_audio="path/to/reference.wav",  # 3-10秒参考音频
    ref_text="（可选）参考音频对应的文本，Whisper ASR自动转录"
)
```

### 2. 语音设计（Voice Design）— 无需参考音频
```python
output = model.generate(
    text="你好，欢迎使用OmniVoice语音设计。",
    gender="female",
    age="young",
    pitch="high",
    style="whisper",       # whisper / normal
    english_accent="British",
    chinese_dialect="Sichuan"  # 四川话
)
```

### 3. 自动语音（Auto Voice）
```python
output = model.generate(
    text="模型自动选择声音合成这段文字。"
)
```

---

## 命令行工具

```bash
# 安装
pip install omnivoice
# 或源码安装
pip install git+https://github.com/k2-fsa/OmniVoice.git

# 交互式Web演示（Gradio）
omnivoice-demo --ip 0.0.0.0 --port 8001

# 单样本推理
omnivoice-infer --text "你好" --ref_audio ref.wav --output out.wav

# 批量推理（支持多GPU）
omnivoice-infer-batch --config batch_config.yaml
```

---

## 参数控制

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `num_step` | 扩散步数（16=加速，32=质量） | 32 |
| `speed` | 速度因子（>1更快，<1更慢） | 1.0 |
| `duration` | 固定输出时长（秒） | - |

---

## 非语言符号支持

```
[laughter]      — 笑声
[sigh]         — 叹气
[question-en]  — 英文疑问语气
```

---

## 硬件要求

| 平台 | 配置 |
|------|------|
| NVIDIA GPU | CUDA 12.8，推荐 torch==2.8.0+cu128 |
| Apple Silicon | `device_map="mps"` |
| 内存 | 建议16GB+ |

---

## 与主流模型对比

| 模型 | 语言数 | 克隆方式 | RTF | 许可证 | 亮点 |
|------|--------|---------|-----|--------|------|
| **OmniVoice** ⭐ | **600+** | Zero-shot（3秒音频） | **0.025** | Apache-2.0 | 语言覆盖最广，RTF最快 |
| Qwen3-TTS | 50+ | Zero-shot（15秒音频） | ~0.05 | Apache-2.0 | 中文最强，情感丰富 |
| CosyVoice2 | 50+ | Zero-shot（10秒音频） | ~0.1 | Apache-2.0 | 中文首选，稳定 |
| Voxtral TTS | 多语言 | Zero-shot | 0.09 | 开放权重 | Mistral出品，68%胜率 |
| LongCat-AudioDiT | 中英 | Zero-shot | ~0.05 | MIT | SIM 0.818全场最高 |
| Fish Speech | 中英日韩 | 微调（30分钟） | ~0.15 | Apache-2.0 | 中文友好 |
| GPT-SoVITS | 多语言 | 微调（1分钟） | ~0.2 | Apache-2.0 | 1分钟极少量样本 |

---

## 适用场景

✅ **多语言出海应用**（600+语言，零样本克隆）  
✅ **极速合成需求**（RTF 0.025，实时40倍速）  
✅ **无需训练数据**（3秒参考音频即可）  
✅ **语音设计**（无需参考音频，控制音色属性）  
✅ **方言合成**（四川话、陕西话等中文方言）

---

## 局限性

- ⚠️ 参数量未公开
- ⚠️ 音频采样率24kHz（低于部分竞品的44.1/48kHz）
- ⚠️ 无情绪控制参数（对比ChatTTS的情绪标签）
- ⚠️ 纯扩散架构，生成质量有待大规模用户验证

---

## OpenClaw Skills 集成

### 创建 Skill 文件
```bash
# 在OpenClaw skills目录创建
mkdir -p ~/.openclaw/skills/omnivoice-tts
```

创建 `~/.openclaw/skills/omnivoice-tts/SKILL.md`：
```markdown
# OmniVoice TTS Skill

## 用途
调用 OmniVoice 进行零样本语音克隆和多语言TTS

## 安装
pip install omnivoice torch --extra-index-url https://download.pytorch.org/whl/cu128

## 核心调用
python
from omnivoice import OmniVoice
import torch

model = OmniVoice.from_pretrained(
    "k2-fsa/OmniVoice",
    device_map="cuda:0",
    dtype=torch.float16
)

# 语音克隆
model.generate(text="文本", ref_audio="ref.wav")

# 语音设计
model.generate(text="文本", gender="female", age="young")
```

## 注意事项
- 首次运行自动下载模型（约数GB）
- 推荐CUDA 12.8 + torch 2.8+
- 参考音频推荐3-10秒，语音清晰无混响
```

---

## 参考链接

- GitHub: https://github.com/k2-fsa/OmniVoice
- HuggingFace: https://huggingface.co/k2-fsa/OmniVoice
- 论文: https://arxiv.org/abs/2604.00688
- Demo: https://huggingface.co/spaces/k2-fsa/OmniVoice
