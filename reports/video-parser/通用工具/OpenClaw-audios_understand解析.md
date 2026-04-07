# 通用工具 - OpenClaw audios_understand 音频分析

## 核心工具/API

- **audios_understand**：OpenClaw 内置音频理解工具
  - 自动语音转文字 + 内容分析
  - 支持本地音频文件和 URL
  - 多提供商：OpenAI Whisper / Groq / Deepgram / Google Gemini
  - 支持最多 10 个音频并行分析
  - 可设置 prompt 指定分析维度

## 步骤流程

```
1. 传入音频文件或 URL
   audios_understand([
     { file: "/path/to/audio.mp3", prompt: "请转录并总结音频内容" }
   ])

2. 自动选择提供商（按配置优先级）
   OpenAI Whisper API → Groq → Deepgram → Google Gemini

3. 返回转录文本 + 分析结果
```

## 配置示例（openclaw.json）

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { provider: "groq", model: "whisper-large-v3-turbo" },
          { provider: "deepgram", model: "nova-3" }
        ]
      }
    }
  }
}
```

## 适用场景

- ✅ **播客 / 访谈音频** → 转录 + 要点总结
- ✅ **会议录音** → 提取决策和行动项
- ✅ **教学音频** → 内容结构化
- ✅ **音乐分析** → 歌词识别、风格判断
- ✅ **视频音轨** → 配合 FFmpeg 提取音轨后分析

## 避坑指南

- ⚠️ **maxBytes 限制**：默认 20MB，大文件需压缩或调整配置
- ⚠️ **无字幕视频**：先 ffmpeg 提取音频，再 audios_understand
- ⚠️ **多语言音频**：明确指定语言，避免自动检测错误
- ⚠️ **提供商选择**：Groq 免费额度高，优先配置

## 参考链接

- [OpenClaw 媒体理解文档](https://docs.openclaw.ai/zh-CN/nodes/media-understanding)
- [Whisper API Skill](/app/openclaw/skills/openai-whisper-api/SKILL.md)
