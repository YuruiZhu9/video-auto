# CosyVoice 3.0 — 阿里通义语音旗舰方案

> 🤖 更新于 2026-03-27 | FunAudioLLM团队（阿里通义实验室）| 发布于 2025-12-15

---

## 一、概述

**Fun-CosyVoice 3.0** 是阿里通义实验室（SpeechLab@Tongyi）于 **2025年12月15日** 发布的第三代大规模语音生成模型，基于大语言模型（LLM）架构，在内容一致性、说话人相似度、韵律自然度三项核心指标上全面超越前代（CosyVoice 2.0）。

CosyVoice 3.0 是当前**最成熟、文档最完善、生态最完整**的开源多语言TTS方案，由阿里官方持续维护。

---

## 二、核心升级（相比 CosyVoice 2.0）

| 指标 | CosyVoice 2.0 | CosyVoice 3.0 |
|------|--------------|----------------|
| **训练数据** | 10,000 小时 | **1,000,000 小时**（百倍增长）|
| **模型参数** | 0.5B | 0.5B（推荐）/ 1.5B（完整）|
| **语言数量** | 有限 | **9种主流语言 + 18+种中文方言** |
| **中文方言** | 不支持 | 广东话、东北话、天津话、四川话、上海话等 |
| **发音修补** | 基础 | **拼音/音素级精准修补** |
| **跨语言克隆** | 有限 | **中文参考音 → 英文合成**（大幅优化）|
| **流式延迟** | 流式 | **低至 150ms** |

### 新增核心技术能力

1. **Pronunciation Inpainting（发音修补）**：通过拼音/音素标注精准修复多音字、生僻字读音
2. **Instruct Commands**：以自然语言指令控制语速、情感、音量
3. **Bi-Streaming**：文本输入流式 + 音频输出流式，延迟低至 150ms
4. **Emotion Control**：支持 Happy / Sad / Fearful / Angry / Surprised 五种情感
5. **Dialect Control**：18+ 中文方言/口音独立控制
6. **Differentiable Reward Model**：可用于后训练优化（支持 CosyVoice 3 及其他 LLM-TTS 模型）

---

## 三、支持的模型版本

| 模型 | 说明 | 推荐度 |
|------|------|--------|
| **Fun-CosyVoice3-0.5B-2512** | 基准模型（生产推荐）| 🥇 首选 |
| **Fun-CosyVoice3-0.5B-2512_RL** | 强化学习优化版，WER更低 | ⭐ 推荐 |
| CosyVoice2-0.5B | 前代模型（仍有价值）| 🥉 |
| CosyVoice-300M / -SFT / -Instruct | 早期版本 | 不推荐 |

---

## 四、支持语言与方言

### 9 种主流语言
- 🇨🇳 中文（普通话）、🇬🇧 英语、🇯🇵 日语、🇰🇷 韩语
- 🇩🇪 德语、🇪🇸 西班牙语、🇫🇷 法语、🇮🇹 意大利语、🇷🇺 俄语

### 18+ 种中文方言/口音
广东话、闽南语、四川话、东北话、上海话、天津话、陕西话（两种）、山东话、宁夏话、甘肃话 等

---

## 五、性能评测（官方 CV3-Eval）

| 模型 | 开源 | 规模 | 中文CER ↓ | 中文相似度 ↑ | 英文WER ↓ | 英文相似度 ↑ |
|------|------|------|-----------|-------------|-----------|-------------|
| **Fun-CosyVoice3-0.5B-2512** | ✅ | 0.5B | **1.21%** | **78.0** | **2.24%** | **71.8** |
| Fun-CosyVoice3-0.5B-2512_RL | ✅ | 0.5B | 0.81% | 77.4 | 1.68% | 69.5 |
| CosyVoice2 | ✅ | 0.5B | 1.45% | 75.7 | 2.57% | 65.9 |

> CosyVoice 3.0 在中文相似度（78.0）和英文相似度（71.8）上均显著超越 CosyVoice 2.0。

---

## 六、快速开始

### 1. 环境配置

```bash
# 克隆仓库（含子模块）
git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice
git submodule update --init --recursive

# 创建环境
conda create -n cosyvoice -y python=3.10
conda activate cosyvoice
pip install -r requirements.txt \
  -i https://mirrors.aliyun.com/pypi/simple/ \
  --trusted-host mirrors.aliyun.com

# Linux 系统依赖
sudo apt-get install sox libsox-dev
```

### 2. 下载模型（ModelScope，推荐国内用户）

```python
from modelscope import snapshot_download
import os
os.makedirs('pretrained_models', exist_ok=True)

# CosyVoice 3.0 基准模型
snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B-2512',
                  local_dir='pretrained_models/Fun-CosyVoice3-0.5B')

# CosyVoice 2.0（可选，兼容旧用法）
snapshot_download('iic/CosyVoice2-0.5B',
                  local_dir='pretrained_models/CosyVoice2-0.5B')

# TTS 前端包（更好的文本规范化）
snapshot_download('iic/CosyVoice-ttsfrd',
                  local_dir='pretrained_models/CosyVoice-ttsfrd')
```

### 3. 下载模型（HuggingFace，海外用户）

```python
from huggingface_hub import snapshot_download
snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B-2512',
                  local_dir='pretrained_models/Fun-CosyVoice3-0.5B')
```

### 4. 零样本克隆推理

```python
import torch
from cosyvoice import CosyVoice

cosyvoice = CosyVoice('pretrained_models/Fun-CosyVoice3-0.5B')

# 零样本克隆（3-10秒参考音频）
output = cosyvoice.inference_zero_shot(
    text='今天天气真不错，适合出门散步。',
    prompt_text='这是参考音频的文字内容',
    prompt_wav='ref_voice.wav'
)
output.save('result.wav')

# 带情感控制
output = cosyvoice.inference_instruct(
    text='这个消息真是太棒了！',
    instruct_text='Happy, fast',
    prompt_wav='ref_voice.wav'
)
output.save('happy_output.wav')

# 中文方言（东北话）
output = cosyvoice.inference_instruct(
    text='你吃了吗？',
    instruct_text='东北话',
    prompt_wav='ref_voice.wav'
)
output.save('dongbei_output.wav')

# 发音修补（解决多音字）
output = cosyvoice.inference_zero_shot(
    text='长大了[journal]要当医生。',
    prompt_text='小时候想当医生',
    prompt_wav='ref_voice.wav'
)
output.save('fixed_output.wav')
```

### 5. WebUI 交互界面

```bash
python3 webui.py --port 50000 --model_dir pretrained_models/Fun-CosyVoice3-0.5B
# 访问 http://localhost:50000
```

### 6. vLLM 加速（可选）

```bash
# 创建独立环境
conda create -n cosyvoice_vllm --clone cosyvoice
conda activate cosyvoice_vllm

# 安装 vLLM
pip install vllm==v0.11.0 transformers==4.57.1 numpy==1.26.4

# 运行加速推理
python vllm_example.py
```

### 7. Docker 部署

```bash
cd runtime/python
docker build -t cosyvoice:v1.0 .

# gRPC 服务
docker run -d --runtime=nvidia -p 50000:50000 cosyvoice:v1.0 \
  /bin/bash -c "cd /opt/CosyVoice/CosyVoice/runtime/python/grpc && \
  python3 server.py --port 50000 --max_conc 4 --model_dir pretrained_models/Fun-CosyVoice3-0.5B && \
  sleep infinity"

# FastAPI 服务
docker run -d --runtime=nvidia -p 50000:50000 cosyvoice:v1.0 \
  /bin/bash -c "cd /opt/CosyVoice/CosyVoice/runtime/python/fastapi && \
  python3 server.py --port 50000 --model_dir pretrained_models/Fun-CosyVoice3-0.5B && \
  sleep infinity"
```

---

## 七、Instruct 指令控制示例

CosyVoice 3.0 支持通过自然语言指令精细控制语音输出：

```python
# 语速控制
instruct_text = 'speak slowly'
instruct_text = 'talk faster'

# 情感控制
instruct_text = 'happy and excited'
instruct_text = 'sad and slow'
instruct_text = 'angry'

# 音量控制
instruct_text = 'quiet and soft'
instruct_text = 'loud'

# 风格控制
instruct_text = 'whisper'  # 轻声
instruct_text = 'reading news'  # 新闻播报
instruct_text = 'narrating a story'  # 讲故事

# 组合控制
instruct_text = 'happy, fast, loud'
```

---

## 八、常见问题

| 问题 | 解决方案 |
|------|----------|
| 显存不足（OOM） | 使用 0.5B 模型而非 1.5B；设置 `CUDA_VISIBLE_DEVICES` 限制并发 |
| 英文发音不准确 | 使用发音修补：`word[PHONEMES]` 或切换英文模型 |
| 中文方言效果不佳 | 确保参考音频为对应方言，或使用 `instruct_text='xxx话'` |
| 流式推理延迟高 | 确认使用 3.0 版本而非 2.0；开启 vLLM 加速 |
| 多音字读音错误 | 使用拼音标注：`文字[pīnyīn]` 精准控制 |
| 音色相似度不够 | 增加参考音频时长（3秒→10秒）；使用 RL 版模型 |

---

## 九、与 Qwen3-TTS 的对比

| 特性 | CosyVoice 3.0 | Qwen3-TTS |
|------|---------------|-----------|
| **发布方** | 阿里通义实验室 | 阿里 Qwen 团队 |
| **发布时间** | 2025-12 | 2026-01 |
| **模型规模** | 0.5B / 1.5B | 0.6B / 1.7B |
| **克隆速度** | 3-10秒参考音频 | **3秒参考音频** |
| **中文方言** | **18+ 种** | 不支持 |
| **情感控制** | 5种情感 + Instruct | 自然语言描述 |
| **发音修补** | ✅ 拼音/音素级 | 有限 |
| **许可证** | Apache 2.0 | Apache 2.0 |
| **成熟度** | ⭐⭐⭐⭐⭐ 经过大规模生产验证 | ⭐⭐⭐⭐ 2026年新发布 |

**选型建议：**
- 追求中文方言和情感控制 → **CosyVoice 3.0**
- 追求最新技术 + 快速上手 → **Qwen3-TTS**
- 两者可互补使用

---

## 十、资源链接

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/FunAudioLLM/CosyVoice |
| 官方演示 | https://funaudiollm.github.io/cosyvoice3/ |
| 技术论文 | https://arxiv.org/abs/2505.17589 |
| HuggingFace | https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512 |
| ModelScope | https://www.modelscope.cn/models/FunAudioLLM/Fun-CosyVoice3-0.5B-2512 |
| 评测集 | https://github.com/FunAudioLLM/CV3-Eval |

---

*CosyVoice 3.0 由 FunAudioLLM 团队（阿里通义实验室）开发并开源，Apache 2.0 许可证，免费商用。*
