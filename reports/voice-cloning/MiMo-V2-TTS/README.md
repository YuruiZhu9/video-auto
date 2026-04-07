# Xiaomi MiMo-V2-TTS — 小米情感语音合成大模型

> 🤖 免费语音克隆方案Agent | 2026-03-27 新增

---

## 一、模型概览

| 指标 | 数值 |
|------|------|
| **发布时间** | 2026年3月18日 |
| **开发团队** | 小米（Xiaomi） |
| **参数量** | 未公开（超亿小时语音数据预训练） |
| **训练数据** | **超亿小时**语音数据 |
| **架构** | 自研 Audio Tokenizer + 多码本语音-文本联合建模 |
| **克隆方式** | 零样本克隆（参考音频） |
| **开源协议** | 需确认（参考 mimo.xiaomi.com） |
| **GitHub** | [github.com/XiaomiMiMo](https://github.com/XiaomiMiMo) |
| **官网** | [mimo.xiaomi.com/mimo-v2-tts](https://mimo.xiaomi.com/mimo-v2-tts) |
| **API平台** | [platform.xiaomimimo.com](https://platform.xiaomimimo.com) |

---

## 二、核心亮点

### 🎯 超亿小时语音预训练
- 基于自研 Audio Tokenizer（语义提取+高保真重建统一分词器）
- 多码本语音-文本联合建模架构
- 超亿小时多样化语音数据预训练
- 多维度强化学习微调（RLHF对齐）

### 😃 多粒度情感控制
- **SSML标签控制**：可在句子中途切换情感（如"兴奋→专业"）
- **上下文情感推断**：自动根据文本内容推断合适情感
- 情感表达细腻自然，避免AI机械感

### 🌏 方言支持（中文）
- **粤语**（Cantonese）
- **四川话**（Sichuanese）
- **台湾腔**（Taiwanese accent）
- 覆盖主要中文方言，适用区域化语音场景

### 🎤 歌唱合成
- 精确音高控制（Pitch Control）
- 颤音控制（Vibrato Control）
- 游戏、娱乐等创意场景可用

### 🔌 OpenAI兼容API
- 提供与 OpenAI API 兼容的接口
- 支持 `mimo_default` / `default_zh` / `default_en` 等预置音色
- 便于快速集成到现有应用

---

## 三、性能与规格

| 指标 | 数值 |
|------|------|
| 预训练数据 | 超亿小时语音 |
| 情感控制粒度 | 句内多粒度切换 |
| 延迟 | <200ms TTFT（参考MiMo-V2-Pro） |
| 音频质量 | 24kHz（推测） |
| 中文方言 | 粤语/四川话/台湾腔 |
| 歌唱合成 | 支持音高+颤音控制 |
| 开源 | 尚未完全开源（API可用） |

---

## 四、安装与使用

### API调用（OpenAI兼容）

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.xiaomimimo.com/v1"
)

response = client.audio.speech.create(
    model="MiMo-V2-TTS",
    voice="default_zh",       # 中文预置音色
    input="欢迎使用小米语音合成模型！"
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

### 预置音色列表

| voice 参数 | 说明 |
|------------|------|
| `mimo_default` | 默认音色 |
| `default_zh` | 中文默认音色 |
| `default_en` | 英文默认音色 |

### SSML情感标签示例

```xml
<speak>
    <voice name="excited">今天太开心了！</voice>
    <voice name="professional">接下来为您介绍产品功能。</voice>
</speak>
```

### 本地部署（待开源）

> ⚠️ 注意：截至2026年3月，MiMo-V2-TTS尚未完全开源，仅提供API访问。
> 关注 GitHub：https://github.com/XiaomiMiMo

```bash
# 预计开源后安装方式（参考）
git clone https://github.com/XiaomiMiMo/MiMo-V2-TTS.git
cd MiMo-V2-TTS
pip install -r requirements.txt
python app.py --port 8000
```

---

## 五、适用场景

| 场景 | 适配度 | 说明 |
|------|--------|------|
| 智能语音助手/客服 | ⭐⭐⭐⭐⭐ | 多粒度情感，告别机械感 |
| 区域化语音产品 | ⭐⭐⭐⭐⭐ | 支持粤语/四川话/台湾腔 |
| 有声书/配音 | ⭐⭐⭐⭐ | 中文情感表达自然 |
| 游戏NPC语音 | ⭐⭐⭐⭐ | 支持歌唱合成 |
| 多语言应用 | ⭐⭐⭐⭐ | 中英双语，中英混合 |

---

## 六、与主流方案对比

| 方案 | 情感控制 | 方言支持 | 歌唱合成 | 开源情况 |
|------|----------|----------|----------|----------|
| **MiMo-V2-TTS** | 句内多粒度 | 粤语/四川话/台湾腔 | ✅ | ⚠️ API可用，待开源 |
| CosyVoice 3.0 | 多情感 | 18+方言 | ❌ | ✅ 完全开源 |
| ChatTTS v2 | 对话情感 | 无 | ❌ | ✅ 完全开源 |
| Qwen3-TTS | 自然语言描述 | 中文为主 | ❌ | ✅ 完全开源 |
| Fish Audio S2 | 精细情感标签 | 80+语言 | ❌ | ⚠️ 不可商用 |

---

## 七、常见问题

| 问题 | 解决方案 |
|------|----------|
| API访问需要付费？ | 发布首周免费（2026-03-18起），关注platform.xiaomimimo.com |
| 本地部署不可用？ | 目前仅API，需等待开源（关注GitHub） |
| 是否支持零样本克隆？ | API支持参考音色，但克隆能力待验证 |
| 如何选择音色？ | 试用 `default_zh`（中文）和 `default_en`（英文）|

---

## 八、相关资源

- [官网产品页](https://mimo.xiaomi.com/mimo-v2-tts)
- [API平台](https://platform.xiaomimimo.com)
- [GitHub](https://github.com/XiaomiMiMo)
- [AIHub介绍](https://www.aihub.cn/ai-model/xiaomi-mimo-v2-tts/)
- [知乎接入测试](https://zhuanlan.zhihu.com/p/2018246353650758564)
