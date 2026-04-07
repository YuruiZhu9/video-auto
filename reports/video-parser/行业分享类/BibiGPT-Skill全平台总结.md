# 行业分享类 - BibiGPT Skill 全平台AI视频总结

## 核心工具/API

| 工具 | 作用 | 备注 |
|------|------|------|
| **BibiGPT** | AI视频总结核心引擎 | 底层用 Claude Sonnet 4.6 |
| **bibigpt-skill** | OpenClaw/Claude Code集成 | MIT开源协议 |
| **bibi CLI** | 命令行调用入口 | 支持 summarize/subtitle/chapter 等子命令 |

---

## 支持平台（30+）

| 平台 | 状态 | 平台 | 状态 |
|------|------|------|------|
| B站（Bilibili） | ✅ 完整支持 | YouTube | ✅ 完整支持 |
| 小红书 | ✅ 完整支持 | 抖音 | ✅ 完整支持 |
| 小宇宙/播客 | ✅ 完整支持 | 喜马拉雅 | ✅ 完整支持 |
| 本地文件（mp3/mp4/m4a/mov） | ✅ 完整支持 | 微博视频 | ✅ 完整支持 |
| Twitter/X视频 | ✅ 完整支持 | Instagram | ✅ 完整支持 |

---

## 步骤流程

### 安装步骤

```bash
# 1. 安装 BibiGPT 桌面端
# macOS
brew install --cask jimmylv/bibigpt/bibigpt
# Windows
winget install JimmyLv.BibiGPT

# 2. 安装 bibigpt-skill（OpenClaw集成）
npx skills add JimmyLv/bibigpt-skill

# 3. 验证安装
bibi auth check    # 检查登录状态
bibi --help        # 查看所有命令
```

### 核心命令

| 命令 | 说明 |
|------|------|
| `bibi summarize "<url>"` | 标准总结 |
| `bibi summarize "<url>" --chapter` | 按章节分段总结 |
| `bibi summarize "<url>" --subtitle` | 仅获取字幕/转录文本 |
| `bibi summarize "<url>" --json` | 输出完整JSON（程序处理用） |
| `bibi summarize "<url>" --async` | 异步模式（适合长视频>30min） |

### OpenClaw集成方式

**方式一：直接调用（推荐）**
在OpenClaw中直接发送：
> 帮我总结这个视频，重点提取核心观点：https://www.bilibili.com/video/BVxxxx

**方式二：定时任务**
配置心跳任务 → 自动调用 `bibi summarize` → 生成Markdown日报 → 推送钉钉/Slack

---

## 适用场景

- ✅ **B站/抖音/小红书内容研究**：快速提炼创作者核心观点
- ✅ **竞品视频分析**：批量总结同类型视频，提炼共同模式
- ✅ **知识体系构建**：视频笔记+Anki卡片+思维导图
- ✅ **外语视频学习**：多语言字幕翻译+双语对照
- ✅ **长视频精华提取**：30min+视频一键生成结构化摘要

---

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|------|
| 需要登录/付费 | BibiGPT有免费试用额度 | 注册账号获取免费额度；长期使用需订阅 |
| 异步任务无返回 | 网络超时或任务失败 | 使用 `--json` 轮询任务状态 |
| 某些小众平台不支持 | 平台限制 | 检查BibiGPT官网支持列表 |
| 中文视频英文总结乱码 | 语言检测问题 | 视频URL前加语言前缀或在命令中指定 |
| 大量视频需要批量处理 | 单次调用效率低 | 结合Python脚本循环调用CLI |

---

## 特色功能

| 功能 | 说明 |
|------|------|
| **带时间戳的结构化摘要** | 每个要点对应视频时间点，可点击跳转 |
| **AI对话溯源** | 对视频内容深度问答，每个回答附时间戳 |
| **AI高光笔记** | 自动提取高光片段，按主题分类 |
| **闪记卡（Flashcard）** | 自动生成Anki问答卡片 |
| **播客生成** | 将视频转化为双人对谈播客风格 |
| **Nano Banana 2 配图** | 生成小红书风格的AI配图 |

---

## 参考链接

- GitHub仓库：https://github.com/JimmyLv/bibigpt-skill
- BibiGPT官网：https://bibigpt.co
- ClawHub技能页：搜索 `bibigpt-skill` 或 `JimmyLv`
