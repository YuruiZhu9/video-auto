# 开源项目演示类 — TLDW 解析

> GitHub: https://github.com/s例/TLDW（Too Long; Didn't Watch）
> 官网：https://www.aipuzi.cn/ai-news/tldw.html

## 核心工具/API

| 组件 | 技术 | 说明 |
|------|------|------|
| **Next.js 15** | 前端框架 | 用户界面 |
| **xAI Grok 4 / Google Gemini** | LLM | 高光片段生成、结构化摘要 |
| **Supabase** | 数据库+认证 | 用户数据存储、笔记管理 |
| **YouTube Transcript API** | 字幕获取 | 无需下载视频，直接获取字幕 |

---

## 步骤流程

### 一、快速开始

**前置条件**
- Node.js 18.18+
- Supabase 账号（免费额度足够）
- xAI Grok API Key 或 Google Gemini API Key

**部署步骤**
```bash
# 1. 克隆项目
git clone <TLDW-repo>
cd tldw

# 2. 安装依赖
npm install   # 或 pnpm install

# 3. 配置环境变量（.env.local）
cp .env.example .env.local
# 填写：
# NEXT_PUBLIC_SUPABASE_URL=...
# NEXT_PUBLIC_SUPABASE_ANON_KEY=...
# GROK_API_KEY=...

# 4. Supabase 数据库配置
# 在Supabase后台运行 migrations/ 目录下的SQL

# 5. 启动
npm run dev
```

### 二、使用流程

**匿名用户（无需注册）**
```
1. 打开TLDW网页
2. 粘贴 YouTube 视频URL
3. 选择生成模式：
   - Smart（优质模式）：AI深度分析，提取关键论点+核心案例
   - Fast（快速模式）：优先速度，抓取高频片段
4. 等待分析完成（约30秒-2分钟）
5. 查看：
   - 结构化摘要（核心观点→分论点→支撑案例→结论）
   - 高光片段（带时间戳，可点击跳转）
   - 快速预览（100-200字精简摘要）
   - 经典语录
   - 建议问题
```

**登录用户（额外功能）**
```
1. 注册/登录（支持邮箱或Supabase第三方登录）
2. 所有匿名功能 + 以下功能：
3. 记录个人笔记（Markdown，自动关联视频+时间戳）
4. 收藏视频，建立个人视频库
5. 跨视频笔记聚合（/all-notes 页面）
```

---

## 适用场景

- ✅ 学生：网课视频的高效学习与知识点梳理
- ✅ 职场人士：快速提取技术教程关键操作步骤
- ✅ 内容创作者：批量分析竞品视频，收集素材与语录
- ✅ 终身学习者：海量YouTube视频的筛选与碎片化学习
- ✅ 不想自己部署Python环境的用户

---

## 避坑指南

- **仅支持YouTube**：TLDW主要针对YouTube视频，不支持B站、本地视频
  - 解决：B站视频可使用 `yt-dlp` 下载后用 Video-Analyzer 分析
  - 或使用 OpenClaw 内置 `videos_understand` 工具处理本地视频
- **长视频等待时间**：1小时以上视频分析可能需要3-5分钟
  - 解决：使用 Fast 模式降低等待时间；或先跳转到感兴趣段落分析
- **API费用**：Grok 4 / Gemini API 按使用量计费
  - 解决：TLDW有 aggressive 缓存策略，已分析视频不重复计费
  - 监控：在 Supabase 仪表板查看API用量
- **Supabase免费额度**：月活跃用户10万以内免费，超出需付费
- **无法处理无字幕视频**：依赖YouTube字幕，无字幕视频分析质量较差
  - 解决：使用 `yt-dlp --write-auto-subs` 尝试生成自动字幕

---

## 参考链接

- TLDW GitHub：https://github.com/s例/TLDW（Too Long; Didn't Watch）
- xAI Grok：https://x.ai
- Google Gemini：https://ai.google.dev
- Supabase：https://supabase.com
- yt-dlp（YouTube下载）：https://github.com/yt-dlp/yt-dlp
