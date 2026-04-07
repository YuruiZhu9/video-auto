# ☁️ 免费 AI API 完整指南

> 来源：跨Agent新技术同步中心 — 模型库
> ⚠️ 免费额度以平台最新政策为准，实名认证后即可使用
> 额度每日 UTC+8 00:00 重置，超量返回 429 错误，不自动扣费

---

## 📝 文本生成 API（免费）

| 平台 | 模型 | 免费额度 | 注册地址 | API格式 | 备注 |
|------|------|---------|---------|---------|------|
| **智谱AI** | GLM-4.7-Flash / GLM-4-Flash | **模型本身永久免费**，输入+输出均免费 | https://open.bigmodel.cn/ | 类OpenAI (v4/chat/completions) | 中文友好，新用户另赠20M Tokens一次性额度 |
| **硅基流动CN** | Qwen3.5-4B / DeepSeek-R1-Distill-Qwen-7B / GLM-4-9B 等12个模型 | **模型本身永久免费**（无明确日额度上限） | https://account.siliconflow.cn/zh/login | 类OpenAI格式 | 国内直连，兼容OpenAI格式，需注册 |
| **阿里云DashScope** | qwen-plus / qwen-max 等 | 注册有赠送额度，2000次/天 | https://dashscope.aliyuncs.com/ | REST / Python SDK | 需阿里云账号 |
| **百度千帆（QianFan）** | ERNIE-Bot-4 / ERNIE-Bot-turbo | 注册有赠送额度 | https://console.bce.baidu.com/qianfan/ | qianfan Python SDK 或 AK/SK签名 | 需百度云实名 |
| **Hugging Face Inference** | Llama 3 / Mistral / Flan-T5 等10万+开源模型 | 有速率限制（Serverless免费） | https://huggingface.co/ → Settings→Access Tokens | 自由选择开源模型 | 速率限制，冷启动较慢 |

**推荐首选：智谱GLM-4.7-Flash（永久免费，200K上下文，中文能力强）**
**备选：硅基流动（12个免费开源模型，无需海外手机号）**

---

## 🎨 图片生成 API（免费）

| 平台 | 模型 | 免费额度 | 注册地址 | API格式 | 备注 |
|------|------|---------|---------|---------|------|
| **Hypereal AI** | Flux 2 / SDXL / SeeDream 4.0 / Recraft / Qwen Image | **35免费积分**（注册即送，可生成数千张） | https://hypereal.ai/dashboard → API Keys | REST: `POST https://api.hypereal.ai/v1/generate/image` | 无需信用卡，$0.001/张起，统一密钥 |
| **阿里云通义万相** | Wanx2.1 | 新用户免费试用 | https://dashscope.console.aliyun.com/ | REST / Python SDK | 需阿里云账号 |
| **讯飞星火** | 图像生成模型 | 新用户免费额度 | https://xinghuo.xfyun.cn/ | REST API | 需讯飞账号 |
| **Stability AI** | Stable Diffusion 3 / SDXL | 每月25免费积分 | https://platform.stability.ai/ → API Keys | REST: `POST https://api.stability.ai/v1/generation/` | 免费输出带水印 |
| **Together AI** | Flux / SDXL | 注册送1美元积分 | https://api.together.ai/ → Settings→API Keys | 类OpenAI格式 | 额度较小 |
| **laozhang.ai（中转）** | DALL-E 3 / GPT-4o / Gemini / 通义万相 | 新用户注册送免费积分 | https://api.laozhang.ai/register/ | 兼容OpenAI格式，国内直连 | 中转服务，价格低30-50%，中文支持 |

**推荐首选：Hypereal AI（35积分=数千张图像，图片/视频/TTS/3D统一API）**

---

## 🎬 视频生成 API（免费）

| 平台 | 模型 | 免费额度 | 注册地址 | API格式 | 备注 |
|------|------|---------|---------|---------|------|
| **Hypereal AI** | Sora 2 / Kling 2.1 / WAN 2.5 / Seedance | **35免费积分** | https://hypereal.ai/dashboard → API Keys | REST: `POST https://api.hypereal.ai/v1/generate/video` | $0.02/秒起，支持多种视频模型 |
| **Replicate** | 社区视频模型（Sora类、Kling类等） | 新用户免费GPU时长 | https://replicate.com/ → API Tokens | Python/CLI调用 | 冷启动30-60秒，额度有限 |

**推荐首选：Hypereal AI（35积分覆盖图片+视频+3D+语音，统一API，无需多平台注册）**

---

## 🎵 语音 / TTS API（免费）

| 平台 | 模型 | 免费额度 | 注册地址 | API格式 | 备注 |
|------|------|---------|---------|---------|------|
| **Hypereal AI** | 语音克隆 / 30+语言TTS | 包含在35免费积分中 | https://hypereal.ai/dashboard → API Keys | REST API | 10秒样本语音克隆 |
| **Fish Audio** | 开源语音克隆 / TTS | 限制性免费 | https://fish.audio/ → API | 开源模型，本地可部署 | 支持中文语音克隆 |

---

## 🆕 3D生成 API（免费）

| 平台 | 模型 | 免费额度 | 注册地址 | API格式 | 备注 |
|------|------|---------|---------|---------|------|
| **Hypereal AI** | TripoSR / Rodin / Hunyuan3D | 包含在35免费积分中 | https://hypereal.ai/dashboard → API Keys | REST API | 文本转3D / 图像转3D |
| **Meshy** | 3D生成模型 | 每月200免费积分 | https://meshy.ai/ → API Keys | REST API | 免费层级分辨率较低 |

---

## 📌 调用示例

**智谱AI（文本）**
```python
import requests
url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "model": "glm-4-flash",
    "messages": [{"role": "user", "content": "解释量子计算原理"}]
}
response = requests.post(url, headers=headers, json=data)
print(response.json()["choices"][0]["message"]["content"])
```

**Hypereal AI（图片）**
```bash
curl -X POST https://api.hypereal.ai/v1/generate/image \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"flux-2","prompt":"cyberpunk Tokyo sunset","width":1024,"height":1024}'
```

**Hypereal AI（视频）**
```bash
curl -X POST https://api.hypereal.ai/v1/generate/video \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"wan-2.5","prompt":"golden retriever running on beach","duration":5}'
```

**阿里魔搭（文本，类OpenAI格式）**
```python
import openai
client = openai.OpenAI(
    api_key="YOUR_MODELSCOPE_TOKEN",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
resp = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "你好"}]
)
print(resp.choices[0].message.content)
```

---

> 📅 更新日志见 CHANGELOG.md — 免费API相关条目
