# Voice Clone & TTS Skill

> 声音克隆（优先）+ TTS 备选，一体化语音生成方案

## 触发条件
用户需要将文本转换为语音（配音），或需要用少量音频克隆声音时使用。

## 输入
- `audio_file`: 原始音频文件路径（可选，用于克隆）
- `text`: 要朗读的文本（字符串）
- `mode`: "clone"（克隆模式）或 "tts"（直接TTS）
- `voice_name`: 克隆声音的名称标识（可选，默认 "custom_voice"）
- `language`: 语种（"auto" / "zh" / "en"，默认"auto"）

## 输出
- TTS 音频文件路径：`/workspace/agents/video-auto/audio/tts_output.wav`
- 克隆模型就绪提示或 TTS 完成提示

---

## 方案一：声音克隆（优先使用）

### 推荐方案：Fish Audio（开源免费，中文最强）

**API 端点：** `https://api.fish.audio`  
**文档：** https://fish.audio/apis/

**克隆步骤：**

**Step 1：上传参考音频，获取模型 ID**
```python
import requests

# 上传5-30秒音频样本
with open("your_voice_sample.wav", "rb") as f:
    files = {"file": f}
    headers = {"Authorization": "Bearer YOUR_FISH_API_KEY"}
    resp = requests.post(
        "https://api.fish.audio/model/train",
        headers=headers,
        files=files,
        data={"name": "my_voice", "language": "zh"}
    )
    result = resp.json()
    model_id = result["model_id"]  # 克隆后的模型ID
```

**Step 2：使用克隆模型合成语音**
```python
import requests

text = "要朗读的完整文本内容"
resp = requests.post(
    "https://api.fish.audio/tts",
    headers={"Authorization": f"Bearer {model_id}"},
    json={
        "text": text,
        "chunk_length": 50,  # 每次发送的字符数
    }
)
with open("output.wav", "wb") as f:
    f.write(resp.content)
```

**免费方案限制：** Fish Audio 免费层有一定用量限制
**申请地址：** https://fish.audio/

---

### 备选方案：CosyVoice 3.0（阿里达摩院，开源最强中文）

**GitHub：** https://github.com/SymphonyOS/CosyVoice  
**模型：** CosyVoice-300M-SFT / CosyVoice-300M-Instruct

**本地部署（需GPU）：**
```bash
# 推荐用预训练模型，直接使用
git clone https://github.com/SymphonyOS/CosyVoice.git
cd CosyVoice
pip install -r requirements.txt
python CosyVoice/cli/clone.py --audio sample.wav --text "要朗读的文本"
```

**托管API方案：** 使用阿里云 PAI-DSW 或其他 GPU 云服务部署

---

## 方案二：TTS 直接合成（无克隆素材时使用）

### 方案A：MiniMax TTS（推荐，延迟低，质量高）

MiniMax 语音合成在国内效果优秀，支持多语言：

```python
import requests

url = "https://api.minimax.chat/v1/t2a_v2"
headers = {
    "Authorization": "Bearer YOUR_MINIMAX_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "model": "speech-02-hd",
    "text": "要朗读的文本内容",
    "stream": False,
    "voice_setting": {
        "voice_id": "male-qn-qingse",  # 或选择其他音色
        "speed": 1.0,
        "volume": 1.0,
        "pitch": 0
    },
    "audio_setting": {
        "audio_bitrate": 128000,
        "audio_format": "wav",
        "sample_rate": 32000
    }
}
resp = requests.post(url, headers=headers, json=data)
with open("output.wav", "wb") as f:
    f.write(resp.content)
```

**API申请：** https://platform.minimaxi.com/

---

### 方案B：Fish Audio TTS（免费，无需克隆）

Fish Audio 也提供 base TTS 模型，无需参考音频：

```python
import requests

resp = requests.post(
    "https://api.fish.audio/tts",
    headers={"Authorization": "Bearer YOUR_FISH_API_KEY"},
    json={
        "text": "要朗读的文本内容",
        "model": "default",  # 使用官方基础模型
        "language": "zh"
    }
)
with open("output.wav", "wb") as f:
    f.write(resp.content)
```

---

### 方案C：ElevenLabs（英文最强，免费层可用）

```python
import requests

voice_id = "21m00Tcm4TlvDq8ikYAM"  # Rachel, 常用英文音色
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {
    "xi-api-key": "YOUR_ELEVENLABS_KEY",
    "Content-Type": "application/json"
}
data = {
    "text": "Text to read aloud",
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
}
resp = requests.post(url, headers=headers, json=data)
with open("output.wav", "wb") as f:
    f.write(resp.content)
```

**免费额度：** 每月 10,000 字符  
**申请地址：** https://elevenlabs.io/

---

## 智能选择逻辑

```
if audio_file 存在 and (克隆需求 or 想要个性化声音):
    → 使用 Fish Audio 克隆（免费开源，中文好）
elif 中文内容:
    → 使用 MiniMax TTS（延迟低，质量好）
elif 英文内容:
    → 使用 ElevenLabs（英文最自然）
else:
    → Fish Audio TTS（多语言，免费）
```

## 注意事项
- 克隆音频建议 5-30 秒，音质清晰，无背景音乐
- 合成文本过长时（>500字），分段合成再拼接
- 输出格式统一为 WAV（16kHz，单声道）便于后续视频制作
- 中文 TTS 推荐使用 `zh` 语种参数，提升准确率
