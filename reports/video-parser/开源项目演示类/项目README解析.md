# 开源项目演示类 - GitHub README + 视频联合解析

> 适用于：GitHub 项目演示视频、开源工具介绍、OSS 发布会、技术 Demo 展示类视频

## 核心工具/API

- **GitHub CLI（gh）**：提取仓库元数据（stars、PR、issue、readme）
- **yt-dlp**：下载演示视频并提取字幕
- **summarize / videos_understand**：视频内容快速解析
- **Bilibili API / llmbase.ai B站解析 Skill**：国内开源项目演示视频解析
- **cursor-less / Claude Code**：自动化分析项目 README 和视频联动

## 步骤流程

### 第一步：定位项目 + 提取 README

```bash
# 克隆仓库
git clone https://github.com/owner/repo.git
cd repo

# 提取 README 内容
cat README.md | head -200

# 查看 release notes / changelog
cat CHANGELOG.md 2>/dev/null || echo "No CHANGELOG"

# 查看项目结构
find . -name "*.py" -o -name "*.ts" -o -name "*.go" | head -20

# 提取核心信息（star 数、语言、主题）
gh repo view owner/repo --json name,description,stargazerCount,languages,topics
```

### 第二步：查找并下载演示视频

```bash
# 查找视频链接（README / issue / discussion）
grep -r "youtube\|bilibili\|mp4\|video" README.md --include="*.md"

# YouTube 下载
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID" \
  --write-auto-sub --write-sub \
  --sub-lang zh-Hans,en \
  -o "/tmp/%(title)s.%(ext)s"

# B站 下载
yt-dlp "https://www.bilibili.com/video/BVxxxxxx" \
  --write-auto-sub \
  -o "/tmp/bilibili_%(title)s.%(ext)s"
```

### 第三步：视频内容解析

```bash
# 快速摘要（推荐）
summarize "/tmp/demo.mp4" --length long --model google/gemini-3-flash-preview

# 提取字幕（用于代码追踪）
summarize "/tmp/demo.mp4" --youtube auto --extract-only --out /tmp/subtitles.srt

# 截取关键片段（如 Demo 部分：10:00-20:00）
ffmpeg -i "/tmp/demo.mp4" -ss 00:10:00 -to 00:20:00 \
  -c:v libx264 -c:a aac "/tmp/demo_clip.mp4"
```

### 第四步：README + 视频联动分析

```python
# 分析 prompt：让 LLM 对比 README 和视频内容，找出差距和亮点

prompt = """
你是一名资深开源项目分析师。请分析以下信息：

【项目 README 摘要】
{readme_summary}

【视频内容摘要】
{video_summary}

【视频字幕片段】
{subtitle_snippet}

请输出：
1. 项目核心价值（1句话）
2. 视频演示了哪些 README 未强调的特性？
3. 代码实现亮点（从字幕中提取）
4. 与同类项目相比的核心差异化
5. 潜在风险/局限
"""

result = videos_understand(videos_info=[{"file": "/tmp/demo_clip.mp4", "prompt": prompt}])
```

## 适用场景

- GitHub Trending 项目研究（用视频了解实际效果）
- 开源工具选型（对比多个工具的视频演示）
- 学习新技术（看官方 Demo 而非读文档）
- 竞品分析（追踪同类开源项目的视频发布）
- 贡献开源项目（理解现有 Demo 的实现思路）

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| B站视频下载失败 | 需大会员或地区限制 | 换用 llmbase.ai B站解析 Skill 或在线工具 |
| 视频有水印 | 免费工具带水印 | 用 yt-dlp 官方版本，或用 --embed-thumbnail 时检查 |
| README 太长 | 项目文档膨胀 | 用 summarize 或手动提取核心部分（前500行） |
| 视频语言非中文/英文 | 小语种项目 | Whisper 支持 100+ 语言，可翻译 |
| GitHub rate limit | gh CLI 访问限制 | 登录：`gh auth login`，或加 `--sleep-interval` |
| 视频字幕缺失 | 自动字幕质量差 | 用 Whisper 本地重新转录（比 YouTube 自动字幕准） |

## 结构化输出模板

```markdown
# [开源项目名] - 项目 Demo 分析

## 基本信息
- GitHub：https://github.com/owner/repo
- Stars：[X]k
- 语言：[Python/TypeScript/Go...]
- 视频：YouTube / B站
- 视频时长：[X] 分钟
- Demo 片段：[XX:XX - XX:XX]

## 项目一句话介绍
用一句话说明这个项目是做什么的

## 核心功能（从 README 提取）
1. 功能1
2. 功能2

## 视频 Demo 亮点
| 时间 | 功能 | 描述 |
|------|------|------|
| 00:03 | XX | ... |

## 技术实现亮点
- 技术点1：从视频/字幕提取
- 技术点2：从代码结构分析

## 与竞品对比
| 维度 | [本项目] | [竞品A] |
|------|---------|---------|
| 性能   | ...     | ...     |
| 易用性 | ...     | ...     |

## 行动建议
- 是否值得关注：⭐⭐⭐⭐⭐
- 深入研究方向：...
```

## 参考链接

- yt-dlp：https://github.com/yt-dlp/yt-dlp
- GitHub CLI：https://cli.github.com
- llmbase.ai B站解析 Skill：https://llmbase.ai/openclaw/bilibili-video-parser/
- OpenClaw summarize skill：https://clawhub.ai/kn70pywhgf996kpa8xj89s57yhv26/summarize
