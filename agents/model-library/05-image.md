# 🎨 图像生成

> 来源：跨Agent新技术同步中心 — 模型库  
> 维护方式：参考 CHANGELOG.md 按日期追加

---

## 🖼️ 图像生成模型

| 模型/工具 | 核心能力 | 适用场景 | 替代方案 | 更新时间 |
|-----------|----------|----------|----------|----------|
| **MAI-Image-2**（微软）| 微软自研图像生成模型，LMArena排行榜**全球第三**（仅次于GPT-Image-1.5和Nano Banana 2）；微软Super Intelligence部门首款产品；10人团队用一半GPU完成训练；已部署至Copilot/Bing和PowerPoint；提升图像真实感、细节质感、商业可用性；适用海报/信息图/品牌图形/产品可视化/营销素材 | 图像生成、Bing搜索增强、**PPT设计**、海报设计、营销素材 | GPT-Image-1.5、Nano Banana 2、DALL-E 4、Midjourney V7 | 2026-04-06 |
| Wan2.7-Image（阿里）| 解决AI生成图像"千篇一律"问题，人像定制、色彩控制和长文本渲染方面实现突破，开启"千人千面"新时代 | 人像定制、创意设计、内容生成 | Midjourney、DALL-E 4 | 2026-04-02 |
| 闲鱼AI相机（阿里）| 闲鱼推出的AI拍照发布工具，拍照后5秒自动识别商品并生成描述，一键发布，大幅降低二手交易门槛 | 二手电商、商品拍摄、AI内容生成 | - | 2026-03-26 |
| Loki.Build | AI设计落地页 | UI设计、网站创建 | - | 2026-03-13 |
| Midjourney V7 | 高画质艺术风格 | 创意设计 | DALL-E 4 | - |
| DALL-E 4 | 多模态理解 | 通用图像 | Midjourney | - |
| Stable Diffusion 4 | 开源可定制 | 本地部署 | - | - |

---

## ☁️ 免费图像生成 API

| 平台 | 模型 | 免费额度 | 注册地址 | API格式 | 备注 |
|------|------|---------|---------|---------|------|
| **Hypereal AI** | Flux 2 / SDXL / SeeDream 4.0 / Recraft / Qwen Image | **35免费积分**（可生成数千张） | https://hypereal.ai/dashboard → API Keys | REST: `POST https://api.hypereal.ai/v1/generate/image` | $0.001/张起，统一密钥 |
| **阿里云通义万相** | Wanx2.1 | 新用户免费试用 | https://dashscope.console.aliyun.com/ | REST / Python SDK | 需阿里云账号 |
| **讯飞星火** | 图像生成模型 | 新用户免费额度 | https://xinghuo.xfyun.cn/ | REST API | 需讯飞账号 |
| **Stability AI** | Stable Diffusion 3 / SDXL | 每月25免费积分 | https://platform.stability.ai/ → API Keys | REST | 免费输出带水印 |
| **laozhang.ai（中转）** | DALL-E 3 / GPT-4o / Gemini / 通义万相 | 新用户注册送免费积分 | https://api.laozhang.ai/register/ | 兼容OpenAI格式，国内直连 | 中转服务，价格低30-50% |

---

## 📌 图像生成选型速查

| 需求 | 推荐方案 |
|------|----------|
| **全球质量顶尖** | MAI-Image-2（LMArena第三，微软）🆕 |
| 最高画质/艺术感 | Midjourney V7 |
| 开源可商用 | Stable Diffusion 4 / Hypereal AI（Flux 2）|
| 免费API首选 | Hypereal AI（35积分≈数千张，统一API）|
| 中文生态 | 通义万相 / 讯飞星火 |
| 二手电商商品图 | 闲鱼AI相机（阿里）|

---

> 📅 更新日志见 CHANGELOG.md — 图像生成相关条目
