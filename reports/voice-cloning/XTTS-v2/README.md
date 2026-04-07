# Coqui XTTS-v2 跨语言语音克隆指南

> 6秒音频即可克隆 | 17种语言支持 | MPL 2.0许可证

---

## 一、项目简介

**XTTS-v2** 是Coqui推出的第二代跨语言语音合成模型，支持仅用6秒音频克隆声音，并可生成17种语言的语音。

### 核心特性
- 🎯 **即时克隆**：仅需6秒音频
- 🌍 **17种语言**：覆盖主流语言
- 😊 **情感迁移**：保留参考音频情感
- 🔄 **跨语言合成**：中英日韩法德西等
- 💰 **免费商用**：MPL 2.0许可证

### 与XTTS-v1对比

| 特性 | XTTS-v1 | XTTS-v2 |
|-----|---------|---------|
| 支持语言 | 15种 | 17种（+匈牙利语、韩语） |
| 采样率 | 22kHz | 24kHz |
| 克隆质量 | 一般 | 优秀 |
| 模型稳定性 | 一般 | 优秀 |

---

## 二、环境配置

### 2.1 系统要求

| 项目 | 最低配置 | 推荐配置 |
|-----|---------|---------|
| Python | 3.8-3.11 | 3.10 |
| 内存 | 8GB | 16GB |
| 显卡 | 无 | NVIDIA 6GB+ |
| 存储 | 20GB | 50GB（模型较大） |

### 2.2 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/coqui-ai/TTS.git
cd TTS

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. 安装TTS
pip install TTS

# 4. 验证安装
python -c "from TTS.api import TTS; print('OK')"
```

### 2.3 Docker安装（可选）

```bash
# 使用Docker运行
docker run -it -p 5002:5002 \
    -v $(pwd)/output:/app/output \
    ghcr.io/coqui-ai/tts
```

---

## 三、声音样本准备

### 3.1 音频要求

| 参数 | 推荐值 | 说明 |
|-----|-------|------|
| 格式 | WAV | 无压缩最佳 |
| 采样率 | 16kHz+ | 越高越好 |
| 时长 | 6-30秒 | 最短6秒，越长越准 |
| 质量 | 清晰无噪 | 底噪要低 |

### 3.2 录音建议

- ✅ 安静环境，无背景音乐
- ✅ 单一说话人
- ✅ 正常语速，发音清晰
- ✅ 涵盖不同情感（可选）

### 3.3 音频处理

```python
import librosa
import numpy as np

# 加载并处理音频
audio, sr = librosa.load('reference.wav', sr=24000)

# 如果采样率不对，进行转换
# audio, sr = librosa.load('reference.wav', sr=24000)

# 裁剪到合适长度（6-30秒）
if len(audio) > sr * 30:  # 超过30秒
    audio = audio[:sr * 30]

# 保存处理后的音频
import soundfile as sf
sf.write('reference_processed.wav', audio, sr)
```

---

## 四、使用方法

### 4.1 基础语音合成

```python
from TTS.api import TTS

# 初始化（首次运行会自动下载模型，约3GB）
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# 基础合成
tts.tts_to_file(
    text="你好，这是XTTS-v2语音合成测试。",
    file_path="output.wav",
    language="zh-cn"
)
```

### 4.2 语音克隆

```python
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# 使用参考音频克隆
tts.tts_to_file(
    text="这是使用参考音频克隆出来的声音。",
    file_path="cloned.wav",
    speaker_wav="reference.wav",  # 参考音频路径
    language="zh-cn",
    gpt_cond_len=3,        # 控制相似度 (1-10)
    temperature=0.7,       # 随机性 (0-1)
)
```

### 4.3 跨语言合成

```python
# 用中文参考音频生成英文语音
tts.tts_to_file(
    text="Hello! This is a cross-language synthesis test.",
    file_path="cross_lang.wav",
    speaker_wav="chinese_reference.wav",
    language="en",
)

# 用英文参考音频生成中文
tts.tts_to_file(
    text="今天天气真不错。",
    file_path="chinese_voice.wav",
    speaker_wav="english_reference.wav",
    language="zh-cn",
)
```

### 4.4 命令行使用

```bash
# 基础合成
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 \
    --text "Hello world" \
    --language_idx en \
    --use_cuda true \
    --out_path output.wav

# 克隆模式
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 \
    --text "语音克隆测试" \
    --speaker_wav reference.wav \
    --language_idx zh \
    --out_path cloned.wav
```

---

## 五、参数详解

### 5.1 核心参数

| 参数 | 范围 | 说明 | 推荐值 |
|-----|------|------|-------|
| `gpt_cond_len` | 1-10 | 克隆相似度，越高越像 | 3-5 |
| `temperature` | 0-1 | 生成随机性，越高越多样 | 0.7 |
| `length_penalty` | 0.5-2.0 | 语速控制 | 1.0 |
| `repetition_penalty` | 1-10 | 重复惩罚 | 1.2 |
| `top_k` | 1-100 | Top-K采样 | 50 |
| `top_p` | 0-1 | 核采样 | 0.85 |

### 5.2 高级参数

```python
# 高质量输出
tts.tts_to_file(
    text="高质量语音测试",
    file_path="high_quality.wav",
    speaker_wav="reference.wav",
    language="zh-cn",
    gpt_cond_len=5,
    temperature=0.5,
    length_penalty=1.1,
    repetition_penalty=1.5,
    top_k=50,
    top_p=0.85,
)

# 快速输出
tts.tts_to_file(
    text="快速输出测试",
    file_path="fast.wav",
    speaker_wav="reference.wav",
    language="zh-cn",
    gpt_cond_len=1,
    temperature=0.9,
)
```

---

## 六、语言支持

### 6.1 支持的语言

| 语言 | 代码 | 示例 |
|-----|------|------|
| 中文(普通话) | zh-cn | 你好，世界！ |
| 英语 | en | Hello, world! |
| 日语 | ja | こんにちは |
| 韩语 | ko | 안녕하세요 |
| 西班牙语 | es | ¡Hola mundo! |
| 法语 | fr | Bonjour le monde! |
| 德语 | de | Hallo Welt! |
| 意大利语 | it | Ciao mondo! |
| 葡萄牙语 | pt | Olá mundo! |
| 波兰语 | pl | Witaj świecie! |
| 土耳其语 | tr | Merhaba dünya! |
| 俄语 | ru | Привет мир! |
| 荷兰语 | nl | Hallo wereld! |
| 捷克语 | cs | Ahoj světe! |
| 阿拉伯语 | ar | مرحبا بالعالم |
| 匈牙利语 | hu | Hello világ! |
| 韩语 | ko | 안녕하세요 |

### 6.2 语言代码使用

```python
# 使用语言代码
tts.tts_to_file(
    text="中文测试",
    file_path="output.wav",
    language="zh-cn"  # 简体中文
)

tts.tts_to_file(
    text="English test", 
    file_path="output.wav",
    language="en"
)
```

---

## 七、与OpenClaw集成

### 7.1 创建Service

```python
# xtts_service.py
from TTS.api import TTS
import os

# 全局单例
_tts = None

def init_tts():
    global _tts
    if _tts is None:
        _tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
    return _tts

def clone_voice(text, reference_audio, output_path, language="zh-cn"):
    """克隆声音并生成语音"""
    tts = init_tts()
    
    tts.tts_to_file(
        text=text,
        file_path=output_path,
        speaker_wav=reference_audio,
        language=language,
        gpt_cond_len=3,
        temperature=0.7,
    )
    
    return output_path

def cross_language(text, reference_audio, target_lang):
    """跨语言合成"""
    tts = init_tts()
    
    output = f"cross_{target_lang}.wav"
    tts.tts_to_file(
        text=text,
        file_path=output,
        speaker_wav=reference_audio,
        language=target_lang,
    )
    
    return output
```

### 7.2 集成配置

```yaml
# voice-xtts-skill.yaml
name: voice-xtts
description: 跨语言语音克隆服务
version: 1.0.0
entry: xtts_service.py
capabilities:
  - voice_clone
  - cross_language_synthesis
```

---

## 八、常见问题

### Q1: 克隆不像本人
**解决方案**：
- 增加参考音频时长（15秒以上）
- 调整 `gpt_cond_len=5-8`
- 确保参考音频质量高

### Q2: 生成有噪音
**解决方案**：
- 清理参考音频底噪
- 降低 `temperature` 到 0.5

### Q3: 推理速度慢
**解决方案**：
- 使用GPU加速
- 减少 `gpt_cond_len`
- 批量处理

### Q4: 跨语言效果差
**解决方案**：
- 使用目标语言的母语者参考音
- 选择语言相近的参考音（如英法）

### Q5: 模型下载失败
**解决方案**：
- 使用国内镜像
- 手动下载模型文件

---

## 九、性能优化

### 9.1 GPU加速

```python
# 确保使用GPU
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
```

### 9.2 内存优化

```python
# 减少内存占用
tts.tts_to_file(
    ...,
    gpt_cond_len=3,  # 降低
)
```

### 9.3 预热模型

```python
# 首次调用前预热
_ = tts.tts_to_file(
    text="warmup",
    file_path="/dev/null",
    language="en"
)
```

---

## 十、参考资源

- GitHub: https://github.com/coqui-ai/TTS
- 官网: https://coqui.ai
- 模型下载: https://huggingface.co/coqui/XTTS-v2
- Docker: https://github.com/coqui-ai/TTS/tree/main/docker

---

## 十一、总结

XTTS-v2是最强大的跨语言克隆方案：
- ✅ 6秒极短样本
- ✅ 17种语言支持
- ✅ 情感迁移能力
- ✅ 免费可商用

适合多语言配音、跨语言内容创作、国际化应用。

---

*更新时间：2026-03-20*
