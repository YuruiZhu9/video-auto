# AnythingLLM — 本地视频/音频 RAG 知识库搭建方案

> 🤖 视频解析方法总结Agent（小M）
> 📅 更新日期：2026-04-02
> 📁 文档路径：`/workspace/reports/video-parser/通用工具/AnythingLLM本地RAG知识库解析.md`

---

## 核心工具/API

- **AnythingLLM**：Mintplex Labs 开源的全栈 AI 应用平台
  - GitHub：https://github.com/Mintplex-Labs/anything-llm
  - 官网：https://anythingllm.com/
  - 文档：https://docs.anythingllm.com/
  - 核心定位：一站式本地 ChatGPT + RAG 知识库，支持文档/视频/音频

- **AnythingLLM 支持的媒体**：
  - 文档：PDF、Word、Markdown、TXT
  - 音频：MP3、WAV、M4A（Whisper 转录后入库）
  - 视频：MP4、MOV（提取音频 + 字幕 + 截帧后入库）
  - 网页：URL 自动抓取

- **RAG 技术栈**：
  - LLM 支持：Ollama（本地）/ OpenAI / Azure OpenAI / Anthropic / Google Gemini
  - 向量数据库：LanceDB（内置）/ Qdrant / Chroma / Pinecone
  - 嵌入模型：Embedded（内置）/ OpenAI / Ollama

---

## 步骤流程

### AnythingLLM 视频知识库搭建

```
Step 1 → 安装 AnythingLLM
          # Docker（推荐）
          docker pull mintplexlabs/anythingllm:latest
          docker run -d -p 3000:3000 \
            -v $HOME/anythingllm:/app/server/storage \
            mintplexlabs/anythingllm

          # 或源码安装
          git clone https://github.com/Mintplex-Labs/anything-llm
          cd anything-llm && npm install && npm run setup

Step 2 → 配置 LLM 提供者（推荐 Ollama 本地）
          Settings → LLM Preferences
          - Provider: Ollama
          - Base URL: http://localhost:11434
          - Model: llama3.2 或 mixtral
          - Embedder: Ollama (nomic-embed-text)

Step 3 → 上传视频文件
          Workspace → Add Documents → 上传 video.mp4
          AnythingLLM 自动：
          1. 提取视频音频 → Whisper 转录 → 文本分块
          2. 可选：截帧 + 图像描述 → 存入向量库
          3. 文本块向量化 → 存入向量数据库

Step 4 → 视频问答
          # 在 Workspace 中提问
          User: "视频中关于部署的部分讲了什么？"
          AnythingLLM → RAG 检索 → LLM 回答
          # 输出：引用原文 + 回答 + 时间戳（如果字幕有）

Step 5 → 批量导入多个视频
          # 创建一个"技术教程"Workspace
          # 批量上传 B站/YouTube 下载的视频
          # 建立跨视频的知识网络
```

### API 方式集成（开发者）

```
Step 1 → 获取 API Key
          Settings → API Keys → Create new key

Step 2 → Python 调用
          import requests

          # 创建 Workspace
          requests.post("http://localhost:3001/api/v1/workspace", 
              headers={"Authorization": "Bearer YOUR_KEY"},
              json={"name": "video-tutorials"})

          # 上传文档（视频转音频后上传）
          requests.post(".../document/upload", 
              files={"file": open("audio.wav", "rb")})

          # 问答
          requests.post(".../workspace/{id}/chat",
              json={"message": "视频讲了什么？"})
```

---

## 适用场景

- **个人视频知识库**：将所有技术教程视频转成可问答的知识库
- **团队视频资产沉淀**：团队积累的视频教程、会议录像，转化为可检索的企业知识
- **跨视频综合分析**：上传多个相关视频，询问"这些视频对某个主题的观点有何异同"
- **隐私敏感视频**：完全本地部署，无需上传云端，适合处理内部培训视频
- **视频档案管理**：历史视频内容检索，不需要完整观看才能找到答案

---

## 避坑指南

- **视频需转音频**：AnythingLLM 不能直接理解视频，必须先提取音频再用 Whisper 转录
- **截帧需额外处理**：默认只处理音频/文本，视频帧需要手动截取并上传为图片
- **上下文窗口限制**：Ollama 模型上下文窗口有限，长视频字幕需要适当分块（建议每段 < 2000 token）
- **向量检索质量依赖分块策略**：视频字幕分块过小→失去上下文；过大→检索精度下降，建议按句子自然断点分块
- **中文模型**：Ollama 中中文能力强的模型较少，建议用 mixtral 或 qwen2.5 等中文优化模型
- **首次索引慢**：视频越多，首次向量索引时间越长，后续检索速度正常

---

## 与 OpenClaw 的互补方案

AnythingLLM 非常适合作为 OpenClaw `videos_understand` 的持久化知识层：

```
OpenClaw + AnythingLLM 完整视频知识管理方案：

处理阶段（OpenClaw）：
  video URL → yt-dlp 下载
           → FFmpeg 提取音频
           → Whisper 转录
           → videos_understand 深度分析
           → 结构化 Markdown 输出

存储阶段（AnythingLLM）：
  音频.wav + 分析报告.md → 上传到 AnythingLLM Workspace
                         → 向量化存储
                         → 建立视频知识库

检索阶段（OpenClaw + AnythingLLM）：
  用户提问 → OpenClaw 分析意图
          → AnythingLLM RAG 检索相关视频内容
          → OpenClaw 整合回答 + 时间戳引用
```

---

## 参考链接

- GitHub：https://github.com/Mintplex-Labs/anything-llm
- 官方文档：https://docs.anythingllm.com/
- 中文教程（腾讯云）：https://cloud.tencent.com/developer/article/2526583
- RAG 实践（稀土掘金）：https://juejin.cn/post/7509702769822318646

---

## AnythingLLM vs 其他本地 RAG 方案对比

| 维度 | AnythingLLM | Dify | MaxKB |
|------|------------|------|-------|
| **上手难度** | ⭐⭐ 简单 | ⭐⭐⭐ 中等 | ⭐⭐ 简单 |
| **视频支持** | ✅（音频） | ⚠️ 需插件 | ⚠️ 需插件 |
| **本地部署** | ✅ 完整 | ✅ 完整 | ✅ 完整 |
| **界面美观度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **API 开放** | ✅ | ✅ | ✅ |
| **多租户** | ✅ | ✅ | ✅ |
| **视频最佳拍档** | FFmpeg+Whisper | FFmpeg+Whisper | FFmpeg+Whisper |

*AnythingLLM 是目前最适合非技术用户搭建本地视频知识库的方案，推荐配合 OpenClaw 的视频处理流程使用。*
