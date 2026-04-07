# CosyVoice 3.0 完整部署与使用指南

> 阿里通义实验室出品 | 实时流式延迟150ms | Apache-2.0商用许可

---

## 一、项目概览

CosyVoice 是阿里通义实验室 FunAudioLLM 团队开发的新一代生成式语音大模型。2025年12月发布 **CosyVoice 3.0**，在音色相似度、情感控制、多方言支持上全面升级。

- **最新版本**：Fun-CosyVoice 3.0（2025年12月）
- **GitHub**：https://github.com/FunAudioLLM/CosyVoice
- **星标**：18k ⭐ | Fork：2k
- **许可证**：Apache-2.0（可商用）
- **模型下载**：ModelScope / HuggingFace

---

## 二、核心能力一览

| 能力 | 说明 |
|------|------|
| **语言覆盖** | 9种语言（中/英/日/韩/德/西/法/意/俄） |
| **中文方言** | 18种+（粤语/闽南语/四川话/东北话/山西话/上海话/天津话等） |
| **流式延迟** | 最低 **150ms** 首包延迟 |
| **克隆速度** | 3秒样本零样本克隆 |
| **情感控制** | 支持哭腔/机器人音/指令控制 |
| **商用许可** | Apache-2.0，完全免费商用 |

---

## 三、声音样本准备

### 音频格式要求

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| **格式** | WAV / FLAC | 无损格式优先 |
| **采样率** | 16000 Hz 或 22050 Hz | 16kHz 最低要求 |
| **时长** | 零样本：3-30秒<br>微调：5-30分钟 | 零样本3秒即可 |
| **声道** | 单声道 | 必须mono |
| **信噪比** | >30dB | 安静环境录制 |

### 录音内容建议

```
✅ 零样本（3-30秒）：
   「你好，我是你的语音助手，今天有什么可以帮助你的吗？」

✅ 高质量样本（1-5分钟）：
   包含：问候 / 陈述 / 疑问 / 感叹 等多种句式
   建议：朗读一段新闻或故事

❌ 避免：
   - 背景音乐
   - 多人对话
   - 回声/混响严重的环境
```

---

## 四、安装部署

### 方案1：PyPI 一键安装（推荐）

```bash
# 创建虚拟环境
conda create -n cosyvoice python=3.10
conda activate cosyvoice

# 安装 PyTorch（CUDA 12.1）
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装 CosyVoice
pip install cosyvoice

# 下载预训练模型（自动）
python -c "from cosyvoice import CosyVoice; CosyVoice.download('CosyVoice-300M')"
```

### 方案2：GitHub 源码安装

```bash
# 克隆仓库
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice

# 创建环境
conda create -n cosyvoice python=3.10
conda activate cosyvoice

# 安装依赖
pip install -r requirements.txt

# 下载模型（手动）
# ModelScope: FunAudioLLM/Fun-CosyVoice3-0.5B-2512
# HuggingFace: FunAudioLLM/Fun-CosyVoice3-0.5B-2512
```

### 方案3：Docker 部署

```bash
# 构建镜像
docker build -t cosyvoice:latest .

# 运行
docker run --gpus all -p 8080:8080 \
  -v $(pwd)/models:/app/models \
  cosyvoice:latest
```

### 方案4：ModelScope 在线体验

```
https://www.modelscope.cn/models/Audio/Generative/TTS/summary
```

---

## 五、推理使用

### 5.1 Python 代码推理

```python
from cosyvoice import CosyVoice, CosyVoice2

# ========== 方式1：CosyVoice 2.0（推荐，兼容性好）==========
cosyvoice = CosyVoice2('CosyVoice-300M-SFT')

# 使用预训练音色（无需克隆）
output = cosyvoice.inference_sft(
    text='你好，欢迎使用CosyVoice语音合成系统。',
    spk='default_spk',  # 或 'female_2' / 'male_1'
    stream=False
)
output.postprocess().save('output.wav')


# ========== 方式2：零样本语音克隆 ===========
cosyvoice = CosyVoice2('CosyVoice-300M-ZeroShot')

# 上传参考音频进行克隆
output = cosyvoice.inference_zero_shot(
    text='今天天气真好，我们去公园散步吧。',
    prompt_text='欢迎使用语音助手，请问有什么需要帮助的？',
    prompt_wav='reference.wav',  # 3-30秒参考音频
    stream=False
)
output.postprocess().save('cloned_voice.wav')


# ========== 方式3：流式推理（低延迟）==========
cosyvoice = CosyVoice2('CosyVoice-300M-SFT', stream=True)

for chunk in cosyvoice.inference_sft_stream(
    text='这是一段流式输出的语音内容。',
    spk='female_2'
):
    # chunk 是音频片段，可实时播放
    print(f"收到音频片段: {len(chunk)} bytes")
```

### 5.2 命令行推理

```bash
# 使用预训练音色
cosyvoice-cli \
  --model CosyVoice-300M-SFT \
  --text "你好，今天是2026年3月24日。" \
  --output output.wav

# 零样本克隆
cosyvoice-cli \
  --model CosyVoice-300M-ZeroShot \
  --ref-wav reference.wav \
  --ref-text "欢迎使用语音助手。" \
  --text "今天天气真不错。" \
  --output cloned.wav

# 流式输出
cosyvoice-cli \
  --model CosyVoice-300M-SFT \
  --text "这是一段测试语音。" \
  --stream | aplay
```

### 5.3 WebUI 部署

```bash
# 启动 WebUI（Gradio）
python webui.py --port 8080 --model CosyVoice-300M-SFT

# 或启动流式版本
python webui.py --port 8080 --stream
```

---

## 六、情感与风格控制

### 6.1 情感指令控制

```python
cosyvoice = CosyVoice2('CosyVoice-300M-Instruct')

# 正常语气
output = cosyvoice.inference_instruct(
    text='这个消息非常重要，请务必仔细阅读。',
    instruct_text='normal',  # 正常
)

# 悲伤语气
output = cosyvoice.inference_instruct(
    text='听到这个消息，我感到非常难过。',
    instruct_text='sad',  # 悲伤
)

# 高兴语气
output = cosyvoice.inference_instruct(
    text='太棒了！我们成功了！',
    instruct_text='happy',  # 高兴
)

# 惊讶语气
output = cosyvoice.inference_instruct(
    text='什么？真的吗？',
    instruct_text='surprise',  # 惊讶
)

# 机器人语气
output = cosyvoice.inference_instruct(
    text='系统运行正常，请稍后重试。',
    instruct_text='robot',  # 机器人
)
```

### 6.2 语速控制

```python
# 调整语速（0.5-2.0，1.0为正常）
output = cosyvoice.inference_sft(
    text='这是一段正常语速的语音。',
    spk='female_2',
    speed=1.0  # 0.8=慢速，1.2=快速
)
```

### 6.3 方言控制

```python
# 使用方言音色
cosyvoice = CosyVoice2('CosyVoice-300M-SFT')

# 四川话
output = cosyvoice.inference_sft(
    text='今天天气巴适得很。',
    spk='sichuan'  # 四川话
)

# 粤语
output = cosyvoice.inference_sft(
    text='今日天气好好啊。',
    spk='cantonese'  # 粤语
)

# 天津话
output = cosyvoice.inference_sft(
    text='介事儿可真哏儿啊。',
    spk='tianjin'  # 天津话
)
```

---

## 七、API 服务部署

### FastAPI 服务

```python
# api_server.py
from fastapi import FastAPI, UploadFile, File
from cosyvoice import CosyVoice2
import uvicorn

app = FastAPI(title="CosyVoice API")
cosyvoice = CosyVoice2('CosyVoice-300M-SFT')

@app.post("/tts/sft")
async def tts_sft(text: str, speaker: str = "default_spk"):
    output = cosyvoice.inference_sft(text, speaker)
    output.postprocess().save('/tmp/output.wav')
    return {"audio_url": "/tmp/output.wav"}

@app.post("/tts/clone")
async def tts_clone(
    text: str,
    ref_text: str,
    ref_audio: UploadFile = File(...)
):
    # 保存上传的参考音频
    ref_path = f'/tmp/{ref_audio.filename}'
    with open(ref_path, 'wb') as f:
        f.write(await ref_audio.read())
    
    output = cosyvoice.inference_zero_shot(
        text, ref_text, ref_path
    )
    output_path = f'/tmp/clone_{hash(text)}.wav'
    output.postprocess().save(output_path)
    return {"audio_url": output_path}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
# 启动服务
uvicorn api_server:app --host 0.0.0.0 --port 8000

# 调用示例
curl -X POST "http://localhost:8000/tts/sft?text=你好世界&speaker=female_2"
```

---

## 八、性能基准

| 模型版本 | 参数量 | 说话人相似度 | 首包延迟 | 备注 |
|----------|--------|-------------|----------|------|
| CosyVoice 3.0 Base | 0.5B | 78.0% | 150ms | 最新版本 |
| CosyVoice 3.0 RL | 0.5B | 77.4% | 150ms | 强化学习版 |
| CosyVoice 2.0 | 300M | ~75% | 300ms | 稳定版 |

> 对比参考：人类录音的说话人相似度基准为 75.5%

---

## 九、与 GPT-SoVITS 对比

| 维度 | CosyVoice 3.0 | GPT-SoVITS V4 |
|------|---------------|----------------|
| **克隆最低样本** | 3秒 | 5秒 |
| **流式延迟** | **150ms** | 无流式支持 |
| **情感控制** | ✅ 丰富 | 基础 |
| **中文方言** | **18种** | 仅粤语 |
| **中文克隆质量** | 78% | **90%+（微调后）** |
| **商用许可** | ✅ Apache-2.0 | MIT |
| **推理速度（非流式）** | 慢 | 快 |
| **长文本处理** | ✅ 流式支持 | 需分段 |

**选择建议**：
- 🎯 **实时交互** → CosyVoice 3.0
- 🎯 **中文克隆质量** → GPT-SoVITS V4（微调后）
- 🎯 **快速零样本** → 两者皆可（CosyVoice 3秒 vs GPT-SoVITS 5秒）

---

## 十、常见问题解决

| 问题 | 解决方案 |
|------|----------|
| 首次加载模型很慢 | 自动下载模型，可预先下载到本地 |
| 流式输出有杂音 | 检查音频驱动，确保采样率匹配 |
| 克隆音色不像 | 增加参考音频时长至30秒以上 |
| 方言发音不标准 | 使用对应方言的预训练模型 |
| 显存不足 | 切换到 0.5B 轻量版模型 |
| 中文发音错误 | 使用文本归一化功能 |
| API 响应慢 | 启用流式输出，减少首包等待 |
