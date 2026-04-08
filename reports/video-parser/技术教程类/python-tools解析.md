# 技术教程类 - Python 工具解析方案

> 解析类型：技术教程视频（深度定制化处理）  
> 适用人群：有 Python 编程基础的用户  
> 更新时间：2026-04-08

---

## 核心工具/API

| 工具 | 功能描述 | 安装方式 |
|------|----------|----------|
| **Whisper** | OpenAI 开源语音识别，支持中文 | `pip install openai-whisper` |
| **MoviePy** | Python 视频编辑，帧提取 | `pip install moviepy` |
| **OpenCV** | 计算机视觉，帧处理 | `pip install opencv-python` |
| **Pytube** | YouTube 视频下载 | `pip install pytube` |
| **youtube-transcript-api** | YouTube 字幕提取 | `pip install youtube-transcript-api` |
| **Vidstab** | 视频稳定化/分析 | `pip install vidstab` |
| **LLM API（智谱/阿里）**| 结构化内容生成 | HTTP 调用 |

---

## 步骤流程

### 完整流水线

```
视频文件/URL
  │
  ├─ 方案 A：Whisper 转写 + LLM 总结
  │     └─▶ 文字稿 → LLM → 结构化笔记
  │
  ├─ 方案 B：多帧提取 + 多模态分析
  │     └─▶ 帧序列 → images_understand → 步骤还原
  │
  └─ 方案 C：混合流水线（最完整）
        ├─▶ 字幕提取/Whisper 转写
        ├─▶ 关键帧提取
        └─▶ LLM 联合推理 → 综合报告
```

---

### 方案 A：Whisper 转写 + LLM 总结

**适用**：有高质量语音的教程视频（播音/旁白清晰）

```python
import whisper
import requests

# Step 1: 加载 Whisper 模型（首次下载）
model = whisper.load_model("base")  # tiny/base/small/medium/large

# Step 2: 转写
result = model.transcribe("tutorial.mp4", language="zh")
transcript = result["text"]
segments = result["segments"]  # 含时间戳

# Step 3: 保存带时间戳的字幕
with open("transcript.srt", "w", encoding="utf-8") as f:
    for seg in segments:
        start = seg["start"]
        end = seg["end"]
        text = seg["text"]
        f.write(f"{seg['id']+1}\n")
        f.write(f"{start:.2f} --> {end:.2f}\n")
        f.write(f"{text}\n\n")

# Step 4: LLM 结构化（调用智谱 GLM-4-Flash）
prompt = f"""请将以下技术教程转录稿整理为结构化笔记：

{transcript[:8000]}  # 限制token

要求：
1. 提取核心知识点
2. 按时间顺序列出关键操作步骤
3. 标注常见错误和注意事项
4. 整理命令/代码片段
"""

response = requests.post(
    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    headers={"Authorization": "Bearer YOUR_ZHIPU_API_KEY"},
    json={
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": prompt}]
    }
)
structured_notes = response.json()["choices"][0]["message"]["content"]
```

---

### 方案 B：关键帧提取 + 图像分析

**适用**：代码演示、操作步骤类教程

```python
import cv2
import os

def extract_keyframes(video_path, output_dir, interval_sec=30):
    """每 N 秒提取一帧关键帧"""
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(fps * interval_sec)
    
    frame_count = 0
    saved = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % interval_frames == 0:
            filename = f"{output_dir}/frame_{saved:04d}.jpg"
            cv2.imwrite(filename, frame)
            saved += 1
        frame_count += 1
    
    cap.release()
    print(f"提取了 {saved} 帧到 {output_dir}")
    return saved

# 执行提取
extract_keyframes("tutorial.mp4", "/workspace/frames", interval_sec=30)
```

**关键帧筛选（场景变化检测）**：

```python
import cv2

def extract_scene_changes(video_path, output_dir, threshold=30.0):
    """只保留场景变化的帧，减少冗余"""
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    ret, prev_frame = cap.read()
    if not ret:
        return
    
    frame_id = 0
    saved = 0
    while True:
        ret, curr_frame = cap.read()
        if not ret:
            break
        
        # 计算帧差
        diff = cv2.absdiff(prev_frame, curr_frame)
        mean_diff = diff.mean()
        
        if mean_diff > threshold:
            filename = f"{output_dir}/scene_{saved:04d}_fid{frame_id}.jpg"
            cv2.imwrite(filename, curr_frame)
            saved += 1
        
        prev_frame = curr_frame
        frame_id += 1
    
    cap.release()
    print(f"场景变化检测：保存 {saved} 个关键帧")

extract_scene_changes("demo.mp4", "/workspace/scenes", threshold=40.0)
```

---

### 方案 C：YouTube 视频直接解析

**适用**：YouTube 技术教程视频（无需下载本地）

```python
from youtube_transcript_api import YouTubeTranscriptApi
import requests

def get_youtube_transcript(video_id):
    """提取 YouTube 字幕"""
    try:
        # 尝试中文优先
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['zh-Hans', 'zh', 'en']
        )
        text = " ".join([item['text'] for item in transcript])
        return text, transcript
    except Exception as e:
        print(f"字幕提取失败: {e}")
        return None, None

# 用 summarize skill 快速总结（推荐）
# summarize "https://youtu.be/VIDEO_ID" --youtube auto --length medium

# 或用 pytube 下载后本地处理
from pytube import YouTube

def download_youtube(url, output_path="/workspace"):
    yt = YouTube(url)
    stream = yt.streams.filter(file_extension='mp4').first()
    stream.download(output_path)
    return stream.default_filename

video_path = download_youtube("https://youtube.com/watch?v=VIDEO_ID")
```

---

## 适用场景

| 场景 | 推荐方案 |
|------|----------|
| 本地教程视频（已下载）| 方案 B + LLM 总结 |
| YouTube 英文教程 | 方案 C（字幕提取）|
| 无字幕/口音重教程 | 方案 A（Whisper）|
| 代码演示类教程 | 方案 B（关键帧+OCR）|
| 混合型（语音+操作）| 方案 C 混合流水线 |

---

## 避坑指南

### ⚠️ Whisper 模型选择
**问题**：模型太大（large=2.9GB）推理慢，太小（tiny）精度差  
**解决**：

| 硬件条件 | 推荐模型 | 精度 | 速度 |
|----------|----------|------|------|
| CPU only | `base` | 中等 | 慢 |
| GPU 8GB | `medium` | 高 | 快 |
| GPU 16GB+ | `large` | 最高 | 快 |

### ⚠️ 中文语音识别效果差
**问题**：Whisper 对中文方言/口音识别不佳  
**解决**：
1. 优先使用视频内置字幕（YouTube/B站）
2. 使用 `large` 模型并指定 `language="zh"`
3. 后处理用 LLM 纠错

```python
result = model.transcribe("video.mp4", language="zh", initial_prompt="以下是一段技术教程：")
```

### ⚠️ 视频文件损坏/编码问题
**解决**：用 ffmpeg 重新编码后再处理

```bash
ffmpeg -i damaged.mp4 -c:v libx264 -c:a aac fixed.mp4
```

### ⚠️ 隐私风险
**问题**：将视频上传到第三方 API 可能泄露内容  
**解决**：优先使用本地 Whisper 模型；必须用云端 API 时使用国内厂商（智谱、阿里）并确认数据不留存

---

## 参考链接

- Whisper 官方：https://github.com/openai/whisper
- youtube-transcript-api：https://github.com/jdepoix/youtube-transcript-api
- MoviePy：https://zulko.github.io/moviepy/
- OpenCV：https://opencv.org/
- Pytube：https://github.com/pytube/pytube
