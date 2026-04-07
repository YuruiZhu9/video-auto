# 技术教程类 — Video Summary Skill（多平台视频摘要）

> 🤖 维护：视频解析方法总结Agent（小M）
> 📅 新增日期：2026-04-06（第五周）
> 🔗 来源：clawhub / llmbase.ai/openclaw/video-summary
> 📦 安装：`clawhub install video-summary`
> 🏷️ 适用平台：B站(哔哩哔哩)/小红书/抖音/YouTube

---

## 核心工具/API

| 工具 | 类型 | 能力描述 |
|------|------|----------|
| **视频平台原生API** | 平台能力 | 获取标题、描述、时长、标签等元数据 |
| **视频转录（Whisper/平台字幕）** | ASR | 将语音转为文字，支持中文+英文 |
| **LLM摘要** | 大模型 | 将转录文本转为结构化摘要 |
| **OpenClaw Skill** | 封装层 | 统一接口处理多平台差异 |

---

## 支持平台

| 平台 | 英文名 | URL特征 | 特殊处理 |
|------|--------|---------|---------|
| **哔哩哔哩** | Bilibili | bilibili.com / b23.tv | B站字幕/弹幕分析 |
| **小红书** | Xiaohongshu | xiaohongshu.com | 视频图文混合理解 |
| **抖音** | Douyin | douyin.com | 短/中视频，竖屏优先 |
| **YouTube** | YouTube | youtube.com / youtu.be | 字幕/自动字幕 |

---

## 步骤流程

```
Step 1 — 识别视频平台
  接收URL → 正则匹配平台 → 调用对应解析器
  
Step 2 — 获取视频元数据
  Bilibili → bv号解析 + API获取标题/简介/标签
  YouTube  → Data API获取标题/描述/时长/频道
  抖音     → 标题/描述/作者
  
Step 3 — 语音转文字
  有字幕 → 直接提取（yt-dlp / 平台API）
  无字幕 → Whisper本地/云端转录
  
Step 4 — LLM结构化摘要
  system: "你是专业的视频内容分析师..."
  prompt: "总结以下视频内容，输出结构化摘要..."
  
Step 5 — 输出格式
  ## 视频信息
  ## 核心主题
  ## 关键要点（3-5条）
  ## 时间线/章节
  ## 推荐话题标签
```

---

## 适用场景

- **快速了解视频主题**：先看摘要再决定是否完整观看
- **批量视频归档**：批量获取多视频的结构化信息
- **跨平台内容管理**：统一接口处理B站/抖音/YouTube等平台
- **竞品/行业监控**：批量处理同主题视频，提炼共性观点
- **学习资料整理**：将教程视频批量整理为可检索笔记

---

## 输出示例

```markdown
## 视频信息
- 标题：OpenClaw Skills 完全指南
- 平台：Bilibili
- 时长：28:35
- UP主：XXX
- 标签：#OpenClaw #AI助手 #插件

## 核心主题
本文介绍OpenClaw Skills的安装、配置与最佳实践。

## 关键要点
1. Skills是OpenClaw的扩展包，通过SKILL.md定义行为
2. 推荐从ClawHub安装社区验证Skills
3. 视频演示了3个实际用例：网页抓取、邮件处理、任务管理
4. 进阶技巧：自定义Skill开发、多Skill协同工作

## 时间线
[00:00-01:30] 开场介绍
[01:30-05:45] OpenClaw基础概念
[05:45-15:20] ClawHub Skills安装演示
[15:20-22:10] 实战案例讲解
[22:10-28:35] 总结与资源推荐
```

---

## 与其他工具的关系

```
Video-Summary Skill
  ├─ 底层可调用 BibiGPT（如果有）
  ├─ 底层可调用 summarize CLI
  ├─ 底层可调用 videos_understand（多模态理解）
  └─ 作为统一入口，根据平台自动选择最优方案
```

---

## 避坑指南

- **平台限制**：小红书等平台可能有反爬限制，部分视频无法自动获取
- **字幕质量**：B站/YouTube字幕质量参差不齐，无字幕视频需走Whisper转录
- **视频长度**：超长视频（>1小时）摘要可能过于笼统，建议分段处理
- **版权内容**：批量下载/处理有版权的视频需注意合规

---

## 参考链接

- ClawHub：https://llmbase.ai/openclaw/video-summary/
- 安装命令：`clawhub install video-summary`
- OpenClaw Skills：https://docs.openclaw.ai/zh-CN/tools/skills
