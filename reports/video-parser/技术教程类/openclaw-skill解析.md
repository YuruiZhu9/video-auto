# 技术教程类 - OpenClaw Skill 解析方案

> 解析类型：技术教程视频（编程教学、工具使用、操作演示）  
> 更新时间：2026-04-08

---

## 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| `videos_understand` | OpenClaw 内置多模态视频理解工具，分析视频内容 |
| `summarize` skill | 快速总结 YouTube 视频、提取字幕和结构 |
| `video-frames` skill | ffmpeg 帧提取，截取关键步骤画面 |
| `audios_understand` | 音频理解，适合无字幕教程的声音分析 |
| LLM API（智谱 GLM-4-Flash 等）| 文字稿深度结构化处理 |

---

## 步骤流程

### 方案 A：一站式 LLM 视频理解（推荐）

适用：各类技术教程视频，步骤最简

```
输入视频 → videos_understand → 结构化总结
```

```python
# OpenClaw Agent 调用示例
videos_understand(
  videos_info=[
    {
      "file": "/workspace/tutorials/react-hooks.mp4",
      "prompt": """请详细分析这个技术教程视频：
1. 视频主题与难度级别
2. 按时间顺序列出所有操作步骤
3. 每个步骤涉及的关键命令/代码片段
4. 教程中提到的坑点和注意事项
5. 总结这个教程的核心知识点（50字以内）
6. 推荐学习这个教程的人群"
    }
  ]
)
```

### 方案 B：多工具组合解析（高精度）

适用：代码演示类、需要提取具体命令的教程

```
视频 → ffmpeg帧提取 → 关键帧截图 → images_understand(批量) → 文字稿整理
  ↓
音频分离 → Whisper转写 → LLM结构化
```

**Step 1：提取关键帧（每30秒一帧）**

```bash
ffmpeg -i tutorial.mp4 -vf "fps=1/30" -q:v 3 frames_%04d.jpg
```

**Step 2：批量分析截图中的代码内容**

```python
images_understand(
  image_info=[
    {"file": "frames_0001.jpg", "prompt": "提取图中所有代码，标注语言和关键功能"},
    {"file": "frames_0002.jpg", "prompt": "描述当前操作步骤，配合代码截图"},
    # ... 继续处理所有帧
  ]
)
```

**Step 3：音频转文字稿**

```bash
# 提取音频
ffmpeg -i tutorial.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav

# 用 audios_understand 分析（内置Whisper）
audios_understand(
  audio_info=[
    {
      "file": "/workspace/audio.wav",
      "prompt": "请转录这段技术教程的音频，并标注时间戳（格式：00:00:00）"
    }
  ]
)
```

**Step 4：LLM 二次结构化**

```
将截图分析 + 音频转写结果合并 → 发送给智谱GLM-4-Flash → 输出结构化教程文档
```

---

## 适用场景

- **编程教学视频**：Python/JavaScript/Go 等语言教学
- **工具使用教程**：VSCode、Docker、K8s 等工具操作演示
- **命令行教学**：Terminal、Git、npm 等命令操作
- **设计软件教程**：Figma、Photoshop、Blender 操作演示
- **AI工具使用**：ChatGPT、Claude、Midjourney 等工具教程

---

## 避坑指南

### ⚠️ 代码截图识别错误
**问题**：低分辨率截图中的代码被错误识别  
**解决**：提取帧时使用 PNG 格式或高分辨率 JPEG，控制缩放

```bash
# 高质量帧提取
ffmpeg -i tutorial.mp4 -ss 00:01:00 -vframes 1 -q:v 2 highres_frame.png
```

### ⚠️ 口语化表达干扰结构
**问题**：教程中的"呃"、"这个"、"然后"等口头禅影响文字稿可读性  
**解决**：在 LLM prompt 中明确要求"去除口语化表达，整理为正式技术文档格式"

### ⚠️ 长教程分集处理
**问题**：超过 30 分钟的教程视频，LLM 上下文窗口不够  
**解决**：按自然段落（章节）分段，用 ffmpeg 切割后分别处理

```bash
# 提取视频前10分钟
ffmpeg -i long_tutorial.mp4 -ss 00:00:00 -to 00:10:00 -c copy part1.mp4
# 提取10-20分钟
ffmpeg -i long_tutorial.mp4 -ss 00:10:00 -to 00:20:00 -c copy part2.mp4
```

### ⚠️ 演示类教程缺少字幕
**问题**：纯操作演示无旁白，无法提取文字内容  
**解决**：使用 `videos_understand` 多帧分析画面操作步骤，结合用户推断意图

---

## 输出示例

```markdown
# React Hooks 完整教程笔记

## 基本信息
- **难度**：入门 → 中级
- **时长**：约 45 分钟
- **涵盖 Hooks**：useState, useEffect, useContext, useReducer

## 核心知识点

### 1. useState（00:02:15）
- 状态初始化：`const [count, setCount] = useState(0)`
- 函数式更新：`setCount(prev => prev + 1)`
- ⚠️ 注意：状态更新是异步的

### 2. useEffect（00:15:30）
- 基本用法：组件挂载后执行副作用
- 清理函数：return () => { ... }
- ⚠️ 依赖数组必须填写，否则会导致无限循环

## 命令/代码速查
```bash
npx create-react-app my-app
npm install use-history
```
```

---

## 参考链接

- OpenClaw videos_understand：内置 MCP 工具
- summarize skill：`/app/openclaw/skills/summarize/SKILL.md`
- video-frames skill：`/app/openclaw/skills/video-frames/SKILL.md`
- Whisper GitHub：https://github.com/openai/whisper
- 智谱 AI：https://open.bigmodel.cn/
