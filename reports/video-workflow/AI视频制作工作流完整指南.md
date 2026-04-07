# AI协作视频制作工作流 — 完整指南（2026年4月版）

> 本指南由 AI协作视频制作Agent 自动生成
> 更新日期：2026-04-06
> 数据来源：跨Agent新技术同步中心模型库

---

## 一、工作流总览

```
┌──────────────────────────────────────────────────────────────┐
│                   AI视频制作全流程                            │
│                                                              │
│  文案生成  →  视觉生成  →  音频生成  →  视频合成  →  成品输出   │
│                                                              │
│  脚本撰写     PPT/配图     语音克隆     剪映/FFmpeg    导出发布  │
│  字幕准备     图像生成     背景音乐     字幕合成                │
│              分镜设计     音效合成     封面制作                │
└──────────────────────────────────────────────────────────────┘
```

### 核心工具链（2026年4月最新）

| 阶段 | 推荐工具 | 替代方案 | 备注 |
|------|---------|---------|------|
| 视频生成 | **Wan2.7-Video**（阿里通义）| Seedance 2.0 / PixVerse V6 | 最新全模态输入，2026-04-05更新 |
| 视频生成（免费API）| **Hypereal AI** | — | Sora2/Kling/WAN统一入口，35积分 |
| 音乐生成 | **Mureka V8**（昆仑万维）| Lyria 3 Pro / Suno v5 | 全球AI音乐第一，中文最优 |
| 语音克隆/TTS | **MAI-Voice-1**（微软）| ElevenLabs / Fish Audio | 1秒生成60秒，2026-04-04更新 |
| 语音识别/字幕 | **MAI-Transcribe-1**（微软）| Whisper / Cohere Transcribe | 25语言，词错率3.8% |
| PPT生成 | **Gamma** / **Motion Go** | Beautiful.ai / AiPPT | AI驱动演示文稿 |
| 图像生成 | **Midjourney** / **DALL-E** | Stable Diffusion / 通义万相 | 分镜/配图 |
| 视频剪辑 | **剪映专业版** | FFmpeg / Canva / InVideo | 自动化合成 |

---

## 二、第一阶段：文案生成

### 2.1 脚本撰写流程

**Step 1：确定视频主题**
- 明确目标受众（职场/学生/大众）
- 确定视频时长（15秒/60秒/3分钟/更长）
- 选择视频类型（种草/科普/故事/产品介绍）

**Step 2：结构化脚本模板**

```markdown
【开场钩子】（0-3秒）
- 抛出痛点或惊人数据
- 例："你知道吗？90%的人都在用错误的方式..."

【主体内容】（X-Y秒）
- 分3-5个要点展开
- 每个要点：观点 + 案例/数据 + 金句

【结尾引导】（最后5秒）
- 总结核心信息
- 行动号召（点赞/关注/评论区）
```

### 2.2 台词/字幕准备
- 使用 **MAI-Transcribe-1** 将语音转写为字幕SRT文件
- 导出格式：`{序号}\n{开始时间} --> {结束时间}\n{台词内容}\n`
- 推荐工具：SubtitleEdit（免费本地工具）

---

## 三、第二阶段：视觉生成

### 3.1 PPT生成

#### Gamma（推荐 ⭐⭐⭐⭐⭐）
- **官网**：gamma.app
- **核心能力**：输入主题，自动生成完整PPT，支持AI实时编辑
- **免费额度**：每月400积分（约10次生成）
- **操作流程**：
  1. 输入视频主题或粘贴文案
  2. 选择模板风格（商务/科技/活泼）
  3. AI生成PPT，可逐页调整
  4. 导出为PPTX或PDF
- **技巧**：
  - 输入更详细的Prompt，生成质量更高
  - 使用"Brand Kit"功能统一风格
  - 配合Figma做进一步视觉定制

#### Motion Go（推荐 ⭐⭐⭐⭐）
- **官网**：motiongo.yidianzhibo.com
- **核心能力**：PPT动画生成，让静态PPT动起来
- **适用场景**：需要动画效果的演示视频
- **操作流程**：
  1. 在PPT中安装Motion Go插件
  2. 选择页面动画模板（入场/强调/退出）
  3. 一键生成动画
  4. 导出视频

#### Beautiful.ai / AiPPT
- **Beautiful.ai**：国外AI PPT，模板质量高，适合国际化内容
- **AiPPT**：国内工具，中文支持更好

### 3.2 配图生成

#### Midjourney（推荐 ⭐⭐⭐⭐⭐）
- **核心能力**：高质量图像生成，风格多样
- **订阅**：$10/月起（Standard plan）
- **常用命令**：
  ```
  /imagine prompt: [主体描述], [风格], [光影], [比例]
  /describe [图片] → 反推提示词
  /blend [图1] [图2] → 图片融合
  ```
- **视频分镜技巧**：
  - 统一使用 `--seed` 参数保证风格一致
  - 使用 `--cref`（角色参考）保持人物一致性
  - 比例建议 `--ar 16:9`（横版）或 `--ar 9:16`（竖版）

#### DALL-E（OpenAI）
- **核心能力**：与ChatGPT集成，操作便捷
- **优势**：GPT-4理解能力强，Prompt优化更智能
- **适用场景**：快速生成简单配图

#### Stable Diffusion（免费开源）
- **部署方式**：本地部署（需要GPU）或云端（如 RunDiffusion）
- **优势**：完全免费，可自定义模型
- **推荐模型**：
  - Realistic Vision（写实风格）
  - Animagine XL 3.1（动漫风格）
  - Juggernaut XL（通用）

### 3.3 视频生成（核心工具）

#### Wan2.7-Video（阿里通义）⭐最新推荐⭐
- **更新**：2026-04-05
- **核心能力**：
  - 全模态输入（文本/图像/视频/音频）
  - 精准控制视频元素（删除路人、替换物体）
  - 与Wan2.7-Image形成完整图文视频矩阵
- **适用场景**：AI漫剧、短视频、内容编辑
- **API接入**：
  ```python
  # 阿里云百炼平台 API 调用示例
  import requests
  
  response = requests.post(
      "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2video/video-synthesis",
      headers={"Authorization": f"Bearer {API_KEY}"},
      json={
          "model": "wanx2.7-video",
          "input": {
              "prompt": "古风少女在竹林中起舞，白色长裙飘逸",
              "aspect_ratio": "16:9"
          }
      }
  )
  ```

#### Seedance 2.0（豆包）⭐公测中⭐
- **更新**：2026-04-04
- **核心能力**：
  - 文本/图像/音频/视频多输入
  - 登顶 Artificial Analysis 全球视频AI排行榜
  - 推理效率较1.0提升60%
  - **2.0 API正式公测**，企业可申请
- **官网**：seedance.byteunit.com

#### SkyReels V1（昆仑万维）⭐国产首发⭐
- **更新**：2026-04-05
- **核心能力**：
  - 中国首个开源AI短剧视频生成模型
  - 千万级好莱坞数据训练
  - 表情动作可控算法 SkyReels-A1（同步开源）
- **开源地址**：GitHub（昆仑万维官方）
- **适用场景**：AI短剧、AI影视内容生产

#### Veo 3.1 Lite（Google）
- **更新**：2026-04-01
- **核心能力**：视频生成成本降低50%+，720p仅$0.05/秒
- **性价比**：当前最低成本的工业级视频生成
- **适用场景**：创作者大规模使用

#### PixVerse V6
- **更新**：2026-04-02
- **核心能力**：AI视频空间/时间处理能力大增
- **替代Sora**成为视频生成新选择
- **免费额度**：每天若干免费生成

### 3.4 视频生成工具选型速查

| 需求 | 推荐 | 理由 |
|------|------|------|
| 最高画质工业级 | Runway Gen-4 | 成熟生态，专业用户多 |
| 性价比首选 | **Veo 3.1 Lite** | 720p仅$0.05/秒 |
| 最新全模态 | **Wan2.7-Video** | 文本+图像+视频+音频全输入 |
| 国产开源 | **SkyReels V1** | 中国首个开源AI短剧模型 |
| Sora替代（说话）| Grok Imagine（xAI）| 支持开口说话 |
| 免费API | Hypereal AI | 35积分覆盖多种模型 |

---

## 四、第三阶段：音频生成

### 4.1 语音克隆 / TTS

#### MAI-Voice-1（微软）⭐最新推荐⭐
- **更新**：2026-04-04
- **核心能力**：
  - 1秒音频输入 → 60秒自然语音输出
  - 支持数秒音频克隆
  - 与 MAI-Transcribe-1 形成完整语音矩阵
- **适用场景**：虚拟主播、语音克隆、AI配音

#### ElevenLabs（行业标准）
- **核心能力**：最成熟的语音克隆平台
- **免费额度**：每月10000字符
- **声音市场**：可直接购买已克隆声音
- **API示例**：
  ```python
  import elevenlabs
  
  audio = elevenlabs.generate(
      text="你好，欢迎观看本期内容",
      voice="Professional/Chinese",
      model="eleven_v2"
  )
  elevenlabs.play(audio)
  ```

#### Fish Audio（免费开源）
- **核心能力**：开源语音克隆，支持中文
- **部署方式**：本地部署或使用官方API
- **优势**：完全免费，中文效果好

### 4.2 背景音乐生成

#### Mureka V8（昆仑万维）⭐全球第一⭐
- **更新**：2026-03-26
- **核心能力**：
  - MusiCoT音乐思维链技术
  - Artificial Analysis 人声+器乐双榜全球第一
  - 碾压 Suno V4.5 / Udio / Lyria 2
  - 中文旋律与歌词韵律贴合度行业领先
  - 全球8000+客户，官方API开放
- **适用场景**：商业配乐、中文歌曲、AI短剧BGM
- **API接入**：昆仑万维开放平台

#### Lyria 3 Pro（Google DeepMind）
- **更新**：2026-03-26
- **核心能力**：
  - 音乐生成时长从30秒提升至3分钟
  - 新增"结构感知"能力（前奏/主歌/副歌/桥段/尾奏）
  - 完整结构歌曲生成
- **适用场景**：完整歌曲、商业配乐

#### Suno v5 / Udio
- **Suno**：AI音乐老牌平台，社区活跃
- **Udio**：音乐生成，操作简单
- **注意**：中文支持不如 Mureka V8

### 4.3 音效生成
- **ElevenLabs 音效API**：可生成特定场景音效
- **免费工具**：Freesound.org（版权音效库）
- **推荐策略**：先用AI生成，版权库兜底

---

## 五、第四阶段：视频合成

### 5.1 剪映专业版（推荐 ⭐⭐⭐⭐⭐）
- **平台**：Windows / Mac / iOS / Android
- **核心功能**：
  - AI图生视频（将PPT/配图转视频）
  - AI文案成片（输入文案自动生成视频）
  - 字幕自动识别
  - 音色克隆
  - 智能剪辑（自动踩点）
- **AI协作工作流**：
  1. 导入AI生成的视频片段
  2. 拖入时间线，按脚本顺序排列
  3. 使用"AI图生视频"处理PPT图片
  4. 导入克隆语音，替换原声
  5. 启用"自动字幕"（配合MAI-Transcribe-1精度更高）
  6. 添加背景音乐（来自Mureka V8）
  7. 一键导出

### 5.2 FFmpeg（自动化合成）
- **适用场景**：批量处理、自动化流水线
- **核心命令**：
  ```bash
  # 视频拼接
  ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
  
  # 添加音频
  ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4
  
  # 添加字幕
  ffmpeg -i video.mp4 -vf subtitles=subtitle.srt output.mp4
  
  # 调整分辨率和码率
  ffmpeg -i video.mp4 -vf "scale=1920:1080" -b:v 5000k output.mp4
  
  # 批量裁剪
  ffmpeg -i input.mp4 -ss 00:00:05 -t 00:00:10 -c copy clip.mp4
  ```

### 5.3 音画同步（PrismAudio）
- **工具**：PrismAudio（阿里通义实验室）
- **能力**：解决AI视频音画不同步问题，ICLR 2026收录
- **适用场景**：大量AI生成视频的后处理

---

## 六、完整工作流示例

### 示例一：知识科普类短视频（60秒）

```
Day 1（30分钟）
├── 用 Gamma 生成PPT框架（主题：AI辅助编程）
├── 用 Midjourney 生成5张分镜配图（16:9，统一风格）
└── 用 MAI-Transcribe-1 转写配音脚本

Day 2（20分钟）
├── 用 ElevenLabs 生成配音音频
├── 用 Mureka V8 生成30秒背景音乐
└── 用 PrismAudio 校准音画同步

Day 3（30分钟）
├── 打开剪映专业版
├── 导入5张配图，使用"AI图生视频"各生成5秒片段
├── 按脚本顺序排列片段，添加配音
├── 叠加背景音乐，调整音量比例（语音80%/音乐20%）
├── 自动字幕生成，导出1080P视频
└── 发布至抖音/B站
```

### 示例二：AI漫剧（3分钟）

```
前期（2小时）
├── 用 Wan2.7-Video 生成核心场景视频片段
├── 用 Seedance 2.0 生成角色动作特写
├── 用 PixVerse V6 生成过渡转场
└── 用 FFmpeg 批量拼接片段

中期（1小时）
├── 用 MAI-Voice-1 克隆角色音色
├── 用 Fun-CineForge（阿里通义）生成多角色对话配音
└── 用 Mureka V8 生成情绪化背景音乐

后期（1小时）
├── 剪映专业版合成：视频+配音+BGM+字幕
├── 用 PrismAudio 校准音画同步
└── 导出发布
```

---

## 七、免费资源汇总

| 工具 | 免费额度 | 获取方式 |
|------|---------|---------|
| **Hypereal AI** | 35积分/注册 | hypereal.ai → API Keys |
| **Veo 3.1 Lite** | 部分免费 | Google AI Studio |
| **MAI-Transcribe-1** | 商用付费 | 微软Azure |
| **MAI-Voice-1** | 商用付费 | 微软Azure |
| **Seedance 2.0** | 公测申请 | 豆包官网 |
| **Mureka V8** | API付费 | 昆仑万维开放平台 |
| **ElevenLabs** | 10000字/月 | elevenlabs.ai |
| **Fish Audio** | 免费开源 | fish.audio |
| **SkyReels-A1** | 开源免费 | GitHub |
| **Cohere Transcribe** | Apache 2.0 | GitHub |
| **Whisper** | 开源免费 | GitHub |

---

## 八、工具参数推荐配置

### 视频生成推荐参数
```yaml
Wan2.7-Video:
  aspect_ratio: "16:9"      # 16:9横版 / 9:16竖版
  resolution: 1080p
  duration: 6-10秒/片段
  guidance_scale: 7.5       # 越高越遵循prompt

Seedance 2.0:
  duration: 5-10秒
  resolution: 1080P
  api_status: "公测中"       # 申请: seedance.byteunit.com

PixVerse V6:
  motion_strength: 高      # 高/中/低
  negative_prompt: "模糊, 变形, 低质量"
```

### TTS推荐参数
```yaml
MAI-Voice-1:
  stability: 0.5           # 0-1，越高越稳定
  similarity: 0.8           # 0-1，越高越像原声
  style: "conversational"  # conversational / formal / dramatic

ElevenLabs:
  model: "eleven_v2"
  voice_settings:
    stability: 0.5
    similarity_boost: 0.75
    style: 0.3
    use_speaker_boost: true
```

### 音乐生成推荐参数
```yaml
Mureka V8:
  duration: 30秒            # 可选30秒/完整歌曲
  genre: "ambient/cinematic"
  mood: "peaceful"
  instrumental: true        # true=纯音乐 / false=带人声

Lyria 3 Pro:
  duration: 3分钟           # 最大3分钟，完整结构
  structure: "intro-verse-chorus-bridge-outro"
```

---

## 九、技巧与常见问题

### Q1：视频生成角色不一致怎么办？
**A**：使用图像参考功能（Wan2.7-Video支持），先用Midjourney生成角色正面照作为种子图，后续所有片段使用该图作为角色参考。

### Q2：AI配音听起来太假？
**A**：
1. 在TTS后加入微小的背景噪音（5%音量）
2. 适当加入自然停顿（句间0.3秒）
3. 使用 ElevenLabs 的 voice isolation 功能

### Q3：音画不同步怎么解决？
**A**：使用 **PrismAudio**（阿里通义，ICLR 2026）自动校准音画同步，或手动在剪映中微调。

### Q4：视频太长/文件太大？
**A**：
```bash
# FFmpeg 压缩
ffmpeg -i input.mp4 -vcodec h264 -acodec aac -b:v 3000k output.mp4
```

### Q5：如何批量生成相似风格视频？
**A**：
1. 制作视频模板（固定片头/片尾）
2. 用 FFmpeg 的 concat 分离主体内容
3. 调用视频生成API批量生产内容片段
4. FFmpeg 批量拼接 + 自动化脚本

---

## 十、文档目录

```
video-workflow/
├── AI视频制作工作流完整指南.md（本文件）
├── 工作流/
│   ├── 全流程示例.md
│   └── 各阶段配置.md（工具参数配置）
├── 工具/
│   ├── PPT生成/
│   │   ├── Gamma使用指南.md
│   │   └── MotionGo使用指南.md
│   ├── 视频生成/
│   │   ├── Wan2.7-Video使用指南.md
│   │   ├── Seedance2.0使用指南.md
│   │   └── SkyReels使用指南.md
│   ├── 音频/
│   │   ├── MAI-Voice-1使用指南.md
│   │   ├── MurekaV8使用指南.md
│   │   └── 语音克隆集成方案.md
│   └── 视频剪辑/
│       ├── 剪映专业版工作流.md
│       └── FFmpeg常用命令速查.md
└── 技巧总结/
    └── 常见问题解决方案.md
```

---

> 📌 本指南将随模型库持续更新，关注 `/workspace/agents/model-library/` 获取最新工具动态
> 🤖 由 AI协作视频制作Agent 自动维护
