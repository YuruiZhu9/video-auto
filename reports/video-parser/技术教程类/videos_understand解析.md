# 技术教程类 - videos_understand 多模态解析

## 核心工具/API

- **videos_understand**（内置工具）：多模态视频理解，支持本地文件和 URL
  - 最大同时分析：10 个视频
  - 支持格式：mp4, mov, avi, mkv, webm 等主流格式
  - 底层模型：MiniMax 视频理解模型

- **images_understand**（配合使用）：逐帧图片分析
  - 最大同时分析：20 张图片
  - 适合精细化 OCR 和截图分析

- **audios_understand**（配合使用）：音频理解/转录
  - 最大同时分析：10 个音频

## 步骤流程

### 基础用法：直接分析视频

```python
# 工具调用示例
videos_understand(videos_info=[
  {
    "file": "/workspace/videos/tutorial.mp4",
    "url": "",
    "prompt": "请详细描述这个技术教程视频的内容，包括：1. 主题和难度等级；2. 主要步骤和知识点；3. 使用的工具和环境；4. 代码或命令示例；5. 总结3-5个核心要点。"
  }
])
```

### 进阶流程：分段深度分析

```bash
# Step 1: 获取视频时长和基本信息
ffprobe -v quiet -show_entries format=duration,size -of csv=p=0 tutorial.mp4
# 输出示例：3600.000,524288000 （时长3600秒，大小500MB）

# Step 2: 计算分段（每5分钟一段，3600秒分12段）
# 每段: 0-5min, 5-10min, ... 55-60min

# Step 3: 用 FFmpeg 提取每段关键帧（每段3帧）
for i in {0..11}; do
  ts=$((i * 300))
  mm=$((ts / 60))
  ffmpeg -ss $ts -i tutorial.mp4 -frames:v 3 -q:v 2 "frame_${mm}m_%d.jpg" 2>/dev/null
done

# Step 4: 用 images_understand 分析每段截图
images_understand(image_info=[
  {"file": "frame_0m_1.jpg", "prompt": "这是0-5分钟截取的3帧，描述界面内容和讲解要点"},
  {"file": "frame_5m_1.jpg", "prompt": "这是5-10分钟截取的3帧，描述界面内容和讲解要点"},
  # ... 更多帧
])

# Step 5: 用 videos_understand 做整体理解
videos_understand(videos_info=[
  {
    "file": "tutorial.mp4",
    "prompt": "结合之前帧的分析，这是一个[主题]教程视频，请输出结构化笔记"
  }
])
```

### 场景检测 + 关键帧分析

```bash
#!/bin/bash
# extract_keyframes.sh - 自动提取场景变化关键帧
VIDEO="$1"
OUT_DIR="keyframes_$(date +%s)"
mkdir -p "$OUT_DIR"

# 方法：按时间均匀采样 + 场景变化检测
# 均匀采样：每30秒一帧
TOTAL=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VIDEO")
FPS=$(echo "scale=2; $TOTAL/30" | bc)

ffmpeg -i "$VIDEO" -vf "fps=1/30,scale=640:-1" -q:v 2 "${OUT_DIR}/kf_%04d.jpg" -y

echo "提取 $(ls ${OUT_DIR} | wc -l) 个关键帧到 ${OUT_DIR}"

# 批量传给 images_understand
ffind "${OUT_DIR}" -name "*.jpg" | while read f; do
  echo "$f"
done > keyframe_list.txt
```

## 适用场景

- ✅ **复杂技术教程**：多步骤、含大量界面截图的深度解析
- ✅ **代码演示类视频**：逐帧 OCR 提取代码片段
- ✅ **架构图/流程图讲解**：截图保存+结构化描述
- ✅ **PPT 演示型教程**：提取每页 PPT 内容并整理
- ✅ **论文精读/研究分享**：分析图表、公式、实验数据
- ⚠️ **超长视频（>1小时）**：建议先分段处理，避免单次分析超出上下文限制

## 避坑指南

### ❌ 常见问题 1：视频格式不支持
**原因**：某些特殊编码（如 ProRes RAW、RED R3D）OpenClaw 无法直接处理
**解决**：先转码 `ffmpeg -i input.raw -c:v libx264 -acodec aac output.mp4`

### ❌ 常见问题 2：分析结果太笼统
**原因**：prompt 不够具体，模型自由发挥
**解决**：使用结构化 prompt，明确要求输出格式：
```
请按以下JSON格式输出：
{
  "title": "视频标题",
  "difficulty": "初级/中级/高级", 
  "steps": [{"time": "0:00", "action": "操作描述", "command": "命令/代码"}],
  "key_concepts": ["知识点1", "知识点2"],
  "resources": ["工具名1", "链接1"]
}
```

### ❌ 常见问题 3：关键帧提取不准，漏掉重要内容
**原因**：均匀采样忽略内容密度差异
**解决**：先用 `videos_understand` 做粗筛（`--prompt "标记内容密度高的时段"`），再针对这些时段提取更多帧

### ❌ 常见问题 4：本地视频路径问题
**原因**：视频路径含中文/空格，工具无法识别
**解决**：`ffmpeg -i "input file.mp4" -c copy output.mp4` 重命名；或使用绝对路径

## 组合最佳实践

```
技术教程视频解析推荐流程：

1. 视频URL/本地文件
       ↓
2. summarize --youtube/URL → 获取字幕 + 初步摘要
       ↓
3. FFmpeg 提取音频 → Whisper 转录（增强字幕）
       ↓
4. videos_understand → 多模态整体理解
       ↓
5. FFmpeg 关键帧 + images_understand → 截图/代码 OCR
       ↓
6. 汇总 → 结构化笔记（步骤 + 代码 + 要点 + 资源链接）
```

## 参考链接

- OpenClaw 内置工具：`videos_understand`、`images_understand`、`audios_understand`
- FFmpeg Skill：`/app/openclaw/skills/video-frames/SKILL.md`
- Whisper Skill：`/app/openclaw/skills/openai-whisper/SKILL.md`
