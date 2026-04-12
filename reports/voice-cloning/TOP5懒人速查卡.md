# 免费语音克隆 TOP5 懒人速查卡（2026-04-11更新）

## 🥇 CosyVoice 3.0 — 中文首选
```
pip install cosyvoice

from cosyvoice import CosyVoice
model = CosyVoice()
result = model.clone_and_synthesize(
    ref_audio="sample.wav",  # 3秒即可
    text="欢迎收听",
    instruct="用温柔的女声，播新闻的感觉"
)
```
- ✅ 中文CER 0.71全场最低
- ✅ 18种中文方言
- ✅ 自然语言情感控制
- ⚠️ Apache-2.0许可
- ⚠️ **已知 Bug**：CosyVoice 3.0 部分 prompt 内容会混入输出音频（疑似分词问题）
- ⚠️ **建议**：对中文克隆质量要求高的场景，回退使用 **CosyVoice 2.0**

---

## 🥇 Qwen3-TTS — 极速克隆
```
pip install qwen-tts

from qwen_tts import QwenTTS
tts = QwenTTS()
audio = tts.synthesize(
    "你好世界",
    voice=tts.clone_voice("sample.wav")  # 3秒克隆
)
```
- ✅ 97ms超低延迟
- ✅ 英文WER 1.24全场最低
- ✅ 9种预设音色（CustomVoice）
- ⚠️ 1.7B需12GB显存

---

## 🥈 F5-TTS — 最快推理
```
pip install f5-tts

from f5_tts import F5TTS
model = F5TTS()
audio = model.generate(text="你好", lang="zh")
```
- ✅ RTF=0.15 业界最快
- ✅ **MIT许可可商用**
- ⚠️ 中英双语（非多语言）
- ⚠️ 长文本偶发"核嗓"

---

## 🥉 ChatTTS v2 — 对话场景
```
import ChatTTS
chat = ChatTTS.Chat()
chat.load()
audio = chat.speak("[laugh]你好啊，[uv_break]好久不见！")
```
- ✅ 笑声/停顿/情绪精细控制
- ✅ 对话场景自然
- ⚠️ 情感控制需参考音频微调

---

## 🆕 VoxCPM2 — 方言发烧友首选（2026-04-12 更新：Stars 9.9k）
```
pip install voxcpm

from voxcpm import VoxCPM
model = VoxCPM.from_pretrained("openbmb/VoxCPM2")
audio = model.generate(
    text="今天天气好巴适哦！",
    dialect="Sichuan"  # 四川话
)
```
- ✅ **9种中国方言**（四川/粤语/吴语/东北/河南/陕西/山东/天津/闽南）
- ✅ 48kHz CD音质（全场最高之一）
- ✅ Tokenizer-Free 架构（无量化误差）
- ✅ Apache 2.0 许可（可商用）
- ✅ 终极克隆（高保真重放，保留全部情感细节）
- ⚠️ 2B参数，推荐 RTX 4090+

---

## 🥉 GPT-SoVITS v4 — 少样本定制
```
# 整合包：https://github.com/RVC-Boss/GPT-SoVITS/releases
# 双击 go-web.bat 启动WebUI
```
- ✅ 1分钟数据即可克隆
- ✅ 高相似度个性化
- ✅ MIT许可
- ⚠️ 需要训练（非即时克隆）

---

## RVC V3 — 实时变声
```
python infer-web.py
# WebUI: 上传音频 → 训练10分钟 → 实时变声
```
- ✅ 170ms低延迟
- ✅ RMVPE音高提取
- ✅ MIT许可
- ⚠️ 需训练（10分钟数据）

---

## 选型速查

| 需求 | 方案 | 关键优势 |
|------|------|---------|
| 中文质量最高 | CosyVoice3 RL | CER 0.71 |
| 极速3秒克隆 | Qwen3-TTS | 97ms |
| 商用免费 | F5-TTS / RVC | MIT许可 |
| 情感控制 | CosyVoice3 | 指令控制 |
| 实时变声 | RVC V3 | 170ms |
| 80+语言 | Fish Speech | 80语言 |
| Apple Mac | LongCat MLX | 0.4GB可跑 |

---

## 硬件速查（2026-04-08 更新）

| 显存 | 可跑方案 |
|------|---------|
| 4GB | CosyVoice3, F5-TTS, RVC V3, Qwen3-TTS oQ8 |
| 8GB | ChatTTS v2, GPT-SoVITS, Fish Speech, KaniTTS2 |
| 12GB+ | Qwen3-TTS 1.7B, LongCat 3.5B, Higgs Audio V2.5 |
| Apple M1+ | LongCat MLX（0.4GB可跑！）|
| 无GPU / CPU | Kokoro-82M, Pocket TTS, NeuTTS Air |

---

## 🎯 场景一句话推荐（2026-04-08 更新版）

| 场景 | 首推 | 备选 | 核心指标 |
|------|------|------|---------|
| 中文即时克隆 | CosyVoice3 RL | Qwen3-TTS 1.7B | CER 0.71 / 97ms |
| 英文即时克隆 | Qwen3-TTS 1.7B | Dia2-2B | WER 1.24 / Apache 2.0 |
| 声音相似度最高 | LongCat-AudioDiT 3.5B | CosyVoice3 RL | SIM 0.818 |
| 实时变声/直播 | RVC V3 (ASIO 90ms) | F5-TTS | RTF 0.15 |
| 多语言出海 | LEMAS-TTS (10语言) | Fish Speech (80+) | CC BY 4.0 |
| 中文情感配音 | CosyVoice3 Instruct | Xiaomi MiMo-V2-TTS | 18种方言 |
| Apple Mac 本地 | LongCat-AudioDiT MLX 4bit | KaniTTS2 | 0.4GB VRAM |
| 超低延迟 | Voxtral TTS (90ms) | Orpheus TTS (25ms) | 90ms / 25ms |
| 商用免费可商 | F5-TTS / RVC / CosyVoice3 | — | MIT / Apache 2.0 |
| 少样本微调 | GPT-SoVITS v4 (1分钟) | RVC V3 (10分钟) | SIM高保真 |
| 超长音频生成 | TADA (700秒上下文) | VibeVoice (90分钟) | RTF 0.09 |

---

## 🆕 本周新增（2026-04-07/08）

- **LongCat-AudioDiT MLX量化版** → Apple Silicon原生支持，0.4B参数即可运行（MacBook Air可用！）
- **Qwen3-TTS CustomVoice oQ8** → 0.5B参数 GGUF量化，移动端可跑
- **Dia2-2B** → Nari Labs，HuggingFace新收录，Apache 2.0，英文对话TTS
- **LEMAS-Edit** → IDEA研究院，语音编辑能力

## Benchmark 最终版（Seed-TTS 测试集）

| 模型 | 中文 CER↓ | 英文 WER↓ | SIM↑ | 延迟 |
|------|---------|---------|------|------|
| CosyVoice3 RL | **0.71** | 1.45 | — | 150ms |
| Qwen3-TTS 1.7B | 0.77 | **1.24** | 0.89 | **97ms** |
| LongCat-AudioDiT 3.5B | 1.09 | 1.50 | **0.818** | — |
| TADA | — | — | 4.18/5.0 | RTF 0.09 |
