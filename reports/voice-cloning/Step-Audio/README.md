# Step-Audio：阶跃星辰 1300 亿参数产品级语音交互模型

> 资料来源：GitHub stepfun-ai/Step-Audio · arXiv:2502.11946
> 本报告由免费语音克隆方案Agent 自动生成 | 2026-03-27

---

## 一、方案概览

| 属性 | 详情 |
|------|------|
| **开发者** | 阶跃星辰（StepFun AI）+ 吉利汽车 |
| **发布时间** | 2025年2月18日 |
| **开源地址** | https://github.com/stepfun-ai/Step-Audio |
| **Hugging Face** | https://huggingface.co/stepfun-ai/Step-Audio-Chat |
| **ModelScope** | https://modelscope.cn/models/stepfun-ai/Step-Audio-Chat |
| **论文** | arXiv:2502.11946 |
| **许可证** | Apache 2.0（代码）/ 模型权重遵循各仓库协议 |
| **核心能力** | 端到端语音对话 · 零样本克隆 · 情感控制 · 方言 · 歌唱 · Rap |
| **中文理解** | ⭐⭐⭐⭐⭐（HSK-6 汉语水平考试顶级评测第一）|
| **推荐度** | 🥇 **全双工语音助手首选（企业级）** |

---

## 二、核心架构：全球首个产品级全链路语音交互模型

Step-Audio 是全球首个**产品级开源全链路语音交互模型**，将 ASR（语音识别）、LLM（对话理解）和 TTS（语音合成）在统一框架内融合，突破传统串联架构的延迟瓶颈。

### 三层模型体系

| 模型 | 参数规模 | 作用 | 显存需求 |
|------|----------|------|----------|
| **Step-Audio-Chat** | **130B** | 统一多模态大模型（理解+生成）| 265GB（全模型）|
| **Step-Audio-TTS-3B** | **3B** | 轻量级 TTS（指令跟随能力强）| ~8GB |
| **Step-Audio-Tokenizer** | — | 双码本音频 tokenizer | 1.5GB |

### 核心技术亮点

#### 1. 首创双码本音频 Tokenizer
| Tokenizer | 码本大小 | Token 速率 | 时序对应 |
|-----------|----------|------------|----------|
| **语义 Tokenizer** | 1024-entry | 16.7Hz | 2个单位 |
| **声学 Tokenizer** | 4096-entry | 25Hz | 3个单位 |
| **时序对齐** | — | — | 语义:声学 = **2:3** |

双码本设计让模型同时捕获高层语义信息和细粒度声学特征。

#### 2. 生成式数据引擎（颠覆性创新）✨
传统 TTS 依赖大量人工采集录音数据，成本极高。Step-Audio 创新性地使用 **130B 多模态模型自动生成高质量训练数据**，大幅降低数据成本。

#### 3. RLHF 细粒度控制
通过强化学习人类反馈（RLHF）对 AQTA（Audio Input Text Output）任务进行优化，实现对以下维度的精准控制：
- 🎭 情感（愤怒/快乐/悲伤）
- 🗣️ 方言（粤语/四川话）
- 🎵 语速/韵律风格
- 🎤 歌唱/Rap 风格

---

## 三、声音样本准备要求（语音克隆）

### 克隆方式
Step-Audio 支持通过 **prompt wav** 进行音色克隆，无需微调模型。

### 参考音频要求
- 格式：WAV
- 时长：建议 10-30秒（越长克隆效果越好）
- 环境：安静、无噪声
- 内容：清晰普通话朗读

### Speaker 信息格式

```python
speaker_info = {
    "speaker": "unique_speaker_id",       # 自定义说话人ID
    "prompt_text": "今天天气真好。",        # 参考音频对应的文本
    "wav_path": "/path/to/prompt.wav"     # 参考音频路径
}
```

---

## 四、安装与部署

### 环境要求
- Python ≥ 3.10.0
- PyTorch ≥ 2.3（含 CUDA 11.8+）
- NVIDIA GPU（A800/H800 80GB × 4 推荐）
- Linux 操作系统

### Step-Audio-Chat（130B 全量模型，顶级效果）

```bash
# 克隆仓库
git clone https://github.com/stepfun-ai/Step-Audio.git
cd Step-Audio

# 构建 Docker（推荐）
docker build . -t step-audio
docker run --rm -ti --gpus all \
    -v /your/code/path:/app \
    -v /your/model/path:/model \
    -p 7860:7860 step-audio -- bash

# 下载模型（vLLM 推理推荐）
export OPTIMUS_LIB_PATH=/model/Step-Audio-Chat/lib
vllm serve /model/Step-Audio-Chat \
    --dtype auto -tp $tp \
    --served-model-name step-audio-chat \
    --trust-remote-code

# 启动语音对话
python call_vllm_chat.py
```

### Step-Audio-TTS-3B（轻量版，8GB 显存可运行）

```bash
# 推荐用于纯 TTS 任务（非全双工对话）
# 仅需 ~8GB 显存，适合个人开发者

python tts_inference.py \
    --model-path /path/to/downloaded/model \
    --output-path /output/audio \
    --synthesis-type use_tts_or_clone
```

### Web 界面体验

```bash
# 全双工对话 Demo
python app.py --model-path /path/to/model

# 纯 TTS Demo
python tts_app.py --model-path /path/to/model
```

---

## 五、推理命令与 Python API

### 离线推理（语音对话模式）

```bash
python offline_inference.py --model-path /path/to/model
```

### TTS 语音克隆推理

```python
import os

# Step-Audio TTS 克隆推理
python tts_inference.py \
    --model-path /path/to/downloaded/model \
    --output-path /output/audio \
    --synthesis-type use_tts_or_clone
```

### 音色克隆示例（Python API）

```python
# speaker_info 定义音色
speaker_info = {
    "speaker": "my_voice",
    "prompt_text": "今天天气真不错，我们出去走走吧。",
    "wav_path": "/workspace/voice_samples/my_voice.wav"
}

# 生成语音
audio = step_audio_tts.generate(
    text="你好，欢迎使用 Step-Audio 语音合成系统！",
    speaker=speaker_info,
    emotion="happy",        # 可选：happy/sad/angry/neutral
    speed=1.0,              # 可选：语速 0.5-2.0
    dialect="sichuan"       # 可选：sichuan/cantonese（空=普通话）
)
```

### 全双工语音对话（最强大功能）

```bash
# 实时对话，突破传统 ASR→LLM→TTS 三段式架构延迟
python app.py --model-path /path/to/model
# 访问 http://localhost:7860 即可体验
```

---

## 六、性能基准评测

### ASR 语音识别性能

| 模型 | Aishell-1 WER (%) | LibriSpeech test-clean WER (%) | 平均 (%) |
|------|-------------------|-------------------------------|----------|
| **Step-Audio-Pretrain** | **0.87** | **2.36** | **4.64** |
| Step-Audio-Chat | 1.95 | 3.11 | 5.89 |

### TTS 语音合成性能

| 模型 | test-zh CER (%) | test-en WER (%) |
|------|-----------------|-----------------|
| **Step-Audio-TTS** | **1.17** | **2.0** |
| Step-Audio-TTS-3B | 1.31 | 2.31 |

### AQTA 全双工语音对话评测（StepEval-Audio-360）

| 模型 | 事实性 (%) | 相关性 (%) | 对话评分 |
|------|-----------|-----------|----------|
| **Step-Audio-Chat** | **66.4** | **75.2** | **4.11/5** |
| GLM4-Voice | 54.7 | 66.4 | 3.49/5 |

> 在 HSK-6（汉语水平考试六级）评测中，Step-Audio 排名第一，是**最懂中国话的开源语音交互大模型**。

---

## 七、与其他主流方案对比

| 维度 | Step-Audio 130B | Step-Audio-TTS-3B | CosyVoice2 | Qwen3-TTS | ChatTTS v2 |
|------|----------------|-------------------|------------|-----------|-----------|
| **架构类型** | 端到端全双工 | 独立 TTS | 级联 TTS | 级联 TTS | 生成式 |
| **参数规模** | 130B | 3B | 0.5B | 1.7B | ~200M |
| **克隆方式** | prompt wav | prompt wav | 零样本 | 零样本 | 无需克隆 |
| **中文 CER** | **1.17%** | 1.31% | 1.38% | 未公开 | — |
| **对话能力** | ✅ 全双工 | ❌ | ❌ | ❌ | ❌ |
| **方言** | 粤语/四川话 | 粤语/四川话 | 18+ | 有限 | 有限 |
| **歌唱/Rap** | ✅ | ✅ | 有限 | ❌ | ❌ |
| **最低显存** | 265GB（全量）| ~8GB | ~6GB | ~6GB | ~2GB |
| **许可证** | Apache 2.0 | Apache 2.0 | Apache 2.0 | Apache 2.0 | Apache 2.0 |

---

## 八、常见问题与解决

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 130B 模型跑不动 | 显存需求 265GB | 使用 TTS-3B 轻量版（~8GB）|
| 克隆音色不像 | 参考音频质量差 | 换用更清晰、时长更长的音频 |
| 对话延迟高 | 网络/硬件不足 | 使用 TTS-3B 轻量版单独做 TTS |
| 唱歌不自然 | 音乐数据不足 | 使用 `--singing` 专用模式 |
| 中文方言不准确 | 模型方言数据分布 | 提供更多方言参考音频 |

---

## 九、与 OpenClaw Skills 集成

### 全双工语音助手集成（130B 模型）

```
用户语音输入（麦克风）
    ↓
Step-Audio-Chat（端到端理解+生成）
    ↓
流式音频输出（直接说话，无需等待）
    ↓
OpenClaw 实时推送至用户
```

```python
# /workspace/integrations/step_audio_full.py
# 全双工语音助手集成
import subprocess

def start_voice_assistant(model_path: str):
    """启动 Step-Audio 全双工语音助手"""
    subprocess.Popen([
        "python", "app.py",
        "--model-path", model_path,
        "--port", "7860"
    ])
    print("🌐 访问 http://localhost:7860 体验全双工语音对话")
```

### TTS 语音克隆集成（轻量版，8GB 显存）

```python
# /workspace/integrations/step_audio_tts.py
import subprocess, os

MODEL_PATH = "/workspace/models/Step-Audio"
REF_AUDIO = "/workspace/voice_samples/user_voice.wav"
OUTPUT_DIR = "/workspace/tts_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def tts_clone(text: str, output: str = None, emotion: str = "neutral"):
    output = output or f"{OUTPUT_DIR}/output.wav"
    
    cmd = [
        "python", f"{MODEL_PATH}/tts_inference.py",
        "--model-path", MODEL_PATH,
        "--output-path", output,
        "--synthesis-type", "use_tts_or_clone",
        "--text", text,
        "--emotion", emotion
    ]
    subprocess.run(cmd, check=True)
    return output

# 使用示例
if __name__ == "__main__":
    audio = tts_clone(
        "欢迎使用阶跃星辰语音合成，这是一段测试音频。",
        emotion="happy"
    )
    print(f"生成完毕: {audio}")
```

---

## 十、总结与推荐理由

**Step-Audio 优势：**
1. ✅ **130B 顶级参数**：全场最强语音理解和生成能力
2. ✅ **全双工端到端**：突破传统 ASR→LLM→TTS 延迟瓶颈，一步到位
3. ✅ **中文第一**：HSK-6 评测第一，最懂中国话的开源语音模型
4. ✅ **情感+方言+歌唱+Rap**：全方位语音风格控制
5. ✅ **生成式数据引擎**：大幅降低训练数据成本，技术创新性强
6. ✅ **Apache 2.0**：商业可用

**注意事项：**
- ⚠️ 130B 全量模型需要 265GB 显存，适合有高端硬件的团队
- ⚠️ **TTS-3B 轻量版**（~8GB）适合纯 TTS 任务，性能也很强（CER 1.31%）
- ⚠️ 2025年2月发布，非最新（但技术依然领先）
- ⚠️ 主要面向产品级全双工语音助手，非轻量个人工具

**推荐场景：**
- 🥇 **全双工语音助手**（企业级，有高端 GPU 集群）
- 🥇 **中文语音交互产品**（最懂中国话）
- 🥇 **需要情感+方言+歌唱综合能力**（全网最强综合能力）
- 🥈 **TTS 轻量克隆**（使用 TTS-3B 版本，8GB 显存即可）
