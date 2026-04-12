# 技术教程类 - videos_understand 多模态解析

> 适用于：编程教学、框架讲解、技术会议演讲、操作演示类视频

## 核心工具/API

- **videos_understand（OpenClaw 内置工具）**：多模态 LLM 直接分析视频文件/URL，支持批量
- **VideoCaptioner**：国产开源工具，集成字幕生成 + 视频理解（支持 SilicionCloud 等国产 API）
- **LLMVS（CVPR 2025）**：将视频帧转为多模态 caption，再用 LLM 生成结构化摘要
- **Google Gemini 2.0 Flash**：视频理解主力模型，支持超长上下文

## 步骤流程

### 方法一：videos_understand（推荐，最简）

```python
# OpenClaw 工具调用方式
videos_understand(videos_info=[
    {
        "file": "/path/to/tutorial.mp4",
        "prompt": "这是一个技术教程视频，请提取：1. 主题和目标 2. 主要知识点（分点）3. 代码片段/命令 4. 关键时间点 5. 参考资源链接"
    },
    {
        "url": "https://example.com/video.mp4",
        "prompt": "提取视频中的所有命令行操作，按时间顺序列出"
    }
])
```

### 方法二：VideoCaptioner（适合国内用户）

```bash
# 安装
git clone https://github.com/HighCWu/VideoCaptioner.git
cd VideoCaptioner && pip install -r requirements.txt

# 配置 LLM API（支持 SiliconCloud 聚合接口）
# 编辑 config/llm_config.json

# 运行
python main.py --video /path/to/tutorial.mp4 --output ./output/

# 可指定分析维度
python main.py --video /path/to/tutorial.mp4 \
    --prompt "这是一个Python教程视频，请详细列出：1. 涉及的Python库 2. 核心代码逻辑 3. 常见错误和解决方案"
```

### 方法三：LLMVS 流水线（学术级，适合深度分析）

```
视频 → 帧采样 → M-LLM生成帧描述 → LLM聚合摘要 → 结构化报告
```

```python
# 伪代码流程
import cv2

# 1. 均匀采样帧
cap = cv2.VideoCapture("tutorial.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
frames = []
for i in range(0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), int(fps * 5)):  # 每5秒一帧
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ret, frame = cap.read()
    if ret:
        frames.append(frame)

# 2. 用多模态LLM分析每帧（可用 videos_understand 批量）
captions = videos_understand([{"file": frame, "prompt": "描述这张图的核心内容"} for frame in frames])

# 3. LLM 聚合生成结构化教程摘要
summary_prompt = f"以下是一个技术教程视频的帧描述，请整合成一个完整的教程摘要：\n{captions}"
```

## 适用场景

- 编程教学视频（Python/JS/Go/AI框架等）
- 技术会议演讲（SIGIR/RecSys/NeurIPS 等）
- 工具使用教程（Figma/Sketch/IDE 等）
- 开源框架官方文档视频
- AI/LLM 技术科普视频

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 视频太长分析超时 | 超过 API 单次处理上限 | 先用 ffmpeg 切分片段，或降低帧采样率 |
| 代码显示不完整 | 帧分辨率不足 | 用高分辨率截帧（1080p+），避免字体模糊 |
| 专业知识遗漏 | 通识 LLM 缺乏领域知识 | 在 prompt 中加背景约束：`"假设观众熟悉推荐系统基础"` |
| 分析结果碎片化 | 帧间缺乏连贯性 | 用时间轴 prompt：`"按时间顺序整理，注意前后逻辑"` |
| 视频下载受限 | B站/YouTube 地区锁 | 用 yt-dlp 加代理：`yt-dlp --proxy "socks5://127.0.0.1:7890" URL` |
| 本地视频太大 | 文件超过工具限制 | 先压缩：`ffmpeg -i video.mp4 -vf scale=1280:-1 video_720p.mp4` |

## 结构化输出模板

```markdown
# [视频标题]

## 基本信息
- 时长：XX:XX
- 平台：YouTube/B站/本地
- 讲师：[姓名]
- 发布日期：[日期]

## 核心知识点
1. **知识点1**：详细说明...
2. **知识点2**：详细说明...

## 关键代码片段
```python
# 代码块
```

## 时间线索引
- 00:00 - 05:00：引入/背景
- 05:00 - 15:00：核心内容
- 15:00 - 20:00：实战演示
- 20:00 - 25:00：总结

## 参考资源
- 官方文档链接
- GitHub 仓库
- 相关博客
```

## 参考链接

- VideoCaptioner GitHub：https://github.com/HighCWu/VideoCaptioner
- LLMVS 论文（CVPR 2025）：https://postech-cvlab.github.io/LLMVS/
- yt-dlp：https://github.com/yt-dlp/yt-dlp
