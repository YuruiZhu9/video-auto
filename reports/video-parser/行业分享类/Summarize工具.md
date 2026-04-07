# 行业分享类 - Summarize 工具

## 核心工具/API

- **summarize.sh**: 命令行工具，支持URL、本地文件、YouTube视频的摘要
- **Firecrawl**: 网页内容提取（作为fallback）
- **Apify**: YouTube视频提取fallback方案

## 步骤流程

### 基本用法

1. **总结网页内容**
   ```bash
   summarize "https://example.com" --model google/gemini-3-flash-preview
   ```

2. **总结YouTube视频**
   ```bash
   summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto
   ```

3. **仅提取字幕/脚本**
   ```bash
   summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto --extract-only
   ```

### 高级选项

```bash
# 指定输出长度
summarize "url" --length short      # 短摘要
summarize "url" --length medium     # 中等
summarize "url" --length long       # 详细

# 指定模型
summarize "url" --model openai/gpt-5.2

# 输出JSON格式
summarize "url" --json

# 强制使用Firecrawl
summarize "url" --firecrawl always
```

### API Key配置

支持的模型提供商：

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GEMINI_API_KEY="..."
```

或在配置文件中设置：`~/.summarize/config.json`

```json
{
  "model": "openai/gpt-5.2"
}
```

## 适用场景

- 快速了解行业分享视频的核心观点
- 提取YouTube/B站视频的要点
- 生成文章/视频的简短摘要
- 获取视频的文字稿（用于后续分析）

## 避坑指南

- **问题**: YouTube视频提取失败
  - **解决**: 设置 `APIFY_API_TOKEN` 环境变量启用Apify fallback

- **问题**: 网页内容被阻止
  - **解决**: 设置 `FIRECRAWL_API_KEY` 启用Firecrawl

- **问题**: 视频太长，摘要太简略
  - **解决**: 使用 `--extract-only` 获取完整字幕，再分段处理

- **问题**: 模型响应慢或超时
  - **解决**: 使用 `--length short` 或切换到更快的模型

## 与其他工具的组合

### Summarize + Whisper 工作流

```bash
# 1. 先下载视频音频
yt-dlp -x --audio-format mp3 "https://youtu.be/xxx" -o "audio.mp3"

# 2. 用Whisper转录
whisper "audio.mp3" --output_format txt

# 3. 用Summarize总结
summarize "audio.txt" --length long
```

### Summarize + 视频帧提取

```bash
# 1. 提取关键帧
{baseDir}/scripts/frame.sh video.mp4 --time 00:05:00 --out frame.jpg

# 2. Summarize视频内容
summarize "https://youtu.be/xxx"

# 3. 结合分析（用于理解视频上下文）
```

## 输出格式说明

### 默认输出（人类可读）
```
📺 Video Title

Key Points:
1. 第一个要点
2. 第二个要点
3. ...

Summary:
这是一段总结文字...
```

### JSON输出
```json
{
  "title": "Video Title",
  "summary": "Summary text...",
  "key_points": ["Point 1", "Point 2"],
  "url": "..."
}
```

## 参考链接

- [summarize.sh官网](https://summarize.sh)
- [OpenClaw summarize Skill](./../../app/openclaw/skills/summarize/SKILL.md)
- [Firecrawl](https://www.firecrawl.dev/)
- [Apify](https://apify.com/)
