# 🎙️ Voice Clone Assistant — 语音克隆助手

> 基于免费语音克隆方案资源库（35+方案）| 2026-03-31

## 触发条件

用户说/发送以下内容时激活：

- "克隆我的声音"、"用我的声音读/说..."、"语音合成"
- "帮我生成一段语音"、"做一个语音克隆"
- "克隆音色"、"克隆声音"、"AI配音"
- 附带了 `.wav` / `.mp3` 音频文件并要求处理

## 输入处理

### 1. 识别参考音频
- 接收用户上传的音频文件（5秒～30分钟）
- 检查音频质量：时长 ≥ 5秒，格式为 wav/mp3/m4a，无明显噪声

### 2. 识别目标文本
- 从用户消息中提取待合成文本
- 如用户未提供文本，引导补充："请告诉我你想让这个声音说什么？"

### 3. 选择最优模型

根据以下决策树选择模型：

```
参考音频 ≤ 30秒？
├─ 是 → Qwen3-TTS（首选）或 CosyVoice2 或 MOSS-TTS
└─ 否（30秒~10分钟）→ GPT-SoVITS v4（微调）或 Fish Audio S2 Pro

无参考音频？
└─ ChatTTS v2（直接生成对话语音）

中文情感/方言需求？
└─ Xiaomi MiMo-V2-TTS（粤语/四川话/台湾腔/歌唱）

商用场景？
└─ 确认 License：选 Apache 2.0 / MIT 方案（CosyVoice3 / GLM-TTS / LuxTTS）
```

**首选推荐（2026-03 综合最优）：**

| 场景 | 推荐模型 | 理由 |
|------|----------|------|
| 3秒克隆，最简单 | **Qwen3-TTS** | pip安装，3秒参考，Apache 2.0 |
| 中文最强情感 | **Higgs Audio V2.5** | GRPO对齐，SOTA情感表达 |
| 完全免费商用 | **CosyVoice 3.0** | Apache 2.0，18+方言 |
| 超低延迟实时 | **LuxTTS** | 1GB显存，150x实时 |
| 有声书/超长文本 | **TADA** | 700秒上下文，零幻觉 |
| 高保真音质 | **VoxCPM 1.5** | 44.1kHz CD级音质 |

## 执行流程

### Step 1：环境准备（首次使用时执行）

```bash
# 推荐安装 Qwen3-TTS（一行命令搞定）
pip install qwen3-tts torch --index-url https://download.pytorch.org/whl/cu128
```

其他备选环境：
```bash
# CosyVoice2
git clone https://github.com/FunAudioLLM/CosyVoice.git && cd CosyVoice && pip install -r requirements.txt

# ChatTTS
pip install ChatTTS
```

### Step 2：调用 TTS 模型

**Qwen3-TTS（首选，最简单）：**
```python
from qwen3_tts import Qwen3TTS
import soundfile as sf

model = Qwen3TTS("Qwen/Qwen3-TTS-12Hz-1.7B-Base", quantize="int8")

# 克隆模式
audio = model.generate(
    text="你好，这是我克隆你声音生成的第一段语音。",
    ref_audio="/path/to/user_voice.wav"  # 用户上传的参考音频
)

sf.write("/workspace/output.wav", audio, 24000)
print("音频已生成：/workspace/output.wav")
```

**CosyVoice2（备选）：**
```python
import sys
sys.path.append('third_party/Matcha-TTS')
from cosyvoice.cli.cosyvoice import CosyVoice2
import torchaudio

model = CosyVoice2('pretrained_models/CosyVoice2-0.5B')
# 3秒极速克隆
result = model.inference_zero_shot(
    '你好，这是克隆语音演示。',
    '你',
    'path/to/user_voice.wav'
)
torchaudio.save('/workspace/output.wav', result['tts_speech'], 22050)
```

**ChatTTS（无参考音频，直接生成）：**
```python
import ChatTTS
chat = ChatTTS.Chat()
chat.load()

audio = chat.generate(
    "今天我给大家介绍一下人工智能的最新进展。",
    voice_temperature=0.3,  # 降低随机性，获得更稳定音色
)
chat.save(audio, "/workspace/output.wav")
```

### Step 3：返回结果
- 将生成的音频文件路径告知用户
- 如文件较大，提供 CDN 上传链接供下载
- 可选：用 `tts` 工具将文本转语音直接发回（简短内容）

## 进阶功能

### 情感控制
```python
# Qwen3-TTS 情感指令
audio = model.generate(
    text="太棒了！这次成功了呢！",
    ref_audio="参考.wav",
    emotion="excited"  # happy / sad / angry / neutral / excited
)
```

### 长文本批量生成
```python
# Qwen3-TTS Skill（长文稿批量配音）
# 参见 /workspace/reports/voice-cloning/Qwen3-TTS-Skill/README.md
from qwen3_tts import Qwen3TTS
model = Qwen3TTS(...)
result = model.batch_generate(long_text="长篇文章内容...", ref_audio="参考.wav")
```

### 多语言克隆
```python
# CosyVoice3 跨语言克隆
result = model.inference_cross_lingual(
    'Bonjour, comment allez-vous?',  # 法语
    ref_audio='chinese_voice.wav'   # 中文音色克隆法语
)
```

## 常见问题处理

| 问题 | 解决方案 |
|------|----------|
| "音色不像" | 换用更高质量参考音频（5-10秒清晰无噪声）；或用 GPT-SoVITS 微调训练 |
| "显存不足 (OOM)" | 换成 0.6B 轻量模型；开启 INT8 量化；减小 batch_size |
| "生成速度太慢" | 选 LuxTTS（150x实时）/ TADA（RTF 0.09）|
| "中文发音错误" | 换 GLM-TTS（音素级控制）或 CosyVoice 3.0（内置发音修补）|
| "有背景噪音" | 用 ffmpeg 预处理音频：`ffmpeg -i raw.wav -af denoise=hw=1 clean.wav` |
| "无参考音频" | 切换到 ChatTTS v2，无需克隆直接生成对话语音 |

## 音频预处理（推荐）

```bash
# 降噪 + 静音切除 + 格式标准化
ffmpeg -i raw.wav -af "highpass=f=200,lowpass=f=3000,adenoise=strength=5" \
  -ar 48000 -ac 1 -ab 192k clean.wav

# 静音切除（VAD）
ffmpeg -i raw.wav -af "silenceremove=start_periods=1:start_silence=0.5:start_threshold=-50dB:detection=peak,silenceremove=stop_periods=-1:stop_silence=0.5:stop_threshold=-50dB:detection=peak" \
  clean.wav
```

## 资源库位置

- 完整方案对比 → `/workspace/reports/voice-cloning/模型对比.md`
- Benchmark 性能数据 → `/workspace/reports/voice-cloning/Benchmark对比报告.md`
- 懒人速查卡 → `/workspace/reports/voice-cloning/懒人速查卡.md`
- 微调实战手册 → `/workspace/reports/voice-cloning/微调实战手册.md`
- 选型指南 → `/workspace/reports/voice-cloning/选型指南/README.md`
- 硬件推荐 → `/workspace/reports/voice-cloning/硬件推荐指南.md`

---

> 🤖 本 Skill 由免费语音克隆方案Agent（GPT-4o驱动）生成
> 资源库累计收录 **35+** 开源语音克隆方案 | 最后更新：2026-03-31
