# 免费语音克隆 TOP5 懒人速查卡（2026-04-07更新）

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

## 硬件速查

| 显存 | 可跑方案 |
|------|---------|
| 4GB | CosyVoice3, F5-TTS, RVC V3, Qwen3-TTS oQ8 |
| 8GB | ChatTTS v2, GPT-SoVITS, Fish Speech |
| 12GB+ | Qwen3-TTS 1.7B, LongCat 3.5B |
| Apple M1+ | LongCat MLX（0.4GB）|
