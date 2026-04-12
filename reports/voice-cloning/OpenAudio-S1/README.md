# OpenAudio S1 / S1-mini — Fish Speech 全新一代旗舰 TTS

> 🤖 免费语音克隆方案Agent | 2026-03-27 新增 | 2026-04-12 品牌升级确认

---

## ⚠️ 品牌升级确认（2026-04-12 更新）

Fish Speech 已正式更名为 **OpenAudio**，项目架构全面升级：

| 指标 | 数据 |
|------|------|
| 新品牌名 | OpenAudio（原 Fish Speech）|
| GitHub 仓库 | `fishaudio/fish-speech`（仓库名暂未更改）|
| 最新版本 | **V1.5.1**（2025-05-31）|
| 最新提交 | 2025-11-06（修复模型权重加载日志）|
| GitHub Stars | **24.4k** |
| 重大更新 | OpenAudio-S1 新增 **Finetune 支持**（2025-10-19，PR #1115）|
| Docker | 全面重构，支持 **CUDA 12.6.0**（2025-09）|
| 许可证 | 代码 Apache 2.0；模型 CC-BY-NC-SA（免费非商用）|

---

## 基本信息

| 项目 | S1（旗舰版） | S1-mini（蒸馏版） |
|------|------------|------------------|
| **品牌** | OpenAudio（Fish Speech 全新命名） | OpenAudio |
| **GitHub** | https://github.com/fishaudio/fish-speech | 同左 |
| **体验地址** | https://fish.audio/（S1完整版） | https://huggingface.co/spaces/fishaudio/openaudio-s1-mini |
| **技术博客** | https://speech.fish.audio | 同左 |
| **参数规模** | **4B（四十亿参数）** | **0.5B（五亿参数）** |
| **发布时间** | 2025年（v1.5系列） | 2025年 |
| **License** | ⚠️ **代码 Apache 2.0；模型 CC-BY-NC-SA-4.0（非商用免费）** | 同左 |
| **中文支持** | ✅ Tier 1（中文/英文/日语最优） | 同左 |
| **GitHub Stars** | ⭐ **24.4k** | 同左 |

---

## 核心定位

OpenAudio S1/S1-mini 是 Fish Speech 项目的**全新一代核心模型**，基于 **RLHF（从人类反馈中强化学习）**训练，在语音质量指标上达到开源 TTS 的领先水平。与同门师兄 **Fish Audio S2 Pro**（5B Dual-AR 架构）不同，S1 系列更侧重**通用表现力 + 多语言 + 精细情感控制**。

---

## 技术指标（Seed TTS Eval 基准）

| 指标 | S1 | S1-mini | 说明 |
|------|-----|---------|------|
| **WER（词错误率）** | **0.008**（0.8%） | 0.011 | 越低越好 |
| **CER（字符错误率）** | **0.004**（0.4%） | 0.005 | 越低越好 |
| **说话人距离（Speaker Sim）** | **0.332** | 0.380 | 越低越好，音色保真度 |
| **情感一致性** | 高 | 中高 | 参考音频风格保持 |

> S1-mini 在参数量减少 8 倍的情况下，WER/CER 仅轻微退化（0.8%→1.1%），性价比极高。

---

## 核心能力

### ✅ 零样本/Few-shot 克隆
- **输入参考音频**：10-30 秒语音样本
- **克隆音色保真度**：Speaker Sim 0.332（全场领先之一）
- **跨语言克隆**：同一音色可用不同语言表达

### ✅ 精细情感控制（50+ 标签）

**基础情感标签（24个）：**
```
(angry) (sad) (excited) (surprised) (satisfied) (delighted)
(scared) (worried) (upset) (nervous) (frustrated) (depressed)
(empathetic) (embarrassed) (disgusted) (moved) (proud)
(relaxed) (grateful) (confident) (interested) (curious) (confused) (joyful)
```

**高级情感标签（28个）：**
```
(disgustful) (unhappy) (anxious) (hysterical) (indifferent) (impatient)
(guilty) (scornful) (panicked) (furious) (reluctant) (keen)
(disapproving) (negative) (denying) (astonished) (serious) (sarcastic)
(conciliative) (comforting) (sneering) (hesitating) (yielding)
(painful) (awkward) (amused)
```

**语调标记：**
```
(in a hurry tone) (shouting) (screaming) (whispering) (soft tone)
```

**特殊音效：**
```
(laughing) (chuckling) (sobbing) (crying loudly) (sighing)
(panting) (groaning) (crowd laughing) (background laughter) (audience laughing)
```

### ✅ 支持语言
中文 · 英语 · 日语 · 韩语 · 法语 · 德语 · 阿拉伯语 · 西班牙语

**无需担心语言问题**：模型具有强大的泛化能力，可处理任何语言脚本，无需音素依赖。

---

## 技术特点

### RLHF 训练
S1 系列采用**在线 RLHF**（从人类反馈中强化学习）训练，不同于传统的监督学习，让模型直接学习人类对语音质量的偏好，显著提升自然度和情感表达。

### 多标签叠加
支持**多个标签叠加**，实现复合情感：
```
文本: "太好了！" + 标签: "(excited) (laughing)"
文本: "我很抱歉..." + 标签: "(sad) (empathetic)"
```

### 长文本流式推理
- 支持流式输出（streaming）
- 长文本分句处理，避免内存爆炸
- RTX 4090 上 RTF（实时因子）约 **1:7**（S1）

---

## 硬件要求

| 项目 | S1（4B） | S1-mini（0.5B） |
|------|---------|--------------|
| **GPU 显存** | ~8-10GB（fp16） | ~1-2GB |
| **推荐** | NVIDIA H200/A100 | RTX 3090/4090 或更少 |
| **CPU 运行** | ❌ 不推荐 | ⚠️ 可行但慢 |
| **量化支持** | INT8/INT4 | INT8 足够 |

---

## 快速开始

### 安装

```bash
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech
pip install -r requirements.txt

# 下载模型（自动）
python -c "from fish_audio import FishAudio; FishAudio.download('s1')"
```

### WebUI 推理

```bash
python -m fish_audio.webui \
    --model-name "s1" \
    --share \
    --listen 0.0.0.0
```

### Python API

```python
from fish_audio import FishAudio

# 加载模型
model = FishAudio.from_pretrained("fishaudio/s1")

# 克隆 + 情感控制生成
audio = model.generate(
    text="你好，今天天气真不错！",
    ref_audio="my_voice.wav",  # 10-30秒参考音频
    instructions="(happy) (excited)",  # 情感标签
)

audio.save("output.wav")
```

### 进阶：多标签叠加

```python
# 愤怒+惊讶的场景
audio = model.generate(
    text="你说什么？！这不可能！",
    ref_audio="ref.wav",
    instructions="(angry) (surprised)",
)

# 温柔的低语
audio = model.generate(
    text="嘘...小声点",
    ref_audio="ref.wav",
    instructions="(soft tone) (whispering)",
)
```

---

## Fish Speech 家族对比

| 模型 | 参数量 | 架构 | 克隆 | 情感控制 | 中文 | License | 推荐场景 |
|------|--------|------|------|----------|------|---------|----------|
| **S1** | 4B | RLHF AR | 零样本 | 50+标签 | Tier 1 | CC-NC-SA | 高质量通用TTS |
| **S1-mini** | 0.5B | RLHF AR | 零样本 | 50+标签 | Tier 1 | CC-NC-SA | 轻量部署 |
| **Fish Audio S2 Pro** | 5B | Dual-AR | 零样本 | 15,000+标签 | Tier 1 | ⚠️需授权 | 极致表现力 |
| **Fish Speech v1.5** | 1B | VQ-VAE | 零样本 | 少量标签 | ✅ | Apache 2.0 | 旧版本 |

---

## OpenClaw 集成思路

```python
# OpenClaw + OpenAudio S1 集成（伪代码）
import subprocess
import os

def generate_speech_openaudio(
    text: str,
    ref_audio: str,
    instructions: str = "",
    output_path: str = "/tmp/openaudio_output.wav"
) -> str:
    """通过 OpenAudio S1 生成克隆+情感控制语音"""
    cmd = f"""
    python -c "
    from fish_audio import FishAudio
    model = FishAudio.from_pretrained('fishaudio/s1')
    audio = model.generate(
        text=\\"{text}\\",
        ref_audio=\\"{ref_audio}\\",
        instructions=\\"{instructions}\\"
    )
    audio.save(\\"{output_path}\\")
    "
    """
    subprocess.run(cmd, shell=True, check=True)
    return output_path

# 示例：生成开心兴奋的克隆语音
result = generate_speech_openaudio(
    text="太棒了！我们成功了！",
    ref_audio="my_voice.wav",
    instructions="(excited) (delighted)"
)
print(f"音频已生成: {result}")
```

---

## ⚠️ 重要注意事项：License 限制

| 组件 | License | 商用 |
|------|---------|------|
| **代码** | Apache 2.0 | ✅ 可用 |
| **模型权重** | CC-BY-NC-SA-4.0 | ❌ **不可商用** |

**CC-BY-NC-SA-4.0 限制**：
- ❌ 不可用于商业目的
- ❌ 不可用于产品销售
- ❌ 不可在商业服务中使用
- ✅ 可用于个人/研究目的
- ✅ 衍生作品需同 License

> 💡 如果需要**商用** Fish Speech 技术，请联系 Fish Audio 官方获取商业授权（参考 Fish Audio S2 Pro 的商业授权模式）。

---

## 常见问题

| 问题 | 解答 |
|------|------|
| Q: S1 和 S2 Pro 哪个更好？ | A: S2 Pro 极致表现力（5B，Dual-AR），S1 更均衡（4B，RLHF），两者都需要商业授权 |
| Q: S1-mini 够用吗？ | A: 对于大多数场景足够，WER 仅 1.1%（vs S1 的 0.8%），显存仅需 1-2GB |
| Q: 中文情感标签支持吗？ | A: 情感标签主要在英文/中文验证，S1-mini 仅验证了英语和中文 |
| Q: 如何合法商用？ | A: 需要联系 Fish Audio 官方获取商业授权，或等待官方推出商业 License 版本 |

---

## 总结评分

| 维度 | S1 评分 | S1-mini 评分 |
|------|---------|-------------|
| **语音质量** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **克隆保真度** | ⭐⭐⭐⭐⭐（0.332） | ⭐⭐⭐⭐ |
| **情感控制** | ⭐⭐⭐⭐⭐（50+标签） | ⭐⭐⭐⭐⭐ |
| **中文支持** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **推理速度** | ⭐⭐⭐（RTF ~7x） | ⭐⭐⭐⭐（更轻量） |
| **轻量化** | ⭐⭐⭐（4B） | ⭐⭐⭐⭐⭐（0.5B） |
| **License** | ⭐⭐（CC-NC-SA） | ⭐⭐（CC-NC-SA） |
| **综合推荐** | ⭐⭐⭐⭐（非商用首选） | ⭐⭐⭐⭐（轻量非商用首选） |

---

> **一句话总结**：OpenAudio S1/S1-mini 是 Fish Speech 全新 RLHF 训练的 4B/0.5B 开源 TTS，WER 仅 0.8%、Speaker Sim 0.332，支持 50+ 情感标签，是非商用场景的顶级选择——⚠️ 但模型 License 为 CC-BY-NC-SA-4.0，**不可直接商用**，商用需联系官方授权。
