# Redis 缓存与性能优化实战

> 推荐系统的命脉：80% 的请求依赖 20% 的热点数据，不缓存必死。

---

## 一、为什么推荐系统必须缓存？

### 推荐系统的性能瓶颈

一次推荐请求，背后可能涉及：

| 操作 | 平均耗时 | QPS 要求 | 不缓存的问题 |
|------|---------|---------|-------------|
| 用户特征查询 | 5-50ms | 10万/s | 数据库被打爆 |
| Item 特征查询 | 5-20ms | 100万/s | 无法承受 |
| 模型推理 | 20-200ms | 1万/s | 延迟太高 |
| 多路召回调取 | 10-100ms | 5万/s | RT 超标 |

**没有缓存的现实**：单机 MySQL 扛不住 1000 QPS 的用户特征查询，加机器也解决不了 IO 问题。

### 缓存带来的收益

```
不缓存：推荐 RT（99线）  →  500ms+
Redis 缓存：推荐 RT（99线）  →  20ms
```

**收益是 25 倍的延迟改善**，而且节省了大量计算资源。

---

## 二、Redis 在推荐系统中的典型应用场景

```
┌─────────────────────────────────────────────────────────────┐
│                    Redis 缓存场景全景                         │
├─────────────────────────────────────────────────────────────┤
│  1. 用户特征缓存        │  用户向量、偏好标签、人口属性         │
│  2. Item 特征缓存       │  商品向量、类别、热度分数             │
│  3. 推荐结果缓存        │  首页推荐、相似推荐、猜你喜欢           │
│  4. 计数缓存            │  点击数、曝光数、收藏数                │
│  5. 分布式锁            │  库存扣减、秒杀、防重复处理             │
│  6. 排行榜              │  热销榜、热度榜、新品榜                 │
│  7. Session 管理        │  用户登录态、Token                    │
│  8. 实时数据管道         │  Kafka 消费位点、实时统计窗口          │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、三大缓存模式详解

### 模式 1：Cache-Aside（最常用）

**读多写少场景**，业务代码自己负责读写缓存。

```
读流程：
  应用 → 查询 Redis → 命中？ → 直接返回
                  ↓ 未命中
          查询 MySQL → 返回结果
          同时写入 Redis（设置 TTL）

写流程：
  更新 MySQL → 删除 Redis 中的旧缓存（下一次读取时重新填充）
```

**推荐系统适用场景**：
- 用户特征（读多写少，用户不频繁更新画像）
- Item 特征（几乎不变，只有审核状态会变）
- 推荐结果（用户不点就不变）

```python
# Python 实现：Cache-Aside 模式
import json
import redis
from typing import Optional

class UserFeatureCache:
    """用户特征缓存 — Cache-Aside 模式"""
    
    def __init__(self, redis_client: redis.Redis, mysql_repo, ttl: int = 3600):
        self.redis = redis_client
        self.mysql_repo = mysql_repo
        self.ttl = ttl
    
    def get_user_features(self, user_id: str) -> Optional[dict]:
        """读取用户特征：先查缓存，未命中查库并回填"""
        cache_key = f"user:features:{user_id}"
        
        # Step 1: 查 Redis
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Step 2: 未命中，查 MySQL
        features = self.mysql_repo.find_user_features(user_id)
        if features:
            # Step 3: 回填缓存
            self.redis.setex(
                cache_key,
                self.ttl,
                json.dumps(features)
            )
        return features
    
    def invalidate_user(self, user_id: str) -> None:
        """用户特征变更时，主动删除缓存"""
        cache_key = f"user:features:{user_id}"
        self.redis.delete(cache_key)
```

### 模式 2：Write-Through（写穿透）

**写操作同时更新缓存和数据库**，保证强一致性。

```
写流程：
  更新请求 → 写入 MySQL → 同步写入 Redis → 返回
```

**推荐系统适用场景**：
- 点赞/收藏计数（需要精确，用户每次操作都要更新）
- 用户画像的实时标签（写和读都频繁）
- 订单状态（不允许不一致）

```python
# Python 实现：Write-Through 模式
class LikeCountService:
    """点赞计数 — Write-Through 模式"""
    
    def __init__(self, redis_client: redis.Redis, mysql_repo):
        self.redis = redis_client
        self.mysql_repo = mysql_repo
    
    def like_item(self, user_id: str, item_id: str) -> int:
        """点赞：同时写 MySQL + Redis，保证一致性"""
        cache_key = f"item:likes:{item_id}"
        
        # Step 1: 更新 MySQL（主数据库）
        new_count = self.mysql_repo.increment_like(item_id)
        
        # Step 2: 同步更新 Redis（Write-Through）
        self.redis.set(cache_key, new_count)
        
        return new_count
    
    def get_like_count(self, item_id: str) -> int:
        """读取点赞数"""
        cache_key = f"item:likes:{item_id}"
        count = self.redis.get(cache_key)
        if count is not None:
            return int(count)
        
        # 缓存未命中：从数据库加载
        count = self.mysql_repo.get_like_count(item_id)
        self.redis.set(cache_key, count)
        return count
```

### 模式 3：Write-Behind（写回）

**写操作只写缓存，异步批量写回数据库**。

```
写流程：
  更新请求 → 写入 Redis → 返回成功
  （后台进程定时批量写回 MySQL）
```

**推荐系统适用场景**：
- 用户行为计数（点击、曝光、播放时长）
- 实时特征更新（用户每点击一个商品，特征向量要更新）
- AB 实验打点数据收集

```python
# Python 实现：Write-Behind 模式
import threading
import time
from collections import defaultdict
from typing import Dict

class BehaviorCounter:
    """用户行为计数 — Write-Behind 模式"""
    
    def __init__(self, redis_client: redis.Redis, mysql_repo, flush_interval: int = 60):
        self.redis = redis_client
        self.mysql_repo = mysql_repo
        self.flush_interval = flush_interval
        self._buffer: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
        
        # 启动后台 flush 线程
        self._stop = False
        self._thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._thread.start()
    
    def increment(self, item_id: str, event_type: str, delta: int = 1) -> None:
        """记录行为：只写 Redis 内存 buffer"""
        cache_key = f"counter:{event_type}:{item_id}"
        self.redis.incrby(cache_key, delta)
    
    def _flush_loop(self) -> None:
        """后台线程：定时将 Redis 数据批量写回 MySQL"""
        while not self._stop:
            time.sleep(self.flush_interval)
            self._flush_to_mysql()
    
    def _flush_to_mysql(self) -> None:
        """批量写回 MySQL（可以 scan Redis keys 实现）"""
        # 实际实现：scan keys 收集待写回数据，批量 INSERT ON DUPLICATE KEY UPDATE
        pass
    
    def stop(self) -> None:
        self._stop = True
        self._thread.join()
```

### 三种模式对比

| 维度 | Cache-Aside | Write-Through | Write-Behind |
|------|------------|--------------|-------------|
| 一致性 | 最终一致 | 强一致 | 最终一致 |
| 写入延迟 | 低 | 中 | 极低 |
| 实现复杂度 | 低 | 中 | 高 |
| 数据丢失风险 | 无（异步写） | 无 | 有（未 flush 就宕机） |
| 推荐系统适用场景 | 推荐结果、Item特征 | 点赞计数、订单状态 | 行为打点、实时特征 |

---

## 四、推荐系统缓存实战

### 场景 1：首页推荐结果缓存

**特点**：用户量大，推荐计算贵，首页请求 QPS 极高。

```
缓存策略：Cache-Aside + 多级 TTL
├── 用户维度缓存：key = f"rec:home:{user_id}"，TTL = 30分钟
└── 兜底全局缓存：key = "rec:home:popular"，TTL = 5分钟（新用户用这个）
```

```python
# 首页推荐缓存实现
class HomeRecommendationCache:
    
    HOME_TTL = 1800          # 30 分钟
    GLOBAL_TTL = 300          # 5 分钟
    
    def get_home_recommendations(self, user_id: str, rec_service) -> list:
        user_cache_key = f"rec:home:{user_id}"
        
        # 1. 尝试用户个性化缓存
        cached = self.redis.get(user_cache_key)
        if cached:
            return json.loads(cached)
        
        # 2. 降级：返回全局热门推荐
        global_cache_key = "rec:home:popular"
        cached_global = self.redis.get(global_cache_key)
        if cached_global:
            return json.loads(cached_global)
        
        # 3. 兜底：实时计算（此时请求会慢，但不会挂）
        recommendations = rec_service.generate_home_rec(user_id)
        
        # 4. 回填用户缓存
        self.redis.setex(user_cache_key, self.HOME_TTL, json.dumps(recommendations))
        
        # 5. 同时更新全局热门缓存（基于这次计算结果）
        # 实际生产：另一个异步任务维护全局缓存，这里简化处理
        return recommendations
    
    def refresh_user_cache(self, user_id: str, recommendations: list) -> None:
        """用户触发刷新（如点了赞）"""
        self.redis.setex(f"rec:home:{user_id}", self.HOME_TTL, json.dumps(recommendations))
```

### 场景 2：多路召回调用的特征缓存

**特点**：一次推荐请求要查 N 路召回的 Item 特征，每路可能查几百个 Item。

```
优化前（循环查库）：
  for item_id in item_ids:
      item_feature = mysql.query(item_id)  # 1000次 DB 查询 ❌

优化后（Pipeline 批量查）：
  features = mget(item_id_1, item_id_2, ..., item_id_1000)  # 1次 Redis 查询 ✅
```

```python
# 多路召回特征批量查询
class ItemFeatureCache:
    
    def batch_get_features(self, item_ids: list[str]) -> dict[str, dict]:
        """批量获取 Item 特征：使用 Redis Pipeline"""
        if not item_ids:
            return {}
        
        cache_keys = [f"item:features:{iid}" for iid in item_ids]
        
        # Redis Pipeline：一次网络往返，获取所有特征
        pipe = self.redis.pipeline()
        for key in cache_keys:
            pipe.get(key)
        cached_values = pipe.execute()
        
        result = {}
        hit_ids = []
        miss_ids = []
        
        for iid, val in zip(item_ids, cached_values):
            if val:
                result[iid] = json.loads(val)
                hit_ids.append(iid)
            else:
                miss_ids.append(iid)
        
        # 未命中：从 MySQL 批量查询
        if miss_ids:
            db_features = self.mysql_repo.batch_find_item_features(miss_ids)
            # 回填 Redis
            pipe = self.redis.pipeline()
            for iid, feat in db_features.items():
                pipe.setex(f"item:features:{iid}", self.ITEM_TTL, json.dumps(feat))
            pipe.execute()
            result.update(db_features)
        
        return result
```

### 场景 3：用户 Embedding 向量缓存

**特点**：向量维度大（768-1024维），存储占用高，但查询性能要求极高。

```python
# 用户向量缓存 — 用 Redis String 存储序列化向量
import numpy as np

class UserEmbeddingCache:
    VECTOR_TTL = 3600  # 1小时
    
    def get_user_vector(self, user_id: str) -> Optional[np.ndarray]:
        cache_key = f"user:embedding:{user_id}"
        cached = self.redis.get(cache_key)
        if cached:
            # 从 bytes 反序列化
            return np.frombuffer(cached, dtype=np.float32)
        return None
    
    def set_user_vector(self, user_id: str, vector: np.ndarray) -> None:
        cache_key = f"user:embedding:{user_id}"
        # 压缩存储：float32 → bytes
        self.redis.setex(cache_key, self.VECTOR_TTL, vector.astype(np.float32).tobytes())
    
    def batch_get_user_vectors(self, user_ids: list[str]) -> dict[str, np.ndarray]:
        """批量获取用户向量（用于 i2i 召回）"""
        cache_keys = [f"user:embedding:{uid}" for uid in user_ids]
        values = self.redis.mget(cache_keys)
        return {
            uid: np.frombuffer(v, dtype=np.float32)
            for uid, v in zip(user_ids, values) if v
        }
```

---

## 五、TTL 设计策略

TTL（Time-To-Live）是缓存的核心参数，设计不好会引发缓存击穿/雪崩。

### 推荐系统的 TTL 参考

| 缓存类型 | 推荐 TTL | 说明 |
|---------|---------|------|
| 首页推荐结果 | 30 分钟 | 用户行为变化不快 |
| Item 特征 | 2-24 小时 | 审核状态变化时主动删除 |
| 用户特征 | 1-2 小时 | 画像更新时主动 invalidate |
| 热门推荐列表 | 5-30 分钟 | 随热度实时变化 |
| 用户 Embedding | 1-4 小时 | 定期从模型更新 |
| 计数（点赞/评论） | 不设 TTL | 用 Write-Through 更新 |

### 防止缓存雪崩：TTL + 随机偏移

```python
# ❌ 问题：大量 key 同时过期 → 大量请求打到数据库（雪崩）
self.redis.setex("rec:home:hot", 1800, data)  # 整点到期的 key 会一起失效

# ✅ 解决：为 TTL 加随机偏移，分散过期时间
import random
base_ttl = 1800
actual_ttl = base_ttl + random.randint(0, 300)  # 1800-2100秒
self.redis.setex("rec:home:hot", actual_ttl, data)
```

---

## 六、缓存三大经典问题

### 问题 1：缓存穿透（Cache Penetration）

**场景**：恶意请求查询数据库中根本不存在的 Item 或 User，所有请求都穿透到 MySQL。

```
请求 → Redis（未命中）→ MySQL（未命中）→ 返回空
问题：大量不存在的数据请求 → MySQL 被打爆
```

**解决方案 A：Bloom Filter**

```python
import redis
from bitarray import bitarray
import hashlib

class BloomFilter:
    """布隆过滤器：快速判断 key 是否可能存在"""
    
    def __init__(self, redis_client: redis.Redis, key: str, size: int = 1000000):
        self.redis = redis_client
        self.key = key
        self.size = size
    
    def _get_bit_positions(self, item_id: str) -> list[int]:
        """用多个 hash 函数计算 bit 位置"""
        positions = []
        for seed in range(6):
            h = int(hashlib.md5(f"{seed}:{item_id}".encode()).hexdigest(), 16)
            positions.append(h % self.size)
        return positions
    
    def add(self, item_id: str) -> None:
        positions = self._get_bit_positions(item_id)
        for pos in positions:
            self.redis.setbit(self.key, pos, 1)
    
    def might_exist(self, item_id: str) -> bool:
        """返回 False 必定不存在，返回 True 可能是误判（可接受）"""
        positions = self._get_bit_positions(item_id)
        return all(self.redis.getbit(self.key, pos) for pos in positions)


# 使用：查询前先过 Bloom Filter
def get_item_features(self, item_id: str) -> Optional[dict]:
    if not self.bloom_filter.might_exist(item_id):
        return None  # 必定不存在，直接返回
    return self.get_item_features_from_db(item_id)
```

**解决方案 B：空值缓存（适合数据确定不会有的场景）**

```python
# 对确定不存在的数据，缓存一个空值（TTL 要短）
cache_key = f"item:features:{item_id}"
if not self.redis.exists(cache_key):
    exists = self.mysql_repo.item_exists(item_id)
    if not exists:
        self.redis.setex(cache_key, 60, "NULL")  # 短 TTL 空值缓存
    else:
        self._load_and_cache(item_id)
```

### 问题 2：缓存击穿（Cache Breakdown）

**场景**：热点 key 突然过期 → 大量请求同时查 DB（尤其是缓存预热不足时）。

```
热点 key 过期瞬间
    ↓
10000 个并发请求
    ↓
同时查 MySQL → MySQL 被打爆
```

**解决方案：分布式锁（单飞加锁）**

```python
import uuid
import redis

class DistributedLock:
    """基于 Redis 的分布式锁"""
    
    def __init__(self, redis_client: redis.Redis, lock_key: str, ttl: int = 5):
        self.redis = redis_client
        self.lock_key = lock_key
        self.ttl = ttl
        self.lock_value = str(uuid.uuid4())
    
    def acquire(self) -> bool:
        """尝试获取锁（SET NX）"""
        return bool(self.redis.set(
            self.lock_key, self.lock_value,
            nx=True, ex=self.ttl
        ))
    
    def release(self) -> bool:
        """释放锁（Lua 脚本保证原子性）"""
        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        return bool(self.redis.eval(lua, 1, self.lock_key, self.lock_value))


def get_with_lock(self, user_id: str) -> dict:
    """带分布式锁的缓存查询（防止击穿）"""
    cache_key = f"user:features:{user_id}"
    
    # Step 1: 直接查缓存
    cached = self.redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Step 2: 未命中，尝试加锁
    lock = DistributedLock(self.redis, f"lock:{cache_key}", ttl=5)
    
    if lock.acquire():
        try:
            # 拿到锁的请求负责查库+回填
            features = self.mysql_repo.find_user_features(user_id)
            if features:
                self.redis.setex(cache_key, self.ttl, json.dumps(features))
            return features
        finally:
            lock.release()
    else:
        # 没拿到锁：等待其他请求回填后，再查缓存
        import time
        for _ in range(10):
            time.sleep(0.1)
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        # 兜底：直接查库（极少量请求会到这）
        return self.mysql_repo.find_user_features(user_id)
```

### 问题 3：缓存雪崩（Cache Avalanche）

**场景**：大量 key 同时过期，或 Redis 突然宕机 → 所有请求直接打 MySQL。

**解决方案 1：多级缓存**

```python
# L1（本地缓存）+ L2（Redis）+ L3（MySQL）
# L1 用 Python dict/Caffeine，本地极快
# L2 用 Redis，跨进程共享
# 正常情况：L1 命中，0.01ms
# L1 未命中：查 L2
# L2 未命中：查 L3 + 回填 L2 + 回填 L1

from functools import lru_cache
import threading

class TwoLevelCache:
    
    def __init__(self, redis_client: redis.Redis, mysql_repo, local_ttl=10, redis_ttl=300):
        self.redis = redis_client
        self.mysql_repo = mysql_repo
        self.local_ttl = local_ttl
        self.redis_ttl = redis_ttl
        self._local_cache = {}
        self._local_timestamps = {}
        self._lock = threading.Lock()
    
    def get(self, user_id: str) -> Optional[dict]:
        # L1: 本地缓存（极快，0.01ms）
        if user_id in self._local_cache:
            if time.time() - self._local_timestamps[user_id] < self.local_ttl:
                return self._local_cache[user_id]
        
        # L2: Redis
        cache_key = f"user:features:{user_id}"
        cached = self.redis.get(cache_key)
        if cached:
            result = json.loads(cached)
            # 回填 L1
            with self._lock:
                self._local_cache[user_id] = result
                self._local_timestamps[user_id] = time.time()
            return result
        
        # L3: MySQL
        result = self.mysql_repo.find_user_features(user_id)
        if result:
            self.redis.setex(cache_key, self.redis_ttl, json.dumps(result))
            with self._lock:
                self._local_cache[user_id] = result
                self._local_timestamps[user_id] = time.time()
        return result
```

**解决方案 2：Redis 高可用 + 持久化**

```
推荐生产配置：
- Redis Cluster（3主3从，自动故障转移）
- RDB + AOF 混合持久化
- 定时备份 + 跨机房容灾
```

---

## 七、Redis 在推荐系统的完整架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                       推荐系统缓存架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   客户端请求 ──→ API Gateway ──→ 推荐服务                       │
│                                    │                            │
│              ┌─────────────────────┼─────────────────────┐     │
│              ↓                     ↓                     ↓     │
│         L1 本地缓存           L2 Redis 缓存           MySQL     │
│     (进程内 dict, 10ms)    (分布式, 1-5ms)        (主库, 50ms) │
│                                                                 │
│   推荐服务内部缓存分层：                                           │
│   ┌─────────────────────────────────────────────────┐          │
│   │ L1: 本地缓存（用户向量 top-K, 策略配置）          │  TTL=10s │
│   │ L2: Redis（用户/Item 特征, 推荐结果）           │  TTL=5min│
│   │ L3: MySQL/ClickHouse（完整特征）                 │          │
│   └─────────────────────────────────────────────────┘          │
│                                                                 │
│   异步更新路径：                                                  │
│   Kafka 事件 ──→ 画像更新服务 ──→ Redis SETEX + MQ广播          │
│                      ↓                                           │
│                  热点缓存预热（点击量 top-K）                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 八、生产环境注意事项

### 监控指标

| 指标 | 告警阈值 | 说明 |
|------|---------|------|
| 缓存命中率 | < 80% 告警 | 说明缓存策略有问题 |
| Redis CPU | > 70% 告警 | 说明热点 key 过多 |
| Redis 内存 | > 80% 告警 | 接近 OOM 风险 |
| 缓存未命中 RT | > 100ms 告警 | 查库太慢 |
| 连接池耗尽 | > 90% 告警 | 连接数不足 |

### key 命名规范

```
推荐系统 key 命名规范：
{实体类型}:{特征类型}:{具体ID}

user:features:{user_id}          # 用户特征
user:embedding:{user_id}         # 用户向量
item:features:{item_id}          # Item 特征
item:embedding:{item_id}          # Item 向量
rec:home:{user_id}               # 首页推荐结果
rec:similar:{item_id}            # 相似推荐
counter:click:{item_id}          # 点击计数
lock:user:features:{user_id}     # 分布式锁
bf:item:exists                   # Item 存在性布隆过滤器
```

### 序列化选择

```python
# 推荐序列化方式对比
# 1. JSON（可读，跨语言，但慢）：适合需要调试的特征
# 2. msgpack（紧凑，快3-5倍）：适合向量、高频数据
# 3. pickle（Python 专用，有安全风险）：不推荐用于生产
# 4. Protobuf（最紧凑，跨语言）：适合推荐系统特征

import msgpack

# 推荐：用 msgpack 替代 JSON
features = {"age": 25, "gender": "M", "tags": ["科技", "数码"]}
packed = msgpack.packb(features)
unpacked = msgpack.unpackb(packed, raw=False)

print(f"JSON bytes: {len(json.dumps(features).encode())}")        # 50 bytes
print(f"msgpack bytes: {len(packed)}")                             # 35 bytes
```

---

## 九、常见误区

### ❌ 误区 1：缓存命中率越高越好
**真相**：命中率不是目标，满足业务需求的命中率才是目标。有些场景（如搜索）天然命中率低，重点是保证未命中时的性能。

### ❌ 误区 2：所有数据都要缓存
**真相**：只缓存热点数据（80/20 法则）。非热点数据直接查库，加缓存反而浪费内存、增加复杂度。

### ❌ 误区 3：缓存不需要过期
**真相**：缓存的数据最终会过时。设计 TTL 时要权衡：太长数据陈旧，太短命中率低。热点数据 TTL 短，冷数据 TTL 长。

### ❌ 误区 4：Redis 宕机时系统仍能工作
**真相**：没有兜底降级策略的 Redis 高可用是伪高可用。必须设计降级路径：Redis 挂了 → 查 MySQL（慢，但能用）。

### ❌ 误区 5：Pipeline 就是万能优化
**真相**：Pipeline 适合批量读，不适合大 key（单 key > 1MB 会造成 Redis 阻塞）。

---

## 十、适用场景速查表

| 场景 | 推荐模式 | TTL | 序列化 |
|------|---------|-----|--------|
| 首页推荐结果 | Cache-Aside | 30min | JSON/msgpack |
| 用户特征 | Cache-Aside + Write-Through | 1-2h | JSON |
| Item 特征 | Cache-Aside | 2-24h | JSON/msgpack |
| 用户/Item 向量 | Cache-Aside | 1-4h | bytes（numpy） |
| 点赞/评论计数 | Write-Through | 无TTL | String |
| 行为打点计数 | Write-Behind | 无TTL | String |
| 分布式锁 | — | 5-10s | — |
| 排行榜 | Redis Sorted Set | 实时更新 | — |

---

## 相关知识

- [CQRS模式实战](CQRS模式实战.md)：缓存是 CQRS 读写分离的核心基础设施
- [事件驱动架构与Kafka实战](事件驱动架构与Kafka实战.md)：Kafka 消费结果写 Redis 的完整链路
- [微服务架构实战](微服务架构实战.md)：推荐服务间共享 Redis 缓存的设计
- [架构师思维修炼](架构师思维修炼.md)：容量规划中如何计算 Redis 集群规模
