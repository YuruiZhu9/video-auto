# OpenVoice 完整部署与使用指南

> MIT + MyShell 开源 | 即时语音克隆 | ⚠️ 已停止活跃维护

---

## 一、项目概览

OpenVoice 由 MIT 与 MyShell.ai 联合开发，于 2024 年初发布，是最早期的即时语音克隆方案之一。支持**准确的音色克隆**、**灵活的语音风格控制**和**零样本跨语言克隆**。

> ⚠️ **重要提醒**：OpenVoice 项目已于 2024 年 3 月停止活跃维护（GitHub 最后更新 Mar 2024）。建议作为参考或临时急用，不建议作为长期主力方案。

- **GitHub**：https://github.com/myshell-ai/OpenVoice
- **星标**：约 11k ⭐
- **许可证**：MIT（可商用）
- **维护状态**：⚠️ 已停止更新

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| **即时克隆** | 短音频即可克隆 |
| **风格控制** | 可控制情感、口音、节奏、停顿 |
| **跨语言** | 零样本跨语言合成 |
| **商用许可** | MIT |

---

## 三、声音样本准备

### 音频格式要求

| 参数 | 推荐值 |
|------|--------|
| **格式** | WAV / MP3 |
| **采样率** | 16kHz+ |
| **时长** | 10秒以上效果更好 |
| **音质** | 清晰无噪音 |

### 录音内容建议

```
✅ 推荐：干净的人声，说话内容清晰
✅ 时长：10秒 - 5分钟
✅ 内容：日常对话或朗读

❌ 避免：背景音乐、多人对话、回声严重
```

---

## 四、安装部署

### 方案1：PyPI 安装

```bash
pip install openvoice
```

### 方案2：GitHub 源码安装

```bash
git clone https://github.com/myshell-ai/OpenVoice.git
cd OpenVoice
pip install -e .
```

### 方案3：Docker

```bash
# 使用预构建镜像
docker pull myshell/openvoice
docker run --gpus all -p 8080:8080 myshell/openvoice
```

---

## 五、推理使用

### 5.1 Python 代码推理

```python
from openvoice import OpenVoice

# 初始化
openvoice = OpenVoice()

# ========== 即时克隆 ==========
output = openvoice.instant_clone(
    ref_audio="reference.wav",  # 参考音频
    text="要生成的文本内容。"  # 目标文本
)
output.save("cloned.wav")

# ========== 风格控制 ==========
output = openvoice.generate(
    ref_audio="reference.wav",
    text="这是一段带有情感的语音。",
    style={
        "emotion": "happy",     # happy/sad/neutral
        "pace": 1.0,            # 语速（0.5 - 2.0）
        "pitch": 0,            # 音调调整（-10 - 10）
    }
)
output.save("styled.wav")

# ========== 跨语言克隆 ==========
output = openvoice.cross_lingual_clone(
    ref_audio="english_ref.wav",  # 英文参考
    text="这是一段中文文本。"       # 中文目标
)
output.save("cross_lingual.wav")
```

### 5.2 命令行使用

```bash
# 即时克隆
openvoice clone \
  --ref reference.wav \
  --text "要生成的文本内容" \
  --output output.wav

# 带风格控制
openvoice generate \
  --ref reference.wav \
  --text "带有情感的语音内容" \
  --emotion happy \
  --speed 1.2 \
  --output output.wav
```

---

## 六、WebUI 使用

```bash
# 启动 WebUI
python webui.py

# 访问
# http://localhost:7860
```

---

## 七、已知问题

| 问题 | 状态 | 解决方案 |
|------|------|----------|
| 训练效果不如 GPT-SoVITS | ⚠️ 已知 | 建议使用 GPT-SoVITS |
| V2 效果不如 V1 | ⚠️ 已知 | 使用 V1 版本 |
| 项目已停止维护 | ⚠️ 确认 | 考虑迁移其他方案 |
| 跨语言质量不稳定 | ⚠️ 常见 | 增加参考音频时长 |

---

## 八、替代方案推荐

由于 OpenVoice 已停止维护，建议使用以下替代方案：

| 方案 | 优势 | 适用场景 |
|------|------|----------|
| **GPT-SoVITS V4** | 中文最强，持续更新 | 中文克隆首选 |
| **CosyVoice 3.0** | 流式低延迟，商用友好 | 实时交互 |
| **F5-TTS** | 推理最快 | 直播配音 |

---

## 九、快速参考

```python
# OpenVoice 最简用法（仅作参考）
from openvoice import OpenVoice

ov = OpenVoice()
# 即时克隆（最简单的用法）
audio = ov.instant_clone(
    ref_audio="your_reference.wav",
    text="Hello, this is a cloned voice."
)
audio.save("output.wav")
```
