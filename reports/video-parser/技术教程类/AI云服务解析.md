# 技术教程类 — AI 云服务解析

> 适合不想自行部署、无需本地处理、快速上手的用户

## 核心工具/API

| 工具 | 厂商 | 核心能力 | 免费层级 |
|------|------|----------|----------|
| **ScreenApp** | ScreenApp | 多模态分析、互动问答、摘要生成 | 有（慷慨） |
| **Google Video Intelligence API** | Google Cloud | 2万+标签检测、物体毫秒跟踪 | 有限（前1000分钟） |
| **Azure Video Indexer** | Microsoft | 人脸识别、关键词提取、OCR | 有限（前10小时） |
| **Twelve Labs** | Twelve Labs | 语义搜索（自然语言搜视频） | 有限（API） |
| **Pictory** | Pictory | 自动生成高光片段、自动字幕 | 试用 |

---

## 步骤流程（以 ScreenApp 为例）

### ScreenApp（全中文界面，最简路径）

**步骤一：上传视频**
- 拖拽上传 MP4 / MOV / WEBM
- 或直接粘贴 YouTube / Google Drive 链接

**步骤二：启用深度分析**
- 选择"深度分析"启用：音频转录 + 视觉OCR
- 提示：对于演示文稿和屏幕录像类教程，**务必启用OCR**

**步骤三：查看自动摘要**
- 自动生成：关键主题、演讲者识别、时间戳标记
- 含发言人时间分配统计

**步骤四：Ask AI 查询**
```
示例问题：
- "列出本教程中提到的所有命令和代码"
- "总结本视频的操作步骤"
- "本视频的技术要点有哪些？"
```

---

## 适用场景

- ✅ 快速获取任意视频的结构化摘要，无需本地配置
- ✅ 多人协作：生成的分析结果可分享链接
- ✅ 技术会议/产品发布会视频快速抓取要点
- ✅ 非技术背景用户日常使用
- ✅ 初筛视频：判断某个视频是否值得完整观看

---

## 避坑指南

- **数据隐私**：上传到第三方服务器的视频可能涉及隐私风险
  - 解决：敏感内容使用本地方案（Whisper + Qwen2.5-VL）
  - ScreenApp有隐私声明，但企业用户需确认合规要求
- **免费层级限制**：
  - Google Video Intelligence：每月前1000分钟免费，超出按量付费
  - Azure Video Indexer：每月前10小时，复杂项目容易超限
  - Twelve Labs：无免费层级，企业定价
- **中文转录质量**：Google和Azure对中文术语识别不如Whisper准确
  - 解决：优先选ScreenApp或使用本地Whisper补充
- **API产品无UI**：Google Video Intelligence / Twelve Labs 只有API
  - 解决：需要编写代码调用，适合开发者
- **长视频成本**：云端API按分钟计费，1小时视频可能消耗大量配额
  - 解决：先用ffmpeg裁剪感兴趣段落再上传

---

## 参考链接

- ScreenApp：https://screenapp.io
- Google Video Intelligence API：https://cloud.google.com/video-intelligence
- Azure Video Indexer：https://azure.microsoft.com/en-us/services/video-indexer
- Twelve Labs：https://twelvelabs.io
- Pictory：https://pictory.ai
