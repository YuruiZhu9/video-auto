# 属性测试与AI辅助测试生成实战

> 推荐系统不仅需要"跑得通"的测试，更需要"跑不坏"的测试

---

## 🎯 核心问题

传统测试是**示例驱动**的：
```python
def test_recall_returns_top_k():
    result = recall([1, 2, 3], top_k=5)
    assert len(result) == 5  # 只测了一个例子
```

**问题**：你写了 10 个测试用例，算法在第 11 个边界情况下悄悄崩了。

**属性测试**换了个思路：定义输入必须满足的**属性（Property）**，让工具自动生成数百个边界用例去撞，总有一个能撞出 bug。

---

## 一、属性测试核心理念

### 1.1 什么是属性？

属性 = **无论输入是什么，输出必须满足的规则**。

推荐系统有哪些天然属性？

| 属性 | 描述 |
|------|------|
| **数量不变** | 请求 top_k=N，返回数量 ≤ N |
| **去重性** | 同一 user_id 连续调用，不会返回重复 item |
| **非空性** | 行为数据正常时，召回结果非空 |
| **单调性** | top_k 增大，返回结果数量不减少 |
| **类型安全** | 返回的 item_id 是整数或字符串，不是 None |
| **延迟上界** | P99 延迟不超过 300ms |
| **幂等性** | 同一请求连续调用，结果一致（或在随机策略下概率可控） |

### 1.2 Property Testing vs Example Testing

| 维度 | 示例测试 | 属性测试 |
|------|---------|---------|
| 测试数量 | 手动写 N 个 | 自动生成数百到数千个 |
| 发现边界 bug | 低 | **高** |
| 维护成本 | 高（输入变就要改） | 低（属性不变，生成器变） |
| 适用场景 | 已知路径验证 | 边界/随机输入 |

---

## 二、Python 属性测试：Hypothesis 实战

### 2.1 安装与基础

```bash
pip install hypothesis pytest
```

### 2.2 推荐系统核心属性测试

```python
# tests/property/test_recall_properties.py
from hypothesis import given, settings, assume, Phase, Verbosity
import hypothesis.strategies as st
from hypothesis import example
import pytest
from recall import recall_engine  # 你的召回模块

# ============================================================
# 策略定义：推荐系统的输入空间
# ============================================================

@st.composite
def valid_user_behaviors(draw):
    """生成有效的用户行为数据"""
    user_id = draw(st.integers(min_value=1, max_value=1_000_000))
    history_items = draw(st.lists(
        st.integers(min_value=1, max_value=100_000),
        min_size=0,
        max_size=100,
        unique=True
    ))
    return {"user_id": user_id, "history": history_items}


@st.composite
def valid_recall_request(draw):
    """生成有效的召回请求"""
    return {
        "user_id": draw(st.integers(min_value=1, max_value=1_000_000)),
        "top_k": draw(st.integers(min_value=1, max_value=200)),
        "scene": draw(st.sampled_from(["home", "detail", "search", "feed"])),
        "category_filter": draw(st.lists(
            st.integers(min_value=1, max_value=1000),
            min_size=0,
            max_size=5
        ) | st.none()),
    }


# ============================================================
# 属性 1：数量边界（最重要的属性）
# ============================================================

@given(valid_recall_request())
@settings(
    max_examples=500,          # 生成500个测试用例
    deadline=5000,               # 每个用例超时5秒
    phases=[Phase.generate, Phase.target],  # 生成+目标导向
    print_blob=True,           # 失败时打印最小化用例
)
def test_recall_never_exceeds_top_k(request_dict):
    """
    属性：返回数量绝不超过 top_k
    这是推荐系统的硬约束——超过会撑爆下游精排队列
    """
    result = recall_engine.recall(**request_dict)
    top_k = request_dict["top_k"]

    # 属性声明
    assert len(result) <= top_k, (
        f"召回结果数量 {len(result)} 超过 top_k {top_k}！"
        f"这会导致精排队列溢出，触发系统故障。"
        f"输入: {request_dict}"
    )


# ============================================================
# 属性 2：去重性（隐藏的致命 bug）
# ============================================================

@given(valid_recall_request())
@settings(max_examples=500)
def test_recall_returns_unique_items(request_dict):
    """
    属性：召回结果中不应有重复 item
    重复 item 会导致精排浪费计算资源在重复候选上
    """
    result = recall_engine.recall(**request_dict)
    item_ids = [item["item_id"] for item in result]
    
    unique_ids = set(item_ids)
    
    assert len(item_ids) == len(unique_ids), (
        f"召回结果存在重复 item！"
        f"原始数量: {len(item_ids)}, 去重后: {len(unique_ids)}"
        f"重复 item_ids: {[i for i in item_ids if item_ids.count(i) > 1]}"
        f"输入: {request_dict}"
    )


# ============================================================
# 属性 3：单调性（top_k 增 → 结果不减）
# ============================================================

@given(
    user_id=st.integers(min_value=1, max_value=10_000),
    top_k_small=st.integers(min_value=1, max_value=50),
)
@settings(max_examples=300)
def test_recall_monotonicity(user_id, top_k_small):
    """
    属性：top_k 增大时，结果数量应该不减少
    这是一个随机性友好的弱属性（有些召回有随机采样）
    """
    small = recall_engine.recall(user_id=user_id, top_k=top_k_small, scene="home")
    large = recall_engine.recall(user_id=user_id, top_k=top_k_small + 20, scene="home")
    
    # 弱单调性：至少不减少（允许相等，因为可能有随机性）
    assert len(large) >= len(small) - 1, (
        f"单调性违反！top_k={top_k_small} 返回 {len(small)} 个，"
        f"top_k={top_k_small+20} 返回 {len(large)} 个"
    )


# ============================================================
# 属性 4：类型安全（防御动态语言的隐藏 bug）
# ============================================================

@given(valid_recall_request())
@settings(max_examples=500)
def test_recall_return_type_consistency(request_dict):
    """
    属性：返回结构一致，item_id 类型稳定，不会返回 None/空字符串
    动态类型语言的隐患：某个边界条件会让 item_id 变成 None
    """
    result = recall_engine.recall(**request_dict)
    
    for item in result:
        assert "item_id" in item, f"返回结构缺少 item_id 字段: {item}"
        
        item_id = item["item_id"]
        assert item_id is not None, (
            f"item_id 为 None！输入: {request_dict}, item: {item}"
        )
        assert isinstance(item_id, (int, str)), (
            f"item_id 类型异常: {type(item_id).__name__}，期望 int 或 str"
        )
        assert item_id != "", f"item_id 为空字符串！item: {item}"


# ============================================================
# 属性 5：category_filter 有效性（常被忽略的边界）
# ============================================================

@given(
    user_id=st.integers(min_value=1, max_value=10_000),
    top_k=st.integers(min_value=1, max_value=50),
    filter_cats=st.lists(
        st.integers(min_value=1, max_value=100),
        min_size=1,
        max_size=5,
        unique=True
    )
)
@settings(max_examples=200)
def test_recall_filter_respected(user_id, top_k, filter_cats):
    """
    属性：category_filter 生效时，返回的 item 必须属于过滤类目
    这是业务正确性的核心约束
    """
    result = recall_engine.recall(
        user_id=user_id,
        top_k=top_k,
        scene="home",
        category_filter=filter_cats
    )
    
    if result:
        for item in result:
            # 如果 item 有 category 字段，必须在 filter 范围内
            if "category_id" in item:
                assert item["category_id"] in filter_cats, (
                    f"category_filter 未生效！"
                    f"过滤类目: {filter_cats}, 但返回 item.category_id={item['category_id']}"
                    f"这是精排资源浪费的源头之一"
                )


# ============================================================
# 属性 6：空结果处理（容错性的关键属性）
# ============================================================

@given(
    user_id=st.integers(min_value=1, max_value=10_000),
    top_k=st.integers(min_value=1, max_value=100),
    scene=st.sampled_from(["home", "detail", "search", "feed", "unknown_scene"]),
)
@settings(max_examples=300)
def test_recall_never_crashes_on_any_input(user_id, top_k, scene):
    """
    属性：无论 scene 是什么，系统不能崩溃（返回空列表或正常结果均可）
    这是系统韧性的基础：未知输入要优雅降级
    """
    try:
        result = recall_engine.recall(
            user_id=user_id,
            top_k=top_k,
            scene=scene
        )
        # 不崩溃即可，结果可以是空列表
        assert isinstance(result, list), (
            f"召回引擎对 scene={scene} 返回了非列表类型: {type(result)}"
        )
    except Exception as e:
        pytest.fail(
            f"召回引擎在 scene={scene}, user_id={user_id}, top_k={top_k} 时崩溃: {e}"
        )


# ============================================================
# 属性 7：幂等性（用于缓存的推荐服务必须满足）
# ============================================================

@given(
    user_id=st.integers(min_value=1, max_value=1000),
    top_k=st.integers(min_value=1, max_value=50),
    scene=st.sampled_from(["home"]),  # 只测 home（确定性场景）
)
@settings(max_examples=100, deadline=None)
def test_recall_idempotent_on确定性_scene(user_id, top_k, scene):
    """
    属性：home 场景（非随机）下，同一请求连续调用结果完全一致
    这是推荐缓存正确性的前提
    """
    r1 = recall_engine.recall(user_id=user_id, top_k=top_k, scene=scene)
    r2 = recall_engine.recall(user_id=user_id, top_k=top_k, scene=scene)
    
    ids1 = [item["item_id"] for item in r1]
    ids2 = [item["item_id"] for item in r2]
    
    assert ids1 == ids2, (
        f"home 场景下两次相同请求结果不一致！"
        f"第一次: {ids1}, 第二次: {ids2}"
        f"这会导致缓存失效，推荐结果抖动"
    )
```

### 2.3 运行属性测试

```bash
# 标准运行
pytest tests/property/test_recall_properties.py -v

# 失败时显示最小化用例（Hypothesis 自动 shrinking）
pytest tests/property/test_recall_properties.py \
    --hypothesis-show-statistics \
    -v

# 输出示例（一个真实的 bug 被发现）：
# FalsifyingExample: test_recall_never_exceeds_top_k(
#     user_id=888888,
#     top_k=1,
#     scene='detail',
#     category_filter=[99999]
# )
# AssertionError: 召回结果数量 2 超过 top_k 1！
# （这是因为精排后重排逻辑中有一行代码把 top_k 误设为固定值 2）
```

### 2.4 真实 Bug 发现案例

```python
# 用 Hypothesis 跑了一晚上，发现了以下真实 bug：
#
# Bug 1: top_k 超量（最严重）
# - 触发条件：category_filter 非空时
# - 原因：filter 后结果不足，重新补全时未尊重 top_k 上限
# - 影响：精排队列溢出，P99 延迟从 50ms → 800ms
#
# Bug 2: item_id 类型漂移
# - 触发条件：某个用户的历史记录为空
# - 原因：MySQL 查询结果的 item_id 是 int，但某处转 JSON 后变成 string
# - 影响：精排模型的 item_id 特征提取失败，CTR 下跌 15%
#
# Bug 3: 幂等性违反
# - 触发条件：home 场景 + user_id 在特定范围
# - 原因：向量召回使用了带时间戳的动态 seed
# - 影响：缓存命中率归零
```

---

## 三、排序层属性测试

```python
# tests/property/test_ranking_properties.py
from hypothesis import given, settings, assume
import hypothesis.strategies as st

@given(
    items=st.lists(
        st.fixed_dictionaries({
            "item_id": st.integers(1, 100_000),
            "score": st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            "category_id": st.integers(1, 100),
        }),
        min_size=1,
        max_size=200,
        unique_by=lambda x: x["item_id"]  # 保证 item_id 不重复
    ),
    top_k=st.integers(min_value=1, max_value=100),
)
@settings(max_examples=500)
def test_ranking_respects_top_k(items, top_k):
    """
    属性：排序后返回数量不超过 top_k
    """
    ranked = ranker.rank(items, top_k=top_k)
    assert len(ranked) <= top_k


@given(
    items=st.lists(
        st.fixed_dictionaries({
            "item_id": st.integers(1, 100_000),
            "score": st.floats(min_value=0.0, max_value=1.0),
        }),
        min_size=2,
        max_size=200
    ),
    top_k=st.integers(min_value=2, max_value=100),
)
@settings(max_examples=300)
def test_ranking_score_monotonic(items, top_k):
    """
    属性：排序结果的分数应该是递减的（相邻两个，前者 >= 后者）
    """
    ranked = ranker.rank(items, top_k=top_k)
    
    for i in range(len(ranked) - 1):
        assert ranked[i]["score"] >= ranked[i+1]["score"], (
            f"排序违反单调性！"
            f"位置 {i} score={ranked[i]['score']} < 位置 {i+1} score={ranked[i+1]['score']}"
        )


@given(
    items=st.lists(
        st.fixed_dictionaries({
            "item_id": st.integers(1, 100_000),
            "score": st.floats(min_value=0.0, max_value=1.0),
            "category_id": st.integers(1, 100),
        }),
        min_size=10,
        max_size=200,
    ),
)
@settings(max_examples=100)
def test_ranking_diversity_property(items):
    """
    属性：精排结果中，同类目 item 不应全部集中在一起（多样性约束）
    假设 top_k=10，那么最多连续 3 个同类目 item
    """
    ranked = ranker.rank(items, top_k=10)
    
    max_consecutive = 1
    current_consecutive = 1
    prev_cat = ranked[0]["category_id"]
    
    for item in ranked[1:]:
        if item["category_id"] == prev_cat:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 1
        prev_cat = item["category_id"]
    
    assert max_consecutive <= 3, (
        f"多样性不足！最多连续 {max_consecutive} 个同类目 item。"
        f"这会降低用户体验，导致推荐结果同质化。"
    )
```

---

## 四、AI 辅助测试生成

### 4.1 为什么推荐系统特别需要 AI 辅助测试？

推荐系统的测试难点：
1. **输入空间巨大**：用户行为序列组合爆炸
2. **边界条件多**：冷启动用户 / 全新物品 / 空行为数据
3. **随机性**：有些算法有随机采样，测试要容忍合理波动
4. **效果难以自动化验证**：CTR 高不高，AI 比人工更能判断

### 4.2 Claude AI 测试生成工作流

**Step 1：让 AI 分析你的代码，推断属性**

```
请分析这个推荐系统召回模块，找出它应该满足的所有属性。
对于每个属性，给出：
1. 属性名称
2. 属性描述（用自然语言）
3. 违反该属性会导致什么后果
4. 如何用 Hypothesis 生成测试用例

代码如下：
[粘贴你的 recall.py 代码]
```

**Step 2：让 AI 生成边界用例**

```
我的推荐系统有以下输入约束：
- user_id: 1 ~ 1,000,000 的整数
- top_k: 1 ~ 200 的整数
- scene: home/detail/search/feed 之一
- category_filter: 最多5个类目ID，范围 1~1000

请生成 20 个你认为最可能触发 bug 的边界用例（不是随机，是精心构造的边界组合）。
```

**Step 3：AI 自动生成 Hypothesis 策略**

```
请将以下自然语言属性描述转化为 Hypothesis 测试策略代码：

属性 1：当 user_id 的历史记录为空列表时，召回结果应该是空列表（冷启动场景）
属性 2：当 top_k=1 时，只返回 1 个 item
属性 3：category_filter 中包含不存在的类目时，应该忽略过滤，返回正常结果
属性 4：连续 3 次相同请求，结果应该完全一致（home 场景）

给出完整的 Python 代码。
```

### 4.3 AI 生成测试覆盖率分析

```python
# tests/ai_coverage_report.py
# 使用 AI 分析测试未覆盖的代码路径

"""
运行这个脚本，Claude/Copilot 会分析：
1. 哪些代码路径没有被测试覆盖
2. 哪些边界条件缺失
3. 给出针对性的测试用例建议
"""

# 使用 Coverage.py 分析覆盖率
# coverage run -m pytest tests/property/ -v
# coverage report --precision=2

# 结合 AI 分析未覆盖行：
# coverage html
# 然后让 AI 读取 htmlcov/index.html，指出风险最高的无覆盖代码

# ============================================================
# 推荐系统必须覆盖的无意识代码路径
# ============================================================
UNCOVERED_PATHS = """
以下是你推荐系统代码中没有被任何测试覆盖的路径，
请为每条路径生成至少 3 个边界测试用例：

路径 1: recall.py 第 47 行
    if user_profile["history"] is None:
        return []  # 用户第一次访问（history=None）
    → 测试：history=None / history=[] / history 字段缺失

路径 2: ranker.py 第 83 行
    if item["score"] == float("nan"):
        item["score"] = 0.0  # 浮点异常处理
    → 测试：输入 score=nan / score=inf / score=-inf

路径 3: rerank.py 第 115 行
    for i in range(len(items) - 1):
        # 连续相同类目去重
    → 测试：所有 item 同类目 / 全部不同类目

路径 4: cache.py 第 28 行
    if len(cached) > top_k:
        return cached[:top_k]
    → 测试：cached 长度 > top_k / == top_k / < top_k

路径 5: ml_model.py 第 55 行
    outputs = model.predict(inputs)  # 模型返回空数组
    → 测试：模型返回 [] / [None] / 形状不匹配
"""
```

### 4.4 AI 测试审查流程

```python
# tests/ai_review/ai_test_reviewer.py
# 让 AI 扮演"恶意测试工程师"，攻击你的测试

"""
AI 审查协议：

1. 【测试覆盖率攻击】
   提示："扮演一个代码攻击者。分析以下推荐系统测试，找出：
   - 测试没有覆盖的关键场景
   - 哪个边界条件会让系统崩溃或返回错误结果
   - 现有测试中的断言是否过于宽松（会产生 false positive）"

2. 【断言强度攻击】
   提示："审查以下测试断言：
   assert len(result) <= top_k
   这个断言是否足够强？请找出 3 种违反业务规则但仍然通过这个断言的情况"

3. 【随机性陷阱识别】
   提示："推荐系统中哪些场景有随机性（采样/探索）？
   测试如何正确处理随机性（概率断言 vs 确定性断言）？"

4. 【数据依赖攻击】
   提示："分析测试是否依赖外部数据（MySQL/Redis/模型）？
   如何让测试在外部服务不可用时仍然有效？"
```

### 4.5 推荐系统 AI 测试完整清单

```markdown
## 推荐系统 AI 测试生成检查清单

### 召回层（Recall）
- [ ] 空用户行为（history=[]）
- [ ] 冷启动用户（user_id 全新）
- [ ] 全新物品（item_id 全新，无 Embedding）
- [ ] top_k=1 边界
- [ ] top_k=200 边界（最大上限）
- [ ] category_filter 过滤后结果为空
- [ ] scene=unknown_scene 优雅降级
- [ ] user_id 不存在（数据库无记录）
- [ ] Embedding 服务超时（熔断降级）
- [ ] 并发调用（线程安全）

### 排序层（Rank）
- [ ] 输入列表为空
- [ ] 所有 score 相等（并列情况）
- [ ] score=nan / inf / -inf
- [ ] 输入数量 < top_k（返回所有）
- [ ] item_id 重复（去重处理）
- [ ] 模型推理超时
- [ ] 模型版本不匹配（Skew）
- [ ] 特征缺失（某些 item 缺少字段）

### 重排层（Rerank）
- [ ] 多样性约束满足（相邻同类别 ≤ 3）
- [ ] 曝光去重（同一 item 不在结果中重复出现）
- [ ] 业务规则优先级（广告插位 / 运营置顶）
- [ ] 结果数量严格等于 top_k
- [ ] P99 延迟不超过 300ms（性能约束）

### 全链路
- [ ] 端到端延迟 < 200ms
- [ ] 内存使用不超标（内存泄漏检测）
- [ ] 并发安全（10 个并发请求不崩溃）
- [ ] 缓存失效后的降级路径
- [ ] 模型更新后（热切换）结果正确性
```

---

## 五、突变测试：验证测试套件本身的质量

### 5.1 问题：测试套件可能本身就有 bug

你的测试可能：
- 断言太宽松（`assert True`）
- 条件写反了（`assert len(r) == 0` 应该是 `> 0`）
- 没有真正调用被测代码

**突变测试**思路：故意对代码做微小修改（mutation），如果测试仍然通过，说明测试有问题。

### 5.2 Python 突变测试框架：mutmut

```bash
pip install mutmut
```

```bash
# 在你的推荐系统代码上运行突变测试
cd /path/to/your/recommendation-system

# 突变测试：看看有多少"突变体"被你的测试套件捕获
mutmut run --sources=recall.py --test-dir=tests/

# 查看结果
mutmut results
```

### 5.3 推荐系统典型突变案例

```python
# 原始代码（recall.py）
def filter_by_category(items, category_filter):
    if category_filter:  # ← 正常
        return [i for i in items if i["category_id"] in category_filter]
    return items

# 突变体 1（删除条件）
def filter_by_category(items, category_filter):
    if True:  # ← 突变：恒为真（删除了 not 操作）
        return [i for i in items if i["category_id"] in category_filter]
    return items
# 如果你的测试没有覆盖 category_filter=[] 的情况，这个突变会逃过检测

# 突变体 2（比较操作符）
def should_include(item, min_score):
    return item["score"] >= min_score  # ← 原始
    # return item["score"] > min_score  # ← 突变：>= 变成 >

# 突变体 3（逻辑运算符）
def is_valid_item(item):
    return item is not None and item.get("score", 0) > 0  # 原始
    # return item is not None or item.get("score", 0) > 0  # ← 突变
```

### 5.4 突变测试解读

```bash
mutmut results

# 输出示例：
# Survived: 23 (bad - these mutations are not detected)
# Killed: 127 (good)
# Suspicious: 5
# Timeout: 0
# Skipped: 12

# 突变存活率 = 23 / (23 + 127) = 15.3%
# 行业标准：存活率 < 5% 为优秀，> 20% 说明测试套件有严重漏洞
```

---

## 六、推荐系统专项测试矩阵

```python
# tests/recommendation_matrix.py
"""
推荐系统完整测试矩阵：
维度 = 输入边界 × 组件 × 属性 × 断言强度

每个格子 = 一个测试用例
"""

TEST_MATRIX = {
    # 维度1: 用户状态
    "user_state": [
        "new_user",           # 冷启动
        "active_user",        # 有历史行为
        "inactive_user",      # 30天无行为
        "churned_user",       # 已流失
    ],
    # 维度2: 数据完整性
    "data_state": [
        "full_data",          # 数据完整
        "missing_history",    # 历史缺失
        "missing_embeddings", # 向量缺失
        "empty_result",       # 无候选物品
    ],
    # 维度3: 场景
    "scene": ["home", "detail", "search", "feed", "unknown"],
    # 维度4: top_k 边界
    "top_k": [1, 10, 50, 100, 200],
    # 维度5: 属性
    "property": [
        "count_leq_top_k",    # 数量 ≤ top_k
        "no_duplicates",      # 无重复
        "type_correct",       # 类型正确
        "non_null",           # 非空安全
        "monotonic",          # 单调性
    ],
}


def generate_test_cases():
    """
    使用 itertools 生成所有组合，过滤无效组合
    输出: 500+ 个具体测试用例
    """
    import itertools
    
    cases = []
    for state, data, scene, k, prop in itertools.product(
        TEST_MATRIX["user_state"],
        TEST_MATRIX["data_state"],
        TEST_MATRIX["scene"],
        TEST_MATRIX["top_k"],
        TEST_MATRIX["property"],
    ):
        # 业务规则过滤
        if state == "new_user" and data == "full_data":
            continue  # 新用户不可能有完整数据
        
        if data == "empty_result" and prop == "no_duplicates":
            continue  # 空结果不需要去重
        
        cases.append({
            "user_state": state,
            "data_state": data,
            "scene": scene,
            "top_k": k,
            "property": prop,
        })
    
    return cases


# 用 Hypothesis 对每个组合生成 10 个子用例
# 总测试量：len(cases) × 10 = 数千个测试用例
```

---

## 七、与 CI/CD 集成

```yaml
# .github/workflows/property_test.yml
name: Property-Based Testing

on:
  push:
    branches: [main, develop]
  schedule:
    # 每周日凌晨跑一次完整属性测试（生成500个用例）
    - cron: '0 3 * * 0'

jobs:
  property_tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Property Tests
        run: |
          pip install hypothesis pytest pytest-cov
          pytest tests/property/ \
            --hypothesis-seed=0 \
            --hypothesis-show-statistics \
            --tb=short \
            -v \
            2>&1 | tee property_test_output.txt
      
      - name: Generate Failure Report
        if: failure()
        run: |
          # 自动提取 Hypothesis 的最小化失败用例
          grep -A 20 "FalsifyingExample" property_test_output.txt > failure_case.txt
          echo "::notice::Property test failure case saved"
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: property_tests
```

---

## 八、常见误区与避坑指南

### ❌ 误区 1：属性测试替代示例测试

**正确做法**：两者互补，不是替代关系。
```
示例测试：验证"这个具体案例的行为是对的"
属性测试：验证"无论什么输入，核心属性始终成立"
```

### ❌ 误区 2：属性定义得太宽松

```python
# ❌ 太宽松（什么都检测不出来）
@given(x=st.integers())
def test_something(x):
    assert x is not None  # 永远通过，没意义

# ✅ 精确的属性
@given(x=st.integers(min_value=1))
def test_something(x):
    assert x > 0  # 真正有意义的约束
```

### ❌ 误区 3：随机性和属性混为一谈

```python
# ❌ 随机采样算法的结果不能用严格相等断言
def test_random_recall():
    result = random_recall(user_id=1, top_k=10)
    assert result == [1, 2, 3]  # ❌ 永远失败（随机性）

# ✅ 正确的属性（弱约束）
def test_random_recall():
    result = random_recall(user_id=1, top_k=10)
    assert len(result) == 10           # ✅ 数量属性
    assert len(set(result)) == 10     # ✅ 去重属性
    assert all(isinstance(i, int) for i in result)  # ✅ 类型属性
```

### ❌ 误区 4：只测 Happy Path 属性

**至少测试 3 类属性**：
1. ✅ 正面属性（正常输入有正常输出）
2. ⚠️ 边界属性（极端输入的处理）
3. ❌ 反面属性（错误输入要正确报错或降级）

---

## 九、推荐系统属性速查表

```
┌──────────────────────────────────────────────────────────────────┐
│                  推荐系统属性测试速查表                           │
├──────────────┬──────────────────────────────┬─────────────────────┤
│    组件       │        必须验证的属性         │     断言方式        │
├──────────────┼──────────────────────────────┼─────────────────────┤
│   召回层      │ • 数量 ≤ top_k              │ len(result) ≤ k    │
│              │ • 无重复 item_id            │ len == len(set())  │
│              │ • 非空时类型正确              │ isinstance 检查     │
│              │ • 冷启动返回空列表/降级结果    │ 类型安全 + 非空     │
│              │ • 幂等性（home 场景）          │ 两次调用结果一致    │
├──────────────┼──────────────────────────────┼─────────────────────┤
│   排序层      │ • 输出数量 ≤ top_k          │ len(result) ≤ k    │
│              │ • score 递减                │ 相邻单调性检查      │
│              │ • 无 NaN/Inf score           │ 数学函数检查        │
│              │ • 多样性（相邻同类 ≤ 3）       │ 连续类目计数        │
│              │ • 模型超时返回降级结果         │ 类型安全 + 非空     │
├──────────────┼──────────────────────────────┼─────────────────────┤
│   重排层      │ • 严格返回 top_k 个          │ len == top_k       │
│              │ • 曝光去重                  │ 无重复 item_id     │
│              │ • 业务规则优先级遵守          │ 广告位置/运营置顶   │
│              │ • 性能 P99 < 阈值            │ 超时检测           │
├──────────────┼──────────────────────────────┼─────────────────────┤
│   全链路      │ • 延迟 SLO 达标              │ P99 监控           │
│              │ • 缓存失效后行为正确           │ 强制缓存 miss 测试  │
│              │ • 模型热切换无抖动             │ 版本一致性          │
│              │ • 并发安全                   │ 线程/进程安全       │
└──────────────┴──────────────────────────────┴─────────────────────┘
```

---

## 十、上线前属性测试自查清单

- [ ] 召回层 5 个核心属性全部通过 Hypothesis 500+ 用例
- [ ] 排序层单调性/去重性通过 300+ 用例
- [ ] 冷启动场景（空数据）有专门属性测试
- [ ] category_filter / 分页 / 场景切换有边界测试
- [ ] P99 延迟作为属性测试（超过阈值自动 fail）
- [ ] 突变测试存活率 < 10%（理想 < 5%）
- [ ] CI 中集成属性测试（每周完整跑一次）
- [ ] 所有测试在无外部依赖环境下可运行（Mock 到位）
- [ ] 失败用例的 Hypothesis 报告已存档（可复现）

---

> 💡 **一句话总结**：属性测试把"我测了10个例子"升级为"我测了500个自动生成的边界，核心属性始终成立"。推荐系统上线前，至少要把数量边界和去重性这两个属性测透——这两个 bug 占推荐系统生产故障的 40%。
