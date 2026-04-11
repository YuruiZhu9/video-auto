# 技术教程类 - Langbase Video Wisdom Extraction Tool 完整解析

> 更新日期：2026-04-11
> 来源：https://langbase.com/docs/guides/video-wisdom-extractor

---

## 核心工具/API

### Langbase SDK
- **包**：`langbase`（`npm install langbase`）
- **用途**：连接 AI Pipes，流式返回结果
- **调用方式**：`pipe.streamText()` 流式生成

### 8 个专业化 AI Pipes

| Pipe 名称 | 用途 | 输出类型 |
|-----------|------|---------|
| **YouTube Videos Q/A Pipe** | 问答：针对视频内容提问 | 文本回答 |
| **Summarize YouTube Video Pipe** | 生成视频摘要 | 段落摘要 |
| **Main Ideas Extractor Pipe** | 提取主要观点和关键点 | 列表 |
| **List Interesting Facts Pipe** | 提取有趣的事实 | 列表 |
| **Wow Moments Extractor Pipe** | 捕捉高光时刻 | 列表 |
| **Video Tweets Extractor Pipe** | 将视频内容转化为推文 | 社媒内容 |
| **Video Recommendations Extractor Pipe** | 提供参考资源链接 | 列表 |
| **List Quotes from Video Pipe** | 提取名言/关键引述 | 列表 |

### 环境变量

```bash
LB_SUMMARIZE_PIPE_KEY          # 摘要
LB_GENERATE_PIPE_KEY           # 通用生成
LB_MAIN_IDEAS_PIPE_KEY         # 主要观点
LB_FACTS_PIPE_KEY              # 有趣事实
LB_WOW_PIPE_KEY                # 高光时刻
LB_TWEETS_PIPE_KEY             # 社媒推文
LB_RECOMMENDATION_PIPE_KEY     # 参考资源
LB_QUOTES_PIPE_KEY             # 名言引述
```

---

## 步骤流程

### Step 0：创建 Next.js 应用

```bash
npx create-next-app@latest video-wisdom
# 或使用 pnpm
pnpm create-next-app@latest video-wisdom
```

### Step 1：安装 Langbase SDK

```bash
npm install langbase
# 或 pnpm add langbase
```

### Step 2：Fork AI Pipes 并获取密钥

从 Langbase Dashboard Fork 8 个 AI Pipes，每个 Pipe 的 API Tab 中获取对应密钥。

### Step 3：创建智慧提取 API 路由

**① 定义 GenerationType 枚举：**
```typescript
enum GenerationType {
  Generate = 'generate',
  Summarize = 'summarize',
  Quotes = 'quotes',
  Recommendation = 'recommendation',
  MainIdeas = 'mainIdeas',
  Facts = 'facts',
  Wow = 'wow',
  Tweets = 'tweets'
}
```

**② 环境变量辅助函数：**
```typescript
const getEnvVar = (type: GenerationType) => {
  switch (type) {
    case GenerationType.Generate: return process.env.LB_GENERATE_PIPE_KEY;
    case GenerationType.Summarize: return process.env.LB_SUMMARIZE_PIPE_KEY;
    case GenerationType.Quotes: return process.env.LB_QUOTES_PIPE_KEY;
    case GenerationType.Recommendation: return process.env.LB_RECOMMENDATION_PIPE_KEY;
    case GenerationType.MainIdeas: return process.env.LB_MAIN_IDEAS_PIPE_KEY;
    case GenerationType.Facts: return process.env.LB_FACTS_PIPE_KEY;
    case GenerationType.Wow: return process.env.LB_WOW_PIPE_KEY;
    case GenerationType.Tweets: return process.env.LB_TWEETS_PIPE_KEY;
  }
};
```

**③ 请求校验（Zod）：**
```typescript
const requestBodySchema = z.object({
  prompt: z.string(),
  transcript: z.string().trim().min(1),
  type: z.enum([...])
});
```

**④ 生成响应函数：**
```
1. 用 API key 初始化 Pipe
2. 构建流输入（transcript 作为变量或用户输入）
3. 调用 pipe.streamText() 生成流
4. 以 Readable 格式返回流
```

---

## 适用场景

| 场景 | 推荐 Pipe |
|------|----------|
| 快速了解视频核心内容 | Summarize |
| 深度理解并追问视频细节 | Q/A |
| 提取学习笔记关键点 | MainIdeas |
| 了解视频中有趣冷知识 | Interesting Facts |
| 制作精彩片段剪辑 | Wow Moments |
| 将视频内容分享到社媒 | Video Tweets |
| 获取视频延伸学习资源 | Recommendations |
| 保存视频金句用于引用 | Quotes |

---

## 避坑指南

| 问题 | 解决方案 |
|------|---------|
| transcript 为空 | 需先通过 yt-dlp 提取字幕作为输入 |
| Pipe key 未配置 | 逐一检查 8 个环境变量是否正确设置 |
| 流式响应处理错误 | 使用 `ReadableStream` 正确处理 Langbase 流式返回 |
| 多个 Pipe 类型处理混乱 | 用枚举 + switch 统一分发，避免 if-else 地狱 |
| 未验证请求体 | 必须使用 Zod schema 校验，防止无效输入 |

---

## 完整 Pipeline 架构图

```
YouTube 视频 URL
     │
     ▼
 yt-dlp 提取字幕（VTT/SRT）
     │
     ▼
 Langbase SDK（8 个 Pipe）
     │
     ├─→ Q/A Pipe ──────────→ 问答
     ├─→ Summarize Pipe ────→ 摘要
     ├─→ MainIdeas Pipe ───→ 主要观点
     ├─→ Facts Pipe ────────→ 有趣事实
     ├─→ Wow Pipe ─────────→ 高光时刻
     ├─→ Tweets Pipe ───────→ 社媒推文
     ├─→ Recommendations ─→ 参考资源
     └─→ Quotes Pipe ───────→ 名言引述
```

---

## 参考链接

- 官方指南：https://langbase.com/docs/guides/video-wisdom-extractor
- 演示地址：https://videowisdom.langbase.dev/
- GitHub 源码：https://github.com/LangbaseInc/langbase/tree/main/examples/video-wisdom
- Summarize Pipe：https://langbase.com/examples/youtube-video-summarizer
- Q/A Pipe：https://langbase.com/examples/you-tube-videos-qn-a
- Main Ideas Pipe：https://langbase.com/examples/youtube-video-main-ideas-extractor
