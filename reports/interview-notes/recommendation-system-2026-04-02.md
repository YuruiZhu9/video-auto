---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a1f3ab73aba3f64748f13aaa418a2a91
    PropagateID: a1f3ab73aba3f64748f13aaa418a2a91
    ReservedCode1: 30460221009a9a98ebe6a73729876536199099d13ec927c2e8ebbb9b5152e5f10b9b5b86f6022100d6746db7f9a8e6062860cd5c23df0f73ebe0fc00d6d15d868b7fb15d82ae1f41
    ReservedCode2: 3046022100c3e59cc86d36b773f7128f858fc811f07a556e12775adbfb7fad3f6b22ef8a16022100b762488b408d104990be2b69c90f12355a7e28b06f2c8b0906567b52ef83d04f
---

# 推荐系统算法面经每日搜集 & 解析报告

**日期：** 2026-04-02（周四）
**岗位方向：** 推荐系统算法工程师
**搜集渠道：** 牛客网、知乎、CSDN、掘金、脉脉、小红书面经

---

## 一、当日面经来源

| 来源平台 | 典型面经 | 涉及公司/部门 |
|----------|----------|---------------|
| 牛客网 | 小红书推荐算法工程师实习三面、腾讯视频号推荐、美团搜索推荐一面 | 小红书、腾讯、美团、字节 |
| 知乎 | 推荐系统常见面试问题（持续更新111题） | 通用 |
| CSDN | 推荐算法岗面试题汇总（依图/探探/华为/字节/快手） | 依图、探探、华为、字节、快手、抖音电商 |
| 掘金 | 推荐系统四层架构深度拆解（2025面试热题） | 通用大厂 |
| 脉脉 | 推荐算法岗暑期实习面试总结 | 腾讯PCG、视频号 |

---

## 二、面试问题清单

> 以下问题均来自近期真实面经，按高频考点分类，⚡ 标记为高频必考题。

### 【全链路架构类】

1. 推荐系统的完整流程是什么？召回→粗排→精排→重排各自的作用是什么？
2. 召回和精排的差异点是什么？为什么排序结果比召回更准？
3. 多路召回的作用是什么？为什么要做多通道召回？
4. 粗排为什么要用双塔模型？它和精排模型的区别是什么？
5. 双塔模型在线上是如何检索的？用户塔和物品塔分别怎么更新？

### 【排序模型类】

6. ⚡ Wide&Deep 模型的原理是什么？Wide 侧和 Deep 侧分别负责什么？
7. ⚡ DeepFM 模型的原理是什么？它和 Wide&Deep 的区别是什么？
8. ⚡ DIN（深度兴趣网络）的原理是什么？Attention Score 是怎么计算的？
9. DIEN 相比 DIN 做了哪些改进？AUGRU 的作用是什么？
10. DSIN（深度会话兴趣网络）和 DIN 的区别是什么？
11. MMOE 和PLE 的区别是什么？多任务学习中如何解决任务间冲突？
12. ESMM 的原理是什么？为什么能解决样本选择偏差问题？

### 【召回模型类】

13. ⚡ 协同过滤（CF）的原理是什么？ItemCF 和 UserCF 有什么区别？
14. ⚡ 双塔模型 / DSSM 的结构是怎样的？负样本如何选择？
15. Swing 算法的原理是什么？时间复杂度是多少？
16. DeepWalk 和 Node2Vec 的区别是什么？随机游走策略有什么不同？
17. Word2Vec 中 Skip-gram 和 CBOW 的区别？Skip-gram 的优势在哪里？
18. Item2Vec 是什么？有哪些应用场景？

### 【工程实践类】

19. ⚡ 线下 AUC 提升但线上效果不好的原因是什么？
20. 负采样的方法有哪些？batch 内随机负采样如何做 bias 修正？
21. 线上线下特征不一致（特征穿越）的原因有哪些？如何解决？
22. 推荐系统如何做冷启动？（用户冷启动 & 物品冷启动）
23. 召回模型的评价指标有哪些？HitRate 如何计算？

### 【多目标学习 & 多任务类】

24. 多目标建模的方法有哪些？（ShareBottom / MMOE / PLE / ESMM）
25. 多任务学习中 task conflict 产生的原因是什么？
26. 为什么引入辅助任务可以提升主任务效果？

### 【大模型 + 推荐系统前沿】

27. 大模型（LLM）如何应用于推荐系统？
28. LLM 推荐和传统推荐模型相比有什么优势与挑战？

### 【机器学习基础类】

29. ⚡ XGBoost 和 GBDT 的区别是什么？XGBoost 做了哪些优化？
30. ⚡ LightGBM 和 XGBoost 的区别？直方图算法原理是什么？
31. 偏差（Bias）和方差（Variance）的区别？Bagging 和 Boosting 的关系？
32. 随机森林的"随机"体现在哪里？
33. L1 正则和 L2 正则的区别？各自适用什么场景？

### 【代码题类】

34. 链表两数相加（LeetCode 原题）
35. 三角形中的最小路径之和（DP）
36. 窗口内最大值（单调队列）
37. 合并两个有序数组
38. IP 地址在过去一小时的访问次数如何统计？（哈希表 + 滑动窗口）

---

## 三、逐题详细解析

### Q1：推荐系统的完整流程？召回→粗排→精排→重排各自的作用？

**参考答案：**

推荐系统的多阶段级联pipeline，核心是**在毫秒级响应时间内，从亿级候选池中选出最合适的Top-K内容**。

| 阶段 | 候选规模 | 模型复杂度 | 核心目标 | 典型模型/策略 |
|------|----------|------------|----------|--------------|
| **召回** | 百万~亿级 | 简单/无模型 | **全**：快速从全库找到候选集，覆盖用户多维兴趣 | ItemCF、UserCF、Embedding召回（Item2Vec）、双塔、DSSM、Graph Embedding |
| **粗排** | 千~万级 | 中等（双塔） | **快**：用轻量模型进一步筛选，承上启下 | 双塔模型、简化的CTR模型 |
| **精排** | 百~千级 | 复杂（DNN） | **准**：用丰富的用户/物品/上下文特征精准排序 | Wide&Deep、DeepFM、DIN、DIEN、MMOE |
| **重排** | 几十~百级 | 策略+模型 | **多样&体验**：Diversity、Exploration、流量分配 | MMR、 DPP、策略规则 |

**为什么分层而不是一步到位？**
- 全库亿级物品无法在毫秒内做精排（特征计算量大）
- 分层漏斗：每层过滤掉大部分候选，逐步逼近最优

---

### Q5：双塔模型在线上是如何检索的？用户塔和物品塔分别怎么更新？

**参考答案：**

**结构：**
- 用户塔（User Tower）：输入用户特征（用户ID、历史行为序列、上下文），输出用户向量 $u$
- 物品塔（Item Tower）：输入物品特征（物品ID、类别、内容向量），输出物品向量 $i$
- 相似度计算：$score(u,i) = \text{cos}(u, i)$ 或内积

**线上检索流程（ANN近似最近邻）：**
1. 离线：将所有物品向量预先建立**ANN索引**（Faiss IVFFlat/HNSW/LSH）
2. 在线：用户请求到达 → 过用户塔得到用户向量 $u$ → 用 $u$ 在 ANN 索引中检索 Top-N 物品
3. 返回的物品列表即为召回结果，送入粗排/精排

**更新策略：**
- 物品塔相对稳定，通常**天级或小时级全量更新**（因为物品特征变化慢）
- 用户塔可通过**实时行为**更新：用户点击/曝光后，将行为序列喂入用户塔，得到新的实时用户向量做召回
- 通常配合 User Embedding Cache（用户向量缓存）使用，降低在线计算压力

---

### Q6：Wide&Deep 模型的原理？

**参考答案：**

Wide&Deep 是 Google 2016年提出的 CTR 预估模型，论文：*"Wide & Deep Learning for Recommender Systems"*。

**模型结构：**
```
Input → Wide侧（线性层）→ Wide输出
      → Deep侧（DNN）→ Deep输出
      → 合并 → Sigmoid → CTR预估值
```

- **Wide侧（宽度）**：输入是原始特征和手工交叉特征，使用 FTRL 优化器进行稀疏在线学习。负责**记忆**（Memorization）—— 学习高频共现模式，如"用户安装了A应用且看过B应用→安装"。
- **Deep侧（深度）**：所有稀疏特征先过 Embedding 层，再堆叠全连接层（DNN）。负责**泛化**（Generalization）—— 自动学习深层特征交叉，发现训练数据中未出现过的组合。
- **联合训练**：Wide侧和Deep侧一起训练，Deep侧的深层特征给Wide侧提供泛化能力，Wide侧的线性模型补充Deep侧可能遗漏的稀疏交互。

**面试加分点：**
- Wide侧用 L1 正则 + FTRL 优化，保证稀疏性，适合大规模特征
- 与 DeepFM 的区别：Wide侧是手工交叉（显式），DeepFM 是自动学习低阶+高阶交叉

---

### Q7：DeepFM 模型的原理？和 Wide&Deep 的区别？

**参考答案：**

**DeepFM**（华为诺亚实验室，2017）= **FM** + **Deep**

**核心创新：**
- FM Component：自动学习**二阶特征交叉**，解决稀疏特征组合问题
- Deep Component：学习**高阶特征交叉**
- **共享Embedding**：FM和Deep共享同一个Embedding层，保证特征表示一致，同时降低参数量

**数学形式：**
$$\hat{y} = \sigma(w_0 + \sum_{i} w_i x_i + \sum_{i=1}^{n} \sum_{j=i+1}^{n} \langle V_i, V_j \rangle x_i x_j + DNN(x))$$

其中 $\langle V_i, V_j \rangle = \sum_{f=1}^{k} V_{i,f} \cdot V_{j,f}$ 是 FM 的二阶交叉项。

**vs Wide&Deep：**
| | Wide&Deep | DeepFM |
|---|---|---|
| Wide侧 | 线性模型（手工交叉） | FM（二阶自动交叉） |
| 特征输入 | 需要人工特征工程 | 自动学习所有阶特征交叉 |
| 表达能力 | 低阶+高阶分离 | 低阶+高阶统一到FM+DNN |
| 工程复杂度 | 需设计Wide侧特征 | 无需手工交叉特征 |

---

### Q8：DIN（深度兴趣网络）的原理？Attention Score怎么算？

**参考答案：**

DIN（阿里妈妈，KDD 2018）—— Deep Interest Network，针对**电商推荐**场景用户兴趣多样、嘈杂的问题。

**背景问题：**
用户历史行为序列中的每个物品，对候选物品的贡献是不同的。比如用户浏览过"手机壳"和"连衣裙"，推荐"手机"时只有"手机壳"相关。DIN 引入注意力机制来解决。

**核心结构：**
- 将用户历史行为序列中的每个 item 向量，与**候选 item 向量**做 Attention：
$$a_j = \frac{\exp(V_j^T \cdot W \cdot V_{target})}{\sum_{k=1}^{T} \exp(V_k^T \cdot W \cdot V_{target})}$$
- 将注意力权重乘以原始行为向量，加权求和得到用户兴趣表示

**面试追问点：**
- 为什么不直接对行为序列做 Average/Pooling？—— 因为等权相加会引入噪声，无法区分不同行为对当前候选的重要程度
- Dice 激活函数：代替 PReLU，解决 Internal Covariate Shift 问题
- Mini-batch Aware Regularization：小批量感知的正则化，减少特征稀疏带来的过拟合

---

### Q11：MMOE 和 PLE 的区别？

**参考答案：**

**MMOE（Multi-gate Mixture-of-Experts）**，Google，2018：
- 引入多个 Expert（专家网络），每个 Expert 是一个 DNN
- 引入 Gate（门控网络），每个 Task 有自己的 Gate，学习该 Task 对各 Expert 的加权组合
- 公式：$y_k = \sum_{i=1}^{n} G_k(x)_i \cdot E_i(x)$
- **优势**：不同 Task 可以利用不同的 Expert 组合，缓解任务冲突

**PLE（Progressive Layered Extraction）**，腾讯，2019：
- 在 MMOE 基础上，增加 **CGC（Customized Gate Control）** 结构
- 每个 Task 有自己的 Specific Expert，同时保留共享的 Common Expert
- 引入 **Progressive Sparing**：底层逐渐分离，先共享后专有，逐层提取更 Task-specific 的表示
- **优势**：同时建模任务的共性和个性，比 MMOE 更细腻地解耦任务

**对比：**
| | MMOE | PLE |
|---|---|---|
| Expert结构 | 多Expert共享 | Task-Specific + Shared Expert |
| Gate | 每个Task一个Gate | CGC双层Gate |
| 解耦能力 | 共享 Expert 仍有冲突 | 先共享后专有，更彻底 |
| 效果 | 优于 ShareBottom | 优于 MMOE |

---

### Q12：ESMM 的原理？为什么能解决样本选择偏差？

**参考答案：**

**ESMM（Entire Space Multi-task Model）**，阿里，SIGIR 2018，解决 CVR 预估中的样本选择偏差（SSB）问题。

**问题背景：**
- CVR（转化率）预估通常在点击后进行，但：
  - 样本量少（转化行为稀疏）
  - 存在**样本选择偏差（SSB）**：训练数据仅来自被点击的样本，但推理时需要预测全量曝光样本
  - **数据稀疏性（Data Sparsity）**：点击→转化路径样本少

**ESMM 结构：**
- 同时建模 CTR 和 CVR，通过两者的乘积得到 **CTCVR = CTR × CVR**
- 损失函数：$\mathcal{L} = \mathcal{L}_{CTR} + \mathcal{L}_{CVR}$（两部分共享 Embedding）
- CVR 模型从未被直接训练，而是在全量曝光空间上通过 CTCVR 隐式学习

**关键洞察：**
$$p(z=1|y=1,x) = \frac{p(y=1,z=1|x)}{p(y=1|x)} = \frac{CTCVR(x)}{CTR(x)}$$
由于 CTR 和 CTCVR 都在全量曝光空间训练，CVR 自然拥有了全量样本的分布特性，完美解决了 SSB 问题。

---

### Q19：线下 AUC 提升但线上效果不好的原因？

**参考答案（高频必背）：**

这是大厂面试高频题，考察候选人对**离线在线一致性**的理解。

**三大核心原因：**

1. **样本问题**
   - 特征穿越：用了 label leakage 的特征（如用了点击后的后验特征），线上 Serving 时这些特征不可用
   - 样本穿越：用线上模型预测分作为特征重新训练（future leakage）
   - 冷启动样本与常规样本分布差异

2. **评估指标问题**
   - 线下 AUC 是全局的，线上是 per-user 的：应该用 **GAUC**（Group AUC）来评估
   - 业务指标（GMV、时长、留存）与离线指标（CTR AUC）不匹配
   - AB 实验时间不够，短期的 AUC 提升未必带来长期收益

3. **环境差异**
   - 线上有实时特征（时间、上下文），离线训练无法获取
   - 线上推荐系统有上下文调节（流量分配、生态调控），离线模型无法感知
   - 模型更新频率差异：离线模型 T+1 更新，线上实时更新导致分布漂移

---

### Q21：线上线下特征不一致（特征穿越）的原因？如何解决？

**参考答案：**

**主要原因：**
1. **未来信息泄露**：使用了点击之后才能获取的特征（如停留时长、是否看完等）
2. **上下文特征缺失**：线上实时 contextual 特征（设备类型、网络状态、实时热门事件）
3. **离线处理时间差**：用户行为日志时间戳模糊，数据回放顺序不确定
4. **缓存不一致**：用户特征缓存过期导致特征陈旧

**解决方案：**
- 严格梳理特征的时间窗口，保证每个特征在在线和离线使用的一致性
- 对实时特征做**延迟上报补偿**或做**特征回填**
- 建立**特征血缘系统**，追踪每个特征的生成时间点
- 引入**穿越检测**工具，在离线训练时自动过滤未来特征

---

### Q22：推荐系统如何做冷启动？

**参考答案：**

**用户冷启动：**
- **热门推荐**：新用户推荐高热内容（如"猜你喜欢"热榜）
- **属性推断**：基于注册信息（年龄、性别、地域）匹配相似用户群的偏好
- **探索策略**：EE（Exploitation-Exploration）—— 引入 Bandit / Thompson Sampling 探索用户兴趣
- **跨域迁移**：利用用户在其他平台（抖音→今日头条）的行为数据
- **大模型**：利用 LLM 通过用户画像描述，生成个性化推荐

**物品冷启动：**
- **内容特征匹配**：利用物品的文字描述、图片、视频等多模态特征找到相似物品的协同信号
- **专家规则**：新物品加入流量扶持池，保证一定曝光量（冷启扶持策略）
- **Graph Embedding**：新物品插入图结构后，通过 Graph Neural Network 快速得到embedding
- **LLM 生成描述**：用大模型生成物品的语义向量，解决新物品 ID 特征缺失问题

---

### Q29：XGBoost 和 GBDT 的区别？XGBoost 做了哪些优化？

**参考答案（高频八股）：**

**GBDT（Gradient Boosting Decision Tree）：**
- 每棵树学习前棵树预测结果的**残差**（或梯度）
- 多棵树预测结果**求和**作为最终输出
- 基模型通常是 CART 回归树

**XGBoost 对 GBDT 的核心优化：**

| 优化点 | GBDT | XGBoost |
|--------|------|---------|
| **正则化** | 无显式正则 | 目标函数中加入 $\Omega(f) = \gamma T + \frac{1}{2}\lambda \sum w_j^2$ |
| **损失函数** | 一阶导（梯度） | 一阶+二阶泰勒展开，更精确 |
| **分裂依据** | 贪婪精确搜索 | 近似算法（直方体分桶），支持并行 |
| **基分类器** | 仅 CART | 支持 CART / 线性分类器 / DART |
| **缺失值** | 需手动处理 | 自动学习缺失值的最优分裂方向 |
| **Shrinkage** | 无 | 乘以 $\eta$（学习率）衰减，降低过拟合 |
| **采样** | 无 | 支持列抽样（Column Subsampling） |
| **并行** | 特征级别并行（弱） | 先建树结构再并行分裂，强并行能力 |

**二阶泰勒展开优势：**
$$Obj^{(t)} \approx \sum_{i=1}^{n}\left[g_i w_{q(x_i)} + \frac{1}{2}h_i w_{q(x_i)}^2\right] + \Omega(f_t)$$
其中 $g_i$、$h_i$ 是一阶、二阶梯度，比一阶导提供更精确的梯度方向。

---

### Q34：代码题 — 链表两数相加（LeetCode 2）

**解题思路：**

逐位相加，注意进位处理。时间 $O(\max(m,n))$，空间 $O(1)$。

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def addTwoNumbers(l1: ListNode, l2: ListNode) -> ListNode:
    dummy = ListNode(0)
    cur = dummy
    carry = 0
    
    while l1 or l2 or carry:
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0
        
        total = val1 + val2 + carry
        carry = total // 10
        cur.next = ListNode(total % 10)
        
        cur = cur.next
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    
    return dummy.next
```

**关键点：**
- while 条件要包含 `carry`，因为最后一位可能产生进位
- 处理不等长链表：用 `if l1 / l2 else 0`

---

### Q38：代码题 — IP 访问频率统计（滑动窗口 + 哈希表）

**解题思路：**
统计 IP 在过去 1 小时内访问次数是否超过 10000。使用**滑动窗口 + 哈希表**，$O(1)$ 时间复杂度。

```python
from collections import defaultdict, deque
from time import time

class访问频率器:
    def __init__(self, limit=10000, window_sec=3600):
        self.limit = limit
        self.window = window_sec
        # ip -> deque of timestamps
        self.history = defaultdict(deque)
    
    def record(self, ip: str):
        now = int(time())
        # 移除1小时外的旧记录
        q = self.history[ip]
        while q and q[0] <= now - self.window:
            q.popleft()
        q.append(now)
    
    def is_exceed(self, ip: str) -> bool:
        return len(self.history[ip]) >= self.limit
```

**复杂度分析：**
- 时间：$O(1)$ 均摊（每条记录最多入队出队各一次）
- 空间：$O(n)$，n 为不同 IP 数量

---

## 四、高频考点 TOP 10（本周重点关注）

| 排名 | 考点 | 出现频率 | 备考优先级 |
|------|------|----------|-----------|
| ⭐1 | 离线AUC↑但线上↓的原因（样本穿越/特征不一致） | 🔥🔥🔥🔥🔥 | ⭐⭐⭐⭐⭐ |
| ⭐2 | Wide&Deep / DeepFM 原理对比 | 🔥🔥🔥🔥🔥 | ⭐⭐⭐⭐⭐ |
| ⭐3 | 双塔模型结构 & 在线ANN检索流程 | 🔥🔥🔥🔥 | ⭐⭐⭐⭐ |
| ⭐4 | 多阶段链路（召回→粗排→精排→重排）设计 | 🔥🔥🔥🔥 | ⭐⭐⭐⭐ |
| ⭐5 | DIN/DIEN 注意力机制原理 | 🔥🔥🔥🔥 | ⭐⭐⭐⭐ |
| ⭐6 | XGBoost vs GBDT vs LightGBM | 🔥🔥🔥🔥 | ⭐⭐⭐⭐ |
| ⭐7 | ESMM 原理（解决样本选择偏差） | 🔥🔥🔥 | ⭐⭐⭐ |
| ⭐8 | MMOE / PLE 多任务学习 | 🔥🔥🔥 | ⭐⭐⭐ |
| ⭐9 | 冷启动问题的多种解法 | 🔥🔥🔥 | ⭐⭐⭐ |
| ⭐10 | LLM + 推荐系统前沿应用 | 🔥🔥🔥 | ⭐⭐⭐ |

---

## 五、备考建议

1. **算法原理**：DeepFM/DIN/Wide&Deep 原理必须能**画图+公式推导**两手抓，面试常追问细节
2. **全链路设计**：能说清楚每层的作用和选型原因，这是架构面的高频题
3. **工程题**：重点刷 LeetCode 中等难度的链表、DP、哈希表题目
4. **前沿**：大模型推荐（LLM4Rec）正在成为新的考察方向，需要了解至少一个代表性工作（如 GPT4Rec 或 RecBole）
5. **项目深挖**：面试中"项目"环节占比最大，需要对简历中的每段经历准备**数据收益、模型选型、踩坑点**三件套

---

*报告生成时间：2026-04-02 11:05 AM（自动搜集 + 人工解析）*
*下期预告：大模型推荐系统前沿 + Graph Embedding 系列面试题*
