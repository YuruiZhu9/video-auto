# 技术教程类 - summarize 工具解析

## 核心工具/API

- **summarize**：Fast CLI 工具，支持 URL、YouTube 和本地文件的摘要/字幕提取
  - 首页：`https://summarize.sh`
  - 安装：`brew install steipete/tap/summarize`
  - 支持模型：OpenAI、Google Gemini、Anthropic、xAI
  - 默认模型：`google/gemini-3-flash-preview`

- **依赖服务**：
  - `FIRECRAWL_API_KEY`（可选，绕过站点封锁）
  - `APIFY_API_TOKEN`（可选，YouTube fallback）

## 步骤流程

### 基本用法（URL）
```bash
summarize "https://example.com" --model google/gemini-3-flash-preview
```

### YouTube 视频
```bash
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto
```

### 纯字幕提取（不做摘要）
```bash
summarize "https://youtu.be/xxx" --youtube auto --extract-only
```

### 本地文件
```bash
summarize "/path/to/file.pdf" --model google/gemini-3-flash-preview
summarize "/path/to/video.mp4" --youtube auto
```

### 常用参数
```bash
--length short|medium|long|xl|xxl|<chars>  # 摘要长度
--max-output-tokens <count>                 # 最大输出token
--json                                     # JSON格式输出
--firecrawl auto|off|always                # Firecrawl提取策略
```

## 适用场景

- ✅ **YouTube 技术教程**：直接输入视频链接，自动提取字幕并生成摘要
- ✅ **技术博客/文章**：URL 直达，无需下载
- ✅ **B站/腾讯视频等国内平台**：通过 `--firecrawl auto` fallback 提取内容
- ✅ **本地带字幕的视频文件**：直接读取转录
- ⚠️ **无字幕原声视频**：summarize 依赖字幕轨道，建议改用 Whisper

## 避坑指南

### ❌ 常见问题 1：YouTube 字幕提取失败
**原因**：视频无字幕轨道，或字幕为自动生成（ASR）质量差
**解决**：设置 `APIFY_API_TOKEN` 启用 fallback；或改用 `videos_understand` 直接分析

### ❌ 常见问题 2：国内平台（微信/知乎/B站）内容提取失败
**原因**：这些平台反爬严格，Firecrawl 无法访问
**解决**：
  1. 手动下载视频到本地，用 `summarize /path/video.mp4`
  2. 或用 `yt-dlp` 下载后处理

### ❌ 常见问题 3：摘要质量差/太短
**原因**：默认 `--length short`，内容被过度压缩
**解决**：使用 `--length long` 或 `--length xx l`，或直接 `--extract-only` 获取全文

### ❌ 常见问题 4：API Key 未配置
**原因**：未设置对应的 API Key 环境变量
**解决**：设置 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY`

## 参考链接

- 工具首页：https://summarize.sh
- OpenClaw Skill：`/app/openclaw/skills/summarize/SKILL.md`
- 安装：`brew install steipete/tap/summarize`
