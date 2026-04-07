# 视频字幕提取 - summarize Skill

> 最后更新：2026-03-06

## 概述

summarize 是 OpenClaw 内置的 CLI 工具，可快速总结 URL、本地文件，支持 YouTube 视频字幕提取。适合需要快速获取视频内容的场景。

---

## 核心功能

| 功能 | 说明 |
|-----|------|
| **URL 总结** | 自动提取网页主要内容 |
| **YouTube 字幕** | 提取或总结 YouTube 视频 |
| **本地文件** | 支持 PDF、TXT、Markdown 等 |
| **多模型支持** | OpenAI、Anthropic、Google 等 |

---

## 快速开始

### 安装

```bash
# 使用 brew 安装
brew install steipete/tap/summarize
```

### 基本用法

```bash
# 总结 YouTube 视频
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto

# 仅提取字幕（不总结）
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto --extract-only

# 总结网页内容
summarize "https://example.com/article"

# 总结本地文件
summarize "/path/to/file.pdf"
```

### 常用参数

| 参数 | 说明 | 示例 |
|-----|------|------|
| `--youtube auto` | 启用 YouTube 模式 | `--youtube auto` |
| `--extract-only` | 仅提取字幕/文本 | `--extract-only` |
| `--length` | 输出长度 | `--length medium` |
| `--model` | 指定模型 | `--model openai/gpt-4o` |
| `--json` | JSON 格式输出 | `--json` |

### 支持的模型

- **OpenAI**: `openai/gpt-4o`, `openai/gpt-4-turbo`
- **Anthropic**: `anthropic/claude-3-opus`, `anthropic/claude-3-sonnet`
- **Google**: `google/gemini-1.5-pro` (默认)
- **xAI**: `xai/grok-beta`

### API Key 配置

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic  
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GEMINI_API_KEY="..."
```

---

## 适用场景

### 1. 快速获取视频要点
```bash
summarize "https://youtu.be/xxx" --youtube auto --length short
```

### 2. 提取完整字幕
```bash
summarize "https://youtu.be/xxx" --youtube auto --extract-only
```

### 3. 长视频分段总结
```bash
# 先提取完整字幕
summarize "https://youtu.be/xxx" --extract-only > transcript.txt

# 再分段总结（每5分钟一段）
# 结合 LLM 进行更精细的分析
```

### 4. 批量处理视频
```bash
# 遍历目录下所有视频
for url in $(cat urls.txt); do
    summarize "$url" --youtube auto "$url.txt"
done --extract-only >
```

---

## 避坑指南

### 问题1：YouTube 视频无法获取字幕
**原因**：视频可能关闭了字幕或无自动生成字幕
**解决方案**：
- 使用 `--youtube auto` 启用 Apify fallback
- 设置 `APIFY_API_TOKEN` 环境变量
- 手动检查视频是否有字幕

### 问题2：总结内容不完整
**解决方案**：
- 使用 `--length xx|xxl` 增加输出长度
- 使用 `--extract-only` 获取完整内容后自行总结
- 分段处理长视频

### 问题3：API 调用失败
**检查项**：
- 确认 API Key 已正确设置
- 检查网络连接
- 确认模型可用性

---

## 对比 videos_understand

| 维度 | summarize | videos_understand |
|-----|-----------|------------------|
| **响应速度** | 快 | 较慢 |
| **输出内容** | 字幕/总结 | 深度理解 |
| **适用场景** | 快速提取 | 深度分析 |
| **本地视频** | 不支持 | 支持 |
| **自定义程度** | 中 | 高 |

---

## 参考资源

- summarize 官网：https://summarize.sh
- GitHub：https://github.com/steipete/summarize
- Apify YouTube Scraper：https://apify.com/transcriptdl/transcript-downloader-youtube-transcript-and-metadata-scraper
