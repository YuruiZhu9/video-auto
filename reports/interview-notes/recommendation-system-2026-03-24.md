---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: c289bb5b27fc2ad7219a671cf46c4a91
    PropagateID: c289bb5b27fc2ad7219a671cf46c4a91
    ReservedCode1: 3046022100e06ab4d5d77202607943c4740a7fbddb6e84b829f4a8762c65fce729079a76550221008a8fb0cc0b12820dc00e97cc87ca4801af46437c44d2648e80f2bcab0de86c02
    ReservedCode2: 304402206ffbaae9c4c014554cd62310b330ec870b03db37510959ecd59df15f04d7a8d902204cc4077b15dba91af5394c587ec41d9fcf754efc15b9473ae20d19edb39adb7a
---

# 推荐系统算法面经每日搜集 — 2026-03-24

> 搜集时间：2026-03-24 | 轮次：每日定时任务 | 来源：牛客网、腾讯云开发者社区、知乎、CSDN

---

## 一、当日面经来源

| 来源平台 | 面经标题 | 岗位 | 亮点 |
|---|---|---|---|
| 腾讯云开发者社区 | 腾讯推荐算法实习面经（已OC） | 推荐算法实习 | LR推导、YouTubeDNN、ItemCF、工程题、完整答案 |
| 牛客网 | 小红书推荐算法工程师实习面经 | 推荐算法实习 | 三轮技术面全流程、冷启动、Debias、系统设计 |
| 知乎专栏 | DSSM双塔模型面试题汇总 | 推荐算法 | 原理/损失函数/推理/缺点全解析 |
| 知乎专栏 | 推荐系统常见面试问题（持续更新） | 推荐系统 | ML/DL基础、Multi-task、Debias高频题 |
| CSDN博客 | 推荐系统经典面试题（附答案） | 推荐系统 | 召回评估、多任务学习、特征选择 |

---

## 二、面试问题清单

> 共整理 **28 道高频核心问题**，按模块分类，涵盖：ML/DL基础、推荐链路、模型原理、工程实践、开放场景。

---

## 三、逐题详细解析

---

### 【模块一：机器学习与深度学习基础】

---

#### Q1：LR（逻辑回归）的损失函数是什么？手推梯度。

**答案：**

**损失函数（对数损失 / Log Loss）：**
$$
L(y, p) = -[y \cdot \log(p) + (1-y) \cdot \log(1-p)]
$$
其中 $p = \sigma(w^T x) = \frac{1}{1 + e^{-w^T x}}$。

**梯度推导：**
$$
\frac{\partial L}{\partial w_j} = (p - y) \cdot x_j
$$
推导过程：
1. $p' = p(1-p)$
2. $\frac{\partial L}{\partial p} = -\frac{y}{p} + \frac{1-y}{1-p} = \frac{p-y}{p(1-p)}$
3. $\frac{\partial p}{\partial w_j} = p(1-p) \cdot x_j$
4. 链式法则 $\Rightarrow \frac{\partial L}{\partial w_j} = (p-y) \cdot x_j$

**面试要点：**
- LR 本质是 **分类** 模型（非回归），但损失函数叫"对数损失"
- 梯度形式极其简洁：**预测误差 × 特征值**
- 正则项（L1/L2）加到损失函数中即可

---

#### Q2：L1正则化和L2正则化的区别？各自的优势场景？

**答案：**

| 对比维度 | L1正则化（Lasso） | L2正则化（Ridge） |
|---|---|---|
| 公式 | $\lambda \|w\|_1 = \lambda \sum_j \|w_j\|$ | $\lambda \|w\|_2^2 = \lambda \sum_j w_j^2$ |
| 解的稀疏性 | ✅ 产生稀疏解，可做特征选择 | ❌ 解是平滑的，无稀疏性 |
| 解的特点 | 解在顶点（某些维度为0） | 解趋向于各维度均匀小的值 |
| 计算代价 | 不可导，需近端梯度（如FTRL） | ✅ 可导，优化简单 |
| 适用场景 | 特征多、需要自动筛选 | 防止过拟合、所有特征都有用 |

**面试要点：**
- L1 会让权重恰好为0 → 等价于做了**特征选择**
- L2 让权重整体缩小但不为0 → 防止权重过大
- 实际工程中常两者结合（Elastic Net）
- FTRL 为什么用 L1：因为在线学习场景需要**稀疏模型**（省内存 + 加速推理）

---

#### Q3：FTRL是什么？优势是什么？

**答案：**

FTRL（Follow The Regularized Leader）是 Google 2013 年提出的在线学习算法，专门用于大规模稀疏逻辑回归。

**核心公式：**
$$
w_{t+1} = \arg\min_w \left( \sum_{i=1}^t g_i \cdot w + \frac{1}{2} \sum_{i=1}^t \sigma_i \|w - w_i\|^2 + \lambda_1 \|w\|_1 \right)
$$

**两个关键组成：**
1. **在线优化**：每来一个样本更新一次，适合流式数据
2. **L1正则化**：产生稀疏解，节省内存和计算

**FTRL 的核心优势：**
- **稀疏性**：在线学习 + L1，正样本快速收敛到稀疏解，线上只存非零权重
- **灵活性**：Per-coordinate 学习率（每个维度独立学习率），对稀疏特征友好
- **效率**：适合千亿特征、TB级数据的在线训练

**面试要点：**
- 与 SGD 对比：SGD 是全局学习率，FTRL 是 per-coordinate 自适应学习率
- FTRL 在 CTR 预估场景是经典方案（Google 2013 论文：Ad Click Prediction）

---

#### Q4：AUC 是如何实现的？它对正负样本采样是否敏感？

**答案：**

**AUC 定义：** ROC 曲线（True Positive Rate vs. False Positive Rate）下的面积，取值范围 [0.5, 1]。

**计算方法：**
1. **公式法（最常用）：**
$$
\text{AUC} = \frac{\sum_{i \in \text{正样本}} \text{rank}(i) - \frac{n(n+1)}{2}}{n \times m}
$$
其中 rank(i) 是正样本在所有样本预测分数排序中的序号。

2. **概率解释：** 随机抽一个正样本和负样本，正样本排在负样本前面的概率。

**对采样的敏感性：**
- **理论上 AUC 不受负采样影响**（因为 AUC 只看正负样本的相对排序）
- 但若采样比例极端（如正:负 = 1:100000），分布偏移会影响模型预测值的校准
- **排序能力（auc）稳定，分值校准（CTR预估的点击率绝对值）会变**，需要用负采样矫正公式

**面试要点：**
- AUC 只关心 **排序** 不关心绝对值 → 对采样天然鲁棒
- 负采样后用 LR 的 logit 矫正：$\hat{p} = \frac{p}{p + (1-p)/\gamma}$（\gamma 为采样比）

---

#### Q5：梯度下降方法有哪些？SGD/Momentum/Adagrad/RMSprop/Adam 的区别？

**答案：**

| 优化器 | 更新公式核心 | 特点 |
|---|---|---|
| SGD | $w \leftarrow w - \eta \cdot g_t$ | 简单，对稀疏特征友好 |
| Momentum | $v \leftarrow \beta v + \eta g_t$ | 动量累积，加速收敛，减小震荡 |
| Adagrad | $w \leftarrow w - \frac{\eta}{\sqrt{G_{tt}} + \epsilon} g_t$ | 自适应学习率，适合稀疏特征；缺点：学习率持续衰减 |
| RMSprop | $E[g^2] \leftarrow \beta E[g^2] + (1-\beta)g_t^2$ | 指数滑动平均，解决 Adagrad 学习率衰减问题 |
| Adam | $m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t$（一阶矩）；$v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2$（二阶矩） | 结合动量 + 自适应学习率，工程最常用，**推荐系统排序模型默认选择** |

**面试要点：**
- Adam 在推荐系统排序阶段**几乎默认使用**，收敛快但泛化略差
- 如果追求泛化性能，用 **AdamW**（带权重衰减的 Adam）
- Bias correction：Adam 的 m 和 v 初始值偏0，需要做矫正

---

#### Q6：Batch Normalization 的原理？为什么有用？

**答案：**

**核心思想：** 对每一层的输入进行标准化（均值0、方差1），再进行仿射变换（scale + shift）。

**公式：**
$$
\hat{x}_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}, \quad y_i = \gamma \hat{x}_i + \beta
$$

其中 $\gamma, \beta$ 是可学习参数。

**为什么有用（4点）：**
1. **Internal Covariate Shift**：深层网络训练时，前层参数变化导致后层输入分布变化（ICS），BN 把分布稳定下来
2. **梯度流更顺畅**：标准化让梯度更平滑，收敛更快
3. **对权重初始化不那么敏感**：不那么挑初始化方法
4. **正则化效果**：每个 batch 的均值/方差有噪声，等价于做了轻微正则化

**注意：**
- 训练时用 batch 统计量；推理时用全局统计量（移动平均）
- 警惕 batch_size 过小（均值/方差不准）；推荐系统场景 batch_size 通常够大

---

#### Q7：交叉熵作为损失函数相比 MSE 有何优势？

**答案：**

**核心原因（两点）：**

**① 梯度形式更优（梯度消失问题）：**
- MSE：$\frac{\partial L}{\partial w} = (f-y) \cdot f'(z) \cdot x$，梯度包含 $f'(z)$（sigmoid/softmax 导数）
- 当 $f$ 接近 0 或 1 时，$f'(z)$ 趋近于 0 → 梯度消失 → 训练慢
- 交叉熵：$\frac{\partial L}{\partial w} = (f-y) \cdot x$，**不包含激活函数导数**，梯度直接与预测误差成正比

**② 物理意义（KL散度视角）：**
- 交叉熵 $H(p,q) = -\sum p(x) \log q(x)$
- 真实分布 $p$ 固定时，最小化 $H(p,q)$ = 最小化 $KL(p \| q)$
- MSE 没有这个概率解释，直接优化"欧氏距离"而非"分布差异"

**面试要点：**
- 面试被问到"为什么用交叉熵而不是MSE"，必答：梯度消失 + KL散度/概率解释

---

### 【模块二：推荐系统链路与模型原理】

---

#### Q8：推荐系统的全链路是怎样的？各阶段的作用和常用模型？

**答案：**

推荐系统典型全链路（工业界 4 阶段）：

```
┌─────────────────────────────────────────────────────────────┐
│  1. 召回（Recall）    ──  从千万/亿级 → 几百~上千个候选        │
│  2. 粗排（Pre-Rank）  ──  从几百个   → 几十个候选              │
│  3. 精排（Rank）      ──  从几十个   → Top N 排序              │
│  4. 重排（Re-Rank）   ──  打散/多样性/业务规则 → 最终展示      │
└─────────────────────────────────────────────────────────────┘
```

| 阶段 | 目标 | 延迟要求 | 常用模型 |
|---|---|---|---|
| 召回 | 快速覆盖用户潜在兴趣 | ms级，QPS极高 | CF类（ItemCF/UserCF）、DSSM双塔、Graph Embedding、YouTubeDNN |
| 粗排 | 召回结果二次筛选 | ~10ms | 轻量级DSSM、简版DeepFM |
| 精排 | 精细打分排序 | ~100ms | DeepFM、Wide&Deep、DIN、DIEN、MMOE |
| 重排 | 多样性/业务干预 | ~5ms | MMR、 DPP、 DQN |

**面试要点：**
- 召回路演化和工程权衡是高频考点：为什么不用精排模型做召回？（太慢，双塔结构的核心价值是解耦 user/item 计算）
- 重排是2024-2025年面试新增热点：大模型辅助重排、上下文感知重排

---

#### Q9：YouTubeDNN 模型的原理？正负样本如何构造？

**答案：**

YouTubeDNN（2016）出自论文《Deep Neural Networks for YouTube Recommendations》，是工业级召回模型的里程碑。

**模型结构：**
```
用户特征（人口属性 + 行为序列） → DNN → User Embedding
                                               ↓
Item Embedding（预训练，来自 Item2Vec 或单独训练）
                                               ↓
                                        ANN 检索 Top-K
```

**关键设计：**
1. **训练**：sampled softmax（避免全量 softmax 计算）
2. **服务**：离线生成 User Vector，在线对全量 Item 做 ANN 检索

**正负样本构造：**
| 样本 | 定义 | 说明 |
|---|---|---|
| 正样本 | 用户点击的 Item | 显式正反馈 |
| 负样本 | 未点击的 Item（随机采样） | 隐式负反馈 |

**注意：**
- 负采样策略很重要！随机负采样（Random Negative Sampling, RNS）是基础
- 高级策略：hard negative mining（难负例挖掘），如 Google DPMM 论文做法

---

#### Q10：ItemCF 和 UserCF 的区别？UserCF 的倒排表优化？

**答案：**

**ItemCF（基于物品的协同过滤）：**
- 核心思想：给用户推荐与他历史喜欢物品**相似**的物品
- 相似度定义：$\text{sim}(i,j) = \frac{|U_i \cap U_j|}{\sqrt{|U_i| \cdot |U_j|}}$（余弦相似度）
- 适用场景：电商（如"看了又看"）、物品相对稳定

**UserCF（基于用户的协同过滤）：**
- 核心思想：找到与用户相似的用户群，推荐那些用户喜欢的东西
- 相似度定义：$\text{sim}(u,v) = \frac{|I_u \cap I_v|}{\sqrt{|I_u| \cdot |I_v|}}$
- 适用场景：社交推荐、新闻推荐（用户兴趣分散）

**UserCF 倒排表优化：**
- 问题：计算所有用户对的时间/空间复杂度高
- 优化：建立 **Item → Users 倒排表**，直接找两个物品的共同用户集合
- 进阶：考虑用户活跃度（活跃用户对相似度贡献权重低）

**面试要点：**
- ItemCF vs UserCF 选择：物品稳定选ItemCF（电商），用户社交关系重要选UserCF
- 大数据量下可结合 ANN（如 Faiss）做近似相似度计算

---

#### Q11：Wide&Deep 的原理？为什么 Wide 和 Deep 需要联合训练？

**答案：**

Wide&Deep（Google Play, 2016）是推荐系统精排模型的里程碑架构。

**模型结构：**
```
Wide部分（左侧）        Deep部分（右侧）
线性模型                DNN模型
记忆能力                泛化能力

输入：稀疏特征（wide）+ 稠密特征（deep）→ 联合输出
```

**Wide 部分：**
- 本质是一个广义线性模型：$y = W_{wide}^T [x, \phi(x)] + b$
- 擅长**记忆**（Memorization）：记住哪些特征组合有效（如"用户安装了X且在搜Y"）
- 输入是原始稀疏特征 + 人工交叉特征（如AND(category=购物, gender=女)）

**Deep 部分：**
- DNN：Sparse Embedding → 全连接层
- 擅长**泛化**（Generalization）：探索未出现的特征组合

**为什么联合训练（Joint Training）：**
- Wide 侧和 Deep 侧 **同时** 优化，而非分别训练再 ensemble
- 联合训练时 Wide 的残差梯度直接传给 Deep，两个组件互相增强
- Wide 侧学习浅层交叉，Deep 侧学习深层表示，互相补充
- 如果分别训练（ensemble），Wide 和 Deep 各自独立，无法互相补偿

---

#### Q12：DeepFM 的原理？与 Wide&Deep 的区别？

**答案：**

DeepFM（华为诺亚方舟实验室，2017）去掉 Wide&Deep 的人工特征交叉，改用 **FM（因子分解机）** 自动学二阶交叉。

**模型结构：**
```
Sparse Features → FM Component（二阶交叉）──┐
                    ↓                        │→ 输出
                Deep Component（DNN） ────────┘
```

**核心优势（相比 Wide&Deep）：**
1. **无需人工特征工程**：FM 自动学所有二阶特征交叉
2. **低参数量**：FM 交叉层参数量 O(km)，而不像显式枚举交叉特征那样爆炸
3. ** Wide&Deep 的 Wide 需要人工构造交叉特征**，DeepFM 完全端到端

**FM 层公式：**
$$
\sum_{i=1}^{n} \sum_{j=i+1}^{n} \langle V_i, V_j \rangle x_i x_j
$$
通过共享 Field Embedding，复杂度从 $O(kn^2)$ 降到 $O(kn)$

---

#### Q13：DIN（Deep Interest Network）的原理？DIEN 做了哪些改进？

**答案：**

**DIN（阿里妈妈，KDD 2018）：**
- 解决：用户行为序列中只有部分历史行为与当前候选物品相关
- 核心：**Attention 机制**（Activation Unit）对行为序列加权
- Attention Score = $\sigma(W_1 \cdot e_i + W_2 \cdot a_j + W_3 \cdot e_i \odot a_j + b)$
- 对与候选 Item 越相关的历史行为，权重越大

**DIEN（阿里妈妈，AAAI 2019）：**
- DIN 只加权，不建模序列的**演化**
- DIEN 两层改进：
  1. **兴趣抽取层（Interest Extractor Layer）**：用 GRU 从行为序列中抽取隐状态 $h_t$
  2. **兴趣演化层（Interest Evolving Layer）**：再用 Attentive GRU，让兴趣随时间演化，对目标 Item 的注意力影响演化方向
- 核心洞察：用户兴趣是**动态演化**的（如买完手机后买配件）

---

#### Q14：DSSM 双塔模型的原理？正负样本？推理流程？缺点？

**答案：**

**DSSM（Deep Structured Semantic Model），微软 2013：**
- 核心思想：Query 和 Document 分别通过 DNN 编码为语义向量，在语义空间计算相似度

**正负样本构造：**
- 正样本：Query 点击的 Document（通常每个 Query 有几个正样本）
- 负样本：随机采样未点击的 Document（通常 4 个负样本）

**推理流程：**
1. **离线**：Doc 塔输出所有 Doc 的 Embedding，存入 Faiss 索引
2. **在线**：Query 塔输出 User Embedding
3. **检索**：Faiss 中 ANN 检索 Top-K 相似 Doc

**DSSM 缺点：**
- **词袋表示**：用 Bag-of-Words，没有考虑词的上下文语义
- 改进方案：用 RNN/CNN 对文本做序列建模（对应 LSM/CLSM）

**面试要点：**
- DSSM 是召回阶段最经典的模型之一，双塔结构是其核心优势（user/item 分离计算）
- Word Hashing：解决输入稀疏问题（30K 词汇表 → 10K 维度，碰撞率 < 0.0044%）

---

#### Q15：多任务学习（Multi-Task Learning）在推荐系统中的应用？MMoE 的原理？

**答案：**

多任务学习的典型场景：同时预测 CTR（点击率）和 CVR（转化率）。

**为什么需要多任务：**
- 数据共享：两个任务的相关性可以利用，减少单独建模的信息浪费
- 统一服务：一次推理得到多个分数，减少工程复杂度

**Hard Parameter Sharing（硬共享）：**
- 所有任务共享底层 DNN 参数
- 优点：参数量少，不易过拟合
- 缺点：任务冲突时效果下降

**MMoE（Multi-gate Mixture-of-Experts，Google 2018）：**
- 核心思想：每个任务有自己的 Gate（门控网络），动态选择 Expert 组合
$$
y_k = \sum_{i=1}^{n} g_k(i) \cdot f_i(x), \quad g_k = \text{Softmax}(W_{gk} \cdot x)
$$
- 多个 Expert（通常是 DNN）各自独立建模不同方面的知识
- 每个任务有自己的 Gate，选择对当前任务最重要的 Expert 输出
- 解决硬共享的任务冲突问题

**ESSM（阿里，ESMM 2018）：**
- 解决 CVR 样本稀疏（转化行为比点击少得多）
- 全链路建模：同时学习 CTR + CVR，CTCVR = CTR × CVR
- CTCVR 和 CTR 用曝光数据训练，CVR 用后续点击转化数据训练

---

### 【模块三：工业实践与工程问题】

---

#### Q16：推荐系统怎么做新用户冷启动？

**答案：**

冷启动是推荐系统经典难题，分**用户冷启动**和**物品冷启动**：

**用户冷启动（5种方案）：**
1. **热门内容兜底**：新用户推热门/高评分内容，等行为积累后再切换个性化
2. **注册信息**：利用年龄、性别、职业、地域等进行粗粒度人群匹配
3. **初次兴趣收集**：注册时让用户选择感兴趣的内容分类/标签（微博、小红书做法）
4. **跨域 Transfer**：用其他平台行为数据（如微信读书阅读记录→推荐）
5. **上下文信息**：设备型号、操作系统、地理位置等作为冷启特征

**物品冷启动（新 Item 上架）：**
1. **内容特征匹配**：用 Item 的标题/类目/标签找相似 Item 的用户群体
2. **EE 探索**：给新 Item 一定曝光流量（Exploration & Exploitation）
3. **Bandit 算法**：用 LinUCB 或 Thompson Sampling 自适应探索
4. **双塔冷启动**：新 Item 用 Content Embedding（不依赖行为数据）

**面试要点：**
- 核心思路：**先用尽量准的信息（内容/人口统计学），再逐步过渡到个性化**
- 要提到 EE（Exploration & Exploitation）平衡，不能只曝光热门

---

#### Q17：推荐系统中的 Debias（去偏）方法有哪些？

**答案：**

推荐系统天然存在多种 Bias，是 2024-2025 面试热点。

**① Selection Bias（选择偏差）：**
- 来源：用户只对自己感兴趣的物品打分，导致评分数据非随机缺失（MNAR）
- 解决：数据填充（Data Imputation）+ 倾向分数（Propensity Score）

**② Exposure Bias（曝光偏差）：**
- 来源：用户只能看到曝光的物品，不曝光 ≠ 不喜欢
- 解决：置信权重（每个样本根据曝光概率加权）+ 采样纠偏

**③ Position Bias（位置偏差）：**
- 来源：用户倾向点击靠前位置的物品，位置越靠前点击率越高
- 解决：位置特征加入模型（Position-Dependent CTR）；或单独建模位置效应（如 PAL 模型）

**④ Conformity Bias（一致性偏差）：**
- 来源：用户评分受群体影响，趋向与他人一致
- 解决：对社会群体/流行度效应建模

**⑤ Popularity Bias（热门偏差）：**
- 来源：模型过度推荐热门物品，冷门优质物品得不到曝光
- 解决：加一个正则项惩罚流行度、re-rank 阶段做多样性干预

**面试要点：**
- 工业界最常用：**位置偏差建模**（位置特征消偏）+ **曝光偏差加权**
- 推荐系统 Debias 是论文方向热点（如 UCB/IPS 类方法）

---

#### Q18：在线学习（Online Learning）是什么？为什么要用？有哪些方法？

**答案：**

**在线学习的定义：** 获得一个新样本的同时更新模型参数，实现模型的实时更新。

**为什么要用（3个原因）：**
1. **实时捕捉新趋势**：用户兴趣、热点事件随时变化，在线学习能快速适应
2. **减少模型延迟**：不像离线训练需要等数据积累到一定量
3. **应对数据分布漂移（Concept Drift）**：618/双11等活动期间用户行为模式剧烈变化

**核心方法：**
| 方法 | 特点 |
|---|---|
| **SGD / Streaming SGD** | 每条样本更新一次，快但稀疏性差 |
| **FTRL** | Per-coordinate 学习率 + L1 稀疏，**工业推荐 CTR 场景首选** |
| **Online Boosting** | 在线集成学习 |
| **DRN（Deep Reinforcement Learning Network）** | 强化学习驱动，2018 年提出，探索与利用平衡 |

**FTRL 在在线学习中的优势（高频追问）：**
- Per-coordinate 学习率 → 对稀疏特征自适应
- L1 正则 → 产生稀疏解，线上只存非零权重，内存占用极低
- 比 SGD 的全局学习率更精准

---

#### Q19：召回阶段如何离线评估模型好坏？

**答案：**

**核心挑战**：召回没有 ground truth（不知道用户真正会喜欢什么），无法直接用 AUC/RMSE。

**三种评估方案：**

**方案一：召回率（最直接）**
$$
\text{Recall@K} = \frac{|\text{召回集中的正样本}|}{|\text{全部正样本}|}
$$
- 构造测试集：用户最近一次交互的正样本定义为准召集中"正样本"
- 衡量召回模型能不能把真正的正样本召回来

**方案二：Recall@K 配合排序 AUC**
- 同一排序模型（如精排模型）给所有召回结果打分
- 用精排 AUC 间接评估召回质量：召回好→排序效果就好

**方案三：在线 A/B 测试（最终标准）**
- 离线指标只是代理，在线才是最终裁判
- 看点击率、停留时长、转化率等业务指标

**面试要点：**
- 常用指标：Recall@K、MRR@K、NDCG@K、Hit Rate@K
- 不能只说 AUC，要说出为什么召回不能直接用 AUC

---

### 【模块四：系统设计与场景开放题】

---

#### Q20：多任务学习中，硬共享和软共享各自的优缺点？

**答案：**

**硬共享（Hard Parameter Sharing）：**
- 所有任务共享底层的部分 DNN 层
```
Task1 output ─┐
Task2 output ─┤→ [Shared Layers] → [Task-specific Output]
Task3 output ─┘
```
- **优点**：参数量少，不易过拟合（正则化效应）；工程实现简单
- **缺点**：任务之间有冲突时（尤其是任务相关性低），共享层被迫同时拟合不同目标，效果下降

**软共享（Soft Parameter Sharing）：**
- 每个任务有自己独立的 DNN，通过正则化/Loss 约束让参数接近
- 常见实现：MMoE、PLE、CGC
```
Task1: [DNN1]  ↗
Task2: [DNN2]  ─→ [Aggregation] → Output
Task3: [DNN3]  ↗
```
- **优点**：各任务独立建模，灵活性高，允许任务差异性
- **缺点**：参数量线性增长（每个任务一套 DNN），训练复杂度高

**推荐系统选择建议：**
- 任务高度相关（如CTR+CVR）→ 硬共享或 MMoE
- 任务相关性低（如点击+时长+负反馈）→ MMoE 或 PLE
- PLE（ Progressive Layered Extraction）：MMoE 的进化，分共享 Expert 和独有 Expert，避免负迁移

---

#### Q21：如果让你设计一个短视频推荐系统架构，你会怎么做？

**答案：**

**分层架构设计：**

```
┌────────────────────────────────────────────────────────┐
│  用户请求到达 → 召回（Multi-Recall）→ 粗排 → 精排 → 重排 │
└────────────────────────────────────────────────────────┘

召回层（Multi-Channel Recall）：              ← QPS 10万+
  • 协同过滤召回（ItemCF + UserCF）
  • DSSM 双塔向量召回
  • Graph Embedding 召回（DeepWalk/Node2Vec）
  • 热门内容兜底召回

粗排层（~10ms latency）：                    ← QPS 千级
  • 轻量级 MLPMini（双塔输出的 cosine score 粗排）

精排层（~100ms latency）：                   ← QPS 百级
  • 多任务：CTR 预估 + CVR 预估（MMoE）
  • 序列建模：DIN/DIEN
  • 特征：User Profile + Item 画像 + 上下文 + 行为序列

重排层（~5ms latency）：                     ← QPS 百级
  • MMR（Maximal Marginal Relevance）多样性
  • 位置消偏
  • 业务规则（广告穿插、打散同类别）
  • 大模型辅助重排（2025 趋势）
```

**核心工程挑战：**
1. **延迟约束**：全链路 P99 < 200ms，需要各阶段严格卡时
2. **特征延迟**：用户最新行为要尽快进入特征工程（实时特征更新）
3. **冷启动**：新用户/新视频兜底策略
4. **多样性 vs 准确性**：排序靠前的同质内容用户体验差，MMR 是经典解法

---

### 【模块五：经典代码题（手撕）】

---

#### Q22：LeetCode 215 — 数组中第 K 大的元素（腾讯一面算法题）

**答案：**

**方法一：小根堆（面试首选）：**
```python
import heapq

def findKthLargest(nums, k):
    # 建大小为 k 的小根堆
    heap = nums[:k]
    heapq.heapify(heap)
    
    for num in nums[k:]:
        if num > heap[0]:
            heapq.heapreplace(heap, num)  # O(logk)
    return heap[0]
```
- 时间复杂度：$O(n \log k)$
- 空间复杂度：$O(k)$

**方法二：快速选择（更快但最坏 O(n²)）：**
```python
import random

def findKthLargest(nums, k):
    target = len(nums) - k
    
    def partition(l, r):
        pivot = nums[r]
        p = l
        for i in range(l, r):
            if nums[i] <= pivot:
                nums[p], nums[i] = nums[i], nums[p]
                p += 1
        nums[p], nums[r] = nums[r], nums[p]
        return p
    
    l, r = 0, len(nums) - 1
    while True:
        p = partition(l, r)
        if p == target:
            return nums[p]
        elif p < target:
            l = p + 1
        else:
            r = p - 1
```
- 平均时间：$O(n)$；空间：$O(1)$

**面试要点：** 推荐系统面试手撕题首选堆排序（建堆/堆化过程要能讲清楚）

---

#### Q23：LeetCode 20 — 有效的括号（腾讯二面算法题）

**答案：**

```python
def isValid(s):
    stack = []
    mapping = {')': '(', ']': '[', '}': '{'}
    
    for char in s:
        if char in mapping:
            # 遇到右括号：栈顶不匹配则失败
            if not stack or stack[-1] != mapping[char]:
                return False
            stack.pop()
        else:
            # 遇到左括号：入栈
            stack.append(char)
    
    return len(stack) == 0
```
- 时间：$O(n)$，空间：$O(n)$

**腾讯面试额外追问**：如何扩展处理 `<>`、`「」` 等多类型括号？
- 用字典映射解决，统一逻辑即可

---

### 【模块六：前沿热点（2025-2026 面试新增）】

---

#### Q24：大模型（LLM）如何在推荐系统中落地？

**答案：**

**三种主流范式：**

**① LLM 作为推荐系统的特征增强：**
- 用 LLM 生成 Item 的文本描述 Embedding，丰富 Item 侧特征
- ChatGPT 生成推荐理由（Explainable Recommendation）

**② LLM 替代传统召回：**
- 将用户历史行为序列 + 当前候选拼成 Prompt
- 直接让 LLM 打分排序（zero-shot / few-shot）
- 代表：Chat-REC、P5（Personalized Prompt Tuning）

**③ 大模型辅助重排：**
- 用 LLM 对候选列表做多样性、相关性的综合重排
- 优势：可以建模长程依赖，考虑上下文连贯性

**挑战（面试要能说出来）：**
- **推理延迟**：LLM 推理太慢，工业推荐系统 P99 < 200ms，LLM 做不到
- **幻觉问题**：推荐结果不可控
- **对齐问题**：LLM 的能力不等于推荐能力

**工程解法：**
- LLM 只在重排阶段用（候选少），不用在召回/粗排
- 模型蒸馏：小模型学习大模型的排序能力

---

#### Q25：Graph Embedding 在推荐系统中的应用？

**答案：**

**核心思想**：将用户-物品交互图结构编码为低维 Embedding，捕捉协同信号。

**经典算法：**

| 算法 | 核心思想 | 代表应用 |
|---|---|---|
| DeepWalk | Random Walk + Word2Vec | 社交推荐 |
| Node2Vec | 有偏随机游走（DFS+BFS） | 淘宝"买了又买" |
| LINE | 一阶/二阶相似度建模 | 大规模图嵌入 |
| GraphSAGE | 邻居聚合（Mean/LSTM/Pool） | 归纳式推理（新节点） |
| GAT | 注意力机制加权邻居 | 微信朋友圈推荐 |

**工业应用场景：**
- **召回**：用户/物品图 Embedding 做向量检索
- **特征**：将 Graph Embedding 作为特征输入精排模型
- **冷启动**：新 Item 无行为，但有 Graph 结构，快速生成 Embedding

---

## 四、面试高频考点总结（按频次排序）

| 排名 | 考点 | 出现频率 |
|---|---|---|
| 1 | DSSM 双塔 / YouTubeDNN 召回原理 | ⭐⭐⭐⭐⭐ |
| 2 | Wide&Deep / DeepFM / DIN / DIEN | ⭐⭐⭐⭐⭐ |
| 3 | 多任务学习 MMoE / ESSM | ⭐⭐⭐⭐ |
| 4 | 冷启动 / Debias / EE | ⭐⭐⭐⭐ |
| 5 | LR 推导 / AUC / 梯度下降 | ⭐⭐⭐⭐ |
| 6 | 推荐全链路架构 | ⭐⭐⭐ |
| 7 | 在线学习 / FTRL | ⭐⭐⭐ |
| 8 | 大模型推荐落地 | ⭐⭐⭐ |
| 9 | Graph Embedding | ⭐⭐ |
| 10 | 手撕算法（堆/链表/快排） | ⭐⭐⭐⭐ |

---

> 📌 **本报告由定时 Agent 自动搜集整理，内容来源于牛客网、腾讯云、知乎等平台公开面经，仅供个人备考使用，请勿用于商业目的。**
> 📅 报告日期：2026-03-24 | 🤖 小M AI 助手整理
