---

## 三、Veo 3.1 Lite（谷歌 — 2026-04-01全新上线）

### 3.1 产品概述

**Veo 3.1 Lite** 是谷歌于2026年4月1日发布的视频生成模型，主打**极致性价比**——720p 仅 $0.05/秒，1080p 仅 $0.08/秒，比同类产品成本降低 50%+，是视频生成领域首个"分币时代"产品。

**核心定位**：面向创作者的大规模视频生产工具，兼顾谷歌级画质与超低价格。

### 3.2 核心能力

| 规格 | 参数 |
|------|------|
| 分辨率 | 720p / 1080p |
| 价格（720p）| $0.05/秒 |
| 价格（1080p）| $0.08/秒 |
| 成本对比 | 比同类产品低 50%+ |
| 开发商 | Google DeepMind |
| 更新日期 | 2026-04-01 |

### 3.3 适用场景

- ✅ **大规模短视频生产**：信息流广告、产品展示、社交媒体内容
- ✅ **AI视频创作**：剧情类、概念类视频
- ✅ **降本优先项目**：预算敏感型内容生产
- ⚠️ **极致画质需求**：建议配合 SkyReels V4 使用

### 3.4 使用方法

1. 访问 Google AI Studio 或 Vertex AI（需 GCP 账号）
2. 进入 Veo 3.1 Lite API 控制台
3. 配置输入参数（提示词、分辨率、时长）
4. 调用 API 或通过界面直接生成
5. 下载成品，导入剪映或 FFmpeg 后续处理

### 3.5 提示词示例

```bash
# 基础文本转视频
curl -X POST "https://api.google.ai/v1/veo31/generate" \
  -H "Authorization: Bearer $GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "veo-3.1-lite",
    "prompt": "A woman walking through a rainy Tokyo street at night, neon signs reflecting on wet pavement, cinematic lighting",
    "resolution": "1080p",
    "duration_seconds": 6
  }'
```

### 3.6 选型建议

**Veo 3.1 Lite vs SkyReels V4 怎么选？**

| 维度 | Veo 3.1 Lite | SkyReels V4 |
|------|--------------|-------------|
| 价格 | ⭐⭐⭐⭐⭐ 极低 | ⭐⭐⭐ 适中 |
| 画质 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐⭐⭐ 顶级 |
| 中文支持 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐⭐ 极强 |
| 适合场景 | 大量、快速、商业 | 高端创作、影视级 |

**推荐组合**：Veo 3.1 Lite 生产基础内容 → SkyReels V4 生产精品内容

---
