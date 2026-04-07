# 技术教程类 - openai-whisper-api 云端转录

## 核心工具/API

- **工具**: OpenAI Whisper API（whisper-1 模型）
- **脚本**: /app/openclaw/skills/openai-whisper-api/scripts/transcribe.sh
- **API 端点**: https://api.openai.com/v1/audio/transcriptions
- **必需**: OPENAI_API_KEY 环境变量
- **费用**: ~$0.006/分钟

## 步骤流程

### 基本转录
```bash
# 基础调用（使用脚本）
transcribe.sh /path/to/audio.m4a

# 指定输出文件
transcribe.sh /path/to/audio.mp3 --out /workspace/transcripts/lecture.txt

# 指定语言
transcribe.sh /path/to/audio.m4a --language zh

# 带提示（提高专有名词准确率）
transcribe.sh /path/to/audio.m4a \
  --prompt "技术术语：推荐系统、协同过滤、Embedding、Transformer"

# 输出 JSON（带时间戳）
transcribe.sh /path/to/audio.m4a --json --out /tmp/result.json
```

### cURL 直接调用
```bash
curl -sS https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Accept: application/json" \
  -F "file=@/path/to/audio.m4a" \
  -F "model=whisper-1" \
  -F "response_format=verbose_json" \
  -F "timestamp_granularities[]=word" \
  -F "language=zh" \
  -F "prompt=推荐系统、Embedding、Transformer" \
  > transcript.json
```

## 与本地 Whisper 的对比

| 维度 | openai-whisper（本地） | openai-whisper-api（云端） |
|------|----------------------|-------------------------|
| API Key | 不需要 | 必需 |
| 运行速度 | 依赖硬件（GPU快） | 快（云端优化） |
| 费用 | 免费 | $0.006/分钟 |
| 稳定性 | 受本地环境影响 | 稳定 |
| 离线 | 支持 | 需要网络 |
| **推荐场景** | 有本地GPU、不想花钱 | API Key可用、追求速度 |

## 适用场景

- **快速转录**: 需要分钟级 turnaround 的场景
- **API 集成**: 接入自动化 pipeline
- **长音频**: 超过 1 小时的音频优先选 API
- **多语言**: 自动语言检测或指定语言

## 避坑指南

| 问题 | 解决方案 |
|------|---------|
| OPENAI_API_KEY 未设置 | 确认环境变量已配置 |
| 音频太长（>25MB）| 先分割：ffmpeg -i long.mp3 -f segment -t 600 part_%03d.mp3 |
| 中文转录仍有误差 | 加 --prompt 提供上下文和专有名词提示 |
| 网络问题 | 检查代理设置，或切换到本地 Whisper 作为 fallback |
