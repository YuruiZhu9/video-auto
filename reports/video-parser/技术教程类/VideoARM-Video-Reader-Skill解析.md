# 技术教程类 — VideoARM Video Reader Skill（子Agent编排架构）

> 🤖 维护：视频解析方法总结Agent（小M）
> 📅 新增日期：2026-04-06（第五周）
> 🔗 来源：qiankemeng / clawhub.ai/qiankemeng/video-reader
> 📦 安装：`clawhub install video-reader`
> ⚙️ 依赖：ffmpeg（本地）、OpenClaw sessions_spawn（子Agent）

---

## 核心工具/API

| 工具 | 类型 | 能力描述 |
|------|------|----------|
| **videoarm-download** | 工具脚本 | 下载视频（YouTube等），支持代理 |
| **videoarm-info** | 工具脚本 | 获取视频元数据（fps/总帧数/时长） |
| **videoarm-extract-frames** | 工具脚本 | 按帧范围提取帧网格图（按比例分布） |
| **videoarm-audio** | 工具脚本 | 转录指定时间范围的音频，返回JSON |
| **sessions_spawn** | OpenClaw API | 派生子Agent进行干净上下文的视觉分析 |
| **记忆文件机制** | 架构设计 | `/tmp/videoarm_memory.json` 为唯一事实来源 |

---

## 架构设计：编排器 + 工作器

```
┌─────────────────────────────────────────────────────────────┐
│                    主Agent（编排器）                         │
│  OBSERVE → THINK → ACT → MEMORY（最多10轮迭代）             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ① videoarm-download    → 获取视频路径                       │
│  ② videoarm-info        → 获取 fps/总帧数/时长              │
│  ③ videoarm-extract-frames → 提取帧网格图                    │
│  ④ sessions_spawn       → 派生子Agent分析帧                  │
│  ⑤ videoarm-audio       → 提取音频片段                       │
│  ⑥ 写记忆文件           → 持续积累发现                       │
│                                                             │
│  [最多10轮后给出最终答案 + 置信度]                           │
└─────────────────────────────────────────────────────────────┘
         ↓ 派生子Agent（干净上下文）
┌─────────────────────────────────────────────────────────────┐
│              子Agent（工作器）— 独立干净上下文               │
│                                                             │
│  接收：图像路径 + 具体问题 + 相关上下文                       │
│  输出：JSON { answer, confidence, evidence }                │
│                                                             │
│  优势：                                                      │
│  ✅ 无对话历史污染                                          │
│  ✅ 每次都是新鲜模型                                       │
│  ✅ 主上下文不因图像token膨胀                              │
│  ✅ 可并行派发多个子Agent                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 记忆文件机制（关键设计）

**位置：** `/tmp/videoarm_memory.json`

```json
{
  "video_path": "/path/to/video.mp4",
  "question": "视频中使用了什么工具？",
  "metadata": {
    "duration": 2689.74,
    "fps": 25.0,
    "total_frames": 67243
  },
  "scene_snapshots": [
    {
      "iteration": 1,
      "reason": "开场段落初步扫描",
      "frame_interval": [0, 1500],
      "caption": "一个人正在使用电钻工作"
    }
  ],
  "audio_snippets": [
    {
      "iteration": 2,
      "reason": "检查中间段对话",
      "segments": [
        {
          "frame_interval": [3000, 4500],
          "text": "他真的需要工作生活平衡",
          "start_time": 120.0,
          "end_time": 180.0
        }
      ]
    }
  ],
  "frame_analyses": [
    {
      "iteration": 3,
      "reason": "验证第500-1000帧的工具使用",
      "frame_interval": [500, 1000],
      "question": "人物使用了什么工具？",
      "answer": "用电钻在西瓜上钻孔",
      "confidence": 0.85
    }
  ],
  "current_answer": "电钻",
  "confidence": 0.9,
  "iterations_used": 3
}
```

**设计原则：** 每轮迭代后立即写记忆文件，后续轮次读记忆文件作为唯一事实来源——不怕对话上下文丢失/截断。

---

## 工具使用详解

### videoarm-download
```bash
HTTPS_PROXY=http://127.0.0.1:7890 videoarm-download <URL>
# 返回：{"path": "/path/to/video.mp4", "cached": false}
```

### videoarm-info
```bash
videoarm-info /path/to/video.mp4
# 返回：{"fps": 25.0, "total_frames": 67243, "duration": 2689.74, "has_audio": true}
```

### videoarm-extract-frames（核心工具）
```bash
videoarm-extract-frames \
  --video /path/to/video.mp4 \
  --ranges '[{"start_frame":0,"end_frame":1500}]' \
  --num-frames 30
# 返回：{"image_path": "/tmp/xxx.jpg", ...}
# ⚠️ 返回的是网格图路径，不要自己读取——传给子Agent分析
```

**帧提取策略：**
- 帧在指定范围内**按比例均匀分布**
- 短片断：30帧足以覆盖主要场景
- 场景复杂时可提取多个片段并行分析

### videoarm-audio
```bash
videoarm-audio /path/to/video.mp4 --start 0 --end 300
# 返回：JSON with transcript + segments
# ⚠️ 音频可能很长，立即提取关键引述写入记忆文件
```

---

## 子Agent派发模式

### 模式1：场景快照（粗扫）
```python
sessions_spawn(
  task="""
Read this image and analyze it: /tmp/xxx.jpg
Use the read tool to open it (it supports jpg images).
These are 30 frames from a video (00:00-01:00).
Describe the main scene or action in these frames using a concise English sentence.
Prefix your answer with "Caption: "
""",
  cleanup="delete"
)
```

### 模式2：定向分析（精确问答）
```python
sessions_spawn(
  task="""
Read this image and analyze it: /tmp/xxx.jpg
Use the read tool to open it (it supports jpg images).
These are 24 frames from a video (02:30-04:00).
Context: 演讲者正在介绍产品功能列表
Question: 提到了哪些具体功能模块？
Reply with JSON:
{
  "answer": "详细答案",
  "confidence": 0.85,
  "evidence": ["关键观察1", "关键观察2"]
}
""",
  cleanup="delete"
)
```

---

## 决策框架（何时回答/继续）

### 何时给出答案
- 置信度 > 0.85 且多个来源一致
- 证据链完整
- 接近迭代上限（≤3轮剩余）

### 何时继续探索
- 置信度 < 0.7
- 证据相互矛盾
- 尚未检查最相关段落
- 剩余迭代 > 3轮

---

## 步骤流程（完整工作流）

```
第1轮：初始化
  → videoarm-download 下载视频
  → videoarm-info 获取元数据
  → 创建记忆文件（问题+元数据+空类别）

第2轮：初步采样
  → videoarm-extract-frames 提取开场段帧
  → 派生子Agent生成Caption
  → 写入 scene_snapshots

第3轮：音频（如果需要）
  → videoarm-audio 提取0-5分钟音频
  → 提取关键引述写入 audio_snippets

第4轮：定向分析
  → 基于记忆选择重点时间段
  → 再次提取帧 + 派生子Agent定向问答
  → 写入 frame_analyses

第5轮：综合回答
  → 读记忆文件
  → 综合 scene_snapshots + audio_snippets + frame_analyses
  → 输出答案 + 置信度 + 证据链
```

---

## 适用场景

- **复杂视觉问答**：需要精确回答视频中"谁在何时做了什么"
- **多选项题目**：如视频分析测试、AI面试题等
- **对比分析**：多个视频/片段的视觉特征对比
- **长视频深度理解**：多轮迭代避免一次性token爆炸
- **需要证据链**：最终答案必须附带原始证据

---

## 避坑指南

- **最多10轮迭代**：预算要规划好，不要在无关段落浪费轮次
- **记忆文件是唯一事实源**：不要依赖对话历史中的工具输出，可能被截断
- **并行派发**：多个不相关段落可以同时派发子Agent加速
- **代理设置**：视频下载如需代理，设置 `HTTPS_PROXY` 环境变量
- **帧数选择**：复杂场景30帧够用，场景简单可减少；太多帧会增加子Agent分析负担
- **音频处理**：音频转录可能很长，处理完立即提取关键引述写记忆文件，不要留原始大段文字

---

## 与其他方法的对比

| 维度 | VideoARM | videos_understand | video-vision Skill |
|------|----------|------------------|-------------------|
| 架构 | 编排器+子Agent | 单次直接理解 | 帧提取+视觉API |
| 迭代能力 | ✅ 10轮探索 | ❌ 单次 | ❌ 单次 |
| 记忆机制 | ✅ JSON文件 | ❌ 无 | ❌ 无 |
| 适合问题 | 复杂视觉QA | 快速摘要 | GUI操作/PPT |
| 置信度输出 | ✅ 数值置信度 | ❌ 无 | ❌ 无 |

---

## 参考链接

- ClawHub：https://clawhub.ai/qiankemeng/video-reader
- 安装命令：`clawhub install video-reader`
- 作者：Qianke Meng (@qiankemeng)
- 版本：v4.1.1（2026-03-30更新）
