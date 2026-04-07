# 扩散语言模型（dLLM）：非自回归生成的新范式

**版本：v1.0 | 更新日期：2026-03-23**

---

## 一句话概括
扩散语言模型（dLLM）用"逐步去噪"的扩散过程替代"预测下一个token"的自回归范式，让模型学会**全局思考**后再生成文本，从根本上改变了LLM的推理机制。

---

## 背景与动机

### 自回归范式的根本局限

传统LLM（如GPT系列、LLaMA、Qwen）采用**自回归（Auto-Regressive, AR）**生成：

$$\pi_\theta(x_t | x_{<t}) = \prod_{k=1}^{T} \pi_\theta(x_k | x_{<k})$$

这带来了三个根本性问题：

1. **推理延迟与长度成正比**：生成1000个token需要1000次前向传播，无法并行
2. **短期局部最优**：每个token的选择只受前文影响，全局一致性无法保证
3. **重复/矛盾问题**：长序列中容易出现前后矛盾或无意义重复

### 扩散模型的启示

图像生成领域的扩散模型（Stable Diffusion、DALL-E 3）已经证明：**通过逐步去噪，模型可以一次性生成完整的输出**，且全局一致性远优于逐像素生成。

dLLM的核心思想：**将这一范式迁移到文本生成**。

---

## 数学原理

### 核心范式对比

| 维度 | 自回归（AR） | 扩散语言模型（dLLM） |
|------|------------|------------------|
| 生成方式 | 逐token串行 | 多token并行去噪 |
| 训练目标 | 预测下一个token | 预测被掩码的token |
| 推理次数 | T次前向传播 | N次去噪迭代 |
| 全局一致性 | 弱（只看前文） | 强（一次性全局生成） |
| 推理速度 | 慢（串行） | 快（可并行，多步可加速） |

### LLaDA：掩码扩散的开创之作

LLaDA（Large Language Diffusion with mAsking）是首个开源的扩散语言模型，其核心思想来自BERT的掩码语言建模，但扩展到**生成式扩散过程**。

#### 1. 前向过程（Forward Process）：逐步添加掩码

给定完整文本 $x^0$（所有token），前向过程逐步将其替换为掩码token $[M]$：

$$q(x^t | x^{t-1}) = \text{Categorical}(x^{t-1}; p = (1-\alpha_t) \cdot e_{x^{t-1}} + \alpha_t \cdot e_{[M]})$$

等价于每个位置以概率 $\alpha_t$ 被替换为$[M]$。经过 $T$ 步后，$x^T \approx \text{全}[M]$（完全掩码）。

简化实现（一步到位）：
$$x^t = (1 - \sqrt{\bar{\alpha}_t}) \cdot x^0 + \sqrt{\bar{\alpha}_t} \cdot \epsilon, \quad \epsilon \sim \text{Uniform}$$

其中 $\bar{\alpha}_t$ 是噪声调度参数。

#### 2. 反向过程（Reverse Process）：预测被掩码的token

用Transformer $p_\theta$ 预测原始token：

$$p_\theta(x^{t-1} | x^t) = \text{Transformer}_\theta(x^t, t)$$

**训练目标（简化版）：**
$$\mathcal{L} = \mathbb{E}_{t, x^0, \epsilon} \left[ \| \epsilon - \text{Transformer}_\theta(\tilde{x}^t, t) \|^2 \right]$$

其中 $\tilde{x}^t = \sqrt{\bar{\alpha}_t} \cdot x^0 + \sqrt{1-\bar{\alpha}_t} \cdot \epsilon$ 是带噪输入。

#### 3. 推理过程：多步去噪

```python
def generate_lada(model, n_steps=64, temperature=1.0):
    """
    LLaDA的生成过程：多步去噪
    """
    # 从全掩码开始
    x = torch.full((1, seq_len), MASK_TOKEN)
    
    for t in reversed(range(n_steps)):
        # 模型预测当前掩码位置的原始token
        pred = model(x, t)  # 输出每个位置token分布
        
        # 对高置信度位置去掩码（并行）
        probs = F.softmax(pred / temperature, dim=-1)
        confidence, tokens = probs.max(dim=-1)
        
        # 置信度 > 阈值的，去掉掩码
        unmask = confidence > threshold(t)  # 阈值随步数动态调整
        x[unmask] = tokens[unmask]
    
    return x
```

---

## 架构分析：LLaDA的核心设计

### 网络结构

LLaDA直接使用标准Transformer编码器（与BERT相同），而非解码器架构：

```
输入：[M] [M] x_3 [M] x_5 [M] [M]  ← 部分掩码的序列
    ↓
[Transformer Encoder]
    - 双向注意力（vs AR的单向）
    - 位置编码（标准Sinusoidal）
    ↓
输出：每个[M]位置预测的token概率分布
```

**关键设计决策：**

| 设计选择 | LLaDA | 原因 |
|---------|-------|------|
| 注意力 | 双向 | 同时看到所有上下文，全局一致性更强 |
| 架构 | Encoder | 比Encoder-Decoder更简单高效 |
| 掩码策略 | 均匀随机 | 简化训练，最大化每步学习信号 |
| 噪声调度 | 余弦调度 | 从易到难，稳定收敛 |

### 推理加速：Block Parallel Decoding

dLLM最关键的优势之一：**同一层可以并行预测多个位置的token**。这催生了Block Parallel Decoding技术：

```
传统AR（串行）：
Step1: 预测token_1 → token_1
Step2: 预测token_2（依赖token_1）→ token_2
Step3: 预测token_3（依赖token_1,2）→ token_3
...

dLLM（并行）：
Step1: 一次性预测所有[M]位置 → token_1,2,3,...（并行）
Step2: （如果需要多步迭代）
```

理论上，去噪步数 $N=64$ 步 × 每步 $O(1)$ 并行 = 远超AR的速度。

---

## LLaDA2：百亿参数的扩散语言模型（2025-2026）

### 架构升级：从Dense到MoE

蚂蚁集团InclusionAI团队在2025年11月发布了LLaDA2.0系列，首次将扩散语言模型扩展到百亿参数：

| 模型 | 架构 | 参数量 | 激活参数 | 特点 |
|------|------|--------|---------|------|
| LLaDA-8B | Dense | 8B | 8B | 首个开源dLLM |
| LLaDA-MoE-7B-A1B | MoE | 7B | 1B | 稀疏激活 |
| **LLaDA2.0-mini** | MoE | 16B | - | LLaDA2入门版 |
| **LLaDA2.0-flash** | MoE | **100B** | - | 首个百亿参数dLLM |

LLaDA2.0-flash（100B MoE）采用与DeepSeek-V3类似的**细粒度专家路由策略**，但在扩散框架下实现。

### Block Diffusion：加速生成的新技术

LLaDA2引入了**Block Diffusion**机制——将token分组，每组用一个"块token"表示整个块的语义，显著减少去噪步数：

```
传统LLaDA：每步预测1个token，需要N步
Block Diffusion：每步预测B个token，只需N/B步（精度略降）

例如：B=8, N=64 → 只需8步迭代！
```

### 性能基准（dInfer实测数据）

基于dInfer推理框架，在8×H800 GPU上的评测：

| 模型 | HumanEval | GSM8K | IFEval | AVG TPS |
|------|----------|-------|--------|---------|
| LLaDA-MoE-7B | 52.4 | 62.1 | 71.3 | **800+** |
| LLaDA2-flash | 75.3 | 88.6 | 79.2 | **580** |

对比参考：Qwen2.5-3B在vLLM上AVG TPS约为400，LLaDA-MoE快了**2-3倍**且质量相当。

---

## dInfer：扩散语言模型的推理引擎

### 为什么需要专用推理引擎

dLLM的推理流程与AR LLM完全不同：
- AR LLM：逐token生成，vLLM的KV-Cache优化直接适用
- dLLM：多步去噪，每步是完整前向传播，需要专门优化

### dInfer架构

dInfer将推理拆解为四个模块：

```
┌─────────────────────────────────────────┐
│           dInfer 推理框架                │
├──────────┬──────────┬──────────┬─────────┤
│  Model   │ Diffusion│  Decoder │ KV-Cache│
│          │ Iteration│          │ Manager │
│ 基础模型 │ 去噪调度 │ 并行解码 │ 缓存策略 │
│          │ 管理     │ 器       │          │
└──────────┴──────────┴──────────┴─────────┘
```

**1. Model（基础模型）**
- 支持LLaDA、LLaDA-MoE、LLaDA2全系列
- 支持FusedMoE格式（MoE专用高效实现）

**2. Diffusion Iteration Manager（去噪调度）**
- 管理去噪步数（N=8~64可配置）
- 支持Block Diffusion的块掩码策略
- 动态调整置信度阈值

**3. Decoder（并行解码器）**
- Threshold Decoding：置信度 > τ 时去掩码
- 支持动态阈值（τ 随去噪进度变化）
- τ 配置范围：0.80（激进，高速）~ 0.95（保守，高精度）

**4. KV-Cache Manager（缓存管理）**
- `dual`模式：缓存所有中间结果，推理最快
- `prefix`模式：复用前缀缓存，适合多query共享前缀
- `cache`模式：智能缓存，平衡内存与速度

### 后端支持

| 推理框架 | 支持的dLLM | 适用场景 |
|---------|-----------|---------|
| **dInfer（原生）** | LLaDA全系列 | 最佳性能，专用优化 |
| **vLLM（0.10.2）** | LLaDA、LLaDA-MoE | AR用户快速迁移 |
| **SGLang（0.5.3+）** | LLaDA2 | Agent/RAG场景集成 |

---

## 技术对比：dLLM vs AR LLM

| 维度 | AR LLM（GPT风格） | dLLM（LLaDA风格） |
|------|-----------------|-----------------|
| **训练目标** | 下一个token预测 | 掩码token去噪 |
| **推理范式** | 自回归串行 | 扩散并行 |
| **注意力** | 单向因果 | 双向全注意 |
| **全局一致性** | 弱（逐token累积） | 强（一次性全局） |
| **推理速度** | 慢（长度×O(n)） | 快（并行，步数少） |
| **长序列生成** | 重复/矛盾风险高 | 一致性更好 |
| **指令遵循** | 成熟（SFT/RLHF） | 发展中 |
| **生态成熟度** | 极高 | 中等（快速发展中） |
| **适用场景** | 通用对话、代码生成 | 需要全局一致性的场景 |

---

## 应用场景与局限

### 适合dLLM的场景

- **需要全局一致性的任务**：如故事续写、代码补全、翻译（需要全局语义一致）
- **短文本高速生成**：如关键词抽取、分类、实体识别（去噪步数可很少）
- **批处理高吞吐**：多个独立请求并行去噪，吞吐量极高

### 当前局限

1. **指令遵循能力弱于AR模型**：SFT/RLHF生态不如AR成熟
2. **生成质量不稳定**：多步去噪可能产生语义跳跃
3. **生态工具不足**：缺乏dLLM专用的Agent/RAG框架

---

## 思考题

1. **dLLM能否与Agent框架结合？** 推理时的多步去噪如何与工具调用、记忆机制融合？

2. **Block Diffusion的最优块大小是多少？** 是否有理论指导？

3. **dLLM + RL后训练是否可行？** GRPO/Dr.GRPO能否直接应用于扩散模型？

4. **能否将AR和dLLM的优势结合？** 例如：用AR模型生成草稿，再用dLLM做全局优化。

---

## 参考资料

1. [LLaDA论文 (arXiv:2502.09992)](https://arxiv.org/abs/2502.09992) - 首个开源扩散LLM
2. [LLaDA2系列 GitHub](https://github.com/inclusionAI/LLaDA2.X) - 百亿参数MoE扩散模型
3. [dInfer推理框架 GitHub](https://github.com/inclusionAI/dInfer) - 扩散LLM专用推理引擎
4. [SGLang dLLM支持 Issue #12766](https://github.com/sgl-project/sglang/issues/12766) - Block Diffusion LLM RFC
5. [扩散语言模型综述 (CSDN)](https://blog.csdn.net/cxr828/article/details/146029394) - 技术综述

*版本：v1.0 | 更新日期：2026-03-23*
