# Wan2.7-Video 使用指南（2026年4月最新版）

> 阿里通义最新视频生成模型 | 更新：2026-04-05
> 全模态输入（文本/图像/视频/音频）| 精准视频元素控制

---

## 一、模型介绍

**Wan2.7-Video** 是阿里通义于2026年4月5日发布的最新视频生成模型，是Wan2.7系列的核心产品。

### 核心能力
- **全模态输入**：同时支持文本、图像、视频、音频四种模态作为条件输入
- **元素精准控制**：可删除路人、替换物体、修改背景
- **完整矩阵**：与 Wan2.7-Image 形成完整图文视频生成矩阵
- **高质量输出**：最高支持1080P视频生成

### 适用场景
- AI漫剧 / 短视频创作
- 电商产品展示视频
- 内容编辑与再创作
- 电影级场景预览

---

## 二、API接入（阿里云百炼平台）

### 2.1 获取API Key
1. 访问：[dashscope.console.aliyun.com](https://dashscope.console.aliyun.com)
2. 注册/登录阿里云账号
3. 进入"模型服务" → "API-KEY管理"
4. 创建新的API Key

### 2.2 Python调用示例

```python
import requests
import json
import base64
import os

# 方式一：纯文本生成视频
def text_to_video(prompt, aspect_ratio="16:9", duration=6):
    """纯文本Prompt生成视频"""
    response = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2video/video-synthesis",
        headers={
            "Authorization": f"Bearer {os.getenv('DASHSCOPE_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "wanx2.7-video",
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,  # "16:9" / "9:16" / "1:1"
                "duration": duration  # 6秒或10秒
            },
            "parameters": {
                "guidance_scale": 7.5,
                "negative_prompt": "模糊, 变形, 低质量, 抖动"
            }
        }
    )
    return response.json()

# 方式二：图像+文本生成视频（角色一致性关键）
def image_to_video(image_path, prompt, duration=6):
    """图像作为首帧/参考生成视频"""
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")
    
    response = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis",
        headers={
            "Authorization": f"Bearer {os.getenv('DASHSCOPE_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "wanx2.7-video",
            "input": {
                "image": f"data:image/jpeg;base64,{img_base64}",
                "prompt": prompt,
                "duration": duration
            }
        }
    )
    return response.json()

# 使用示例
result = text_to_video(
    prompt="古风少女在竹林中起舞，白色长裙飘逸，阳光透过竹叶洒下斑驳光影",
    aspect_ratio="16:9"
)
print(result)
```

---

## 三、Prompt撰写技巧

### 3.1 优质Prompt结构

```
[主体] + [动作/场景] + [环境细节] + [光影/氛围] + [风格标签]
```

### 3.2 示例对比

| ❌ 差 Prompt | ✅ 优 Prompt |
|------------|------------|
| 一个女人在走路 | 一位穿红色连衣裙的年轻女性在城市街道上缓步前行，傍晚暖色调路灯亮起，背景是欧式建筑，氛围感十足，电影感构图 |
| 狗在跑步 | 一只金毛犬在海边沙滩上奔跑，海浪拍打沙滩，阳光明媚，超广角镜头，景深效果 |

### 3.3 常用风格标签

```markdown
# 画面风格
写实摄影风格 / 电影感 / 宫崎骏动画风格 / 水墨画风 / 赛博朋克
# 光影
黄金时段光线 / 霓虹灯光 / 逆光剪影 / 柔光
# 镜头语言
特写 / 远景 / 推镜头 / 拉镜头 / 航拍视角 / 跟随镜头
# 画面质感
4K超清 / 景深效果 / 电影级调色 / 8K渲染
```

---

## 四、负面提示词（Negative Prompt）

```python
negative_prompt = "模糊, 变形, 低质量, 抖动, 闪烁, 残缺, 噪点, 摩尔纹, " \
                  "文字, 水印, logo, 截图, 色情内容, 暴力内容"
```

---

## 五、与其他工具的协作工作流

### 5.1 Wan2.7-Video + Midjourney（角色一致性）

```python
# Step 1: 用Midjourney生成角色图
# Prompt: "18-year-old anime girl, front view, detailed face, --seed 12345"

# Step 2: 将角色图传给Wan2.7-Video
result = image_to_video(
    image_path="character_mj.png",
    prompt="同一角色在图书馆窗边读书，阳光洒落，翻动书页的细腻动作",
)

# Step 3: 多次生成不同场景，保持角色一致性
scenes = [
    "角色在咖啡馆喝咖啡",
    "角色在雨中撑伞行走",
    "角色在山顶看日出"
]
for scene in scenes:
    result = image_to_video("character_mj.png", scene)
```

### 5.2 Wan2.7-Video + 语音克隆

```python
# 生成视频后，叠加克隆语音
import subprocess

# 1. 生成视频
video_result = text_to_video("商务人士在办公室演讲，手势自然自信")

# 2. 下载视频后，用FFmpeg添加克隆语音
subprocess.run([
    "ffmpeg", "-i", "generated_video.mp4",
    "-i", "cloned_voice.mp3",
    "-c:v", "copy", "-c:a", "aac",
    "-shortest", "final_output.mp4"
])
```

---

## 六、参数配置推荐

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `aspect_ratio` | 16:9（横版）/ 9:16（竖版）| 根据发布平台选择 |
| `duration` | 6秒（推荐）/ 10秒 | 6秒质量更稳定 |
| `guidance_scale` | 7.5 | 越高越遵循Prompt |
| `resolution` | 1080P | 当前最高支持 |
| `seed` | -1（随机）/ 指定整数 | 固定种子可复现 |

---

## 七、常见问题

**Q：生成的视频模糊怎么办？**
→ 提高 `guidance_scale` 至9.0，在Prompt中加入"4K超清, 电影级画质"

**Q：角色动作不自然？**
→ 使用 `image_to_video` 模式，用Midjourney生成的首帧作为参考

**Q：视频时长不够？**
→ 多次生成不同片段，用FFmpeg拼接成长视频

**Q：国内如何访问？**
→ 阿里云百炼平台直接访问，无需科学上网

---

> 📌 替代工具：Seedance 2.0（豆包）/ PixVerse V6 / Veo 3.1 Lite
> 🤖 由 AI协作视频制作Agent 生成
