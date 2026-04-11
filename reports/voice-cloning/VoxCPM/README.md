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

---

## 九、VoxCPM2 — 2026-04-11 今日重大更新（2B · Tokenizer-Free · 9种方言）

> ⏰ **新鲜度**：2026-04-11 今日新增

---

### 一句话评价

> **Apache 2.0 可商用 + 2B参数 + 48kHz + 9种中国方言 + Tokenizer-Free 架构消除量化误差** —— 方言保护和高保真语音合成的强力新选择。

---

### 基本信息

| 属性 | 值 |
|------|-----|
| **发布机构** | OpenBMB（面壁智能）+ 清华大学THUHCSI |
| **发布时间** | **2026-04-11（今日）** |
| **参数量** | **2B**（20亿参数）|
| **架构** | Tokenizer-Free 扩散自回归（连续潜空间）|
| **GitHub** | [OpenBMB/VoxCPM](https://github.com/OpenBMB/VoxCPM)（同仓库）|
| **HuggingFace** | [openbmb/VoxCPM2](https://huggingface.co/openbmb/VoxCPM2) |
| **在线Demo** | [voxcpm.net](https://voxcpm.net/zh/)（新版）|
| **许可证** | **Apache 2.0**（商业友好，可自由使用、修改、分发）|
| **训练数据** | **200万小时**多语言语音数据 |

---

### 核心技术

#### 架构：Tokenizer-Free 扩散自回归

**传统 Token-based TTS 的问题：**
```
文本 → Tokenizer（量化）→ 离散Token → 扩散生成 → Tokenizer解码 → 波形
                     ↑ 量化误差：丢失音色细节 ↑
```

**VoxCPM2 的创新：**
```
文本 → 连续潜空间扩散自回归 → 连续波形输出
         ↑ 无Tokenizer，无量化误差，音色细节完整保留
```

| 组件 | 技术说明 |
|------|----------|
| **语言骨干** | 基于 MiniCPM-4 语言模型实现语义理解与韵律控制 |
| **音频编解码** | AudioVAE V2 不对称编码/解码，输出 **48kHz** 高保真音频 |
| **语义-声学解耦** | 韵律与声色并行优化，表达更自然 |
| **推理机制** | 上下文感知韵律推理，根据句子语义推断语调与节奏 |
| **扩散过程** | LocDiT（局部感知 Diffusion Transformer）|

---

### 核心能力

#### 语言与方言覆盖

- **30种全球语言**：中、英、日、韩、法、德、西、葡、俄等
- **特别强化东南亚8国**：泰语、越南语、印尼语、马来语、菲律宾语等
- **🆕 9种中国方言**：四川话、粤语、吴语、东北话、河南话、陕西话、山东话、天津话、闽南语

#### 两种克隆模式

| 模式 | 说明 | 样本要求 |
|------|------|---------|
| **可控克隆（Controllable Clone）** | 提取音色后可调整情绪与节奏 | **3-10秒**参考音频 |
| **终极克隆（Ultimate Clone）** | 高保真重放，保留声线+节奏+情绪全部细节 | 参考音频 + 文字转写 |

> 终极克隆需要提供参考音频对应的文字转录（Whisper ASR 自动生成），实现真正的音频续读式克隆。

#### 音色设计（Voice Design）

- 无需上传任何参考音频
- 通过文字描述从零创造声音（如："清澈男中音，偏冷调，像月光落在雪地上"）
- 支持精确控制情绪、语速、音量

#### 高音质输出

- **48000Hz CD级音质**（市面普遍为24000Hz）
- 生成速度约 1 秒

#### 非语言符号控制

```
[laughing]  — 笑声
[sigh]      — 叹气
[Uhm]       — 嗯/呃语气
```

---

### 性能基准

| 指标 | VoxCPM2 | VoxCPM v1.5 |
|------|---------|-------------|
| **参数量** | **2B** | 1.5B |
| **采样率** | **48kHz** | 48kHz |
| **训练数据** | **200万小时** | 180万小时+ |
| **克隆方式** | 可控克隆 + 终极克隆 | 零样本克隆 |
| **中国方言** | **9种** | 未明确 |
| **加速方案** | **VoxCPM-NanoVLLM**（RTF~0.13）| - |
| **开发者工具** | ComfyUI/WebUI/Rust/LoRA | 基础 |

**RTF 性能对比：**

| 模型 | RTF（RTX 4090）|
|------|---------------|
| OmniVoice | 0.025（全场最快）|
| **VoxCPM2 + NanoVLLM** | **~0.13** |
| **VoxCPM2（标准）** | **~0.30** |
| VoxCPM v1.5 | 0.17 |
| RVC V3 | 0.09 |

---

### 快速上手

#### 安装

```bash
pip install voxcpm
# 或源码
git clone https://github.com/OpenBMB/VoxCPM.git
cd VoxCPM && pip install -e .
```

#### Python 使用

```python
from voxcpm import VoxCPM

# 加载 VoxCPM2（自动识别最新版本）
model = VoxCPM.from_pretrained("openbmb/VoxCPM2")

# 1. 可控克隆（3-10秒参考音频）
audio = model.generate(
    text="你好，这是语音克隆演示。",
    reference_audio="reference.wav",
    language="zh"  # 可省略（自动检测）
)

# 2. 终极克隆（高保真重放，需要转写文本）
audio = model.generate(
    text="这是要合成的新内容。",
    reference_audio="reference.wav",
    reference_text="这是参考音频的文字内容。",  # 终极克隆专用
    mode="ultimate"  # 高保真模式
)

# 3. 语音设计（无需参考音频）
audio = model.generate(
    text="你好，请用这个音色读这段话。",
    voice_prompt="清澈女声，年轻，温柔，像春天的微风"
)

# 4. 方言合成
audio = model.generate(
    text="今天天气好巴适哦！",
    dialect="Sichuan"  # 四川话
)

model.save(audio, "output.wav")
```

#### 方言合成示例

| 方言 | 示例文本 | Control Instruction |
|------|---------|---------------------|
| 四川话 | 今天天气好巴适哦！ | `Sichuan` |
| 粤语 | 今日天气好正啊！ | `Cantonese` |
| 吴语 | 阿拉上海人！ | `Wu` |
| 东北话 | 嘎哈呢你？ | `Northeastern` |
| 河南话 | 中！恁弄啥嘞？ | `Henan` |
| 陕西话 | 额贼！ | `Shaanxi` |
| 山东话 | 恁来唠？ | `Shandong` |
| 天津话 | 嘛呢？介是嘛事儿啊！ | `Tianjin` |
| 闽南语 | 哇爱汝！ | `Minnan` |

---

### 开发者工具链

| 工具 | 说明 |
|------|------|
| **VoxCPM-NanoVLLM** | 高吞吐加速（RTF ~0.13，RTX 4090）|
| **ComfyUI 插件** | 可视化工作流 |
| **WebUI** | Gradio 交互界面 |
| **Rust 版本** | 高性能生产环境 |
| **LoRA 微调** | 5分钟音频微调专属音色 |
| **全参数微调** | 大规模定制训练 |

#### LoRA 微调示例

```python
from voxcpm.finetune import LoRATrainer

trainer = LoRATrainer("openbmb/VoxCPM2")
trainer.train(
    reference_audio="my_voice.wav",  # 5-20分钟音频
    num_epochs=10,
    output_dir="./lora_model/"
)
```

---

### 适用场景

✅ **有声书/播客**（48kHz 高保真音质，9种方言可选）  
✅ **方言内容创作**（四川话/粤语/吴语等方言保护与传播）  
✅ **跨境出海**（东南亚语言强化，30种语言覆盖）  
✅ **游戏/影视配音**（终极克隆保留角色全部情感细节）  
✅ **声音设计**（文字描述生成全新音色，无需录音）  
✅ **个人音色定制**（5分钟音频 LoRA 微调）

---

### 局限性

- ⚠️ RTX 4090 以上 GPU 推荐（2B 参数）
- ⚠️ 标准版 RTF ~0.30（比 OmniVoice 的 0.025 慢很多）
- ⚠️ 终极克隆需要文字转写（增加预处理步骤）
- ⚠️ 中文主要语言支持一般（非专精，不如 Qwen3-TTS / CosyVoice3）

---

### OpenClaw Skills 集成

```python
import subprocess

def tts_voxcpm2(text, ref_audio=None, dialect=None, output="/workspace/output.wav"):
    """VoxCPM2 调用模板（供 OpenClaw exec 使用）"""
    import json
    params = {"text": text, "output": output}
    if ref_audio:
        params["reference_audio"] = ref_audio
    if dialect:
        params["dialect"] = dialect

    cmd = [
        "python", "-c",
        f"""
from voxcpm import VoxCPM
model = VoxCPM.from_pretrained('openbmb/VoxCPM2')
audio = model.generate(**{json.dumps(params)})
model.save(audio, '{output}')
"""
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout
```

---

### vs. 其他主流方案对比

| 模型 | 参数量 | 采样率 | 中国方言 | RTF | 许可证 | 核心优势 |
|------|--------|--------|---------|-----|--------|---------|
| **VoxCPM2** 🆕 | 2B | **48kHz** | **9种** | ~0.30 | Apache 2.0 | 方言+音质首选 |
| **OmniVoice** | 0.8B | 24kHz | 部分 | **0.025** | Apache 2.0 | 646语言+极速 |
| Qwen3-TTS 1.7B | 1.7B | 24kHz | 中文优化 | ~0.05 | Apache 2.0 | 低延迟中文 |
| CosyVoice3 RL | - | - | 中文专精 | ~0.1 | Apache 2.0 | 中文质量最佳 |
| Kokoro-82M | 82M | - | 100音色 | CPU | MIT | 无GPU首选 |

---

> 📌 **一句话总结**：VoxCPM2 是**音质发烧友+方言创作者首选**，Tokenizer-Free 架构 + 9种中国方言 + 48kHz + 终极克隆高保真重放 + Apache 2.0，适合有声书、方言内容创作和出海本地化配音。

