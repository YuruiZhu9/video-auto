# GPT-4.1-mini 视频理解解析

## 核心工具/API

- **OpenAI GPT-4.1-mini API**：1M token 超大上下文窗口（~1600万字符），支持批量图像输入，是视频理解的核心模型
- **FFmpeg**：视频截帧，支持均匀截帧、关键帧提取、帧率控制
- **OpenCV / PIL**：图像预处理（resize、格式转换），控制 token 消耗
- **OpenAI Python SDK**：API 调用接口

## 步骤流程

### Phase 1：视频预处理

```bash
# 安装依赖
pip install openai opencv-python-headless pillow

# 方案A：均匀截帧（推荐，每N秒1帧）
mkdir -p frames
ffmpeg -i video.mp4 -vf "fps=0.2,scale=640:-1" -q:v 2 frames/frame_%04d.jpg
# fps=0.2 表示每5秒1帧；scale=640 限制宽度640px

# 方案B：只截关键帧（I帧），减少冗余
ffmpeg -i video.mp4 -vf "select='eq(pict_type,PICT_TYPE_I)',scale=640:-1" -vsync vfr frames/frame_%04d.jpg

# 方案C：慢放后截帧（代码闪现类教程专用）
ffmpeg -i video.mp4 -vf "setpts=2.0*PTS,fps=1,scale=640:-1" frames/frame_%04d.jpg
# 2x慢放后每秒1帧，适合代码快速切换场景
```

### Phase 2：批量 API 调用

```python
import os, glob, base64, openai
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# 1. 收集帧（建议每批 20-50 帧）
frame_files = sorted(glob.glob("frames/*.jpg"))[:40]

# 2. 构建消息内容
content_parts = [
    {
        "type": "text",
        "text": """你是一个专业的视频内容分析师。请分析这段视频（由多帧图片组成），
按时间顺序总结核心内容。要求：
1. 识别每个场景的主要事件/动作
2. 标注出现的重要文字、代码、数据
3. 输出JSON格式：{"scenes":[{"time":"开始时间","description":"场景描述","key_content":"关键内容"}]}"""
    }
]

# 3. 添加图像（base64 编码）
for f in frame_files:
    with open(f, "rb") as img:
        img_b64 = base64.b64encode(img.read()).decode("utf-8")
    content_parts.append({
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
    })

# 4. 调用 API
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": content_parts}],
    max_tokens=2048,
    temperature=0.3  # 降低随机性，结果更稳定
)

print(response.choices[0].message.content)
```

### Phase 3：长视频分段处理

```python
import math

def process_long_video(video_path, batch_size=40):
    """分批处理长视频，每批独立分析后合并"""
    frame_files = sorted(glob.glob("frames/*.jpg"))
    total_frames = len(frame_files)
    num_batches = math.ceil(total_frames / batch_size)
    
    all_results = []
    for i in range(num_batches):
        batch = frame_files[i*batch_size:(i+1)*batch_size]
        result = analyze_batch(batch, batch_index=i, total=num_batches)
        all_results.append(result)
    
    # 合并所有批次结果
    final_summary = merge_results(all_results)
    return final_summary
```

## 适用场景

- ✅ **代码闪现类教程**：0.5x 慢放截帧 + GPT-4.1-mini 分析，可捕获一闪而过的代码
- ✅ **需要精细控制的场景**：可指定每帧分析内容，不像 videos_understand 是黑盒
- ✅ **已有 OpenAI API key**：不想额外注册其他服务
- ✅ **OCR + 图像理解双重需求**：PPT/白板/截图识别
- ✅ **超长视频分段分析**：1M token 支持更长的帧序列

## 避坑指南

- **Token 消耗巨大**：50 帧 640p ≈ 60K-80K tokens，注意 API 成本
- **中文 OCR 弱**：中文视频建议用 Gemini 2.0 Flash 或豆包VL
- **音频信息完全丢失**：视频旁白/对话内容需配合 Whisper 补充
- **处理时间长**：50 帧可能需要 30-90 秒，设置合理超时
- **帧选择策略重要**：均匀截帧可能错过关键时刻，建议结合 ReaSon 或 FOCUS
- **结果不稳定**：temperature=0 可改善，建议同时提供帧时间戳参考

## 参考链接

- OpenAI GPT-4.1-mini 文档：https://platform.openai.com/docs/models/gpt-4-1-mini
- OpenAI 视频理解示例：https://developers.openai.com/cookbook/how-to-call-the-api-with-audio-or-video-file
- FFmpeg 截帧文档：https://ffmpeg.org/ffmpeg-all.html
- faster-whisper（GPU 加速版）：https://github.com/SYSTRAN/faster-whisper

---

*最后更新：2026-04-03*
