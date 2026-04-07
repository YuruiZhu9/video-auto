# PixVerse V6 完整使用指南

> 🤖 由「AI视频制作Agent」维护  
> 更新时间：2026-04-03  
> 数据来源：PixVerse官方 / AITOP100

---

## 一、产品概述

**PixVerse V6** 是爱诗科技于2026年4月2日发布的视频生成模型，是国内3D视频生成头部公司爱诗科技的旗舰产品。

**核心定位**：Sora关停后的最强替代方案，主打**时空处理能力大幅提升**，尤其在**物理真实感**方面表现突出，是国内视频创作者的首选之一。

| 规格 | 参数 |
|------|------|
| 发布日期 | 2026-04-02 |
| 开发商 | 爱诗科技 |
| 核心突破 | 时空处理能力大增，物理真实感最强 |
| 市场定位 | Sora替代首选 |
| 融资规模 | 3亿美元C轮（2026-03-14）|

---

## 二、核心能力

### 2.1 视频生成质量

| 维度 | 评分 | 说明 |
|------|------|------|
| 画质 | ⭐⭐⭐⭐⭐ | 高清输出，细节丰富 |
| 物理真实感 | ⭐⭐⭐⭐⭐ | 时空处理大增，物体运动符合物理规律 |
| 人物一致性 | ⭐⭐⭐⭐ | 跨镜头角色保持一致 |
| 运动流畅度 | ⭐⭐⭐⭐ | 运动轨迹自然，无明显畸变 |
| 中文支持 | ⭐⭐⭐⭐ | 中文提示词理解优秀 |

### 2.2 主要功能

- **文本转视频（T2V）**：输入文字描述，生成高质量视频
- **图片转视频（I2V）**：上传图片，让静态图像动起来
- **角色一致性**：通过种子/角色ID保持跨镜头角色一致
- **运镜控制**：支持多种镜头运动（推拉摇移）
- **风格预设**：动漫/写实/电影等多种风格一键切换
- **画面扩展**：对已有画面进行扩展

---

## 三、使用方法

### 3.1 在线平台（推荐新手）

1. **访问官网**：`https://pixverse.ai`
2. **注册/登录**：支持Google账号直接登录
3. **选择模式**：T2V（文本）或 I2V（图片）
4. **输入提示词**：使用英文提示词效果更稳定
5. **调节参数**：时长、分辨率、运动强度
6. **生成视频**：等待1-3分钟
7. **下载/编辑**：高清下载或直接进入剪辑

### 3.2 API调用（适合批量生产）

```bash
# PixVerse V6 API 调用示例
curl -X POST "https://api.pixverse.ai/v1/generate" \
  -H "Authorization: Bearer $PIXVERSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "pixverse-v6",
    "prompt": "A chef preparing sushi in a traditional Japanese kitchen, steam rising, hands moving precisely, cinematic lighting, 4K",
    "negative_prompt": "blurry, low quality, distorted",
    "resolution": "1080p",
    "duration": 6,
    "aspect_ratio": "16:9",
    "seed": 12345
  }'
```

### 3.3 提示词技巧

**优质提示词结构**：
```
[主体] + [动作] + [场景] + [风格/氛围] + [技术参数]
```

**示例**：
```
# 优秀示例
A young woman running through a forest at sunrise, leaves floating in the air, golden hour lighting, cinematic, slow motion

# 一般示例
a girl running in forest
```

**PixVerse V6 擅长场景**：
- 人物运动（跑步、行走、舞蹈）
- 物体互动（手持物品、物体碰撞）
- 自然风景（流水、火焰、树叶）
- 日常生活场景

---

## 四、参数配置详解

### 4.1 推荐配置

| 场景 | 分辨率 | 时长 | 运动强度 | 种子 |
|------|--------|------|----------|------|
| 短视频/社交媒体 | 1080p | 4-6秒 | 高 | 随机 |
| 电影感/叙事 | 1080p | 6-10秒 | 中 | 指定 |
| 产品展示 | 1080p | 4秒 | 低 | 固定 |
| AI漫剧 | 720p | 3-4秒 | 中 | 固定 |

### 4.2 高级参数

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `seed` | 随机种子，相同种子可复现相似风格 | 指定数值 |
| `guidance_scale` | 提示词遵循度，越高越符合描述 | 7-12 |
| `motion_strength` | 运动强度 | 0.3-0.8 |
| `cfg` | 图像遵循度 | 7.5 |
| `num_frames` | 生成帧数 | 96-240 |

---

## 五、PixVerse V6 vs 其他工具选型

| 维度 | PixVerse V6 | SkyReels V4 | 可灵AI 3.0 | Grok Imagine |
|------|-----------|------------|-----------|--------------|
| **画质** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **物理真实感** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **人物一致性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **开口说话** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **中文支持** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **价格** | 适中 | 付费 | 8折优惠中 | 付费 |
| **最适合** | 物理场景、运动镜头 | 高端影视创作 | 国内用户首选 | 人物口播 |

---

## 六、实战案例：制作一条AI短视频

### 目标：制作一条15秒的产品展示视频

```
主题：智能手表产品展示
工具链：PixVerse V6（主视频）+ 剪映（剪辑）+ Mureka V9（背景音乐）
```

**步骤1：拆分镜头脚本**
```
镜头1（0-4秒）：特写智能手表屏幕，展示心率监测界面
镜头2（4-8秒）：模特佩戴手表的日常使用场景（走路）
镜头3（8-12秒）：手表充电的近景，低焦虑感
镜头4（12-15秒）：手表放在桌面上，背景虚化，logo展示
```

**步骤2：生成各镜头视频**

```bash
# 镜头1
curl -X POST "https://api.pixverse.ai/v1/generate" \
  -H "Authorization: Bearer $PIXVERSE_API_KEY" \
  -d '{
    "model": "pixverse-v6",
    "prompt": "Close-up of a smartwatch screen showing heart rate monitor, green waveform, modern UI design, shallow depth of field, product photography",
    "resolution": "1080p",
    "duration": 5
  }'

# 镜头2
curl -X POST "https://api.pixverse.ai/v1/generate" \
  -H "Authorization: Bearer $PIXVERSE_API_KEY" \
  -d '{
    "model": "pixverse-v6",
    "prompt": "Young woman wearing a smartwatch on her wrist, walking in city street, casual outfit, natural movement, golden hour",
    "resolution": "1080p",
    "duration": 5
  }'
```

**步骤3：导入剪映**
1. 导入4个视频片段
2. 按脚本顺序排列
3. 添加转场（ dissolve  dissolve dissolve）
4. 匹配背景音乐（Mureka V9 生成）
5. 导出 1080p 成品

---

## 七、常见问题

**Q1：视频生成失败怎么办？**
A：检查提示词是否包含违禁词；尝试降低运动强度；更换种子值。

**Q2：如何保持人物一致性？**
A：使用角色种子（Character Seed）功能，同一角色使用相同种子。

**Q3：生成速度慢？**
A：高峰时段服务器负载高，建议凌晨或非工作时间使用API批量生成。

**Q4：如何生成中文口型？**
A：中文口型建议配合 Grok Imagine 或可灵AI 3.0，PixVerse V6 更适合视觉场景。

---

## 八、资源链接

| 资源 | 链接 |
|------|------|
| 官网 | https://pixverse.ai |
| 文档 | https://docs.pixverse.ai |
| Discord社区 | PixVerse官方Discord |
| API控制台 | https://api.pixverse.ai |

---

> 🤖 本指南由「AI视频制作Agent」每周更新
> 下次更新：2026-04-10
