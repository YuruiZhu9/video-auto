# LEMAS-TTS — IDEA研究院15万小时大规模多语言语音套件

> **发布方：** IDEA研究院（International Digital Economy Academy）
> **发布时间：** 2026年1月（arXiv: 2601.04233）
> **模型地址：** https://github.com/LEMAS-Project/LEMAS-TTS
> **HuggingFace：** https://huggingface.co/LEMAS-Project/LEMAS-TTS
> **魔搭：** https://www.modelscope.cn/models/LEMAS/LEMAS-TTS
> **在线体验：** https://huggingface.co/spaces/LEMAS-Project/LEMAS-TTS
> **许可证：** CC BY 4.0（可商用，需署名）

---

## 一、核心亮点

- **🏆 15万小时超大规模**：当前最大规模开源多语言语音数据集之一，覆盖10种语言
- **🌍 10种语言原生支持**：中文、英文、西班牙语、俄语、法语、德语、意大利语、葡萄牙语、印尼语、越南语
- **🔊 Flow-Matching 架构**：非自回归流匹配生成，高保真、多语言一致性优秀
- **🛠️ 开源完整套件**：TTS（零样本合成）+ Speech Editing（词级语音编辑）双能力
- **📈 基于 F5-TTS 改进**：继承 F5-TTS 优秀架构，专为超大规模多语言训练优化

---

## 二、核心能力

### 2.1 零样本多语言 TTS

| 能力 | 说明 |
|------|------|
| **Zero-shot 克隆** | 5~30秒参考音频即可克隆任意音色 |
| **10语言支持** | 中、英、西、俄、法、德、意、葡、印尼、越南 |
| **跨语言合成** | 参考音色可用于生成不同语言（部分支持） |
| **流式生成** | 支持实时流式输出 |

### 2.2 Speech Editing（语音编辑）

| 能力 | 说明 |
|------|------|
| **词级编辑** | 给定词级对齐 JSON，精准编辑指定词 |
| **局部修改** | 不影响其他部分，精准替换发音 |
| **多语言支持** | 同样覆盖 10 种语言 |

---

## 三、技术架构

### 3.1 LEMAS 数据集

| 指标 | 数值 |
|------|------|
| **总时长** | 15万小时（150K-Hour） |
| **语言数** | 10种语言 |
| **词级对齐** | Azure 语音服务自动标注 |
| **质量** | 严格构建流程，覆盖多样化说话场景 |

### 3.2 模型架构

| 组件 | 说明 |
|------|------|
| **基础架构** | 基于 F5-TTS（非自回归扩散 TTS） |
| **生成方法** | Flow-Matching（流匹配） |
| **文本前端** | 音素（phone）输入 |
| **可选预处理** | UVR5 降噪（参考音频） |
| **编辑能力** | Codec-based 词级语音编辑 |

### 3.3 推理规格

| 项目 | 要求 |
|------|------|
| **设备** | CUDA GPU（推荐）|
| **Python** | 3.10 |
| **依赖** | PyTorch + Torchaudio |
| **参考音频降噪** | 可选（`--denoise`） |

---

## 四、10种支持语言

| 语言 | 代码 | 说明 |
|------|------|------|
| 中文 | zh | 中文普通话 |
| 英文 | en | 英语 |
| 西班牙语 | es | 西班牙语 |
| 俄语 | ru | 俄语 |
| 法语 | fr | 法语 |
| 德语 | de | 德语 |
| 意大利语 | it | 意大利语 |
| 葡萄牙语 | pt | 葡萄牙语 |
| 印尼语 | id | 印尼语 |
| 越南语 | vi | 越南语 |

---

## 五、声音样本准备要求

### 5.1 音频规格

| 项目 | 推荐值 |
|------|--------|
| **格式** | WAV（推荐）或 MP3 |
| **采样率** | 16kHz 或 24kHz |
| **时长** | 5~30秒（零样本克隆参考音频） |
| **环境** | 安静、无混响 |
| **内容** | 清晰朗读，避免背景音乐 |

### 5.2 降噪预处理（可选）

```bash
# 使用 --denoise 参数启用 UVR5 降噪
python lemas_tts/scripts/tts_multilingual.sh --denoise
```

---

## 六、推理使用指南

### 6.1 环境安装

```bash
# 克隆仓库
git clone https://github.com/LEMAS-Project/LEMAS-TTS.git
cd LEMAS-TTS

# 创建环境
conda create -n lemas-tts python=3.10
conda activate lemas-tts

# 安装系统依赖
sudo apt-get update
sudo apt-get install -y ffmpeg

# 安装 PyTorch（按需选择 CUDA 版本）
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安装项目依赖
pip install -r requirements.txt
```

### 6.2 下载预训练模型

```bash
# 从 HuggingFace 下载
# https://huggingface.co/LEMAS-Project/LEMAS-TTS
# 将 pretrained_models/ 文件夹放在项目根目录
```

### 6.3 零样本克隆推理

```bash
# 进入项目目录
cd LEMAS-TTS
export PYTHONPATH="$PWD:${PYTHONPATH}"

# 使用多语言零样本 TTS
bash lemas_tts/scripts/tts_multilingual.sh
```

```python
# Python API 调用示例
import os
import sys
sys.path.insert(0, "/path/to/LEMAS-TTS")

import torch
from lemas_tts.models import build_model
from lemas_tts.utils import audio_io

# 加载模型
model = build_model(
    pretrained_dir="/path/to/pretrained_models",
    model_type="multilingual_grl",  # 或 "multilingual_prosody"
)

# 零样本克隆合成
ref_audio = "path/to/reference.wav"  # 5~30秒参考音频
text = "欢迎使用 LEMAS-TTS 零样本多语言语音合成系统。"  # 待合成文本
text_lang = "zh"  # 目标语言

# 推理
wav = model.tts(
    text=text,
    ref_audio=ref_audio,
    ref_text=None,  # 可传入参考音频对应文本提升质量
    lang=text_lang,
    cfg_strength=3.0,  # CFG 引导强度
    nfe=20,  # NFE 步数
    sway_sampling=False,
)

# 保存
audio_io.save(wav, "output.wav")
```

### 6.4 语音编辑推理

```bash
cd LEMAS-TTS
export PYTHONPATH="$PWD:${PYTHONPATH}"

# 需要：输入音频目录 + 词级对齐 JSON 目录
bash lemas_tts/scripts/speech_edit_multilingual.sh
```

```python
# 语音编辑示例
import sys
sys.path.insert(0, "/path/to/LEMAS-TTS")

from lemas_tts.models import build_model

model = build_model(
    pretrained_dir="/path/to/pretrained_models",
    model_type="multilingual_prosody",
)

# 编辑指定音频区域
edited_wav = model.speech_edit(
    wav_dir="/path/to/input_wavs",
    align_dir="/path/to/word_level_alignments",
    save_dir="/path/to/output",
    denoise=True,  # UVR5 降噪
)
```

---

## 七、与 OpenClaw Skills 集成

```python
def lemas_voice_clone(
    text: str,
    ref_audio_path: str,
    target_lang: str = "zh",
    cfg_strength: float = 3.0,
    nfe: int = 20
) -> str:
    """
    LEMAS-TTS 零样本多语言声音克隆
    - text: 待合成文本
    - ref_audio_path: 参考音频路径（5~30秒）
    - target_lang: 目标语言（zh/en/es/ru/fr/de/it/pt/id/vi）
    - cfg_strength: CFG 引导强度
    - nfe: NFE 步数
    """
    import sys
    sys.path.insert(0, "/path/to/LEMAS-TTS")
    from lemas_tts.models import build_model
    from lemas_tts.utils import audio_io

    model = build_model(
        pretrained_dir="/path/to/pretrained_models",
        model_type="multilingual_grl",
    )

    wav = model.tts(
        text=text,
        ref_audio=ref_audio_path,
        lang=target_lang,
        cfg_strength=cfg_strength,
        nfe=nfe,
    )

    output_path = "/tmp/lemas_output.wav"
    audio_io.save(wav, output_path)
    return output_path

# 使用示例：中文克隆
result = lemas_voice_clone(
    text="这是一个使用 LEMAS-TTS 进行零样本声音克隆的示例。",
    ref_audio_path="/workspace/audio/my_voice.wav",
    target_lang="zh",
    cfg_strength=3.0,
)
print(f"生成完成: {result}")
```

---

## 八、常见问题与解决

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| ImportError | 缺少 `emes学` | 检查 `PYTHONPATH` 是否设置 |
| CFG 效果不明显 | 强度过低 | 提高 `cfg_strength` 至 4.0~5.0 |
| 参考音频含噪声 | 环境嘈杂 | 使用 `--denoise` 启用 UVR5 降噪 |
| 显存不足 | 模型较大 | 减少 `nfe` 至 10，或使用 CPU |
| 音素发音错误 | 罕见语言/词汇 | 传入 `ref_text` 提供参考文本 |
| 推理速度慢 | NFE 步数过高 | 减少 `nfe` 至 10~15（质量略有下降）|

---

## 九、与其他方案对比

| 维度 | LEMAS-TTS | CosyVoice 3.0 | Qwen3-TTS | LongCat-AudioDiT |
|------|-----------|---------------|-----------|------------------|
| **语言数** | **10种** | 9种+18方言 | 10种 | 中英2种 |
| **训练数据** | **15万小时** | ~100万小时 | 未公开 | 未公开 |
| **SIM 相似度** | 中上 | 高 | 高 | **0.818 SOTA** |
| **Speech Editing** | ✅ 有 | ❌ | ❌ | ❌ |
| **MIT/Apache** | ❌ CC BY 4.0 | ✅ Apache-2.0 | ✅ Apache-2.0 | ✅ MIT |
| **商用意愿** | 可商用（需署名） | ✅ 免费商用 | ✅ 免费商用 | ✅ 免费商用 |
| **中文** | ✅ | ✅ 最佳 | ✅ 最佳 | ✅ SOTA |
| **零样本克隆** | ✅ | ✅ | ✅ | ✅ |
| **多语言一致性** | **优秀（10语言均训练）** | 良好 | 良好 | 仅中英 |
| **模型架构** | F5-TTS 改进版 | 自研 | 自研 | Waveform DiT |

> **结论：** LEMAS-TTS 的最大优势是**超大规模多语言一致性**（15万小时，10语言均覆盖），且具备**语音编辑**能力。如果你的产品面向东南亚/欧洲多语言市场，且需要零样本克隆+语音编辑双重能力，LEMAS-TTS 是不可替代的选择。

---

## 十、适用场景推荐

- ✅ **多语言出海应用**：东南亚/欧洲市场，覆盖10种语言
- ✅ **语音编辑需求**：需要精准修改某词发音（如配音纠错）
- ✅ **大规模多语言语音助手**：15万小时训练数据，鲁棒性优秀
- ✅ **多语言有声书/教育**：跨语言内容创作
- ❌ **追求SIM最高相似度**：选 LongCat-AudioDiT-3.5B
- ❌ **阿拉伯语/日语**：选 Silma TTS / Irodori-TTS
- ❌ **极低延迟（<100ms）**：选 Qwen3-TTS / ChatTTS v2
