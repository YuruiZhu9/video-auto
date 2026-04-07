# 技术教程类 - 视频RAG语义搜索方案

> 更新日期：2026-03-22
> 维护者：小M

---

## 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| yt-dlp | 多平台视频下载（含字幕） |
| Whisper (local/API) | 音频转文字 |
| FFmpeg | 音频提取、视频切割 |
| LLM (GPT/Claude/Gemini/Qwen) | 语义分块 + 索引生成 |
| 向量数据库（ChromaDB/Milvus） | 语义向量存储与检索 |
| OpenClaw scripts | 管道自动化 |

---

## 一、方案概述

视频 RAG（Retrieval-Augmented Generation）将视频内容转化为可语义检索的知识库，适合：

- **大量技术视频学习**：从上百个视频中找到相关讲解
- **代码定位**：搜索"某个错误怎么解决"，直接定位到视频时间戳
- **知识问答**：基于视频内容回答专业问题
- **内容审核**：检索包含特定技术内容的视频片段

```
视频文件/URL
    ↓
下载（yt-dlp）
    ↓
音频提取（FFmpeg）
    ↓
转录（Whisper）→ 带时间戳的文字稿
    ↓
语义分块（LLM）→ 按主题/章节切分
    ↓
向量化（Embedding）→ 存入向量数据库
    ↓
语义检索 → 用户Query → Top-K 相关片段 → 时间戳定位
```

---

## 二、完整实施流程

### 2.1 环境准备

```bash
# 安装核心工具
pip install whisper openai chromadb tiktoken
pip install -U "openai-whisper"
brew install yt-dlp ffmpeg  # macOS
# apt install yt-dlp ffmpeg  # Ubuntu

# 可选：向量数据库
pip install chromadb  # 轻量级，本地文件存储
# 或 Milvus（生产级）
```

### 2.2 Step 1：视频下载 + 字幕提取

```python
import subprocess
import os

def download_video(url, output_dir="/workspace/video-rag/input"):
    """下载视频（含字幕）"""
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "yt-dlp",
        "--write-subs", "--write-auto-subs",
        "--sub-lang", "zh-Hans,zh-Hant,en",
        "-o", f"{output_dir}/%(title)s.%(ext)s",
        url
    ]
    subprocess.run(cmd, check=True)
    return f"{output_dir}/"

def extract_audio(video_path, audio_path=None):
    """提取音频"""
    if audio_path is None:
        audio_path = video_path.rsplit('.', 1)[0] + '.mp3'
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "libmp3lame", "-q:a", "2",
        "-y", audio_path
    ], check=True, capture_output=True)
    return audio_path
```

### 2.3 Step 2：Whisper 转录（带时间戳）

```python
import whisper

def transcribe_with_timestamps(audio_path, model_size="medium"):
    """Whisper转录，保留时间戳"""
    model = whisper.load_model(model_size)  # tiny/base/medium/large-v3
    
    result = model.transcribe(
        audio_path,
        language="zh",  # 中文优先
        word_timestamps=True,  # 保留词级时间戳
        verbose=False,
    )
    
    # 提取段落级时间戳
    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip(),
        })
    
    return segments

def segments_to_file(segments, output_path):
    """导出为带时间戳的SRT格式"""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            f.write(f"{i}\n{start} --> {end}\n{seg['text']}\n\n")

def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
```

### 2.4 Step 3：语义分块（关键步骤）

**普通分块（按长度）：**
```python
def chunk_segments(segments, max_chars=500, overlap=50):
    """简单按字符数分块，保留时间戳"""
    chunks = []
    current_text = ""
    current_start = None
    current_end = 0
    
    for seg in segments:
        if len(current_text) + len(seg["text"]) > max_chars:
            # 保存当前块
            chunks.append({
                "text": current_text.strip(),
                "start": current_start,
                "end": current_end,
            })
            # 滑动窗口
            current_text = current_text[-overlap:] + seg["text"]
            current_start = segments[len(chunks) - 1]["start"] if chunks else seg["start"]
        else:
            current_text += seg["text"]
            if current_start is None:
                current_start = seg["start"]
        current_end = seg["end"]
    
    if current_text.strip():
        chunks.append({
            "text": current_text.strip(),
            "start": current_start,
            "end": current_end,
        })
    return chunks
```

**LLM智能分块（推荐）：**
```python
def smart_chunk_with_llm(transcript_text, video_title, llm_api_key):
    """使用LLM按语义章节智能分块"""
    import openai
    
    prompt = f"""请将以下视频文字稿按语义章节进行分块。
    
视频标题：{video_title}

要求：
1. 每个块代表一个独立的知识点或主题
2. 每个块300-600字
3. 块之间主题要有明显区分
4. 返回JSON数组格式

输出格式：
[
  {{"title": "块标题", "content": "块内容摘要", "start_approx": "mm:ss", "end_approx": "mm:ss"}},
  ...
]

文字稿内容：
{transcript_text[:15000]}  // 限制长度
"""
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    import json
    return json.loads(response.choices[0].message.content)
```

### 2.5 Step 4：向量化 + 存储

```python
import chromadb
from openai import OpenAI as OA

class VideoRAG:
    def __init__(self, persist_dir="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding = OA(api_key=os.environ["OPENAI_API_KEY"]).embeddings
        self.collection = self.client.get_or_create_collection(
            name="video_knowledge",
            metadata={"description": "技术视频知识库"}
        )
    
    def add_video(self, video_id, video_title, chunks):
        """向知识库添加一个视频"""
        for i, chunk in enumerate(chunks):
            chunk_id = f"{video_id}_{i}"
            embedding = self.embedding.create(
                input=chunk["content"],
                model="text-embedding-3-small"
            )["data"][0]["embedding"]
            
            self.collection.add(
                ids=chunk_id,
                embeddings=[embedding],
                documents=[chunk["content"]],
                metadatas=[{
                    "video_id": video_id,
                    "video_title": video_title,
                    "chunk_title": chunk.get("title", ""),
                    "start": chunk.get("start", 0),
                    "end": chunk.get("end", 0),
                }]
            )
    
    def search(self, query, top_k=5):
        """语义检索，返回相关片段"""
        query_embedding = self.embedding.create(
            input=query,
            model="text-embedding-3-small"
        )["data"][0]["embedding"]
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        return results
```

### 2.6 Step 5：检索 + 时间戳定位

```python
def search_video(query, video_rag, video_path=None):
    """语义搜索 + 输出时间戳"""
    results = video_rag.search(query, top_k=5)
    
    print(f"📚 检索到 {len(results['ids'][0])} 个相关片段：\n")
    
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        start = format_time(meta["start"])
        end = format_time(meta["end"])
        
        print(f"🎬 《{meta['video_title']}》")
        print(f"   ⏱ {start} → {end}")
        print(f"   📌 {meta['chunk_title']}")
        print(f"   💬 {results['documents'][0][i][:200]}...")
        print()
    
    # 可选：裁剪相关片段为独立小视频
    if video_path:
        for meta in results["metadatas"][0]:
            clip_path = f"clip_{meta['start']:.0f}s.mp4"
            subprocess.run([
                "ffmpeg", "-i", video_path,
                "-ss", str(meta["start"]),
                "-to", str(meta["end"]),
                "-c", "copy", clip_path
            ], check=True)
            print(f"✂️  裁剪片段：{clip_path}")

def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"
```

---

## 三、进阶增强

### 3.1 多模态RAG（视频帧+字幕联合索引）

```python
def extract_keyframes(video_path, n_frames=10):
    """均匀提取关键帧"""
    import subprocess
    frames = []
    for i in range(n_frames):
        output = f"/tmp/frame_{i:04d}.jpg"
        time = i * 60  # 假设视频总长60*n_frames秒
        subprocess.run([
            "ffmpeg", "-ss", str(time), "-i", video_path,
            "-vframes", "1", "-q:v", "2", "-y", output
        ], check=True)
        frames.append({"time": time, "path": output})
    return frames

def multi_modal_index(video_id, video_path, transcript_chunks, keyframes):
    """视频帧 + 字幕双索引"""
    # 1. 字幕块索引
    for chunk in transcript_chunks:
        # ... 向量化存入ChromaDB (collection: "transcripts")
        pass
    
    # 2. 关键帧索引
    for frame in keyframes:
        frame_desc = images_understand(image_info=[{
            "file": frame["path"],
            "prompt": "描述画面中的主要内容（代码/界面/图表/文字）"
        }])
        # ... 向量化存入ChromaDB (collection: "keyframes")
```

### 3.2 问答模式（基于视频内容）

```python
def answer_from_video(question, video_rag, transcript_full):
    """基于视频内容回答问题"""
    # 1. 语义检索相关片段
    results = video_rag.search(question, top_k=5)
    
    # 2. 构建上下文
    context = "\n\n".join([
        f"[{meta['video_title']} {format_time(meta['start'])}]\n{doc}"
        for meta, doc in zip(results["metadatas"][0], results["documents"][0])
    ])
    
    # 3. LLM 生成回答
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": f"""基于以下视频内容回答问题。如果视频内容不能回答问题，请说明。
            
问题：{question}

视频内容：
{context}

回答（引用来源片段）：
"""
        }],
    )
    
    answer = response.choices[0].message.content
    sources = [
        {
            "title": meta["video_title"],
            "time": format_time(meta["start"]),
            "excerpt": doc[:150]
        }
        for meta, doc in zip(results["metadatas"][0], results["documents"][0])
    ]
    return answer, sources
```

---

## 四、适用场景

| 场景 | 方案 | 说明 |
|------|------|------|
| 个人技术视频学习库 | 本地 ChromaDB + Whisper | 隐私安全，完全免费 |
| 团队共享知识库 | Milvus + API服务 | 支持多用户并发 |
| 代码错误搜索 | 字幕RAG + 时间戳 | 直接定位到出错讲解 |
| 竞品视频分析 | 批量处理 + 多模态 | 帧+字幕联合索引 |
| 视频会议回顾 | 实时录制 + Whisper | 会议内容可检索 |

---

## 五、避坑指南

### 坑1：Whisper中文识别率低
**解决**：
```python
# 使用 large-v3 模型 + 中文prompt
model.transcribe(audio, language="zh", initial_prompt="以下是中文普通话音频转录")

# 或使用 faster-whisper（速度更快，精度相近）
from faster_whisper import WhisperModel
model = WhisperModel("large-v3", compute_type="int8")
```

### 坑2：长视频转录OOM
**解决**：分段转录后合并
```bash
# 每10分钟切一段
ffmpeg -i input.mp4 -f segment -segment_time 600 -c copy chunk_%03d.mp4
# 分别转录后合并
```

### 坑3：向量检索结果不相关
**解决**：使用更好的Embedding模型
```python
# 推荐使用中文优化模型
# OpenAI: text-embedding-3-small (多语言支持好)
# 国内: M3E (中文优化，本地部署) / ZhipuAI embedding
```

### 坑4：ChromaDB数据丢失
**解决**：配置持久化 + 定期备份
```python
client = chromadb.PersistClient(path="./chroma_backup")
# 定期备份整个目录
subprocess.run(["cp", "-r", "./chroma_backup", f"./backup_{date}"])
```

---

## 六、OpenClaw 集成

在 OpenClaw 中自动化视频RAG流程：

```python
# === Agent自动化脚本 ===
# 1. 接收视频URL
video_url = user_input  # "https://b站视频链接"

# 2. 下载+转录
exec(f"yt-dlp --write-subs -o 'input/%(title)s.%(ext)s' '{video_url}'")
exec("ffmpeg -i input.mp4 -vn -acodec libmp3lame audio.mp3")
transcript = exec("whisper audio.mp3 --model medium --language zh")

# 3. 结构化分析
result = videos_understand(videos_info=[{
  "file": "input.mp4",
  "prompt": "提取关键步骤、知识点、时间戳"
}])

# 4. 存入知识库
# (调用上述 RAG pipeline)

# 5. 返回结果
return f"✅ 视频已解析并入库！可开始语义检索。\n摘要：{result.content[:500]}"
```

---

## 七、工具对比

| 工具 | 用途 | 成本 | 部署 |
|------|------|------|------|
| Whisper | 音频转文字 | 本地免费/API付费 | 本地/云 |
| faster-whisper | 快速转录 | 本地免费 | GPU加速 |
| ChromaDB | 向量存储 | 本地免费 | 轻量 |
| Milvus | 生产向量库 | 开源免费 | 需要服务器 |
| Qdrant | 向量检索 | 开源免费 | Docker |
| OpenAI Embedding | 向量化 | 按Token计费 | 云API |
| ZhipuAI Embedding | 中文向量化 | 低成本 | 云API |

---

*更新时间：2026-03-22*
