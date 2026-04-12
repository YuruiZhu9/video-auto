# 行业分享类 - 关键帧提取 + LLM 分析

> 适用于：行业峰会演讲、投资人分享、产品发布会、市场分析报告类视频

## 核心工具/API

- **LMSKE（Keyframe Extraction）**：基于大模型的关键帧序列提取，适合长视频
- **yt-dlp / bilili**：B站/YouTube 等平台元数据提取（标题、描述、标签、播放量）
- **Google Gemini / GPT-4V**：多模态分析关键帧图像，提取观点和亮点
- **Minimal Clips（arXiv 2025）**：选择性剪辑 + 轻量 caption 生成，用于长视频摘要

## 步骤流程

### 第一步：视频元数据提取（了解背景）

```bash
# YouTube 视频信息
yt-dlp --dump-json "https://www.youtube.com/watch?v=VIDEO_ID" | jq '{title, description, uploader, view_count, like_count, tags}'

# B站视频信息
yt-dlp --dump-json "https://www.bilibili.com/video/BVxxxxxx" | jq '{title, description, uploader, view, favorite, coin, share}'

# 提取评论（用于了解热点）
yt-dlp --write-comments --dump-json "URL" > video_info.json
```

### 第二步：关键帧批量提取

```python
import cv2, os

def extract_keyframes(video_path, output_dir, threshold=30, max_frames=30):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    prev_frame = None
    saved = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_frame is not None:
            diff = cv2.absdiff(gray, prev_frame)
            if diff.mean() > threshold:
                out_path = f"{output_dir}/kf_{saved:03d}_t{int(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)}s.jpg"
                cv2.imwrite(out_path, frame)
                saved += 1
                if saved >= max_frames:
                    break
        prev_frame = gray

    cap.release()
    print(f"Saved {saved} keyframes")

extract_keyframes("/path/to/video.mp4", "/tmp/keyframes")
```

### 第三步：LLM 批量分析关键帧

```python
import glob
keyframe_files = sorted(glob.glob("/tmp/keyframes/*.jpg"))
keyframe_info = [{"file": f, "prompt": "这张图是行业分享视频的关键帧，请提取：1. 演讲主题/观点 2. 数据图表信息 3. 核心金句"} for f in keyframe_files]

# 分批处理（每次最多10张）
results = []
for i in range(0, len(keyframe_info), 10):
    batch = keyframe_info[i:i+10]
    batch_results = videos_understand(videos_info=batch)
    results.extend(batch_results)
```

## 适用场景

- 行业峰会演讲（提取最新行业趋势、技术方向）
- 投资人分享（提取投资逻辑、市场判断、金句）
- 产品发布会（提取新品特性、竞争优势、定价策略）
- 市场分析报告视频（提取数据图表、关键结论）
- 播客/访谈节目（提取核心观点和论据）

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 关键帧太多重复 | 场景变化检测阈值过低 | 调高 threshold（建议 30-50）或限制 max_frames |
| 关键帧错过重要信息 | 镜头切换不剧烈但内容重要 | 改用均匀采样（每30秒一帧）+ LMSKE 结合 |
| 视频平台反爬 | yt-dlp 被封 IP | 加 User-Agent 或代理：--proxy "socks5://..." |
| 跨平台整合难 | YouTube/B站数据结构不同 | 用统一 JSON Schema 归一化 |
| 会议视频太长 | 2小时+ 峰会演讲 | 先用 Minimal Clips 做预筛选，再重点分析 |

## 结构化输出模板

```markdown
# [分享主题] - 行业分享分析

## 视频信息
- 平台：YouTube / B站 / 其他
- 主讲人：[姓名]
- 机构：[公司/组织]
- 时长：[X] 分钟
- 播放量：[X] 万
- 日期：[发布年份]

## 核心观点（按重要性排序）
1. **观点1**：详细说明 + 支撑数据
2. **观点2**：详细说明 + 支撑数据

## 关键数据/图表
| 数据项 | 数值 | 来源帧 |
|--------|------|--------|
| ...    | ...  | 05:30  |

## 行业趋势洞察
- 趋势1：分析
- 趋势2：分析

## 金句摘录
> "引用的原话"

## 与我当前方向的关联
- 机会点1
- 警惕点2
```

## 参考链接

- LMSKE 论文：https://api.emergentmind.com/topics/large-model-based-sequential-keyframe-extraction-lmske
- Minimal Clips 论文（arXiv 2025）：https://arxiv.org/abs/2512.11399
- yt-dlp GitHub：https://github.com/yt-dlp/yt-dlp
- bilili（B站下载）：https://github.com/lanyeeee/bilibili-video-downloader
