# 推荐系统工程师生产级编码 Checklist

> 从"能跑"到"能上线"的 30 项工程规范

---

## 一、API 层规范

### 1. 请求校验与响应格式

```python
# ❌ 反例：裸接收参数
@app.post("/recommend")
def recommend(user_id: int, item_id: int):
    # 无校验，可能收到 None、空串、负数
    result = recommend_impl(user_id, item_id)
    return result

# ✅ 正例：Pydantic 强制校验 + 统一响应格式
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class RecommendRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    scene: str = Field(..., pattern="^(home|detail|search)$")
    count: int = Field(default=20, ge=1, le=100)
    extra: Optional[dict] = None

class RecommendResponse(BaseModel):
    code: int = 0
    msg: str = "success"
    request_id: str = ""
    data: List[RecommendItem]
    latency_ms: int = 0

@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest, req_id: str = Header(default_factory=lambda: uuid4().hex)):
    start = time_ms()
    items = await recommend_impl(req)
    return RecommendResponse(
        request_id=req_id,
        data=items,
        latency_ms=time_ms() - start
    )
```

### 2. 全链路请求追踪

```python
# ✅ 关键链路节点埋点，request_id 贯穿整个调用链
import logging
from contextvars import ContextVar
from fastapi import Request

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", uuid4().hex)
    request_id_var.set(req_id)
    logger = logging.getLogger("recommend")
    logger.info(f"[{req_id}] {request.method} {request.url.path}")
    # 记录完整请求路径
    return await call_next(request)

# 在任何地方都能拿到 request_id
def any_deep_function():
    req_id = request_id_var.get()
    logger.info(f"[{req_id}] 召回完成，候选数: 50")
```

### 3. 限流保护

```python
# ✅ Redis 滑动窗口限流，每用户 100 次/分钟
import redis.asyncio as redis

_limiter_script = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)
if count < limit then
    redis.call('ZADD', key, now, now .. '-' .. math.random())
    redis.call('EXPIRE', key, window)
    return 1
end
return 0
"""

async def check_rate_limit(user_id: str, limit: int = 100, window: int = 60) -> bool:
    r = redis.from_url(REDIS_URL)
    key = f"rate:{user_id}"
    result = await r.eval(_limiter_script, 1, key, limit, window, int(time.time() * 1000))
    return result == 1

@app.post("/recommend")
async def recommend(req: RecommendRequest):
    if not await check_rate_limit(req.user_id):
        raise HTTPException(429, "请求过于频繁，请稍后再试")
```

### 4. 敏感信息脱敏

```python
# ✅ 响应脱敏中间件
class DesensitizeMiddleware:
    SENSITIVE_FIELDS = {"phone", "email", "id_card", "address"}

    def process(self, data: dict) -> dict:
        result = data.copy()
        for field in self.SENSITIVE_FIELDS:
            if field in result:
                val = str(result[field])
                if len(val) >= 7:
                    result[field] = val[:3] + "****" + val[-4:]
                else:
                    result[field] = "****"
        return result
```

### 5. 统一错误处理

```python
# ❌ 反例：不同地方随意抛异常，无结构
raise Exception("出错了")
raise ValueError("参数错误")

# ✅ 正例：统一异常类 + 全局处理器
class RecommendError(Exception):
    def __init__(self, code: int, msg: str, details: dict = None):
        self.code = code
        self.msg = msg
        self.details = details or {}
        super().__init__(msg)

class UserNotFoundError(RecommendError):
    def __init__(self, user_id: str):
        super().__init__(1001, f"用户不存在: {user_id}", {"user_id": user_id})

class RecallEmptyError(RecommendError):
    def __init__(self, scene: str):
        super().__init__(1002, "召回结果为空", {"scene": scene})

@app.exception_handler(RecommendError)
async def recommend_error_handler(request: Request, exc: RecommendError):
    req_id = request_id_var.get()
    return JSONResponse({
        "code": exc.code,
        "msg": exc.msg,
        "details": exc.details,
        "request_id": req_id
    })
```

---

## 二、业务逻辑层规范

### 6. 核心业务逻辑禁止外部依赖注入

```python
# ✅ 领域层纯 Python，无框架依赖，可测试
# domain/engines.py
class RecommendationEngine:
    """核心推荐引擎——纯业务逻辑，零框架依赖"""

    def __init__(self, recall_strategies: List[BaseRecallStrategy]):
        self._recall_strategies = recall_strategies

    def recommend(self, context: RecommendContext) -> List[RecommendItem]:
        # 纯内存计算，可直接单元测试
        candidates = self._multi_recall(context)
        ranked = self._rank(candidates, context)
        return self._rerank(ranked, context)

    def _multi_recall(self, context: RecommendContext) -> List[RecommendItem]:
        results = []
        for strategy in self._recall_strategies:
            try:
                items = strategy.recall(context)
                results.extend(items)
            except Exception as e:
                logger.warning(f"召回策略 {strategy.name} 失败: {e}")
                continue  # 单路失败不影响其他路
        return self._dedup_and_sort(results)
```

### 7. 空值防御链

```python
# ❌ 反例：无防御，N 级空指针风险
user = db.get_user(uid)
recs = engine.recommend(user.id, user.profile["tags"])

# ✅ 正例：防御式编程
from typing import Optional
from dataclasses import dataclass

@dataclass
class RecommendContext:
    user_id: str
    scene: str
    tags: List[str] = field(default_factory=list)
    age: int = 0

    @classmethod
    def from_user(cls, user: Optional[dict]) -> "RecommendContext":
        if not user:
            return cls(user_id="", scene="home")
        return cls(
            user_id=str(user.get("id", "")),
            scene=user.get("scene", "home"),
            tags=user.get("tags") or [],
            age=user.get("age", 0) or 0,
        )
```

### 8. 日志规范（结构化 + 分级）

```python
# ❌ 反例：字符串拼接日志，grep 困难
logger.info(f"召回完成，数量={len(items)}")
logger.info(f"用户 {uid} 推荐耗时 {cost}ms")

# ✅ 正例：结构化 JSON 日志
import structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()

log.info("recommend.recall.done",
    request_id=req_id,
    user_id=user_id,
    scene=scene,
    candidate_count=len(candidates),
    recall_strategies=[s.name for s in strategies],
    latency_ms=elapsed_ms
)

# 日志分级：
# DEBUG: 详细执行路径（开发环境）
# INFO:  业务关键节点（召回/排序/重排完成）
# WARNING: 可恢复异常（某路召回失败、降级触发）
# ERROR:   不可恢复异常（必须关注）
```

---

## 三、数据访问层规范

### 9. SQL 防注入

```python
# ❌ 反例：字符串拼接 SQL（绝对禁止）
query = f"SELECT * FROM users WHERE id = {user_id}"  # 注入风险！

# ✅ 正例：参数化查询
async with pool.acquire() as conn:
    result = await conn.fetch(
        "SELECT * FROM users WHERE id = $1 AND status = $2",
        user_id, "active"
    )

# ✅ MySQL 参数化
async with pool.acquire() as conn:
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT * FROM users WHERE id = %s AND status = %s",
            (user_id, "active")
        )
        result = await cur.fetchall()
```

### 10. 防 N+1 查询

```python
# ❌ 反例：循环内查数据库（N+1）
for item_id in item_ids:
    item = await db.fetch("SELECT * FROM items WHERE id = %s", item_id)
    results.append(item)

# ✅ 正例：批量查询（IN）
placeholders = ",".join(["%s"] * len(item_ids))
query = f"SELECT * FROM items WHERE id IN ({placeholders})"
items = await db.fetch(query, *item_ids)
items_map = {item["id"]: item for item in items}
results = [items_map[iid] for iid in item_ids if iid in items_map]
```

### 11. Repository 接口抽象

```python
# domain/ports.py
from abc import ABC, abstractmethod
from typing import List, Optional

class UserProfilePort(ABC):
    @abstractmethod
    async def get_profile(self, user_id: str) -> Optional[dict]: ...

    @abstractmethod
    async def batch_get_profiles(self, user_ids: List[str]) -> dict[str, dict]: ...

class ItemRepositoryPort(ABC):
    @abstractmethod
    async def get_items(self, item_ids: List[str]) -> List[dict]: ...

    @abstractmethod
    async def get_items_by_category(self, category: str, limit: int) -> List[dict]: ...
```

### 12. 事务边界清晰

```python
# ❌ 反例：事务范围过大，跨多个领域
async with pool.transaction() as tx:
    await tx.execute("INSERT INTO behaviors ... ")  # 行为记录
    await tx.execute("UPDATE user_stats ... ")      # 用户统计
    await tx.execute("INSERT INTO events ... ")     # 事件发布
    # 三个不同的业务操作放在一个事务里，任何一个失败都导致全部回滚

# ✅ 正例：按业务边界拆分事务
# 事务1：行为记录（必须原子）
async with pool.transaction() as tx:
    await tx.execute("INSERT INTO behaviors ... ")

# 事务2：统计更新（可异步重试，容忍失败）
try:
    await update_user_stats(user_id)
except RetryableError:
    await queue.publish("stats.update", {"user_id": user_id})  # 异步补偿

# 事务3：事件发布（最终一致即可）
await event_bus.publish(UserClickedItem(user_id, item_id))
```

---

## 四、模型推理层规范

### 13. 超时控制（必须设！）

```python
# ❌ 反例：无超时，等模型服务挂掉后无限等待
async with aiohttp.ClientSession() as session:
    async with session.post(TRITON_URL + "/predict", json=payload) as resp:
        result = await resp.json()

# ✅ 正例：connect + read 双超时
async def call_model(payload: dict, timeout: float = 1.0) -> dict:
    timeout_cfg = aiohttp.ClientTimeout(
        total=None,
        connect=0.3,       # 建连超时 300ms
        sock_read=0.7     # 读取超时 700ms
    )
    async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
        async with session.post(TRITON_URL + "/predict", json=payload) as resp:
            return await resp.json()

# ✅ 调用方三层降级
async def rank_with_fallback(payload: dict) -> List[dict]:
    try:
        return await call_model(payload, timeout=1.0)
    except asyncio.TimeoutError:
        logger.warning("模型推理超时，降级为规则排序")
        return await fallback_rule_ranking(payload["item_ids"])
    except Exception as e:
        logger.error(f"模型推理异常: {e}，降级为热门排序")
        return await fallback_hot_ranking()
```

### 14. 模型版本隔离

```python
# ✅ 灰度发布时支持多版本并行
class ModelVersionManager:
    def __init__(self):
        self._versions = {}  # {version: TritonClient}

    async def load_version(self, version: str, url: str):
        self._versions[version] = TritonClient(url)

    def get_client(self, version: str = "production"):
        if version not in self._versions:
            raise ValueError(f"未知模型版本: {version}")
        return self._versions[version]

# 路由：10% 流量走新模型
async def rank_items(item_ids: List[str], user_id: str, experiment: dict):
    target_version = "v2" if hash(user_id) % 100 < experiment.get("v2_traffic", 0) else "production"
    client = model_manager.get_client(target_version)
    return await client.predict(item_ids)
```

### 15. 推理结果校验

```python
# ✅ 模型输出必须校验，防止异常值污染推荐结果
def validate_ranking_result(items: List[dict]) -> List[dict]:
    validated = []
    for item in items:
        score = item.get("score", 0)
        if not isinstance(score, (int, float)):
            logger.error(f"模型分数类型异常: {type(score)}")
            continue
        if score < 0 or score > 100:  # 合理分数范围检查
            logger.warning(f"模型分数超范围: {score}，已截断")
            score = max(0, min(100, score))
        item["score"] = score
        if item.get("item_id") and item.get("score"):
            validated.append(item)
    return validated
```

---

## 五、缓存层规范

### 16. Key 命名规范

```python
# ✅ 格式：{业务}:{实体}:{标识}:{维度}
CACHE_KEYS = {
    "user_profile":      "rec:user:profile:{user_id}",           # 用户画像
    "recommend_result":  "rec:result:{scene}:{user_id}:{hash}",  # 推荐结果
    "item_features":     "rec:item:feat:{item_id}",             # 物品特征
    "hot_items":         "rec:hot:{scene}:{date}",              # 热门物品
    "experiment":        "rec:exp:{user_id}",                   # 实验分组
}

# ✅ 命名检查清单
# 1. 包含主要业务域（rec/feed/search）
# 2. 包含实体类型（user/item/scene）
# 3. 包含唯一标识（id或hash）
# 4. 包含时间维度（如需要）
# 5. 不含敏感信息（uid直接做key可脱敏后hash）
```

### 17. 防缓存三大经典问题

```python
# 穿透：布隆过滤器快速过滤不存在的数据
class BloomFilter:
    def __init__(self, redis_client):
        self.r = redis_client

    async def might_exist(self, item_id: str) -> bool:
        return await self.r.execute_command("BF.EXISTS", "bloom:items", item_id)

# 击穿：分布式锁保护热点key
async def get_recommend_with_lock(user_id: str, scene: str) -> List[dict]:
    cache_key = f"rec:{scene}:{user_id}"
    cached = await r.get(cache_key)
    if cached:
        return json.loads(cached)

    lock_key = f"lock:{cache_key}"
    if not await r.set(lock_key, "1", nx=True, ex=5):
        # 别人正在加载，等一下再查缓存
        await asyncio.sleep(0.1)
        return await get_recommend_with_lock(user_id, scene)

    try:
        result = await build_recommendation(user_id, scene)
        await r.setex(cache_key, 300, json.dumps(result))
        return result
    finally:
        await r.delete(lock_key)

# 雪崩：TTL随机偏移
ttl = int(base_ttl + random.uniform(-0.1 * base_ttl, 0.1 * base_ttl))
await r.setex(cache_key, ttl, json.dumps(result))
```

### 18. 缓存更新策略

```python
# ✅ 推荐结果：Cache-Aside（读多写少，最常用）
async def get_recommend(user_id: str, scene: str) -> List[dict]:
    key = f"rec:{scene}:{user_id}"
    cached = await r.get(key)
    if cached:
        return json.loads(cached)
    result = await build_recommendation(user_id, scene)
    await r.setex(key, 300, json.dumps(result))  # 5分钟缓存
    return result

# ✅ 计数：Write-Through（写操作同步更新）
async def increment_click_count(item_id: str):
    await r.incr(f"stat:click:{item_id}")
    await db.execute("UPDATE items SET click_count = click_count + 1 WHERE id = %s", item_id)

# ✅ 行为数据：Write-Behind（异步批量落库，防阻塞主流程）
async def record_behavior_async(user_id: str, item_id: str, event: str):
    # 先入队列，不阻塞推荐主流程
    await kafka_producer.send("user_behavior", {
        "user_id": user_id,
        "item_id": item_id,
        "event": event,
        "timestamp": int(time.time() * 1000)
    })
```

---

## 六、代码质量规范

### 19. 函数长度限制

```python
# 函数行数检查（建议不超过 50 行）
# 超过 50 行 → 拆！
# 超过 30 行 → 考虑拆分
# 超过 20 行 → 可以接受

# 拆分方法：
# 1. 按步骤拆：fetch → validate → transform → store
# 2. 按分支拆：if 分支逻辑提取为独立函数
# 3. 按数据拆：一个函数只处理一个数据结构
```

### 20. 参数数量限制

```python
# ❌ 反例：参数过多，调用方记不住顺序
def recommend(user_id, scene, count, offset, filters, sorts, boost, dedup, debug, callback):
    ...

# ✅ 正例：参数对象化
@dataclass
class RecommendParams:
    user_id: str
    scene: str
    count: int = 20
    offset: int = 0
    filters: FilterRule = field(default_factory=FilterRule.default)
    sorts: List[SortRule] = field(default_factory=list)
    boost: Optional[BoostRule] = None
    dedup: DedupRule = field(default_factory=DedupRule.default)
    debug: bool = False

def recommend(params: RecommendParams) -> List[RecommendItem]:
    ...
```

### 21. 类型注解必须加

```python
# ✅ 公共函数必须加类型注解（IDE 自动补全 + 静态检查）
from typing import List, Optional, AsyncIterator

async def multi_recall(
    context: RecommendContext,
    strategies: List[BaseRecallStrategy],
    max_candidates: int = 200
) -> AsyncIterator[RecommendItem]:
    """多路并行召回，yield 逐个返回"""
    ...

def sort_by_score(items: List[dict], top_k: int = 50) -> List[dict]:
    """排序并截取 top_k"""
    ...
```

### 22. 魔法数字消灭

```python
# ❌ 反例：魔法数字散布代码各处
if count > 1000:
    page_size = 50
await asyncio.sleep(3)
if score > 0.8 and retry < 5:

# ✅ 正例：配置类集中管理
@dataclass
class RecConfig:
    # 召回配置
    max_recall_candidates: int = 200
    min_recall_per_strategy: int = 10
    # 排序配置
    ranking_timeout_ms: int = 1000
    max_ranking_items: int = 500
    # 缓存配置
    result_cache_ttl_sec: int = 300
    profile_cache_ttl_sec: int = 3600
    # 降级配置
    max_retry: int = 3
    retry_delay_sec: float = 0.5
    # 限流配置
    rate_limit_per_user: int = 100
    rate_limit_window_sec: int = 60

cfg = RecConfig()
```

---

## 七、测试规范

### 23. 核心业务必须有单元测试

```python
# ✅ 推荐系统核心逻辑（无外部依赖）必须测
import pytest

class TestRecommendationEngine:
    def test_multi_recall_at_least_one_strategy_succeeds(self):
        """至少一路召回成功，不全挂"""
        engine = RecommendationEngine([
            FailingRecallStrategy(),   # 故意失败
            MockRecallStrategy([item(1), item(2)]),
        ])
        context = RecommendContext(user_id="test", scene="home")
        results = engine.recommend(context)
        assert len(results) >= 1

    def test_diversity_rerank(self):
        """多样性重排：相同类目不超过50%"""
        items = [item(i, category="A") for i in range(10)]
        reranked = DiversityReranker(rerank_n=10).rerank(items)
        cat_a_count = sum(1 for i in reranked if i.category == "A")
        assert cat_a_count <= 5

    def test_empty_recall_fallback(self):
        """召回为空时降级为热门"""
        engine = RecommendationEngine([])
        result = engine.recommend(RecommendContext(user_id="x", scene="home"))
        assert result[0].source == "hot_fallback"
```

### 24. Repository 必须有集成测试

```python
# ✅ SQLite 内存测试（真实 SQL 语句，不依赖 MySQL）
import pytest, pytest_asyncio, sqlite3

@pytest_asyncio.fixture
async def repo():
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_sql)  # 初始化表结构
    yield UserProfileSQLiteRepo(conn)
    conn.close()

@pytest.mark.asyncio
async def test_batch_get_profiles(repo):
    profiles = await repo.batch_get_profiles(["u1", "u2", "u3"])
    assert len(profiles) == 3
    assert all(p.get("user_id") for p in profiles.values())
```

### 25. AB 实验测试隔离

```python
# ✅ 每个实验分支独立测试，不互相影响
@pytest.fixture
def experiment_context():
    return ExperimentContext(
        user_id="test_user",
        traffic分配={
            "strategy_v2": 0.1,  # 10% 流量
            "new_recall": 0.2,   # 20% 流量
        }
    )

def test_experiment_isolation():
    """同层互斥：一个用户只能命中一个实验"""
    ctx = experiment_context()
    exp_allocator = ExperimentAllocator(layers=["recall", "ranking"])
    assignments = exp_allocator.assign(ctx)
    # 同一层实验不重复
    assert len(set(exp.layer for exp in assignments)) == len(assignments)
```

---

## 八、部署与运维规范

### 26. 健康检查端点

```python
# ✅ K8s liveness + readiness 探针必须分开
@app.get("/health/live")
async def liveness():
    return {"status": "ok"}  # 只检查进程存活，不查下游

@app.get("/health/ready")
async def readiness():
    try:
        # 检查所有下游依赖
        await redis.ping()
        await db.fetch("SELECT 1")
        await model_client.health()
        return {"status": "ready", "components": {"redis": "ok", "db": "ok", "model": "ok"}}
    except Exception as e:
        raise HTTPException(503, f"not ready: {e}")
```

### 27. 优雅关闭

```python
# ✅ SIGTERM 时先停收流量，等现有请求处理完
import signal, asyncio

shutdown_event = asyncio.Event()

async def lifespan(app):
    # 启动时
    await init_dependencies()
    yield
    # 关闭时：先标记停止接请求
    logger.info("收到 SIGTERM，开始优雅关闭")
    await pool.close()      # 等待连接池清空
    await kafka_producer.close()
    logger.info("优雅关闭完成")

# K8s 配置：
# lifecycle:
#   preStop:
#     exec:
#       command: ["sleep", "5"]  # 等待流量排空
```

### 28. 关键指标暴露

```python
# ✅ Prometheus 四大核心指标
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter("rec_request_total", "总请求数",
    ["scene", "status"])  # status=success/error/timeout

REQUEST_LATENCY = Histogram("rec_request_latency_ms", "请求延迟ms",
    ["stage"], buckets=[5, 10, 25, 50, 100, 200, 500, 1000])

CACHE_HIT = Gauge("rec_cache_hit_ratio", "缓存命中率",
    ["cache_type"])  # cache_type=result/profile/feature

MODEL_INFER_LATENCY = Histogram("rec_model_infer_ms", "模型推理延迟ms",
    ["model_version"], buckets=[50, 100, 200, 500, 1000, 2000])

# 埋点示例
def recommend_view():
    start = time_ms()
    try:
        result = await engine.recommend(req)
        REQUEST_COUNT.labels(scene=req.scene, status="success").inc()
    except Exception:
        REQUEST_COUNT.labels(scene=req.scene, status="error").inc()
        raise
    finally:
        REQUEST_LATENCY.labels(stage="total").observe(time_ms() - start)
```

---

## 九、安全规范

### 29. 最小权限原则

```python
# ✅ 数据库用户权限最小化
# 推荐服务只给 SELECT/INSERT，不给 DROP/ALTER
CREATE USER 'rec_service'@'%' IDENTIFIED BY '...';
GRANT SELECT, INSERT ON rec_db.behaviors TO 'rec_service'@'%';
GRANT SELECT ON rec_db.user_profiles TO 'rec_service'@'%';
GRANT SELECT ON rec_db.items TO 'rec_service'@'%';
# 不给 DELETE/UPDATE 权限，防止误操作

# ✅ Redis 只读账号（监控）+ 读写账号（业务）分离
```

### 30. 密钥管理

```python
# ❌ 反例：密钥写死在代码里
API_KEY = "sk-xxxx-xxxx"

# ✅ 正例：环境变量 + Secret Manager
import os
from functools import lru_cache

@lru_cache
def get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        # 从 K8s Secret / Vault 读取
        key = os.environ.get("SECRET_API_KEY_PATH", "/secrets/api_key")
        with open(key) as f:
            return f.read().strip()
    return key
```

---

## 十、代码自检命令（上线前必跑）

```bash
# 1. 代码质量扫描
flake8 app/ --max-line-length=120 --ignore=E501,W503
mypy app/  # 严格模式
bandit -r app/  # 安全扫描

# 2. 复杂度检查
lizard app/ -c function_max_complexity=15  # CCN > 15 标红

# 3. 依赖审计
pip-audit || true

# 4. 秘密扫描（防止密钥泄漏）
git diff --staged | grep -i "sk-\|api_key\|password" && echo "密钥检测！提交被拒绝"

# 5. 测试覆盖率（核心模块 > 80%）
pytest --cov=app/domain --cov-report=term-missing --cov-fail-under=80

# 6. 数据库迁移检查（不跑 migration 只做语法检查）
alembic check

# 7. K8s YAML 语法验证
kubectl apply --dry-run=client -f k8s/deployment.yaml
kubectl apply --dry-run=client -f k8s/service.yaml
```

---

## 常见误区速查表

| 误区 | 正确做法 |
|------|---------|
| 先上线后补测试 | 测试覆盖率 < 60% 不允许合入 main |
| try-pass 吞掉异常 | 至少 log.warning 记录 |
| 模型调用无超时 | connect + read 双超时，熔断降级 |
| 缓存只管写入 | 缓存失效（TTL/主动删除）同样重要 |
| 日志打框架默认格式 | 结构化 JSON，request_id 贯穿全链路 |
| SQL 拼接用户输入 | 参数化查询，永远不拼接 |
| 多个服务用同一 DB 账号 | 按服务分配独立账号，最小权限 |
| 不做缓存预热 | 热点数据提前加载，避免冷启动雪崩 |
| 接口无版本管理 | API 加 v1/v2 前缀，保留老版本兼容 |
| 配置文件写代码里 | 环境变量/配置中心，代码与配置分离 |

---

*本文档配合 [代码质量评估清单](./代码质量评估清单.md) 使用效果更佳——先评估现状，再对照本文 Checklist 逐项修复。*
