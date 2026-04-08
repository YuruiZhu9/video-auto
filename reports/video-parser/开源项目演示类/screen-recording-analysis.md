# 开源项目演示类 - 录屏视频结构化解析

> 解析类型：GitHub 项目演示、工具使用演示、技术 demo 视频  
> 更新时间：2026-04-08

---

## 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| **videos_understand** | 端到端视频内容理解 |
| **video-frames skill (ffmpeg)** | 关键帧提取 |
| **images_understand** | 批量截图分析（代码识别）|
| **Whisper** | 音频转文字 |
| **GitHub API** | 获取项目元信息 |

---

## 步骤流程

### 完整流水线

```
录屏视频
  │
  ├─ 1. 场景分割（ffmpeg）
  │     └─ 按时间轴切分为操作片段
  │
  ├─ 2. 关键帧提取（每段1-3帧）
  │     └─ 保存 PNG 高质量截图
  │
  ├─ 3. 批量图像分析（images_understand）
  │     └─ 识别代码、UI、命令
  │
  ├─ 4. 音频转写（Whisper）
  │     └─ 提取旁白/解说
  │
  └─ 5. LLM 结构化整合
        └─ 还原完整操作步骤文档
```

### Step 1：场景分割

```bash
# 方案A：按时间均匀分段（每段30秒）
ffmpeg -i demo.mp4 -f segment -segment_time 30 -c copy segments/seg_%03d.mp4

# 方案B：场景变化检测分割
ffmpeg -i demo.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | \
  grep showinfo | awk -F pts_time: '{print $2}' | tr -d ']' > scene_times.txt

# 方案C：手动指定分割点
ffmpeg -i demo.mp4 -ss 00:00:00 -to 00:02:30 -c copy part1.mp4
ffmpeg -i demo.mp4 -ss 00:02:30 -to 00:05:00 -c copy part2.mp4
```

### Step 2：关键帧提取

```bash
# 每个片段提取首帧（展示整体）+ 中间帧（展示操作）
for f in segments/*.mp4; do
  name=$(basename "$f" .mp4)
  # 首帧
  ffmpeg -i "$f" -ss 00:00:01 -vframes 1 -q:v 2 "${name}_start.jpg"
  # 中间帧
  dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")
  ffmpeg -i "$f" -ss "00:00:$(echo "$dur/2" | bc)" -vframes 1 -q:v 2 "${name}_mid.jpg"
done
```

### Step 3：批量图像分析

```python
# OpenClaw Agent 调用
images_understand(
  image_info=[
    {"file": "segments/seg_001_start.jpg", "prompt": "识别图中代码语言、关键API、UI元素"},
    {"file": "segments/seg_001_mid.jpg", "prompt": "描述当前操作步骤，推断即将执行的命令"},
    {"file": "segments/seg_002_start.jpg", "prompt": "识别图中代码语言、关键API、UI元素"},
    {"file": "segments/seg_002_mid.jpg", "prompt": "描述当前操作步骤，推断即将执行的命令"},
  ]
)
```

### Step 4：音频转写

```bash
# 提取音频
ffmpeg -i demo.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav

# 用 audios_understand 分析
audios_understand(
  audio_info=[{
    "file": "/workspace/audio.wav",
    "prompt": "转录技术演示旁白，标注时间戳，识别所有命令和代码片段"
  }]
)
```

### Step 5：LLM 结构化整合

```python
# OpenClaw videos_understand 一站式分析（替代 Steps 3-5）
videos_understand(
  videos_info=[{
    "file": "/workspace/demo.mp4",
    "prompt": """详细分析这个开源项目演示视频：
1. 项目名称和用途（根据视频内容推断）
2. 按时间顺序还原所有操作步骤
3. 每个步骤使用的命令/代码（请完整列出）
4. 涉及的关键文件和目录结构
5. 需要的前置环境/依赖（Docker、Node.js等）
6. 视频中演示的核心功能点
7. GitHub 仓库地址（如果出现）
8. 演示过程中的坑点和注意事项"""
  }]
)
```

---

## 适用场景

| 场景 | 推荐方案 |
|------|----------|
| GitHub README 配套视频 | videos_understand 一站式 |
| 详细技术 demo 演示 | 流水线：帧提取 + 图像分析 + LLM |
| 快速了解项目功能 | summarize skill YouTube模式 |
| 需要提取命令/代码 | 帧提取 + images_understand |

---

## 避坑指南

### ⚠️ 代码截图不清晰
**问题**：终端字体小、代码行密集，识别困难  
**解决**：提取高分辨率帧，或指定 ffmpeg 输出 PNG

```bash
ffmpeg -i demo.mp4 -ss 00:01:00 -vframes 1 -vf "scale=1920:1080" -q:v 1 output.png
```

### ⚠️ 演示者语速快/口音重
**问题**：音频转写错误率高  
**解决**：结合图像分析互相印证，不要完全依赖语音

### ⚠️ 多显示器/窗口切换
**问题**：录屏包含多个窗口，难以理解上下文  
**解决**：在 prompt 中明确要求"识别当前焦点窗口"

```python
"prompt": "识别当前焦点窗口，忽略背景窗口，专注描述主操作区的代码/界面"
```

### ⚠️ 缺少 GitHub 链接
**问题**：视频不直接展示仓库地址  
**解决**：通过搜索引擎搜索视频标题 + 项目名，或用 GitHub API 模糊匹配

```bash
# 搜索相关项目
curl "https://api.github.com/search/repositories?q=$(echo $PROJECT_NAME | sed 's/ /+/g')"
```

---

## 输出格式示例

```markdown
# 开源项目演示解析：[项目名称]

## 项目信息
- **名称**：[推断自视频]
- **类型**：CLI工具 / Web应用 / SDK / ...
- **技术栈**：[推断]
- **GitHub**：[URL或"未在视频中出现"]

## 操作步骤

### 第一步：环境准备（00:00:10 - 00:01:30）
**操作**：克隆仓库、安装依赖  
**命令**：
```bash
git clone https://github.com/xxx/yyy
cd yyy
npm install
```

### 第二步：配置（00:01:30 - 00:02:45）
**操作**：设置配置文件  
**命令**：
```bash
cp .env.example .env
# 编辑 .env 文件
```

### 第三步：运行（00:02:45 - 00:04:00）
**操作**：启动服务  
**命令**：
```bash
npm run dev
```

## 关键知识点
- [知识点1]
- [知识点2]

## 注意事项
- ⚠️ Node 版本要求 >= 18
- ⚠️ 需要先申请 API Key
```

---

## 参考链接

- OpenClaw videos_understand：内置 MCP 工具
- video-frames skill：/app/openclaw/skills/video-frames/SKILL.md
- images_understand：内置 MCP 工具
- Whisper：https://github.com/openai/whisper
- GitHub API：https://docs.github.com/en/rest
