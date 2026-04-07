# RAG（检索增强生成）架构

## 一句话概括
RAG通过结合外部知识检索与语言模型生成，解决大模型"幻觉"和知识过时问题，是当前LLM应用落地的核心技术方案。

## 背景与动机

### 解决的问题
- **知识过时**：预训练数据截止日期固定，无法获取最新信息
- **幻觉问题**：模型可能生成看似合理但错误的内容
- **领域知识**：通用模型缺乏特定行业的专业知识
- **成本问题**：完全微调大模型成本极高

### 之前方法的不足
- **微调**：需要大量GPU资源，无法频繁更新知识
- **Prompt工程**：上下文窗口有限，无法注入大量知识
- **纯检索**：返回原始文档，用户体验差

### 核心贡献
1. **知识与模型分离**：知识库可独立更新
2. **动态知识注入**：运行时检索最新信息
3. **降低幻觉**：生成内容有据可查

---

## 数学原理

### RAG流程

```
用户查询 → [意图理解] → [知识检索] → [知识整合] → [答案生成]
                 ↓            ↓            ↓
            语义向量    向量数据库    Prompt构造    LLM生成
```

### 检索阶段

#### 密集检索（Dense Retrieval）
```math
\text{score}(q, d) = \text{sim}(E_q(q), E_d(d))
```

其中：
- $E_q$: 查询编码器
- $d$: 文档
- $\text{sim}$: 余弦相似度

#### BM25（稀疏检索）
```math
\text{score}(q, d) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, d) \cdot (k_1 + 1)}{f(q_i, d) + k_1 \cdot (1 - b + b \cdot \frac{|d|}{\text{avgdl}})}
```

### 知识整合

#### 基础RAG Prompt
```
基于以下参考文档回答问题。如果文档中没有相关信息，请说明"未找到相关信息"。

参考文档：
{retrieved_docs}

问题：{question}

回答：
```

#### GraphRAG知识图谱增强

```python
# GraphRAG核心流程
def graph_rag(query, knowledge_graph, llm):
    # 1. 从知识图谱检索相关实体
    entities = kg.query(query)
    
    # 2. 获取实体关联信息
    subgraph = kg.get_subgraph(entities)
    
    # 3. 社区总结
    community_summary = summarize(subgraph)
    
    # 4. 构建增强上下文
    context = build_context(query, subgraph, community_summary)
    
    # 5. 生成答案
    return llm.generate(context)
```

---

## 核心组件

### 1. 文本分块（Chunking）

| 方法 | 优点 | 缺点 |
|------|------|------|
| 固定大小 | 简单 | 可能切断语义单元 |
| 句子级别 | 语义完整 | 块太小，检索质量差 |
| 递归分块 | 自适应 | 实现复杂 |
| 基于语义 | 质量高 | 计算成本高 |

#### 代码实现
```python
def recursive_chunk(text, separators, min_chunk_size=100):
    """递归文本分块"""
    if len(text) < min_chunk_size:
        return [text]
    
    for sep in separators:
        if sep in text:
            parts = text.split(sep)
            chunks = []
            for part in parts:
                chunks.extend(recursive_chunk(part, separators[1:], min_chunk_size))
            return chunks
    
    return [text]
```

### 2. 向量检索

#### 常用向量数据库
- **Milvus**: 开源分布式向量数据库
- **Qdrant**: 高性能向量搜索
- **Chroma**: 轻量级嵌入式
- **Pinecone**: 云服务

#### 检索优化技术
1. **混合检索**：结合稠密+稀疏检索
2. **重排序（Rerank）**：两阶段检索
3. **查询扩展**：补充同义词/相关词

### 3. 知识图谱增强

#### GraphRAG架构
```
原始文档 → [实体抽取] → [关系抽取] → [知识图谱]
                ↓                    ↓
            社区检测            社区总结
                ↓                    ↓
            全局搜索 ←─────── 总结报告
                ↓
            局部搜索 → [实体上下文]
                ↓
            答案生成
```

#### 实体抽取Prompt
```
从以下文本中抽取实体和关系：

文本：{text}

请以以下格式输出：
- 实体：[实体名, 类型]
- 关系：[主体, 关系, 客体]
```

---

## RAG工作流

### 标准RAG流程
```
1. 用户输入Query
2. 向量化Query（Embedding模型）
3. 向量数据库检索Top-K相关文档
4. 文档重排序（如需要）
5. 构造Prompt（Context + Query）
6. LLM生成答案
7. 返回结果
```

### 高级RAG模式

#### 1. 路由模式（Routing）
```python
def router(query):
    """根据查询类型路由到不同处理流程"""
    if is_math_query(query):
        return "calculator"
    elif is_code_query(query):
        return "code_executor"
    elif is_knowledge_query(query):
        return "rag"
    else:
        return "general_llm"
```

#### 2. 查询理解
```python
def query_understanding(query):
    """多维度查询理解"""
    return {
        "original": query,
        "rewritten": rewrite(query),
        "expanded": expand_with_synonyms(query),
        "intent": classify_intent(query),
        "entities": extract_entities(query)
    }
```

#### 3. 迭代RAG
```python
def iterative_rag(query, max_iterations=3):
    """迭代检索-生成-验证"""
    context = []
    for i in range(max_iterations):
        answer = llm.generate(query, context)
        
        # 检查答案是否完整
        if verify(answer):
            break
        
        # 补充检索
        new_docs = retrieve(answer)
        context.extend(new_docs)
    
    return answer
```

---

## 技术对比

| 方面 | 基础RAG | GraphRAG | Agentic RAG |
|------|---------|----------|-------------|
| 知识组织 | 向量块 | 知识图谱 | 工具链 |
| 推理能力 | 弱 | 中 | 强 |
| 多跳问答 | 差 | 好 | 很好 |
| 实现复杂度 | 低 | 中 | 高 |
| 检索质量 | 中 | 高 | 高 |

---

## 代表模型/框架

### 开源RAG框架

| 框架 | 特点 | 适用场景 |
|------|------|----------|
| **LangChain** | 生态丰富 | 快速原型 |
| **LlamaIndex** | 数据友好 | 文档问答 |
| **RAGFlow** | UI友好 | 企业应用 |
| **QAnything** | 网易开源 | 中文场景 |

### GraphRAG（微软）
- **核心**：基于知识图谱的检索增强
- **优势**：全局总结能力强
- **适用**：复杂多跳问答

### RAG+Agent
```python
class RAGAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
    
    def run(self, query):
        plan = self.llm.plan(query, self.tools)
        
        while not plan.is_complete:
            if plan.needs_retrieval:
                docs = self.retrieve(plan.query)
                plan.update_context(docs)
            
            if plan.needs_action:
                result = self.execute(plan.action)
                plan.update_result(result)
            
            plan = self.llm.replan(query, plan)
        
        return plan.final_answer
```

---

## 2025年最新进展

### 1. 长上下文RAG
- **技术**：支持100K+上下文窗口
- **代表**：Gemini 1.5 Pro
- **优势**：减少分块信息损失

### 2. 自适应检索
- **技术**：根据问题难度决定检索深度
- **代表**：Self-RAG
- **优势**：平衡效果与效率

### 3. 多模态RAG
- **技术**：支持图像、视频检索
- **代表**： multimodal-RAG
- **优势**：处理非结构化数据

### 4. RAG评估
- **基准**：RAGAS、ARES、RGB
- **指标**：Faithfulness、Answer Relevance、Context Precision

---

## 常见误区

1. **分块越大越好**：需平衡检索精度与召回
2. **向量维度越高越好**：考虑存储与检索效率
3. **忽视查询理解**：garbage in, garbage out
4. **只关注检索**：生成质量同样重要

---

## 思考题

1. 如何设计一个支持实时更新的RAG系统？
2. 如何处理RAG中的隐私敏感数据？
3. RAG与微调如何选择？

---

## 进阶阅读

### 必读论文
1. [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) - RAG原始论文
2. [Self-RAG: Learning to Retrieve, Generate, and Critique](https://arxiv.org/abs/2310.11511) - 自适应检索
3. [From Local to Global: Knowledge Graph Centric RAG](https://arxiv.org/abs/2404.01037) - GraphRAG

### 开源项目
1. [LangChain](https://github.com/langchain-ai/langchain)
2. [LlamaIndex](https://github.com/run-llama/llama_index)
3. [GraphRAG](https://github.com/microsoft/graphrag)
