# 技术教程类 - Whisper 语音转文字方法

## 核心工具/API

- **openai-whisper**: OpenAI开源的本地Whisper CLI，无需API key
- **openai-whisper-api**: OpenAI Whisper API调用（需要API key）
- **faster-whisper**: 优化后的Whisper实现，速度更快

## 步骤流程

### 方法一：本地Whisper CLI（免费）

1. **安装**
   ```bash
   # macOS
   brew install openai-whisper
   
   # 或通过pip
   pip install openai-whisper
   ```

2. **基本转录**
   ```bash
   whisper /path/audio.mp3 --model medium --output_format txt --output_dir .
   ```

3. **输出字幕格式**
   ```bash
   whisper /path/video.m4a --task translate --output_format srt
   ```

4. **指定语言**
   ```bash
   whisper /path/audio.m4a --language zh --model medium
   ```

### 方法二：OpenAI API（付费）

1. **设置API Key**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

2. **使用OpenClaw脚本**
   ```bash
   {baseDir}/scripts/transcribe.sh /path/to/audio.m4a
   ```

3. **高级选项**
   ```bash
   {baseDir}/scripts/transcribe.sh /path/audio.ogg --model whisper-1 --out /tmp/transcript.txt
   {baseDir}/scripts/transcribe.sh /path/audio.m4a --language en --prompt "Speaker: John, Sarah"
   ```

## 适用场景

- 技术教程视频提取完整文字稿
- 会议/访谈录音转文字
- 生成视频字幕（SRT/VTT）
- 提取代码演示的语音解说

## 避坑指南

- **问题**: 转录速度太慢
  - **解决**: 使用更小的模型（如tiny/base），或使用faster-whisper

- **问题**: 中文识别不准
  - **解决**: 添加 `--language zh` 明确指定语言，使用更大的模型

- **问题**: 专有名词识别错误
  - **解决**: 使用 `--prompt` 参数提供上下文或专有名词列表

- **问题**: 没有声音或音频损坏
  - **解决**: 先用 `ffmpeg -i input.mp4 -vn -acodec copy output.aac` 提取音频

## 模型选择建议

| 模型 | 速度 | 准确性 | 适用场景 |
|------|------|--------|----------|
| tiny | 最快 | 较低 | 快速预览 |
| base | 快 | 中等 | 一般转录 |
| medium | 中等 | 较高 | 重要内容 |
| large | 慢 | 最高 | 精度要求高 |

## 参考链接

- [OpenAI Whisper](https://openai.com/research/whisper)
- [OpenClaw openai-whisper Skill](./../../app/openclaw/skills/openai-whisper/SKILL.md)
- [OpenClaw openai-whisper-api Skill](./../../app/openclaw/skills/openai-whisper-api/SKILL.md)
