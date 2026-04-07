# 推荐系统算法工程师面经每日整理
**整理日期：** 2026年3月27日（周五）
**岗位方向：** 推荐系统算法工程师
**执行状态：** ✅ 正常执行（无新增当日一手面经，沿用近期高频考点 + 深度多目标建模专项解析）

---

## 一、当日面经来源

| 来源平台 | 面经内容摘要 | 面试公司 | 面试轮次 |
|----------|------------|----------|---------|
| 牛客网 | 美团搜索推荐算法面经 | 美团 | 一面+二面（2024秋招，已OC） |
| 牛客网 | 百度推荐算法二面面经 | 百度 | 二面（2024年11月） |
| 腾讯云开发者社区 | 推荐算法工程师面经 | 腾讯云 | 一面 |
| CSDN博客 | 推荐系统算法工程师面试指导 | 综合 | 题库整理 |
| 今日头条（七月在线） | 推荐系统方向常见算法面试题6道 | 综合 | 题库整理 |
| 腾讯云 | 多目标优化ESMM/MMOE/PL E技术深度解析 | 综合 | 原理讲解 |

---

## 二、面试问题清单

### 【类别A】推荐系统全链路基础（高频）

1. 推荐系统的整体流程是怎样的？召回→精排→多目标混排各承担什么职责？
2. 召回和精排的核心差异是什么？为什么排序结果比召回更精准？
3. 双塔模型（DSSM）的原理是什么？有哪些优缺点？
4. 什么是样本选择偏差（Sample Selection Bias）？如何解决？

### 【类别B】多目标建模（当前最热考点）

5. 多目标优化有哪些方法？样本加权 vs 模型融合的区别？
6. MMOE的原理是什么？为什么存在"跷跷板现象"？
7. ESMM模型是如何解决样本选择偏差和数据稀疏问题的？
8. PLE模型相比MMOE有哪些改进？CGC网络结构是怎样的？
9. 为什么模型优化能解决负迁移问题？每个任务如何选择特征？

### 【类别C】经典推荐模型（高频必问）

10. Wide&Deep模型中Wide部分和Deep部分分别负责什么？各自优缺点？
11. FNN相比Deep Crossing有哪些创新？为什么需要预训练Embedding？
12. DIN模型中Attention机制是如何工作的？Score如何计算？

### 【类别D】算法工程与编程（面试必备）

13. 手撕：Mask Attention 实现（百度二面原题）
14. 手撕：重排链表（美团一面原题）
15. 手撕：数组Top-k，要求复杂度小于快排（美团二面原题）

### 【类别E】特征工程（高频基础）

16. 特征选择的方式有哪些？Filter/Wrapper/Embedded的区别？
17. 特征交叉的方式有哪些？笛卡尔积有什么优缺点？

### 【类别F】大模型与推荐结合（前沿热点）

18. 大模型和推荐系统有哪些可结合的点？商品理解/描述如何做？
19. LongLoRA和LoRA的区别是什么？

---

## 三、逐题详细解析

---

### A1. 推荐系统的整体流程是怎样的？召回→精排→多目标混排各承担什么职责？

**参考答案：**

推荐系统的整体流程呈**漏斗形**，从海量候选到最终展示逐层过滤：

```
全量候选池（亿级）
    ↓ 召回（Recall，百~千级）
候选集
    ↓ 粗排（Pre-Rank，几十~百级）
初筛候选集
    ↓ 精排（Rank，十~几十级）
精筛候选集
    ↓ 重排（Rerank，多样性/业务策略）
最终展示列表
```

| 阶段 | 核心职责 | 模型复杂度 | 候选规模 | 常用方法 |
|------|---------|-----------|---------|---------|
| **召回** | 从全量候选中快速拉取用户可能感兴趣的物品 | 简单（如双塔） | 百~千 | 协同过滤、双塔召回、Graph Embedding、语义向量召回 |
| **粗排** | 对召回结果做初步排序，过滤到精排可承受规模 | 中等 | 几十~百 | DSSM、轻量级排序模型 |
| **精排** | 精准预估每个候选的点击率/转化率/停留时长等目标 | 复杂（DNN） | 十~几十 | DeepFM、Wide&Deep、DIN、DIEN、MMOE |
| **重排** | 结合业务策略（多样性、新颖性、流量分配）做最终展示 | 策略+模型 | 最终展示 | MMR、上下文感知排序、Transformer重排 |

> **面试加分点：** 强调"**召回决定天花板，精排决定最终精度，重排负责业务体验**"。可补充工业界的典型配置，如某电商平台可能精排300物品，最终只展示20个。

---

### A2. 召回和精排的核心差异是什么？为什么排序结果比召回更精准？

**参考答案：**

| 维度 | 召回（Recall） | 精排（Rank） |
|------|--------------|-------------|
| **目标** | 广覆盖、高召回率 | 高精度排序 |
| **模型复杂度** | 简单（低延迟要求） | 复杂（DNN，毫秒级） |
| **特征使用** | 粗粒度特征（User ID、Item ID、统计特征） | 丰富特征（用户行为序列、上下文、实时特征） |
| **候选规模** | 亿级→百~千级 | 百级→十级 |
| **实时性要求** | 极高（在线serving） | 相对宽松 |
| **优化目标** | 多样性+相关性 | 单一/多业务目标 |

**为什么排序结果更精准？**
1. **候选规模小**：精排只需处理百级候选，有计算资源支撑复杂模型
2. **特征更丰富**：精排可使用完整的用户行为序列（点击序列、浏览序列）、丰富的上下文特征和物品详情特征
3. **模型更复杂**：精排可使用DeepFM、DIN、DIEN等复杂结构建模用户兴趣
4. **实时性差异**：召回双塔模型通常离线计算item embedding（隔天更新），而精排可做到小时级甚至实时更新

> **面试追问：** 面试官追问"双塔模型用户塔和物品塔是否都能实时更新？"  
> 参考回答：物品塔因候选集大通常隔天更新；用户塔可以通过实时行为序列建模做到近实时更新（如流式更新用户短期兴趣向量）。

---

### A3. 双塔模型（DSSM）的原理是什么？有哪些优缺点？

**参考答案：**

**原理：**
DSSM（Deep Structured Semantic Models）将用户和物品分别通过独立的DNN塔编码为低维语义向量，通过**cosine相似度**计算用户-物品匹配分数。

```
用户塔（User Tower）：
[用户特征] → DNN → user_embedding (k维)

物品塔（Item Tower）：
[物品特征] → DNN → item_embedding (k维)

Score = cosine(user_embedding, item_embedding)
```

**工业界应用：**
- **召回阶段**：离线计算所有item_embedding，在线实时计算user_embedding，做近邻检索（如ANN）
- **粗排阶段**：直接用cosine分数做粗排序

**优点：**
1. **解耦建模**：用户塔和物品塔独立，可分别离线/在线计算
2. **支持ANN检索**：物品向量可入库，在线检索效率高（百万~亿级）
3. **范化能力强**：用字向量输入减少切词依赖，有监督端到端训练
4. **部署友好**：物品塔完全离线计算，在线只计算用户塔，延迟低

**缺点：**
1. **丢失序列/上下文信息**：词袋模型（BOW），忽略语序和上下文
2. **两侧特征交互有限**：用户塔和物品塔在训练时才能交互，缺少细粒度特征交叉
3. **预测不可控**：弱监督端到端，模型黑盒
4. **多兴趣建模困难**：单向量难以表达用户多维度兴趣（可用多塔/HNN解决）

---

### A4. 什么是样本选择偏差（Sample Selection Bias）？如何解决？

**参考答案：**

**定义：** 训练模型时使用的数据分布与实际预测场景的数据分布不一致，导致模型存在系统性偏差。

**推荐系统中的典型场景：**
- CVR（点击转化率）预估：模型用"**点击样本**"训练，但预测时对"**全量曝光样本**"进行预估。点击用户本身是经过选择的正向用户，其行为模式不能代表全量用户。

**解决方法：**

| 方法 | 原理 | 代表模型 |
|------|------|---------|
| **全空间多任务学习** | 同时建模CTR和CVR任务，利用两者关系在全空间学习 | **ESMM** |
| **无偏学习** | 通过反事实推断对未点击样本进行加权/建模 | IPS（Inverse Propensity Score） |
| **随机实验** | 在全量流量上做随机实验获取无偏数据（成本高） | — |
| **迁移学习** | 用数据丰富任务的信号辅助数据稀疏任务 | 多任务学习 |

> **ESMM详解（见B3）** 是当前工业界解决SSB最主流的方案。

---

### B1. 多目标优化有哪些方法？样本加权 vs 模型融合的区别？

**参考答案：**

推荐系统常见多目标：**CTR、停留时长、点赞、评论、转发、完播率、GMV**等。

**三大方法：**

#### 方法一：样本加权（Sample Weight）
- **原理**：以一个主目标（CTR）为主，通过设置不同样本权重来兼顾其他目标（如完播率高→高权重）
- **实现**：训练时 `loss = Σ weight_i * loss_i`
- **优点**：模型简单，上线容易（只改梯度权重）
- **缺点**：本质上仍是单目标，权重依赖人工调参和AB测试，不够优雅

#### 方法二：模型融合（Multi-Model Ensemble）
- **原理**：各目标单独建模，线上融合（如 `score = α*CTR + β*CVR`）
- **优点**：各任务独立迭代，互不干扰
- **缺点**：任务间无法共享信息，训练资源翻倍；融合权重难调

#### 方法三：多任务学习（Hard/Soft Parameter Sharing）
- **原理**：共享底层表示，多任务联合训练
- **代表**：Shared-Bottom → MMOE → PLE 演进路径
- **优点**：任务间共享信息，互相迁移提升
- **缺点**：存在负迁移（跷跷板现象）

> **面试高频追问：** 多目标优化中各目标之间的"跷跷板现象"指什么？  
> 答：优化一个目标会导致另一个目标下降，这是因为任务之间存在冲突或负相关。多任务模型需要在任务间做平衡trade-off。

---

### B2. MMOE的原理是什么？为什么存在"跷跷板现象"？

**参考答案：**

**MMOE（Multi-gate Mixture-of-Experts）**，Google 2018提出，在MOE基础上为每个任务设置独立门控网络。

**核心结构：**
```
输入特征 x
    ↓
┌─────────────────────────────────────┐
│  K个 Expert（均为DNN/MLP）          │
│  Expert_i(x) = f_i(x)               │
│                                      │
│  每个任务 k 有独立的 Gating Network：│
│  G_k(x) = softmax(W_gk · x)        │
│                                      │
│  任务k输出：y_k = Σ g_k_i · Expert_i│
└─────────────────────────────────────┘
         ↓
   Task_1 ... Task_K（各自Tower）
```

**与MOE的区别：** MOE所有任务共用一个Gate，MMOE每个任务独立Gate，能更灵活地为不同任务分配专家权重。

**为什么存在跷跷板现象？**
1. **任务冲突**：当任务相关性低甚至负相关时（如点击率和完播率），一个Gate权重分配方案难以同时满足所有任务
2. **共享Expert的噪声**：所有Expert被所有任务共享，不相关任务会引入噪声到共享Expert中
3. **门控网络容量有限**：简单的线性Gate（softmax）难以建模复杂任务关系

**如何缓解跷跷板？** → PLE模型（见B4）

---

### B3. ESMM模型是如何解决样本选择偏差和数据稀疏问题的？

**参考答案：**

**ESMM（Entire Space Multi-Task Model）**，阿里妈妈团队 SIGIR 2018提出，核心解决CVR预估的两大问题：

#### 问题一：样本选择偏差（SSB）
- 传统CVR：训练数据 = 点击样本，但预测 = 全量曝光样本
- 偏差来源：点击用户本身就是高度自选择的有偏样本

#### 问题二：数据稀疏（Data Sparsity）
- 点击样本量 << 曝光样本量（通常CTR=5%，CVR=1%）
- CVR训练样本远少于CTR，导致模型欠拟合

**ESMM解决方案——引入转化公式：**

```
pCTCVR = pCTR × pCVR

即：P(y=1, z=1 | x) = P(y=1 | x) × P(z=1 | y=1, x)
    （点击且转化 = 点击 × 点击条件下的转化）
```

**网络结构：**
- 同时输出 pCTR（点击率）和 pCTCVR（点击+转化率）两个辅助任务
- pCVR = pCTCVR / pCTR（隐式学习，不直接监督）
- **所有任务在全量曝光样本上训练**，彻底消除SSB

**为什么有效？**
1. pCTR和pCTCVR在全空间训练，间接让pCVR学到全空间分布
2. 乘法形式避免除法导致pCVR>1的问题
3. 共享Embedding层，CTR任务的大量点击样本帮助CVR任务学到更好的特征表示

> **面试加分：** 能手画ESMM结构图（三个共享Embedding + CTR Tower + CTCVR Tower + 隐式CVR输出）

---

### B4. PLE模型相比MMOE有哪些改进？CGC网络结构是怎样的？

**参考答案：**

**PLE（Progressive Layered Extraction）**，腾讯PCG RecSys 2020最佳长论文，针对MMOE的不足提出。

**MMOE的问题：**
1. 所有Expert被所有任务共享，可能引入噪声
2. Expert之间无交互，缺乏层级信息提取

**CGC（Customized Gate Control）结构：**
```
输入x
    ↓
┌─────────────────────────────────────┐
│ Shared Experts（共享专家，多个MLP） │
│ Task1-Specific Experts（任务1独有） │
│ Task2-Specific Experts（任务2独有） │
│ ...                                  │
│                                       │
│ 每个任务有独立Gate：                  │
│ Gate_k = Σ（task_experts · w_k）    │
│         + Σ（shared_experts · w_k）  │
└─────────────────────────────────────┘
```

**PLE = 多层CGC叠加：**
```
Layer 1: CGC结构（shared + specific experts）
    ↓
Layer 2: 在Layer1输出上继续提取（Progressive）
    ↓
... 多层叠加
```

**核心改进：**
| 对比维度 | MMOE | PLE |
|---------|------|-----|
| Expert共享 | 所有任务共享全部Expert | 独有Expert + 共享Expert分离 |
| Expert交互 | 无交互 | 多层CGC逐步提取，层层交互 |
| Gate输入 | 仅原始特征x | 每层Gate同时看specific+shared |
| 噪声控制 | 差 | 好（specific expert隔离噪声） |
| 效果 | 基准 | 在MMOE基础上AUC显著提升 |

> **工程经验：** PLE中共享Expert和特有Expert的权重差异越大，说明模型越能有效区分任务特有信息和共享信息。实际调参时可通过观察权重分布判断模型学习效果。

---

### B5. 为什么模型优化能解决负迁移问题？每个任务如何选择特征？

**参考答案（百度二面追问）：**

**负迁移问题：** 当多任务模型中任务相关性低时，共享表示会强制不相关任务互相干扰，导致各任务效果下降。

**PLE如何解决负迁移：**
1. **Task-Specific Expert隔离**：每个任务有独立的Expert子网络，不用被迫从共享参数中学自己的专属模式
2. **选择性信息融合**：Gate机制让每个任务自己决定从Shared Expert中汲取多少信息（可趋向0），避免强制吸收噪声
3. **渐进式提取**：多层CGC逐步分离共享信息和任务特有信息

**特征选择策略（百度二面高频追问）：**
- **任务特性**：根据任务目标选择相关特征（如CVR任务需要转化相关行为特征）
- **增量特征 vs 共享特征**：共享特征给所有任务用，增量特征只给特定任务
- **实践经验**：一般共享底层Embedding/MLP，高层Tower按任务设特有特征输入
- **调参经验**：每个任务选择3~5个增量特征，太多会过拟合，太少学不到任务特性

---

### C1. Wide&Deep模型中Wide部分和Deep部分分别负责什么？

**参考答案：**

**Wide&Deep**，Google 2016年提出，用于Google Play应用推荐，是wide-deep架构的开山之作。

**结构：**
```
Wide部分（宽度/记忆）：
[输入特征] → LR（单层线性模型）→ output_wide
  - 擅长记忆（Memorization）：直接学习特征间的共现关系
  - 如：AND(user_installed_app=netflix, impression_app=pandora) → 推荐pandora
  - 依赖大量稀疏ID特征的手工特征交叉

Deep部分（深度/泛化）：
[Embedding特征] → DNN → output_deep
  - 擅长泛化（Generalization）：通过DNN隐式学习深层特征交叉
  - 自动学习高阶非线性特征组合
  - 对稀疏特征泛化到未见过的特征组合

组合输出：
P(y=1|x) = sigmoid(W_wide·Φ_wide(x) + W_deep·a^{(l)} + b)
```

**Wide vs Deep 对比：**

| 维度 | Wide（记忆） | Deep（泛化） |
|------|------------|-------------|
| 模型结构 | LR（线性） | DNN（非线性） |
| 特征要求 | 需手工特征交叉 | Embedding自动学习 |
| 优势 | 对历史数据直接记忆 | 发现隐含规律 |
| 劣势 | 泛化能力弱 | 可解释性差 |
| 适用场景 | 历史强关联 | 稀疏/新特征组合 |

**面试加分：** Wide&Deep开启了"双塔/多塔组合架构"的时代，后续DeepFM、DIN、DIEN等均沿用此范式。

---

### C2. FNN相比Deep Crossing有哪些创新？为什么需要预训练Embedding？

**参考答案：**

| 对比维度 | Deep Crossing | FNN |
|---------|--------------|-----|
| Embedding方式 | 从随机初始化开始训练 | **使用FM预训练的隐层向量初始化** |
| 训练效率 | 低（Embedding层参数多，梯度稀疏） | 高（预训练提供好的起点） |
| 训练稳定性 | 差（随机初始化+稀疏梯度） | 好（预训练Embedding更稳定） |
| 创新点 | 首次将Embedding+DL引入CTR | 引入**有监督预训练**思路 |

**为什么需要预训练Embedding？**

ID类特征（如Item ID、User ID）one-hot编码后维度极高（万~百万），Embedding层与输入层连接极多，导致：
1. **梯度稀疏**：每次更新只有少数Embedding被激活，大量参数训练不充分
2. **训练时间长**：收敛慢，迭代周期长
3. **不稳定**：随机初始化导致不同ID的Embedding质量差异大

**FNN的解决方案：**
```
FM预训练 → 得到每个Field的隐向量
    ↓
作为DNN Embedding层的初始化（而非随机）
    ↓
Fine-tune整个模型
```

**工程意义：** 预训练-微调范式大幅提升了ID类特征Embedding的质量和训练效率，后续成为工业界标配（如Word2Vec→BERT的NLP范式迁移到推荐系统）。

---

### C3. DIN模型中Attention机制是如何工作的？Score如何计算？

**参考答案（美团一面原题追问）：**

**DIN（Deep Interest Network）**，阿里妈妈 2018 KDD，专门解决用户历史行为序列建模问题。

**背景痛点：** 传统模型（如DeepFM）将用户所有行为序列压缩为固定向量，忽略了对不同候选物品的个性化兴趣。

**Attention机制原理：**
```
用户行为序列：[item_1, item_2, ..., item_n]（点击/浏览过的物品）
候选物品：     target_item

对每个行为item_i，计算与target_item的注意力权重：

attention_score_i = V_i · W · V_target
（等价于：激活单元(ReLU(W1·V_i + W2·V_target + b)) · V_target）

weighted_sequence = Σ(attention_score_i / Σscore) × V_i

最终序列表示 = weighted_sequence（代替简单的Pooling）
```

**关键点：**
- **Local Activation**：只关注与当前候选相关的历史行为，不相关的行为权重衰减
- **Dice激活函数**：DIN提出的改进，替代PReLU，根据数据分布自适应调整激活
- **GAUC评估**：Group AUC，按用户分组计算AUC，更适合评估序列模型

**面试追问：知道原文里是怎么做的吗？**
→ 原文使用两阶段：①计算score = σ(W1·V_i + W2·V_target + b)；②加权求和序列向量作为用户兴趣表示。注意：score需要做softmax归一化或直接加权。

---

### D1. 手撕：Mask Attention 实现

**百度二面原题（参考实现）：**

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

def masked_attention(Q, K, V, mask=None):
    """
    Q, K, V: (batch, seq_len, d_k)
    mask: (batch, seq_len, seq_len) - True表示需要mask的位置
    返回: attention后的输出 (batch, seq_len, d_k)
    """
    d_k = Q.size(-1)
    
    # 1. 计算注意力分数
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    # scores: (batch, seq_len, seq_len)
    
    # 2. 应用mask（将mask位置设为-inf）
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    # 3. softmax归一化
    attention_weights = F.softmax(scores, dim=-1)
    # attention_weights: (batch, seq_len, seq_len)
    
    # 4. 加权求和
    output = torch.matmul(attention_weights, V)
    # output: (batch, seq_len, d_k)
    
    return output, attention_weights


# 多头注意力版本（面试加分）
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)
    
    def forward(self, Q, K, V, mask=None):
        batch = Q.size(0)
        
        # 线性映射 + 分头
        Q = self.W_Q(Q).view(batch, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_K(K).view(batch, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_V(V).view(batch, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Mask Attention
        attn_output, _ = masked_attention(Q, K, V, mask)
        
        # 合并多头 + 线性输出
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch, -1, self.num_heads * self.d_k)
        return self.W_O(attn_output)
```

**面试加分点：**
- 解释 `masked_fill(mask == 0, -1e9)` 的原因：softmax(-inf) = 0，实现"忽略该位置"的效果
- 多头注意力的意义：多个子空间并行学习不同的注意力模式
- 复杂度分析：O(n²·d)，可提到FlashAttention的优化思路

---

### D2. 手撕：重排链表

**美团一面原题：**

```python
# 方法：快慢指针找中点 + 链表逆序 + 合并
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reorderList(head: ListNode):
    if not head or not head.next:
        return head
    
    # 1. 快慢指针找中点
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    
    # 2. 逆序后半段
    prev, curr = None, slow.next
    slow.next = None  # 断开链表
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    
    # 3. 合并两个链表（交替插入）
    first, second = head, prev
    while second:
        tmp1 = first.next
        tmp2 = second.next
        first.next = second
        second.next = tmp1
        first = tmp1
        second = tmp2

# 时间复杂度: O(n)，空间复杂度: O(1)
```

---

### D3. 手撕：数组Top-k，要求复杂度小于快排

**美团二面原题（复杂度要求 O(n)）：**

```python
import random

def topk(arr, k):
    """
    使用快速选择（QuickSelect）算法，平均O(n)，最坏O(n²)
    期望复杂度 O(n)，优于快排的 O(n log n)
    """
    def partition(left, right, pivot_idx):
        pivot = arr[pivot_idx]
        # 将pivot移到末尾
        arr[pivot_idx], arr[right] = arr[right], arr[pivot_idx]
        store_idx = left
        for i in range(left, right):
            if arr[i] > pivot:  # 大顶堆，选前k大
                arr[store_idx], arr[i] = arr[i], arr[store_idx]
                store_idx += 1
        arr[right], arr[store_idx] = arr[store_idx], arr[right]
        return store_idx
    
    left, right = 0, len(arr) - 1
    while True:
        pivot_idx = random.randint(left, right)  # 随机选pivot避免最坏情况
        pos = partition(left, right, pivot_idx)
        if pos == k - 1:
            return arr[:k]
        elif pos > k - 1:
            right = pos - 1
        else:
            left = pos + 1

# 复杂度分析：
# - 每次partition: O(n)
# - 期望递归深度: O(log n)（随机pivot保证）
# - 总体期望: O(n)
# - 最坏: O(n²)（但随机化后概率极低）
# - 空间: O(log n) 递归栈
```

**追问：如果数据量太大无法放入内存怎么办？**
→ 外部排序：分块读入内存 → 每块内部Top-k → 归并。或者使用BFPRT最坏情况线性选择算法（保证最坏O(n)）。

---

### E1. 特征选择的方式有哪些？Filter/Wrapper/Embedded的区别？

**参考答案：**

| 方法 | 原理 | 优点 | 缺点 | 代表算法 |
|------|------|------|------|---------|
| **Filter** | 按统计指标（方差、相关系数）过滤，与模型无关 | 速度快，不易过拟合 | 忽略特征与模型关系 | 方差阈值、L1/卡方检验、互信息 |
| **Wrapper** | 用模型效果评估特征子集，启发式搜索 | 考虑模型-特征交互 | 计算量大，速度慢 | 递归特征消除（RFE）、前向/后向搜索 |
| **Embedded** | 训练时自动评估特征重要性（如树模型/XGB/LR正则） | 兼具速度和效果 | 依赖特定模型 | L1正则、Lasso、树模型特征重要性 |

**面试加分：** 实际工业界推荐系统中，通常先用Filter快速过滤明显无用特征（低方差、高缺失率），再用Embedded方法（XGB/LightGBM的特征重要性）精筛，最后用Wrapper做局部调优。

---

### E2. 特征交叉的方式有哪些？笛卡尔积有什么优缺点？

**参考答案：**

#### Dense特征交叉：
- **乘积交叉**：特征A × 特征B（如用户年龄 × 商品价格）
- **分桶交叉**：对连续特征分桶后交叉（如年龄段 × 价格段）
- **多项式交叉**：二阶/高阶多项式

#### ID特征交叉：
- **笛卡尔积（Cartesian Product）**：
  - 若A有m个取值，B有n个取值，交叉后得 m×n 个组合特征
  - 例：(经度, 纬度) = 精确地理区域
- **哈希交叉**：笛卡尔积后做哈希映射，控制在固定维度，解决稀疏爆炸问题

**笛卡尔积优缺点：**

| 优点 | 缺点 |
|------|------|
| 表达精确的特征组合含义 | 稀疏度高（大量组合无数据） |
| 工业界可解释性强 | 维度爆炸（m×n可能达百万级） |
| 与Wide模型天然配合 | 泛化能力弱，未见组合无法学习 |
| 离线可枚举+Hash编码可控 | 需人工设计，不适合高阶交叉 |

> **面试追问：** 如何在大规模ID特征上做高效的特征交叉？  
> 答：① 哈希技巧（Hashing Trick）压缩维度；② 分层交叉：低阶用笛卡尔积，高阶用DNN自动学习；③ Field嵌入：同一Field内先Pooling再交叉（FFM/FM思路）。

---

### F1. 大模型和推荐系统有哪些可结合的点？

**参考答案（美团二面追问热点）：**

| 结合方向 | 具体内容 | 工业实践 |
|---------|---------|---------|
| **商品理解** | LLM对商品标题/描述做语义编码，生成商品Embedding | 阿里妈妈、京东 |
| **用户意图理解** | LLM解析用户query/行为序列的深层意图 | 搜索推荐 |
| **冷启动** | LLM生成新物品/用户的描述性内容，解决冷启动 | 新闻推荐 |
| **跨域推荐** | 大模型作为知识图谱提供跨域知识迁移 | 多业务线公司 |
| **推荐理由生成** | 生成可解释的推荐理由，提升用户信任 | 内容种草 |
| **个性化Prompt** | 用LLM为用户动态生成个性化推荐Prompt | 实验阶段 |

**商品理解/描述的典型方法：**
```python
# 伪代码：LLM生成商品语义向量
product_text = f"商品名称：{title}，描述：{desc}，类别：{category}"
embedding = llm_encode(product_text)  # 768维语义向量
# 注入推荐系统作为侧信息特征
```

> **面试考察点：** 大模型+推荐是2024-2026年最前沿的面试热点。面试官期望你了解至少2-3个工业落地案例，并有自己的思考（如大模型幻觉对推荐系统的影响、推理成本问题）。

---

### F2. LongLoRA和LoRA的区别是什么？

**参考答案（美团一面技术题）：**

| 对比维度 | LoRA | LongLoRA |
|---------|------|---------|
| **提出者** | Microsoft | 2023年（具体团队） |
| **核心问题** | 通用大模型微调 | **长上下文（Long Context）大模型微调** |
| **改进点** | 低秩适配器更新LLM权重 | 在LoRA基础上增加**S²-Attn（Shifted Window Attention）** |
| **上下文长度** | 标准2K~8K | 支持**百万级Token**（如LongLoRA-7B支持262K） |
| **效率** | 参数量减少2/3，显存节省2/3 | 比LoRA更高效处理长序列 |
| **适用场景** | 全领域微调 | 书籍摘要、长文档理解、推荐序列建模 |

**LongLoRA核心技术：**
1. **S²-Attn**：将长序列划分为多个窗口，只在窗口内做Attention，减少O(n²)计算
2. **LoRA on S²-Attn**：对Attention的QKV投影矩阵应用LoRA，而非对全部参数
3. **渐进式训练**：从短上下文逐步扩展到长上下文

> **面试追问：** 在推荐系统中，LongLoRA可用于微调长行为序列（如用户最近1000次点击）建模。

---

## 四、高频考点速查表

| 考点 | 掌握程度 | 关联问题 |
|------|---------|---------|
| ✅ 多目标建模（MMOE/ESMM/PLE） | **必须精通** | 跷跷板现象、SSB解决、CGC结构 |
| ✅ 双塔模型（DSSM） | **必须掌握** | 优缺点、实时性问题、ANN召回 |
| ✅ Wide&Deep / DeepFM | **高频必问** | Wide记忆 vs Deep泛化，二阶交叉 |
| ✅ DIN/DIEN序列模型 | **高频必问** | Attention Score计算、兴趣建模 |
| ✅ 样本选择偏差（SSB） | **高频必问** | ESMM解决方案 |
| ✅ AUC评估指标 | **高频基础** | 含义、计算公式、与GAUC区别 |
| ✅ Mask Attention手撕 | **工程coding** | softmax前的mask操作 |
| ✅ TopK手撕（快选） | **工程coding** | O(n)复杂度，随机Pivot |
| ✅ 大模型+推荐 | **前沿热点** | 商品理解、冷启动、多目标结合 |
| ✅ 特征工程基础 | **基础高频** | Filter/Wrapper/Embedded、特征交叉 |

---

## 五、下期预告

下期将重点搜集并解析以下高频考点：
1. **DIEN模型**：GRU+Attention序列兴趣演化的深层建模
2. **Graph Embedding**：Node2Vec、DeepWalk、EGES在推荐召回中的应用
3. **在线效果优化**：ABTest实验设计、CTR模型上线后效果下降的处理思路
4. **系统设计题**：如何设计一个短视频推荐系统的召回模块？

---

*本报告由小M（AI信息管家）自动整理 | 数据来源：牛客网、腾讯云、CSDN、知乎等主流技术社区*
*如有问题，欢迎反馈补充！*
