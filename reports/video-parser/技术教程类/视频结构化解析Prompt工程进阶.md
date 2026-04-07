# 技术教程类 — 视频结构化解析Prompt工程进阶

> 🤖 视频解析方法总结Agent（小M）
> 📅 新增日期：2026-04-03（第二周更新）
> 📁 归属分类：技术教程类

---

## 核心工具/API

- **videos_understand**：OpenClaw 内置多模态视频理解，支持自然语言 Prompt 直接驱动
- **audios_understand**：音频/视频语音内容分析，适合无字幕教程
- **images_understand**：帧级图像理解 + OCR，可精准提取代码截图
- **FFmpeg**：帧提取 + 时间戳标记，配合 Prompt 实现精细控制
- **Whisper**：语音转文字，生成带时间戳的字幕 SRT 文件
- **LLM API（GPT-4.1 / Gemini / Qwen）**：结构化 JSON 输出，后处理自动化

---

## 步骤流程

### 流程一：Prompt驱动直接解析（最简路径）

```
视频URL/本地路径 → videos_understand(Prompt) → 结构化文本输出
```

**核心 Prompt 模板（技术教程类）**：
```
你是一位专业的技术教程分析师。请分析这个视频，提取以下结构化信息：

1. 【教程主题】一句话概括
2. 【难度级别】入门/进阶/高级（参考：目标受众假设为有X年经验的开发者）
3. 【技术栈】列出涉及的所有技术/工具/框架
4. 【步骤拆解】按视频时间顺序列出所有操作步骤（格式：时间戳 - 动作 - 目的）
5. 【代码片段】提取所有出现的代码块（标注语言）
6. 【命令清单】提取所有命令行操作
7. 【关键概念】列出解释的技术概念（附视频时间戳）
8. 【常见错误】视频中提到或演示的常见错误及解决方案
9. 【资源链接】视频中提到的所有链接/工具地址
10. 【学习建议】给观众的后续学习建议
```

### 流程二：分阶段精细解析（高质量路径）

```
Step 1: FFmpeg 均匀截帧（每10秒1帧）+ 关键帧提取
Step 2: Whisper 音频转录 → SRT 字幕（带时间戳）
Step 3: videos_understand 逐场景理解帧序列
Step 4: LLM 合并字幕+帧理解 → 结构化 JSON
```

**分场景 Prompt 示例**：
```python
# 伪代码示例
prompts = {
    "intro": "这是什么类型的视频？讲师背景是什么？预期受众是？",
    "demo": "描述这个演示的操作步骤，涉及哪些工具/命令？",
    "code": "这段代码实现什么功能？关键代码行有哪些？",
    "conclusion": "总结本教程的核心要点和可操作性结论",
}

# 每个场景配对应帧
for scene, prompt in prompts.items():
    frames = extract_frames(video, scene_start, scene_end)
    result = videos_understand(frames, prompt)
```

### 流程三：结构化输出自动化（生产路径）

```python
import json, openai

# 定义输出Schema
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "difficulty": {"type": "string", "enum": ["入门", "进阶", "高级"]},
        "steps": {
            "type": "array",
            "items": {
                "timestamp": "string",
                "action": "string",
                "purpose": "string",
                "code_snippets": ["string"]
            }
        },
        "tools": ["string"],
        "key_concepts": [{"concept": "string", "timestamp": "string"}]
    }
}

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role":"user","content": f"{transcript}\n\n请按以下JSON Schema输出：{json.dumps(schema)}"}],
    response_format={"type":"json_object"}
)
```

---

## 适用场景

- **编程教学视频**：提取代码片段 + 命令 + 操作步骤
- **工具使用教程**：提取 UI 操作路径 + 配置参数
- **命令行教程**：Whisper 转录 + 结构化命令清单
- **多步骤操作演示**：FFmpeg 截帧 + 时间戳对齐 + 步骤标注
- **开源项目 Demo**：GitHub README 对照 + 视频帧验证

---

## 避坑指南

### 1. Prompt 过于宽泛 → 输出碎片化
**问题**：直接问"这个视频讲了什么"，输出往往是大段文字，难以结构化利用。
**解决**：使用 JSON Schema 强制约束输出格式，并在 Prompt 中明确分段（章节/步骤/概念）。

### 2. 长视频超出模型上下文 → 关键信息被稀释
**问题**：60 分钟视频整体传给 LLM，开头和结尾信息权重差异大。
**解决**：分场景处理（用时间戳切分），每段独立解析后合并。

### 3. 代码截帧模糊 → OCR 误识别
**问题**：IDE/终端画面压缩后代码字符粘连。
**解决**：FFmpeg 截帧用无损 PNG + 适当分辨率（720p 以上）；代码解析用 `images_understand` 而非 OCR。

### 4. 中文视频 Whisper 识别错误率高
**问题**：技术术语（K8s、gRPC、OOM） Whisper 常识别错误。
**解决**：用 `--initial_prompt` 参数注入术语表；或后期用正则批量替换。

### 5. 视频含多个主题 → 结构化输出混杂
**问题**：一个视频讲多个工具，步骤编号混乱。
**解决**：Prompt 中加入"如果视频包含多个独立教程，请分别输出"的指令。

---

## 按视频类型的 Prompt 模板库

### 模板A：工具安装教程
```
分析这个工具安装教程视频，输出：
1. 目标工具及版本要求
2. 操作系统/环境前提条件
3. 安装步骤（精确命令序列）
4. 常见报错及解决方案（视频中提到的）
5. 验证安装成功的方法
```

### 模板B：API 调用教程
```
从这个 API 教程视频提取：
1. 目标 API 及版本
2. 认证方式（API Key/OAuth/其他）
3. 核心接口调用示例（代码）
4. 请求/响应数据结构
5. 错误处理方式
6. 视频中演示的完整 Demo 代码
```

### 模板C：架构设计教程
```
从这个系统设计/架构视频提取：
1. 系统要解决的问题
2. 核心架构图描述（视频帧内容）
3. 关键技术选型及理由
4. 数据流/调用链路
5. 优缺点分析（讲师观点）
6. 适用场景和局限性
```

---

## 参考链接

- OpenClaw `videos_understand`：内置工具，无需安装
- OpenClaw `audios_understand`：内置工具，适合音频内容
- FFmpeg Whisper 集成：https://ffmpeg.org/doxygen/8.0/filter_8h.html（Whisper 滤镜）
- LLM 结构化输出：https://platform.openai.com/docs/guides structured-outputs
- Awesome-LLMs-for-Video-Understanding：https://github.com/yunlong10/Awesome-LLMs-for-Video-Understanding
