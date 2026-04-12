# 通用工具类 - bilibili-analyzer-skill（B站视频 AI 分析技能）

## 核心工具/API

- **bilibili-analyzer**：.NET 10 SDK 驱动的 B站视频 AI 分析技能
- **Bilibili API**：通过 SocialSisterYi/bilibili-API-collect 获取视频信息
- **FFmpeg**：视频帧提取，支持自定义帧率和相似度去重
- **Task 工具（Agent）**：分批并行分析提取的帧图片
- **文档生成器**：将分析结果重组为结构化文档

## 步骤流程

1. **安装环境**（.NET 10 SDK + FFmpeg）
2. **下载视频并拆帧**：`dotnet run scripts/prepare.cs "<视频URL>" -o <输出目录> --fps 1`
3. **AI 分批分析帧图片**：使用 Task 工具分批并行分析
4. **生成结构化文档**：实操类→操作教程，知识类→专题文档

## 适用场景

- 编程教程分析（直接提取视频帧中的代码）
- 软件操作演示生成配置指南
- B站视频知识库批量沉淀

## 避坑指南

- 必须安装 .NET 10 SDK（不是旧版本）
- FFmpeg 必须提前安装
- 帧率设置决定质量（短视频1fps，长视频0.2fps）
- 文档必须按主题重组，非时间线流水账
- 图文对应必须验证，不可凭空描述

## 质量检查清单

- [ ] 内容按主题重组，非时间线流水账
- [ ] 章节逻辑清晰，不看视频也能理解
- [ ] 每张图标注帧号，描述准确反映实际内容
- [ ] 代码来自图片实际代码，可直接复制

## 核心洞察

1. 代码友好：直接从视频帧提取代码，准确率高于语音识别
2. 文档质量最高：按主题重组，生成文档可独立阅读
3. .NET 单文件执行：`dotnet run` 一键执行
4. 适合知识沉淀：输出文档可直接作为团队知识库存档

## 参考链接

- 技能详情：https://skillsmp.com/zh/skills/aidotnet-moyucode-skills-tools-bilibili-analyzer-skill-md
- B站 API：https://github.com/SocialSisterYi/bilibili-API-collect
