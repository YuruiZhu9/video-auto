# 深度技术报告：Dr.GRPO——消除长度偏差的强化学习优化新范式

**更新版本：v2.1 | 更新日期：2026-03-23**

---

## 一句话概括
Dr.GRPO（Group Relative Policy Optimization Done Right）是Sea AI Lab针对GRPO长度偏差问题提出的改进算法，通过无偏的策略梯度计算，显著提升令牌效率和推理精度。

---

## 背景与动机

### GRPO的核心问题：长度偏差

DeepSeek-R1-Zero的成功证明了纯强化学习（无监督微调、无价值网络）可以让大模型自主涌现推理能力。GRPO是该工作的核心算法，其通过**组内相对奖励比较**代替传统PPO的价值网络，大幅降低了训练开销：

**GRPO的奖励归一化：**
$$\tilde{r}_i = \frac{r_i - \mu(\mathbf{r})}{\sigma(\mathbf{r})}$$

其中 $\mu$ 是组内奖励均值，$\sigma$ 是组内奖励标准差。

这个设计在理论上简洁优雅，但在实践中引入了**两个隐藏的长度偏差**：

**偏差来源一：奖励归一化中的分母依赖响应长度**

当同一组内两个回答奖励相同时（如都是正确答案），较短回答的优势反而被高估：

- 正确答案A：长度=50 tokens，奖励=1.0
- 正确答案B：长度=200 tokens，奖励=1.0

两者归一化后完全等价，但长回答包含更多计算"浪费"。关键问题在于，错误回答如果也很长，其方差贡献更大，间接影响所有回答的归一化结果。

**偏差来源二：策略梯度符号被错误响应长度干扰**

在GRPO的策略梯度中：
$$\nabla_\theta \mathcal{L} \approx \mathbb{E}\left[\frac{\pi_\theta}{\pi_{old}} \cdot \hat{A}\right]$$

当优势 $\hat{A}$ 为负时（错误回答），较长的错误回答因累积概率更低，其梯度反而被"削弱"——这与"越长越应被惩罚"的直觉相反。

**最终后果：**
模型在RL训练过程中响应长度持续膨胀（bloat），产生大量无意义的"过度推理"token，训练效率低下。

---

## 数学原理：Dr.GRPO的改进

### 核心改进：用常量替代动态归一化项

Sea AI Lab的洞察是：**归一化项 $\sigma(\mathbf{r})$ 本身包含了响应长度的隐式信息**（因为长回答更容易累积概率、产生方差），因此引入偏差。

Dr.GRPO的核心改动极为简洁——将标准差 $\sigma(\mathbf{r})$ 替换为常量 $c$：

**GRPO（原始）：**
$$\hat{A}_i^{GRPO} = \frac{r_i - \mu(\mathbf{r})}{\sigma(\mathbf{r})}$$

**Dr.GRPO（改进）：**
$$\hat{A}_i^{Dr.GRPO} = \frac{r_i - \mu(\mathbf{r})}{c}$$

其中 $c$ 是一个**固定常量**（如取1.0或组内token数均值），完全切断长度信息的泄漏通道。

### 为什么这能工作：无偏优化的视角

从策略梯度的期望来看：

$$\mathbb{E}\left[\nabla_\theta \log \pi_\theta(a_i) \cdot \hat{A}_i\right]$$

当使用相对奖励时，我们关心的是 $\text{sign}(\hat{A}_i)$——正优势推动正样本，负优势抑制负样本。

在GRPO中，$\sigma(\mathbf{r})$ 作为归一化因子，会随组内回答长度方差变化，导致：
- 长回答 → 高方差 → $\sigma$ 大 → 优势被"压扁"
- 短回答 → 低方差 → $\sigma$ 小 → 优势被"放大"

这等价于在优化目标中引入了长度作为隐变量，是为"偏差"。

Dr.GRPO去掉这个隐变量后，令牌效率（tokens per correct answer）显著下降，同时正确率提升。

### 完整目标函数对比

**GRPO：**
$$\mathcal{L}^{GRPO} = -\mathbb{E}\left[\min\left(\frac{\pi_\theta}{\pi_{old}} \cdot \frac{r_i - \mu}{1+\epsilon}, \text{clip}(\cdots)\right)\right] - \beta \cdot D_{KL}(\pi_\theta \| \pi_{ref})$$

**Dr.GRPO：**
$$\mathcal{L}^{Dr.GRPO} = -\mathbb{E}\left[\min\left(\frac{\pi_\theta}{\pi_{old}} \cdot \frac{r_i - \mu}{c}, \text{clip}(\cdots)\right)\right] - \beta \cdot D_{KL}(\pi_\theta \| \pi_{ref})$$

差异仅在于分母：$\sigma(\mathbf{r})+1 \to c$，但效果是根本性的。

---

## 代码实现

```python
import torch
import torch.nn.functional as F

def compute_advantages_grpo(rewards: torch.Tensor, old_log_probs: torch.Tensor):
    """
    GRPO原始实现（含长度偏差）
    """
    mean_reward = rewards.mean()
    std_reward = rewards.std() + 1e-8  # 动态标准差 ← 偏差来源
    
    advantages = (rewards - mean_reward) / std_reward
    return advantages

def compute_advantages_dr_grpo(rewards: torch.Tensor, c: float = 1.0):
    """
    Dr.GRPO实现（无偏版本）
    
    Args:
        rewards: 组内每个回答的奖励张量 [batch_size]
        c: 固定常数（推荐取1.0或组内token数的倒数）
    
    Returns:
        advantages: 无偏优势估计
    """
    mean_reward = rewards.mean()
    
    # 核心改动：用固定常数c替代动态std
    advantages = (rewards - mean_reward) / c
    return advantages

def policy_gradient_loss_grpo(log_probs: torch.Tensor, 
                               old_log_probs: torch.Tensor,
                               advantages: torch.Tensor,
                               clip_eps: float = 0.2):
    """
    策略梯度损失（GRPO/Dr.GRPO通用）
    """
    ratio = torch.exp(log_probs - old_log_probs)
    
    # PPO风格的clip
    clipped_ratio = ratio.clamp(1 - clip_eps, 1 + clip_eps)
    
    # 使用原始ratio或clip后的ratio，取较小值
    surrogate = torch.minimum(
        ratio * advantages,
        clipped_ratio * advantages
    )
    
    return -surrogate.mean()
```

**关键区别一目了然：**

```python
# GRPO：动态标准差 ← 长度偏差悄悄渗入
std = rewards.std() + 1e-8

# Dr.GRPO：固定常数 ← 完全切断长度信息
c = 1.0  # 或其他经验常量
```

---

## 实验结果

### Qwen2.5-Math-7B上的对比

| 方法 | AIME 2024 准确率 | 平均响应长度 | 令牌效率 |
|------|-----------------|------------|---------|
| SFT基线 | 2.2% | ~80 tokens | 基准 |
| GRPO | 46.7% | ~500 tokens | 较低 |
| **Dr.GRPO** | **52.1%** | ~280 tokens | **最高** |

**结论：Dr.GRPO在AIME 2024上超越了GRPO 5.4个百分点，同时响应长度缩短了44%。**

### 不同基础模型的适配性

Sea AI Lab还发现，基础模型对RL后训练的响应模式差异显著：

| 模型 | 有模板 vs 无模板 | 关键发现 |
|------|----------------|---------|
| **Qwen2.5系列** | 无模板反而更好 | 预训练数据含大量QA对，无需显式引导 |
| **DeepSeek-V3-Base** | 有模板涌现"顿悟"时刻 | 模板引导下自发出现自我反思行为 |
| **Llama系列** | 严重依赖模板 | 无模板时几乎无推理能力 |

这说明不同模型的预训练数据分布深刻影响其RL后训练表现——"顿悟时刻"不是凭空产生的，而是从预训练中已有的推理模式中被激活的。

---

## 架构分析：Dr.GRPO在RL Pipeline中的位置

```
[问题输入 prompt]
       ↓
[模型采样G个回答]  ← 并行采样，显存高效
       ↓
[奖励模型打分]  ← 每回答一个标量reward
       ↓
┌────────────────────────────┐
│  优势计算（关键区别）         │
│  GRPO:  ÷std(r) ← 长度偏差  │
│  Dr.GRPO: ÷c  ← 无偏       │
└────────────────────────────┘
       ↓
[PPO-style策略梯度更新] ← 无价值网络，显存友好
       ↓
[KL约束保护] ← 防止策略崩溃
       ↓
[迭代优化...]
```

---

## 与其他RL增强方法的对比

| 方法 | 长度控制 | 价值网络 | 适用场景 | 核心优势 |
|------|---------|---------|---------|---------|
| PPO | 无 | 需要 | 通用RL | 理论最稳定 |
| GRPO | 无 | 不需要 | 推理增强 | 显存低 |
| **Dr.GRPO** | **主动控制** | 不需要 | 推理增强 | **令牌效率最高** |
| DPO | 间接 | 不需要 | 对齐微调 | 不需要奖励模型 |

---

## 常见误区

**❌ 误区1：Dr.GRPO只是调参**
实际上，GRPO→Dr.GRPO是从"隐式长度建模"到"无偏优化"的质变，是原理层面的修正而非超参调整。

**❌ 误区2：所有模型都应使用Dr.GRPO**
对于不需要控制响应长度的场景（如创意写作），GRPO与Dr.GRPO效果相近。选择取决于具体任务需求。

**❌ 误区3：c取任何值都行**
c太小会导致梯度过大、训练不稳定；c太大则优势信号被稀释。一般从c=1.0开始调。

---

## 思考题

1. **如何自适应地选择c？** 不同任务的最优c可能不同，能否设计一个随训练动态调整c的机制？

2. **Dr.GRPO能否与PPO结合？** 去掉std后，是否可以在某些层用价值网络弥补信息损失？

3. **过度推理的自动检测：** 能否在推理时动态检测"无意义推理"并提前终止（如类似Self-Termination的技术）？

---

## 附：HDPO——悬崖提示的蒸馏突破（2026-03-27更新）

HDPO（Hybrid Distillation Policy Optimization，arXiv 2603.23871，2026.03.24）与GRPO体系紧密相关，共同构成RLVR优化的完整图谱。

### 悬崖提示与GRPO的关联

当使用GRPO训练数学推理时，**悬崖提示（Cliff Prompts）**指模型完全无法回答的问题——组内所有rollout奖励均为零：

$$\mathcal{C}_{cliff} = \{x : \forall \tau \sim \pi_\theta(\cdot|x), \ r(x, \tau) = 0\}$$

此时GRPO的优势归一化中 $\mu(\mathbf{r}) = 0$，导致 $\tilde{r}_i \approx 0$，策略梯度消失。模型在悬崖提示上**完全停止学习**。

### HDPO的解决方案

HDPO通过**特权自蒸馏**为悬崖提示补充梯度信号：

**特权输入构造：** 向模型提供ground truth（标准答案、关键定理），生成正确解题路径

**蒸馏目标：**

$$\mathcal{L}_{distill} = -\sum_t \pi_{teacher}(t|x, \text{GT}) \cdot \log \pi_\theta(t|x)$$

**最终混合目标：**

$$\mathcal{L}_{HDPO} = \underbrace{\mathcal{L}_{GRPO}}_{\text{常规问题}} + \underbrace{\lambda \cdot \mathcal{L}_{distill}}_{\text{悬崖提示}}$$

**关键保证：** 教师与学生共享权重 $\Rightarrow$ 蒸馏能力差距有界，不会引入分布偏移。

### 与Dr.GRPO的关系

| 维度 | Dr.GRPO | HDPO |
|------|---------|------|
| 优化对象 | 长度偏差（GRPO内部问题） | 悬崖提示（GRPO外部问题） |
| 核心方法 | 替换归一化常量为固定值 | 特权自蒸馏补充梯度 |
| 解决的问题 | 响应膨胀、token效率低 | 梯度消失、能力边界无法突破 |
| 互补性 | ✅ 两者可叠加使用 | ✅ |

---

## 参考资料

1. [DeepSeek-R1 Zero论文](https://arxiv.org/abs/2409.21376) - GRPO原始论文
2. [Sea AI Lab Dr.GRPO](https://github.com/sail-sg/understand-r1-zero) - Dr.GRPO开源实现
3. [R1-Zero训练分析报告](https://blog.csdn.net/tMb8Z9Vdm66wH68VX1/article/details/147845997) - 中文技术解读
4. [HDPO论文](https://arxiv.org/abs/2603.23871) - 悬崖提示蒸馏（2026.03.24）
