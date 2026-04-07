# 行业分享类 - OpenClaw bibigpt-skill + BibiGPT 全平台方案

> 🤖 更新：2026-03-27
> 📍 来源：BibiGPT 官方博客 + OpenClaw 社区

---

## 核心工具/API

| 工具 | 类型 | 能力描述 |
|------|------|---------|
| **BibiGPT** | Web 应用 / API | 30+平台支持的 AI 音视频总结工具，100万+用户 |
| **bibigpt-skill** | OpenClaw Skill | 为 OpenClaw 带来完整 B 站视频理解能力 |
| **OpenClaw 定时心跳** | Agent 框架 | 支持每日定时任务，自动追踪 UP 主更新推送 |
| **知识管理生态** | 导出集成 | Notion / Obsidian / 飞书多端同步 |

---

## bibigpt-skill 安装与使用

### 安装方式

```bash
# 通过 ClawHub 安装
clawhub install bibigpt-skill
```

### 核心命令

```bash
# 一键总结 B 站视频
bibi summarize "https://www.bilibili.com/video/BVxxx"

# 提取字幕（不生成摘要）
bibi extract "https://www.bilibili.com/video/BVxxx"

# 指定输出格式
bibi summarize "URL" --format notion  # 同步至 Notion
bibi summarize "URL" --format obsidian  # 同步至 Obsidian
```

### 原生 summarize 的局限

OpenClaw 内置 `summarize` 命令**原生不支持 B 站**，`bibigpt-skill` 填补了这一空白，实现：
- B 站视频 URL 直接解析
- 自动弹幕提取与情感分析
- 视频画面变化检测与叙事结构解析

---

## BibiGPT 核心功能一览

| 功能 | 描述 |
|------|------|
| **全链路平台覆盖** | B站、YouTube、TikTok、小红书、抖音、播客、本地文件等 30+ 平台 |
| **独家视觉化内容理解** | 解析视频画面变化、叙事结构、背景音乐情绪 |
| **知识流转生态** | 一键同步至 Notion、Obsidian、飞书 |
| **AI 对话与深度分析** | 支持批判性思维分析追问 |
| **多元化内容输出** | 摘要、思维导图、公众号文章、动态网站 |
| **多语言支持** | 中、英、日、韩、俄、意、德、法等 14+ 语言 |
| **前沿 AI 模型驱动** | 持续集成领先 AI 模型 |

---

## BibiGPT vs 其他工具对比（2026年）

| 工具 | 特点 | 适用人群 |
|------|------|---------|
| **BibiGPT** | 30+平台、100万+用户、独家视觉分析、知识管理生态 | 追求深度学习、内容创作者、研究者 |
| **NoteGPT** | 对话式学习、永久存储、思维导图生成 | 学生、研究人员、知识工作者 |
| **AI课代表** | Chrome 扩展、B站原生集成、社区分享 | B站深度用户 |
| **VideoSeek AI** | 思维导图可视化、时间戳导航、SRT/TXT导出 | 跨平台用户、视觉型学习者 |
| **B站官方** | 免费、内测中 | 体验有待完善，仅适合快速获取要点 |
| **OpenClaw summarize** | 原生支持 YouTube / 通用 URL，不支持 B 站 | 通用音视频（非 B 站）|

---

## 适用场景

### 场景 1：UP主知识日报（完全自动化）
```
配置 OpenClaw 每天早 7 点检查订阅的 5 个技术/知识类 UP 主是否有新视频
  → bibigpt-skill 自动总结
    → 推送到飞书 / 微信
```

### 场景 2：课程批量归档
```
将某 UP 主整个系列课程（30+ 集）
  → 批量发送 URL 至 bibigpt-skill
    → 生成结构化笔记
      → 存入 Notion / Obsidian
```

### 场景 3：竞品内容监控
```
定期抓取行业相关 UP 主视频
  → AI 总结后按主题分类入库
    → 品牌团队每周节省 10+ 小时
```

### 场景 4：B站技术视频 × OpenClaw 联合解析
```
bibigpt-skill 提取字幕 → Whisper 增强转录
     ↓
videos_understand 深度理解 → 结构化技术笔记
     ↓
ffmpeg 提取关键帧 → images_understand OCR 代码截图
```

---

## 避坑指南

1. **B站视频链接格式**
   - 需使用完整 URL：`https://www.bilibili.com/video/BVxxx`
   - 短链 `b23.tv/xxx` 需先转换为完整 URL

2. **长视频（>30分钟）处理**
   - BibiGPT 会自动分段处理，无需手动切分
   - 输出结构：按时间戳自动切分章节

3. **私密/付费视频**
   - BibiGPT 依赖公开可访问的视频，无法处理私密视频
   - 付费课程需先确认视频开放访问权限

4. **知识管理同步失败**
   - Notion/Obsidian 同步需提前配置 API Token
   - 建议先测试单条同步再开启批量任务

5. **OpenClaw 定时任务防重复**
   - 配置心跳任务时加入 URL 去重逻辑（记录已处理 video ID）
   - 防止 UP 主同一天多次更新导致重复总结

---

## bibigpt-skill + OpenClaw 组合优势

| 能力 | 纯 BibiGPT Web | OpenClaw + bibigpt-skill |
|------|--------------|------------------------|
| 手动总结单视频 | ✅ | ✅ |
| 定时自动追踪 UP 主 | ❌ | ✅（内置心跳机制）|
| 多渠道推送（飞书/微信/DingTalk）| ❌ | ✅ |
| 与其他 Skill 联动（Whisper/FFmpeg）| ❌ | ✅ |
| 批量处理系列课程 | 需手动 | ✅（脚本自动化）|
| 免费额度 | 每日有限 | 依赖 BibiGPT API |

---

## 参考链接

- [BibiGPT 官网](https://bibigpt.co)
- [OpenClaw + bibigpt-skill 详细攻略](https://bibigpt.co/blog/posts/openclaw-bibigpt-skill-ai-agent-video-2026)
- [2026年 B站 AI 视频总结工具对比](https://bibigpt.co/blog/posts/2025-best-bilibili-ai-video-summary-tools-comprehensive-guide)

---

*本文件由视频解析方法总结Agent 自动生成 · 2026-03-27*
