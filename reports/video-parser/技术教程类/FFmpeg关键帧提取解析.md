# 技术教程类 - FFmpeg 关键帧提取解析

## 核心工具/API

- **FFmpeg**：开源视频处理工具，命令行操作
  - 抽帧：`ffmpeg -i input.mp4 -frames:v 1 output.jpg`
  - 按时间抽帧：`ffmpeg -ss 00:01:30 -i input.mp4 -frames:v 1 output.jpg`
  - 按帧号抽帧：`ffmpeg -i input.mp4 -vf "select=eq(n\,100)" -vframes 1 output.jpg`
  - 批量等间隔抽帧：`ffmpeg -i input.mp4 -vf "fps=1/60" frames/%04d.jpg`
- **OpenCV (cv2)**：Python 视觉库，支持内容感知抽帧
  - 帧差法（shot boundary detection）
  - 颜色直方图法
  - SIFT/ORB 特征匹配
- **MediaInfo**：视频元数据提取（时长、编码、分辨率）
- **shot-scene-detect**：Python 开源镜头检测库

---

## 步骤流程

### 流程一：FFmpeg 等间隔抽帧（最常用）

```
1. 安装 FFmpeg（如未安装）
   # macOS
   brew install ffmpeg
   # Linux
   sudo apt install ffmpeg

2. 提取第一帧（封面）
   ffmpeg -hide_banner -loglevel error -y \
     -i video.mp4 -vf "select=eq(n\,0)" -vframes 1 cover.jpg

3. 按时间点抽帧（示例：10s, 30s, 1m, 2m）
   for t in 10 30 60 120; do
     ffmpeg -ss $t -i video.mp4 -frames:v 1 frame_${t}s.jpg
   done

4. 等间隔批量抽帧（每30秒一帧）
   ffmpeg -i video.mp4 -vf "fps=1/30" frames/%04d.jpg

5. 降采样后批量抽帧（节省存储）
   ffmpeg -i video.mp4 -vf "scale=1280:720,fps=1/60" frames/%04d.jpg
```

### 流程二：OpenCV 智能关键帧提取

```python
import cv2
import numpy as np

def extract_keyframes(video_path, num_frames=10, threshold=30.0):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    prev_frame = None
    keyframes = []
    scores = []
    
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if prev_frame is not None:
            # 计算帧差分（场景切换检测）
            diff = cv2.absdiff(gray, prev_frame)
            score = np.mean(diff)
            scores.append((frame_idx, score))
        
        prev_frame = gray
        frame_idx += 1
    
    cap.release()
    
    # 选择变化最大的 N 个帧
    scores.sort(key=lambda x: x[1], reverse=True)
    keyframe_indices = [s[0] for s in scores[:num_frames]]
    
    return sorted(keyframe_indices)

# 使用示例
keyframes = extract_keyframes("tutorial.mp4", num_frames=8)
print(f"关键帧位置：{keyframes}")
```

### 流程三：镜头边界检测（shot-scene-detect）

```bash
pip install scenedetect

# 探测镜头边界
scenedetect detect-content input.mp4 -o scenes/

# 提取每个镜头第一帧
scenedetect detect-content input.mp4 -o frames/ \
  --df 25 export-images

# 与 AI 结合：分析每个镜头
for frame in frames/*.jpg; do
  images_understand([{"file": "$frame", "prompt": "描述这个画面的内容"}])
done
```

---

## 适用场景

- ✅ 教程视频需要提取操作界面截图
- ✅ 需要按场景/章节分割长视频
- ✅ 制作视频缩略图/封面
- ✅ 将视频内容可视化（PPT 素材）
- ✅ 大规模视频内容预筛选（先抽帧再人工审核）
- ✅ 声音嘈杂但视觉信息丰富的演示视频

---

## 避坑指南

### ⚠️ 坑1：抽帧速度极慢（从视频开头开始 seek）
- **问题**：FFmpeg 默认从头开始解码，seek 到后期时间点很慢
- **解决**：使用 `-ss before -i input`（将 -ss 放在 -i 前面，FFmpeg 会做关键帧二分查找）：
  ```bash
  # ❌ 慢：从头开始解码到 5 分钟
  ffmpeg -i input.mp4 -ss 300 -frames:v 1 out.jpg
  
  # ✅ 快：关键帧快速定位
  ffmpeg -ss 300 -i input.mp4 -frames:v 1 out.jpg
  ```

### ⚠️ 坑2：H.264/H.265 编码视频抽帧质量下降
- **问题**：压缩编码导致抽帧出现色块/模糊
- **解决**：使用 `-q:v 1` 输出高质量 JPEG/PNG：
  ```bash
  ffmpeg -ss 60 -i input.mp4 -q:v 1 -frames:v 1 output.png
  ```

### ⚠️ 坑3：批量抽帧存储爆炸
- **问题**：1小时 1080P 视频按 1fps 抽帧 = 3600 张图 ~10GB
- **解决**：
  - 先降分辨率：`scale=640:360`
  - 质量控制：`-q:v 3`（JPEG quality 2-31，越小越高）
  - 只抽关键场景：用 shot-scene-detect 代替等间隔

### ⚠️ 坑4：OpenCV 帧差法漏检缓慢过渡镜头
- **问题**：渐变、淡入淡出等缓慢场景变化，帧差分值低，被漏掉
- **解决**：降低阈值 + 结合直方图相似度检测

---

## 参考链接

- FFmpeg 官方文档：https://ffmpeg.org/documentation.html
- OpenCV 视频分析：https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- scenedetect（镜头检测）：https://www.scenedetect.com/
- MediaInfo 工具：https://mediaarea.net/en/MediaInfo
