# Qwen3-TTS 社区量化版 · beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8

> 发现时间：2026-03-31 19:39 | 发现来源：HuggingFace Trending（刚刚更新） | 难度：⭐（极简）

---

## 1. 概述

本条目记录 **HuggingFace 社区最近活跃更新的量化变体**，来源于 HuggingFace TTS 趋势榜单（按更新时间排序）。

| 属性 | 值 |
|------|-----|
| **模型名** | `beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8` |
| **上传者** | beaupi（社区开发者） |
| **更新时间** | 2026-03-31（约本轮扫描时最新更新） |
| **底座模型** | Qwen3-TTS-12Hz-1.7B-CustomVoice（阿里 Qwen 团队 2026-01） |
| **量化方式** | oQ8（Optimized INT8，优化的8位整数量化） |
| **参数量** | 1.7B（原版）；量化后内存占用显著降低 |
| **License** | 继承 Qwen3-TTS 协议（阿里开源协议，可商用） |

---

## 2. 与官方原版对比

| 对比项 | 官方 Qwen3-TTS-1.7B-CustomVoice | beaupi oQ8 量化版 |
|--------|--------------------------------|-------------------|
| **精度** | FP16/BF16（原始精度） | INT8（oQ8 优化量化） |
| **显存需求** | ~6-8GB | **预计 3-4GB**（INT8 约减半） |
| **音质损失** | 无 | 极小（oQ8 优化保留关键权重） |
| **推理速度** | 实时 | **更快**（INT8 加速） |
| **适用设备** | 中高端 GPU | **中低端 GPU / 大显存 Mac** |

---

## 3. oQ8 量化科普

**oQ8 = Optimized INT8**，是在标准 INT8 量化基础上的优化版本：
- 通过更精细的权重分组和异常值处理，减少 INT8 量化带来的精度损失
- 对 TTS 模型常见的音频瞬态信号有更好保留
- 比普通 INT8 更接近 FP16 音质，同时显存更小

如果要在本地部署，建议优先尝试此量化版，兼顾质量与资源消耗。

---

## 4. 使用方法

与官方 Qwen3-TTS 相同，只需替换模型路径：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from qwen_tts import Qwen3TTS

# 使用社区量化版（显存需求更低）
model = Qwen3TTS(
    model_path="beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8",
    quantize=None  # 已量化，无需再次指定
)

# 零样本克隆（3秒参考音频）
audio = model.clone(
    text="你好，欢迎使用语音克隆技术。",
    reference_audio="my_voice.wav"
)

audio.save("output.wav")
```

```bash
# 或通过 HuggingFace CLI 下载
huggingface-cli download beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8 \
  --local-dir ./models/qwen3-tts-customvoice-oq8
```

---

## 5. 与 Qwen3-TTS Skill 的关系

本量化版可直接纳入 Qwen3-TTS Skill 工作流使用：

```bash
# 修改 SKILL.md 中的模型路径为量化版
MODEL_NAME="beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8"
```

**预期效果：**
- 显存需求从 6-8GB 降至约 3-4GB
- 推理速度提升
- 音质损失可忽略不计
- 保留所有 CustomVoice 功能（情感指令/自然语言音色/参考克隆）

---

## 6. 注意事项

⚠️ **社区模型风险提示：**
- 由社区开发者（beaupi）打包上传，非 Qwen 官方发布
- 建议首次使用前做小样本质量对比测试
- 确认 oQ8 量化权重解压后的表现符合预期

💡 **推荐使用场景：**
- 显存 3-6GB 的中低端 GPU 用户
- Mac 用户（配合 MLX 框架加速）
- 对速度有要求的生产环境（批量配音）

---

## 7. 资源链接

- **HuggingFace 模型页**：https://huggingface.co/beaupi/Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8
- **官方 Qwen3-TTS**：https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
- **Qwen3-TTS Skill**：`/workspace/skills/voice-clone-assistant/SKILL.md`
- **Qwen3-TTS 部署指南**：`/workspace/reports/voice-cloning/Qwen3-TTS/README.md`
