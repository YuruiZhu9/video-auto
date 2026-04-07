# 通用方法 - summarize CLI 统一入口

## 核心工具/API

- **summarize CLI**: `brew install steipete/tap/summarize` 安装；或通过 OpenClaw Skill 调用
- **内置模型**: Google Gemini 3 Flash（默认）、OpenAI GPT、Anthropic Claude
- **YouTube 支持**: `--youtube auto` 自动处理，无需 yt-dlp
- **Fallback**: Apify（需 `APIFY_API_TOKEN`）；Firecrawl（需 `FIRECRAWL_API_KEY`）

## 步骤流程

### 基本用法（URL 摘要）
```bash
summarize "https://example.com/article" \
  --model google/gemini-3-flash-preview \
  --length medium
```

### YouTube 视频摘要
```bash
# 自动选择最佳模式（字幕优先，无字幕则音频转录）
summarize "https://youtu.be/dQw4w9WgXcQ" \
  --youtube auto \
  --length long

# 仅提取字幕文本（不去重，保留原始时间戳）
summarize "https://youtu.be/dQw4w9WgXcQ" \
  --youtube auto \
  --extract-only

# 指定使用 Apify fallback
summarize "https://youtu.be/VIDEO_ID" \
  --youtube auto \
  --firecrawl auto
```

### 本地文件
```bash
summarize "/path/to/video.mp4" \
  --model google/gemini-3-flash-preview \
  --length medium
```

### 输出格式
```bash
# JSON 格式（程序化处理）
summarize "URL" --json --length short

# 控制输出长度
summarize "URL" --length short|medium|long|xl|xxl|<chars>
```

## 适用场景

- **技术教程视频**: 提取步骤要点，生成结构化笔记
- **行业分享/演讲**: 获取核心观点和时间线
- **播客（Podcast）**: 快速了解本期主题和亮点
- **无字幕视频**: 自动调用 Whisper/Apify 进行音频转录
- **多语言视频**: 设置语言参数提高准确率

## 避坑指南

| 问题 | 解决方案 |
|------|---------|
| 视频无字幕，提取质量差 | 加 `--firecrawl auto`，或手动用 `yt-dlp` 下载后转录 |
| 字幕语言错误 | 用 `--language zh` / `--language en` 指定语言 |
| 输出太长 | 用 `--length short` 或 `--max-output-tokens` 控制 |
| YouTube 视频被屏蔽 | 设置 `APIFY_API_TOKEN` 启用 Apify fallback |
| API Key 未设置 | 确认环境变量：`OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` |

## OpenClaw Skill 触发词

当你听到以下说法时，应立即使用此 Skill：
- "use summarize.sh"
- "what's this link/video about?"
- "summarize this URL/article"
- "transcribe this YouTube/video"（best-effort，**无需** yt-dlp）

## 参考链接

- Skill 路径: `/app/openclaw/skills/summarize/SKILL.md`
- 工具主页: https://summarize.sh
- 模型配置: `~/.summarize/config.json`
