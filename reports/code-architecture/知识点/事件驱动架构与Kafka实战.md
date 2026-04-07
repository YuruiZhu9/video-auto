# 事件驱动架构与 Kafka 实战
> 推荐系统的实时血液 · 从同步调用到异步解耦

---

## 什么是事件驱动架构？

### 传统同步调用 vs 事件驱动

**同步调用（耦合）：**
```
用户点击商品
    ↓
推荐服务（同步等待所有下游返回）
    ↓
更新用户画像（同步）
    ↓
更新物品评分（同步）
    ↓
发送消息通知（同步）
    ↓
推荐服务才能继续 → 延迟高
```
所有操作串行，任意一个慢 → 整体慢。

**事件驱动（解耦）：**
```
用户点击商品
    ↓
发布"点击事件"到消息队列 → 立即返回（毫秒级）
    ↓
推荐服务继续处理（不等下游）

← 消费者异步并行处理：
    • 用户画像服务 监听 → 更新用户特征
    • 物品评分服务 监听 → 调整物品权重
    • 通知服务     监听 → 发送推送消息
```

**核心区别：**

| 维度 | 同步调用 | 事件驱动 |
|------|---------|---------|
| 耦合度 | 高（调用方知道下游是谁） | 低（发布者不知道谁在听） |
| 响应时间 | 累加所有下游耗时 | 仅自身处理时间 |
| 扩展性 | 难（加消费者要改调用方） | 易（加消费者不改动代码） |
| 可靠性 | 失败即失败 | 消息持久化，可重试 |
| 适用场景 | 需要同步返回结果 | 允许延迟、可并行处理 |

---

## 核心概念

### 事件驱动三要素

| 概念 | 说明 | 推荐系统例子 |
|------|------|-------------|
| **Event（事件）** | "发生了什么"，不可变的事实 | `UserClickedItem`、`ItemPurchased`、`UserRatedItem` |
| **Producer（生产者）** | 发布事件的组件 | API 服务、客户端 SDK |
| **Consumer（消费者）** | 订阅并处理事件的组件 | 画像更新服务、推荐重排服务 |

### 事件结构设计

```python
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import uuid

@dataclass
class RecommenderEvent:
    """推荐系统通用事件结构"""
    event_id: str          # 全局唯一 ID（幂等性保证）
    event_type: str        # 事件类型
    user_id: str           # 触发用户
    item_id: str | None    # 关联物品（可选）
    timestamp: str         # ISO 时间戳
    context: dict          # 上下文信息

    @classmethod
    def click(cls, user_id: str, item_id: str, extra: dict = None):
        return cls(
            event_id=str(uuid.uuid4()),
            event_type="user.clicked_item",
            user_id=user_id,
            item_id=item_id,
            timestamp=datetime.now().isoformat(),
            context=extra or {}
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, raw: str) -> "RecommenderEvent":
        return cls(**json.loads(raw))
```

---

## Kafka 快速入门

### 核心概念

```
Kafka Cluster
    └── Topic: user-events（主题，分区存储）
        ├── Partition 0: [event1, event2, event3, ...]
        ├── Partition 1: [event4, event5, ...]
        └── Partition 2: [event6, ...]
            ↑
    Consumer Group A（画像服务）→ 消费所有分区
    Consumer Group B（推荐服务）→ 消费所有分区
```

| 概念 | 说明 |
|------|------|
| **Topic** | 事件分类（类似数据库表） |
| **Partition** | 分区（并行消费 + 顺序保证） |
| **Consumer Group** | 消费者组（组内竞争，组间广播） |
| **Offset** | 消费进度（可回溯） |
| **Retention** | 消息保留时间（默认 7 天） |

### Producer 生产者（Python）

```python
from kafka import KafkaProducer
from recommender_events import RecommenderEvent

class UserActionProducer:
    """用户行为事件生产者"""

    def __init__(self, bootstrap_servers: list[str]):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: v.to_json().encode("utf-8"),
            # 关键配置
            acks="all",          # 等待所有副本确认（可靠性最高）
            retries=3,           # 重试 3 次
            retry_backoff_ms=100,
        )
        self.topic = "user-events"

    def emit_click(self, user_id: str, item_id: str, **kwargs):
        """发布用户点击事件"""
        event = RecommenderEvent.click(user_id, item_id, extra=kwargs)
        # 异步发送，不阻塞主线程
        future = self.producer.send(self.topic, value=event)
        # 可选：附加回调处理发送结果
        future.add_callback(lambda r: print(f"✅ 已发送至 {r.topic}:{r.partition}"))
        future.add_errback(lambda e: print(f"❌ 发送失败: {e}"))
        return event.event_id  # 立即返回，不等待

    def flush(self):
        self.producer.flush()
```

### Consumer 消费者（Python）

```python
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
import json

class ProfileUpdateConsumer:
    """用户画像更新消费者"""

    def __init__(self, bootstrap_servers: list[str], group_id: str):
        self.consumer = KafkaConsumer(
            "user-events",           # 订阅的主题
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,       # 消费者组（决定消费模式）
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",  # 从头消费
            enable_auto_commit=False,       # 手动提交 offset（可靠性）
            max_poll_records=100,           # 每批最多 100 条
        )

    def start_consuming(self):
        """主消费循环"""
        try:
            for message in self.consumer:
                event = message.value
                print(f"[{message.partition}:{message.offset}] {event['event_type']}")

                if event["event_type"] == "user.clicked_item":
                    self._update_profile(event)
                elif event["event_type"] == "user.purchased_item":
                    self._update_profile(event)

                # 手动提交 offset（处理完成后提交）
                self.consumer.commit()

        finally:
            self.consumer.close()

    def _update_profile(self, event: dict):
        """更新用户画像"""
        user_id = event["user_id"]
        item_id = event["item_id"]
        print(f"更新用户 {user_id} 对物品 {item_id} 的画像")
        # 调用画像服务更新...
```

---

## 推荐系统事件流设计

### 推荐系统关键事件清单

```
user-events Topic
├── user.clicked_item        # 点击（短期兴趣信号，强）
├── user.viewed_item         # 浏览（弱信号）
├── user.purchased_item      # 购买（强转化信号，最重要）
├── user.added_to_cart       # 加购（高意图）
├── user.rated_item          # 评分（显式反馈）
├── user.searched_query      # 搜索词（意图信号）
├── user.followed_item       # 关注（长期兴趣）
└── user.unfollowed_item     # 取关
```

### 完整事件流架构图

```
                    ┌─────────────────────────────────────────┐
                    │              推荐请求                    │
                    │   GET /api/recommend?user_id=xxx        │
                    └────────────────────┬────────────────────┘
                                         ↓
                              ┌──────────────────────┐
                              │   API Gateway        │
                              │  （鉴权 / 限流）      │
                              └──────────┬───────────┘
                                         ↓
                              ┌──────────────────────┐
                              │   推荐服务            │
                              │  召回→排序→重排       │
                              └──────────┬───────────┘
                                         ↓
┌─────────────────────────────────────────┼───────────────────────────────┐
│              事件驱动层（Kafka）          ↓                               │
│                                         │                               │
│  ┌─────────────────┐  ┌─────────────────┐│┌─────────────────────────┐    │
│  │  用户行为事件    │  │ Kafka Producer  ││                          │    │
│  │  user.clicked   │──│ 同步发送事件     ││                          │    │
│  │  user.purchased │  │ （异步，非阻塞） ││                          │    │
│  └─────────────────┘  └─────────────────┘│                          │    │
│                                        ↓                            │    │
│                              ┌──────────────────┐                   │    │
│                              │  Kafka Cluster   │                   │    │
│                              │  Topic: events   │                   │    │
│                              └────────┬─────────┘                   │    │
│                                       │                              │    │
│              ┌────────────────────────┼────────────────────────┐     │    │
│              ↓                        ↓                        ↓     │    │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐  │    │
│  │ 画像更新 Consumer  │  │ 推荐缓存 Consumer │  │ 数据分析 Consumer │  │    │
│  │ 实时更新用户向量    │  │ 刷新协同过滤缓存  │  │ 统计 CTR/GMV      │  │    │
│  │ & 物品向量         │  │                   │  │                   │  │    │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘  │    │
└──────────────────────────────────────────────────────────────────────┘
```

### 多 Consumer 场景：消费者组隔离

```python
# 每个 Consumer 属于不同 Group，Group 内竞争消费，Group 间独立广播
consumer_groups = {
    "profile-service":   ProfileUpdateConsumer(bootstrap_servers, group_id="profile-service"),
    "cache-warmer":      CacheWarmerConsumer(bootstrap_servers, group_id="cache-warmer"),
    "analytics":         AnalyticsConsumer(bootstrap_servers, group_id="analytics"),
}
# profile-service 消费的消息，cache-warmer 和 analytics 也能收到
```

---

## 实战案例：推荐缓存预热

### 场景：用户行为触发推荐缓存更新

```
用户点击商品
    ↓
发布 click 事件 → Kafka
    ↓（异步，不阻塞推荐请求）
Cache Warmer 消费事件
    ↓
查询该用户最新特征
    ↓
预计算 Top20 推荐结果
    ↓
写入 Redis 缓存（TTL=5min）
    ↓
下次推荐请求直接命中缓存 → P99 从 200ms → 20ms
```

```python
# cache_warmer_consumer.py
class CacheWarmerConsumer:
    """推荐缓存预热消费者"""

    def __init__(self, recommendation_service, redis_client):
        self.rec_service = recommendation_service
        self.redis = redis_client

    def handle(self, event: RecommenderEvent):
        """处理用户行为事件，触发缓存更新"""
        if event.event_type not in [
            "user.clicked_item",
            "user.purchased_item",
            "user.rated_item"
        ]:
            return  # 只关心高价值行为

        user_id = event.user_id
        cache_key = f"rec:user:{user_id}:homefeed"

        # 异步计算并更新缓存（不阻塞事件处理）
        try:
            # 查询最新用户特征
            user_features = self._fetch_user_features(user_id)

            # 计算推荐结果（轻量级，多路召回简化版）
            recommendations = self.rec_service.recall(
                user_id=user_id,
                features=user_features,
                limit=20,
                timeout_ms=50  # 缓存更新要有超时保护
            )

            # 写入 Redis，设置过期时间
            self.redis.setex(
                cache_key,
                ttl=300,  # 5 分钟
                value=json.dumps(recommendations)
            )
            print(f"💾 缓存已更新: {cache_key}")

        except Exception as e:
            print(f"⚠️ 缓存更新失败: {e}")
            # 缓存失败不影响主流程，不重抛

    def _fetch_user_features(self, user_id: str) -> dict:
        """从特征存储获取用户实时特征"""
        # 实现特征获取逻辑...
        pass
```

---

## Kafka 可靠性配置

### 推荐系统关键配置

```python
producer = KafkaProducer(
    bootstrap_servers=["kafka-1:9092", "kafka-2:9092"],

    # ===== 可靠性配置 =====
    acks="all",           # 所有 ISR 副本确认（零丢失）
    retries=5,           # 网络抖动重试
    max_in_flight_requests_per_connection=1,  # 防止乱序

    # ===== 性能配置 =====
    compression_type="lz4",     # LZ4 压缩（吞吐高，CPU 低）
    batch_size=16384,           # 批量发送（16KB）
    linger_ms=5,                # 等待 5ms 凑批（降低请求数）

    # ===== 幂等性 =====
    enable_idempotence=True,   # 开启幂等性（防止重复发送）
)

consumer = KafkaConsumer(
    "user-events",

    # ===== 可靠性配置 =====
    enable_auto_commit=False,   # 手动提交（处理成功后再提交）
    max_poll_interval_ms=300000,  # 处理超时（5 分钟内必须处理完）
    session_timeout_ms=30000,   # 心跳超时

    # ===== 消费者配置 =====
    max_poll_records=200,       # 每批最多拉 200 条
    fetch_min_bytes=1024,       # 至少拉 1KB 才返回
)
```

### 生产环境巡检清单

```
Kafka 生产环境检查项
═══════════════════════════════════════════════════
✅ acks=all（数据不丢失）
✅ enable_idempotence=True（防止重复）
✅ replication_factor=3（每个分区 3 副本）
✅ 消费者手动提交 offset（处理成功才提交）
✅ 消费者处理有 try-catch（处理失败不阻塞后续）
✅ 监控：消费 lag（lag = 消费落后生产多少条）
✅ 监控：Producer 发送失败重试率
✅ 消费者组 rebalance 告警（消费者增减时触发）
```

---

## 事件驱动 vs 同步调用：如何选

```
什么时候用同步（gRPC / HTTP）？
├─ 需要实时返回结果（推荐请求 → 必须同步）
├─ 强一致性要求（下单→扣库存，必须同步等待）
└─ 简单场景（两个服务直接交互，无扩展需求）

什么时候用事件驱动（Kafka）？
├─ 允许延迟（用户行为分析，不需要实时）
├─ 多消费者（一个事件触发多个下游）
├─ 峰值削峰（618/双11 流量洪峰，先收消息慢慢处理）
├─ 系统解耦（服务间无直接依赖）
└─ 事件溯源（记录所有行为，重放历史）
```

---

## 常见误区

### ❌误区1：什么都用 Kafka
Kafka 不是万能的。简单的点对点同步调用，用 HTTP/gRPC 更直接。

### ❌误区2：Consumer 处理阻塞主循环
Consumer 处理耗时长 → 消费速度跟不上生产速度 → Lag 越来越大。
**正确做法**：处理逻辑用异步或线程池，不阻塞 `poll()` 循环。

### ❌误区3：没有幂等性设计
Kafka 可能重复投递（网络抖动后重试）。消费者必须幂等处理（如：根据 event_id 去重）。

```python
processed_ids = set()  # 内存去重（简单场景）

def handle(event: RecommenderEvent):
    if event.event_id in processed_ids:
        return  # 已处理，跳过
    processed_ids.add(event.event_id)
    # 处理逻辑...
```

### ❌误区4：不监控 Lag
消费 lag = 消息堆积 = 系统延迟。
**必须监控**：每个 Consumer Group 的消费 lag，设置告警阈值。

---

## 适用场景

- **推荐系统**：用户行为实时更新特征、预热推荐缓存
- **电商系统**：下单后异步发送邮件/短信/积分/库存核对
- **日志系统**：结构化日志 → Kafka → Flink/ClickHouse
- **搜索系统**：商品变更 → Kafka → 重建索引
- **风控系统**：支付事件 → Kafka → 多路风控规则并行检测

---

## 下一步

- 配合 [微服务架构实战](微服务架构实战.md) 理解 gRPC（同步）和 Kafka（异步）的混合架构
- 配合 [CQRS 模式实战](CQRS模式实战.md) 理解事件驱动在读写分离中的角色
- 参考 [架构师思维修炼](架构师思维修炼.md) 中的容量规划：Kafka 吞吐量估算
