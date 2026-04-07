# 通用方法 - videos_understand 内置工具

## 核心工具/API

- **工具名称**: `videos_understand`（OpenClaw 内置 LLM 视频理解工具）
- **模型**: OpenClaw 平台内置，无需额外配置 API Key
- **输入**: 支持本地视频文件路径（`/workspace/xxx.mp4`）或公开 URL
- **并发**: 单次最多 **10 个**视频并行分析
- **最大文件数**: 每请求最多 10 个视频

## 步骤流程

### 基本调用（通过 Tool 界面）
```
视频输入 → videos_understand → LLM 多模态理解 → 结构化文本输出
```

### Python/SDK 调用示例
```python
# OpenClaw Tool 调用格式（JSON）
{
  "videos_info": [
    {
      "file": "/workspace/tutorials/reco-system-intro.mp4",
      "prompt": "提取这个技术教程视频的核心知识点，包括：1.主题 2.关键概念 3.技术要点 4.代码片段（如果有）"
    },
    {
      "url": "https://example.com/demo.mp4",
      "prompt": "描述这个开源项目的演示内容，包括：功能演示步骤、使用的技术栈、关键亮点"
    }
  ]
}
```

### 典型分析 Prompt 设计

```python
# 结构化知识提取
videos_info = [{
  "file": "video.mp4",
  "prompt": """
请分析这个视频，按以下格式输出：

## 视频概览
- 标题/主题：
- 时长：
- 类型：

## 核心内容（分章节）
[章节1] 时间戳: 内容摘要
[章节2] 时间戳: 内容摘要
...

## 关键要点（5条以内）
1.
2.
...

## 技术细节
- 涉及的技术栈：
- 演示的工具/框架：

## 金句/洞察
- 引用原文：
"""
}]
```

## 适用场景

- **技术教程深度解析**: 直接提取代码、步骤、概念
- **开源项目 Demo 分析**: 识别演示的功能和技术亮点
- **行业演讲/会议记录**: 按时间线切分要点
- **多视频批量对比**: 并行分析多个视频找共同主题
- **画面+音频双通道理解**: 不依赖字幕，直接理解视觉内容

## 避坑指南

| 问题 | 解决方案 |
|------|---------|
| 视频太长（>1小时） | 建议先切分成小段（ffmpeg），再逐段分析 |
| 文件格式不支持 | 确保格式为 mp4/webm/avi/mov 等常见格式 |
| 视频文件过大 | 可先用 `video-frames` 提取关键帧，降低 token 消耗 |
| 需要时间戳 | Prompt 中明确要求"按时间戳组织" |
| 分析结果太泛 | 给出具体的输出格式模板，让 LLM 严格按格式输出 |
| 视频无声音 | 仍可分析画面内容，但应告知用户音频缺失 |

## 与其他工具的配合

```
输入视频
  ├─ 需快速概览 ───▶ summarize ──→ 粗略摘要
  │
  ├─ 需深度理解（画面+声音）──▶ videos_understand ──→ 详细结构化分析
  │
  ├─ 需字幕 + 全文 ──▶ whisper/whisper-api ──→ 纯文本
  │
  └─ 需精确帧画面 ───▶ video-frames ──→ 图片帧 ──▶ images_understand
```

## 适用场景速查

| 需求 | 推荐工具 |
|------|---------|
| 只要文字内容 | `summarize` 或 `whisper` |
| 只要视频画面截图 | `video-frames` |
| 深度理解画面+音频 | `videos_understand` |
| 完整分析 pipeline | `yt-dlp` → `whisper` → `videos_understand` |
