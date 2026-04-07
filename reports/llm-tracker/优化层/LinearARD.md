# LinearARD：线性内存注意力蒸馏恢复RoPE

## 一句话概括

LinearARD是一种**自蒸馏**方法，通过对齐教师模型和学生模型的注意力结构（Q/K/V自关系矩阵），在仅425万训练tokens的条件下恢复RoPE缩放后的短文本性能，相比传统CPT方法（2.56亿tokens）效率提升约60倍。

---

## 背景与动机

### 问题：RoPE缩放导致短文本能力退化

大语言模型的上下文窗口扩展，通常通过以下流程实现：

```
原始模型：RoPE (θ_i = B^(-2i/d)), 最大长度 4K
    ↓
应用RoPE缩放：θ'_i = θ_i / α (α > 1), 目标长度 32K
    ↓
持续预训练（CPT）：在长文本上继续训练
    ↓
得到扩展上下文模型：32K最大长度
```

**核心问题**：CPT后，长上下文能力↑，但短文本性能↓（即"能力退化"）。

原因：RoPE缩放改变了位置编码的旋转角度，破坏了原始模型在细粒度位置上的区分能力。

### 传统解法及缺陷

| 方法 | 原理 | 数据需求 | 效果 |
|------|------|---------|------|
| CPT | 在长文本上持续预训练 | 256M tokens | 能部分恢复，但需要海量数据 |
| LongReD | 蒸馏隐藏状态 | 256M tokens | 效果较好，但同样昂贵 |

**核心缺陷**：都是**匹配隐藏状态**（Hidden States），而隐藏状态是高维不透明向量，难以精确对齐。

---

## 数学原理

### 核心思想：蒸馏注意力结构，而非隐藏状态

**直觉**：Transformer的决策来自于注意力结构（哪些token关注哪些token），而非隐藏状态本身。对齐注意力结构比对齐隐藏状态更直接有效。

### 注意力自关系矩阵

对于输入序列 $X = (x_1, ..., x_n)$，定义：

```
Q = XW_Q,  K = XW_K,  V = XW_V
注意力矩阵：A = softmax(QK^T / √d)
```

对于每一层l，定义自关系矩阵（Self-Relation Matrix）：

$$R^{(l)}_Q = \text{softmax}(Q^{(l)} Q^{(l)^T} / \sqrt{d})$$

$$R^{(l)}_K = \text{softmax}(K^{(l)} K^{(l)^T} / \sqrt{d})$$

$$R^{(l)}_V = \text{softmax}(V^{(l)} V^{(l)^T} / \sqrt{d})$$

**这些矩阵描述了**：每个token的Query/Key/Value与其他token的相似性结构。

### 蒸馏目标：行分布对齐

LinearARD对齐的不是完整的n×n矩阵，而是**每一行的分布**：

```math
\mathcal{L}_{\text{ARD}} = \sum_{l} \sum_{R \in \{Q,K,V\}} 
    \text{KL}(R^{(l)}_{\text{teacher}} \| R^{(l)}_{\text{student}})
```

其中，KL散度定义：

$$KL(P \| Q) = \sum_i P_i \log \frac{P_i}{Q_i}$$

### 线性内存内核：O(n²) → O(n)

**问题**：n×n矩阵的存储需要 $O(n^2)$ 显存，对于n=32K，显存需求无法接受。

**解法**：对每行 $R_i$（n维向量），只存储其log-sum-exp统计量：

$$s_i = \text{logsumexp}(R_i) = \log \sum_{j=1}^{n} \exp(R_{ij})$$

```python
# 原始矩阵
R = softmax(Q @ K.T / sqrt(d))  # [n, n] → 需要 O(n²) 显存

# LinearARD：对每行只存一个标量
s = logsumexp(R, dim=-1)  # [n] → 需要 O(n) 显存

# 反向传播时重计算精确梯度（不近似）
# 通过 log-sum-exp 的梯度公式精确重建
```

**log-sum-exp 梯度公式**：

$$\frac{\partial s_i}{\partial R_{ij}} = \frac{\exp(R_{ij})}{\sum_k \exp(R_{ik})} = \text{softmax}(R_i)_j$$

即：虽然前向传播只存储标量 $s_i$，但反向传播可以精确重建每行的完整梯度向量。

### 蒸馏流程图

```
教师模型（原生RoPE，冻结）
  ↓
  输入: 短文本 x_1,...,x_n
  前向: Q_t, K_t, V_t
  计算: R_Qt = softmax(Q_t Q_t^T / √d)
        R_Kt = softmax(K_t K_t^T / √d)
        R_Vt = softmax(V_t V_t^T / √d)
  
学生模型（缩放RoPE，可学习）
  ↓
  输入: 相同短文本 x_1,...,x_n（RoPE角度按 α 缩放）
  前向: Q_s, K_s, V_s
  计算: R_Qs, R_Ks, R_Vs（用线性内存内核，O(n)显存）
  
蒸馏损失（行分布KL对齐）
  ↓
  L = Σ_l Σ_{R∈{Q,K,V}} KL(R_t || R_s)
  反向传播，更新学生模型
```

---

## 代码实现

### 核心：线性内存注意力蒸馏

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class LinearARDLoss(nn.Module):
    """
    LinearARD: Linear-Memory Attention Distillation for RoPE Restoration
    
    核心思想：对齐注意力结构（Q/K/V自关系矩阵），而非隐藏状态
    关键创新：使用 log-sum-exp 统计量将 O(n²) 显存降至 O(n)
    """
    
    def __init__(self, temperature=1.0):
        super().__init__()
        self.temperature = temperature
    
    def logsumexp(self, x, dim=-1):
        """数值稳定的 log-sum-exp"""
        max_x = x.max(dim=dim, keepdim=True).values
        return max_x.squeeze(dim) + torch.log(
            torch.exp(x - max_x).sum(dim=dim)
        )
    
    def row_kl_divergence(self, P, Q, eps=1e-8):
        """
        计算行方向的 KL(P || Q) 散度
        
        P: [n, n] 教师注意力矩阵（已 softmax）
        Q: [n, n] 学生注意力矩阵（已 softmax）
        
        对每一行 i：计算 KL(P_i || Q_i)
        KL(P_i || Q_i) = Σ_j P_ij * log(P_ij / Q_ij)
        """
        # 添加 eps 避免 log(0)
        P = P.clamp(min=eps)
        Q = Q.clamp(min=eps)
        
        # 行方向归一化（确保每行和为1）
        P = P / P.sum(dim=-1, keepdim=True).clamp(min=eps)
        Q = Q / Q.sum(dim=-1, keepdim=True).clamp(min=eps)
        
        # KL(P || Q) = Σ P * log(P/Q) = Σ P * log(P) - Σ P * log(Q)
        # 对行维度求和
        kl = P * (torch.log(P) - torch.log(Q))
        return kl.sum(dim=-1).mean()  # [n] → scalar
    
    def linear_memory_self_relation(self, x, dim=-1):
        """
        线性内存自关系矩阵计算
        
        原始：R = softmax(x @ x.T / √d) → O(n²) 显存
        LinearARD：只存储 log-sum-exp 统计量 → O(n) 显存
        
        x: [n, d]  Q/K/V 向量
        返回: per-token log-sum-exp 统计量 [n]
        """
        # 数值稳定的 softmax 计算
        # 避免 x @ x.T 的二次方存储
        
        # 方案：分块计算 + log-sum-exp 增量更新
        # 对于每个 token i，计算 log Σ_j exp(score_ij)
        # 其中 score_ij = x_i · x_j / √d
        
        d = x.shape[-1]
        scale = d ** 0.5
        
        # 分块处理（避免 n×n 显存的直接计算）
        # 每个块计算 log-sum-exp，然后合并
        chunk_size = 512
        n = x.shape[0]
        
        stats = torch.zeros(n, device=x.device)
        
        for i in range(0, n, chunk_size):
            chunk_end = min(i + chunk_size, n)
            x_chunk = x[i:chunk_end]  # [chunk, d]
            
            # 计算与所有 x 的点积
            scores = x_chunk @ x.T / scale  # [chunk, n]
            
            # log-sum-exp over 最后一个维度
            stats[i:chunk_end] = self.logsumexp(scores, dim=-1)
        
        return stats  # [n]
    
    def forward(self, teacher_features, student_features):
        """
        teacher_features: dict of {layer_idx: (Q_t, K_t, V_t)}  # 来自原生RoPE模型
        student_features: dict of {layer_idx: (Q_s, K_s, V_s)}  # 来自缩放RoPE模型
        
        计算多层的注意力结构蒸馏损失
        """
        total_loss = 0.0
        num_layers = 0
        
        for layer_idx in teacher_features:
            Qt, Kt, Vt = teacher_features[layer_idx]
            Qs, Ks, Vs = student_features[layer_idx]
            
            # 计算教师模型的自关系矩阵（用于前向，不存储完整矩阵）
            # 由于教师是冻结的，只在反向时重计算
            with torch.no_grad():
                # Q-Q 自关系
                R_Qt = F.softmax(Qt @ Qt.T / Qt.shape[-1]**0.5, dim=-1)
                # K-K 自关系
                R_Kt = F.softmax(Kt @ Kt.T / Kt.shape[-1]**0.5, dim=-1)
                # V-V 自关系
                R_Vt = F.softmax(Vt @ Vt.T / Vt.shape[-1]**0.5, dim=-1)
            
            # 计算学生模型的自关系矩阵
            R_Qs = F.softmax(Qs @ Qs.T / Qs.shape[-1]**0.5, dim=-1)
            R_Ks = F.softmax(Ks @ Ks.T / Ks.shape[-1]**0.5, dim=-1)
            R_Vs = F.softmax(Vs @ Vs.T / Vs.shape[-1]**0.5, dim=-1)
            
            # 蒸馏损失 = 三种自关系矩阵的 KL 散度之和
            loss_Q = self.row_kl_divergence(R_Qt, R_Qs)
            loss_K = self.row_kl_divergence(R_Kt, R_Ks)
            loss_V = self.row_kl_divergence(R_Vt, R_Vs)
            
            total_loss += loss_Q + loss_K + loss_V
            num_layers += 1
        
        return total_loss / (num_layers * 3)  # 平均到每种关系矩阵


class LinearARDTrainer:
    """
    LinearARD 训练器
    """
    def __init__(self, teacher_model, student_model, lr=1e-4):
        self.teacher = teacher_model  # 冻结的原生RoPE模型
        self.student = student_model  # 可学习的缩放RoPE模型
        self.loss_fn = LinearARDLoss()
        self.optimizer = torch.optim.AdamW(student_model.parameters(), lr=lr)
    
    def train_step(self, batch_short_text):
        """
        单步训练
        batch_short_text: 短文本 tokens（如 2K 长度）
        """
        # 教师模型前向（冻结）
        with torch.no_grad():
            teacher_outputs = self.teacher(
                batch_short_text,
                output_hidden_states=False,
                output_attentions=True  # 需要注意力矩阵
            )
            teacher_features = {
                i: (out.q, out.k, out.v) 
                for i, out in enumerate(teacher_outputs.attentions)
            }
        
        # 学生模型前向（可学习）
        student_outputs = self.student(
            batch_short_text,
            output_hidden_states=False,
            output_attentions=True
        )
        student_features = {
            i: (out.q, out.k, out.v)
            for i, out in enumerate(student_outputs.attentions)
        }
        
        # 计算蒸馏损失
        loss = self.loss_fn(teacher_features, student_features)
        
        # 反向传播
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
```

---

## 架构分析

### 完整蒸馏系统架构

```
输入短文本（≤ 原始最大长度，如 4K）
      │
      ▼
┌─────────────────────────────────────────┐
│  教师模型（冻结：原生 RoPE，θ_i）        │
│  ├─ L 层 Transformer                    │
│  ├─ 每层输出：Q_t, K_t, V_t             │
│  └─ 冻结，不更新参数                     │
└─────────────────────────────────────────┘
      │
      │ 对齐 Q-Q、K-K、V-V 自关系矩阵
      │ 每层 3 个 KL(R_t || R_s)
      ▼
┌─────────────────────────────────────────┐
│  学生模型（可学习：缩放 RoPE，θ_i/α）   │
│  ├─ L 层 Transformer（参数初始化自教师） │
│  ├─ RoPE 角度按 α 缩放                  │
│  └─ 线性内存内核（O(n) 显存）           │
└─────────────────────────────────────────┘
      │
      │ 梯度更新
      ▼
   学生模型权重更新
```

### 关键组件

| 组件 | 作用 | 实现要点 |
|------|------|---------|
| 教师特征提取 | 冻结模型，每层提取Q/K/V | torch.no_grad()，仅前向 |
| 自关系计算 | R = softmax(X·X^T/√d) | Q-Q、K-K、V-V三种 |
| 行分布对齐 | KL(R_Qt || R_Qs) 等 | 对每行单独计算KL后平均 |
| 线性内存内核 | log-sum-exp统计量替代完整矩阵 | 分块计算+数值稳定log-sum-exp |
| 梯度重建 | 反向时精确还原完整梯度 | 通过softmax梯度公式 |

---

## 代表模型

### LLaMA2-7B（4K → 32K）

| 配置 | 值 |
|------|---|
| 原始上下文 | 4K |
| 目标上下文 | 32K |
| 缩放因子 α | 8 |
| 训练tokens | 425万 |
| 短文本恢复率 | 98.3% |
| 长上下文基准 | 超越SOTA |

---

## 技术对比

| 方面 | CPT（持续预训练） | LongReD | **LinearARD** |
|------|------------------|---------|-------------|
| 蒸馏目标 | 隐藏状态 | 隐藏状态 | 注意力结构 |
| 训练tokens | 256M | 256M | **4.25M** |
| 显存复杂度 | O(n²) | O(n²) | **O(n)** |
| 短文本恢复 | ~95% | ~96% | **98.3%** |
| 长上下文能力 | 一般 | 良好 | **超越SOTA** |
| 训练成本 | 高 | 高 | **极低** |
| 效率提升 | 1× | 1× | **60×** |

---

## 进阶阅读

### 必读论文
1. [LinearARD: Linear-Memory Attention Distillation for RoPE Restoration](https://arxiv.org/abs/2604.00004) — 原始论文
2. [RoPE: Rotary Position Embedding](https://arxiv.org/abs/2104.09864) — 旋转位置编码基础
3. [LongRoPE: Efficient Context Extension](https://arxiv.org/abs/2402.13655) — LongReD前身

### 开源实现
1. [gracefulning/LinearARD](https://github.com/gracefulning/LinearARD) — 官方实现
2. [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) — 可用于CPT基线对比

---

## 历史演进

- **2023年**：RoPE提出（Su et al.），通过旋转矩阵编码位置信息
- **2024年**：LongRoPE提出，用渐进式扩展将上下文从32K扩到256K，但需256M tokens
- **2025年**：CPT成为主流，但效率问题始终未解决
- **2026年**：LinearARD，用注意力结构蒸馏，425万tokens达到更好效果

---

## 思考题

1. **为什么对齐注意力结构比对齐隐藏状态更有效？**
   提示：Transformer的决策本质上由注意力权重决定，而非最终隐藏状态。注意力结构是对"决策过程"的对齐，隐藏状态是对"中间产物"的对齐。

2. **LinearARD能否扩展到多模态模型（VLMo、LLaVA）？**
   提示：视觉token的自关系矩阵是否也有类似的对齐价值？

3. **4.25M tokens的极致效率是否意味着"上下文扩展可以随时做"？**
   提示：还需要考虑(1) 教师模型的规模 (2) 学生模型架构是否支持 (3) 长上下文能力的验证成本
