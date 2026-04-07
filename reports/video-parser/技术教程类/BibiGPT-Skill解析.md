# 技术教程类 - BibiGPT Skill（AI视频一键总结）

## 核心工具/API

| 工具 | 类型 | 说明 |
|------|------|------|
| **BibiGPT** | 云端 AI 服务 | 全平台 AI 视频/音频总结，支持 30+ 平台 |
| **bibigpt-skill** | OpenClaw Skill | 让 OpenClaw 直接调用 BibiGPT 的命令行工具 |
| **bibi CLI** | CLI 工具 | bibigpt-skill 的核心命令工具 |
| **OpenAI Whisper** | 底层转录 | BibiGPT 内部使用的语音转文字引擎 |

---

## 步骤流程

### 第一步：安装 BibiGPT 桌面端

```bash
# macOS（推荐）
brew install --cask bibigpt

# Windows
winget install JimmyLv.BibiGPT

# 或直接下载：https://bibigpt.co/apps/desktop
```

### 第二步：安装 bibigpt-skill

```bash
npx skills add JimmyLv/bibigpt-skill
```

### 第三步：验证安装

```bash
bibi auth check   # 检查登录状态（需要有效的 BibiGPT 账号）
bibi --help       # 查看所有可用命令
```

### 第四步：在 OpenClaw 中使用

```
用户：帮我用 BibiGPT 总结这个 B站视频：https://www.bilibili.com/video/BV1xxx
OpenClaw → 调用 bibigpt-skill → 返回结构化摘要
```

或在 Claude Code / OpenClaw 定时任务中自动化使用：

```bash
# Path 3：OpenClaw 心跳任务（全自动）
# 1. 读取订阅频道 RSS
# 2. 筛选新视频
# 3. 调用 bibi summarize
bibi summarize "https://www.bilibili.com/video/BV1xxx" --chapter --json
# 4. 汇总生成 Markdown 日报
# 5. 发送到钉钉/邮箱
```

---

## 核心命令

| 命令 | 说明 |
|------|------|
| `bibi summarize "<url>"` | 标准总结 |
| `bibi summarize "<url>" --chapter` | 按章节分段总结 |
| `bibi summarize "<url>" --subtitle` | 仅获取字幕/转录文本 |
| `bibi summarize "<url>" --json` | 输出完整 JSON（适合程序处理） |
| `bibi summarize "<url>" --async` | 异步模式（适合长视频） |
| `bibi auth check` | 验证登录状态 |

---

## 支持平台

| 平台 | 状态 | 特别支持 |
|------|------|----------|
| 哔哩哔哩 / B站 | ✅ 完整支持 | 弹幕分析 |
| 小红书 | ✅ 完整支持 | 图文+视频 |
| 抖音 | ✅ 完整支持 | 短视频 |
| YouTube | ✅ 完整支持 | 字幕翻译 |
| 小宇宙（播客） | ✅ 完整支持 | 音频优先 |
| 本地音视频文件 | ✅ 完整支持 | mp3/mp4/m4a/mov |
| Twitter/X | ✅ 完整支持 | 视频推文 |
| 会议（Zoom/Teams） | ✅ 完整支持 | 会议记录 |
| 网页任意视频 | ✅ 完整支持 | iframe 嵌入 |

---

## 高级功能

| 功能 | 说明 | 典型用途 |
|------|------|----------|
| **AI 视频对话与溯源** | 每个 AI 回答附带可点击时间戳 | 精准定位原始片段 |
| **AI 高光笔记** | 自动提取带时间戳的高光片段，按主题分类 | 快速回顾精华 |
| **合集归纳总结** | 多视频整体归纳，生成思维导图 | 系列教程学习 |
| **闪记卡（Flashcard）** | 自动生成 Anki 问答卡片 | 间隔重复记忆 |
| **多语言字幕翻译** | 自动生成双语对照字幕 | 外语学习 |
| **播客生成** | 视频转为双人对谈播客风格 | 通勤收听 |
| **MV 编辑器** | 一键生成抖音/视频号短视频 | 二次创作 |
| **Nano Banana 2** | 从视频摘要生成 AI 图片（小红书风格） | 配图生成 |

---

## 适用场景

- ✅ **技术教程学习**：B站编程教学视频，一键生成章节笔记
- ✅ **外语学习**：YouTube 英文字幕 + 双语翻译
- ✅ **会议记录**：Zoom/Teams 会议快速总结行动项
- ✅ **播客消化**：小宇宙长播客，转为文字稿+高光
- ✅ **竞品研究**：批量总结同一话题的多个视频
- ✅ **知识管理**：自动同步到 Notion/Obsidian/飞书

---

## 避坑指南

### ⚠️ 免费额度限制

- bibigpt-skill **开源免费**（MIT 协议）
- 但使用 BibiGPT 云端服务**需要有效账号**（有免费试用额度）
- 长视频或高频使用建议购买会员（官网 bibigpt.co）

### ⚠️ B站登录限制

- 部分 B站视频需要登录才能获取字幕
- 解决方案：在 BibiGPT 桌面端登录后，cookie 会自动用于 CLI

### ⚠️ 异步处理长视频

```bash
# 长视频（>1小时）建议用异步模式
bibi summarize "https://youtube.com/watch?v=xxx" --async --json

# 异步任务通过 WebSocket 推送结果，适合自动化流程
```

### 💡 与 OpenClaw 定时任务结合

```bash
# 示例：每日自动总结订阅频道新视频
# 1. 读取 RSS feed
# 2. 筛选过去24小时新视频
# 3. 批量调用 bibi summarize --chapter --json
# 4. 解析 JSON，生成 Markdown 日报
# 5. 通过钉钉 webhook 发送给用户
```

---

## 与 OpenClaw 原生 summarize 对比

| 能力 | OpenClaw 原生 | bibigpt-skill |
|------|--------------|---------------|
| YouTube | ✅ | ✅ |
| B站/小红书/抖音 | ❌ | ✅ |
| 本地音视频 | ❌ | ✅ |
| 章节分段 | ❌ | ✅ |
| JSON 输出 | ❌ | ✅ |
| 异步处理 | ❌ | ✅ |
| 多语言字幕 | ❌ | ✅ |
| 闪记卡/Anki | ❌ | ✅ |
| 合集归纳 | ❌ | ✅ |
| 成本 | API 费用 | BibiGPT 会员 |

---

## 参考链接

- BibiGPT 官网：https://bibigpt.co
- bibigpt-skill GitHub：https://github.com/JimmyLv/bibigpt-skill
- BibiGPT API 文档：https://docs.bibigpt.co
- 安装指南：https://bibigpt.co/blog/posts/openclaw-bibigpt-skill-ai-agent-video-2026
- 定价页面：https://bibigpt.co/user/integration
