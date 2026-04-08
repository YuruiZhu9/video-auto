# OpenClaw 内置视频解析工具

> 工具来源：OpenClaw 内置 MCP 工具集  
> 适用版本：OpenClaw 全版本  
> 更新时间：2026-04-08

---

## 核心工具一览

| 工具名称 | 功能 | 输入 | 输出 |
|----------|------|------|------|
| `videos_understand` | 视频内容理解与总结 | 本地视频文件路径 或 视频URL | 结构化文字描述 |
| `batch_text_to_video` | 文本生成视频 | 文字 prompt | MP4 文件 |
| `batch_image_to_video` | 图片生成视频 | 图片路径 + prompt | MP4 文件 |
| `gen_videos` | 统一视频生成入口 | 文本/图片 prompt | MP4 文件 |
| `image_synthesize` | 图片生成/编辑 | 文字描述或参考图 | 图片文件 |

---

## videos_understand（核心解析工具）

### 功能描述

`videos_understand` 是 OpenClaw 内置的视频理解工具，基于多模态大模型，支持对本地视频文件和在线视频URL进行深度内容理解。

### 核心能力

- **多帧联合理解**：将视频按时间轴采样多帧，输入多模态 LLM 进行联合分析
- **语音+画面联合推理**：结合视觉内容与旁白/字幕信息
- **中文友好**：内置中文理解优化，对中文语音和字幕识别效果好
- **批量处理**：单次最多处理 10 个视频

### 适用场景

- 技术教程视频的步骤提取与总结
- 行业分享视频的要点提炼
- 开源项目演示的操作步骤还原
- 产品发布会亮点提取

### 使用方法

```python
# 在 OpenClaw Agent 中直接调用
videos_understand(
  videos_info=[
    {
      "file": "/path/to/video.mp4",      # 本地文件
      # 或 "url": "https://example.com/video.mp4",  # 在线URL
      "prompt": "请详细分析这个技术教程视频：\n1. 视频的主题是什么？\n2. 按时间顺序列出主要操作步骤\n3. 关键技术点有哪些？\n4. 视频来源/作者信息"
    }
  ]
)
```

### Prompt 设计技巧

| 场景 | 推荐 Prompt 要素 |
|------|------------------|
| 技术教程 | "按步骤列出"、"关键代码/命令"、"容易出错的地方" |
| 行业分享 | "核心观点"、"数据支撑"、"趋势判断" |
| 产品发布 | "新功能亮点"、"定价信息"、"适用人群" |
| 会议记录 | "讨论议题"、"决定事项"、"行动项" |

### 局限性与替代方案

| 局限性 | 替代方案 |
|--------|----------|
| 不支持实时字幕生成 | 配合 `summarize` skill 提取字幕 |
| 长视频可能截断 | 先用 ffmpeg 分割，再分批理解 |
| 不擅长纯音频分析 | 使用 `audios_understand` 工具 |

---

## batch_image_to_video（视频续写/动画生成）

### 功能描述

从单张图片生成视频动画，可用于将视频关键帧转化为动态场景。

### 适用场景

- 技术教程中关键步骤的动态演示生成
- 产品展示的动态封面
- 将静态截图转化为视频片段

### 使用方法

```python
batch_image_to_video(
  count=1,
  image_file_list=["/path/to/frame.jpg"],
  output_file_list=["/workspace/frame_video.mp4"],
  prompt_list=["演示这个操作步骤的动态效果"],
  reference_type_list=["first_frame"],
  duration_list=[6],
  resolution_list=["768P"]
)
```

---

## 工具组合工作流

```
原始视频
  │
  ├─▶ videos_understand ──────────────────▶ 结构化摘要
  │         │
  │         └─（可选）分段处理长视频
  │
  ├─▶ video-frames (ffmpeg skill) ───────▶ 关键帧截图
  │         │
  │         └─▶ image_synthesize ─────────▶ 增强/标注图
  │
  └─▶ summarize skill ──────────────────▶ 字幕/文字稿
            │
            └─▶ LLM 二次处理 ──────────────▶ 深度总结
```

---

## 参考链接

- OpenClaw 官方文档：https://docs.openclaw.ai/zh-CN
- videos_understand 工具说明：内置 MCP 工具
- ClawHub Skills 库：https://clawhub.ai
