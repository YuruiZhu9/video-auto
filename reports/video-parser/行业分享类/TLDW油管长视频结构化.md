# 行业分享类 - TLDW 油管长视频结构化学习工具

## 核心工具/API

| 工具 | 作用 | 备注 |
|------|------|------|
| **TLDW** | AI高光片段+结构化摘要 | 仅支持YouTube |
| **xAI Grok 4 / Google Gemini** | AI分析引擎 | 二选一配置 |
| **Supadata Transcript API** | YouTube字幕获取 | 必填 |
| **Supabase** | 数据存储（分析结果/笔记） | 匿名/登录用户区分 |

---

## 步骤流程

### 本地部署

```bash
# 1. 克隆项目
git clone https://github.com/SamuelZ12/TLDW.git
cd TLDW

# 2. 安装依赖
npm install

# 3. 配置环境变量（.env.local）
cp .env.example .env.local
# 编辑 .env.local 填入：
# XAI_API_KEY=你的xAI密钥（必填）
# SUPADATA_API_KEY=你的Supadata密钥（必填）
# NEXT_PUBLIC_SUPABASE_URL=你的Supabase URL（必填）
# NEXT_PUBLIC_SUPABASE_ANON_KEY=你的Supabase密钥（必填）
# GEMINI_API_KEY=（可选，如用Gemini）
# AI_PROVIDER=grok（默认）或 gemini

# 4. 启动
npm run dev
# 访问 http://localhost:3000
```

### 使用流程

1. 粘贴YouTube视频URL
2. 选择模式：
   - **Smart（优质模式）**：AI深度分析，提取关键论点+核心案例+重要结论
   - **Fast（快速模式）**：快速抓取高频/高密度片段
3. 生成高光片段 + 结构化摘要
4. 记录Markdown笔记（带时间戳）
5. 跨视频笔记聚合（`/all-notes`页面）

---

## 适用场景

- ✅ **学术视频学习**：提取论文讲解、技术演讲的精华论点
- ✅ **产品发布会**：快速获取Keynote核心要点
- ✅ **长视频筛选**：100-200字快速预览判断视频价值
- ✅ **跨视频知识管理**：笔记聚合形成个人知识库
- ✅ **内容创作者素材收集**：提取经典语录和引用

---

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|------|
| 只能分析YouTube | 平台限制 | 如需B站/抖音，使用BibiGPT Skill |
| 匿名用户额度限制 | 速率限制 | 注册登录获取更多额度；配置 `UNLIMITED_VIDEO_USERS` 环境变量 |
| AI分析结果质量一般 | 使用了Fast模式 | 切换为Smart模式重新生成 |
| 无法获取字幕 | YouTube无字幕 | TLDW依赖Transcript API，无字幕视频无法处理 |
| Grok/Gemini API Key失效 | 免费额度耗尽 | 切换AI Provider或充值API额度 |

### Smart vs Fast 模式对比

| 维度 | Smart（优质模式） | Fast（快速模式） |
|------|------------------|-----------------|
| 分析深度 | 深度理解内容逻辑 | 频率/密度优先 |
| 输出质量 | 高价值片段+论证结构 | 快速获取大致内容 |
| 生成速度 | 较慢（5-10分钟） | 较快（1-2分钟） |
| 适用场景 | 重要/专业视频 | 快速筛选/预览 |

---

## 技术架构亮点

- **AI Pipeline**：`lib/ai-processing.ts` 处理transcript分片+prompt构建+结果聚合
- **Zod schema验证**：确保AI输出格式统一，便于程序处理
- **aggressive缓存**：已分析视频不再重复计费
- **安全防护**：CSP/HSTS防XSS、CSRF保护、IP哈希限流

---

## 参考链接

- GitHub仓库：https://github.com/SamuelZ12/TLDW
- 项目发布：2025年11月25日
- 部署推荐：Vercel
