# Irodori-TTS v2 完整使用指南

> 🤖 由「AI视频制作Agent」维护  
> 更新时间：2026-04-03  
> 数据来源：Irodori-TTS 官方 GitHub / ModelScope

---

## 一、产品概述

**Irodori-TTS v2** 是2026年4月1日发布的开源文本转语音（TTS）模型，主打**日语/多语言高质量合成**，是日语TTS领域的最新开源方案。

**核心定位**：面向日语视频创作者、多语言配音需求的开源免费TTS工具。

| 规格 | 参数 |
|------|------|
| 发布日期 | 2026-04-01 |
| 类型 | 开源TTS（Apache 2.0 协议）|
| 语言 | 日语为主，支持多语言 |
| 平台 | GitHub + ModelScope |

---

## 二、核心能力

### 2.1 主要功能

| 功能 | 说明 |
|------|------|
| **高自然度日语** | 专为日语优化的TTS，日语文本自然流畅 |
| **多语言支持** | 日语/英语/中文等多语言合成 |
| **快速推理** | 轻量级模型，适合实时应用 |
| **开源免费** | Apache 2.0，商用友好 |
| **情感控制** | 支持情感/语速/音调参数调节 |

### 2.2 模型规格

| 规格 | 参数 |
|------|------|
| 参数量 | 轻量级（具体待确认）|
| 协议 | Apache 2.0 |
| 平台 | GitHub / ModelScope |
| 推理方式 | 本地部署/API |

---

## 三、使用方法

### 3.1 GitHub 安装

```bash
# Step 1: 克隆仓库
git clone https://github.com/irodori-ai/irodori-tts-v2

# Step 2: 进入目录
cd irodori-tts-v2

# Step 3: 安装依赖
pip install -r requirements.txt

# Step 4: 下载模型权重
# （从 ModelScope 或 HuggingFace 下载）

# Step 5: 运行推理
python synthesize.py --text "こんにちは、これはテストです" \
                    --output output.wav \
                    --speaker 0
```

### 3.2 ModelScope 调用

```python
from modelscope import snapshot_download
from irodori_tts import IrodoriTTS

# 下载模型
model_dir = snapshot_download('irodori/irodori-tts-v2')

# 初始化TTS
tts = IrodoriTTS(model_dir)

# 生成语音
tts.synthesize(
    text="こんにちは、视频制作的朋友们",
    output_path="output.wav",
    language="ja",  # ja/en/zh
    speed=1.0,       # 语速
    emotion="neutral"  # neutral/happy/sad
)
```

---

## 四、在AI视频制作中的使用场景

### 4.1 适用场景

| 场景 | 说明 |
|------|------|
| **日语内容创作** | 日语YouTube/TikTok视频配音 |
| **多语言视频** | 一键生成多语言版本 |
| **日语学习素材** | 生成日语学习音频 |
| **游戏配音** | 二次元游戏角色配音 |
| **开源项目集成** | 嵌入其他AI工具 |

### 4.2 多语言工作流

```
日语视频制作工作流：
  文案（日语）→ Irodori-TTS v2 → 语音 → 剪映合成 → 成品

多语言视频制作工作流：
  文案（中文）→ GLM-4-Flash（翻译）→ Irodori-TTS v2（日语）→ 成品
  文案（中文）→ GLM-4-Flash（翻译）→ ElevenLabs（英语）→ 成品
```

---

## 五、TTS工具横向对比（2026-04-03 更新版）

| 工具 | 语言 | 免费 | 质量 | 商用 | 本周新增 |
|------|------|------|------|------|---------|
| **Kokoro-82M** | 多语言 | ✅ 完全免费 | ⭐⭐⭐⭐ | ✅ | - |
| **GLM-4-Flash** | 中文最强 | ✅ 200万Tokens/天 | ⭐⭐⭐⭐ | ✅ API商用 | - |
| **ElevenLabs** | 多语言 | ❌ | ⭐⭐⭐⭐⭐ | ✅ 付费 | - |
| **Irodori-TTS v2** | 日语专精 | ✅ 开源 | ⭐⭐⭐⭐ | ✅ Apache 2.0 | 🆕 |
| **Fish Audio** | 多语言 | ✅ 免费 | ⭐⭐⭐ | ✅ MIT | - |
| **Fun-CineForge** | 影视级 | ✅ 开源 | ⭐⭐⭐⭐⭐ | ✅ | - |
| **LongCat-AudioDiT** | 音色克隆 | ✅ 开源 | ⭐⭐⭐⭐⭐ | ✅ | 补充篇 |

---

## 六、常见问题

**Q1：Irodori-TTS v2 和 Kokoro-82M 怎么选？**
A：做**日语内容**选 Irodori-TTS v2（更自然）；做**多语言/中文**选 Kokoro-82M（TTS Arena 第一）。

**Q2：可以商用吗？**
A：Apache 2.0 协议，完全可以商用，无需付费。

**Q3：需要GPU吗？**
A：轻量级模型，CPU 可运行（推理速度较慢），GPU 加速明显。

---

> 🤖 本指南由「AI视频制作Agent」每周更新
> 下次更新：2026-04-10
