# Gated DeltaNet：Delta规则与SSM门控的融合

## 一句话概括

Gated DeltaNet由NVIDIA Research提出（ICLR 2025），通过将Delta累积规则注入Mamba-2的SSM门控递归，解决了线性注意力在精确token检索上的软肋，成为2026年Qwen3.5和Kimi Linear构建3:1混合注意力架构的核心组件。

## 背景与动机

### 精确检索困境

Mamba类线性模型的核心问题：**固定大小的状态必须压缩所有历史信息**。当需要从长序列中提取特定位置的内容（如"大海捞针"任务）时：

- Transformer：直接查表，精确无误
- 线性SSM：信息经过N步压缩，精确恢复困难

这是SSM"有损压缩"的本质局限。

### Gated DeltaNet的核心洞察

**全注意力层作为周期性"精度校验点"，Gated DeltaNet负责高效上下文传播。**

3:1混合比（3层Gated DeltaNet → 1层全注意力）的理论依据：在深度推理链中，模型大约每4个token需要一次"精确锚点"来校准确认当前位置和内容。

---

## 数学原理

### 1. Delta规则：累积而非覆盖

**传统SSM状态更新（覆盖式）**：
$$h_t = A_t h_{t-1} + B_t x_t$$

当前状态$h_t$直接由$A_t h_{t-1}$（旧状态缩放）和$B_t x_t$（新输入）**叠加**得到。问题是：当$A_t$的幅值小于1时，历史信息被指数级衰减；当$A_t$接近1时，状态会饱和。

**Delta规则（累积式）**：
$$h_t = h_{t-1} + \Delta h_t$$

只记录**增量（Delta）**，历史信息通过纯加法累积——类似ResNet的残差连接。累积式更新的梯度路径更短，有效避免梯度消失。

### 2. Gated DeltaNet = Delta + 门控 + SSM

Gated DeltaNet将Delta规则、Mamba的门控机制和SSM递归三者融合：

```
标准Mamba SSM:
  h_t = g_t · (A_t · h_{t-1} + B_t · x_t)  # 门控 + 覆盖

Gated DeltaNet:
  h_t = g_t · (h_{t-1} + Δh_t)            # 门控 + 累积
       ↓
     = g_t · h_{t-1} + g_t · Δh_t          # 展开
       ↓
     = g_t · h_{t-1} + (1-g_t) · B_curr · x_curr  # 当Δh_t = B_curr·x_curr - h_{t-1}时
```

更一般的形式：
$$h_t = g_t \odot h_{t-1} + (1 - g_t) \odot \text{SSM\_update}(x_t)$$

其中门控$g_t \in [0,1]^N$（逐通道），平衡"保留历史"和"接受新信息"。

### 3. 与Mamba-2的核心差异

| 特性 | Mamba-2 | Gated DeltaNet |
|------|---------|----------------|
| 状态更新 | $h_t = A_t h_{t-1} + B_t x_t$ | $h_t = h_{t-1} + \Delta h_t$ |
| 信息传递 | 乘法覆盖 | 加法累积 |
| 长期依赖 | 衰减风险 | 累积保真 |
| 精确检索 | 弱（状态压缩） | 强（加法保留更多细节） |
| 与全注意力混合 | 一般 | **专为混合设计** |

---

## 与Mamba-3的对比

| 维度 | Gated DeltaNet | Mamba-3 |
|------|---------------|---------|
| 核心机制 | Delta累积 + 门控 | 梯形离散化 + 复值SSM + MIMO |
| 状态表达 | 实数累积 | **复数旋转** |
| 位置建模 | 位置衰减 | BC RoPE（旋转编码） |
| 精确检索 | 良好（通过全注意力锚点） | 良好（通过复值增强） |
| 最优使用场景 | **混合架构的线性层** | **独立模型骨干** |
| 训练并行性 | ✅ 完全并行 | ✅ 完全并行 |

---

## 架构集成：Qwen3.5的3:1混合设计

```
Qwen3.5层结构（重复N次）:
  [Gated DeltaNet] → [Gated DeltaNet] → [Gated DeltaNet] → [全局MLA] → [SwiGLU] → [FFN]
```

**KV缓存降低75%**的来源：
- 全注意力层：标准KV缓存
- Gated DeltaNet层：线性复杂度的状态传递，**无需KV缓存**
- 3:1配比下，75%的层不产生KV缓存开销

**100万token上下文**的能力来源：
- Gated DeltaNet处理线性复杂度的上下文传播（O(N)）
- 全注意力层周期性"刷新"精确检索能力
- Ring Attention进一步分布式扩展到多卡

---

## 性能基准

| 模型 | 总量参数 | 激活参数 | 上下文 | KV缓存节省 |
|------|---------|---------|-------|-----------|
| Qwen3.5 | 397B (MoE) | 17B | 1M token | 75% |
| Kimi Linear | 48B (MoE) | 3B | 200K token | ~70% |
| Gated DeltaNet-H1（纯线性） | 1B | 1B | 32K | 100% |

---

## 必读论文

1. [Gated Delta Networks (arXiv:2412.06464)](https://arxiv.org/abs/2412.06464) - 原始论文
2. [Mamba-3 (arXiv:2603.15569)](https://arxiv.org/abs/2603.15569) - ICLR 2026 Oral，Mamba团队对Delta规则的隐性采用
3. [Kimi Linear (Moonshot AI)](https://www.moonshot.ai) - KDA设计参考

---

## Qwen3.5的Gated DeltaNet具体实现（新增，2026-03-31）

> Qwen3.5的Gated DeltaNet在NVIDIA原始论文基础上做了重大工程改进，首次在超大规模LLM（397B参数）上验证了混合注意力的可行性。

### Qwen3.5的三大核心改进

| 改进 | 原始Gated DeltaNet | Qwen3.5版本 |
|------|-------------------|-------------|
| Q/K处理 | 标准投影 | **L2归一化** |
| 门控机制 | 单一g门控 | **双重门控（β + g）** |
| 输出门控 | 无 | **RMSNorm + Z-Gate** |

### L2归一化替代核函数

```python
# Qwen3.5版本的Q/K处理
q = F.normalize(q, p=2, dim=-1)   # q / √(Σq_i²)
k = F.normalize(k, p=2, dim=-1)   # k / √(Σk_i²)
```

- 内积有界：q_norm^T · k_norm ∈ [-1, 1]
- 数值稳定：避免了ELU核函数在大值时的饱和问题
- 本质：用向量方向（余弦相似度）而非模长来计算注意力
- 替代了原始版本的ELU核函数φ(x) = elu(x) + 1

### 双重门控机制（Qwen3.5核心创新）

```python
# 第一重：β门控（遗忘决策）
β_t = sigmoid(W_β · x_t)    # 输出∈(0,1)，决定是否保留此token

# 第二重：g门控（精细衰减）
g_t = -exp(A_log) * softplus(W_g · x_t + d_bias^t)
λ_t = β_t * exp(g_t)        # λ ∈ (0, 1)

# 状态更新
S_t = λ_t · S_{t-1} + k_t ⊗ v_t    # 展开：k_t⊗v_t + λ_t·k_{t-1}⊗v_{t-1} + λ_t²·...
```

- β门控：决定"是否记住"（开/关，硬开关）
- g门控：决定"记住多少"（衰减速度，软控制）
- A_log是可训练的衰减基准参数
- 与原始Gated DeltaNet的单一门控相比，**信息选择更精细**

### RMSNorm + Z-Gate输出门控

```python
o_t = RMSNorm(q_t^T · S_t) ⊙ silu(W_z · x_t)
```

- RMSNorm：只除以均方根，不计算均值，节省50%归一化计算
- Z-Gate（silu激活）：对输出做动态缩放，模型学习哪些维度值得关注
- 这是从Mamba-2继承的输出门控设计，在Qwen3.5中被进一步优化

### Causal Conv1D（局部感知的必要补充）

```python
qkv_t = Conv1D(W_qkv · x_t)
# 参数：kernel_size=4，Depthwise，Causal padding=3
```

- 让每个token在进入注意力前，能"看到"最近4个token的局部上下文
- **类比**：Conv1D = "局部扫描仪"，Gated DeltaNet = "全局压缩仪"，两者配合
- Gated DeltaNet的状态更新是递归的，没有Conv1D则无法捕获局部模式

### Qwen3.5完整混合注意力架构

```
Qwen3.5 Block（每4层重复）:
┌─────────────────────────────────────────────────┐
│ Layer 1-3: Gated DeltaNet（线性，O(n)）         │
│   - L2归一化Q/K                                 │
│   - 双重门控（β + g）                           │
│   - Causal Conv1D (kernel=4)                   │
│   - RMSNorm + Z-Gate输出                        │
│                                                 │
│ Layer 4: Gated Attention（全注意力，O(n²)）      │
│   - Q/K Norm归一化                             │
│   - 输出门控                                    │
└─────────────────────────────────────────────────┘
```

---

## 常见误区

1. **"Gated DeltaNet是Mamba的改进版，可以完全替代"** — 错。两者是互补关系：Gated DeltaNet擅长做混合架构的线性层，Mamba-3更适合独立使用
2. **"3:1混合比是固定的"** — 错。这是经验最优值，模型可以根据任务自适应调整（但目前实现是固定的）
3. **"线性注意力不需要全注意力"** — 错。Gated DeltaNet+全注意力的混合设计，本质上是在效率和精度之间做工程权衡
4. **"Qwen3.5的Gated DeltaNet和原始NVIDIA版本相同"** — 错。Qwen3.5版本用L2归一化替代了ELU核函数，增加了双重门控机制，改进了输出门控，是一次重大的工程演进
