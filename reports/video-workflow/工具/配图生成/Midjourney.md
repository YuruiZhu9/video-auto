# 配图生成工具对比

## 主流工具对比

| 工具 | 核心能力 | 适用场景 | 免费额度 | 推荐度 |
|------|----------|----------|----------|--------|
| **Midjourney V7** | 高画质艺术风格 | 创意设计 | 有限 | ⭐⭐⭐⭐⭐ |
| **DALL-E 4** | 多模态理解 | 通用图像 | 有限 | ⭐⭐⭐⭐ |
| **Stable Diffusion 4** | 开源可定制 | 本地部署 | 无限 | ⭐⭐⭐⭐ |

---

## Midjourney V7 详细指南

### 1. 访问与使用

1. 加入 Discord 服务器
2. 在 #generate 频道使用
3. 或在个人服务器使用

### 2. 基础命令

```bash
/imagine [提示词]
```

### 3. 提示词结构

**基础公式**：
```
[主体] [动作] [环境] [风格] [技术参数]
```

**示例**：
```
A cute robot, sitting on a desk, modern office, Pixar style, 3D render, 8k, soft lighting
```

### 4. 参数设置

| 参数 | 说明 | 选项 |
|------|------|------|
| `--ar` | 宽高比 | 16:9, 9:16, 1:1, 4:3 |
| `--v` | 版本 | v1-v7 |
| `--q` | 质量 | .25, .5, 1, 2 |
| `--s` | 风格化 | 0-1000 |
| `--iw` | 图像权重 | 0-2 |

### 5. 常用命令

```
/imagine: 生成图片
/settings: 设置选项
/describe: 图生文
/blend: 图混合
```

### 6. 进阶技巧

#### 风格关键词
- Photorealistic（写实）
- Illustration（插画）
- Anime（动漫）
- 3D Render（3D渲染）
- Oil painting（油画）

#### 灯光关键词
- Cinematic lighting（电影光）
- Soft lighting（柔光）
- Golden hour（金色时刻）
- Volumetric lighting（体积光）

#### 构图关键词
- Wide shot（广角）
- Close-up（特写）
- Over the shoulder（过肩）
- Bird's eye（鸟瞰）

---

## DALL-E 4 指南

### 1. 访问方式

1. ChatGPT Plus 订阅
2. 或使用 OpenAI API

### 2. 使用方法

在 ChatGPT 中：
```
Generate an image of [描述]
```

### 3. 特点

- **优势**：多模态理解强，对话式生成
- **劣势**：艺术风格不如 Midjourney
- **适合**：需要理解复杂场景

---

## Stable Diffusion 4 本地部署

### 1. 安装

```bash
# 使用 AUTOMATIC1111 WebUI
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
cd stable-diffusion-webui
./webui.sh
```

### 2. 模型下载

推荐模型：
- SDXL 1.0
- Juggernaut XL
- Realistic Vision

### 3. 本地部署优势

- 完全免费
- 无生成限制
- 可训练自定义模型
- 隐私安全

### 4. 硬件要求

| 配置 | 推荐 |
|------|------|
| 显存 | 8GB+ (12GB 最佳) |
| 内存 | 16GB+ |
| 存储 | 50GB+ |

---

## 工作流集成

### 场景选择

| 场景 | 推荐工具 |
|------|----------|
| 创意概念图 | Midjourney |
| 产品展示 | DALL-E |
| 角色设计 | Midjourney |
| 批量生成 | Stable Diffusion |
| 本地隐私 | Stable Diffusion |

### 生成流程

1. **明确需求**：确定图片用途和风格
2. **生成测试**：先生成3-5个版本
3. **选择最佳**：根据需求选择
4. **后期处理**：导入PS/剪映调整

### 参数建议

| 场景 | 参数建议 |
|------|----------|
| 社交媒体 | --ar 9:16 --q 1 |
| 视频封面 | --ar 16:9 --q 2 |
| 打印物料 | --ar 4:3 --q 2 --v 7 |

---

## 版权说明

- Midjourney：付费会员可商用
- DALL-E：API/Plus 可商用
- Stable Diffusion：开源可商用（注意模型授权）

---

## 版本历史

| 版本 | 发布 | 主要更新 |
|------|------|----------|
| V7 | 2026 | 高画质，艺术风格增强 |
| V6 | 2025 | 文本理解提升 |
| V5 | 2024 | 写实风格增强 |
