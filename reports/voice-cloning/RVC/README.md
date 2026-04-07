# RVC v2 — 实时变声与声音转换

> 项目地址：https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
> Stars：~50k（截至2026年3月）
> 最新版本：v2

---

## 一、项目简介

**RVC（Retrieval-based Voice Conversion）** 即检索式声音转换，是一个基于 VITS 的开源语音转换框架，最大的优势是：
- ⚡ **实时变声**：延迟低至 **90ms**
- 🎤 **零样本声音转换**：无需训练即可转换
- 🎵 **音乐场景适用**：可用于歌曲翻唱

### 与 TTS 克隆的区别

| 特性 | RVC 声音转换 | TTS 声音克隆（CosyVoice等） |
|------|-------------|------------------------------|
| 输入 | 源说话人音频 | 文本 |
| 输出 | 目标音色的音频 | 目标音色的音频 |
| 场景 | 实时变声、歌曲翻唱 | 有声内容生成、播客 |
| 延迟 | 极低（90ms） | 较高（150ms+） |

### 核心功能
- 🎙️ **实时变声**：适合直播连麦、游戏语音
- 🎵 **歌声转换**：将唱歌声音转换为目标歌手音色
- 🔧 **模型融合**：多个模型混合生成新音色
- 🛡️ **音色防泄漏**：top1 检索技术防止音色串扰

---

## 二、声音样本准备要求

### 音频格式要求

| 项目 | 要求 |
|------|------|
| 格式 | WAV、MP3、FLAC |
| 采样率 | 16kHz 或 48kHz |
| 人声提取后 | 推荐 20-40kHz |
| 训练数据量 | **10-30 分钟** |
| 信噪比 | > 20dB |

### 录音环境要求
- ✅ 安静、无噪音
- ✅ 无背景音乐
- ✅ 使用 UVR5 分离人声（推荐）

### 素材准备流程

```
原始音频 → 人声分离(UVR5) → 降噪 → 切割 → 训练
```

---

## 三、环境配置与安装

### 方式一：Windows 一键整合包（推荐新手）

1. 下载 `RVC-beta.7z`：https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/releases
2. 解压后运行 `go-web.bat`
3. 访问 `http://localhost:7867`

### 方式二：GitHub 源码安装

```bash
# 1. 克隆项目
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI

# 2. 创建环境
conda create -n rvc python=3.10
conda activate rvc

# 3. 安装依赖
pip install -r requirements.txt

# 4. 下载预训练模型
# 从 Hugging Face 下载：
# - hubert_base.pt
# - ./pretrained/ 目录
# - ./uvr5_weights/ 目录
# - ./ffmpeg (Windows需要)
```

### 预模型下载地址

```bash
# Hugging Face 官方仓库
https://huggingface.co/lj1995/VoiceConversionWebUI/tree/main

# 需要下载：
# 1. hubert_base.pt
# 2. pretrained/ 目录所有文件
# 3. uvr5_weights/ 目录所有文件
# 4. ffmpeg.exe + ffprobe.exe (Windows)
```

### 实时变声额外配置

推荐使用 **Voicemeeter** 虚拟声卡：

```
官网：https://voicemeeter.com/
```

---

## 四、训练步骤

### WebUI 训练流程

1. 打开 `http://localhost:7867`
2. 切换到 **「训练」** 标签
3. 设置参数：
   ```
   模型名称：my_voice
   采样率：40k（推荐）
   训练轮数：100-200
   batch_size：自动
   ```
4. 上传音频素材
5. 点击 **「训练模型」**
6. 等待训练完成（约 15-30 分钟）

### 命令行训练

```bash
# 1. 人声分离（使用 UVR5）
python UVr5.py
# 在 WebUI 中操作更方便

# 2. 启动训练
python train.py \
    --model_name my_voice \
    --sample_rate 40000 \
    --epochs 100

# 3. 导出模型
# 在 WebUI 的 "模型管理" 中导出 .pth 文件
```

---

## 五、推理命令

### WebUI 推理

1. 打开 `http://localhost:7867`
2. 切换到 **「推理」** 标签
3. 选择目标音色模型（.pth 文件）
4. 上传或选择输入音频
5. 点击 **「转换」**

### Python API 推理

```python
import os
import soundfile as sf
import numpy as np

# RVC 主要通过 WebUI 运行，Python API 较少直接使用
# 推荐使用 WebUI 的 HTTP API

import requests

# 声音转换 API
def convert_voice(
    input_audio: str,
    model_path: str,
    pitch_change: int = 0,
    output_path: str = "output.wav"
):
    """
    声音转换
    - input_audio: 输入音频路径
    - model_path: RVC 模型路径
    - pitch_change: 音高调整（-12 到 +12）
    - output_path: 输出路径
    """
    with open(input_audio, 'rb') as f:
        files = {'audio': f}
        data = {
            'model': model_path,
            'pitch': pitch_change,
        }
        
        response = requests.post(
            'http://localhost:7867/voice_convert',
            files=files,
            data=data,
            timeout=120
        )
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return output_path
    
    raise Exception(f"转换失败: {response.status_code}")
```

---

## 六、与 OpenClaw Skills 集成

### 集成场景

RVC 主要适合**实时变声**场景，与 OpenClaw 的集成方式：

```
用户 → OpenClaw Agent → RVC WebUI API → 变声音频 → 发送
```

### 集成代码示例

```python
# rvc_skill.py
import requests
import os
import subprocess

class RVCSkill:
    def __init__(self, model_dir="./rvc_models"):
        self.api_url = "http://localhost:7867"
        self.model_dir = model_dir
    
    def list_models(self):
        """列出可用模型"""
        response = requests.get(f"{self.api_url}/models")
        return response.json()
    
    def convert_voice(
        self,
        input_audio: str,
        model_name: str,
        pitch_shift: int = 0,
        output_path: str = None
    ) -> str:
        """
        声音转换
        - input_audio: 输入音频
        - model_name: 模型名称（不含.pth后缀）
        - pitch_shift: 音高偏移（-12到+12）
        """
        if output_path is None:
            output_path = f"/workspace/audio/rvc_{model_name}.wav"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(input_audio, 'rb') as f:
            files = {'audio': f}
            data = {
                'model_name': model_name,
                'pitch': pitch_shift
            }
            
            response = requests.post(
                f"{self.api_url}/voice_convert",
                files=files,
                data=data,
                timeout=300
            )
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return output_path
        
        raise Exception(f"RVC转换失败: {response.status_code}")
    
    def start_webui(self):
        """启动 RVC WebUI（如果未运行）"""
        import sys
        subprocess.Popen(
            [sys.executable, "infer-web.py"],
            cwd=os.getcwd()
        )
```

---

## 七、常见问题与解决

| 问题 | 解决方案 |
|------|----------|
| 转换后音质差 | 确保输入音频清晰无噪音 |
| 音色不像 | 增加训练数据量，增加训练轮数 |
| 实时变声延迟高 | 使用 TensorRT 加速，使用性能更强的 GPU |
| 出现杂音 | 使用 UVR5 预处理去除背景音 |
| 模型太大 | 使用 ONNX 导出压缩模型 |

---

## 八、资源链接

| 资源 | 地址 |
|------|------|
| GitHub | https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI |
| Hugging Face | https://huggingface.co/lj1995/VoiceConversionWebUI |
| 虚拟声卡 | https://voicemeeter.com/ |
| UVR5 | 内置在 RVC WebUI 中 |
