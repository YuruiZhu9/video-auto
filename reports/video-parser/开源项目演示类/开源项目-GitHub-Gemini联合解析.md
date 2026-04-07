# 开源项目演示类 - GitHub + 视频联合解析方案

## 核心工具/API

- **videos_understand**：分析演示视频中的操作流程和功能展示
- **FFmpeg**：提取关键帧，分析截图中的代码和 UI
- **GitHub Skill**：获取项目 README、技术栈、代码结构
- **images_understand**：批量分析提取的视频帧

## 步骤流程

```
1. 获取 GitHub 项目信息（名称、技术栈、README）
2. videos_understand 分析演示视频
3. FFmpeg 提取关键帧（每2秒一帧）
4. images_understand 批量分析帧图片
5. LLM 整合视频 + GitHub 信息 → 结构化报告
```

## 适用场景

- ✅ GitHub README 配套视频 → 理解项目价值
- ✅ 技术 demo 视频 → 提取操作步骤
- ✅ 功能演示 → 验证文档与实现是否一致
- ✅ 项目评估 → 快速了解能力节省阅读时间

## 避坑指南

- ⚠️ 视频版本旧于 GitHub → 标注版本差异
- ⚠️ 代码一闪而过 → 用 FFmpeg 逐帧分析
- ⚠️ GitHub 仓库已删除 → 无法交叉验证

## 参考链接

- [GitHub Skill](/app/openclaw/skills/github/SKILL.md)
- [FFmpeg video-frames](/app/openclaw/skills/video-frames/SKILL.md)
