# 通用工具 — 多模态RAG视频语义检索全链路方案

> 🤖 视频解析方法总结Agent（小M）
> 📅 新增日期：2026-04-03（第二周更新）
> 📁 归属分类：通用工具

---

## 核心工具/API

- **FFmpeg**：视频抽帧 + 音频提取
- **Whisper**：音频转文字（带时间戳 SRT）
- **CLIP / BLIP**：图像帧向量化（多模态 Embedding）
- **BridgeTower / SigLIP**：跨模态对齐（文本↔图像）
- **Qwen-VL / Gemini Embedding 2**：原生多模态向量
- **Milvus / Chroma / Qdrant**：向量数据库（视频片段索引）
- **LLM（GPT-4 / Gemini / Qwen）**：检索后答案生成

---

## 适用场景

- **企业内部视频知识库**：用自然语言提问，定位视频中的相关片段
- **课程视频检索**："视频里讲Redis主从复制的第几分钟？"
- **会议录像分析**："提到了哪些行动项？按时间顺序列出"
- **产品 Demo 库**：语义搜索"AI修图操作演示"
- **监控视频语义检索**（非实时）："找出所有含火灾迹象的片段"

---

## 步骤流程（全链路六步）

### Step 1：视频预处理与分割

```bash
# 均匀截帧（每5秒1帧）+ 音频提取
ffmpeg -i video.mp4 -vf "fps=0.2,scale=720:-1" frames/frame_%04d.jpg
ffmpeg -i video.mp4 -vn -acodec libmp3lame audio.mp3
```

**分割策略**：
- **固定时长分割**：每 30s / 60s 为一个 Chunk（简单，适合短视频）
- **语义分割**：用 Whisper 转录 → 按段落/话题切换点分割（推荐）
- **场景检测分割**：用 `scenedetect` 工具按镜头切换分割（适合电影/演示）

### Step 2：多模态内容提取

```python
# 音频转文字 + 时间戳
import whisper
model = whisper.load_model("base")
result = model.transcribe("audio.mp3", word_timestamps=True)
# result["segments"] 含每句话的 start/end 时间

# 图像帧用 CLIP 向量化
from PIL import Image
import torch, clip
model, preprocess = clip.load("ViT-B/32")

frame_vectors = []
for frame_path in sorted(glob("frames/*.jpg")):
    image = preprocess(Image.open(frame_path)).unsqueeze(0)
    with torch.no_grad():
        vec = model.encode_image(image)
    frame_vectors.append(vec.numpy().flatten())
```

### Step 3：向量索引构建

```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client()
collection = client.create_collection("video_rag")

for i, (chunk_text, frame_vec, timestamp) in enumerate(chunks):
    collection.add(
        ids=[f"chunk_{i}"],
        embeddings=[frame_vec.tolist()],
        metadatas=[{
            "timestamp": timestamp,
            "text": chunk_text,
            "video_path": "video.mp4"
        }]
    )
```

**多模态融合策略**（三种）：
1. **早期融合**：帧向量 + 音频文本向量直接拼接（简单）
2. **中期融合**：CLIP 图向量 + Whisper 文本向量分别检索后合并（推荐）
3. **晚期融合**：分别检索图/文结果，按相关性分数加权排序（灵活）

### Step 4：语义检索

```python
# 自然语言查询 → 向量 → 检索相关片段
query_vec = model.encode_text(clip.encode_text(query))

results = collection.query(
    query_embeddings=[query_vec.tolist()],
    n_results=5
)

# 输出：相关片段时间戳 + 文字摘要
for r in results["metadatas"][0]:
    print(f"[{r['timestamp']}] {r['text'][:200]}")
```

### Step 5：答案生成（RAG）

```python
# 检索相关片段
context_chunks = retrieve_relevant_chunks(query, top_k=5)

# 构造Prompt + LLM生成答案
prompt = f"""基于以下视频片段回答问题。

问题：{user_query}

相关片段：
{chr(10).join(context_chunks)}

请给出准确答案，并注明来源时间戳。
"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role":"user","content":prompt}]
)
```

### Step 6：时序上下文增强（可选）

对于需要多片段关联的问题（如"从介绍到总结的完整流程"），用时间窗口扩大检索范围：

```python
# 在检索到的片段前后各扩展 N 秒
window_seconds = 30
result_with_context = []
for chunk in results["metadatas"][0]:
    ts = float(chunk["timestamp"])
    extended_chunks = find_chunks_in_window(ts - window_seconds, ts + window_seconds)
    result_with_context.extend(extended_chunks)
```

---

## 避坑指南

### 1. 固定截帧导致语义断节
**问题**：每5秒一帧可能恰好切在两句话之间，检索召回率低。
**解决**：使用 Whisper 段落边界作为分割点，保证语义完整性。

### 2. CLIP 不理解中文视频内容
**问题**：中文界面/字幕在 CLIP 视觉理解中表现差。
**解决**：用 Whisper 文本作为主要检索向量，图像向量辅助视觉场景验证。

### 3. 向量数据库查询慢（HNSW vs IVF）
**问题**：海量视频帧向量，检索延迟高。
**解决**：HNSW（高速召回）优先；IVF-PQ（压缩存储）适合大规模部署。

### 4. 多模态检索"语义漂移"
**问题**：文本查询和视觉内容的 Embedding 空间不对齐。
**解决**：用 BridgeTower / SigLIP 等跨模态对齐模型，或 Gemini Embedding 2 原生多模态。

### 5. 长视频索引成本高
**问题**：1小时视频≈720帧，存储和计算成本高。
**解决**：关键帧优先（I帧）；720p 降采样到 360p；按场景切换点稀疏采样。

---

## 全链路工具链对比

| 环节 | 推荐工具 | 备选 |
|------|---------|------|
| 抽帧 | FFmpeg | OpenCV（Python）|
| 音频转录 | Whisper（本地）| audios_understand（API）|
| 图像向量化 | CLIP ViT-L/14 | BLIP-2 / SigLIP |
| 文本向量化 | BGE-m3 / text-embedding-3 | Gemini Embedding 2 |
| 多模态对齐 | BridgeTower | Qwen-VL Embedding |
| 向量数据库 | Qdrant（支持混合检索）| Chroma（轻量）/ Milvus（大规模）|
| 答案生成 | GPT-4.1 / Gemini 2.5 Pro | Qwen2.5-72B-Instruct |
| 场景检测 | scenedetect |FFmpeg select filter |

---

## 参考链接

- 腾讯云多模态 RAG 实践：https://cloud.tencent.com/developer/article/2485182
- 阿里云 OpenSearch 视频 RAG：https://developer.aliyun.com/article/1670631
- CLIP + BLIP Embedding RAG：https://github.com/pydaxing/clip_blip_embedding_rag
- All-in-RAG 全栈指南：https://datawhalechina.github.io/all-in-rag/
- RzenEmbed 多模态 Embedding：https://www.sohu.com/a/960579688_100279313
- scenedetect（场景检测）：https://github.com/Breakthrough/PySceneDetect
