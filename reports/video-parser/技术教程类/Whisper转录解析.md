# 技术教程类 - Whisper 转录解析

## 核心工具/API

### 方案 A：OpenAI Whisper API（openai-whisper-api Skill）
- 通过 OpenAI Whisper-1 模型转录，需要 `OPENAI_API_KEY`
- OpenClaw Skill：`/app/openclaw/skills/openai-whisper-api/SKILL.md`
- API 端点：`POST https://api.openai.com/v1/audio/transcriptions`

### 方案 B：OpenAI Whisper CLI（openai-whisper Skill）
- 本地运行，无需 API Key，需要 `whisper` CLI
- 模型下载到 `~/.cache/whisper`（首次运行自动下载）
- OpenClaw Skill：`/app/openclaw/skills/openai-whisper/SKILL.md`

## 步骤流程

### 方案 A：API 转录

```bash
# OpenClaw 封装脚本
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a

# 指定模型
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --model whisper-1

# 指定语言
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --language en

# 指定说话人提示
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --prompt "Speaker names: 张三, 李四"

# 输出 JSON
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --json --out /tmp/transcript.json
```

### 方案 B：本地 CLI 转录

```bash
# 基础转录
whisper /path/audio.mp3 --model medium --output_format txt --output_dir .

# 带翻译（英译中等）
whisper /path/audio.m4a --task translate --output_format srt --output_dir .

# 指定语言 + 小模型（速度快）
whisper /path/video.mp4 --model small --language zh --output_format txt

# 完整参数示例
whisper /path/audio.mp3 \
  --model medium \
  --language auto \
  --output_format json \
  --output_dir ./transcripts \
  --beam_size 5 \
  --condition_on_previous_text false
```

### 完整流程（视频 → 转录 → 摘要）

```bash
# Step 1: FFmpeg 提取音频
ffmpeg -i tutorial.mp4 -vn -acodec pcm_s16le audio.wav -y

# Step 2: Whisper 转录
whisper audio.wav --model medium --language zh --output_format json --output_dir .

# Step 3: 读取 JSON 获取带时间戳字幕
cat audio.json | jq '.segments[] | "\(.start) -> \(.end): \(.text)"'

# Step 4: 将转录结果交给 summarize 做摘要
summarize "$(cat audio.txt)" --length long
```

## 适用场景

- ✅ **无字幕技术教程视频**：自动生成字幕和文字稿
- ✅ **会议/演讲记录**：长音频转文字，可搜索可编辑
- ✅ **代码演示旁白**：还原讲解步骤，提取关键命令
- ✅ **多语言内容**：Whisper 支持 100+ 语言，含中英文混合
- ✅ **方言/专业术语**：通过 `--prompt` 提供上下文提示提升准确率

## 避坑指南

### ❌ 常见问题 1：Whisper 幻觉（Hallucination）
**问题**：音频空档期，模型生成虚假内容
**解决**：
- 使用 `--beam_size 5` 提升准确性
- 音频质量差时先降噪：`ffmpeg -i audio.wav -af denoise output.wav`
- 通过 `--prompt` 提供上下文约束

### ❌ 常见问题 2：中文分词不准/专有名词错误
**问题**："OpenClaw" 识别成 "open claw"，"FFmpeg" 识别成 "F FM peg"
**解决**：
```bash
whisper audio.wav --prompt "本音频涉及以下术语：OpenClaw FFmpeg Whisper 推荐系统"
```
首次使用 prompt 设定术语表，后续段落的 ASR 准确率会提升

### ❌ 常见问题 3：API 费用超出预算
**问题**：OpenAI Whisper API 按分钟计费
**解决**：
- 小文件用本地 CLI `whisper`（免费）
- 确认视频是否已有字幕轨（有则直接用 summarize）

### ❌ 常见问题 4：本地 CLI 模型选择
**问题**：`large` 模型太慢，`tiny` 模型不准
**解决**：
| 场景 | 推荐模型 | 速度 | 准确率 |
|------|---------|------|--------|
| 测试/快速预览 | `tiny` | ⚡⚡⚡ | ⭐⭐ |
| 实时/流式 | `base` | ⚡⚡ | ⭐⭐⭐ |
| 一般用途 | `small` | ⚡ | ⭐⭐⭐⭐ |
| 生产/长视频 | `medium` | 🐢 | ⭐⭐⭐⭐⭐ |
| 最高精度 | `large` | 🐢🐢 | ⭐⭐⭐⭐⭐ |

## 参考链接

- OpenAI Whisper API：https://platform.openai.com/docs/guides/speech-to-text
- OpenAI Whisper 研究：https://openai.com/research/whisper
- OpenClaw Skill（API）：`/app/openclaw/skills/openai-whisper-api/SKILL.md`
- OpenClaw Skill（CLI）：`/app/openclaw/skills/openai-whisper/SKILL.md`
