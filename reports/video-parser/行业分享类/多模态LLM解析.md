# 行业分享类 - 多模态 LLM 视频解析方案

## 核心工具/API

- **GPT-4o / GPT-4o-mini（OpenAI）**
  - 能力：原生多模态，支持图像帧 + 音频 + 文本联合理解
  - API：https://api.openai.com/v1/chat/completions
  - 特点：视频帧序列理解，可输出结构化 JSON

- **Gemini 1.5 / 2.0（Google）**
  - 能力：1000万 token 上下文，支持直接上传视频文件
  - API：https://generativelanguage.googleapis.com/
  - 特点：超长视频理解，上传视频文件 URL 即可

- **智谱 GLM-4V（国内）**
  - 能力：中文优化，支持视频帧分析
  - API：https://open.bigmodel.cn/
  - 特点：免费额度充足，适合中文内容

- **通义千问 Qwen-VL（阿里）**
  - 能力：视觉语言模型，视频帧理解
  - API：https://modelscope.cn/
  - 特点：开源版本可本地部署

- **videos_understand（OpenClaw 内置）**
  - 能力：封装多模态 LLM，支持本地视频路径 / URL
  - 最大并发：10 个视频

## 步骤流程

### 方案A：OpenClaw videos_understand（推荐）
```python
# OpenClaw 内置工具，自动选择最优多模态模型
videos_understand(
  videos_info=[
    {
      "file": "/path/to/video.mp4",
      "prompt": """请深度分析这个行业分享视频，输出：
1. 核心观点（3-5条）
2. 行业趋势洞察
3. 关键技术/产品亮点
4. 数据指标（如有）
5. 演讲者背景推测"""
    }
  ]
)
```

### 方案B：GPT-4o 多帧序列理解
```python
import base64, requests, cv2, json

def extract_frames(video_path, num_frames=10):
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = max(1, total // num_frames)
    frames = []
    for i in range(num_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * interval)
        ret, frame = cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            frames.append(base64.b64encode(buffer).decode())
    cap.release()
    return frames

def analyze_video_gpt4o(video_path, api_key):
    frames = extract_frames(video_path, num_frames=8)
    content = [{"type": "text", "text": "分析这个行业分享视频的核心内容"}]
    for f in frames:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{f}"}})
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": content}],
              "response_format": {"type": "json_object"}, "max_tokens": 2000}
    )
    return json.loads(response.json()["choices"][0]["message"]["content"])
```

### 方案C：Gemini 1.5 直接视频上传
```python
import requests
# Gemini 支持直接传视频文件或 URL
# 智谱 AI 调用示例（免费额度）
url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
headers = {"Authorization": "Bearer YOUR_ZHIPU_API_KEY"}
data = {
    "model": "glm-4v-plus",
    "messages": [{"role": "user", "content": [
        {"type": "video_url", "video_url": {"url": "https://example.com/video.mp4"}},
        {"type": "text", "text": "请分析这个视频的行业洞察和关键数据"}
    ]}]
}
response = requests.post(url, headers=headers, json=data)
print(response.json())
```

### 方案D：完整 Pipeline（FFmpeg → Whisper → LLM）
```python
import subprocess, os

def full_pipeline(video_path, output_dir="output/"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: 提取关键帧
    print("Step 1: 提取关键帧...")
    frames = extract_smart_keyframes(video_path, max_frames=8)
    for idx, frame in frames:
        cv2.imwrite(f"{output_dir}frame_{idx:04d}.jpg", frame)
    
    # Step 2: 音频转写
    print("Step 2: 音频转写...")
    subprocess.run(["ffmpeg", "-i", video_path, "-vn",
        "-acodec", "libmp3lame", "-q:a", "2",
        f"{output_dir}audio.mp3"], check=True)
    
    # Step 3: 多模态 LLM 分析
    print("Step 3: LLM 分析...")
    # 用 videos_understand 或 OpenAI GPT-4o API
```

## 适用场景

- ✅ 行业趋势分析（Keynote 演讲类视频）
- ✅ 投资/融资路演视频结构化
- ✅ 竞品发布会视频分析
- ✅ 行业峰会/论坛视频摘要
- ✅ 产品发布会视频关键信息提取
- ✅ 播客/访谈视频核心观点提取

## 避坑指南

- **坑1：视频太长超出模型上下文**
  - 解决：先用 FFmpeg 等间隔提取 8-10 帧
  - Gemini 1.5 支持长视频，可直接传
  - 长视频分段处理，每段单独分析再合并

- **坑2：帧质量差（模糊/反光/角度差）**
  - 解决：提取帧时增加 -q:v 2 保证质量
  - 跳过纯文字/纯背景帧（浪费 token）

- **坑3：API 费用高**
  - 解决：国内用智谱 GLM-4V（免费额度）
  - 帧数控制在 8 帧以内
  - 优先用 Whisper 提取文字，再用 LLM 分析（更便宜）

- **坑4：视频含敏感内容**
  - 解决：注意 API 服务商内容政策，人脸/声音数据需合规

## 参考链接

- OpenAI GPT-4o：https://platform.openai.com/docs/guides/vision
- Google Gemini：https://ai.google.dev/docs/gemini_api
- 智谱 GLM-4V：https://open.bigmodel.cn/
- 通义千问 Qwen-VL：https://modelscope.cn/models/Qwen/Qwen-VL
- OpenClaw videos_understand：内置工具（无需安装）
