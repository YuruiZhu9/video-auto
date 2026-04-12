# 通用工具 — VideoLLaMA3（达摩院7B视频理解）

## 核心工具/API

- **VideoLLaMA3-7B**：主模型，视频理解SOTA（开源），7B参数
- **VideoLLaMA3-2B**：端侧版，适合移动/轻量部署，2B参数
- **视觉编码器**：支持任意分辨率（AVT技术），2D-RoPE位置编码
- **DiffFP**：差分帧剪枝器，减少40%-60%视频token
- **VL3Syn7M**：高质量预训练数据集

## 步骤流程

**方案一：Hugging Face Transformers 调用（推荐）**

```python
from transformers import AutoModelForVideoCausalLM, AutoProcessor
import torch

# 1. 加载模型
model_id = "DAMO-NLP-SG/VideoLLaMA3-7B"
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForVideoCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

# 2. 视频理解（任意分辨率输入 - AVT核心优势）
video_path = "tutorial.mp4"
question = "请逐步总结这段视频中讲的所有技术要点"

inputs = processor(
    text=[question],
    videos=[video_path],
    return_tensors="pt",
    padding=True
).to(model.device)

# 3. 生成回答
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.7
    )

answer = processor.batch_decode(outputs, skip_special_tokens=True)[0]
print(answer)
```

**方案二：ModelScope 调用（国内加速）**

```python
from modelscope import snapshot_download, AutoTokenizer, AutoModelForCausalLM
import torch

model_dir = snapshot_download('DAMO-NLP-SG/VideoLLaMA3-7B')
tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

# 视频理解
inputs = tokenizer([question], return_tensors="pt").to(model.device)
with torch.no_grad():
    outputs = model.generate(video_path=video_path, **inputs, max_new_tokens=512)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## 适用场景

- ✅ **技术教程视频**：长视频时间推理 + 步骤提取
- ✅ **课程/演讲视频**：通用视频理解 + 要点抽取
- ✅ **文档+视频混合内容**：InfoVQA 卓越（图表+视频）
- ✅ **STEM教育视频**：MathVista 数学推理能力强
- ✅ **端侧部署**：2B版可本地运行，保护隐私
- ❌ **超长视频（>1小时）**：建议用 Video-XL / VideoSeek
- ❌ **实时流式处理**：建议用 VideoChat-Online

## 避坑指南

**问题1：模型下载慢**
- 解决方案：使用 ModelScope 国内镜像（`modelscope.cn`）
- HuggingFace 国内访问不稳定，建议科学上网或用 ModelScope

**问题2：显存不足**
- 7B版需 ~16GB 显存（fp16），使用 `device_map="auto"` 自动分配
- 2B版仅需 ~6GB，可部署在消费级 GPU
- 如仍不足，使用量化：`load_in_8bit=True` 或 `load_in_4bit=True`

**问题3：视频过长导致 OOM**
- DiffFP 已自动剪枝，但超长视频仍可能超出
- 建议先用 FFmpeg 预分段：`ffmpeg -i long.mp4 -segment_time 1800 -c copy part%d.mp4`
- 或直接使用 Video-XL 处理超长视频

**问题4：时间推理精度不足**
- VideoLLaMA3 的时间推理 SOTA，但复杂多跳推理可能出错
- 建议：关键时间点用 Whisper 提取字幕 + VideoLLaMA3 分析
- 或使用 VideoARM 做 Agentic 深度推理

## 技术亮点详解

### AVT（任意分辨率视觉标记化）

核心：用 2D-RoPE 替换传统绝对位置嵌入，视觉编码器可原生处理任意分辨率图像：

```
传统方法：
  输入图像 → resize到固定分辨率（如224x224）→ 丢失信息
  ↓
VideoLLaMA3：
  输入图像（任意分辨率）→ 2D-RoPE编码 → 保留完整细节
```

### DiffFP（差分帧剪枝）

```
相邻帧像素差异 < 阈值 → 判定冗余 → 丢弃该帧
相邻帧像素差异 ≥ 阈值 → 判定关键 → 保留+压缩
```

效果：视频token减少40%-60%，速度提升显著，精度几乎不下降。

## 参考链接

- 论文：https://arxiv.org/abs/2501.13106
- GitHub：https://github.com/DAMO-NLP-SG/VideoLLaMA3
- HuggingFace：https://huggingface.co/collections/DAMO-NLP-SG/videollama3-678cdda9281a0e32fe79af15
- 视频Demo：https://huggingface.co/spaces/lixin4ever/VideoLLaMA3
- 图像Demo：https://huggingface.co/spaces/lixin4ever/VideoLLaMA3-Image
- ModelScope：https://modelscope.cn/models/DAMO-NLP-SG/VideoLLaMA3-7B
