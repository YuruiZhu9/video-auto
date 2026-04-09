---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3aaee6c2ae8868cafac14ec89b719003
    PropagateID: 3aaee6c2ae8868cafac14ec89b719003
    ReservedCode1: 304402206542ed8fa5a92cb420213ae12c132aa7b3ebff5071e5cb1c7c1c104c1ceb19f6022027c49af32f0fc3142c37036a6555a6d88a445f022d63fec56cf303c215ea7d29
    ReservedCode2: 304402205cdf07fc17a0505c3082e4d8fc728d07ca71ace91f73a132f7c189a9dc97abde02202669d69dcc73c562dad2d6d2004030dde88369318e33630f127abf507ba33794
---

# TOOLS.md - Local Notes

## 搜索 API

### 博查 AI Web Search API
- **Key:** sk-7aa8fbfa43534a9e8fb26a3d1ab74b6a
- **接口：** POST https://api.bochaai.com/v1/web-search
- **调用示例：**
```bash
curl -s -X POST "https://api.bochaai.com/v1/web-search" \
  -H "Authorization: Bearer sk-7aa8fbfa43534a9e8fb26a3d1ab74b6a" \
  -H "Content-Type: application/json" \
  -d '{"query":"搜索关键词","count":10,"freshness":"oneDay"}'
```
- **freshness 参数：** oneDay（今日）/ oneWeek / oneMonth / noLimit
- **返回格式：** JSON，data.webPages.value 包含搜索结果列表（name/url/snippet）
- **注意：** web_search 工具不支持博查，用 exec + curl 调用

---

## TTS 语音合成模型

> 完整收录见 `/workspace/model-library-tts.md`，包含 Kokoro-82M 和 Voxcpm2 等开源模型详细评测。
> Voxcpm2 已收录至 model-library-tts.md（2026-04-09）。

---

## 免费 AI API（注册即用，长期免费）

### 文本生成

| 平台 | 模型 | 免费额度 | 注册地址 |
|------|------|---------|---------|
| **智谱AI** | GLM-4-Flash | 200万Tokens/天 | https://open.bigmodel.cn/ |
| **阿里魔搭** | qwen-plus/turbo | 2000次/天 | https://modelscope.cn → 个人中心→访问令牌 |
| **蚂蚁Ling Studio** | Ling-1T | 50万Tokens/天 | https://ling-studio.antgroup.com |
| **百度千帆** | ERNIE-Bot | 500次/天 | https://console.bce.baidu.com/qianfan/ |

### 图片/视频/语音生成

| 平台 | 类型 | 免费额度 | 注册地址 |
|------|------|---------|---------|
| **Hypereal AI** | 图片/视频/TTS/3D | 35积分（注册送） | https://hypereal.ai/dashboard → API Keys |
| **阿里通义万相** | 图片 | 新用户免费 | https://dashscope.console.aliyun.com/ |

**Hypereal AI 常用端点：**
```bash
# 图片
curl -X POST https://api.hypereal.ai/v1/generate/image \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"model":"flux-2","prompt":"...","width":1024,"height":1024}'

# 视频
curl -X POST https://api.hypereal.ai/v1/generate/video \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"model":"wan-2.5","prompt":"...","duration":5}'
```

### 智谱AI调用示例
```python
import requests
url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
headers = {"Authorization": "Bearer YOUR_KEY"}
data = {"model": "glm-4-flash", "messages": [{"role": "user", "content": "你好"}]}
print(requests.post(url, headers=headers, json=data).json())
```
