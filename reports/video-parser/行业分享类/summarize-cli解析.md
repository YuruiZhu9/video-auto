# 行业分享类 — summarize CLI 解析方案

## 核心工具/API

- **summarize CLI**：OpenClaw 内置的快速摘要工具，支持 URL、本地文件、YouTube 链接的一键总结，底层支持多模型（OpenAI GPT / Anthropic Claude / Google Gemini / xAI Grok）
- **YouTube 专用管道**：
  - 主通道：`--youtube auto` — 自动选择最优提取方式
  - 备选通道：`APIFY_API_TOKEN` — 当自动提取失败时触发 Apify Fallback
- **关键参数**：
  - `--extract-only`：仅提取原文/字幕，不做摘要
  - `--length short|medium|long|xl|xxl`：控制摘要详细程度
  - `--json`：机器可读格式输出
  - `--firecrawl auto|off|always`：对付反爬网站

---

## 步骤流程

### 场景 1：YouTube / 在线视频摘要

```
1. 获取视频 URL
   → YouTube: https://youtu.be/xxx
   → Bilibili: https://www.bilibili.com/video/xxx

2. 调用 summarize（YouTube 优先）
   summarize "https://youtu.be/xxx" --youtube auto --extract-only
   → 提取字幕/转写文本

3. 生成摘要
   summarize "https://youtu.be/xxx" --length medium
   → 输出结构化摘要

4. 定向提取（如需特定信息）
   → 追加 prompt 进一步分析
   → 例："请从中提取所有提到的行业数据和公司名称"
```

### 场景 2：本地视频文件摘要

```
1. 确认文件路径
   → 支持格式：MP4 / MOV / AVI / MKV 等视频文件

2. 直接调用 summarize
   summarize "/workspace/video.mp4" --length medium
   → 自动识别为本地文件并处理

3. 仅提取文字内容
   summarize "/workspace/video.mp4" --extract-only
   → 获取原始转写文本，便于后续自定义处理
```

### 场景 3：网页嵌入视频（行业分享直播回放）

```
1. 获取分享页面 URL
   → 36氪直播、知乎直播、公众号视频等

2. 先用 summarize 提取页面内容
   summarize "https://example.com/live/123" --extract-only
   → 获取分享主题、嘉宾介绍等文字信息

3. 如有视频部分
   → 结合 browser 工具截图关键帧
   → 再用 images_understand 分析画面内容
```

### 模型选择建议

| 场景 | 推荐模型 | 原因 |
|------|----------|------|
| 快速摘要 | `google/gemini-3-flash-preview` | 速度快，免费额度高 |
| 深度分析 | `openai/gpt-5.2` | 上下文理解能力强 |
| 技术内容 | `anthropic/claude-sonnet-4` | 擅长技术细节 |
| 中文内容 | `google/gemini-3-flash-preview` | 中文支持优秀 |

### 环境变量配置

```bash
# 推荐配置（~/.summarize/config.json）
{
  "model": "google/gemini-3-flash-preview"
}

# 可选：Apify（YouTube 备选通道）
export APIFY_API_TOKEN=your_token

# 可选：Firecrawl（反爬网站）
export FIRECRAWL_API_KEY=your_key
```

---

## 适用场景

- ✅ YouTube 技术演讲、行业峰会分享视频
- ✅ B站、知乎、36氪等平台的行业分享视频
- ✅ 播客音频（summarize 同样适用）
- ✅ 需要快速获取视频核心观点的场景
- ✅ 本地会议录像、培训录像的快速摘要
- ✅ 定期消费系列视频（如每周行业周报）

---

## 避坑指南

- **YouTube 字幕依赖**：summarize 的 YouTube 提取依赖视频自带的字幕，非所有视频都有字幕（无字幕视频效果差）
- **中文视频支持**：B站等国内平台视频使用 `--youtube auto` 可能无法直接提取，需要先通过 yt-dlp 下载再用 summarize 处理
- **视频时长影响**：超长视频（>2小时）的摘要可能不完整，建议分段处理
- ** `--extract-only` 慎用**：原始转写文本可能很长（数万字），大视频先估算文本量
- **API Key 轮换**：多平台 Key 轮换使用可避免单 Key 速率限制
- **隐私内容**：summarize 会将内容发送到第三方 API，涉及隐私/公司内部视频请用本地模型
- **Bilibili 视频处理**：
  ```bash
  # 第一步：yt-dlp 下载（需先配置 cookie 或 cookies.txt）
  yt-dlp --cookies-from-browser chrome -o "%(title)s.%(ext)s" "https://www.bilibili.com/video/BVxxx"
  # 第二步：summarize 本地文件
  summarize "视频文件.mp4" --length medium
  ```

---

## 参考链接

- summarize Skill 文档：`/app/openclaw/skills/summarize/SKILL.md`
- Apify YouTube Scraper：<https://apify.com/apify/youtube-scraper>
- yt-dlp（视频下载）：<https://github.com/yt-dlp/yt-dlp>
- Firecrawl（网页内容提取）：<https://docs.firecrawl.dev>
