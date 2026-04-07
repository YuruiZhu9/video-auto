# Video Learn Skill — 多平台视频基本信息提取

## 核心工具/API

| 工具 | 功能描述 |
|------|---------|
| **web_fetch** | 直接请求视频页面，提取 title/description/duration |
| **YouTube Data API** | 结构化获取 YouTube 视频元数据 |
| **Bilibili API** | 获取 B 站视频标题、简介、BV 号 |
| **RapidAPI Video APIs** | 第三方聚合 API，覆盖多平台 |

---

## 步骤流程

```
用户输入：视频链接
       ↓
① 识别平台（YouTube / Bilibili / 抖音 / 腾讯视频 / 爱奇艺）
       ↓
② 调用对应 API / web_fetch 获取基本信息
       ↓
   YouTube → title + description + duration + channel
   Bilibili → 标题 + 简介 + BV号
   抖音    → 标题 + 描述
       ↓
③ 整合输出：视频信息 + 章节（若有）+ 建议观看重点
```

---

## 支持平台矩阵

| 平台 | URL 模式 | 可获取内容 |
|------|---------|-----------|
| YouTube | youtube.com / youtu.be | 标题、描述、时长、频道、观看量 |
| Bilibili | bilibili.com / b23.tv | 标题、简介、BV号、UP主 |
| 抖音 | douyin.com | 标题、描述 |
| 腾讯视频 | v.qq.com | 标题、简介 |
| 爱奇艺 | iq.com | 标题、简介 |

---

## 适用场景

- **快速了解视频主题**：无需观看即可知道视频讲什么
- **视频目录/索引构建**：批量获取大量视频的元信息
- **跨平台视频管理**：统一接口处理多平台视频
- **配合深度解析使用**：先用此 Skill 获取基础信息，再决定用哪种深度解析工具

---

## 局限性

- ❌ **无法直接播放或理解视频画面内容**
- ❌ 无法理解视频中的动态演示/操作
- ❌ 无法提取未在元数据中写明的关键内容
- ✅ 依赖平台支持，部分平台 API 限制较多

---

## 安装方式

```bash
# 通过 clawhub 安装
clawhub install video-learn

# 需要 npm 全局安装 clawhub
npm i -g clawhub
```

---

## 参考链接

- ClawHub: https://clawskills.sh/skills/video-learn
- OpenClaw Skills 文档: https://docs.openclaw.ai/zh-CN/tools/skills
