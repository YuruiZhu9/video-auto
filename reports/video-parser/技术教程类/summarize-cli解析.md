# 技术教程类 — summarize CLI 解析

## 核心工具/API

- **`summarize` CLI**：一体化总结工具，支持 URL/文件/YouTube，自动选择最优提取策略。
- **底层依赖**：
  - `yt-dlp`：YouTube 视频下载
  - `Apify API`（可选）：YouTube 字幕爬取备用方案
  - `Firecrawl API`（可选）：被墙站点的网页抓取
- **LLM Provider**：支持 OpenAI / Anthropic / Google Gemini / xAI

## 步骤流程

```
1. 一键总结 YouTube 视频
   summarize "https://youtu.be/VIDEO_ID" --youtube auto

   # 指定长度
   summarize "https://youtu.be/VIDEO_ID" --youtube auto --length long

2. 仅提取字幕/文字（不总结）
   summarize "https://youtu.be/VIDEO_ID" --youtube auto --extract-only

3. 总结本地文件
   summarize "/path/to/video.mp4" --model google/gemini-3-flash-preview

4. 批量处理 + 输出 JSON
   for url in $(cat urls.txt); do
     summarize "$url" --youtube auto --extract-only --json >> results.jsonl
   done

5. 结合 SRT 生成结构化笔记
   - 用 yt-dlp 下载字幕：yt-dlp --write-subs --write-auto-subs URL
   - summarize 提取摘要
   - 将 SRT 时间轴与摘要对齐
```

## 适用场景

- 快速了解视频核心内容（不需要逐字稿）
- 有字幕的视频（YouTube/Bilibili/ Coursera 等）
- 当你只想知道"这个视频讲了什么"，而非完整转写
- 信息密度高的演讲/技术分享

## 避坑指南

| 问题 | 解决方案 |
|------|----------|
| 视频无字幕 | `summarize` 会自动尝试 Apify 爬取，需设置 `APIFY_API_TOKEN` |
| 被防火墙拦截的网站 | 安装 Firecrawl：`FIRECRAWL_API_KEY` 环境变量 |
| 只想提取特定段落 | `--extract-only` 先拿到完整文字，再让 LLM 聚焦处理 |
| 输出太长/太短 | `--length` 参数：`short`/`medium`/`long`/`xl`/`xxl` |
| 多视频批量处理 | 配合 shell 脚本或 Python 循环，使用 `--json` 便于后续解析 |
| 模型选型 | 默认 `gemini-3-flash-preview`（免费高速）；重要视频用 `gpt-5.2` |

## 配置示例

```json
// ~/.summarize/config.json
{
  "model": "openai/gpt-5.2",
  "length": "medium"
}
```

```bash
# 环境变量
export OPENAI_API_KEY="sk-..."
export APIFY_API_TOKEN="..."        # YouTube字幕备用
export FIRECRAWL_API_KEY="..."      # 防火墙绕过
```

## summarize vs 其他方案对比

| 维度 | summarize | yt-dlp+Whisper | videos_understand |
|------|-----------|----------------|-------------------|
| 速度 | ⭐⭐⭐⭐⭐ 快 | ⭐⭐ 慢 | ⭐⭐⭐ 中 |
| 精度 | ⭐⭐⭐ 依赖字幕 | ⭐⭐⭐⭐⭐ 最高 | ⭐⭐⭐⭐ 高 |
| 需下载 | 否 | 是 | 否 |
| 成本 | LLM调用 | LLM调用 | 工具调用 |
| 适用内容 | 有字幕的演讲 | 代码演示/无字幕 | 通用视频 |

---

*最佳实践：`summarize` 用于快速筛选，`yt-dlp+Whisper` 用于深度存档*
