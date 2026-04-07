# IndexTTS-2 快速上手

> 版本：v2 | 来源：哔哩哔哩语音团队 | 开源时间：2025年6月

## 核心优势
- 🎭 情感与音色分离控制（业界首创）
- 📊 8维情感向量（Happy/Disgusted/Angry/Melancholic/Sad/Surprised/Afraid/Calm）
- ⏱️ 精确时长控制（有声书场景必备）
- 🆓 完全开源，免费商用

## 安装（一键部署）
推荐使用 OpenBayes 平台：
1. 访问 https://www.openbayes.com
2. 克隆「IndexTTS-2」公共教程
3. 点击运行，等待分配资源
4. 访问API地址，进入Demo页面

## 情感向量控制
```python
result = index_tts.synthesize(
    text="欢迎收听今天的内容。",
    voice_ref="voice.wav",           # 音色来源
    emotion_vector={
        "happy": 0.8,
        "calm": 0.2,
    }
)
```

## 开源地址
- GitHub: https://github.com/IndexTTS
- 教程: https://go.openbayes.com/XutrT
