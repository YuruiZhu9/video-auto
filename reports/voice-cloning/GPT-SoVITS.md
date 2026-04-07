# GPT-SoVITS — 开源最成熟声音克隆方案

---

## 基本信息

| 项目 | 信息 |
|------|------|
| GitHub | https://github.com/RVC-Boss/GPT-SoVITS |
| Stars | ⭐ **53.2k**（语音克隆类最高）|
| 最新版本 | V4 / V2Pro |
| 许可证 | MIT |
| 中文支持 | ✅ 极佳 |
| 声音克隆 | ✅ 零样本（5秒）+ 少样本微调（1分钟）|

---

## 核心亮点

- 🎯 **零样本克隆**：仅需 **5 秒** 音频即可克隆音色（业界最低门槛）
- ⚡ **少样本微调**：1 分钟音频微调后，相似度大幅提升
- 📊 **最高 Star**：53.2k，开源语音克隆类项目 Star 数最高
- 🌐 **多语言**：中文、英语、日语、韩语、粤语
- 🛠️ **工具链完整**：内置人声分离、自动切片、中文 ASR、文本标注
- 📦 **Docker 支持**：一行命令完成部署

---

## 版本演进

| 版本 | 特点 |
|------|------|
| V1 | 基础版本 |
| V2 | 增加韩语和粤语，训练数据从 2k 小时扩展到 5k 小时 |
| V3 | 更高音色相似度，GPT 模型更稳定 |
| V4 | 修复金属伪影，原生输出 48kHz 高质量音频 |
| V2Pro | 性能优于 V2，硬件成本和速度与 V2 相当 |

---

## 声音样本准备要求

| 项目 | 要求 |
|------|------|
| 音频格式 | WAV / MP3 / FLAC |
| 推荐时长 | 零样本：5-30秒；微调：**1-10 分钟** |
| 采样率 | 16kHz / 32kHz / 48kHz（越高越好）|
| 录音环境 | **安静、无回声、无背景音乐、无伴奏** |
| 音频质量 | 128kbps 以上，无削波、无爆音 |
| 文本标注 | 零样本时需要；微调时可自动生成 |

### 录音技巧
1. **时长**：微调推荐 5-30 分钟效果更好，1 分钟最低可用
2. **内容**：涵盖多种句子结构（短句、长句、疑问句、感叹句）
3. **语速**：有快有慢，覆盖不同情感（平静、激动、疑问）
4. **设备**：手机录音可用，但建议用耳机麦克风减少环境音
5. **噪声处理**：有噪音可使用 UVR5 工具分离人声（内置）

---

## 安装与部署

### 方法 1：Docker 部署（⭐推荐，最简单）

```bash
# 克隆项目
git clone https://github.com/RVC-Boss/GPT-SoVITS
cd GPT-SoVITS

# 启动（自动下载模型）
docker compose run --service-ports GPT-SoVITS-CU126
# 浏览器打开 http://localhost:7860
```

### 方法 2：Conda 手动部署

```bash
# Linux + CUDA
conda create -n GPTSoVits python=3.10
conda activate GPTSoVits
bash install.sh --device cuda --source https://github.com/RVC-Boss/GPT-SoVITS

# Windows PowerShell
conda create -n GPTSoVits python=3.10
conda activate GPTSoVits
pwsh -F install.ps1 --Device cuda --Source https://github.com/RVC-Boss/GPT-SoVITS
```

---

## 训练步骤（WebUI）

### 1. 数据准备（上传音频）
```
# 目录结构
GPT-SoVITS/
└── data/
    └── my_voice/
        ├── 1.wav
        ├── 2.wav
        └── ...
```

### 2. 预处理（WebUI 中点击「一键三连」）
- **人声分离**：使用 UVR5 去除背景音乐/伴奏
- **自动切片**：将长音频切成短句
- **ASR 标注**：自动识别音频文本（需下载 ASR 模型）

### 3. 训练
```
WebUI → 训练标签页
  - 选择预处理后的数据集
  - 设置 Epoch（默认 15-20 即可）
  - 开始训练
```

### 4. 推理
```
WebUI → 推理标签页
  - 选择训练好的模型
  - 上传参考音频（或输入参考文本）
  - 输入要合成的文本
  - 点击生成
```

---

## Python API 调用

### 零样本推理（5秒音频即可）
```python
import subprocess
import os

def gpt_sovits_zero_shot(text, ref_audio, ref_text, output_path):
    """
    使用零样本模式（需要预训练底模）
    text: 要合成的文本
    ref_audio: 参考音频路径（5秒+）
    ref_text: 参考音频对应的文本
    output_path: 输出路径
    """
    cmd = [
        "python", "GPT_SoVITS/inference_webui.py",
        "--gpt_path", "GPT_SoVITS/pretrained_models/gptsovits-v3-*.pt",
        "--sovits_path", "GPT_SoVITS/pretrained_models/sovits-*.pt",
        "--ref_audio", ref_audio,
        "--ref_text", ref_text,
        "--text", text,
        "--output", output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
```

### 微调模型推理
```python
def gpt_sovits_infer(text, gpt_model_path, sovits_model_path, 
                     ref_audio, ref_text, output_path):
    """
    使用微调后的模型进行推理
    """
    from GPT_SoVITS.inference import GPTSoVITS

    tts = GPTSoVITS(
        gpt_path=gpt_model_path,
        sovits_path=sovits_model_path,
    )
    
    audio = tts.generate(
        text=text,
        reference_audio=ref_audio,
        reference_text=ref_text,
    )
    audio.save(output_path)
    return output_path
```

---

## 与 OpenClaw Skills 集成

```python
import subprocess
import json
import uuid
import os

WORKSPACE = "/workspace/gpt_sovits"
os.makedirs(f"{WORKSPACE}/output", exist_ok=True)

def clone_voice(text, ref_audio_path, ref_text):
    """
    OpenClaw Skill: 语音克隆
    输入: text - 要合成的文本
          ref_audio_path - 参考音频路径
          ref_text - 参考音频文本
    输出: 生成的音频文件路径
    """
    output_file = f"{WORKSPACE}/output/{uuid.uuid4().hex}.wav"
    
    # 优先使用微调模型（如果存在）
    gpt_model = f"{WORKSPACE}/pretrained_models/gptsovits-finetune/*.pt"
    
    cmd = [
        "python", f"{WORKSPACE}/GPT_SoVITS/inference_webui.py",
        "--gpt_path", gpt_model,
        "--ref_audio", ref_audio_path,
        "--ref_text", ref_text,
        "--text", text,
        "--output", output_file,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(output_file):
        return output_file
    raise Exception(f"GPT-SoVITS 失败: {result.stderr}")
```

---

## 常见问题与解决

| 问题 | 解决方案 |
|------|----------|
| 零样本效果不够好 | 使用微调模式，1分钟音频即可显著提升 |
| 显存不足 | 使用 `--batch-size 1` 或切换到 CPU 推理 |
| 推理太慢 | 使用 V2Pro 版本；升级到 RTX 4090 加速 |
| 中文发音不准 | 确保使用中文 ASR 模型标注；用 G2PWModel 处理文本 |
| 吞字/漏字 | 检查音频-文本对齐是否准确；调整切片参数 |
| 无背景音乐可用音频 | 使用 UVR5 从音乐中提取人声（内置工具）|
| Mac 无法训练 | 支持 CPU 推理但训练需 GPU；Mac 可用 Docker 尝试 |

---

## 性能基准

| 设备 | RTF | 1400字耗时 |
|------|-----|-----------|
| RTX 4060Ti | 0.028 | ~5秒 |
| RTX 4090 | 0.014 | ~3.4秒 |
| M4 Mac CPU | 0.526 | ~130秒 |
| Intel i9 CPU | 0.8+ | 非常慢 |

---

## 最佳实践总结

1. **首次使用**：用 Docker 一键启动，用零样本模式测试（5秒音频）
2. **提升质量**：准备 5-30 分钟音频，微调 15-20 Epoch
3. **录音建议**：安静环境下，用手机或耳机麦克风录制
4. **中文优化**：确保使用中文 ASR 模型和 G2PW 文本前端
5. **模型保存**：微调后保存 pth 文件，方便下次复用
