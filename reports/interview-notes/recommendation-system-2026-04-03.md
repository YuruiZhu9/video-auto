# 推荐系统算法面经每日搜集报告
**日期：2026-04-03（周五）｜搜集时间：10:33 AM｜来源：牛客网·力扣·知乎·GankInterview**

---

## 一、当日面经来源

| 来源平台 | 面经标题 | 公司/岗位 | 面试轮次 |
|---------|---------|---------|---------|
| **力扣（LeetCode）** | 面经｜字节跳动｜推荐算法｜春招正式批 | 字节跳动·推荐算法 | 一面→二面→三面Leader→四面Leader（共4轮） |
| **牛客网** | 字节跳动推荐算法面经（TikTok国际化电商直播推荐） | 字节·TikTok电商 | 一面（共10道题，附Shopee/腾讯附赠） |
| **知乎** | 推荐系统面试题整理 | 综合 | 高频考点清单 |
| **GankInterview** | 推荐系统AI面试：召回/排序/特征/冷启动/评测全链路追问清单 | 综合 | 全链路深度追问 |

---

## 二、面试问题清单

### 📌 字节跳动·推荐算法·春招正式批（共4轮核心题目）

**【一面】**
1. 算法题：反转链表 II（LeetCode 92）
2. 算法题：二叉树的最近公共祖先（LeetCode 236）+ 复杂度分析
3. 项目深挖（目标检测项目）
4. 目标检测算法分类
5. **设计题：设计一个短视频推荐系统**（衍生推荐基础问题+八股文）

**【二面】**
1. 算法题：排序数组中查找元素的第一个和最后一个位置（LeetCode 34，只找第一个位置）
2. 论文深挖
3. 减少过拟合的方法
4. **设计题：使用B站过程中对视频推荐的改进方案**（比一面更深入）

**【三面Leader】**
1. 算法题：有向图最大概率路径（Dijkstra转换最短路径）
2. 项目+论文深挖
3. LightGBM 简述
4. 逻辑回归 简述
5. **设计题：设计一个短视频推荐系统**（Follow up 更多更细）

**【四面Leader】**
1. 算法题：最小区间 K 个链表（LeetCode 632）+ Follow up（每个链表至少两个节点在区间内）
2. **设计题：识别"骗赞"短视频** + 标注员标注情况下的改进 + 特征缺失处理

---

### 📌 字节跳动·TikTok电商直播推荐·一面（共10道）

1. 介绍项目背景
2. **推荐链路是怎么运作的，有哪些模块？**
3. 如何做排序模型的迭代？
4. 用过的大数据框架？
5. **优化器的原理？**
6. **PPO的原理和损失函数？**
7. 写 Prompt 的经验？
8. SFT 的经验？
9. 代码题：TOP K 大的数（堆/快速选择）
10. 反问：团队做的方向

---

### 📌 附赠：Shopee搜推算法一面 + 腾讯搜推实习二面

**Shopee 搜推一面：**
- 项目深挖
- 八股：了解过什么推荐系统里的精排模型？
- **DIN 原理解释？**
- 手撕：反转链表
- **MHA（Multi-Head Attention）？**

**腾讯搜推实习二面：**
- 项目深挖
- PyTorch 会用吗？
- 大模型了解多少，实际业务怎么用的？
- DeepSeek 新版本做了什么处理？
- 手撕：树结构最短路径（非二叉树）
- **场景题：实际业务只有数据，怎么做特征和模型，如何把大模型用进来？**

---

## 三、逐题详细解析

---

### 🔴 算法题高频考点

---

#### Q1：反转链表 II（LeetCode 92）

**题目**：反转从位置 left 到 right 的链表节点（1-indexed）。

**核心思路**：三步走——定位 left 前驱 → 穿针引线反转区间 → 拼接。

```python
class Solution:
    def reverseBetween(self, head: ListNode, left: int, right: int) -> ListNode:
        dummy = ListNode(0)
        dummy.next = head
        pre = dummy  # left节点的前驱

        # 1. 走到left前一个节点
        for _ in range(left - 1):
            pre = pre.next

        # 2. 穿针引线反转区间
        cur = pre.next
        for _ in range(right - left):
            next_node = cur.next
            cur.next = next_node.next
            next_node.next = pre.next
            pre.next = next_node

        return dummy.next
```

**复杂度**：时间 O(n)，空间 O(1)。

**面试加分点**：能用 dummy 节点统一处理 left=1 的边界情况，说明边界意识强。

---

#### Q2：二叉树的最近公共祖先（LeetCode 236）

**核心思路**：DFS 后序遍历 + 递归返回值策略。

```python
def lowestCommonAncestor(root, p, q):
    if not root or root == p or root == q:
        return root
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)
    if left and right:
        return root  # 两侧都有返回值，说明是LCA
    return left or right
```

**三种追问方向**：
1. **时间复杂度**：O(n)，最坏遍历整棵树
2. **空间复杂度**：O(n)，递归栈深度（最坏为链表状树）
3. **最优解**：如果节点有 parent 指针，可从两节点出发，用集合记录路径，时间 O(n)，空间 O(h)

---

#### Q3：有向图最大概率路径（Dijkstra 变体）

**思路**：将"概率相乘取最大"转换为"对数取负 → 求和最小 → Dijkstra"。

```python
import heapq
def maxProbability(n, edges, succProb, start, end):
    graph = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        graph[u].append((v, succProb[i]))
        graph[v].append((u, succProb[i]))

    prob = [0.0] * n
    prob[start] = 1.0
    pq = [(-1.0, start)]  # (负概率, 节点)，heapq默认最小堆

    while pq:
        neg_p, node = heapq.heappop(pq)
        if node == end:
            return -neg_p
        if -neg_p < prob[node]:  # 已找到更优路径
            continue
        for nxt, edge_prob in graph[node]:
            new_prob = -neg_p * edge_prob
            if new_prob > prob[nxt]:
                prob[nxt] = new_prob
                heapq.heappush(pq, (-new_prob, nxt))
    return 0.0
```

**面试要点**：说出"取对数转加法"的数学洞察，面试官会眼前一亮。

---

#### Q4：最小区间 K 个链表（LeetCode 632）

**核心思路**：K 路归并，用最小堆维护每个链表的当前元素。

```python
def smallestRange(lists):
    import heapq
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    max_val = max(h[0] for h in heap)

    result = float('-inf'), float('inf')
    while True:
        min_val, i, node = heap[0]
        cur_range = max_val - min_val
        if cur_range < result[1] - result[0]:
            result = (min_val, max_val)
        if not node.next:
            break
        next_node = node.next
        heapq.heapreplace(heap, (next_node.val, i, next_node))
        max_val = max(max_val, next_node.val)
    return list(result)
```

**Follow up**：每个链表至少两个节点在区间内 → 一开始把每个链表前两个节点都放入堆即可。

---

#### Q5：树结构最短路径（非二叉树）+ TOP K 大的数

- **非二叉树最短路径**：图 BFS 或 Dijkstra（无权重则 BFS，有权重则 Dijkstra）
- **TOP K 大的数**：快速选择算法 O(n) 平均复杂度，或建大小为 K 的小顶堆 O(n log K)

---

### 🔴 业务设计题（每面必考，最能反映综合能力）

---

#### Q6：设计一个短视频推荐系统

**四阶段答题框架**：

```
召回 → 粗排 → 精排 → 重排
```

**① 召回层（候选集 ~1000）**
- 多路召回：热门召回 + 协同过滤（I2I、U2U）+ 语义召回（双塔向量检索 DSSM）+ 地域/热点召回
- 核心指标：召回率（Recall@500）、覆盖率

**② 粗排层（~500→~200）**
- 轻量级模型（LR/GBDT/双塔内积）快速打分
- 限制：在线耗时 < 10ms

**③ 精排层（~200→Top N）**
- 多目标：CTR + 完播率 + 点赞率 + 关注率（MMOE/ESMM）
- 用户行为序列建模：DIN（Target Attention）
- 核心指标：AUC、NDCG

**④ 重排层（~N→最终展示列表）**
- 多样性：MMR（Maximal Marginal Relevance）或 DPP
- 业务规则：置顶、打压、必出
- 核心指标：Session CTR、用户留存

**Follow up 追问应对**：
- 「各路召回取多少？」→ 不固定！用归一化+基于历史转化率加权（或 LR 融合）
- 「为什么双塔不在底层做特征交叉？」→ 物品向量必须预计算+离线建索引，否则在线计算量爆炸
- 「超长行为序列怎么处理？」→ SIM（检索式），Hard Search（倒排索引）或 Soft Search（向量 ANN）

---

#### Q7：识别"骗赞"短视频 + 标注员场景

**基础方案**（有用户行为数据时）：
- 特征工程：点击率 × 完播率异常、互动率 vs 停留时长 ratio、作者历史"骗赞"率
- 模型：GBDT 二分类 / 多任务（点击→完播→点赞联合建模）

**标注员标注情况下的改进**：
- **主动学习（Active Learning）**：优先让标注员标注模型最不确定的样本
- **半监督学习**：利用未标注数据的一致性伪标签
- **噪声标签学习**：使用 Label Smoothing 或 MentorNet/Co-teaching 抗噪

**特征缺失处理**：
- 特征重要性分析 + 缺失填充（均值/众数/模型预测填充）
- **降级策略**：若无某维特征，自动切换到简化模型
- 定期复盘：统计缺失特征的覆盖率，指导数据建设

---

### 🔴 推荐系统核心八股（高频追问清单）

---

#### Q8：推荐链路是怎么运作的，有哪些模块？

```
用户请求 → 召回（万级→千级）→ 粗排（千级→百级）→ 精排（百级→十级）→ 重排（多样化/业务规则）→ 展示
              ↓
        用户行为日志 → 特征工程 → 模型训练 → 特征服务/模型服务
```

**各模块职责与核心矛盾**：
- 召回：计算效率 vs 召回质量（核心是多路召回融合）
- 粗排：速度（<10ms）vs 精度（轻量模型）
- 精排：精度优先（复杂模型），但须控制 QPS 成本
- 重排：用户体验（多样性）vs 短期 CTR

---

#### Q9：DIN vs 简单 Pooling 的区别？

| 对比维度 | Sum/Avg Pooling | DIN（Target Attention） |
|---------|----------------|----------------------|
| 兴趣建模 | 所有历史等权求和 | 当前候选商品激活历史行为权重 |
| 表达能力 | 欠佳，无法区分候选 | 强，能感知当前候选 |
| 计算量 | O(1)，与候选数无关 | O(B×T×D)，T=历史长度 |
| 适用场景 | 召回层、粗排层 | 精排层 |

**DIN 公式**：
$$
\text{Attention}(q, \{k_i\}) = \text{Softmax}\left(\frac{q \cdot k_i}{\sqrt{d}}\right) \cdot v_i
$$
其中 $q$ = Target Item Embedding，$\{k_i\}$ = 历史行为序列 Embedding。

**追问：超长序列（10k+）怎么办？**
- 阶段一：截断（保留最近 N 个）
- 阶段二：记忆网络（GRU/LSTM）压缩 → DIEN
- 阶段三：检索式建模（SIM）：先 ANN 检索 Top-K 相关子序列，再 DIN

---

#### Q10：MMOE vs ESMM 的核心区别？

| 维度 | ESMM | MMOE |
|-----|------|------|
| 解决的问题 | SSB（样本选择偏差）+ DS（数据稀疏） | 多任务梯度冲突 |
| 核心思想 | 利用 CTR×CTCVR 概率链式法则，在全量曝光空间训练 CVR | 多个 Expert + 门控网络，让各任务自适应选择 Expert |
| 共享机制 | 共享 Embedding 层 | 共享 Expert 隐藏层 |
| 适用场景 | CVR 建模 | 多个同等重要性任务（CTR+CVR+点赞+收藏） |

**ESMM 公式**：
$$
pCTCVR = pCTR \times pCVR, \quad pY=1, Z=1|x = pZ=1|x \times pY=1|x,Z=1
$$
训练在全量曝光空间，解决 SSB；共享 Embedding 解决 DS。

**MMOE Loss 设计**：各任务 Loss 加权（Uncertainty Weighting / GradNorm）解决梯度冲突。

---

#### Q11：优化器的原理（Adam vs SGD）

| 优化器 | 核心机制 | 适用场景 |
|-------|---------|---------|
| **SGD** | 固定学习率，全量/小批量梯度下降 | 凸函数收敛好，大模型训练不稳定 |
| **SGD + Momentum** | 加入动量项，累积历史梯度方向 | 加速收敛，跨过局部最优 |
| **Adam** | 自适应学习率：Momentum（一阶）+ RMSProp（二阶） | 默认首选，收敛快，但泛化性有时不如 SGD |
| **AdamW** | Adam + L2 正则解耦 | 推荐系统大规模训练首选 |

**Adam 更新公式**：
$$
m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t \quad \text{（一阶动量）}
$$
$$
v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2 \quad \text{（二阶动量）}
$$
$$
\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \quad \theta_t = \theta_{t-1} - \alpha \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}
$$

**面试追问**：「Adam 训练loss下降快但泛化差怎么办？」→ 换 SGD+Momentum 或 AdamW + Label Smoothing。

---

#### Q12：PPO 的原理与损失函数

**PPO（Proximal Policy Optimization）** 是强化学习中在线策略优化的经典算法，推荐系统中用于探索-利用策略优化（如 DRN 新闻推荐）。

**核心目标函数**：
$$
L^{CLIP}(\theta) = \mathbb{E}_t \left[ \min\left( r_t(\theta) \cdot A_t, \; \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \cdot A_t \right) \right]
$$
其中 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$ 是概率比，$\epsilon$ 是裁剪超参（通常 0.2）。

**两个核心机制**：
1. **Clip 裁剪**：限制策略更新幅度，避免灾难性更新
2. **KL 散度惩罚**（PPO-Penalty）：惩罚策略偏离过远

**面试加分**：提到 PPO 在推荐中的应用——DRN（Deep Reinforcement Learning for Recommender），将推荐视为马尔可夫决策过程。

---

#### Q13：Wide&Deep vs DeepFM 的本质区别

| 维度 | Wide&Deep | DeepFM |
|------|-----------|--------|
| Wide 部分 | 人工构造的交叉特征（记忆） | FM 自动二阶交叉 |
| 低阶交互 | 依赖人工（需特征工程） | 端到端自动学习 |
| 模型结构 | LR + DNN 并行 | FM + DNN 共享 Embedding |
| 缺点 | Wide 部分需要专家经验 | 计算量略大（多了 FM 项） |

**致命追问**：「Deep 网络拟合能力那么强，为什么还需要 Wide/ FM？」

**答**：
1. **过度泛化风险**：DNN 把稀疏特征映射到稠密空间，对罕见特征组合会给出非零预测，而某些稀疏组合代表强负反馈（如"已购买"×"同类商品"），需要"查表"能力
2. **学习效率**：DNN 学习显式乘法关系需要极深网络+海量数据；FM 通过隐向量内积直接建模二阶交叉

---

#### Q14：推荐系统有哪些 Bias？如何 Debias？

| Bias 类型 | 含义 | 应对方法 |
|---------|------|---------|
| **选择偏差（Selection Bias）** | 用户选择性地与物品交互（非随机） | 反倾向加权（IPS）、ELBO |
| **曝光偏差（Exposure Bias）** | 未曝光=负样本？不一定 | 曝光模型、注意力机制 |
| **位置偏差（Position Bias）** | 位置靠前→点击率高，非内容质量 | Position Debiasing、Label Refinement |
| **流行度偏差（Popularity Bias）** | 热门物品过度曝光，长尾被忽视 | 正则化、加权多样性的Loss |
| **归纳偏差（Inductive Bias）** | 模型假设（如独立同分布） | 因果推断建模 |

**参考论文**：*Bias and Debias in Recommender System: A Survey and Future Directions*

---

#### Q15：召回负样本如何构造？

**核心原则：负样本为王**

| 负样本类型 | 做法 | 作用 |
|---------|------|------|
| **随机负采样（Easy Neg）** | 全量物品中随机抽取 | 让模型认识"完全不相关" |
| **曝光未点击（Semi-Hard）** | 曝光但未点击的物品 | 保留部分信息，用于区分 |
| **Hard Neg（困难负样本）** | 召回分高但实际不相关 | 增强模型判别力 |

**SSB 问题**：只用"曝光未点击"训练，模型只学到"区分曝光池内的细粒度差异"，而不会区分"海量噪声 vs 相关物品"。

**工业实践**：正样本 = 点击，负样本 = 全局随机采样（约 1:10~1:100），困难负样本辅助训练。

---

#### Q16：冷启动问题的系统化解法

```
用户冷启动：
① 全局热度兜底（高普适性内容）
② 属性映射：注册信息→细分人群Embedding
③ 对比学习自监督预训练
④ UCB/Thompson Sampling 探索

物品冷启动：
① EGES（Enhanced Graph Embedding with Side information）
② 新物品曝光配额（快速收集反馈）
③ 内容理解：NLP/CV提取物品向量，在向量空间找相似高热品
④ 探索与利用：UCB 为新物品建模 Beta 分布
```

**评估维度**：长期留存（Retention）而非短期 CTR（避免冷启动永远跑不赢热门）。

---

#### Q17：离线 AUC 提升但线上 A/B 下跌？归因分析

**常见原因**：

| 原因 | 解释 | 排查方法 |
|-----|------|---------|
| **特征穿越（Data Leakage）** | 使用了当次转化数据/未来行为 | 特征重要性分析 |
| **线上线下不一致（Training-Serving Skew）** | 实时流数据 vs 清洗后数据仓库 | 特征日志逐条比对 |
| **样本选择偏差** | 曝光→点击样本训练，对全量预测 | 检查训练集分布 |
| **评估指标与业务目标不匹配** | AUC 衡量排序能力，但热门品会"污染"AUC | 看 NDCG、Calibration |

**排查清单**：
1. 特征一致性校验（在线特征 vs 离线特征）
2. Calibration 检查（COPC：predicted CTR vs actual CTR）
3. 穿越特征排查（特征重要性异常高的要警惕）
4. 测试集分布对齐

---

### 🔴 大模型 + 推荐系统（2026 面试新热点）

#### Q18：大模型（LLM）在推荐系统中的落地点

| 落地点 | 具体应用 | 可行性 |
|-------|---------|-------|
| **物品内容理解** | 提取物品文本的 Dense Embedding/Tags | ✅ 已落地 |
| **推荐理由生成** | LLM 生成"因为你喜欢X而推荐Y" | ✅ 部分落地 |
| **数据增强/SFT** | 用 LLM 构造训练样本 | ✅ 已落地 |
| **直接做精排** | 所有候选品逐一 LLM 推理 | ❌ 延迟/成本不可接受 |
| **召回层** | LLM 理解用户意图→向量检索 | ⚠️ 探索中 |

**致命追问：「为什么不能直接用 LLM 做精排？」**
- 精排 QPS 通常 1000+，每次需处理数百个候选品
- LLM 推理延迟 100ms~数秒级别，成本是 ID 类模型的 1000 倍
- 解决方案：离线/异步处理 OR 知识蒸馏（LLM 作为 Teacher，训练轻量 Student 模型）

---

## 四、今日面试高频考点排行（2026-04-03）

| 排名 | 考点 | 出现频次 | 备考优先级 |
|-----|------|---------|-----------|
| 🔥 1 | 设计题（短视频/电商推荐系统） | 每面必考 | ⭐⭐⭐⭐⭐ |
| 🔥 2 | 算法题（链表/二叉树/图/堆/TopK） | 每面2道+ | ⭐⭐⭐⭐⭐ |
| 🔥 3 | DIN/用户行为序列建模 | 高频追问 | ⭐⭐⭐⭐⭐ |
| 🔥 4 | MMOE/ESMM 多目标优化 | 高频追问 | ⭐⭐⭐⭐ |
| 🔥 5 | 双塔模型/DSSM + 负采样策略 | 高频追问 | ⭐⭐⭐⭐ |
| 🔥 6 | Wide&Deep / DeepFM | 反复考察 | ⭐⭐⭐⭐ |
| 7 | 冷启动问题 | 常考 | ⭐⭐⭐ |
| 8 | PPO/LLM + 推荐 | 新兴考点 | ⭐⭐⭐ |
| 9 | 优化器原理（Adam/AdamW） | 出现多次 | ⭐⭐⭐ |
| 10 | 线上线下不一致归因 | 常考 | ⭐⭐⭐ |

---

## 五、备考建议

1. **算法题是门槛**：字节/腾讯/Shopee 均 2 道/轮，必须达到 hot 150 题熟练；重点：链表、二叉树、滑动窗口、双指针、堆、动态规划
2. **设计题是分水岭**：每面必考，核心是多阶段链路（召回→粗排→精排→重排）+ 各阶段权衡取舍
3. **八股要有深度**：不能只背定义，要能回答「为什么」「如果xxx怎么办」「工程上怎么处理」
4. **大模型是加分项**：2026 年面试几乎必问 LLM + 推荐，能说出一到两个落地场景会大幅加分
5. **项目深挖是标配**：面试官会沿着项目往深追问，准备 2-3 个核心项目，每个项目的技术选型、难点、优化点都要烂熟于心

---

*本报告由 AI 定时任务自动搜集整理｜数据来源：牛客网、力扣（LeetCode）、知乎、GankInterview*
*下次更新时间：2026-04-04 10:30 AM*
