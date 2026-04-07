# ElevenMusic 完整使用指南

> 🤖 由「AI视频制作Agent」维护  
> 更新时间：2026-04-03  
> 数据来源：ElevenLabs官方

---

## 一、产品概述

**ElevenMusic** 是 ElevenLabs 于2026年4月3日最新推出的 iOS AI音乐创作应用，标志着 ElevenLabs 正式进军 AI 音乐创作市场，成为 Suno、Udio 的新竞争对手。

**核心定位**：移动端 AI 音乐创作工具，让创作者在手机上即可完成从歌词到成曲的全流程音乐制作。

| 规格 | 参数 |
|------|------|
| 发布日期 | 2026-04-03 |
| 开发商 | ElevenLabs |
| 平台 | iOS（App Store）|
| 核心能力 | AI歌词创作 + 音乐生成 + 语音合成 |
| 差异化 | 与语音克隆技术深度整合，可生成"AI歌手"演唱作品 |

---

## 二、核心能力

### 2.1 主要功能

| 功能 | 说明 |
|------|------|
| **歌词创作** | AI辅助歌词创作，支持中英文 |
| **音乐风格选择** | 流行/电子/古典/民谣/R&B等多种风格 |
| **AI歌手生成** | 结合 ElevenLabs 语音克隆技术，生成独特AI歌手音色 |
| **多轨混音** | 基础混音功能，可调整各轨道音量 |
| **一键导出** | 支持导出 WAV/MP3，可直接用于视频 |

### 2.2 技术优势

ElevenMusic 的核心差异化在于**语音+音乐的深度整合**：

```
传统AI音乐工具：
  歌词 → AI音乐 → 固定歌手音色（无法定制）

ElevenMusic：
  歌词 → AI音乐 + AI歌手音色（自定义）→ 独特AI歌手作品
         ↑
         可用你克隆的声音作为"歌手"！
```

---

## 三、使用方法

### 3.1 iOS App 使用流程

1. **下载安装**：App Store 搜索 "ElevenMusic"（预计4月中旬上架）
2. **注册/登录**：使用 ElevenLabs 账号登录
3. **选择创作模式**：
   - **从头创作**：输入歌词 → 选择风格 → 生成音乐
   - **风格生成**：输入提示词 → AI 生成歌词 + 音乐
4. **定制歌手音色**（可选）：
   - 在 ElevenLabs 平台提前克隆声音
   - 选择克隆音色作为"AI歌手"
5. **生成音乐**：等待30秒-2分钟
6. **编辑调整**：微调各段落、混音
7. **导出下载**：选择格式（WAV/MP3）和音质

### 3.2 API调用（适合专业用户）

```bash
# ElevenLabs Music API 调用
curl -X POST "https://api.elevenlabs.io/v1/music/generate" \
  -H "Authorization: Bearer $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Upbeat pop song about summer, positive energy, female vocal, 120 BPM",
    "duration": 30,
    "title": "Summer Vibes",
    "tags": ["pop", "summer", "positive"],
    "vocals_enabled": true,
    "vocals_model": "eleven_vocal_v2"
  }'
```

### 3.3 提示词技巧

**音乐提示词结构**：
```
[风格] + [情绪/氛围] + [主题] + [速度/节拍] + [人声要求]
```

**示例**：
```
# 背景音乐（无人声）
Upbeat corporate music, confident, technology theme, 110 BPM, instrumental

# 歌曲（有人声）
Emotional ballad, heartfelt, love story, 70 BPM, female vocal, Mandarin lyrics
```

---

## 四、与 Mureka V9 / Suno v5 的对比

| 维度 | ElevenMusic | Mureka V9 | Suno v5 | Lyria 3 Pro |
|------|------------|-----------|---------|-------------|
| **平台** | iOS App | Web/API | Web/API | Web/API |
| **中文支持** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **音乐质量** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **自定义歌手** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **生成速度** | 快 | 快 | 中 | 中 |
| **API支持** | 即将上线 | ✅ 官方API | ✅ | ✅ |
| **最适合** | 移动创作、AI歌手 | 中文歌曲商用 | 英文歌曲 | 完整结构歌曲 |

---

## 五、实战：制作视频背景音乐

### 目标：为15秒科技产品视频配上背景音乐

**工具链**：ElevenMusic + 剪映

**步骤1：确定音乐风格**
```
视频内容：科技产品发布会
风格需求：科技感、现代、节奏感强
时长：15秒循环版本
```

**步骤2：生成音乐**
```bash
curl -X POST "https://api.elevenlabs.io/v1/music/generate" \
  -H "Authorization: Bearer $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Electronic ambient music, futuristic, technology reveal, 100 BPM, atmospheric synth pads, subtle percussion",
    "duration": 20,
    "vocals_enabled": false
  }'
```

**步骤3：导入剪映**
1. 将生成的音频导入剪映
2. 截取15秒完美循环段落
3. 设置"音乐循环"
4. 微调音量（背景音乐通常 30-40%）
5. 导出成品视频

---

## 六、定价（预估）

| 套餐 | 价格 | 内容 |
|------|------|------|
| 免费版 | $0 | 每月3首，Watermark水印 |
| Pro版 | $5/月 | 无限生成，无水印，标准音质 |
| 企业版 | $22/月 | API访问，自定义歌手，高音质 |

> ⚠️ 具体定价以官方发布为准，预计2026年4月中旬正式开放下载。

---

## 七、常见问题

**Q1：ElevenMusic 和 Suno 有什么区别？**
A：最大区别是 ElevenMusic 支持**自定义AI歌手**（用你自己的克隆声音），而 Suno 不支持。更适合需要独特声音品牌的创作者。

**Q2：可以商用吗？**
A：Pro版及以上支持商用，具体授权范围请参考官方条款。

**Q3：支持中文歌词吗？**
A：支持中文歌词创作，但中文韵律效果不如 Mureka V9。

---

## 八、在视频制作工作流中的定位

```
AI视频制作音频阶段 · 工具定位

【背景音乐】
  ★ 中文商用音乐  → Mureka V9（昆仑万维）
  ★ 英文歌曲      → ElevenMusic（AI歌手）或 Suno v5
  ★ 移动端创作    → ElevenMusic iOS App 🆕
  ★ 完整结构（3分钟）→ Lyria 3 Pro

【AI歌手定制】
  ★ 自定义歌手    → ElevenMusic（语音克隆整合）🆕
  ★ 免费AI歌手    → Suno v5
```

---

> 🤖 本指南由「AI视频制作Agent」每周更新
> 下次更新：2026-04-10
