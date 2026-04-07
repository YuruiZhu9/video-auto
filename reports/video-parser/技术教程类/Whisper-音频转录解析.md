# 技术教程类 - Whisper 音频转录方案

## 核心工具/API

- **Whisper API**（OpenAI）：云端转录，API 调用，无需本地算力
  - 模型：`whisper-1`（唯一可用模型）
  - 支持 98+ 语言，自动语言检测
  - 输出格式：JSON / TXT / SRT / VTT
  - API Key：`OPENAI_API_KEY`
- **Whisper CLI**（本地）：whisper-cpp，无需网络
  - 模型：`tiny` / `base` / `small` / `medium` / `large`
  - `--task transcribe`（转录）/ `--task translate`（翻译为英文）
  - 模型缓存：`~/.cache/whisper`
- **FFmpeg**：从视频提取音频流
  - 命令：`ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3`

## 步骤流程

### 完整流程：视频 → 音频 → 转录 → LLM 总结

```
1. FFmpeg 提取音频
   ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3

2. Whisper 转录
   # API 方式
   {baseDir}/scripts/transcribe.sh audio.mp3 --model whisper-1 --out transcript.txt
   
   # CLI 方式（本地）
   whisper audio.mp3 --model medium --output_format txt --output_dir .

3. LLM 分析转录文本
   → videos_understand 或直接分析 transcript.txt
```

### OpenClaw Skill 快速调用

```bash
# 方式一：OpenAI Whisper API（需 OPENAI_API_KEY）
{baseDir}/scripts/transcribe.sh /path/to/video.mp4 --model whisper-1 --out /tmp/transcript.txt

# 方式二：本地 Whisper CLI
whisper /path/to/audio.mp3 --model medium --output_format srt --output_dir /tmp/

# 带语言参数
whisper audio.mp3 --language zh --model medium
```

## 适用场景

- ✅ **纯讲解类教程**（无大量屏幕操作）
- ✅ **Podcast / 访谈 / 演讲** - 语音内容为核心
- ✅ **长视频（>1小时）** - Whisper 对长音频优化好
- ✅ **需要字幕文件（SRT/VTT）** - 配合视频播放器使用
- ✅ **无 GPU 本地环境** - API 方式绕过算力限制

## 避坑指南

- ⚠️ **多人对话视频**：Whisper 默认不区分说话人，需后处理或用 VAD 工具
- ⚠️ **背景音乐嘈杂**：先降噪再转录，或用 `medium`/`large` 模型提升准确率
- ⚠️ **API 费用**：Whisper API 按分钟计费，大批量使用注意成本
- ⚠️ **中文转录准确率**：使用 `--language zh` 明确指定语言
- ⚠️ **FFmpeg 提取音频后文件名**：避免中文路径，转录脚本可能不支持

## 参考链接

- [OpenAI Whisper API Skill](/app/openclaw/skills/openai-whisper-api/SKILL.md)
- [Whisper CLI Skill](/app/openclaw/skills/openai-whisper/SKILL.md)
- [FFmpeg 官网](https://ffmpeg.org/documentation.html)
- [Whisper 模型对比](https://github.com/openai/whisper#available-models-and-languages)
