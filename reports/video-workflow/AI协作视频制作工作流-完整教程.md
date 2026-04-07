# 🎬 AI协作视频制作工作流 — 完整教程

> 🤖 由 AI协作视频制作Agent 自动生成  
> 更新日期：2026-04-04  
> 模型库版本：2026-04 最新

---

## 📋 目录

1. [工作流全景图](#工作流全景图)
2. [第一阶段：文案生成](#第一阶段文案生成)
3. [第二阶段：视觉生成](#第二阶段视觉生成)
4. [第三阶段：音频生成](#第三阶段音频生成)
5. [第四阶段：视频合成](#第四阶段视频合成)
6. [完整实操示例](#完整实操示例)
7. [工具选型速查表](#工具选型速查表)

---

## 🔭 工作流全景图

```
┌──────────────────────────────────────────────────────────────┐
│                  AI协作视频制作完整工作流                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  📝 文案生成 ──→ 🎨 视觉生成 ──→ 🎵 音频生成 ──→ 🎬 视频合成  │
│      │              │              │              │          │
│      ▼              ▼              ▼              ▼          │
│  主题确定        PPT/动画        语音克隆        剪映       │
│  脚本撰写        配图生成        背景音乐        FFmpeg      │
│  字幕准备        分镜设计        音效合成        成片输出    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**推荐流水线：**
```
文案 + Gamma（PPT/分镜）
    → 配图（通义万相/可灵）
    → 语音克隆（ElevenLabs / Fish Audio）
    → 背景音乐（Mureka V8）
    → Seedance 2.0 / 可灵（文生视频/图生视频）
    → FFmpeg 合并音视频
    → 成片
```

---

## 第一阶段：文案生成

### 1.1 主题确定

**核心原则：**
- 主题清晰，一句话能说清楚
- 受众明确，内容有针对性
- 时长可控（1分钟视频 ≈ 150字旁白）

**常用主题方向：**
| 类型 | 示例 | 适合平台 |
|------|------|----------|
| 知识科普 | "AI如何改变推荐系统" | B站/知乎/小红书 |
| 产品介绍 | 新功能演示、使用教程 | 抖音/视频号 |
| 热点解读 | 大厂动态、技术新闻解读 | 微博/B站 |
| 情感故事 | 个人经历、观点输出 | 小红书/抖音 |
| 娱乐混剪 | 影视解说、盘点合集 | 各平台 |

### 1.2 脚本撰写

**标准脚本格式：**
```
【开场钩子】(0-5秒)
  "你知道吗？2026年，AI已经能做这件事了..."

【核心内容】(5-50秒)
  第1点：...
  第2点：...
  第3点：...

【结尾引导】(最后5秒)
  "如果你觉得有用，点赞+关注，我们下期见！"
```

**脚本撰写工具推荐：**
- **ChatGPT / Claude**：文案润色、扩写
- **秘塔写作猫**：中文语法优化
- **通义千问**：中文场景深度优化

### 1.3 字幕准备

**字幕格式规范：**
```
00:00 → 00:03  [开场字幕]
00:03 → 00:08  [正文第1句]
00:08 → 00:13  [正文第2句]
...
```

**工具：**
- **Whisper**（开源）：自动语音识别生成字幕
- **剪映**：自动识别字幕 + 一键导出SRT
- **Caption.io**：在线字幕编辑

---

## 第二阶段：视觉生成

### 2.1 PPT / 分镜生成

#### Gamma（⭐ 推荐 — AI驱动PPT）

**特点：** 输入文案 → 自动生成专业PPT，支持嵌入视频、图表

**使用方法：**
1. 访问 `gamma.app` 注册/登录
2. 点击 "Create with AI"
3. 输入视频主题/脚本
4. 选择模板（建议选 "Presentation"）
5. 自定义编辑后导出

**核心参数：**
| 参数 | 推荐值 |
|------|--------|
| 风格 | Corporate / Minimal |
| 配色 | 自动匹配主题色 |
| 每页字数 | ≤50字 |
| 总页数 | 8-15页（按视频时长）|

**技巧：**
- 每页只讲一个核心观点
- 使用 Gamma 的 "Analyze Data" 功能自动生成图表
- 导出时可选择16:9宽屏比例（适配横版视频）

---

#### 通义万相（阿里 — 国内首选）

**特点：** 文本/图像生成，支持中文场景优化，国内访问稳定

**API 调用示例（curl）：**
```bash
curl -X POST https://dashscope.console.aliyun.com/api/video_gen \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"model":"wanx2.1-t2i-turbo","prompt":"科技感PPT封面，蓝色渐变背景"}'
```

**适用场景：**
- 视频封面生成
- 分镜草图生成
- 背景图批量制作

---

#### 可灵 KLING 2.0（快手 — 视频+图像）

**特点：** 国内性价比最高，40%成本优势，支持图生视频

**核心功能：**
| 功能 | 说明 |
|------|------|
| 文生图 | 提示词→高质量图片 |
| 图生视频 | 图片→5秒视频片段 |
| 运动笔刷 | 控制图像局部运动 |

**适用：** 视频分镜动态预览、关键画面生成

---

#### Motion Go（Motion数组）

**特点：** PPT一键生成动画，适合知识类视频

**适用：** B站课程、科普视频的分镜动画快速生成

---

### 2.2 配图生成

| 工具 | 优势 | 适用场景 | 费用 |
|------|------|----------|------|
| **Midjourney** | 艺术感强、质量最高 | 电影感/艺术类视频 | 付费 |
| **DALL-E 3** | 与ChatGPT深度集成 | 快速原型 | 付费 |
| **Stable Diffusion** | 开源可商用、本地部署 | 批量生成 | 免费 |
| **通义万相** | 中文理解强、免费额度 | 国内项目 | 免费额度 |
| **可灵 KLING** | 图生视频一体化 | 分镜→视频无缝衔接 | 付费 |

**推荐工作流：**
```
文案描述 → 通义万相（草图）
    → Midjourney/SD（精修高清图）
    → 可灵（图生视频片段）
    → FFmpeg（拼接成完整视频）
```

---

## 第三阶段：音频生成

### 3.1 语音克隆 / TTS

| 工具 | 核心能力 | 推荐场景 | 费用 |
|------|----------|----------|------|
| **ElevenLabs** | 语音克隆、情感TTS、行业最优 | 商业配音、个人IP音色 | 付费（免费额度）|
| **Fish Audio** | 中文TTS开源方案、克隆免费 | 中文视频配音 | 免费 |
| **Fun-CineForge**（通义）| 影视级多场景配音 | 影视解说 | 部分免费 |
| **Grok语音API**（xAI）| 开口说话功能 | AI助手类视频 | xAI订阅 |
| **MiniMax TTS** | 全模态订阅含TTS | 综合创作 | 订阅制 |

**ElevenLabs 使用流程：**
1. 注册 `elevenlabs.io`
2. 上传5-30分钟音频训练音色
3. 使用 Voice Library 选择预设声音
4. API 调用：
```python
import requests
url = "https://api.elvenlabs.com/v1/text-to-speech/{voice_id}"
headers = {"xi-api-key": "YOUR_KEY"}
data = {
    "text": "你的视频旁白文本",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.3
    }
}
# 返回音频文件，导入剪映或FFmpeg合成
```

**Fish Audio（免费中文TTS）：**
```bash
# 克隆仓库
git clone https://github.com/fishaudio/fish-speech
cd fish-speech
# 使用预训练模型进行TTS
python -m fish_speech --text "你的旁白文案" --output result.wav
```

### 3.2 背景音乐生成

| 工具 | 核心能力 | 适用场景 | 费用 |
|------|----------|----------|------|
| **Mureka V8**（昆仑万维）| 全球AI音乐第一，中文韵律最优，API开放 | 中文视频BGM、商业配乐 | API付费 |
| **Lyria 3 Pro**（Google）| 3分钟完整结构歌曲（支持前奏/主歌/副歌/桥段）| 完整歌曲配乐 | Google订阅 |
| **Suno v5** | 全场景AI音乐生成，社区活跃 | 流行/电子/摇滚BGM | 付费 |
| **Udio** | 音乐生成质量高 | 电子/氛围音乐 | 付费 |
| **ElevenMusic**（ElevenLabs）| iOS移动端AI音乐创作 | 移动端创作 | App内购 |

**Mureka V8 API 调用示例：**
```python
import requests
url = "https://api.mureka.com/v1/music/generate"
headers = {"Authorization": "Bearer YOUR_KEY"}
data = {
    "prompt": "科技感背景音乐，轻盈电子风格，无人声，60秒循环",
    "duration": 60,
    "model": "mureka-v8",
    "lang": "zh"
}
response = requests.post(url, headers=headers, json=data)
music_url = response.json()["data"]["audio_url"]
```

**快速获取免费BGM方案：**
- **Pixabay Music**（免费版权音乐）
- **Freesound**（AI音效 + 环境音）
- **剪映素材库**（内置BGM，可商用）

### 3.3 音效合成

| 工具 | 说明 |
|------|------|
| **ElevenLabs SFX** | AI生成拟音、音效 |
| **Freesound** | 开源音效库，50万+音频 |
| **剪映音效库** | 内置常用音效（转场/环境音/搞笑音）|
| **Stable Audio**（Stability AI）| 开源AI音效/音乐生成 |

---

## 第四阶段：视频合成

### 4.1 剪映专业版（⭐ 推荐 — 入门首选）

**核心操作流程：**
```
1. 新建项目（16:9 或 9:16，按平台选择）
2. 导入素材：音频 + 图片/视频片段
3. 拖入时间轴，对齐字幕
4. 添加转场（叠化 / 闪黑 / 推动）
5. 添加字幕（自动识别 or 手动导入SRT）
6. 调整音量比例（BGM:30% / 人声:100%）
7. 导出（推荐MP4，1080P，H.264）
```

**AI增强功能：**
| 功能 | 位置 | 说明 |
|------|------|------|
| AI图生视频 | 剪同款 → AI玩法 | 图片→动态视频 |
| AI自动字幕 | 字幕 → 自动字幕 | 语音识别 |
| AI配音 | 音频 → 文字转语音 | 内置TTS |
| AI变声 | 音频 → 变声 | 音色变换 |
| AI商品图 | 图片 → AI变现 | 产品图生成 |

### 4.2 FFmpeg（⭐ 推荐 — 自动化批量合成）

**优势：** 支持命令行批量处理，适合定时任务和批量视频生成

**安装：**
```bash
# Linux/macOS
brew install ffmpeg

# 或使用 conda
conda install -c conda-forge ffmpeg
```

**常用命令速查：**

```bash
# 1. 图片序列 + 音频 → 视频（最常用）
ffmpeg -y \
  -framerate 1 \
  -pattern_type glob \
  -i 'images/*.jpg' \
  -i audio.wav \
  -c:v libx264 \
  -pix_fmt yuv420p \
  -shortest \
  output.mp4

# 2. 视频片段合并（拼接）
ffmpeg -y \
  -f concat \
  -safe 0 \
  -i filelist.txt \
  -c copy \
  merged.mp4

# filelist.txt 内容格式：
# file 'segment1.mp4'
# file 'segment2.mp4'
# file 'segment3.mp4'

# 3. 添加字幕（SRT格式）
ffmpeg -y \
  -i video.mp4 \
  -vf subtitles=subtitle.srt \
  output_with_subtitle.mp4

# 4. 音量标准化（避免BGM过大/过小）
ffmpeg -y \
  -i video_with_audio.mp4 \
  -af "volume=normalize=peak:level=0.8" \
  normalized.mp4

# 5. 添加片头片尾
ffmpeg -y \
  -i intro.mp4 \
  -i main_content.mp4 \
  -i outro.mp4 \
  -filter_complex "concat=n=3:v=1:a=1" \
  complete_video.mp4

# 6. 横版转竖版（加黑边方案）
ffmpeg -y \
  -i horizontal.mp4 \
  -vf "pad=ih*9/16:ih:(ow-iw)/2:0:black" \
  vertical_version.mp4

# 7. 压缩文件体积
ffmpeg -y \
  -i input.mp4 \
  -c:v libx264 \
  -crf 23 \
  -preset fast \
  compressed.mp4

# 8. 提取音频
ffmpeg -y \
  -i video.mp4 \
  -vn \
  -acodec libmp3lame \
  -q:a 2 \
  audio_only.mp3
```

**自动化脚本示例（Python）：**
```python
import subprocess
import os

def create_video_from_images(image_dir, audio_file, output, fps=1):
    """图片序列 + 音频 → 视频"""
    # 获取所有图片（按文件名排序）
    images = sorted([f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png'))])
    
    # 生成文件列表
    with open('filelist.txt', 'w') as f:
        for img in images:
            f.write(f"file '{os.path.join(image_dir, img)}'\n")
    
    # 视频合成
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0',
        '-i', 'filelist.txt',
        '-i', audio_file,
        '-vf', f'fps={fps},scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-shortest',
        output
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ 视频生成完成：{output}")

# 使用示例
create_video_from_images(
    image_dir='/workspace/video_project/images',
    audio_file='/workspace/video_project/voiceover.wav',
    output='/workspace/video_project/final_video.mp4',
    fps=0.5  # 每张图片停留2秒
)
```

### 4.3 其他工具

| 工具 | 优势 | 适用场景 |
|------|------|----------|
| **Canva Video** | 在线编辑、模板丰富 | 快速社交媒体视频 |
| **InVideo** | AI脚本生成 + 视频一体化 | 自动化视频生产 |
| **Runway Gen-4** | 工业级AI视频 + 剪辑 | 高端商业视频 |
| **Seedance 2.0 API** | 文本/图片直接生成高质量视频 | 自动化AI视频管线 |
| **可灵 KLING** | 图生视频 + 运动控制 | 分镜转视频 |

---

## 完整实操示例

### 案例：3分钟"AI推荐系统入门"科普视频

**目标：** B站/小红书科普视频，3分钟，竖版9:16

---

#### Step 1：文案生成
```
主题：AI推荐系统是什么？抖音/小红书为何总知道你喜欢什么？
时长：3分钟（约450字旁白）

脚本：
[0-10秒] 开场钩子
  "你有没有这种感觉——抖音刷着刷着，根本停不下来？
   你以为是巧合，其实是AI在偷偷操控你的大脑。"

[10-60秒] 什么是推荐系统
  "推荐系统，就是猜你喜欢什么的AI算法..."

[60-120秒] 三大核心原理
  "协同过滤、内容理解、深度学习..."

[120-180秒] 实际应用场景
  "抖音、淘宝、Spotify、Netflix..."

[180秒] 结尾
  "关注我，带你用代码理解AI。我们下期见！"
```

---

#### Step 2：视觉生成

**分镜PPT（Gamma）：**
1. 封面：深蓝渐变 + "AI推荐系统"大字标题
2. 第2页：抖音/淘宝推荐截图 + "你为什么停不下来？"
3. 第3页：三大原理图解
4. 第4页：应用场景展示
5. 第5页：关注引导 + Logo

**配图（通义万相 + 可灵）：**
- 每个分镜生成1-2张高清配图
- 关键画面用可灵转成动态视频片段（5秒）

---

#### Step 3：音频生成

**语音克隆（ElevenLabs）：**
- 上传自己录制的3分钟音频训练音色
- 或使用"Matthew"（英文）/ "Sarah"（英文）预设音色

**BGM（Mureka V8）：**
- Prompt：`科技感背景音乐，轻盈电子风格，无人声，180秒循环版`
- 或使用 Pixabay 免费BGM：`upbeat-tech-background`

---

#### Step 4：视频合成

**剪映操作流程：**
```
1. 新建项目（9:16竖版，1080P）
2. 导入分镜图片/视频片段，按顺序排列
3. 导入人声音频 + BGM，调整音量
4. 添加字幕（自动识别）
5. 添加转场（叠化，0.5秒）
6. 添加片尾：关注引导
7. 导出 MP4，1080P
```

**或 FFmpeg 自动化（适合批量生产）：**
```bash
# 图片序列（分镜截图）+ 语音 + BGM → 成片
ffmpeg -y \
  -framerate 1 \
  -pattern_type glob -i 'slides/*.png' \
  -i voiceover.wav \
  -i background_music.mp3 \
  -filter_complex "
    [0:v]fps=1,scale=1080:1920:force_original_aspect_ratio=decrease,
           pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black[v];
    [1:a]volume=1.0[voice];
    [2:a]volume=0.3[bgm];
    [voice][bgm]amix=inputs=2:duration=longest[a];
    [v][a]concat=n=1:v=1:a=1[out]
  " \
  -map "[out]" \
  -c:v libx264 -pix_fmt yuv420p \
  -shortest \
  ai_recommendation_system.mp4
```

---

## 工具选型速查表

### 🎬 视频生成

| 需求 | 首选 | 备选 |
|------|------|------|
| 高质量AI视频 | Seedance 2.0 / Runway Gen-4 | 可灵 KLING 2.0 |
| 性价比/国内 | 可灵 KLING 2.0（40%成本优势）| Veo 3.1 Lite |
| Sora替代（开口说话）| Grok Imagine | Grok语音API |
| 开源可商用 | Seedance 2.0 API / WAN 2.5 | Stable Video |
| 极速生成 | Pika 2.5 | PixVerse V6 |

### 🎵 音频 / 音乐

| 需求 | 首选 | 备选 |
|------|------|------|
| AI音乐全球第一 | Mureka V8（昆仑万维）| Lyria 3 Pro |
| 中文歌曲/BGM | Mureka V8 | Suno v5 |
| 语音克隆/TTS | ElevenLabs | Fish Audio |
| 影视配音 | Fun-CineForge（通义）| ElevenLabs |
| 免费TTS | Fish Audio | MiniMax TTS |
| 音画同步修复 | PrismAudio（通义）| 手动对齐 |

### 🎨 PPT / 视觉

| 需求 | 首选 | 备选 |
|------|------|------|
| AI驱动PPT | Gamma | Beautiful.ai |
| 中文AI绘图 | 通义万相 | 可灵 KLING |
| 高质量配图 | Midjourney | Stable Diffusion |
| 分镜→视频 | 可灵 KLING | Runway |

### ✂️ 视频剪辑

| 需求 | 首选 | 备选 |
|------|------|------|
| 入门友好 | 剪映专业版 | Canva Video |
| 批量自动化 | FFmpeg | InVideo |
| 工业级AI剪辑 | Runway | Seedance 2.0 |

---

## 📁 相关文件索引

| 文件 | 说明 |
|------|------|
| `工具/PPT生成/Gamma.md` | Gamma详细使用教程 |
| `工具/音频/语音克隆集成.md` | ElevenLabs + Fish Audio 集成方案 |
| `工具/音频/背景音乐.md` | Mureka/Suno 音乐生成教程 |
| `工具/视频剪辑/FFmpeg.md` | FFmpeg命令速查手册 |
| `工作流/各阶段配置.md` | 各工具参数配置推荐 |

---

> 🤖 本文档由 AI协作视频制作Agent 自动生成  
> 模型库更新时间：2026-04-04  
> 如有工具更新，请查阅 `/workspace/agents/model-library/` 分类文件
