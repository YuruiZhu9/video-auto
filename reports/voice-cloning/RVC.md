# RVC — 实时变声框架（Voice Conversion）

---

## 基本信息

| 项目 | 信息 |
|------|------|
| GitHub | https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI |
| Stars | ⭐ **35k** |
| 最新版本 | v2.2.231006（2024-06）|
| 许可证 | MIT |
| 中文支持 | ✅ 良好 |
| 声音克隆 | ✅ 变声（10分钟训练）/ ✅ 实时变声 |

---

## 核心亮点

- ⚡ **实时变声**：端到端延迟仅 **170ms**（ASIO 设备可达 90ms）
- 🎯 **极低训练数据**：仅需 **10 分钟** 音频即可训练
- 🔒 **音色保护**：top1 检索替换杜绝音色泄漏
- 🖥️ **WebUI 友好**：开箱即用的网页界面
- 📦 **模型融合**：通过 ckpt-merge 自由混合不同音色
- 🛠️ **工具链完整**：内置人声分离（UVR5）、音高提取（RMVPE）

---

## 与其他工具的区别

> RVC 是 **变声（Voice Conversion）** 工具，不是 TTS 合成工具。
> - TTS（文字转语音）：输入文本 → 生成语音
> - VC（变声转换）：输入任意人的音频 → 转换为目标音色
>
> **典型应用场景**：唱歌变声、视频配音、隐私保护、角色扮演

---

## 声音样本准备要求

| 项目 | 要求 |
|------|------|
| 音频格式 | WAV / MP3 |
| 推荐时长 | **最少 10 分钟**，推荐 20-30 分钟 |
| 采样率 | 32kHz / 40kHz / 48kHz |
| 录音环境 | **安静、无伴奏**（必须无人声以外的声音）|
| 音频质量 | 无削波、无爆音、无回声 |
| 内容建议 | 涵盖不同音高（高/中/低）、不同情感（平静/激动）的句子 |

### 伴奏处理（重要！）
⚠️ 如果录音中包含音乐/伴奏：
1. 使用 WebUI 中的 **UVR5** 工具分离人声
2. 推荐设置：
   - Model: HP-5_only_main_vocal
   - 勾选：Demucs、为人声优化

---

## 安装与部署

### 方法 1： pip 安装（Linux/Windows N卡）

```bash
# 1. 克隆项目
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
cd Retrieval-based-Voice-Conversion-WebUI

# 2. 安装 PyTorch
pip install torch torchvision torchaudio

# RTX 30xx 系列（CUDA 11.7）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# 3. 安装依赖
pip install -r requirements.txt

# 4. 下载预训练模型（从 Hugging Face）
# 模型地址：https://huggingface.co/lj1995/VoiceConversionWebUI/tree/main/
# 需下载：
#   - assets/hubert/hubert_base.pt
#   - assets/pretrained/ (v1 和 v2)
#   - assets/uvr5_weights/
#   - rmvpe.pt

# 5. 启动
python infer-web.py
# 浏览器打开 http://localhost:7860
```

### 方法 2：macOS

```bash
sh ./run.sh
```

### 方法 3：AMD/Intel 显卡

```bash
# AMD ROCm (Linux)
pip install -r requirements-amd.txt

# Intel IPEX (Linux)
pip install -r requirements-ipex.txt

# DML (Windows AMD/Intel)
pip install -r requirements-dml.txt
```

---

## 训练步骤（WebUI）

### Step 1：预处理音频
```
WebUI → 训练标签页
  1. 点击「输入训练文件夹路径」→ 选择包含音频的文件夹
  2. 音频预处理：
     - 自动切片
     - 人声分离（UVR5）
     - 音高提取
```

### Step 2：训练模型
```
训练参数（推荐）：
  - 训练Epoch数：30-50
  - 批量大小：默认即可
  - 音高提取算法：RMVPE（推荐，效果最好）
  
开始训练 → 等待10-30分钟
```

### Step 3：推理使用
```
推理标签页：
  1. 选择训练好的 .pth 模型文件
  - 选择音色模型（可选，用于保护音色）
  2. 输入 f0 参数（音高调整，半音为单位）
     - 0 = 原调
     - +12 = 升高一个八度
     - -12 = 降低一个八度
  3. 上传要变声的音频
  4. 点击「推理」→ 导出变声后音频
```

---

## Python API 调用

```python
from rvc import RVC
import soundfile as sf

def voice_convert(input_audio, output_audio, model_path, f0_key=0):
    """
    变声函数
    input_audio: 输入音频路径
    output_audio: 输出音频路径
    model_path: 训练好的 .pth 模型路径
    f0_key: 音高偏移（半音），0为原调
    """
    vc = RVC(model_path)
    
    # 加载音频
    audio_data, sr = sf.read(input_audio)
    
    # 变声
    converted = vc.convert(
        audio=audio_data,
        sr=sr,
        f0_key=f0_key,  # 音高偏移
        index_rate=0.75,  # 音色检索强度（越大音色越接近训练音色）
        filter_radius=3,  # 滤波半径
        rms_mix=0.25,  # 音量混合
        protect=0.33,  # 保护非人声部分
    )
    
    # 保存
    sf.write(output_audio, converted, sr)
    return output_audio

# 使用示例
result = voice_convert(
    input_audio="input.wav",
    output_audio="output.wav",
    model_path="./weights/我的声音.pth",
    f0_key=0  # 不变调
)
print(f"✅ 变声完成: {result}")
```

---

## 与 OpenClaw Skills 集成

```python
import subprocess
import os

RVC_DIR = "/workspace/rvc-webui"

def rvc_voice_clone(source_audio, target_voice_pth, output_path, f0_key=0):
    """
    RVC 变声 - OpenClaw Skill 集成
    source_audio: 要变声的音频
    target_voice_pth: 训练好的音色模型
    output_path: 输出路径
    f0_key: 音高偏移（半音）
    """
    cmd = [
        "python", f"{RVC_DIR}/infer-web.py",
        "--model", target_voice_pth,
        "--input", source_audio,
        "--output", output_path,
        "--f0_key", str(f0_key),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return output_path
    raise Exception(f"RVC 变声失败: {result.stderr}")
```

---

## 实时变声配置

### 目标：唱歌实时变声

```
设备要求：
  - ASIO 声卡（或虚拟 ASIO）
  - 麦克风
  - 目标延迟 < 200ms

WebUI → 实时变声标签页
  1. 选择 RVC 模型
  2. 设置：
     - 推理批次大小：1-3
     - 音高提取：RMVPE
     - 变调参数
  3. 选择 ASIO 输入输出设备
  4. 开始实时变声
```

---

## 常见问题与解决

| 问题 | 解决方案 |
|------|----------|
| 训练后音色不自然 | 增加训练数据（建议20-30分钟）；调低训练步数 |
| 变声后跑调 | 切换音高提取算法（RMVPE > faiss >crepe）；调整 f0 参数 |
| 有底噪/杂音 | 使用 UVR5 更好地分离人声；增加训练数据信噪比 |
| 实时变声延迟高 | 使用 ASIO 设备；降低推理批次大小；切换到 RMVPE |
| 显存不足 | 减小 batch_size；使用 TensorRT 加速 |
| 模型太大 | 使用模型压缩；切换到 v2 底模（更小）|

---

## 性能对比

| 设备 | 实时变声延迟 | 训练时间（10分钟数据）|
|------|------------|-------------------|
| RTX 4090 | ~50ms | ~5分钟 |
| RTX 3060 | ~100ms | ~15分钟 |
| RTX 2060 | ~170ms | ~30分钟 |
| AMD RX 7900 | ~150ms | ~20分钟 |
