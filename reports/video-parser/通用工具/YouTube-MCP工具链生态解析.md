# YouTube数据获取MCP生态 — yt-mcp / yt-dlp-mcp / mcp-youtube

## 核心工具/API

### 1. yt-mcp（YouTube Data API方案）
- **数据源**：YouTube Data API v3（官方API）
- **字幕获取**：`youtube-transcript-api` Python包
- **环境变量**：`YOUTUBE_API_KEY`（必需）

### 2. yt-dlp-mcp / mcp-youtube（yt-dlp方案）
- **数据源**：yt-dlp（第三方解析，绕过API限制）
- **能力**：下载视频/音频/字幕/元数据
- **平台覆盖**：YouTube、Facebook、TikTok等

### 3. yt-subs-mcp
- **专精**：仅字幕提取
- **轻量**：最小化MCP服务器

## yt-mcp 支持工具列表

| 工具 | 功能 |
|------|------|
| `getVideoDetails` | 批量获取视频元数据（标题/时长/统计） |
| `searchVideos` | 关键词搜索视频 |
| `getTranscripts` | 批量获取字幕（带时间戳） |
| `getRelatedVideos` | 获取推荐视频 |
| `getChannelStatistics` | 频道统计数据 |
| `getChannelTopVideos` | 频道热门视频 |
| `getVideoEngagementRatio` | 互动率计算 |
| `getTrendingVideos` | 热门视频（按地区/类别） |
| `compareVideos` | 跨视频对比 |
| `getPlaylistDetails/Videos` | 播放列表信息 |

## 步骤流程（yt-mcp）
1. 配置 `YOUTUBE_API_KEY` 环境变量
2. 配置 `mcpServers.youtube` 指向 `npx yt-mcp`
3. AI助手自动调用工具获取YouTube数据
4. 字幕+元数据→后续LLM分析

## 适用场景
- **批量YouTube频道/视频分析**（舆情监控、竞品分析）
- **自动字幕提取**（无API Key限制版用mcp-youtube）
- **视频元数据采集**（标题/描述/标签/统计数据）
- **播放列表批量解析**（课程内容整理）
- **热门趋势分析**（按地区/类别）

## 避坑指南
- **YouTube Data API配额限制**：免费版每日1万单位，大批量需申请配额提升
- **字幕可用性**：并非所有视频都有字幕，自动回退机制很重要
- **mcp-youtube依赖yt-dlp**：在中国大陆可能需代理
- **OAuth可选**：私人播放列表需配置OAuth（端口3000）

## 选型建议
```
需要官方数据/频道分析 → yt-mcp（YouTube Data API）
需要字幕+绕过API限制 → mcp-youtube（yt-dlp）
只需要字幕提取 → yt-subs-mcp（最轻量）
需要多平台（TikTok等）→ yt-dlp-mcp
```

## 参考链接
- yt-mcp：https://github.com/space-cadet/yt-mcp
- yt-dlp-mcp：https://github.com/kevinwatt/yt-dlp-mcp
- mcp-youtube：https://github.com/anaisbetts/mcp-youtube
- yt-subs-mcp：https://github.com/jvsteiner/yt-subs-mcp
