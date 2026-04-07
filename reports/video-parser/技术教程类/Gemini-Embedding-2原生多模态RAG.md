# 技术教程类 - Gemini Embedding 2 原生多模态 RAG

> 🤖 更新：2026-03-27
> 📍 来源：Google Gemini Embedding 2（2026年3月10日发布）

---

## 核心工具/API

| 工具 | 类型 | 能力描述 |
|------|------|---------|
| **Gemini Embedding 2** | Google API / SDK | 首个原生多模态嵌入模型，将文本、图片、视频、音频统一映射到单一向量空间 |
| **Python Google GenAI SDK** | SDK | 官方 Python 客户端，支持 `genai.Client` 调用嵌入 API |
| **Vertex AI** | 企业级平台 | Google Cloud 企业版，支持 VPC-SC、CMEK、IAM |
| **AI Studio** | 开发平台 | 原型开发个人开发者版，含免费额度 |

---

## 核心参数规格

| 参数 | 规格 |
|------|------|
| **模型标识** | `gemini-embedding-exp-03-07` |
| **向量维度** | 默认 3,072 维；支持 MRL 降至 1,536 / 768 / 256 维 |
| **单请求最大视频时长** | 120 秒（MP4 / MOV） |
| **多模态统一空间** | 文本、图片、视频、音频 → 同一向量索引 |
| **计费** | 预览期免费，预计 GA 后按量收费 |

---

## 步骤流程

### 完整视频 RAG 流水线

```
数据摄入 → Gemini Embedding 2 API → 向量数据库 → 检索 → LLM 生成
视频文件(Mp4)   统一向量               pgvector/Pinecone/Weaviate  重排序  回答
```

### Python 调用示例

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
from google.genai import types

# 嵌入视频
video = types.Part.from_uri(
    file_uri="gs://my-bucket/meeting-recording.mp4",
    mime_type="video/mp4"
)

result = client.models.embed_content(
    model="gemini-embedding-exp-03-07",
    contents=[video],
    config={
        "output_dimensionality": 768,  # MRL 降维
        "task_type": "RETRIEVAL_DOCUMENT"  # 索引用
    }
)
print(f"视频向量维度: {len(result.embeddings[0].values)}")
```

### 检索任务类型策略

| task_type | 用途 |
|-----------|------|
| `RETRIEVAL_DOCUMENT` | 视频/文档索引（入库时使用）|
| `RETRIEVAL_QUERY` | 查询编码（搜索时使用，推荐不对称检索）|
| `SEMANTIC_SIMILARITY` | 跨模态相似度比较 |
| `CLASSIFICATION` | 自动分类 |
| `CLUSTERING` | 主题聚类分组 |

**最佳实践**：入库用 `RETRIEVAL_DOCUMENT`，检索用 `RETRIEVAL_QUERY`，可提升非对称检索精度。

---

## 适用场景

- **企业视频知识库**：会议录像、培训视频、产品演示的统一语义搜索
- **跨模态检索**：用文字描述"找出包含这个图表的视频"，无需视频-文本转换
- **多模态 RAG**：文本+图片+视频+音频统一召回，无需分别建索引
- **视频去重/相似度检测**：同一向量空间内计算视频间相似度
- **长视频智能切片**：聚类分析自动发现视频内部主题切换点
- **移动端轻量检索**：MRL 256 维向量适配边缘设备

---

## 避坑指南

1. **视频时长限制（120秒）**
   - 超长视频需先切分 → 每段独立嵌入 → 段级检索
   - 可按场景/章节预先切分，再逐段入库

2. **向量维度与向量库兼容性**
   - 确认向量库支持 3072 维（pgvector ✅ / Pinecone ✅ / Weaviate ✅）
   - 存储成本高时先用 256 维做初筛，再用 3072 维精排

3. **MRL 两阶段检索**
   - 第一阶段：256 维快速过滤候选集（存储成本降低 87%）
   - 第二阶段：3072 维重排序 top 结果

4. **数据安全审查**
   - 视频上传 Google API 需做 PII 脱敏处理
   - 企业场景优先用 Vertex AI 而非 AI Studio

5. **GCS URI vs 本地文件**
   - API 需 GCS URI（`gs://bucket/path.mp4`）或公开 HTTPS URL
   - 本地文件需先上传至 GCS 或转为公开 URL

---

## 与现有方案的对比

| 对比维度 | 传统方案（视频→文本→嵌入） | Gemini Embedding 2 |
|----------|--------------------------|-------------------|
| **处理流程** | 语音识别→文本切分→文本嵌入 | 视频直接嵌入 |
| **信息损失** | 视频画面信息丢失 | 保留完整视觉语义 |
| **跨模态检索** | 文本→文本 | 文字搜视频/图片搜视频 |
| **API 成本** | Whisper + Embedding API 两次调用 | 单次调用 |
| **预览期价格** | 按调用量付费 | 免费 |
| **成熟度** | 成熟稳定 | 新发布（预览期）|

---

## 推荐组合：OpenClaw + Gemini Embedding 2

```
yt-dlp 下载视频 → ffmpeg 切分(每段<120s) → Gemini Embedding 2 入库
                                                     ↓
用户查询 → Gemini Embedding 2 检索 → videos_understand 深度理解 → 结构化回答
```

---

## 参考链接

- [Gemini Embedding 2 官方博客](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-embedding-2/)
- [Gemini API 文档](https://ai.google.dev/gemini-api/docs/models/gemini-embedding-2-preview)
- [Vertex AI 文档](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/embedding-2)
- [ JangWook 实战教程](https://jangwook.net/en/blog/en/gemini-embedding-2-multimodal-rag-pipeline/)

---

*本文件由视频解析方法总结Agent 自动生成 · 2026-03-27*
