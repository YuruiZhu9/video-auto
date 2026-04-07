# GPT-SoVITS V4 完整部署与使用指南

> 国产最强开源语音克隆 | GitHub ⭐53.2k | MIT许可证

---

## 一、项目概览

GPT-SoVITS 由 RVC-Boss 团队开发，融合 GPT 模型的语言理解能力与 SoVITS 的声学特征提取，实现**极少量样本的高质量语音克隆**。

- **最新版本**：V4（2025年2月发布）
- **GitHub**：https://github.com/RVC-Boss/GPT-SoVITS
- **星标**：53.2k ⭐ | Fork：5.8k
- **许可证**：MIT（可商用）

---

## 二、声音样本准备

### 音频格式要求

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| **格式** | WAV（推荐）或 MP3 | 无损格式效果更好 |
| **采样率** | 16000 Hz 或 32000 Hz | 必须16kHz以上 |
| **时长** | 零样本：5-30秒<br>微调：1-10分钟 | 越多质量越高 |
| **音质** | 128kbps+ | 避免压缩损失 |
| **声道** | 单声道（mono） | 双声道需转换 |

### 录音环境要求

- ✅ **安静房间**：无背景音乐、空调声、窗外噪音
- ✅ **无混响**： closetclothes wardrobe 或软装空间最佳
- ✅ **距离麦克风15-30cm**：避免喷麦/过远
- ✅ **语气自然**：正常说话语气，避免刻意表演

### 录音内容建议

**零样本克隆（5-30秒）**：
```
推荐内容：「今天天气真好，我们去公园散步吧。」
要求：覆盖尽量多的音素（a/o/e/i/u/b/p/m/f等）
避免：重复词语太多、内容太短（<5秒）
```

**微调训练（1-10分钟）**：
```
推荐内容：故事叙述 + 情感变化 + 多音素覆盖
样例：新闻播报、讲故事、朗读文章
要求：涵盖不同语气（陈述/疑问/感叹）
```

### 预处理命令（ffmpeg）

```bash
# 转换为单声道 16kHz WAV
ffmpeg -i input.mp3 -ar 16000 -ac 1 -acodec pcm_s16le output.wav

# 批量转换目录下所有音频
for f in *.mp3; do
  ffmpeg -i "$f" -ar 16000 -ac 1 -acodec pcm_s16le "${f%.mp3}.wav"
done
```

---

## 三、安装部署

### 方案1：Windows 一键整合包（推荐新手）

1. 下载整合包：`GPT-SoVITS-v3lora-20250228.7z`
2. 解压到任意目录
3. 双击运行 `_go-webui.bat`
4. 自动打开浏览器 WebUI

### 方案2：Anaconda 手动安装

```bash
# 创建虚拟环境
conda create -n GPTSoVits python=3.10
conda activate GPTSoVits

# Windows 安装
pwsh -ExecutionPolicy Bypass -File install.ps1 --Device cuda --Source . --DownloadUVR5

# Linux/macOS 安装
bash install.sh --device cuda --source . --download-uvr5

# 启动 WebUI
python webui.py v1  # 使用V1版本（显存占用更小）
python webui.py     # 默认V2版本
```

### 方案3：Docker 部署

```bash
# 构建镜像（CUDA 12.6 或 12.8）
bash docker_build.sh --cuda 12.6

# 运行服务
docker compose run --service-ports gpt-sovits

# 或手动运行
docker run --gpus all -p 7860:7860 \
  -v $(pwd)/output:/app/output \
  gpt-sovits-cu126
```

### 方案4：Google Colab（免费云端）

```bash
# 训练：打开 Colab-WebUI.ipynb
# 推理：打开 Colab-Inference.ipynb
# 地址：https://github.com/RVC-Boss/GPT-SoVITS/blob/main/Colab-WebUI.ipynb
```

### 环境依赖

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| **GPU** | 6GB 显存 | RTX 3060+ (12GB) |
| **内存** | 8GB RAM | 16GB+ |
| **Python** | 3.9+ | 3.10 |
| **PyTorch** | 2.0+ | 2.5.1 |
| **CUDA** | 11.8+ | 12.4/12.6 |

---

## 四、训练步骤

### 4.1 数据预处理

1. 打开 WebUI，进入 **「1-GPT-SoVITS-Training」** 标签
2. **音频切片**：上传原始音频，设置切片时长（建议5-15秒）
3. **ASR识别**：启用中文ASR自动标注（需要模型下载）
4. **文本标注修正**：人工检查/修正自动标注结果

### 4.2 训练模型

```yaml
# 训练参数建议（WebUI界面设置）

# SoVITS 训练
batch_size: 8          # 显存不足时减小
gradient_accumulation: 1
epochs: 15-30           # V4建议15-20 epoch
learning_rate: 1e-4
checkpoint_interval: 5  # 每5轮保存

# GPT 训练
epochs: 10-20
warmup_steps: 500
max_text_len: 2048
```

### 4.3 训练监控

```bash
# 查看训练日志
tail -f logs/gpt-sovits/training.log

# TensorBoard 监控
tensorboard --logdir=logs/
# 访问 http://localhost:6006
```

---

## 五、推理使用

### 5.1 WebUI 推理

1. 进入 **「3-GPT-SoVITS-Inference」** 标签
2. 加载训练好的模型（.pth 文件）
3. 上传参考音频（3-10秒）
4. 输入文本，点击生成

### 5.2 命令行/代码推理

```python
# inference.py
import torch
from GPT_SoVITS inference import GPT_SoVITS_Inference

# 初始化
gpt_sovits = GPT_SoVITS_Inference(
    gpt_model_path="logs/gpt-largev3_e10.ckpt",
    sovits_model_path="logs/sovitsv3_e15.ckpt"
)

# 零样本推理（无需微调）
audio = gpt_sovits.generate(
    ref_audio="reference.wav",      # 参考音频路径
    ref_text="今天天气真好。",        # 参考音频对应文本
    target_text="欢迎收听今天的新闻。", # 要生成的文本
    top_k: 5,
    top_p: 1.0,
    temperature: 0.7
)

# 保存音频
gpt_sovits.save(audio, "output.wav")
```

### 5.3 API 服务部署

```python
# api.py - FastAPI 服务
from fastapi import FastAPI
from GPT_SoVITS inference import GPT_SoVITS_Inference
import base64

app = FastAPI()
gpt_sovits = GPT_SoVITS_Inference(
    gpt_model_path="logs/gpt-largev3_e10.ckpt",
    sovits_model_path="logs/sovitsv3_e15.ckpt"
)

@app.post("/tts")
async def text_to_speech(ref_audio: str, ref_text: str, text: str):
    audio = gpt_sovits.generate(ref_audio, ref_text, text)
    return {"audio": base64.b64encode(audio).decode()}
```

```bash
# 启动API服务
uvicorn api:app --host 0.0.0.0 --port 8000
```

---

## 六、性能基准

| 设备 | RTF（实时率） | 4分钟音频耗时 | 备注 |
|------|---------------|---------------|------|
| RTX 4090 | **0.014** | ~3.4秒 | 最高效 |
| RTX 4060Ti | **0.028** | ~7秒 | 主流推荐 |
| RTX 3060 | ~0.05 | ~12秒 | 入门够用 |
| M4 Apple Silicon | 0.526 | ~2分钟 | 勉强可用 |
| CPU (i7) | ~2.0 | ~8分钟 | 仅测试用 |

**RTF 解释**：RTF = 推理时间 / 音频时长。RTF=0.014 表示1秒音频只需0.014秒推理。

---

## 七、常见问题解决

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 音色不自然/机械感 | 训练数据太少或质量差 | 增加音频样本至5分钟以上，使用高质量音频 |
| 推理显存不足（OOM） | batch_size 太大 | 减小 batch_size 到 4 或 2，或切换 V1 版本 |
| 推理速度慢 | GPU 利用率低 | 确认 CUDA 版本匹配，安装 cudnn |
| 重复复读 | 模型过拟合或参数问题 | 减小学习率，增加训练数据 |
| 声音闷/不清晰 | V3原生输出24kHz导致 | 升级到 V4 版本（原生48kHz） |
| 中文发音错误 | ASR标注错误 | 人工修正标注文本 |
| 英文发音奇怪 | 训练数据缺少英文 | 混入英文音频样本 |

---

## 八、V4 相对 V3 的改进

1. ✅ **修复金属伪影**：V3因非整数倍上采样产生金属噪音，V4彻底修复
2. ✅ **原生48kHz输出**：V3仅24kHz，V4音质大幅提升
3. ✅ **GPT模型更稳定**：重复和遗漏问题减少
4. ✅ **情感表达更丰富**：V4的情感复刻能力更强

> 💡 **建议**：新用户直接使用 V4，老用户从 V3 迁移只需替换模型文件。
