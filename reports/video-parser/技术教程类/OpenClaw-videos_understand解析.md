# 技术教程类 - OpenClaw videos_understand 工具

## 核心工具/API

- **videos_understand**：OpenClaw 内置多模态视频理解工具
  - 调用后端多模态模型（Gemini 等）理解视频内容
  - 支持本地视频文件和 URL
  - 可传入 prompt 指定分析维度（如"列出所有技术要点"、"提取代码示例"）
- **Gemini API**（Google）：视频 + 音频联合多模态分析
  - 模型：`gemini-3-flash-preview`（快速）/ `gemini-3-pro-preview`（丰富）
  - 自动分析视频画面 + 音频内容
- **OpenClaw 内置自动检测**：若未配置，自动回退到当前活动模型
  - 图片/视频/音频按配置优先级自动选择

## 步骤流程

### 方式一：直接使用 videos_understand（推荐）

```
1. 传入视频文件路径或 URL
2. 指定分析 prompt（如"请总结这个技术教程的核心内容和步骤"）
3. videos_understand 返回结构化分析结果
```

**OpenClaw 调用示例**：
```
/path/to/video.mp4 → videos_understand(prompt="提取视频中的技术要点、代码示例、操作步骤")
```

### 方式二：通过媒体理解配置（自动预处理）

```json5
// openclaw.json 配置
{
  tools: {
    media: {
      video: {
        enabled: true,
        maxChars: 2000,
        models: [
          { provider: "google", model: "gemini-3-flash-preview" },
          {
            type: "cli",
            command: "gemini",
            args: ["-m", "gemini-3-flash", "--allowed-tools", "read_file",
                   "Read the media at {{MediaPath}} and describe it in <= {{MaxChars}} characters."],
            capabilities: ["image", "video"],
          }
        ]
      }
    }
  }
}
```

## 适用场景

- ✅ **技术教程视频** - 提取操作步骤、命令、代码片段
- ✅ **长视频（>30分钟）** - 自动分段 + 重点提炼
- ✅ **多语言教程** - Gemini 支持多语言理解
- ✅ **屏幕录制演示** - 识别界面操作和代码
- ✅ **不确定视频内容时** - 先用此工具快速了解全貌

## 避坑指南

- ⚠️ **视频文件过大**（>50MB）：配置 `maxBytes` 限制，或先压缩
- ⚠️ **默认 maxChars=500**：技术教程内容多，建议调大到 1500-2000
- ⚠️ **API 费用**：Gemini API 有调用成本，注意频率控制
- ⚠️ **视频时长过长**：可先用 FFmpeg 截取关键片段再分析
- ⚠️ **中文视频**：确保 prompt 用中文，避免输出语言混乱

## 参考链接

- [OpenClaw 媒体理解文档](https://docs.openclaw.ai/zh-CN/nodes/media-understanding)
- [Gemini API Video Understanding](https://ai.google.dev/gemini-api/docs/vision)
- [video-frames Skill](/app/openclaw/skills/video-frames/SKILL.md)
