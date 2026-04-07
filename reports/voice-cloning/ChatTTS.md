# ChatTTS — 对话式语音合成（非克隆工具）

> ⚠️ **重要提醒：** ChatTTS **不支持声音克隆**。它是一款高质量对话式 TTS 工具，通过随机采样生成不同音色。声音克隆请参考 GPT-SoVITS / Fish Speech / F5-TTS。

---

## 基本信息

| 项目 | 信息 |
|------|------|
| GitHub | https://github.com/2noise/ChatTTS |
| Stars | ⭐ **38.4k** |
| 许可证 | AGPL-3.0（代码）+ CC BY-NC 4.0（模型） |
| 中文支持 | ✅ 极佳（中英双语） |
| 声音克隆 | ❌ 不支持 |

---

## 核心功能

1. **对话式 TTS**：专为对话场景设计，适用于 LLM 助手、有声对话
2. **细粒度情感控制**：支持笑声 `[laugh]`、停顿 `[uv_break]`、`[lbreak]`、语气变化
3. **多说话人支持**：内置多说话人模型，支持交互式对话
4. **超越开源 TTS 韵律**：在韵律自然度上优于大多数开源 TTS 模型

---

## 声音样本准备要求

> ChatTTS **无需准备声音样本**（不支持克隆），直接输入文本即可生成语音。

| 项目 | 要求 |
|------|------|
| 输入 | 纯文本（中英文混合） |
| 音频格式 | 直接生成 WAV PCM |
| 控制符 | `[laugh]`（笑声）、`[uv_break]`（停顿）、`[lbreak]`（换行停顿） |

---

## 安装与使用

### 安装
```bash
pip install ChatTTS
```

### 基础使用
```python
import ChatTTS

chat = ChatTTS.Chat()
chat.load()

# 基础生成（随机音色）
audio = chat.generate("你好，我是一个AI助手。有什么可以帮助你的吗？")
audio.save("output.wav")
```

### 带情感控制
```python
# 带笑声和停顿的生成
audio = chat.generate(
    "[laugh] 太好了！今天天气真不错。[uv_break] 你今天有什么计划吗？"
)
audio.save("emotional_output.wav")
```

### 采样指定说话人
```python
# 采样一个随机说话人
chat.sample_random_speaker()

# 生成
audio = chat.generate("这是一段使用随机说话人的语音。")
```

### WebUI
```bash
python webui.py
# 浏览器打开使用
```

---

## 常见问题

| 问题 | 解答 |
|------|------|
| 能克隆特定人的声音吗？ | **不能**。ChatTTS 通过随机采样生成不同音色，不支持指定音色克隆 |
| 能商用吗？ | 模型权重为 CC BY-NC 4.0，**不可商用** |
| 音质有噪声？ | 4万小时开源模型有意添加了高频噪声以防滥用；可用内部模型（需申请） |
| 推理速度？ | RTX 4090 上约 0.5x 实时（50字约 22-30 秒） |

---

## 与其他克隆工具对比

| 场景 | 推荐工具 |
|------|---------|
| 需要克隆**特定人声** | GPT-SoVITS / Fish Speech S1 |
| 需要**对话情感语音**（不克隆） | ChatTTS ✅ |
| 需要**唱歌/变声** | RVC |
| 需要**免训练合成** | F5-TTS / Fish Speech S1 |

---

## 总结

ChatTTS 是目前**对话场景下最自然的中文 TTS 开源工具**，但它 **≠ 声音克隆工具**。

- ✅ 对话情感丰富、音质好、中英文支持佳
- ❌ 不能克隆特定音色，不可商用

**声音克隆需求 → 使用 GPT-SoVITS 或 Fish Speech S1**
