# 视频标签自动化生成 Pipeline（推荐系统工程师视角）

> 🤖 视频解析方法总结Agent（小M）
> 📅 更新日期：2026-04-10（第十周）
> 📁 文档目录：`/workspace/reports/video-parser/技术教程类/`

---

## 背景

推荐系统的视频标签（Tag）是连接**内容理解**和**用户兴趣**的桥梁。
传统做法依赖人工打标或用户行为统计，冷启动问题严重。
本文提供一个**零门槛、低成本、可迭代**的视频标签自动化 Pipeline，
专为有 Python 基础、想转行推荐系统的工程师设计。

---

## 核心工具/API

| 工具 | 用途 | 成本 | 获取方式 |
|------|------|------|---------|
| **yt-dlp** | 视频下载 | 免费 | `pip install yt-dlp` |
| **FFmpeg** | 音频提取/截帧 | 免费 | 系统包管理安装 |
| **Whisper（CLI）** | 本地语音转文字 | 免费 | `pip install openai-whisper` |
| **Qwen-VL**（ModelScope） | 视觉理解+标签生成 | GPU成本 | ModelScope SDK |
| **BGE**（FlagEmbedding） | 文本向量编码 | 免费 | `pip install FlagEmbedding` |
| **FAISS** | 向量相似度检索 | 免费 | `pip install faiss-cpu` |
| **OpenClaw videos_understand** | 多模态视频理解 | 平台限制 | 内置工具 |

---

## 完整 Pipeline（5步）

### Step 1：视频下载（5分钟/100条）

```python
import subprocess
from pathlib import Path

def download_video(url: str, output_dir: str = "./videos") -> str:
    """下载YouTube/B站视频"""
    Path(output_dir).mkdir(exist_ok=True)
    cmd = [
        "yt-dlp",
        "-f", "best[height<=720]",  # 限制720p节省空间
        "--no-playlist",
        "-o", f"{output_dir}/%(id)s.%(ext)s",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # 从输出中提取文件名
    video_id = url.split("=")[-1]
    return f"{output_dir}/{video_id}.mp4"
```

**B站视频下载（需额外参数）：**
```bash
yt-dlp "https://www.bilibili.com/video/BV1xx411c7mD" \
  --format "bv*[height<=720]+ba/bv[height<=720]" \
  -o "./videos/%(id)s.%(ext)s"
```

### Step 2：音频提取 + Whisper 转录（5-30分钟/条，取决于长度）

```python
import whisper
import subprocess

def transcribe_video(video_path: str, model_size: str = "medium") -> dict:
    """Whisper本地转录，输出JSON包含文字稿+时间戳"""
    
    # 1. 提取音频（Whisper更偏好纯净音频）
    audio_path = video_path.replace(".mp4", ".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        audio_path
    ], capture_output=True)
    
    # 2. Whisper转录
    model = whisper.load_model(model_size)  # turbo/medium/large
    result = model.transcribe(audio_path, word_timestamps=True)
    
    return {
        "text": result["text"],
        "segments": result["segments"],  # 含时间戳
        "language": result.get("language", "unknown")
    }
```

**模型选择建议：**
- `turbo`：快（3x），英文质量好，中文一般
- `medium`：平衡（2x），中英文均可用
- `large`：慢（1x），最高质量，中文最强

### Step 3：关键帧提取

```python
import subprocess

def extract_keyframes(video_path: str, interval_sec: int = 30, 
                       output_dir: str = "./frames") -> list:
    """固定间隔截帧（每30秒1帧）"""
    Path(output_dir).mkdir(exist_ok=True)
    video_id = Path(video_path).stem
    
    # 获取视频时长
    probe = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ], capture_output=True, text=True)
    duration = float(probe.stdout.strip())
    
    # 固定间隔截帧
    frame_paths = []
    for t in range(0, int(duration), interval_sec):
        out_path = f"{output_dir}/{video_id}_t{t:04d}.jpg"
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(t), "-i", video_path,
            "-vframes", "1", "-q:v", "2",
            out_path
        ], capture_output=True)
        frame_paths.append(out_path)
    
    return frame_paths
```

**进阶：场景检测智能截帧（比固定间隔更精准）**
```bash
# FFmpeg 内置场景检测（--extra_frame_ratio 控制灵敏度）
ffmpeg -i video.mp4 -vf "select='gt(scene,0.3)',showinfo" \
  -vsync vfr frame_%04d.jpg
```

### Step 4：VL模型生成帧级标签（GPU必需）

```python
from modelscope import snapshot_download, AutoModelForCausalLM
from modelscope.msdatasets import MsDataset
import torch

def generate_frame_tags(frame_paths: list, batch_size: int = 4) -> list:
    """用Qwen-VL为每帧生成标签描述"""
    
    # 加载模型（ModelScope）
    model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen2-VL-7B-Instruct",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    frame_tags = []
    for i in range(0, len(frame_paths), batch_size):
        batch = frame_paths[i:i+batch_size]
        # 批量处理（注意显存限制）
        results = model.batch_predict(batch)  # 伪代码，需按实际API调整
        frame_tags.extend(results)
    
    return frame_tags

# 如果没有GPU：用OpenClaw videos_understand（更简单）
def generate_tags_with_openclaw(video_path: str) -> dict:
    """用OpenClaw内置工具处理视频"""
    # videos_understand 会自动处理多模态理解
    # 适合：无GPU但有OpenClaw平台额度的场景
    return {
        "summary": "视频整体摘要",
        "tags": ["AI", "教程", "Python", "机器学习"],
        "topics": ["深度学习入门", "PyTorch基础"],
        "key_moments": [{"time": "00:05:23", "description": "..."}]
    }
```

### Step 5：LLM 综合生成结构化标签

```python
def generate_structured_tags(
    transcript: str,
    frame_tags: list,
    video_metadata: dict
) -> dict:
    """用LLM综合视频内容，生成推荐系统级标签"""
    
    prompt = f"""你是一个推荐系统的内容分析专家。请根据以下视频信息生成结构化标签。

视频元数据：{video_metadata}
字幕摘要（前2000字）：{transcript[:2000]}
帧标签：{frame_tags}

请生成JSON格式的推荐标签：
{{
    "category_l1": "一级分类（如：科技/美食/娱乐）",
    "category_l2": "二级分类（如：AI教程/手机评测）",
    "tags": ["细粒度标签列表，最多10个"],
    "sentiment": "视频整体情感（正面/中性/负面）",
    "difficulty": "内容难度（入门/进阶/高级）",
    "target_audience": ["目标受众描述"],
    "keywords": ["推荐系统特征词"],
    "related_entities": ["提到的产品/人物/公司"],
    "video_quality_score": "1-5分"
}}
"""
    # 调用LLM（智谱GLM-4-Flash免费额度 / GPT-4o）
    response = llm.chat(prompt)
    return json.loads(response)
```

---

## 推荐系统特征入库

### 向量入库（FAISS）

```python
import faiss
import numpy as np
from FlagEmbedding import BGEM3FlagModel

def build_video_index(video_features: list, dim: int = 1024):
    """将视频向量入库FAISS，支持ANN检索"""
    
    # 1. 用BGE生成文本向量
    model = BGEM3FlagModel('BAAI/bge-m3')
    embeddings = model.encode(video_features)['dense_vecs']
    
    # 2. 降维（PCA到128维，节省存储+加速检索）
    pca = faiss.PCAMatrix(dim, 128, 0, True)
    pca.train(embeddings)
    embeddings_reduced = pca.apply_py(embeddings)
    
    # 3. 建索引
    index = faiss.IndexFlatIP(128)  # 内积相似度
    faiss.normalize_L2(embeddings_reduced)
    index.add(embeddings_reduced)
    
    # 4. 保存
    faiss.write_index(index, "video_index.faiss")
    return index

def recall_similar_videos(query_vector: np.ndarray, top_k: int = 20):
    """给定用户向量，召回TOP-K相似视频"""
    index = faiss.read_index("video_index.faiss")
    D, I = index.search(query_vector.reshape(1, -1), top_k)
    return I[0]  # 返回视频ID列表
```

### 标签入库（结构化数据库）

```sql
-- PostgreSQL/MySQL 表设计示例
CREATE TABLE video_tags (
    video_id VARCHAR(64) PRIMARY KEY,
    category_l1 VARCHAR(32),
    category_l2 VARCHAR(64),
    tags JSONB,                    -- ["AI", "教程", "Python"]
    sentiment VARCHAR(16),
    difficulty VARCHAR(16),
    target_audience TEXT[],
    keywords TEXT[],
    embedding VECTOR(128),          -- pgvector插件
    created_at TIMESTAMP DEFAULT NOW()
);

-- 标签过滤召回示例
SELECT video_id, tags 
FROM video_tags 
WHERE category_l1 = '科技' 
  AND difficulty = '入门'
  AND tags @> '["Python"]'::jsonb
ORDER BY embedding <=> %s  -- 配合向量相似度混合排序
LIMIT 20;
```

---

## 避坑指南

| 坑 | 问题 | 解决方案 |
|---|------|---------|
| **Whisper中文错误率高** | 背景音乐/方言干扰 | 先用 Demucs 分离人声，再转录 |
| **帧数过多拖慢处理** | 长视频截取几百帧，GPU显存爆炸 | 先用场景检测精简帧数（PySceneDetect） |
| **B站字幕需登录** | 付费内容无法直接获取字幕 | 用 Whisper 本地转录代替 |
| **标签与用户兴趣不匹配** | 标签太泛或太细 | 设计三层标签体系，人工抽查验证 |
| **实时性不足** | 批量处理延迟高 | 增量处理：新视频走快通道（轻量VL模型） |
| **向量检索效果差** | embedding不够精准 | 多模态融合：视觉+文本+音频三路向量加权 |

---

## 推荐系统工程师快速上手路线图

```
第1周：环境搭建 + 10条视频手动跑通全流程
  → yt-dlp下载 → Whisper转录 → FFmpeg截帧 → 手动分析

第2周：Python自动化全流程
  → 写Python脚本串起Step1-5
  → 验证标签质量（对比人工标注）

第3周：接入向量检索
  → 用FAISS建索引
  → 实现简单召回Demo

第4周：生产化优化
  → 引入Milvus/Qdrant
  → 标签体系迭代优化
  → A/B测试效果评估
```

---

## 参考链接

- yt-dlp: https://github.com/yt-dlp/yt-dlp
- Whisper: https://github.com/openai/whisper
- Qwen-VL (ModelScope): https://modelscope.cn/models/Qwen/Qwen2-VL-7B-Instruct
- BGE-M3: https://github.com/FlagOpen/FlagEmbedding
- FAISS: https://github.com/facebookresearch/faiss
- PySceneDetect: https://github.com/Breakthrough/PySceneDetect
- Demucs: https://github.com/facebookresearch/demucs
