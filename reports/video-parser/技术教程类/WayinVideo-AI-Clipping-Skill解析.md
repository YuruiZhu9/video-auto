# 通用工具 — WayinVideo AI视频理解与智能剪辑 Skill

> 🤖 维护：视频解析方法总结Agent（小M）
> 📅 新增日期：2026-04-06（第五周）
> 🔗 来源：WayinVideo / clawhub.ai/wayinvideo/video-understanding-and-ai-clipping
> 📦 安装：`clawhub install WayinVideo/video-understanding-and-ai-clipping`

---

## 核心工具/API

| 工具 | 类型 | 能力描述 |
|------|------|----------|
| **WayinVideo API** | 商业API | 一套API搞定理视频理解/剪辑/搜索/转录 |
| **OpenClaw Skill** | Skill封装 | 安装即用，四大能力一键切换 |
| **多平台支持** | 视频源 | YouTube/Bilibili/TikTok/抖音等主流平台 |

---

## 四大核心能力（一套安装，全部解锁）

### 1. AI Clipping（AI智能剪辑）⭐
自动将长视频转换为适合TikTok/抖音的短视频片段，带标题、描述、话题标签和下载链接。

**典型场景：**
```
输入："Clip the best moments from this video for TikTok"
输出：
  - 片段1：[00:32-01:05] 高光时刻1 + 标题 + #话题标签
  - 片段2：[02:18-02:45] 高光时刻2 + 标题 + #话题标签
  - 下载链接（可直接发布）
```

### 2. Find Moments（精确时刻搜索）⭐
用自然语言搜索视频，返回精确时间戳或可直接剪辑的片段。

**典型场景：**
```
输入："Find the best goal moments in this sports match"
输出：
  - [03:22-03:35] 进球时刻A
  - [11:45-11:58] 进球时刻B
  - [27:30-27:48] 绝杀时刻
```

### 3. Video Summary（视频结构化摘要）⭐
生成带章节的结构化摘要、核心要点和话题标签，适合存档和研究。

**典型场景：**
```
输入："Summarize this webinar and list the key takeaways"
输出：
  ## 摘要
  ## 核心要点（3-5条）
  ## 关键数据/案例
  ## 推荐话题标签
```

### 4. Video Transcription（视频转录）⭐
提取带时间戳的文字稿，包含词级时间信息和说话人标注（如有）。

**典型场景：**
```
输入："Transcribe this interview and identify each speaker"
输出：
  [00:00-00:15] 主持人：欢迎来到...
  [00:15-00:42] 嘉宾A：今天要讨论的主题是...
  [00:42-01:10] 嘉宾B：我认为...
```

---

## 步骤流程

```
Step 1 — 安装 Skill
  tell agent: "Install the WayinVideo/video-understanding-and-ai-clipping skill"
  或手动：clawhub install WayinVideo/video-understanding-and-ai-clipping

Step 2 — 配置 API Key
  访问 https://wayin.ai/wayinvideo/api-dashboard
  创建账户 → 创建API Key → 购买API Units（按视频分钟计费，约2 Units/分钟）

Step 3 — 告诉 Agent 你要做什么
  粘贴视频链接 + 描述需求
  Agent自动选择合适的处理模式

Step 4 — 获取结果
  AI Clipping → 多个短视频片段 + 元数据
  Find Moments → 时间戳列表 / 剪辑就绪片段
  Video Summary → 结构化Markdown文档
  Transcription → 带时间戳的JSON/文本
```

---

## 适用场景

- **短视频内容创作者**：快速从长视频中提取高光片段，自动生成标题和标签
- **研究者/分析师**：快速获取视频核心要点，无需完整观看
- **教育培训**：将课程视频自动切分为章节，支持快速检索
- **营销团队**：从产品发布会/访谈视频中提取素材
- **竞品监控**：批量处理多个视频，快速获取结构化信息

---

## 避坑指南

- **计费方式**：按视频分钟数计费（约2 Units/分钟），长视频需预估成本
- **平台覆盖**：优先测试目标平台是否在支持列表中
- **质量依赖**：剪辑质量依赖原视频音频/画面质量，低画质视频效果可能打折扣
- **API Key安全**：不要在公开场合暴露API Key，存储在环境变量中
- **批量处理**：大量视频时注意成本控制，可先做元数据提取再选择性深度处理

---

## 成本参考

| 视频时长 | 约消耗Units | 说明 |
|---------|------------|------|
| 5分钟 | ~10 Units | 短视频/片段 |
| 30分钟 | ~60 Units | 标准教程/演讲 |
| 1小时 | ~120 Units | 长视频/会议 |

> 具体费率以WayinVideo官网为准：https://wayin.ai/api-docs/pricing/

---

## 参考链接

- ClawHub安装页：https://clawhub.ai/wayinvideo/video-understanding-and-ai-clipping
- API申请：https://wayin.ai/wayinvideo/api-dashboard
- 官方文档：https://wayin.ai/api-docs/skills-video-understanding-and-ai-clipping/
- 定价信息：https://wayin.ai/api-docs/pricing/
