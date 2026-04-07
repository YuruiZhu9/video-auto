# GraphQL 推荐系统实战：灵活查询与 N+1 解决之道

> 本专题对应学习路径第四阶段「接口层设计」补充内容

## 概念解释

### REST 的痛点

**Over-fetching（过度获取）：**
```
GET /api/user/123  → 返回用户全部50个字段
只想要 name + avatar → 被迫拿全部
```

**Under-fetching（获取不足）：**
```javascript
// 需要3次请求才能凑齐一个推荐卡片的数据
const user = await fetch('/api/user/123')
const items = await fetch('/api/recommend/123?count=10')
const details = await Promise.all(
  items.map(item => fetch(`/api/item/${item.id}`))  // N次！
)
// 10个推荐 → 12次请求
```

GraphQL 解决了这两个问题：**客户端按需声明字段，一次请求拿完所有数据。**

### GraphQL 三大核心概念

| 概念 | 作用 | 类比 |
|------|------|------|
| **Schema** | 定义类型系统和API能力 | 数据库DDL |
| **Query** | 读操作，类似GET | SELECT |
| **Mutation** | 写操作，类似POST/PUT | INSERT/UPDATE |

---

## 一、推荐系统 GraphQL Schema 设计

### 基础类型定义

```python
# graphql/schema.py
import strawberry
from typing import List, Optional
from enum import Enum

@strawberry.enum
class RecommendScene(Enum):
    """推荐场景枚举"""
    HOME_FEED = "home_feed"      # 首页推荐
    RELATED_ITEMS = "related_items"  # 关联推荐
    PERSONALIZED = "personalized"    # 个性化推荐
    HOT_TRENDING = "hot_trending"    # 热门推荐

@strawberry.type
class Item:
    """推荐物品类型"""
    id: str
    title: str
    cover_url: str
    author: str
    price: Optional[float]
    rating: float
    tags: List[str]
    # 不需要的字段根本不会出现——这是GraphQL的核心价值

@strawberry.type
class UserProfile:
    """用户画像类型"""
    id: str
    nickname: str
    avatar_url: str
    follow_count: int
    preference_tags: List[str]

@strawberry.type
class RecommendResult:
    """推荐结果（含元数据）"""
    items: List[Item]
    scene: str
    next_cursor: Optional[str]  # 游标分页，不使用页码
    total_hint: int             # 估算总数（不是精确值，避免深分页）
    request_id: str              # 追踪ID

@strawberry.type
class Interaction:
    """用户行为类型"""
    id: str
    user_id: str
    item_id: str
    action_type: str   # click / view / purchase / like / unlike
    created_at: str
```

### 完整的 Query 定义

```python
@strawberry.type
class Query:

    @strawberry.field
    async def recommend(
        self,
        user_id: str,
        scene: RecommendScene,
        count: int = 10,
        cursor: Optional[str] = None,
    ) -> RecommendResult:
        """
        推荐查询：一次请求返回推荐列表 + 用户信息 + 分页游标
        
        GraphQL优势示例：
        {
            recommend(userId: "u123", scene: HOME_FEED, count: 5) {
                items { id title coverUrl tags }
                scene
                nextCursor
            }
        }
        """
        # 底层调用推荐引擎（可以是gRPC/Redis/模型服务）
        result = await recommendation_engine.get_recommendations(
            user_id=user_id,
            scene=scene.value,
            count=count,
            cursor=cursor,
        )
        return RecommendResult(
            items=[Item(**item) for item in result["items"]],
            scene=scene.value,
            next_cursor=result.get("next_cursor"),
            total_hint=result.get("total_hint", 0),
            request_id=result.get("request_id", ""),
        )

    @strawberry.field
    async def batch_recommend(
        self,
        requests: List[RecommendRequest],
    ) -> List[RecommendResult]:
        """
        批量推荐：一次请求多个场景/用户的推荐
        解决：移动端多Tab同时需要多路召回的场景
        
        GraphQL优势示例：
        {
            batchRecommend(requests: [
                {userId: "u1", scene: HOME_FEED},
                {userId: "u1", scene: RELATED_ITEMS},
                {userId: "u2", scene: PERSONALIZED}
            ]) {
                items { id title }
            }
        }
        """
        results = await asyncio.gather(*[
            recommendation_engine.get_recommendations(**req)
            for req in requests
        ])
        return [RecommendResult(**r) for r in results]

    @strawberry.field
    async def user_profile(self, user_id: str) -> Optional[UserProfile]:
        """用户画像查询"""
        profile = await user_service.get_profile(user_id)
        return UserProfile(**profile) if profile else None

    @strawberry.field
    async def item(self, id: str) -> Optional[Item]:
        """物品详情查询"""
        item = await item_service.get_by_id(id)
        return Item(**item) if item else None

    @strawberry.field
    async def search_items(
        self,
        keyword: str,
        tags: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "relevance",
        first: int = 20,
        after: Optional[str] = None,
    ) -> ItemConnection:
        """
        高级搜索：支持多条件过滤 + 排序 + 分页
        一个Query替代了REST的多个endpoint
        """
        items, has_next, end_cursor = await search_engine.search(
            keyword=keyword,
            filters={"tags": tags, "price_range": [min_price, max_price]},
            sort_by=sort_by,
            limit=first + 1,
            cursor=after,
        )
        return ItemConnection(
            items=[Item(**i) for i in items[:first]],
            page_info=PageInfo(
                has_next_page=has_next,
                end_cursor=end_cursor,
            )
        )
```

---

## 二、Mutation：用户行为收集

### REST 方式的问题

```javascript
// REST：行为上报需要3个endpoint，客户端调用碎片化
POST /api/events/click
POST /api/events/view  
POST /api/events/purchase
POST /api/events/rate

// GraphQL：一个mutation搞定
```

### GraphQL Mutation 实现

```python
@strawberry.type
class Mutation:

    @strawberry.mutation
    async def record_interaction(
        self,
        user_id: str,
        item_id: str,
        action_type: str,
        duration_ms: Optional[int] = None,
        source: Optional[str] = None,
    ) -> InteractionResult:
        """
        统一行为记录mutation
        支持的action_type: click / view / purchase / like / unlike / share / comment
        """
        # 参数校验
        valid_actions = {"click", "view", "purchase", "like", "unlike", "share", "comment"}
        if action_type not in valid_actions:
            raise GraphQLError(f"action_type必须是: {valid_actions}")

        interaction = await interaction_service.record(
            user_id=user_id,
            item_id=item_id,
            action_type=action_type,
            duration_ms=duration_ms,
            source=source,
        )
        # 返回简洁结果，不需要完整Interaction对象
        return InteractionResult(
            success=True,
            interaction_id=interaction["id"],
            message="记录成功"
        )

    @strawberry.mutation
    async def batch_record_interactions(
        self,
        events: List[InteractionEvent],
    ) -> BatchResult[InteractionResult]:
        """
        批量行为上报——移动端离线场景必备
        用户在地铁里刷了20个内容，信号恢复后一次上报
        """
        results = await interaction_service.batch_record([
            {
                "user_id": e.user_id,
                "item_id": e.item_id,
                "action_type": e.action_type,
                "timestamp": e.timestamp,
            }
            for e in events
        ])
        return BatchResult(
            total=len(events),
            success_count=sum(1 for r in results if r["success"]),
            results=[InteractionResult(success=r["success"], **r) for r in results]
        )

    @strawberry.mutation
    async def update_user_preferences(
        self,
        user_id: str,
        preference_tags: List[str],
    ) -> UserProfile:
        """用户偏好主动更新"""
        updated = await user_service.update_preferences(user_id, preference_tags)
        return UserProfile(**updated)

    @strawberry.mutation
    async def feed_back(
        self,
        user_id: str,
        item_id: str,
        feedback_type: str,  # "interested" | "not_interested" | "report"
        reason: Optional[str] = None,
    ) -> FeedbackResult:
        """用户显式反馈（重要！用于模型训练信号）"""
        await feedback_service.record(
            user_id=user_id,
            item_id=item_id,
            feedback_type=feedback_type,
            reason=reason,
        )
        # 触发推荐引擎重新排序（实时调整）
        await recommendation_engine.invalidate_user_cache(user_id)
        return FeedbackResult(success=True, message="感谢反馈")
```

---

## 三、N+1 问题与 DataLoader 解决方案

### 经典 N+1 场景

```python
# ❌ N+1 问题：获取10个推荐后，再查10次详情
@strawberry.field
async def recommend(self, user_id: str, count: int = 10) -> List[Item]:
    result = await recommendation_engine.get_recommendations(user_id, count)
    # result = [{item_id: "i1"}, {item_id: "i2"}, ...]  10个
    items = []
    for r in result:  # 循环10次！
        item = await item_service.get_by_id(r["item_id"])  # 10次DB查询
        items.append(Item(**item))
    return items
# 1次推荐查询 + 10次详情查询 = 11次数据库往返
```

### DataLoader 批量加载器

```python
# graphql/dataloaders.py
from strawberry.dataloader import DataLoader
from typing import List, Optional
import asyncio

def create_item_loader(item_service) -> DataLoader[str, Optional[dict]]:
    """创建物品批量加载器——解决N+1问题的关键"""
    
    async def load_batch(item_ids: List[str]) -> List[Optional[dict]]:
        """
        DataLoader会自动收集一个event loop内的所有请求，合并为一次批量查询
        即使代码里写了10次get_by_id，DataLoader也会合并为1次batch查询
        """
        # 一次批量查询：SELECT * FROM items WHERE id IN (ids)
        items = await item_service.batch_get_by_ids(item_ids)
        # 构建 id → item 映射
        item_map = {item["id"]: item for item in items}
        # 按原顺序返回（DataLoader要求顺序一致）
        return [item_map.get(item_id) for item_id in item_ids]
    
    return DataLoader(load_fn=load_batch, max_batch_size=100)


def create_user_loader(user_service) -> DataLoader[str, Optional[dict]]:
    async def load_batch(user_ids: List[str]) -> List[Optional[dict]]:
        users = await user_service.batch_get_by_ids(user_ids)
        user_map = {u["id"]: u for u in users}
        return [user_map.get(uid) for uid in user_ids]
    return DataLoader(load_fn=load_batch, max_batch_size=100)


def create_recall_strategy_loader(recall_engine) -> DataLoader[str, List[dict]]:
    """批量加载多路召回结果"""
    async def load_batch(scene_names: List[str]) -> List[List[dict]]:
        results = await recall_engine.batch_get_strategies(scene_names)
        return [results.get(name, []) for name in scene_names]
    return DataLoader(load_fn=load_batch, max_batch_size=20)
```

### 带 DataLoader 的完整 Query

```python
@strawberry.type
class Query:
    # DataLoader通过上下文注入（每个请求独立）
    @strawberry.field
    async def recommend_with_items(
        self,
        info: strawberry.Info,
        user_id: str,
        count: int = 10,
    ) -> List[ItemWithAuthor]:
        """
        一次GraphQL查询，返回推荐列表（包含物品详情+作者信息）
        
        {
            recommendWithItems(userId: "u123", count: 5) {
                item { id title coverUrl }
                author { id nickname avatarUrl }
            }
        }
        
        幕后：虽然同时查询了items和authors，但DataLoader会把
        10次item查询合并为1次、作者查询合并为1次 → 总共2次DB查询
        """
        # 获取DataLoader实例（每个请求独立，无状态共享）
        item_loader: DataLoader = info.context["item_loader"]
        author_loader: DataLoader = info.context["author_loader"]
        
        # Step 1: 推荐引擎获取推荐ID列表
        rec_result = await recommendation_engine.get_recommendations(
            user_id=user_id, count=count
        )
        item_ids = [item["id"] for item in rec_result["items"]]
        
        # Step 2: DataLoader批量加载（内部合并N次调用为1次）
        # 即使下面写循环，DataLoader也会在当前event loop末尾合并
        items_with_authors = []
        for item_id in item_ids:
            item = await item_loader.load(item_id)
            if item:
                author = await author_loader.load(item["author_id"])
                items_with_authors.append(ItemWithAuthor(
                    item=Item(**item),
                    author=Author(**author) if author else None,
                ))
        
        return items_with_authors

    @strawberry.field
    async def explore_feed(
        self,
        info: strawberry.Info,
        tag: str,
        count: int = 20,
    ) -> List[ItemWithMetrics]:
        """
        推荐解释性查询：展示为什么推荐了这个内容
        DataLoader自动处理多层级N+1
        
        {
            exploreFeed(tag: "machine_learning") {
                item { id title }
                metrics { viewCount likeCount clickRate }
                recallReason  # "你关注machine_learning + 热门度加权"
            }
        }
        """
        item_loader: DataLoader = info.context["item_loader"]
        metrics_loader: DataLoader = info.context["metrics_loader"]
        
        items = await item_service.get_by_tag(tag, count=count)
        item_ids = [i["id"] for i in items]
        
        # 三个DataLoader并行触发，最后按序组装
        loaded_items = await asyncio.gather(*[
            item_loader.load(iid) for iid in item_ids
        ])
        loaded_metrics = await asyncio.gather(*[
            metrics_loader.load(iid) for iid in item_ids
        ])
        
        return [
            ItemWithMetrics(
                item=Item(**it) if it else None,
                metrics=ItemMetrics(**m) if m else None,
                recall_reason=f"标签匹配: {tag}",
            )
            for it, m in zip(loaded_items, loaded_metrics)
        ]
```

---

## 四、与 REST / gRPC 混合架构

GraphQL 不是银弹，**推荐系统的核心推理部分仍然用 gRPC/Thrift**，GraphQL 只做前端 BFF（Backend For Frontend）层：

```
┌─────────────┐         ┌──────────────────┐
│   Mobile    │ ──HTTPS──│  GraphQL BFF     │
│   Web       │         │  (FastAPI+Strawberry)│
│   微信小程序 │         │  负责：聚合/裁剪  │
└─────────────┘         │ 鉴权/限流/缓存    │
                       └───────┬──────────┘
                               │ gRPC内部通信（高性能）
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
        ┌───────────┐  ┌────────────┐  ┌────────────┐
        │ 召回引擎  │  │ 精排引擎   │  │ 用户画像   │
        │ gRPC/Thrift│ │ gRPC/Triton│  │ gRPC       │
        └───────────┘  └────────────┘  └────────────┘
```

### GraphQL 网关实现

```python
# graphql/gateway.py
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter
from starlette.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram
import time

# ── 指标采集 ──────────────────────────────────
graphql_request_total = Counter(
    "graphql_requests_total", "GraphQL请求总数",
    ["operation", "status"]
)
graphql_request_duration = Histogram(
    "graphql_request_duration_seconds", "GraphQL请求延迟",
    ["operation"]
)

async def get_context(request: Request):
    """每个请求创建独立上下文（DataLoader不跨请求共享）"""
    # 从依赖注入获取服务（应用启动时初始化）
    item_loader = create_item_loader(request.state.item_service)
    user_loader = create_user_loader(request.state.user_service)
    metrics_loader = create_metrics_loader(request.state.metrics_service)
    
    return {
        "request": request,
        "item_loader": item_loader,
        "user_loader": user_loader,
        "metrics_loader": metrics_loader,
        "request_id": request.headers.get("X-Request-ID", ""),
    }

# ── Strawberry GraphQL Router ────────────────
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # 启用自动文档（schema introspection）
)

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True,  # 开发环境：/graphql 提供可视化IDE
)

# ── FastAPI 应用 ─────────────────────────────
app = FastAPI(title="推荐系统 GraphQL API", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "X-Request-ID"],
)

# 限流中间件
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/graphql":
        client_ip = request.client.host
        allowed = await rate_limiter.check(f"graphql:{client_ip}", limit=100, window=60)
        if not allowed:
            return JSONResponse({"errors": [{"message": "请求过于频繁"}]}, status_code=429)
    response = await call_next(request)
    return response

app.include_router(graphql_app, prefix="/graphql")
```

---

## 五、Schema 进阶：Relay 风格分页

### 为什么不用传统 page/per_page？

```javascript
// ❌ REST风格分页：页码在推荐系统中是灾难
GET /api/recommend?page=3&per_page=10
// 推荐是实时计算的！第3页的item在用户刷新后可能消失
// 页码分页导致：重复推荐 / 遗漏推荐

// ✅ Cursor分页：稳定的游标
GET /api/recommend?cursor=eyJpZCI6MTIzfQ&limit=10
// 游标 = 上一页最后一条的加密信息
// 用户向下加载时，不会出现重复
```

### Relay Connection 规范实现

```python
@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str]
    end_cursor: Optional[str]

@strawberry.type
class ItemEdge:
    node: Item
    cursor: str  # 游标：Base64编码的 item_id

@strawberry.type
class ItemConnection:
    """Relay标准Connection类型"""
    edges: List[ItemEdge]
    page_info: PageInfo
    total_count: int  # 估算总数（可选）

@strawberry.type
class Query:

    @strawberry.field
    async def recommend_paginated(
        self,
        user_id: str,
        scene: RecommendScene,
        first: int = 10,                  # 前N条
        after: Optional[str] = None,       # 游标（之前最后一条的cursor）
        last: Optional[int] = None,        # 后N条（before游标）
        before: Optional[str] = None,
    ) -> ItemConnection:
        """
        Relay风格分页：稳定、可预测、无重复
        
        查询示例：
        {
            recommendPaginated(userId: "u123", scene: HOME_FEED, first: 5, after: "eyJpZCI6IjEwIn0=") {
                edges {
                    node { id title }
                    cursor
                }
                pageInfo { hasNextPage endCursor }
            }
        }
        
        加载更多时，把 pageInfo.endCursor 作为下次查询的 after 参数
        """
        # 解析游标
        cursor = decode_cursor(after) if after else None
        
        result = await recommendation_engine.get_recommendations(
            user_id=user_id,
            scene=scene.value,
            count=first + 1,  # 多查1条判断是否有下一页
            cursor=cursor,
        )
        
        items = result["items"]
        has_next = len(items) > first
        display_items = items[:first]
        
        edges = [
            ItemEdge(
                node=Item(**item),
                cursor=encode_cursor(item["id"]),  # Base64编码item_id
            )
            for item in display_items
        ]
        
        return ItemConnection(
            edges=edges,
            page_info=PageInfo(
                has_next_page=has_next,
                has_previous_page=(after is not None),
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None,
            ),
            total_count=result.get("total_hint", 0),
        )
```

---

## 六、查询复杂度控制（防止滥用）

GraphQL 的灵活性也是双刃剑——客户端可能一次请求成千上万条数据：

```python
# graphql/security.py
from strawberry.schema.config import StrawberryConfig
from graphql import GraphQLError

class ComplexityAnalyzer:
    """查询复杂度分析器"""
    
    # 各类型字段的复杂度权重
    FIELD_COSTS = {
        "Item": 1,           # 普通字段
        "Item.items": 2,     # 嵌套列表
        "UserProfile": 1,
        "RecommendResult": 3,   # 推荐涉及复杂计算
    }
    
    MAX_COMPLEXITY = 1000   # 单次查询最大复杂度
    MAX_DEPTH = 10          # 最大嵌套深度
    
    def analyze(self, query_document) -> int:
        """计算查询复杂度（字段数 × 嵌套权重）"""
        complexity = 0
        
        def walk(node, depth=0):
            nonlocal complexity
            if depth > self.MAX_DEPTH:
                raise GraphQLError(f"查询深度超过{self.MAX_DEPTH}层")
            # 累加字段权重
            complexity += self.FIELD_COSTS.get(node.name.value, 1)
        
        for definition in query_document.definitions:
            if definition.kind == "operation_definition":
                walk(definition.selection_set)
        
        return complexity

# 在schema中启用复杂度限制
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    config=StrawberryConfig(
        enable_validation=True,
    )
)

# 中间件层：解析并拒绝超复杂查询
@app.middleware("http")
async def complexity_check(request: Request, call_next):
    if request.url.path == "/graphql" and request.method == "POST":
        body = await request.json()
        query = body.get("query", "")
        complexity = analyzer.analyze(parse(query))
        if complexity > ComplexityAnalyzer.MAX_COMPLEXITY:
            return JSONResponse({
                "errors": [{"message": f"查询复杂度{complexity}超过限制{ComplexityAnalyzer.MAX_COMPLEXITY}"}]
            }, status_code=400)
    return await call_next(request)
```

---

## 七、生产环境检查清单

| 检查项 | 说明 | 优先级 |
|--------|------|--------|
| ✅ DataLoader | 每个resolver都用DataLoader了吗？ | 必须 |
| ✅ 超时控制 | GraphQL HTTP超时 + Resolver超时 | 必须 |
| ✅ 查询复杂度 | 限制单次查询复杂度，防止恶意查询 | 必须 |
| ✅ CORS配置 | 禁止任意来源 | 必须 |
| ✅ 限流 | GraphQL层限流（比REST更危险，一次顶10次REST请求） | 必须 |
| ✅ 认证 | JWT/Bearer Token验证 | 必须 |
| ✅ 监控 | 请求量/延迟/错误率/复杂度分布 | 必须 |
| ✅ Persisted Queries | 生产环境用哈希预存查询，防注入 | 建议 |
| ✅ Query_depth_limit | 限制嵌套深度 | 建议 |
| ✅ 限流字段 | 禁止 `__schema` introspection（生产环境） | 建议 |

---

## 适用场景

- **移动端多Tab推荐**：一次GraphQL请求聚合多个场景的推荐结果
- **前端灵活展示**：不同页面展示不同字段，GraphQL按需返回
- **实时行为反馈**：用户点击后立即刷新推荐，无需刷新页面
- **探索式推荐**：用户可以自由过滤/排序推荐结果

## 常见误区

- ❌ **把GraphQL当数据库用**：N+1问题导致性能灾难，DataLoader必须用
- ❌ **所有API都迁移到GraphQL**：推荐推理引擎内部用gRPC性能更好
- ❌ **不用限流**：GraphQL一次请求可以触发大量计算，比REST更危险
- ❌ **缺少超时**：GraphQL resolver卡住会导致整个请求超时
- ❌ **Schema设计过度**：一开始用简单类型，后续按需演进

## 反例 vs 正例

```python
# ❌ 过度设计的GraphQL Schema（企业内部工具不需要这么复杂）
@strawberry.type
class Node:
    id: ID!
    
@strawberry.type  
class UserNode(Node):
    name: str

# ✅ 推荐系统实用Schema：够用就好
@strawberry.type
class RecommendResult:
    items: List[Item]
    next_cursor: Optional[str]
```
