# ReFusion：并行解码扩散语言模型

**版本：v1.0 | 更新日期：2026-03-24 | 来源：ICLR 2026**

---

## 一句话概括
ReFusion通过**槽级并行解码**和**KV缓存复用**两大创新，首次让掩码扩散语言模型在推理速度上显著超越自回归模型（2.33倍加速），同时将性能差距缩小到接近ARM水平，是扩散语言模型从"理论可行"走向"工业实用"的关键里程碑。

---

## 背景与动机

### 扩散语言模型的两大痼疾

掩码扩散模型（Masked Diffusion Models, MDM）在文本生成中面临两个根本瓶颈：

**痼疾1：KV缓存完全失效**

自回归语言模型（ARM）的推理效率核心依赖KV缓存：生成第`t`个token时，只需计算第`t`个位置的Q（Query），而K（Key）和V（Value）可直接复用前`t-1`步的结果。形式上：

$$\text{Attention}(Q_t, K_{1:t}, V_{1:t}) = \text{Softmax}\left(\frac{Q_t K_{1:t}^\top}{\sqrt{d}}\right) V_{1:t}$$

这里 $K_{1:t}$ 和 $V_{1:t}$ 是**缓存的**，只有 $Q_t$ 需要从头计算。

但MDM在每个去噪迭代中，序列中的所有位置都处于活跃状态——已知token和mask token混合在一起，**无法区分"已完成"和"待生成"**。因此每次迭代都必须重新计算全部位置的K和V，KV缓存完全失效。

设序列长度为 $L$，去噪步数为 $T$，嵌入维度为 $d$，头数为 $h$：

| 模型类型 | 单步计算量 | T步总计算量 |
|---------|-----------|------------|
| ARM（AR模型）| $O(L \cdot d)$ | $O(T \cdot L \cdot d)$ |
| 传统MDM | $O(L^2 \cdot d)$ | $O(T \cdot L^2 \cdot d)$ |

当 $L=512, T=50$ 时，传统MDM的计算量是ARM的约50倍。

**痼疾2：token组合空间指数爆炸**

MDM的学习目标是最大化观测数据的似然：

$$\mathcal{L} = \mathbb{E}_{x \sim p_{\text{data}}}\left[-\log p_\theta(x)\right]$$

在掩码设置下，这要求模型学习"给定部分token，预测完整token序列"的条件分布。对于一个长度为 $n$ 的序列，每个位置有 $V$（词表大小）种取值，完整的token组合空间是 $V^n$ —— **指数级不可计算（intractable）**。

即便只预测活跃的 $k$ 个mask位置，组合数也有 $C(n,k) \cdot V^k$，同样是指数级。

---

## 数学原理

### 核心思想：将token空间映射到槽空间

ReFusion的核心洞察是：**槽的数量是固定的（由模型架构决定），与序列内容无关**。

设模型使用 $N$ 个槽（slots）来组织信息，则所有可能的槽排列（permutation）构成的空间大小为 $N!$。

```
举例：
N = 8 时，N! = 40320（可学习）
而token组合空间：V^L，当V=32000, L=8时 = 6.87×10³⁵

比例：N!/V^L ≈ 10^-30
```

**这不是一个近似近似，而是一个精确的维度压缩**：通过将"token内容"的学习（指数空间）转化为"槽填充顺序"的学习（阶乘空间），ReFusion将不可学习的问题变为可学习的。

### Slot级马尔可夫链建模

ReFusion将生成过程建模为槽序列的**顺序填充**，每步选择下一个待填充的槽：

$$p(\mathbf{s}) = \prod_{t=1}^{N} p(s_t | s_1, s_2, \ldots, s_{t-1})$$

其中 $\mathbf{s} = (s_1, s_2, \ldots, s_N)$ 是槽的填充顺序，$s_t \in \{1, 2, \ldots, N\} \setminus \{s_1, \ldots, s_{t-1}\}$。

**与AR模型对比**：
- AR模型：$p(x_t | x_{<t})$，词表大小 $V$，每次预测一个token
- ReFusion：$p(s_t | s_{<t})$，槽集合大小 $N!$，每次决定一个填充顺序

### KV缓存复用：数学机制

设第 $i$ 个槽的内容为 $c_i \in \mathbb{R}^d$，一旦某个槽被标记为"已填充"，其内容 $c_i$ **在整个后续生成过程中保持不变**，对应的Key和Value向量也随之固定：

$$\text{KV}_\text{cached} = \{K(c_i), V(c_i) | \text{槽}i \text{已填充}\}$$

设当前有 $k$ 个活跃（未填充）槽，它们的索引集合为 $\mathcal{A}$。当前去噪迭代只需计算：

$$\text{Attention}_{\text{hybrid}} = \text{Attention}(Q_\mathcal{A}, K_{\overline{\mathcal{A}}}, V_{\overline{\mathcal{A}}}, K_\mathcal{A}, V_\mathcal{A})$$

其中：
- $K_{\overline{\mathcal{A}}}, V_{\overline{\mathcal{A}}}$：已填充槽的K/V → **来自缓存**，O(1) 复用
- $K_\mathcal{A}, V_\mathcal{A}$：活跃槽的K/V → **需要计算**，规模为 $|\mathcal{A}| \ll N$

这与标准多头注意力的区别在于：**ReFusion允许对已填充位置使用缓存K/V，对活跃位置重新计算QKV**，而标准Attention无法区分这两种位置。

---

## 代码实现

### 槽管理核心代码

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SlotManager:
    """
    管理槽的填充状态和KV缓存
    N: 槽的总数（通常等于序列最大长度）
    """
    def __init__(self, num_slots: int, device='cuda'):
        self.N = num_slots
        self.filled = [False] * num_slots  # 槽是否已填充
        self.kv_cache = {}                   # 已填充槽的KV缓存
        self.slot_contents = [None] * num_slots  # 已填充槽的内容
    
    def mark_filled(self, slot_idx: int, content: torch.Tensor):
        """标记槽为已填充，缓存其KV"""
        self.filled[slot_idx] = True
        self.slot_contents[slot_idx] = content
        # 实际实现中，这里会计算并存储K和V向量
        # K = W_K @ content, V = W_V @ content
        self.kv_cache[slot_idx] = {
            'k': F.linear(content, self.W_K),  # shape: [d]
            'v': F.linear(content, self.W_V)
        }
    
    def get_active_indices(self):
        """返回所有未填充槽的索引"""
        return [i for i, filled in enumerate(self.filled) if not filled]
    
    def get_cached_kv(self):
        """获取所有已填充槽的KV，用于注意力计算"""
        cached_indices = [i for i, filled in enumerate(self.filled) if filled]
        if not cached_indices:
            return None, None
        K = torch.stack([self.kv_cache[i]['k'] for i in cached_indices])
        V = torch.stack([self.kv_cache[i]['v'] for i in cached_indices])
        return K, V

# 前向传播中的使用示例
def refusion_forward(model, x, slot_manager):
    # 1. 获取未填充槽的索引
    active_indices = slot_manager.get_active_indices()
    
    # 2. 对未填充槽计算注意力（实时计算）
    active_kv = model.compute_kv_for_slots(x, active_indices)
    
    # 3. 获取已填充槽的KV（来自缓存，复用，无需重算）
    cached_K, cached_V = slot_manager.get_cached_kv()
    
    # 4. 拼接并计算混合注意力
    if cached_K is not None:
        K = torch.cat([cached_K, active_kv['k']], dim=0)
        V = torch.cat([cached_V, active_kv['v']], dim=0)
    else:
        K, V = active_kv['k'], active_kv['v']
    
    # 5. 计算注意力输出
    Q = active_kv['q']
    attn_output = scaled_dot_product_attention(Q, K, V)
    
    return attn_output
```

### 间插式解码循环

```python
def refusion_generate(model, prompt_tokens, max_len=512, num_steps=50):
    """
    ReFusion的生成循环
    model: 预训练的ReFusion模型（基于Qwen3-8B）
    prompt_tokens: 输入token列表
    """
    slot_manager = SlotManager(num_slots=max_len)
    
    # Step 1: 将prompt填入初始槽
    for i, token in enumerate(prompt_tokens):
        embedding = model.embed_token(token)
        slot_manager.mark_filled(i, embedding)
    
    # Step 2: 迭代去噪
    for step in range(num_steps):
        active_indices = slot_manager.get_active_indices()
        if not active_indices:
            break  # 所有槽都已填充
        
        # 槽级并行：同时对所有活跃槽进行去噪
        noise_level = 1.0 - step / num_steps  # 线性衰减
        
        # 计算当前活跃槽的去噪预测
        for slot_idx in active_indices:
            # 用扩散模型预测该槽应填充的内容
            predicted_content = model.denoise_slot(
                slot_idx, 
                slot_manager,  # 传入当前槽管理器（包含KV缓存）
                noise_level
            )
            
            # 判断是否收敛（预测内容变化足够小）
            if model.is_converged(predicted_content, slot_idx):
                # 槽内AR填充：展开为多个token
                tokens = model.ar_fill(predicted_content)
                for t in tokens:
                    slot_manager.mark_filled(
                        slot_idx + len(tokens),  # 顺序填充后续槽
                        model.embed_token(t)
                    )
            else:
                # 未收敛，更新槽内容（但不标记为已填充）
                slot_manager.update_slot(slot_idx, predicted_content)
    
    # Step 3: 解码所有槽为token序列
    return slot_manager.decode_to_tokens()
```

### 计算复杂度对比

```python
# 对比：传统MDM vs ReFusion（生成L个token）

def traditional_mdm_complexity(L, T, d):
    """传统MDM：每步O(L²·d)，T步"""
    return T * L * L * d

def refusion_complexity(L, T, d, k_avg=2):
    """
    ReFusion：每步只有k_avg个活跃槽需要计算
    T步之后，所有槽都填充完毕
    """
    # 初始化：O(L·d)
    init = L * d
    # 去噪迭代：每步只有k_avg个活跃槽
    # 假设槽内平均k_avg个token
    denoise = sum([k_avg * (L - t*k_avg) * d for t in range(T)])
    # AR填充：每槽O(k_avg·d)
    ar_fill = L * k_avg * d
    return init + denoise + ar_fill

# 数值示例
L, T, d = 512, 50, 4096
trad = traditional_mdm_complexity(L, T, d)
refus = refusion_complexity(L, T, d, k_avg=4)

print(f"传统MDM: {trad:,} FLOPS")
print(f"ReFusion: {refus:,} FLOPS")
print(f"加速比: {trad/refus:.1f}×")
# 输出示例：加速比约 15-20×
```

---

## 架构分析

### 数据流图

```
输入 Prompt
    ↓ [Token Embedding]
槽初始化 (Slot Initialization)
    ↓
┌─────────────────────────────────────────────┐
│           迭代去噪循环（最多T步）              │
│                                              │
│  [活跃槽集 A] ──→ [扩散去噪模块] ──→ [收敛判断] │
│       ↑                ↓                    │
│       └──[KV缓存] ←── [已填充槽集 F] ←┘       │
│                                              │
│  若收敛 → 槽内AR填充 → 新增已填充槽            │
│  若未收敛 → 更新槽内容 → 继续下一迭代          │
└─────────────────────────────────────────────┘
    ↓ [所有槽填充完毕]
Token解码 (Detokenization)
    ↓
输出文本
```

### 与此前扩散语言模型的架构对比

```
LLaDA/MMDM:
prompt → [全量并行去噪 × T步] → 输出
          ↑
      所有token同时参与
      无KV缓存，每步O(L²)

ReFusion:
prompt → [槽初始化] → [活跃槽去噪 ↔ 已填充槽KV复用] × T步 → 输出
          ↑
      活跃槽和已填充槽分开处理
      有KV缓存，每步O(k·L)，k ≪ L
```

### 关键组件

| 组件 | 作用 | 实现要点 |
|------|------|---------|
| **槽管理器（SlotManager）** | 跟踪填充状态、存储KV缓存 | 状态数组 + KV字典 |
| **扩散去噪模块** | 对活跃槽进行去噪 | 基于标准diffusion/unet |
| **收敛判断器** | 决定槽是否足够稳定 | 预测方差/变化幅度阈值 |
| **槽内AR填充** | 将收敛槽展开为token序列 | 轻量AR模型 |
| **序列重组织（Sequence Reorganization）** | 将收敛槽重新排序到前面 | 关键工程实现 |

---

## 代表模型

### ReFusion-Qwen3-8B
- **基础模型**：Qwen3-8B
- **参数规模**：~8B（扩散架构适配后）
- **训练数据**：GSAI-ML/ReFusion（HuggingFace开源）
- **Benchmark表现**：
  - MBPP（代码）：+34% vs 此前最优MDM
  - HumanEval：与同规模ARM性能接近
- **推理速度**：2.33× 同规模ARM，18× 此前最优MDM
- **开源地址**：https://huggingface.co/GSAI-ML/ReFusion

---

## 技术对比

| 维度 | LLaDA | MMDM | Mercury | Seed Diffusion | **ReFusion** |
|------|-------|------|---------|----------------|--------------|
| 发布时间 | 2024 | 2024 | 2024 | 2026.03 | **2026.03** |
| KV缓存 | ❌ | ❌ | ❌ | ❌ | ✅ **完整复用** |
| 解码方式 | 全序列并行 | 全序列并行 | token级并行 | 全序列并行 | **槽级并行** |
| 学习目标 | token预测 | token预测 | token预测 | token预测 | **槽排列** |
| 推理速度 | < ARM | < ARM | ~ARM | 5.4× ARM | **2.33× ARM** |
| 代码质量 | 中等 | 中等 | 良好 | 优秀 | **优秀** |
| 学术发表 | arXiv | arXiv | arXiv | 技术报告 | **ICLR 2026** |
| 开源 | ✅ | ✅ | ✅ | ❌ | ✅ |

---

## 进阶阅读

### 必读论文
1. [ReFusion: arXiv:2512.13586](https://arxiv.org/abs/2512.13586) — 完整论文
2. [LLaDA: Large Language Model with Diffusion Architecture](https://arxiv.org/abs/2405.15071) — MDM基础
3. [Seed Diffusion技术报告](https://seed.bytedance.com/seed_diffusion) — 工业级实现

### 开源实现
1. [ReFusion官方GitHub](https://github.com/ML-GSAI/ReFusion) — 含训练/推理/评估代码
2. [HuggingFace: GSAI-ML/ReFusion](https://huggingface.co/GSAI-ML/ReFusion) — 模型权重
3. [HuggingFace: GSAI-ML/ReFusion数据集](https://huggingface.co/datasets/GSAI-ML/ReFusion) — 训练数据

---

## 常见误区

**误区1：ReFusion完全放弃了自回归**  
✅ 实际上ReFusion采用**间插式设计**（inter-slot diffusion + intra-slot AR），在槽内仍使用AR填充。完全放弃AR仅适用于短文本场景。

**误区2：KV缓存复用可以零成本获得**  
✅ KV缓存复用的前提是**槽级粒度**的并行解码。只有当槽的填充顺序可以被打散重排时，已填充槽才能与活跃槽解耦。这需要架构层面的特殊设计。

**误区3：扩散语言模型即将取代AR模型**  
✅ 目前的SOTA结果仍显示ReFusion与同规模Qwen3-8B存在一定性能差距。扩散模型的优势在于**特定场景的推理速度**，而非全面超越。

---

## 思考题

1. **架构创新**：ReFusion的槽排列空间学习将问题从指数空间降到阶乘空间。但当N=64或N=128时，N!仍然很大。如何进一步压缩？

2. **工程落地**：KV缓存复用的关键在于"哪些槽可以提前标记为已填充"。能否设计一个更激进的提前标记策略，在保证质量的前提下进一步提高速度？

3. **多模态扩展**：ReFusion目前只验证了文本场景。能否将槽级KV复用思想迁移到多模态扩散模型（如DiT for Video）？图像/视频的槽与文本的槽有何本质区别？

4. **与MoE的结合**：专家混合（MoE）已经在AR模型中证明了效率优势。能否将MoE引入扩散语言模型的槽级解码中，让不同专家处理不同类型的槽？
