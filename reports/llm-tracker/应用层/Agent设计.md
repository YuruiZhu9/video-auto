# Agent架构设计

## 一句话概括
Agent是大模型通过工具调用与环境交互的智能系统架构，是2025年LLM应用落地的核心范式。

## 背景与动机

### 解决的问题
- **能力边界**：大模型无法直接访问外部世界
- **任务复杂度**：单一模型调用无法完成复杂任务
- **实时性**：无法获取最新信息和执行实际操作

### 之前方法的不足
- **Prompt工程**：静态指令，无法动态适应
- **CoT（思维链）**：仅限推理，无法行动
- **API调用**：固定模式，缺乏灵活性

### 核心贡献
1. **工具扩展**：突破模型自身能力边界
2. **规划能力**：复杂任务分解执行
3. **反思机制**：自我纠错和迭代优化

---

## 数学原理

### Agent决策过程

#### ReAct架构
```math
\text{Agent}(s_0) = \text{Generate} \rightarrow \text{Act} \rightarrow \text{Observe} \rightarrow \dots
```

```
思考 (Thought) → 行动 (Action) → 观察 (Observation) → ...
```

#### 工具选择概率
```math
P(\text{tool}_i | \text{context}) = \text{softmax}(W \cdot h_{\text{context}})_i
```

其中 $h_{\text{context}}$ 是当前上下文的向量表示

### 规划（Planning）

#### CoT + Tool Use
```
问题：帮我查北京明天天气并订机票

分解：
1. 查询天气 → tool: weather, city: 北京, date: 明天
2. 如果天气好 → tool: flight_booking, from: 任意, to: 北京
3. 返回结果
```

#### ReWoo架构
- **Planner**：生成子任务和依赖图
- **Worker**：执行子任务
- **Solver**：汇总结果

---

## 核心组件

### 1. 工具系统（Tools）

#### 工具定义
```python
from typing import Any, Callable

class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: dict
    ):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
    
    def execute(self, **kwargs) -> Any:
        """执行工具并返回结果"""
        return self.function(**kwargs)
    
    def to_json_schema(self) -> dict:
        """生成JSON Schema供LLM使用"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
```

#### 常用工具类型
| 类型 | 功能 | 示例 |
|------|------|------|
| 搜索 | 网络信息检索 | Google, Bing |
| 数据库 | 结构化数据查询 | SQL, API |
| 计算 | 数学运算 | Python执行器 |
| 文件 | 读写操作 | 文件系统 |
| 函数 | 业务逻辑 | 自定义API |

### 2. 记忆系统（Memory）

#### 记忆层次
```
┌─────────────────────────────────────┐
│           长期记忆                   │
│     （向量数据库/知识图谱）           │
├─────────────────────────────────────┤
│           工作记忆                   │
│       （当前任务上下文）              │
├─────────────────────────────────────┤
│           短期记忆                   │
│      （对话历史/最近N轮）             │
└─────────────────────────────────────┘
```

#### 记忆实现
```python
class Memory:
    def __init__(self, vector_store=None):
        self.short_term = []  # 对话历史
        self.working = {}     # 工作记忆
        self.long_term = vector_store  # 向量存储
    
    def add(self, content, memory_type="short"):
        """添加记忆"""
        if memory_type == "short":
            self.short_term.append(content)
        elif memory_type == "long":
            self.long_term.add(content)
    
    def retrieve(self, query, top_k=5):
        """检索相关记忆"""
        return self.long_term.search(query, top_k)
    
    def summarize(self):
        """压缩记忆"""
        # 使用LLM总结关键信息
        return llm.summarize(self.short_term)
```

### 3. 规划器（Planner）

#### 任务分解
```python
class Planner:
    def __init__(self, llm):
        self.llm = llm
    
    def decompose(self, task):
        """将复杂任务分解为子任务"""
        prompt = f"""
        将以下任务分解为可执行的子任务：
        
        任务：{task}
        
        要求：
        1. 每个子任务应该是原子性的
        2. 标注任务之间的依赖关系
        3. 明确每个任务的输入输出
        
        输出格式：
        - 子任务1：[任务描述] (依赖: 无)
        - 子任务2：[任务描述] (依赖: 子任务1)
        """
        return self.llm.generate(prompt)
    
    def create_plan(self, task):
        """创建执行计划"""
        subtasks = self.decompose(task)
        return self.build_dag(subtasks)
```

### 4. 反射器（Reflector）

```python
class Reflector:
    def __init__(self, llm):
        self.llm = llm
    
    def evaluate(self, action_result, expected):
        """评估行动结果"""
        if self.is_successful(action_result, expected):
            return "success"
        elif self.can_fix(action_result):
            return "fixable"
        else:
            return "failed"
    
    def反思(self, trajectory):
        """反思整个执行轨迹"""
        prompt = f"""
        反思以下执行轨迹：
        
        {trajectory}
        
        分析：
        1. 哪些地方做得好？
        2. 哪些地方可以改进？
        3. 下次遇到类似任务应该如何处理？
        """
        return self.llm.generate(prompt)
```

---

## Agent架构模式

### 1. ReAct（推理+行动）

```python
class ReActAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
    
    def run(self, query, max_steps=10):
        history = []
        
        for step in range(max_steps):
            # 1. 推理
            thought = self.llm.think(query, history)
            
            # 2. 决定行动
            action = self.llm.decide_action(thought, self.tools)
            
            # 3. 执行行动
            if action.type == "finish":
                return action.result
            
            observation = action.execute()
            
            # 4. 记录观察
            history.append({
                "thought": thought,
                "action": action,
                "observation": observation
            })
        
        return "达到最大步数限制"
```

### 2. Toolformer

- **自监督学习**：模型学习何时调用工具
- **API调用生成**：自动生成工具调用示例
- **无侵入性**：不影响原始模型能力

### 3. Reflexion

```python
class ReflexionAgent:
    def __init__(self, llm, tools, evaluator):
        self.llm = llm
        self.tools = tools
        self.evaluator = evaluator
    
    def run(self, task):
        trajectory = []
        
        while not self.evaluator.is_complete(task, trajectory):
            # 生成行动
            action = self.llm.generate_action(task, trajectory)
            
            # 执行行动
            result = action.execute(self.tools)
            
            # 评估结果
            evaluation = self.evaluator.evaluate(result)
            
            # 反思
            if evaluation.failed:
                reflection = self.llm.reflect(task, trajectory, result)
                trajectory.append({
                    "action": action,
                    "result": result,
                    "reflection": reflection
                })
            else:
                trajectory.append({
                    "action": action,
                    "result": result
                })
        
        return self.construct_final_answer(trajectory)
```

### 4. Agentic RAG

```python
class AgenticRAG:
    def __init__(self, llm, retriever, tools):
        self.llm = llm
        self.retriever = retriever
        self.tools = tools
    
    def run(self, query):
        # 1. 判断是否需要检索
        if not self.needs_retrieval(query):
            return self.llm.generate(query)
        
        # 2. 制定检索计划
        plan = self.plan_retrieval(query)
        
        # 3. 迭代检索
        context = []
        for step in plan.steps:
            docs = self.retriever.retrieve(step.query)
            context.extend(docs)
            
            # 4. 判断是否需要补充检索
            if self.needs_more(context, query):
                continue
        
        # 5. 生成答案
        return self.llm.generate(query, context)
```

---

## 工具调用机制

### OpenAI Function Calling

```python
# 定义工具
functions = [
    {
        "name": "get_weather",
        "description": "获取指定城市的天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                },
                "date": {
                    "type": "string", 
                    "description": "日期，格式YYYY-MM-DD"
                }
            },
            "required": ["city"]
        }
    }
]

# 调用
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "北京明天天气怎么样？"}
    ],
    functions=functions
)

# 解析结果
if response.choices[0].message.function_call:
    tool_call = response.choices[0].message.function_call
    result = call_function(tool_call.name, tool_call.arguments)
```

### LangChain Agent

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain import hub

# 加载提示模板
prompt = hub.pull("hwchase17/openai-functions-agent")

# 创建Agent
agent = create_openai_functions_agent(llm, tools, prompt)

# 执行
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10
)

result = agent_executor.invoke({"input": "北京明天天气怎么样？"})
```

---

## 评估指标

| 指标 | 描述 | 评估方式 |
|------|------|----------|
| **任务完成率** | 是否达成目标 | 人工/自动 |
| **工具使用准确率** | 是否正确选择工具 | 统计 |
| **反思有效性** | 反思是否改进行动 | 对比实验 |
| **执行效率** | 步数/时间消耗 | 统计 |
| **幻觉率** | 工具调用错误率 | 统计 |

---

## 2025年最新进展

### 1. Multi-Agent系统
- **架构**：多个Agent协作分工
- **代表**：ChatDev、AutoGen
- **优势**：处理复杂任务

### 2. Agent编译
- **技术**：将Agent流程固化为可执行代码
- **代表**：MetaGPT
- **优势**：可复用、可调试

### 3. Agent评估基准
- **AgentBench**：综合评估Agent能力
- **WebArena**：Web环境Agent评估
- **AgentBoard**：细粒度能力评估

### 4. 自主Agent
- **技术**：Agent自主规划执行
- **代表**：Claude Computer Use、OpenAI Operator
- **优势**：端到端任务执行

---

## 常见误区

1. **工具越多越好**：关注工具质量而非数量
2. **忽视错误处理**：Agent需要健壮的异常处理
3. **过度依赖LLM规划**：简单任务不应过度复杂化
4. **忽视安全**：工具调用需要权限控制

---

## 思考题

1. 如何设计一个能够持续学习改进的Agent？
2. Agent如何处理不确定性高的任务？
3. 如何保证Agent的安全性？

---

## 进阶阅读

### 必读论文
1. [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) - ReAct原始论文
2. [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) - 工具学习
3. [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) - 反思机制
4. [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) - Agent评估

### 开源项目
1. [LangChain Agents](https://github.com/langchain-ai/langchain)
2. [AutoGen](https://github.com/microsoft/autogen)
3. [MetaGPT](https://github.com/geekan/MetaGPT)
4. [ChatDev](https://github.com/OpenBMB/ChatDev)
