# 技术教程类 - OpenClaw视频理解Skill解析

## 核心工具/API

| 工具 | 功能描述 |
|------|---------|
| **video-learn Skill** | 视频理解与分析能力，支持YouTube/Bilibili等主流平台 |
| **video-frames Skill** | 从视频提取帧/片段 |
| **summarize Skill** | 文字总结与字幕提取 |
| **videos_understand** | 多模态AI深度理解视频内容 |

## 步骤流程

### 工作流概览

```
视频链接/文件
    │
    ├─→ video-learn Skill ──→ 提取元信息（标题/时长/描述/章节）
    ├─→ summarize Skill ──→ 获取文字摘要/字幕
    └─→ videos_understand ──→ 深度内容理解+结构化输出
```

### Step 1：识别平台，调用合适API

**YouTube：**
- API：YouTube Data API v3
- 获取：标题、描述、时长、标签、章节信息
- 接口示例：`GET /youtube/v3/videos?part=snippet,contentDetails&id=VIDEO_ID`

**Bilibili：**
- API：Bilibili API（非官方）
- 获取：标题、简介、BV号、UP主信息、分P列表
- 字幕需额外获取：AV号 → subtitle API

**其他平台（抖音/快手/小红书）：**
- MCP `parse_video` 工具：一键解析获取无水印链接+元信息

### Step 2：提取关键内容

```bash
# summarize快速获取摘要
summarize "https://youtu.be/xxxxx" --youtube auto --extract-only

# 提取Bilibili字幕（B站有官方字幕API）
# 通过BV号请求字幕接口
```

### Step 3：深度理解（videos_understand）

```
视频 → videos_understand → 结构化JSON输出

提取内容：
{
  "主题": "...",
  "难度": "入门/进阶/高级",
  "知识点": [
    {"时间": "00:03:20", "标题": "变量类型", "摘要": "..."},
    ...
  ],
  "代码示例": [...],
  "配图说明": [...],
  "学习路径建议": "..."
}
```

## 适用场景

- 技术博客/公众号配图素材提取
- 课程笔记自动生成
- 技术视频快速预筛（判断是否值得完整观看）
- 视频内容索引建立
- 跨平台技术内容聚合

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Bilibili需要登录才能获取字幕 | 平台限制 | B站部分字幕需要大会员，用 `--extract-only` 降级获取 |
| videos_understand 处理长视频token不足 | 模型上下文限制 | 先用 `ffmpeg -t 600` 切分，每段≤10分钟 |
| 平台元信息不全 | API版本问题 | 检查API Key权限，YouTube用Data API v3 |
| 抖音/快手链接无法直连下载 | 平台防盗链 | 用 `parse_video` MCP工具处理 |
| 视频内容理解偏差 | AI对专业术语理解不足 | 提供更多上下文 prompt，减少幻觉 |

## Skill安装方式

```bash
# video-learn（视频理解）
clawhub install video-learn

# video-frames（帧提取）
# 内置技能，无需安装，ffmpeg已具备

# summarize（总结）
brew install steipete/tap/summarize
```

## 参考链接

- video-learn Skill：https://llmbase.ai/openclaw/video-learn/
- OpenClaw Skills文档：https://docs.openclaw.ai/zh-CN/tools/skills
- ClawHub视频相关：https://clawhub.com/skills/video
