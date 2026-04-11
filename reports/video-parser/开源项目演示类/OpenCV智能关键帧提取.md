# 开源项目演示类 - OpenCV 智能关键帧提取解析

## 核心工具/API

- **OpenCV (cv2)**：Python 计算机视觉库，帧差分/光流/直方图分析
- **shot-scene-detect**：专业镜头边界检测，支持 content/threshold/adaptive 三种算法
- **FFmpeg**：底层视频处理，格式转换、抽帧、降采样
- **LangChain / LlamaIndex**：多模态文档理解 pipeline
- **Ollama / vLLM**：本地 LLM 推理（隐私优先场景）

---

## 步骤流程

### 流程一：场景切换检测（Scene Detection）

```python
from scenedetect import detect, ContentDetector

# 内容感知检测（自动识别场景切换）
scene_list = detect("project_demo.mp4", ContentDetector(threshold=27.0))

for scene in scene_list:
    start, end = scene
    print(f"场景: {start.get_timecode()} → {end.get_timecode()}")

# 提取每个场景第一帧
from scenedetect import split_video
split_video("project_demo.mp4", scene_list, output_dir="scenes/")
```

### 流程二：光流法运动检测（适合演示类视频）

```python
import cv2
import numpy as np

def extract_motion_keyframes(video_path, threshold_motion=500, max_frames=20):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    ret, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    keyframes = []
    frame_idx = 1
    while True:
        ret, curr_frame = cap.read()
        if not ret:
            break
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        motion_score = np.mean(magnitude) * 1000
        if motion_score > threshold_motion:
            timestamp = frame_idx / fps
            keyframes.append({'frame': frame_idx, 'time': f"{int(timestamp//60):02d}:{int(timestamp%60):02d}", 'score': round(motion_score, 2)})
        prev_gray = curr_gray
        frame_idx += 1
    cap.release()
    keyframes.sort(key=lambda x: x['score'], reverse=True)
    return keyframes[:max_frames]

keyframes = extract_motion_keyframes("demo.mp4", threshold_motion=300)
for kf in keyframes:
    print(f"时间 {kf['time']} | 运动得分 {kf['score']} | 帧号 {kf['frame']}")
```

### 流程三：完整 Pipeline → AI 结构化输出

```
视频文件
  ↓ [FFmpeg 降采样 + 镜头检测] → 关键帧列表
  ↓ [OpenCV 光流/直方图分析] → 运动热点 + 切换节点
  ↓ [images_understand 批量分析关键帧] → 每帧文字描述
  ↓ [LLM 综合总结] → 结构化报告
```

```python
import subprocess, os
from scenedetect import detect, ContentDetector

def parse_open_source_demo(video_path):
    # 1. 镜头检测
    scene_list = detect(video_path, ContentDetector(threshold=30))
    os.makedirs("keyframes", exist_ok=True)

    # 2. 提取关键帧（每场景首帧）
    for i, (start, end) in enumerate(scene_list):
        ts = start.get_seconds()
        subprocess.run([
            "ffmpeg", "-ss", str(ts), "-i", video_path,
            "-frames:v", "1", "-q:v", "2",
            f"keyframes/scene_{i:03d}.jpg"
        ], capture_output=True)

    # 3. AI 分析每帧 → images_understand 调用（见工具文档）
    # 4. LLM 综合总结 → 结构化报告
    return "keyframes/"
```

---

## 适用场景

- ✅ 开源项目 README / GitHub Demo 视频
- ✅ 发布会 Keynote 演示（PPT 切换检测）
- ✅ 屏幕录制操作演示（点击、界面切换）
- ✅ 自动化测试记录视频分析
- ✅ 需要精确分割章节的长演示视频

---

## 避坑指南

### ⚠️ PPT 翻页漏检（浅色背景/慢速翻页）
- 直方图变化不显著 → 结合帧差分 + 光流双重检测，降低阈值到 0.02

### ⚠️ 终端黑屏代码演示
- 终端背景接近全黑/全白 → 限定检测区域（屏幕中心 80%）或用 OCR 文本变化检测

### ⚠️ 长视频处理速度慢
- 1小时视频逐帧光流需要数小时 → 先降采样到 720P，每隔 5 帧处理 1 帧，或用 GPU 加速（cv2.cuda）

### ⚠️ OpenCV 安装依赖复杂
- macOS: `brew install opencv@4` | Ubuntu: `apt install libopencv-dev python3-opencv`

---

## 参考链接

- OpenCV 官方文档：https://docs.opencv.org/4.x/
- scenedetect GitHub：https://github.com/PySceneDetect/scenedetect
- Ollama 本地 LLM：https://ollama.com/
- vLLM 高效推理：https://github.com/vllm-project/vllm
