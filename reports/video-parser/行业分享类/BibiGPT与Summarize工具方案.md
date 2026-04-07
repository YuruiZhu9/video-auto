# [行业分享类] - BibiGPT + Summarize 工具方案

## 核心工具/API

- **BibiGPT**：AI 视频/音频一键总结工具
  - 支持平台：B站、YouTube、小红书、抖音、推特、小宇宙播客、本地视频/音频、微信公众号等 30+ 平台
  - 核心功能：AI 一键总结、思维导图、带时间轴字幕、AI 改写图文、AI 对话追问、热门视频总结、音视频知识库
  - API 支持：提供开放 API，可集成到自动化工作流
- **OpenClaw summarize Skill**：命令行 URL/文件总结工具
  - 支持 YouTube 直接解析：`summarize "<url>" --youtube auto`
  - `--extract-only`：仅提取字幕/转录文本，不生成总结
  - 多模型支持：OpenAI / Anthropic / Google Gemini / xAI
- **bibigpt-skill（OpenClaw Skill）**：让 AI Agent 直接调用 BibiGPT API
  - 安装：`clawhub install bibigpt-skill`
  - 支持 OpenClaw/Claude Code 等 Agent 直接调用

## 步骤流程

### BibiGPT 工作流

1. **输入视频链接或上传本地文件**
   ```
   复制视频链接 → 粘贴到 BibiGPT 输入框
   支持平台：B站视频链接 / YouTube 链接 / 本地 MP4 文件
   ```

2. **选择输出格式**
   - 总结摘要（Emoji + 分段详细总结）
   - 思维导图（自动生成结构化导图）
   - 字幕列表（带时间轴，逐行时间戳）
   - 文章视图（Markdown 格式）
   - 对话模式（可追问细节）

3. **导出结构化数据**
   - 支持批量导出
   - 合集管理
   - 可对接知识库系统

### summarize Skill 工作流

1. **YouTube 视频直接解析**
   ```bash
   summarize "https://youtu.be/xxxx" --youtube auto --extract-only
   ```

2. **本地文件解析**
   ```bash
   summarize "/path/to/video.mp4" --model google/gemini-3-flash-preview
   ```

3. **设置总结长度**
   ```bash
   summarize "<url>" --length medium  # short/medium/long/xl/xxl
   ```

## 适用场景

- 快速了解一个行业分享视频的核心观点（30分钟 → 3分钟）
- 批量学习 YouTube/B站 技术频道视频
- 构建个人知识库（视频总结 → Notion/Obsidian 笔记）
- 播客内容快速消化（小宇宙、苹果播客等）
- 产品体验分享视频的结构化摘要

## 避坑指南

- **BibiGPT 免费额度**：新用户 1 小时免费时长，超过需订阅；B站视频 1 小时以内通常免费
- ** summarize Skill API Key**：需要设置对应的环境变量（`OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY`）
- **YouTube 解析失败**：某些地区可能需要设置 `APIFY_API_TOKEN` 作为 fallback
- **Firecrawl 绕过**：被反爬虫拦截的网站可设置 `FIRECRAWL_API_KEY` 解决
- **B站分区支持**：summarize Skill 对 B站支持不如 BibiGPT 稳定，建议用 BibiGPT 处理中文视频

## 参考链接

- BibiGPT 官网：https://bibigpt.co
- BibiGPT API 文档：https://docs.bibigpt.co
- bibigpt-skill：https://clawhub.com（搜索 bibigpt-skill）
- OpenClaw summarize Skill：`/app/openclaw/skills/summarize/SKILL.md`
