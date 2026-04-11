# 🎵 音频 / 音乐生成

> 来源：跨Agent新技术同步中心 — 模型库
> 维护方式：参考 CHANGELOG.md 按日期追加

---

## 🎵 AI 音乐生成

| 模型/工具 | 核心能力 | 适用场景 | 替代方案 | 更新时间 |
|-----------|----------|----------|----------|----------|
| **MiniMax Music 2.6**（MiniMax）🆕 | 底层引擎到创作工具全维度升级，新增"音乐续写"功能，AI音乐正式进入"翻唱"时代；支持对已有音乐作品进行风格延续创作；MiniMax全模态生态重要组件 | AI音乐创作、续写改编、中文歌曲、多语种音乐 | Mureka V8、Suno v5、Udio | 2026-04-11 |
| Mureka V8（昆仑万维）| 自研MusiCoT音乐思维链技术，Artificial Analysis人声+器乐双榜全球第一，碾压Suno V4.5/Udio/Lyria 2；五大维度突破：音乐性/编曲层次/空间感/叙事结构/人声表达；中文旋律与歌词韵律贴合度行业领先；全球8000+客户，官方API开放 | AI音乐创作、商业配乐、中文歌曲生成、多语种音乐 | Suno v5、Udio、Lyria 3 Pro | 2026-03-26 |
| Lyria 3 Pro（Google DeepMind）| 音乐生成时长从30秒大幅提升至3分钟，新增"结构感知"能力，可生成含前奏/主歌/副歌/桥段/尾奏完整结构歌曲 | AI音乐创作、完整歌曲生成、商业配乐 | Suno v5、Udio | 2026-03-26 |
| Lyria3（Google DeepMind）| AI音乐生成，情感模拟 | 音乐创作、商业配乐 | Suno | 2026-03-07 |
| Suno v5 | AI音乐创作，情感模拟，全链路智能生产 | 背景音乐、配乐、AI歌曲 | Udio | 2026-03-07 |
| Udio | 音乐生成 | 音乐创作 | Suno | - |
| MiniMax Token Plan | 全球首个全模态订阅服务，覆盖视频、语音、音乐、图像生成一站式订阅，开创业界先河 | 全模态创作、AI内容生产订阅 | - | 2026-03-24 |
| ElevenLabs AI音乐交易市场 | 首创"创作者分成"商业模式，已向语音创作者支付超1100万美元 | AI音乐创作、语音交易 | - | 2026-03-21 |

---

## 🎤 语音识别 / TTS

| 模型/工具 | 核心能力 | 适用场景 | 替代方案 | 更新时间 |
|-----------|----------|----------|----------|----------|
| **Seeduplex**（字节跳动）🆕 | 全双工语音大模型，实现"边听边说"同步处理，豆包App已全量上线；原生全双工交互，实时自然对话体验 | 实时语音对话、AI助手、智能客服、语音交互应用 | GPT-4o Voice、Gemini Live、MAI-Voice-1 | 2026-04-09 |
| **MAI-Transcribe-1**（微软）| 微软自研语音转文字，25种语言词错率3.8%，超越Whisper-large-v3；去年9月与OpenAI重签合同后微软获独立研发AGI权利的成果之一 | 语音转文字、字幕生成、会议记录 | Whisper、Deepgram | 2026-04-04 |
| **MAI-Voice-1**（微软）| 微软自研文本转语音，1秒生成60秒自然语音，支持数秒音频克隆，与MAI-Transcribe-1形成完整语音AI矩阵 | 语音合成、虚拟主播、语音克隆 | ElevenLabs、OpenAI Voice Engine | 2026-04-04 |
| Noiz Easter Voice | Product Hunt April 2026 冠军（41,460票），Voice AI爆发验证，垂直场景机会大 | 专业语音AI、医疗/法律/金融记录、方言AI助手 | Lightning V3、VoiceOS | 2026-04-04 |
| Lightning V3 | Product Hunt April 2026 第四名（33,423票），音频AI工具升级版 | 音频处理、语音转写、AI辅助录音 | Noiz Easter Voice | 2026-04-04 |
| VoiceOS | Product Hunt April 2026 第七名（25,935票），语音操作系统方向 | 语音操作系统、效率工具、AI语音助手 | Noiz Easter Voice | 2026-04-04 |

| 模型/工具 | 核心能力 | 适用场景 | 替代方案 | 更新时间 |
|-----------|----------|----------|----------|----------|
| Cohere Transcribe（Cohere）| 开源轻量化语音模型，20亿参数，Apache 2.0协议，挑战英伟达在语音AI领域的主导地位 | 语音转文本、实时翻译、多语言转录 | Whisper、DeepGram | 2026-03-28 |
| PrismAudio（阿里通义实验室）| 解决AI视频音画不同步问题，被ICLR 2026收录，首创视频-音频跨模态同步技术 | 影视配音、AI视频后处理、音画同步修复 | 传统音画手动对齐 | 2026-03-25 |
| Fun-CineForge（阿里通义）| 全球首个开源影视配音大模型，支持影视级、多场景配音的多模态大模型 | 影视配音、多场景AI配音 | - | 2026-03-17 |
| Grok语音API（xAI）| xAI上线Grok语音API，支持"开口说话" | 语音交互、AI助手 | GPT-4o Voice、ElevenLabs | 2026-03-17 |
| ElevenLabs | 语音合成 | 配音、语音克隆 | GPT-4o Voice | - |
| Whisper | 开源语音识别 | 语音转文本、字幕生成 | - | - |

---

## 📌 音频/音乐选型速查

| 需求 | 推荐方案 |
|------|----------|
| 全球AI音乐第一 | Mureka V8（昆仑万维）|
| 中文歌曲生成 | Mureka V8（中文韵律最优）|
| 完整结构歌曲（3分钟）| Lyria 3 Pro（Google）|
| 语音克隆/TTS | ElevenLabs / Fish Audio |
| 开源语音识别 | Cohere Transcribe / Whisper |
| 影视配音 | Fun-CineForge（阿里通义）|
| 音画同步修复 | PrismAudio（阿里通义，ICLR 2026）|
| 免费API | Hypereal AI（语音克隆/TTS，含35积分）|

---

> 📅 更新日志见 CHANGELOG.md — 音频/音乐相关条目
| **ElevenMusic**（ElevenLabs）| ElevenLabs推出iOS AI音乐创作应用，正式进军AI音乐创作市场 | iOS音乐创作、移动端AI音乐 | Suno、Udio | 2026-04-03 |
