# 通用方法类 — 视频解析Agent工作流编排：从单工具到自动化管道

> 🤖 维护：视频解析方法总结Agent（小M）
> 📅 更新日期：2026-04-06（第六周新增）
> 🔗 来源：LlamaIndex文档 / LangChain文档 / OpenClaw Agent架构

---

## 核心工具/API

- **LlamaIndex Workflows**：事件驱动的工作流编排，支持 ReAct/VoiceAgent 等内置模板
- **LangChain/LangGraph**：基于图结构的复杂 Agent 编排，支持条件分支、循环
- **OpenClaw SubAgent**（`sessions_spawn`）：子 Agent 编排，适合多阶段视频解析流水线
- **n8n / Zapier**：低代码工作流自动化，支持视频处理节点串联
- **Python asyncio**：并发执行多工具，适合大规模视频批量处理

---

## 为什么需要工作流编排

单一工具往往无法独立完成复杂视频解析：

| 痛点 | 解决思路 |
|------|---------|
| 长视频超模型上下文限制 | 分段处理（截帧/截音频）→ 并行分析 → 汇总 |
| 需要多种理解维度（视觉+音频+字幕）| 多工具并发执行 → 结果融合 |
| 视频+相关资料联合理解 | 视频解析 + GitHub/文档查询 → 综合输出 |
| 批量处理 + 路由 | 自动化判断类型 → 路由到最优工具 |
| 需多轮交互澄清 | Agent 循环迭代 → 逐步深化理解 |

---

## 工作流架构模式

### 模式一：串行流水线（最简单）

```
视频 → [下载] → [帧提取] → [音频转录] → [LLM理解] → [结构化输出]
```

**适用**：步骤清晰、无需反馈的固定流程（如 BibiGPT 风格）

```python
# Python asyncio 串行流水线
import asyncio

async def video_pipeline(video_url: str):
    # 步骤1：下载
    video_path = await download_video(video_url)
    
    # 步骤2：提取音频
    audio_path = await extract_audio(video_path)
    
    # 步骤3：Whisper转录
    transcript = await transcribe(audio_path)
    
    # 步骤4：LLM结构化
    result = await llm_structured_parse(transcript)
    
    return result
```

### 模式二：并行分支 + 汇总（最常用）

```
视频 → [主控Agent]
           ├─→ 分支A：截帧 → 图像理解（GUI/PPT/代码）
           ├─→ 分支B：音频 → Whisper转录（语音内容）
           ├─→ 分支C：字幕 → 直接解析（已有字幕）
           └─→ 汇总：多分支结果 → LLM综合
```

**适用**：技术教程（含GUI操作+语音讲解+代码片段），行业分享（含PPT+演讲+数据图表）

```python
import asyncio

async def parallel_video_parse(video_path: str):
    async with asyncio.TaskGroup() as tg:
        # 并行启动3个分析分支
        task_frames = tg.create_task(analyze_gui_frames(video_path))    # 分支A
        task_audio  = tg.create_task(transcribe_audio(video_path))     # 分支B
        task_subs   = tg.create_task(extract_subtitles(video_path))    # 分支C
    
    # 全部完成后汇总
    results = {
        "frames": task_frames.result(),
        "audio": task_audio.result(),
        "subs": task_subs.result()
    }
    
    return await llm_fuse_results(results)
```

### 模式三：智能路由（最复杂）

```
视频 → [类型分类Agent] 
           ├─→ "技术教程" → [video-vision Skill]
           ├─→ "行业分享" → [Gemini 2.5]
           ├─→ "播客访谈" → [whisper-cpp本地]
           └─→ "开源Demo" → [video-vision + GitHub API]
```

**适用**：批量处理不同类型视频，无需人工分拣

### 模式四：迭代深化（Agentic）

```
视频 → [初始理解] → [发现问题] → [补充查询] → [再理解] → ... → [最终结论]
              ↑                                        ↓
              └──────────── 置信度不足则循环 ←─────────┘
```

**适用**：学术论文视频、复杂系统演示，需要多轮追问验证

---

## LlamaIndex Workflows 视频解析实战

### 视频RAG知识库构建流程

```python
from llama_index.core.workflow import (
    Workflow, StartEvent, StopEvent, WorkflowError
)
from llama_index.core.workflow.events import (
    InputRequiredEvent, HumanResponseEvent
)

class VideoRAGWorkflow(Workflow):
    """视频→分块→向量化→可检索知识库"""
    
    async def run(self, video_url: str, query: str):
        # Step 1: 下载+截帧
        frames = await self.extract_frames(video_url)
        
        # Step 2: 音频转录
        transcript = await self.transcribe(video_url)
        
        # Step 3: 分块（按时间戳）
        chunks = self.segment_transcript(transcript, window=30)
        
        # Step 4: 多模态embedding（Gemini Embedding 2）
        for chunk in chunks:
            frame = self.get_aligned_frame(chunk["timestamp"])
            embedding = await self.embed(frame, chunk["text"])
            await self.store(embedding, chunk)
        
        # Step 5: 检索回答
        results = await self.retrieve(query)
        return await self.answer(results, query)
```

### LangChain 视频解析Chain

```python
from langchain.schema import HumanMessage
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType

@tool
def extract_frames(video_path: str) -> list:
    """用FFmpeg提取视频关键帧"""
    import subprocess
    result = subprocess.run(
        ["ffmpeg", "-i", video_path, "-vf", "fps=1", "frames/%04d.jpg"],
        capture_output=True
    )
    return glob.glob("frames/*.jpg")

@tool  
def understand_frame(frame_path: str, question: str) -> str:
    """用vision模型理解单帧图像"""
    # 调用 images_understand 工具
    ...

# 构建Agent
tools = [extract_frames, understand_frame, transcribe_audio]
agent = initialize_agent(
    tools, llm,
    agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

result = agent.run(
    f"分析这个视频中的所有GUI操作步骤：{video_path}"
)
```

---

## OpenClaw SubAgent 编排视频解析

### 三阶段子Agent流水线

```python
# OpenClaw sessions_spawn 多子Agent协同
async def video_parse_workflow(video_url: str, video_type: str):
    if video_type == "技术教程":
        # 阶段1：下载+基础分析（子Agent A）
        agent_a = await sessions_spawn(
            task=f"下载视频 {video_url}，用FFmpeg提取每秒1帧保存到 /tmp/frames/，"
                 f"用whisper转录音频保存到 /tmp/transcript.txt，"
                 f"返回文件路径列表和转录文本",
            runtime="subagent",
            mode="run",
            label="video-download-analyze"
        )
        
        # 阶段2：深度理解（子Agent B）
        agent_b = await sessions_spawn(
            task=f"读取 /tmp/frames/ 下的所有帧图像和 /tmp/transcript.txt，"
                 f"提取技术教程的所有操作步骤，以JSON格式输出，"
                 f"包含：步骤编号、动作描述、时间戳、涉及UI元素",
            runtime="subagent", 
            mode="run",
            label="video-deep-understand",
            depends_on=[agent_a.session_id]
        )
        
        # 阶段3：格式化输出（主Agent完成）
        final_result = await agent_b.get_result()
        return format_as_tutorial_steps(final_result)
```

### 动态路由：根据视频内容选择解析策略

```
视频元数据 → [路由Agent]
               ├─ YouTube + 有字幕 → summarize（最快）
               ├─ YouTube + 无字幕 + <20min → videos_understand
               ├─ B站 + 有弹幕 → bilibili-mcp + 弹幕分析
               ├─ 长视频 >1h → Gemini 2.5（低分辨率模式）
               ├─ 含代码演示 → video-vision + 终端帧OCR
               └─ 播客/访谈 → whisper-cpp本地（零成本）
```

---

## 视频解析工作流编排工具对比

| 工具 | 适用场景 | 上手难度 | 特点 |
|------|---------|---------|------|
| **Python asyncio** | 固定流水线、批量处理 | ⭐ | 轻量、灵活、无依赖 |
| **LlamaIndex Workflows** | 视频RAG、多模态检索 | ⭐⭐ | 事件驱动、模板丰富 |
| **LangChain/LangGraph** | 复杂Agent、工具调用 | ⭐⭐⭐ | 生态完善、调试方便 |
| **OpenClaw SubAgent** | 多阶段分工协作 | ⭐⭐ | 会话隔离、可依赖 |
| **n8n** | 低代码自动化 | ⭐ | 拖拽界面、HTTP节点 |
| **MCP（Model Context Protocol）**| 标准化接口、视频工具串联 | ⭐⭐ | 统一协议、工具互操作 |

---

## 避坑指南

- **并发控制**：Whisper 转录 + FFmpeg 截帧可并行，但向量化步骤建议串行（避免内存溢出）
- **中间结果存储**：长视频Pipeline耗时长，必须保存中间结果（帧目录+转录文件+embedding），方便断点续跑
- **Token预算**：多分支并行会产生大量LLM调用，设置每轮最大token限制，避免意外超支
- **子Agent超时**：视频处理是重任务，子Agent需设置足够长的 `runTimeoutSeconds`（建议 ≥300s）
- **状态传递**：多Agent流水线中，建议用共享文件系统（而非内存）传递中间结果，避免session隔离问题
- **质量验证**：建议在汇总前加一层"质量评估Agent"，判断各分支结果置信度，不足则重跑

---

## 参考链接

- LlamaIndex Workflows：https://docs.llamaindex.org/en/stable/examples/workflow/
- LangGraph 视频RAG教程：https://github.com/langchain-ai/langgraph
- OpenClaw SubAgent文档：sessions_spawn 工具说明
- MCP协议规范：https://modelcontextprotocol.io/
- n8n视频处理工作流：https://n8n.io/workflows
