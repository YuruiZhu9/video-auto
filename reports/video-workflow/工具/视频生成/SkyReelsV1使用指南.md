# SkyReels V1 使用指南

> 来源：昆仑万维
> 更新：2026-04-05
> 类型：视频生成（开源 AI 短剧）
> 评级：⭐⭐⭐⭐⭐（必读）

---

## 核心定位

SkyReels V1 是**中国首个开源 AI 短剧视频生成模型**，由昆仑万维发布，专为 AI 短剧创作场景优化。

**同步开源**：表情动作可控算法 **SkyReels-A1** 也一并开源。

---

## 核心能力

| 能力 | 详情 |
|------|------|
| **开源许可** | 完全开源，Apache 2.0 / MIT（需确认官方许可）|
| **训练数据** | 千万级好莱坞级数据 |
| **AI短剧** | 专为 AI 短剧场景优化，剧情连贯性强 |
| **表情可控** | SkyReels-A1 支持表情独立控制 |
| **动作可控** | SkyReels-A1 支持动作强度调节 |
| **输入模态** | 文本 → 视频，图像 → 视频 |
| **输出时长** | 支持中长镜头（15秒 ~ 60秒）|
| **分辨率** | 720p / 1080p |

---

## SkyReels V1 vs SkyReels V4

| 维度 | SkyReels V1 🆕 | SkyReels V4 |
|------|---------------|------------|
| **发布状态** | 2026-04-05 全新发布 | 已发布（全球第一）|
| **开源** | ✅ 完全开源 | ❌ 付费API |
| **AI短剧优化** | ✅ 专门优化 | ✅ 有优化 |
| **表情动作控制** | ✅ SkyReels-A1 同步开源 | ✅ 有控制 |
| **适用场景** | AI短剧 / 独立创作 | 高质量商业视频 |
| **价格** | 免费 | ¥约300/月 |
| **推荐用法** | **日常/测试/免费创作** | **重点项目/商业项目** |

> 💡 **最佳策略**：SkyReels V1 用于日常练手和免费创作；SkyReels V4 用于商业付费项目。

---

## 快速上手

### 方法一：GitHub 开源项目（推荐本地部署）

```bash
# 克隆项目
git clone https://github.com/SkyworkAI/skyreels.git
cd skyreels

# 安装依赖
pip install -r requirements.txt

# 下载预训练权重（首次运行自动下载）
python download_weights.py --model skyreels-v1

# 文本 → 视频
python inference.py \
  --model skyreels-v1 \
  --prompt "一位年轻程序员在深夜办公室编程，城市灯火通明，电影感镜头" \
  --duration 30 \
  --resolution 1080p \
  --output "outputs/scene1.mp4"

# 图像 → 视频（图生视频）
python inference.py \
  --model skyreels-v1 \
  --image "inputs/avatar.png" \
  --prompt "角色微笑转身，光线从左侧照射" \
  --duration 15 \
  --resolution 1080p \
  --output "outputs/scene2.mp4"
```

### 方法二：官方 API（正式版上线后使用）

```python
import requests

response = requests.post(
    "https://api.skyreels.ai/v1/generate",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "skyreels-v1",
        "prompt": "古代将军在战场上指挥千军万马，电影感，4K",
        "duration": 30,
        "resolution": "1080p",
        "style": "cinematic"  # cinematic / anime / realistic
    }
)

result = response.json()
video_url = result["data"]["video_url"]
print(f"生成完成：{video_url}")
```

---

## SkyReels-A1 表情动作精细控制

SkyReels-A1 是同步开源的表情/动作可控算法，可在生成视频后精细调整：

```python
# SkyReels-A1 可控参数
params = {
    "model": "skyreels-a1",
    "video": "outputs/scene1.mp4",
    
    # 表情控制
    "expression": "happy",   # happy / sad / angry / surprised / fearful / neutral
    
    # 动作控制
    "motion": "working",     # walking / sitting / talking / gesturing / dancing
    
    # 强度（0.0 = 原始，1.0 = 最强）
    "intensity": 0.8,
    
    # 种子（固定可复现）
    "seed": 42
}

response = requests.post(
    "https://api.skyreels.ai/v1/control",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json=params
)
```

---

## 推荐配置

### 硬件要求

| 规格 | 最低要求 | 推荐配置 |
|------|---------|---------|
| GPU | 16GB VRAM | 24GB+ (A100 / RTX 4090) |
| 内存 | 32GB RAM | 64GB+ |
| 存储 | 50GB | 100GB+（模型权重较大）|
| CUDA | 11.8+ | 12.1+ |

### 生成参数推荐

| 场景 | Duration | Resolution | Motion Intensity | Style |
|------|---------|-----------|----------------|-------|
| **AI短剧** | 30-60s | 1080p | 0.6-0.8 | cinematic |
| **情感特写** | 15-30s | 1080p | 0.3-0.5 | realistic |
| **动作场景** | 15-30s | 1080p | 0.8-1.0 | cinematic |
| **快速预览** | 5-10s | 720p | 0.5-0.7 | any |

---

## 提示词技巧（SkyReels V1 专用）

### 基础公式

```
角色 + 场景 + 动作 + 镜头语言 + 风格 + 光线
```

### 优质提示词示例

```
# 情感类场景
"一位年轻程序员收到晋升通知，惊喜表情，办公室温暖灯光，电影近景，感人至深"

# 动作类场景
"古代武士在竹林中舞剑，剑光闪烁，竹叶飘落，慢镜头，武侠风格，顶级画质"

# 短剧开场
"深夜城市天际线，镜头缓缓推进，一扇亮灯的窗户，故事感十足，电影感，温暖色调"

# 多角色场景
"两个年轻人在咖啡馆里讨论创业计划，充满激情，背景虚化，文艺风格，自然光"
```

### 避免的写法

- ❌ 过于抽象的描述（如"最美的画面"）
- ❌ 过长过复杂的动作（分段生成效果更好）
- ❌ 冲突的光线描述（如"明亮的夜晚"）

---

## 在 AI 视频制作工作流中的位置

```
全流程定位：第四阶段（视频生成）· AI短剧专用首选
═══════════════════════════════════════════════════════════════

第一阶段：文案   → Kimi / GLM-4-Flash
第二阶段：配图    → Stable Diffusion / Midjourney V7
第三阶段：配音    → Kokoro-82M / ElevenLabs
第四阶段：视频    → ⭐ SkyReels V1（AI短剧专用）
第五阶段：剪辑    → 剪映专业版

AI短剧完整工作流：
脚本(Kimi)
  → 分镜图(Stable Diffusion)
    → 视频片段(SkyReels V1)
      → 表情精调(SkyReels-A1)
        → 配音(Kokoro-82M)
          → BGM(Mureka V9)
            → 剪辑(剪映)
              → 成片

═══════════════════════════════════════════════════════════════
```

---

## 常见问题

**Q：SkyReels V1 和 Runway Gen-4 哪个更好？**
A：两者定位不同。SkyReels V1 专为 AI 短剧优化，开源免费；Runway Gen-4 通用质量更强。**AI 短剧场景推荐 SkyReels V1**；**通用高质量场景推荐 Runway Gen-4**。

**Q：本地部署需要什么显卡？**
A：实测建议 24GB+ VRAM（RTX 4090 或 A100）。16GB 可跑但速度较慢。

**Q：SkyReels V1 可以商用吗？**
A：需查看官方开源许可文件。一般开源协议允许商用，但需确认是否要求署名。

**Q：表情动作控制的精度如何？**
A：SkyReels-A1 提供基础级别的表情/动作控制，适合短剧场景。精细影视级控制建议配合 HeyGen 等专业工具。

**Q：生成的视频有版权问题吗？**
A：昆仑万维声明使用好莱坞级训练数据，但具体版权合规情况需等待官方确认。商业项目建议配合 Seedance 2.0（全流程版权保障）。

---

## 相关工具推荐（短剧制作全家桶）

| 阶段 | 工具 | 用途 |
|------|------|------|
| 脚本 | Kimi | 长剧本（200万字上下文）|
| 分镜 | Gamma | PPT 分镜脚本 |
| 配图 | Stable Diffusion | 开源免费 |
| 配音 | Kokoro-82M | 开源免费 TTS |
| BGM | Mureka V9 | 中文歌曲最强 |
| 剪辑 | 剪映专业版 | 免费AI剪辑 |
| 字幕 | Whisper | 开源自动字幕 |

---

> **参考链接**：GitHub: SkyworkAI/skyreels（2026-04-05）
> **替代方案**：SkyReels V4（付费高端）/ Seedance 2.0（公测免费，全模态）
