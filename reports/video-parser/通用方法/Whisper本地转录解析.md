# 通用方法 - Whisper 本地转录解析

> 适用于：音频文件、无字幕视频、技术演讲、会议录像等需要高精准转录的场景

## 核心工具/API

- **openai-whisper（PyPI）**：开源本地 Whisper 模型，支持 pip 安装
- **Whisper API（OpenAI）**：云端 API 版本，无需本地算力
- **Hugging Face Whisper**：多模型变体（large-v3 / distil-whisper 等）
- **openai-whisper-api（OpenClaw Skill）**：封装好的 Whisper API 调用脚本
- **OpenWhispr**：开源桌面端离线转录工具

## 步骤流程（本地 Whisper）

### 方法一：pip 安装使用
```bash
pip install openai-whisper

# 基本转录（自动选择模型大小）
whisper audio.mp3 --model medium

# 指定语言 + 输出格式
whisper audio.m4a --language zh --model large-v3 --output_format json

# 翻译为英文
whisper audio.mp3 --model large-v3 --task translate

# 条件生成（提供上下文提示）
whisper audio.mp3 --initial_prompt "这是一个关于推荐系统的技术分享"
```

### 方法二：OpenClaw Whisper API Skill
```bash
# 安装 skill 后
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a

# 指定语言
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --language zh

# 提供说话人提示
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --prompt "Speaker: 张三, 李四"

# JSON 输出
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --json --out /tmp/transcript.json
```

### 方法三：从视频提取音频再转录
```bash
# 用 ffmpeg 提取音频
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3

# 再用 Whisper 转录
whisper audio.mp3 --model large-v3 --language zh
```

## 适用场景

- **无字幕技术教程**：直接从视频提取音频并转录
- **多语言视频**：Whisper 支持 100+ 语言，可翻译
- **会议/播客录音**：长音频文件转录
- **方言/专业术语**：通过 `--initial_prompt` 提供上下文提升准确率
- **需要说话人分离**：需额外工具（如 pyannote）

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 转录慢 | 模型太大（large-v3） | 改用 `distil-whisper` 或 `medium` 模型提速 6x |
| 中文识别差 | 用了英文模型 | 加 `--language zh` 指定中文 |
| 专业术语错漏 | 缺乏上下文 | 用 `--initial_prompt` 提供术语表 |
| 视频无声音轨道 | ffmpeg 提取失败 | 检查视频编码：`ffprobe video.mp4` 确认有音频流 |
| 内存不足（OOM） | 模型太大 | 用 tiny/base/small 模型，逐步增大 |
| API 费用高 | 用了 OpenAI 云端 | 改用本地 Whisper large-v3，免费且离线可用 |

## 模型选择建议

| 模型 | 参数量 | 速度 | 中文准确率 | 推荐场景 |
|------|--------|------|-----------|---------|
| `tiny` | 39M | 最快 | 一般 | 快速测试 |
| `base` | 74M | 快 | 尚可 | 一般转录 |
| `small` | 244M | 中等 | 较好 | 日常使用 |
| `medium` | 769M | 较慢 | 好 | 高质量需求 |
| `large-v3` | 1550M | 最慢 | 最好 | 精准转录（推荐） |
| `distil-whisper` | 756M | 快 | 接近large | 速度+质量平衡 |

## 参考链接

- OpenAI Whisper GitHub：https://github.com/openai/whisper
- Whisper API 文档：https://platform.openai.com/docs/guides/speech-to-text
- Hugging Face Whisper：https://huggingface.co/openai/whisper-large-v3
- OpenWhispr（桌面端）：https://openwhispr.com
