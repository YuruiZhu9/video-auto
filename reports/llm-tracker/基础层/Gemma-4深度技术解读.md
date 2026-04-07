# Google Gemma 4 深度技术解读

> 版本：v1.0 | 更新日期：2026-04-04 | 来源：[HuggingFace Blog](https://huggingface.co/blog/gemma4) / [IT之家](https://www.ithome.com/0/935/537.htm) / [Google DeepMind](https://deepmind.google/models/gemma/gemma-4/)

---

## 一句话概括

Gemma 4 是 Google DeepMind 于 2026 年 4 月 2 日发布的开源大模型系列，首次全面采用 Apache 2.0 许可证，包含 E2B/E4B/26B MoE/31B 四种规格，在 LMSYS Arena 开源榜单中以 31B 稠密模型拿下**全球开源第三**，刷新了"单位参数智能水平"的天花板。

---

## 背景与动机

Google 在 2025 年 11 月发布 Gemini 3 旗舰闭源模型后，开源社区一直在等待对应的开源版本。Gemma 4 正是基于 **Gemini 3 同源技术**打造，将顶级推理能力带入开源生态。

与前代 Gemma 3 相比，Gemma 4 的核心动机是：
1. **架构创新**：引入交替局部+全局注意力、双RoPE、层嵌入复用等多项新技术
2. **许可开放**：从 Gemma 3 的 Gemma Terms 切换为 **Apache 2.0**，彻底解除商业限制
3. **端侧突破**：让手机、Raspberry Pi 等极低算力设备也能运行前沿级 AI

---

## 数学原理

### 1. 交替局部-全局注意力机制（Alternating Local-Global Attention）

这是 Gemma 4 最核心的架构创新。

**传统 Transformer 的问题**：标准 Multi-Head Attention 的计算复杂度为 O(N²)，其中 N 为序列长度。当处理 256K token 的长上下文时，注意力矩阵的存储和计算代价极其昂贵。

**Gemma 4 的解决方案**：

```
输入序列 → [局部滑动窗口层] → [全局注意力层] → [局部滑动窗口层] → [全局注意力层] → ...
             ↓                                   ↓
        局部信息聚合                         全局依赖建模
        O(N·W) 复杂度                        O(N²) 复杂度
```

- **局部层（Sliding Window Attention）**：每个 token 只关注周围 W 个 token（小模型 512，大模型 1024），复杂度 O(N·W)
- **全局层（Full Context Attention）**：标准的全局注意力，覆盖整个序列
- 两种层**交替排列**，如 `[Local → Global → Local → Global → ...]`

**直观理解**：就像人类的阅读方式——既关注当前段落（局部），也理解整篇文章的主旨（全局）。

### 2. 双 RoPE（Dual Rotary Position Embedding）

Gemma 4 在不同层使用不同的旋转位置编码策略：

| 注意力层类型 | RoPE 策略 | 目的 |
|------------|----------|------|
| 局部滑动窗口层 | 标准 RoPE | 维持局部相对位置感知 |
| 全局注意力层 | 比例 RoPE（Proportional RoPE） | 支持更长上下文的外推 |

**标准 RoPE 公式**：
```
RoPE(x_m, m) = x_m · R(θ_m)
```
其中旋转矩阵 `R(θ_m)` 由频率 θ_m = base^(-2i/d) 决定，i 为维度索引。

**比例 RoPE 的关键改进**：通过调整频率分布，使全局层的旋转角度随序列长度成比例变化，从而在长序列上避免"位置信息崩溃"。

### 3. 每层嵌入复用（Per-Layer Embeddings, PLE）

传统 LLM 中，只有第一层和最后一层有 embedding table，中间层只处理 hidden states。

**PLE 的创新**：在每一层解码器的残差连接处，注入一个额外的 embedding 信号——即**第二 embedding table**。

```
Layer N 的输入 = Layer (N-1) 的 hidden state
                    + Embedding_table[token_id] × 门控系数
```

**作用**：
- 每一层都能获得"这个 token 是什么"的直接信息（token identity component）
- 避免深层网络中的语义漂移问题（semantic drift）
- 等效增加了有效参数量，但不增加推理计算量

### 4. 共享 KV Cache

传统 Transformer 中，每一层的 K（Key）和 V（Value）都需要独立计算和存储。

**共享 KV Cache** 的设计：后面的层直接复用前面层的 KV states，跳过重复的 K/V 投影计算。

```
Layer 1:  x → W_q·x, W_k·x, W_v·x → Q₁, K₁, V₁
Layer 2:  x → W_q·x → Q₂
          K₂ = K₁,  V₂ = V₁（直接复用）
```

**内存节省**：以 31B 模型为例，KV 投影参数约占总参数的 10-15%，通过复用可将这部分开销降低约 50%。

---

## 代码实现

### 交替注意力层 PyTorch 实现

```python
import torch
import torch.nn as nn
import math

class AlternatingAttentionLayer(nn.Module):
    """
    交替局部-全局注意力层
    局部层: Sliding Window Attention (SWA)
    全局层: Full Multi-Head Attention (MHA)
    """
    def __init__(self, d_model, n_heads, window_size, use_global=True):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.window_size = window_size
        self.use_global = use_global
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        # RoPE: 预计算旋转矩阵
        self._register_rope_cache()
        
    def _register_rope_cache(self):
        """预计算 RoPE 所需的 cos/sin 值"""
        d = self.d_k
        # 标准 RoPE 频率
        self.register_buffer(
            "rope_cache",
            self._build_rope_cache(d)
        )
    
    def _build_rope_cache(self, d):
        theta = 10000.0
        freqs = 1.0 / (theta ** (torch.arange(0, d, 2).float() / d))
        return freqs
    
    def apply_rope(self, x, seq_len):
        """应用旋转位置编码"""
        # x shape: [batch, n_heads, seq_len, d_k]
        x_even = x[..., ::2]
        x_odd = x[..., 1::2]
        freqs = self.rope_cache[:x_even.shape[-1]]
        
        x_even_emb = x_even * freqs.cos() - self._rotate_half(x_even) * freqs.sin()
        x_odd_emb = x_odd * freqs.cos() + self._rotate_half(x_odd) * freqs.sin()
        
        x = torch.stack([x_even_emb, x_odd_emb], dim=-1).reshape_as(x)
        return x
    
    def _rotate_half(self, x):
        x1, x2 = x[..., :x.shape[-1]//2], x[..., x.shape[-1]//2:]
        return torch.cat([-x2, x1], dim=-1)
    
    def local_attention(self, Q, K, V, mask=None):
        """局部滑动窗口注意力 - O(N·W) 复杂度"""
        seq_len = Q.shape[2]
        window = self.window_size
        
        # 创建局部注意力掩码（因果 + 窗口限制）
        if mask is None:
            mask = torch.tril(torch.ones(seq_len, seq_len, device=Q.device))
        
        # 只保留窗口内的注意力
        k_range = torch.arange(seq_len, device=Q.device)
        q_range = k_range.unsqueeze(1)
        local_mask = (q_range - k_range).abs() < window
        
        # Q·K^T 计算并应用掩码
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        scores = scores.masked_fill(~local_mask.unsqueeze(0).unsqueeze(0), float('-inf'))
        
        attn_weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(attn_weights, V)
        return output
    
    def global_attention(self, Q, K, V, mask=None):
        """标准全局注意力 - O(N²) 复杂度"""
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        attn_weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(attn_weights, V)
        return output
    
    def forward(self, x, is_global_layer=True):
        """
        x: [batch, seq_len, d_model]
        is_global_layer: True = 全局注意力层, False = 局部注意力层
        """
        B, S, D = x.shape
        
        # QKV 投影
        Q = self.W_q(x).view(B, S, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(x).view(B, S, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(x).view(B, S, self.n_heads, self.d_k).transpose(1, 2)
        
        # 应用 RoPE
        Q = self.apply_rope(Q, S)
        K = self.apply_rope(K, S)
        
        # 选择注意力类型
        if is_global_layer or not self.use_global:
            attn_output = self.global_attention(Q, K, V)
        else:
            attn_output = self.local_attention(Q, K, V)
        
        # 合并多头并输出
        attn_output = attn_output.transpose(1, 2).contiguous().view(B, S, D)
        return self.W_o(attn_output)
```

### 复杂度对比

| 注意力类型 | 参数量 | 时间复杂度 | 空间复杂度（KV Cache） | 适用场景 |
|-----------|--------|-----------|---------------------|---------|
| 标准 MHA | O(D²) | O(N²) | O(N·D) | 通用 |
| Flash Attention | O(D²) | O(N²) | O(N·D) | 训练/推理加速 |
| **Gemma 4 交替** | O(D²) | **O(N·W·L)** | **O(N·D)（共享后约50%节省）** | 长上下文 |

其中 W = 窗口大小（512/1024），L = 层数

---

## 架构分析

### Gemma 4 全系列规格

```
┌─────────────────────────────────────────────────────────┐
│                    Gemma 4 模型系列                       │
├──────────────┬──────────┬──────────┬────────────────────┤
│    型号      │ 参数量   │ 上下文   │      架构类型        │
├──────────────┼──────────┼──────────┼────────────────────┤
│ E2B          │ 2.3B有效 │ 128K    │ 稠密 + 交替注意力   │
│              │ 5.1B词表  │         │                    │
├──────────────┼──────────┼──────────┼────────────────────┤
│ E4B          │ 4.5B有效 │ 128K    │ 稠密 + 交替注意力   │
│              │ 8.0B词表  │         │                    │
├──────────────┼──────────┼──────────┼────────────────────┤
│ 26B A4B      │ 26B总参  │ 256K    │ MoE (4B激活/26B总)  │
│  (MoE)       │ 4B激活   │         │ 稀疏激活            │
├──────────────┼──────────┼──────────┼────────────────────┤
│ 31B          │ 31B稠密  │ 256K    │ 稠密 + 交替注意力   │
│  (Dense)     │          │         │ LMSYS #3全球开源    │
└──────────────┴──────────┴──────────┴────────────────────┘
```

### 26B MoE 架构详解

Gemma 4 26B MoE 是系列中最有趣的变体：
- **总参数量**：26B（分布在多个"专家"中）
- **每次推理激活**：仅 **4B 参数**（约为总参数的 15%）
- **稀疏比**：约 1:6.5，即每生成一个 token，只激活约 15% 的参数
- **延迟优势**：推理速度接近 4B 模型，但能力接近 26B 模型

### 数据流图

```
输入 Token
    ↓
[Embedding Table] → 获得 token 表征
    ↓
[Decoder Layer × N] → 交替执行: Local Attention → Global Attention
    ↓                      (每层复用 Embedding Table - PLE)
[Norm + Output Proj]
    ↓
[语言模型头] → 预测下一个 token
```

---

## 代表模型性能对比

### 核心基准测试

| 基准测试 | Gemma 4 31B | Gemma 4 26B MoE | Gemma 4 E4B | Gemma 4 E2B | 说明 |
|---------|:----------:|:-------------:|:----------:|:----------:|------|
| **MMLU Pro** | 85.2% | 82.6% | 69.4% | 60.0% | 高级知识理解 |
| **AIME 2026** | 89.2% | 88.3% | 42.5% | 37.5% | 数学竞赛（2026新题） |
| **GPQA Diamond** | 84.3% | 82.3% | 58.6% | 43.4% | 研究生级科学题 |
| **BigBench Extra Hard** | 74.4% | 64.8% | 33.1% | 21.9% | 超难综合推理 |
| **LiveCodeBench v6** | 80.0% | 77.1% | 52.0% | 44.0% | 代码生成 |
| **Codeforces ELO** | 2150 | 1718 | 940 | 633 | 编程竞赛评分 |
| **MMMU Pro** | 76.9% | 73.8% | 52.6% | 44.2% | 多模态理解 |
| **MATH-Vision** | 85.6% | 82.4% | 59.5% | 52.4% | 数学视觉 |
| **MRCR 8-Needle 128K** | 66.4% | 44.1% | 25.4% | 19.1% | 长上下文大海捞针 |

### LMSYS Arena 表现

| 模型 | Arena Score | 排名 |
|------|:---------:|------|
| GPT-4o / Claude 等闭源旗舰 | ~1400+ | Top 5 |
| **Gemma 4 31B** | **~1452** | **全球开源第3** |
| **Gemma 4 26B MoE** | **~1441** | **全球开源第6** |
| 其他开源模型 | <1400 | - |

### 与竞品横向对比（31B 规模）

| 指标 | Gemma 4 31B | Llama 4 34B | Mistral 8x22B | 备注 |
|------|:---------:|----------:|:----------:|------|
| 许可证 | **Apache 2.0** | Llama 4 Terms | Apache 2.0 | Gemma 最开放 |
| 上下文 | 256K | 128K | 128K | Gemma 最长 |
| 多模态 | 原生 | 原生 | 需额外训练 | - |
| 端侧支持 | E2B/E4B | 无 | 无 | Gemma 独有 |
| 代码能力 | 80.0% (LCB) | - | - | 领先同规模 |

---

## 部署与生态

### 部署方式

| 平台 | 支持情况 |
|------|---------|
| **Transformers + bitsandbytes/PEFT/TRL** | ✅ 原生支持 |
| **llama.cpp (GGUF)** | ✅ 量化版本可用 |
| **MLX (Apple Silicon)** | ✅ TurboQuant 优化 |
| **Transformers.js (WebGPU)** | ✅ 浏览器内运行 |
| **Mistral.rs** | ✅ 高性能推理 |
| **SGLang** | ✅ 长上下文优化 |
| **ONNX** | ✅ 边缘设备支持 |

### Apache 2.0 许可证的意义

这是 Google 首次在开源模型上采用 Apache 2.0 许可，对比前代的"Gemma Terms"：
- ✅ **允许商用**：无需申请，无使用量限制
- ✅ **允许修改**：可自由改动模型
- ✅ **允许分发**：可作为产品分发
- ✅ **专利授权**：包含相关专利授权
- ✅ **无商标限制**：不要求保留 Google 商标

---

## 技术对比

| 方面 | Gemma 3 | Gemma 4 | 改进幅度 |
|------|---------|---------|---------|
| 许可证 | Gemma Terms | **Apache 2.0** | 🔄 完全开放 |
| 最大上下文 | 128K | **256K** | ↑ 2× |
| 注意力机制 | 标准 MHA | **交替局部+全局** | 🔄 架构革新 |
| 位置编码 | RoPE | **双 RoPE** | 🔄 适配不同层 |
| 端侧模型 | Gemma 3n (2GB RAM) | **E2B/E4B** | ↑ 能力大幅提升 |
| 数学推理(AIME) | ~50% | **89.2%** | ↑ +39pp |
| 代码能力 | ~60% | **80.0%** | ↑ +20pp |

---

## 常见误区

### 误区 1：E2B/E4B 只是小模型
**纠正**：E2B/E4B 虽然参数量小，但引入了完整的交替注意力架构，在**效率-性能权衡**上远超前代同等规模的模型。E4B 的 MMLU Pro（69.4%）超过了许多 7B 模型。

### 误区 2：MoE 模型推理很快
**纠正**：MoE 的"快"是相对于同等能力的稠密模型而言。Gemma 4 26B MoE 虽然推理时只激活 4B 参数，但**总参数量仍是 26B**，加载到 GPU 显存就需要 52GB（bf16），这比加载一个 4B 模型复杂得多。

### 误区 3：Apache 2.0 = 无任何限制
**纠正**：Apache 2.0 不要求开源训练代码和数据，仍有隐私合规风险，企业使用需注意。

---

## 进阶阅读

### 必读论文
1. [Gemma 4 Technical Report](https://huggingface.co/blog/gemma4) - 官方技术解读
2. [RoPE: Rotary Position Embedding](https://arxiv.org/abs/2104.09864) - 位置编码基础
3. [Flash Attention V2](https://arxiv.org/abs/2307.08691) - 高效注意力实现
4. [Mixtral 8x22B MoE](https://mistral.ai/news/mixtral-8x22b/) - MoE 架构参考

### 开源实现
1. [Google Gemma GitHub](https://github.com/google-deepmind/gemma) - 官方代码
2. [Transformers Gemma 4 Support](https://huggingface.co/docs/transformers/en/main_classes/models#gemma) - HuggingFace 集成

---

## 思考题

1. **架构层面**：Gemma 4 的交替注意力在局部层使用固定窗口大小。你认为动态窗口大小（如根据层深自适应）会带来什么改进？

2. **部署层面**：E2B/E4B 模型针对手机和 Raspberry Pi 优化。在实际部署中，量化方案（INT8 vs INT4）和推理引擎的选择如何影响端侧性能？

3. **许可层面**：Apache 2.0 虽然开放，但仍基于 Google 的闭源训练数据。这和 Truly Open 模型（如 OLMo 2）相比，有什么根本区别？
