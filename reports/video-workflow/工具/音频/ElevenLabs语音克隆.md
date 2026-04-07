# ElevenLabs 语音克隆与合成指南

> 更新时间：2026-03-08

## 工具概述

**ElevenLabs** 是领先的AI语音合成平台，支持语音克隆和多语言TTS。

- **网址**：elevenlabs.io
- **平台**：Web端 + API
- **免费额度**：每月约10000字符

## 注册登录

1. 访问 elevenlabs.io
2. 点击 "Sign Up Free"
3. 选择登录方式：
   - Google 账号
   - Apple ID邮箱注册
4
   - . 验证邮箱后即可使用

## 核心功能

### 1. Voice Clone（语音克隆）

**使用条件**：
- 需要上传至少1分钟的清晰音频
- 支持 mp3/wav 格式
- 音频中无背景噪音

**操作步骤**：
1. 进入 "Voice Lab" → "Add Voice"
2. 选择 "Professional Voice Cloning"
3. 上传音频样本（建议5分钟以上）
4. 等待模型训练完成（通常几小时）
5. 生成专属声音ID

**注意**：付费版功能，免费版有限制

### 2. Text to Speech（TTS）

**操作步骤**：
1. 进入 "Text to Speech"
2. 选择已克隆的声音或预设声音
3. 输入文本（支持中文）
4. 调整参数：
   - Stability（稳定性）：0-1
   - Similarity（相似度）：0-1
   - Style（风格化）：0-1
   - Speaker Boost（人声增强）
5. 生成并下载

**参数建议**：
| 场景 | Stability | Similarity | Style |
|------|------------|------------|-------|
| 叙述 | 0.5 | 0.75 | 0 |
| 对话 | 0.4 | 0.8 | 0.2 |
| 情感 | 0.3 | 0.85 | 0.5 |

### 3. Projects（项目）

- 管理和组织多个语音项目
- 支持长文本分段生成

## API 调用（进阶）

```python
import requests

url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": "YOUR_API_KEY"
}

data = {
    "text": "要转换的文本",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

response = requests.post(url, json=data, headers=headers)
```

## 适用场景

- AI视频配音
- 有声书制作
- 语音助手
- 播客录制
- 多语言内容本地化

## 费用说明

| 计划 | 价格 | 字符/月 |
|------|------|----------|
| Free | $0 | 10,000 |
| Starter | $5 | 30,000 |
| Creator | $22 | 100,000 |
| Business | 定制 | 无限制 |

## 替代方案

- **GPT-4o Voice**：OpenAI原生语音
- **Azure TTS**：微软语音服务
- **Cloudflare Stream**：视频+语音解决方案

## 常见问题

**Q：克隆需要多长时间？**
A：通常1-24小时，取决于服务器负载

**Q：支持哪些语言？**
A：支持29种语言，包括中文

**Q：商用是否需要授权？**
A：付费版可商用，但需遵守使用政策

**Q：语音像AI怎么办？**
A：调整Style参数，增加情感表达
