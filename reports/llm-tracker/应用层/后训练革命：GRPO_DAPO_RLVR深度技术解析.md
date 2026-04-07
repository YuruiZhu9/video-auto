# 后训练革命：GRPO、DAPO 与 RLVR 深度技术解析

> 版本：v1.0 | 更新日期：2026-04-01 | 状态：最新重大进展

## 一句话概括

2025-2026 年，LLM 后训练从"RLHF + PPO 时代"全面转向"GRPO + DAPO + RLVR 时代"——不需要 Critic 模型、不需要人工标注、显存占用从 4x 降至 1x，同时催生了 DeepSeek-R1 等推理能力突破的模型。

---

## 背景：RLHF 时代的三大瓶颈

### 经典 RLHF（InstructGPT, ChatGPT）流程

```
预训练模型
    ↓
SFT（监督微调）→ 学习格式和风格
    ↓
奖励建模（RM）→ 训练一个 Reward Model
    ↓
PPO 强化学习 → 优化 Reward Model 得分
```

### PPO + RLHF 的瓶颈

**1. Critic 模型开销**

PPO 需要同时维护四个模型：
- 策略模型（Policy）：需要更新的 LLM
- 参考模型（Reference）：冻结的原始模型（计算 KL 散度）
- 奖励模型（Reward）：预训练的奖励模型
- Critic 模型：价值估计网络（与 Policy 同规模）

**显存占用**（以 7B 模型为例）：

| 模型 | 参数量 | FP16 显存 | 7B 模型显存 |
|------|--------|----------|-----------|
| Policy | 14B | 28GB | 主显存 |
| Reference | 14B | 28GB | KL 散度参考 |
| Reward | 14B | 28GB | 奖励信号 |
| Critic | 14B | 28GB | 价值估计 |
| **总计** | **56B** | **112GB** | **≈ 8×H100 80GB** |

**2. 人类标注成本爆炸**

Reward Model 需要大量**偏好对（Preference Pairs）**：

$$
(x, y_{\text{good}}, y_{\text{bad}}, r)
$$

- $x$：输入提示词
- $y_{\text{good}}$：人类偏好的回答
- $y_{\text{bad}}$：人类不偏好的回答
- $r$：偏好强度标注

随着模型能力提升，**人类越来越难判断哪个回答更好**，标注质量下降、成本上升。

**3. 训练不稳定**

PPO 的 KL 约束需要精心调参：
- KL 系数太大 → 训练无法偏离参考模型太远
- KL 系数太小 → Reward Hacking（模型欺骗 Reward Model）
- Clip 范围需要手动调整

---

## 一、GRPO（Group Relative Policy Optimization）

### 1.1 核心思想：去掉 Critic 模型

GRPO 由 DeepSeek 团队在 **DeepSeekMath**（2024）中首次提出，核心创新是：

> **对于同一个 prompt，采样 G 个回答，用组内相对排名替代 Critic 模型的价值估计。**

### 1.2 数学原理

**传统 PPO 优势函数（Advantage）**：

$$
A_t = \sum_{l=0}^{\infty} \gamma^l r_{t+l} - V(s_t)
$$

需要 Critic 模型 $V(s_t)$ 来估计未来累积奖励。

**GRPO 优势函数**：

$$
A_i = \frac{r_i - \mu}{\sigma}, \quad i = 1, 2, \ldots, G
$$

其中：
- $r_i$：第 $i$ 个回答的奖励（由验证器给出）
- $\mu = \frac{1}{G}\sum_{j=1}^{G} r_j$：组内奖励均值
- $\sigma = \sqrt{\frac{1}{G}\sum_{j=1}^{G}(r_j - \mu)^2}$：组内奖励标准差

**直觉**：不需要知道绝对价值，只需要知道在 G 个选项中哪个相对更好。

**策略梯度**：

$$
\nabla_\theta J(\theta) = \mathbb{E}_{x \sim \mathcal{D}, \{y_i\} \sim \pi_\theta(y|x)} \left[ \sum_{i=1}^{G} \nabla_\theta \log \pi_\theta(y_i|x) \cdot A_i \right]
$$

相比 PPO 的策略梯度，GRPO 的优势在于：
- 减少了方差（组内均值作为 baseline）
- 不需要额外的 Critic 网络

### 1.3 PPO vs GRPO 目标函数对比

**PPO 目标**：

$$
L^{\text{PPO}}(\theta) = \mathbb{E}\left[ \min\left(\frac{\pi_\theta}{\pi_{\theta_{\text{old}}}} \cdot A, \text{clip}\left(\frac{\pi_\theta}{\pi_{\theta_{\text{old}}}}, 1-\epsilon, 1+\epsilon\right) \cdot A\right) \right]
$$

需要 $A = Q(s,a) - V(s)$ → 需要 Critic。

**GRPO 目标**：

$$
L^{\text{GRPO}}(\theta) = \mathbb{E}\left[ \frac{1}{G} \sum_{i=1}^{G} \sum_{t=1}^{|y_i|} \nabla_\theta \log \pi_\theta(y_{i,t}|x, y_{i,<t}) \cdot \frac{r_i - \mu}{\sigma} \right]
$$

**GRPO 简化版（带 KL 正则化）**：

$$
L^{\text{GRPO}} = -\mathbb{E}_{x, \{y_i\}} \left[ \sum_{i=1}^{G} \frac{r_i - \mu}{\sigma} \cdot \frac{1}{|y_i|} \sum_{t} \log \pi_\theta(y_{i,t}|x, y_{i,<t}) \right] + \beta \cdot D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}})
$$

### 1.4 理论保证（2026年新进展）

据 arXiv 2603.22117v1（2026年3月）：

> GRPO 的策略梯度是 **U-统计量**（U-Statistic），其渐近分布等价于拥有**完美价值函数（Oracle Critic）** 的 PPO 算法。

这意味着 GRPO 在理论上可以达到 PPO 的渐近最优性，而不需要 Critic 模型——这是 2026 年 RL 后训练领域最重要的理论进展。

### 1.5 Prompt Replay 技术

**问题**：在线采样 G 个回答的开销很大，特别是长回答任务。

**解决方案**：混合使用新采样的回答和历史采样的回答：

$$
\mathcal{B}_k = \alpha \cdot \mathcal{B}_{\text{new}} + (1-\alpha) \cdot \mathcal{B}_{\text{history}}
$$

其中 $\alpha$ 通常设为 0.5~0.8，可以在保持训练质量的同时减少约 40% 的采样开销。

### 1.6 显存对比

| 方法 | 策略模型 | Critic | 参考模型 | 奖励模型 | 总相对显存 |
|------|---------|--------|---------|---------|-----------|
| PPO + RLHF | ✅ | ✅ | ✅ | ✅ | **4x** |
| GRPO + RLVR | ✅ | ❌ | ✅ | ❌ | **2x** |
| DAPO + RLVR | ✅ | ❌ | ❌ | ❌ | **1x** |

---

## 二、DAPO（Dynamic Advantage Policy Optimization）

### 2.1 背景：GRPO 的三大问题

GRPO 在训练长链推理任务（如数学证明、多步编程）时暴露了三个核心问题：

**问题 1：熵崩塌（Entropy Collapse）**

随着训练进行，策略分布 $\pi_\theta(y|x)$ 的熵急剧下降，模型过早收敛到单一高概率回答，失去探索多样性。

数学上：

$$
H(\pi_\theta) \xrightarrow{\text{训练}} 0
$$

模型开始"偷懒"，只输出最有把握的答案，复杂问题放弃尝试。

**问题 2：梯度消失（Gradient Vanishing）**

在长度为 2048 的回答上，序列级别的损失信号被极度稀释：

$$
\frac{\partial L}{\partial \theta} = \sum_{t=1}^{2048} \frac{\partial L}{\partial \log \pi_\theta(y_t)} \cdot \frac{\partial \log \pi_\theta(y_t)}{\partial \theta}
$$

早期 token 的梯度几乎为零。

**问题 3：超长截断的奖励噪声**

当回答被截断时（超出最大长度），无法获得有意义的奖励，但模型可能已经接近正确答案——这种"伪负例"严重干扰训练。

### 2.2 四项核心改进

| 技术 | 解决的问题 | 核心机制 | 公式 |
|------|----------|---------|------|
| **Clip-Higher** | 熵崩塌 | 增大正 advantage 的 clip 上界 | `clip(1-ε, 1+ε_higher)` 其中 ε_higher > ε |
| **Dynamic Sampling** | 梯度信号不一致 | 过滤 batch 中全对/全错的 prompt | 移除熵为零的样本 |
| **Token-level Loss** | 长序列梯度消失 | 每个 token 独立计算损失 | $L = -\frac{1}{T}\sum_t \log \pi_\theta(y_t)$ |
| **Overlong Reward Shaping** | 截断奖励噪声 | 超长回答 reward = 0（非负惩罚） | $r_{\text{overlong}} = 0$ |

### 2.3 Clip-Higher 详解

**标准 PPO/GRPO 的 clip**：

$$
\pi_\theta(y|x) / \pi_{\theta_k}(y|x) \in [1-\epsilon, 1+\epsilon]
$$

Clip 限制了策略更新的幅度，防止过度偏离旧策略。但对于正 advantage 的 clip 上界过于保守，导致模型熵降低。

**Clip-Higher 的改进**：

$$
\text{ratio} \in [1-\epsilon_{\text{lower}}, 1+\epsilon_{\text{higher}}]
$$

其中 $\epsilon_{\text{lower}} < \epsilon < \epsilon_{\text{higher}}$。

当 $A_i > 0$（好回答）时，增大允许更新的幅度，鼓励模型探索更多好回答的不同变体。

**伪代码**：

```python
def clip_higher_policy_loss(log_probs, old_log_probs, advantages, 
                              eps_lower=0.2, eps_higher=0.4):
    ratio = torch.exp(log_probs - old_log_probs)  # π_θ / π_θ_old
    
    # 对于正 advantage：允许更大范围的增长
    positive_mask = advantages > 0
    negative_mask = advantages <= 0
    
    loss_positive = -advantages * torch.clamp(
        ratio, 
        min=1 - eps_lower,  # 下界收紧
        max=1 + eps_higher  # 上界放宽 → 鼓励探索
    )
    
    loss_negative = -advantages * torch.clamp(
        ratio,
        min=1 - eps_lower,
        max=1 + eps_lower  # 负 advantage 保持标准 clip
    )
    
    return (loss_positive + loss_negative).mean()
```

### 2.4 Dynamic Sampling

**问题**：当一个 batch 中所有 G 个回答全部正确或全部错误时，组内标准差 σ = 0，所有 advantage = 0，梯度为零。

**解决方案**：

```python
def dynamic_sampling(responses, rewards, group_size):
    """过滤无信息量样本"""
    new_groups = []
    new_rewards = []
    
    for i in range(0, len(responses), group_size):
        group = responses[i:i+group_size]
        group_rewards = rewards[i:i+group_size]
        
        # 如果所有奖励相同（方差=0），跳过
        if group_rewards.std() > 1e-6:
            new_groups.append(group)
            new_rewards.append(group_rewards)
        # 否则：这批数据在当前策略下无信息量
    
    return new_groups, new_rewards
```

### 2.5 Token-level Loss vs Sequence-level Loss

**Sequence-level（GRPO 原始）**：

$$
L^{\text{seq}} = -\frac{1}{G} \sum_{i=1}^{G} A_i \cdot \frac{1}{|y_i|} \sum_{t=1}^{|y_i|} \log \pi_\theta(y_{i,t})
$$

每个 token 的梯度贡献被回答长度 $|y_i|$ 平均，在长序列上信号被稀释。

**Token-level（DAPO）**：

$$
L^{\text{token}} = -\frac{1}{\sum_i |y_i|} \sum_{i=1}^{G} \sum_{t=1}^{|y_i|} A_i \cdot \log \pi_\theta(y_{i,t})
$$

每个 token 的权重相同，早期 token 不再被稀释。

### 2.6 效果对比（AIME 2024 基准）

| 方法 | 基座模型 | 规模 | AIME 2024 得分 | 训练步数 | 相对显存 |
|------|---------|------|---------------|---------|---------|
| PPO | DeepSeek-V3 | 236B MoE | 71.0 | ~10K | 4x |
| GRPO | DeepSeek-V3 | 236B MoE | **79.8** | ~8K | 2x |
| DAPO | Qwen2.5-32B | 32B | 50.0 | ~5K（减半）| 1x |

**关键洞察**：
- DeepSeek-R1（GRPO）以 236B 规模达到 79.8 分
- DAPO 仅用 32B 规模（1/7.4 参数）达到 50 分，展示了算法的力量
- DAPO 训练步数减少 50%，显存降至 1x

---

## 三、RLVR（Reinforcement Learning with Verifiable Rewards）

### 3.1 核心思想：用自动验证器替代人类

**问题**：数学、代码等任务有**可验证的正确答案**，为什么还要依赖 Reward Model？

**RLVR 解决方案**：

$$
r(x, y) = \mathbb{1}[y \text{ 通过验证器}]
$$

| 任务类型 | 验证器 | 奖励定义 |
|---------|-------|---------|
| 数学题 | 数学计算器/Lean证明器 | 最终答案正确 = 1，否则 = 0 |
| 代码生成 | 单元测试 | 所有测试通过 = 1，否则 = 0 |
| 结构化推理 | 形式化规范 | 逻辑一致性 = 1，否则 = 0 |
| 指令遵循 | 规则检查器 | 满足所有规则 = 1 |

### 3.2 DeepSeek-R1 的涌现能力

2025年初，DeepSeek 团队用 GRPO + RLVR 训练 DeepSeek-R1，产生了令人震惊的**涌现行为**：

**1. 自我反思（Self-Reflection）**

模型在推理过程中自发学会了：

```
让我重新检查这个证明...
实际上，我的上一步推导有误...
让我换一个思路...
```

**没有任何 CoT 数据训练**，这种行为在纯 RL 过程中自发生成。

**2. "Aha Moment"**

在训练日志中观察到一个著名的时刻：

> 模型在解决一个数学问题时，突然停下来写道：
> "Wait, let me think about this more carefully."
> 然后改变了整个解题策略，最终得到了正确答案。

这是推理能力涌现的经典案例。

**3. 动态策略切换**

模型学会了根据问题难度自动调整推理深度：

- 简单问题：一两步直接回答
- 复杂问题：展开多步推理，花费更多 tokens
- 训练过程中，**平均回答长度自然增长**——模型自动学会了"多想一会儿"

### 3.3 RISE（Reinforced Self-Verification）

**创新**：在单一 RL 过程中同时训练：
- **问题求解能力**（生成正确答案）
- **自我验证能力**（判断自己答案是否正确）

```python
# RISE 的双重奖励
def rise_reward(response, ground_truth):
    solution, verification = response.split("[VERIFICATION]")
    
    # 解题奖励
    solve_reward = verify(solution, ground_truth)
    
    # 验证奖励（验证器本身是否正确判断）
    verify_reward = verify_verification(verification, solution, ground_truth)
    
    return solve_reward + 0.5 * verify_reward
```

训练后，模型在推理阶段能够**发现并纠正自己的错误**，而不需要外部验证器。

### 3.4 噪声处理（去偏校正算法）

**问题**：验证器本身可能有噪声（代码的边界情况、数学的不完备证明），假阳性会导致模型学到错误行为。

**解决方案**：观测奖励的期望无偏估计：

$$
\hat{r}_{\text{unbiased}} = r - \frac{r - \mathbb{E}[r|\text{verification}]}{\mathbb{P}(\text{correct verification})}
$$

即用验证器输出作为校正项，消除假阳性的影响。

---

## 四、完整训练流水线

### 4.1 主流推理模型四阶段流程

```
┌─────────────────────────────────────────────────────────────┐
│                    阶段一：CoT 冷启动                       │
│  ─────────────────────────────────────────────────────── │
│  使用多样化长思维链数据微调（数学、编程、逻辑推理、STEM）   │
│  目标：让模型具备基本推理能力                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              阶段二：基于推理的强化学习（GRPO/DAPO + RLVR）│
│  ─────────────────────────────────────────────────────── │
│  利用可验证奖励扩大强化学习计算资源                         │
│  增强模型的探索和利用能力                                   │
│  涌现自我反思、多路径推理                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│               阶段三：思维模式融合（混合思考模式）          │
│  ─────────────────────────────────────────────────────── │
│  在长 CoT 数据 + 常用指令微调数据组合上微调                 │
│  将"非思考能力"注入到"思考模型"中                          │
│  实现：复杂问题→思考模式，简单问题→快速响应                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              阶段四：通用强化学习                           │
│  ─────────────────────────────────────────────────────── │
│  超过 20 个通用领域任务的 RL                               │
│  包括：指令遵循、格式遵循、Agent 能力等                     │
│  纠正不良行为，提升通用性                                   │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Qwen3 的混合思考模式

Qwen3（2026年）采用了这一流程，实现了**思考模式与非思考模式的动态切换**：

- **思考模式**：模型展开完整的思维链（CoT），适用于数学证明、复杂推理
- **非思考模式**：直接给出答案，适用于简单问答、闲聊
- **预算控制**：用户可以设置 token 预算，平衡成本与质量

### 4.3 DPO 偏好对齐（可选阶段四）

在 RL 阶段之后，可以用 DPO 做额外的偏好对齐：

**DPO 目标函数**（Bradley-Terry 模型）：

$$
L^{\text{DPO}} = -\mathbb{E}_{(x, y^+, y^-) \sim \mathcal{D}} \left[ \log \sigma\left( \beta \cdot \log \frac{\pi_\theta(y^+|x)}{\pi_{\text{ref}}(y^+|x)} - \beta \cdot \log \frac{\pi_\theta(y^-|x)}{\pi_{\text{ref}}(y^-|x)} \right) \right]
$$

将强化学习问题转化为**分类问题**，不需要 Reward Model 或 Critic。

---

## 五、技术全景对比

| 维度 | PPO + RLHF | GRPO + RLVR | DAPO + RLVR | ORPO |
|------|-----------|------------|-------------|------|
| Critic 模型 | 需要 | ❌ 不需要 | ❌ 不需要 | ❌ 不需要 |
| 参考模型 | 需要 | 需要 | ❌ 不需要 | ❌ 不需要 |
| 奖励模型 | 需要（RM） | 验证器 | 验证器 | ❌ 不需要 |
| 显存占用 | 4x | 2x | **1x** | **1x** |
| 适用场景 | 通用 | 数学/代码/推理 | 长链推理 | 极简流程 |
| 训练稳定性 | 中等 | 好 | **最好** | 好 |
| 实现复杂度 | 高 | 中 | 中 | **低** |
| AIME 2024 | 71.0 | **79.8** | 50.0 | — |
| 代表模型 | InstructGPT | DeepSeek-R1 | 字节系模型 | 多语言模型 |

---

## 六、开源资源

| 项目 | 技术 | 链接 | 特点 |
|------|-----|------|-----|
| OpenRLHF | GRPO / PPO / DPO | [GitHub](https://github.com/OpenRLHF/OpenRLHF) | 统一框架，支持主流后训练算法 |
| verl | GRPO 高效分布式 | [GitHub](https://github.com/volcengine/verl) | 字节跳动的 GRPO 高效实现 |
| DAPO 官方 | DAPO 四项技术 | [GitHub](https://github.com/ByteDance/DAPO) | 完整 DAPO 实现 |
| DeepSeek-R1 | GRPO + RLVR | [官方](https://www.deepseek.com) | 推理能力涌现的标杆 |
| TRROL | 无 Critic RL | [arXiv](https://arxiv.org/abs/2504.13367) | 理论保证 |

---

## 七、发展趋势（2026-2027）

### 1. 单一训练目标（ORPO 模式）

当前流程是 SFT → RL → DPO 三阶段。ORPO（Odds Ratio Policy Optimization）已经将 SFT 和偏好优化合并为单一目标，下一步是**将 RL 也合并进去**：

$$
L^{\text{Unified}} = L_{\text{SFT}} + \lambda_1 \cdot L_{\text{GRPO}} + \lambda_2 \cdot L_{\text{DPO}}
$$

### 2. 环境原生训练（Agentic RL）

从静态数据集转向**交互式环境**：
- **NeMo Gym**（NVIDIA）：物理模拟 + RL
- **RLFactory**：代码执行环境 + RL
- **WebArena**：网页交互 + RL

### 3. 自动课程生成

```
模型识别弱点 → 生成针对性数据 → 训练 → 重复 → 闭环
```

### 4. Process Reward Model（PRM）

从**结果奖励（ORM）**到**过程奖励（PRM）**：

| 类型 | 描述 | 粒度 |
|------|------|------|
| ORM（结果奖励） | 只给最终答案打分 | 序列级别 |
| PRM（过程奖励） | 给推理的每一步打分 | Token 级别 |

PRM 可以更好地引导长链推理，但标注成本高。最新方向是用**可验证奖励自动标注 PRM 数据**。

---

## 八、常见误区

1. **"GRPO 总是优于 PPO"**：错。在需要细粒度价值估计的场景（如开放式对话），PPO/RM 体系仍更稳定。GRPO 主要在有可验证奖励的领域（数学/代码）有优势

2. **"RLVR 只能处理简单任务"**：错。DeepSeek-R1 的涌现行为证明，RLVR 可以催生出远超训练数据分布的推理能力

3. **"DAPO 只是 GRPO 的调参"**：错。DAPO 有明确的理论动机（熵崩塌、梯度消失）和系统性的解决方案（Clip-Higher、Dynamic Sampling 等）

4. **"有了 RL 就不需要 SFT"**：错。SFT 提供了格式规范性和基础能力，是 RL 的必要冷启动

---

## 九、思考题

1. **GRPO 的组大小 G 如何选择？** G 越大，优势估计越稳定（方差小），但计算成本线性增长。是否可以自适应调整 G？

2. **DAPO 的 Clip-Higher 是否会导致 Reward Hacking？** 放宽正 advantage 的上界是否会鼓励模型生成"看起来好但实际错误"的长回答？

3. **PRM vs ORM**：是否可以用 RLVR 的可验证奖励自动生成 PRM 标注？每一步的正确性如何自动化验证？

4. **Agentic RL 的 Credit Assignment**：在多步工具调用任务中，如何准确地将最终奖励分配给每一步决策？

---

## 进阶阅读

### 必读论文
1. [GRPO: Group Relative Policy Optimization (DeepSeekMath)](https://arxiv.org/abs/2402.03300) — GRPO 原始论文
2. [DeepSeek-R1](https://arxiv.org/abs/2501.12948) — GRPO + RLVR 催生推理能力
3. [DAPO: Decoupled Clip and Dynamic Sampling Policy Optimization](https://arxiv.org/abs/2503.14476) — DAPO 四项技术
4. [PPO: Proximal Policy Optimization (2017)](https://arxiv.org/abs/1707.06347) — PPO 基础
5. [ORPO: Odds Ratio Preference Optimization](https://arxiv.org/abs/2403.07691) — 单一训练目标
6. [U-Statistic GRPO Theory (arXiv 2603.22117)](https://arxiv.org/abs/2603.22117) — GRPO 理论保证
7. [RISE: Reinforced Self-Verification](https://arxiv.org/abs/2505.02215) — 自我验证联合训练
8. [Tree-GRPO](https://github.com/AMAP-ML/Tree-GRPO) — 树搜索 + GRPO

### 开源实现
1. [OpenRLHF](https://github.com/OpenRLHF/OpenRLHF) — 统一后训练框架
2. [verl (字节)](https://github.com/volcengine/verl) — 高效 GRPO
3. [DAPO (字节)](https://github.com/ByteDance/DAPO) — 完整 DAPO
4. [DeepSeek-R1 系列模型](https://www.deepseek.com) — 模型权重
