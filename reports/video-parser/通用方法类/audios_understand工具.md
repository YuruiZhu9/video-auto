# 通用方法 - audios_understand 内置工具

## 核心工具/API

- **工具名称**: `audios_understand`（OpenClaw 内置 LLM 音频理解工具）
- **模型**: OpenClaw 平台内置，无需额外配置 API Key
- **输入**: 支持本地音频文件路径或公开 URL
- **并发**: 单次最多 **10 个**音频并行分析
- **音频格式**: 支持 mp3/wav/m4a/ogg/flac 等常见格式

## 步骤流程

### 基本调用
```python
{
  "audio_info": [
    {
      "file": "/workspace/recordings/interview.mp3",
      "prompt": "转录并分析这段音频的内容"
    }
  ]
}
```

### 典型分析 Prompt

```python
# 音频转录 + 要点提取
audio_info = [{
  "file": "podcast.mp3",
  "prompt": """
请完成以下任务：
1. 完整转录这段音频（保留说话人区分）
2. 提取 3-5 个核心观点
3. 识别说话人的情绪和态度
4. 总结音频的主题和价值
"""
}]

# 特定信息提取
audio_info = [{
  "file": "meeting.wav",
  "prompt": "提取所有待办事项（TODO）和决策结论"
}]

# 多语言场景
audio_info = [{
  "url": "https://example.com/english-talk.mp3",
  "prompt": "这是一个英文技术演讲，请转录并提取技术要点（中文输出）"
}]
```

## 适用场景

- **播客（Podcast）内容分析**: 批量分析多期节目，提取主题
- **会议记录**: 从录音中提取决策、待办和讨论要点
- **访谈节目**: 结构化访谈内容，提取关键洞察
- **有声书/课程**: 提取章节结构和核心知识点
- **无视频的纯音频**: 弥补 `videos_understand` 对视频文件的限制

## 与 videos_understand 的对比

| 维度 | `videos_understand` | `audios_understand` |
|------|-------------------|-------------------|
| 输入 | 视频文件 | 音频文件 |
| 视觉内容 | ✅ 包含 | ❌ 不包含 |
| 音频内容 | ✅ 包含 | ✅ 包含 |
| 适用场景 | 画面关键的教学/Demo | 纯音频内容（播客/录音） |
| 典型 Prompt | "描述画面中演示的步骤" | "转录并提取核心观点" |

## 避坑指南

| 问题 | 解决方案 |
|------|---------|
| 音频质量差（有噪音） | 建议先用 ffmpeg 降噪后再分析 |
| 长音频（>2小时） | 拆分成多个小段再并行分析 |
| 多人说话难区分 | Prompt 明确要求"区分说话人（Speaker A/B/C）" |
| 小众语言 | 确认 Prompt 中指定语言，避免误识别 |
| 音频文件太大 | 建议先压缩（如 128kbps MP3），不影响理解效果 |

## 典型 Pipeline

```
视频 → ffmpeg 提取音频 → audios_understand 分析
     └─ 或直接用 → videos_understand 全局分析

纯音频 → audios_understand → 结构化文本
```
