# Flink 实时特征工程架构实战

> 推荐系统的"实时性"差距，往往不在模型，而在特征

## 🎯 核心问题

为什么两个召回策略、排序模型都一样的推荐系统，效果可以差 30%？

答案往往是：**特征时效性**。

| 特征类型 | 更新频率 | 技术方案 | 效果提升 |
|---------|---------|---------|---------|
| 静态特征（用户性别、商品类目）| 月/天级 | MySQL/Hive 批处理 | 基准线 |
| 天级统计（用户月购买量）| 天级 | Spark 日批 | +5~10% |
| 小时级统计（近6小时点击量）| 小时级 | Spark 小时批 | +10~15% |
| **实时特征（当前点击序列、实时偏好）** | **秒级** | **Flink 流计算** | **+15~30%** |

本章深入讲解如何用 Apache Flink 构建**秒级响应**的实时特征流水线，让推荐系统"看见"用户当下的行为。

---

## 一、流计算核心概念

### 1.1 批处理 vs 流处理：一张图说清楚

```
批处理（Batch）：全量数据 → 定时计算 → 产出特征
═══════════════════════════════════════════════════
                    ┌──────────┐
全体历史数据 ──────► │ Spark Job │ ──► 每天凌晨跑，产出昨天的特征
                    └──────────┘
问题：用户今天上午的行为，要到明天才影响推荐

流处理（Streaming）：每条事件 → 实时计算 → 立刻生效
═══════════════════════════════════════════════════
Kafka ──► 点击事件 ──► Flink ──► 实时点击计数 ──► Redis ──► 推荐引擎
          事件时间                     ↓
                               秒级更新（<1s延迟）
优势：用户行为秒级反馈到推荐结果
```

### 1.2 Flink 四大核心概念

| 概念 | 说明 | 推荐系统中的应用 |
|------|------|----------------|
| **DataStream** | 无界数据流，每条事件独立处理 | 用户点击/曝光/购买事件流 |
| **Keyed State** | 按 Key 聚合的状态（类似 Redis Hash） | 用户ID → 点击计数器 |
| **Window** | 时间窗口：滚动/滑动/会话 | "近5分钟点击量"、"今日曝光数" |
| **Watermark** | 事件时间水位线，处理乱序/迟到事件 | 3s 水位线 + 允许5s迟到 |

### 1.3 推荐系统五大实时特征

```
用户实时行为特征（最核心）
├── 实时点击序列（最近N个点击item_id）
├── 实时点击/曝光/购买计数（近5m/30m/2h）
├── 实时点击类目分布（偏好向量）
├── 实时Session行为（单次访问内的行为序列）
└── 实时点击转化率（点击→购买）

商品实时特征
├── 实时曝光/点击/购买量
├── 实时CTR（当前小时）
├── 实时价格最低价标记
└── 实时库存可用量

交叉实时特征
├── "用户当前点击类目 + 商品类目"匹配度
├── "用户最近交互品牌 vs 商品品牌"匹配度
└── "用户实时热度类目 vs 待推荐商品类目"加权
```

---

## 二、Flink 实时特征计算：完整代码实现

### 2.1 基础架构：Flink Job 模板

```python
"""
Flink 实时特征工程 Job 骨架
功能：消费 Kafka 用户行为事件 → 计算实时特征 → 写入 Redis
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaSource, KafkaOffsetsInitializer, KafkaRecordDeserializationSchema
)
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream.window import TimeCharacteristic, SlidingEventTimeWindows
from pyflink.common.time import Time
import json
import redis
from collections import defaultdict


# ─────────────────────────────────────────────
# 1. Flink 执行环境初始化
# ─────────────────────────────────────────────
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(8)                      # 并行度 = Kafka Partition 数
env.enable_checkpointing(30_000)            # 每30s做一次Checkpoint（exactly-once保证）
env.get_checkpoint_config().set_min_pause_between_checkpoints(10_000)

# ─────────────────────────────────────────────
# 2. Kafka 数据源配置
# ─────────────────────────────────────────────
kafka_source = (
    KafkaSource.builder()
    .set_bootstrap_servers("kafka:9092")
    .set_topics("user_behavior_events")
    .set_starting_offsets(KafkaOffsetsInitializer.committed_offsets())
    .set_value_only_deserializer(
        KafkaRecordDeserializationSchema.of(lambda record: json.loads(record))
    )
    .build()
)

# 事件时间 + 水位线策略（允许5s乱序）
watermark_strategy = (
    WatermarkStrategy
    .for_bounded_out_of_orderness(Duration.of_seconds(5))  # 允许5s乱序
    .with_timestamp_assigner(UserEventTimestampAssigner())
)

# ─────────────────────────────────────────────
# 3. 主处理流水线
# ─────────────────────────────────────────────
stream = env.from_source(
    source=kafka_source,
    watermark_strategy=watermark_strategy,
    source_name="KafkaUserBehaviorSource"
)

# 3.1 按用户ID分组（保证同一用户事件顺序处理）
keyed_stream = stream.key_by(lambda e: e["user_id"])

# 3.2 实时点击计数（滑动窗口：每5分钟更新一次）
click_count_stream = (
    keyed_stream
    .filter(lambda e: e["event_type"] == "click")
    .window(SlidingEventTimeWindows.of(Time.minutes(30), Time.minutes(5)))
    .count()
    # → 输出: (user_id, window_end, click_count_30m)
)

# 3.3 实时点击序列（保留最近N个item_id）
click_sequence_stream = (
    keyed_stream
    .filter(lambda e: e["event_type"] == "click")
    .map(KeepLastNItemsMapper(max_size=20))
)

# 3.4 实时类目偏好向量
category_distribution_stream = (
    keyed_stream
    .filter(lambda e: e["event_type"] == "click")
    .map(CategoryDistributionMapper(time_window_minutes=60))
)

# 3.5 写 Redis（多个Sink并行）
click_count_stream.add_sink(RedisClickCountSink())
click_sequence_stream.add_sink(RedisClickSequenceSink())
category_distribution_stream.add_sink(RedisCategoryDistSink())

# ─────────────────────────────────────────────
# 4. 启动
# ─────────────────────────────────────────────
env.execute("RealtimeFeaturePipeline")
```

### 2.2 核心算子实现

```python
from pyflink.datastream.functions import MapFunction, ProcessFunction
from pyflink.common.typeinfo import Types
from pyflink.datastream.state import ListStateDescriptor, MapStateDescriptor
from collections import deque


# ─────────────────────────────────────────────
# 算子1：保留最近N个点击（状态后端）
# ─────────────────────────────────────────────
class KeepLastNItemsMapper(MapFunction):
    """
    状态后端示例：每个用户维护一个最多N个item的点击序列
    状态存储在 Flink Managed State（RocksDB），容错且可扩展
    """

    def __init__(self, max_size: int = 20):
        self.max_size = max_size
        self.click_sequence_state = None

    def open(self, runtime_context):
        # 注册 ListState（有序列表，支持添加和截断）
        state_descriptor = ListStateDescriptor(
            "click_sequence",
            Types.PICKLED_BYTE_ARRAY()       # Python对象序列化存储
        )
        self.click_sequence_state = runtime_context.get_list_state(state_descriptor)

    def map(self, event: dict) -> dict:
        item_id = event["item_id"]
        timestamp = event["timestamp"]

        # 读取当前序列
        current_list = list(self.click_sequence_state.get())
        current_list.append({"item_id": item_id, "ts": timestamp})

        # 截断到最近N个（滑动窗口逻辑）
        if len(current_list) > self.max_size:
            current_list = current_list[-self.max_size:]

        # 写回状态
        self.click_sequence_state.update(current_list)

        return {
            "user_id": event["user_id"],
            "click_sequence": [x["item_id"] for x in current_list[-10:]],  # 返回最近10个
            "click_count": len(current_list),
            "last_click_ts": timestamp
        }


# ─────────────────────────────────────────────
# 算子2：类目偏好分布（滑动窗口计数）
# ─────────────────────────────────────────────
class CategoryDistributionMapper(MapFunction):
    """
    计算用户过去N分钟内点击的类目分布
    例如：{ "电子产品": 0.5, "服装": 0.3, "美妆": 0.2 }

    用途：实时捕捉用户当下在逛什么，用于类目加权召回
    """

    def __init__(self, time_window_minutes: int = 60):
        self.time_window = time_window_minutes * 60
        self.category_state = None

    def open(self, runtime_context):
        state_descriptor = ListStateDescriptor(
            "category_clicks",
            Types.PICKLED_BYTE_ARRAY()
        )
        self.category_state = runtime_context.get_list_state(state_descriptor)

    def map(self, event: dict) -> dict:
        category = event.get("category", "unknown")
        timestamp = event["timestamp"]

        # 读取并过滤（移除窗口外的旧数据）
        clicks = list(self.category_state.get())
        cutoff_ts = timestamp - self.time_window
        clicks = [(cat, ts) for cat, ts in clicks if ts > cutoff_ts]
        clicks.append((category, timestamp))

        self.category_state.update(clicks)

        # 计算分布
        total = len(clicks)
        dist = defaultdict(float)
        for cat, _ in clicks:
            dist[cat] += 1.0 / total

        return {
            "user_id": event["user_id"],
            "category_distribution": dict(dist),
            "top_category": max(dist, key=dist.get),
            "window_minutes": self.time_window // 60,
            "ts": timestamp
        }


# ─────────────────────────────────────────────
# 算子3：实时CTR计算（小时窗口）
# ─────────────────────────────────────────────
class RealtimeItemCTRProcessor(ProcessFunction):
    """
    按商品ID聚合，计算实时小时CTR
    输出格式：{ item_id: { "exposure_1h": 1000, "click_1h": 50, "ctr_1h": 0.05 } }

    这是推荐排序层的关键特征：实时热度直接影响排序分数
    """

    def __init__(self):
        self.item_stats_state = None

    def open(self, runtime_context):
        descriptor = MapStateDescriptor(
            "item_hourly_stats",
            Types.STRING(),
            Types.PICKLED_BYTE_ARRAY()
        )
        self.item_stats_state = runtime_context.get_map_state(descriptor)

    def process_element(self, event: dict, ctx: ProcessFunction):
        item_id = event["item_id"]
        event_type = event["event_type"]       # "exposure" 或 "click"
        timestamp = event["timestamp"]

        # 获取当前小时的起始时间戳（整点对齐）
        hour_key = timestamp - (timestamp % 3600)

        # 读取/初始化该商品该小时的统计
        stats = self.item_stats_state.get(item_id)
        if stats is None:
            stats = {"exposure": 0, "click": 0, "hour_key": hour_key}
        else:
            # 新小时开始，重置计数器
            if stats["hour_key"] != hour_key:
                stats = {"exposure": 0, "click": 0, "hour_key": hour_key}

        # 更新计数
        if event_type == "exposure":
            stats["exposure"] += 1
        elif event_type == "click":
            stats["click"] += 1

        self.item_stats_state.put(item_id, stats)

        # 计算CTR
        ctr = stats["click"] / stats["exposure"] if stats["exposure"] > 0 else 0.0
        yield {
            "item_id": item_id,
            "exposure_1h": stats["exposure"],
            "click_1h": stats["click"],
            "ctr_1h": round(ctr, 4),
            "ts": timestamp
        }
```

### 2.3 Redis Sink（实时特征写入）

```python
import redis
import json
from pyflink.datastream import SinkFunction


class RedisFeatureSink(SinkFunction):
    """
    自定义 Flink Sink：将实时特征写入 Redis
    设计决策：
    - Key 格式：feature:{type}:{user_id/item_id}
    - TTL = 窗口长度的2倍（保证窗口滑动时数据不中断）
    """

    def __init__(self, redis_host: str = "redis", redis_port: int = 6379):
        super().__init__()
        self.redis_host = redis_host
        self.redis_port = redis_port

    def open(self, runtime_context):
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            decode_responses=True,
            socket_timeout=2,
            socket_connect_timeout=2
        )

    def invoke(self, value: dict, context: SinkFunction.Context):
        self._write_click_count(value)
        self._write_click_sequence(value)
        self._write_category_dist(value)

    def _write_click_count(self, value: dict):
        """写入实时点击计数"""
        if "click_count" not in value:
            return
        key = f"rt:click_count:{value['user_id']}"
        self.redis_client.setex(
            key,
            3600,                                        # TTL = 1小时
            json.dumps({
                "count": value["click_count"],
                "ts": value.get("last_click_ts", 0)
            })
        )

    def _write_click_sequence(self, value: dict):
        """写入点击序列（保留最近10个item）"""
        if "click_sequence" not in value:
            return
        key = f"rt:click_seq:{value['user_id']}"
        seq_json = json.dumps(value["click_sequence"][-10:])
        self.redis_client.setex(key, 1800, seq_json)    # TTL = 30分钟

    def _write_category_dist(self, value: dict):
        """写入类目偏好分布"""
        if "category_distribution" not in value:
            return
        key = f"rt:cat_dist:{value['user_id']}"
        self.redis_client.setex(
            key,
            7200,                                        # TTL = 2小时
            json.dumps(value["category_distribution"])
        )

    def close(self):
        self.redis_client.close()
```

---

## 三、推荐引擎实时特征接入

```python
"""
推荐引擎实时特征获取
位置：推荐引擎 API 服务，在调用精排模型前获取实时特征
"""

import redis
import json
from typing import Optional


class RealtimeFeatureService:
    """
    实时特征服务：统一封装从 Redis 获取实时特征的逻辑
    设计要点：
    1. 三级降级：Redis → 本地缓存 → 空值（不影响主流程）
    2. 超时保护：单个特征获取超时100ms，整体不超过200ms
    3. 批量获取：一次 Redis MGET 获取多个特征，减少网络往返
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def get_user_realtime_features(self, user_id: str) -> dict:
        """
        获取用户全部实时特征
        """
        keys = [
            f"rt:click_count:{user_id}",
            f"rt:click_seq:{user_id}",
            f"rt:cat_dist:{user_id}",
        ]

        values = self.redis.mget(keys)  # 批量获取

        features = {}

        if values[0]:
            features["click_count_30m"] = json.loads(values[0])["count"]
        else:
            features["click_count_30m"] = 0

        if values[1]:
            features["click_sequence"] = json.loads(values[1])
        else:
            features["click_sequence"] = []

        if values[2]:
            features["category_distribution"] = json.loads(values[2])
        else:
            features["category_distribution"] = {}

        return features

    def get_item_realtime_features(self, item_id: str) -> dict:
        """获取商品实时特征（CTR、曝光量等）"""
        key = f"rt:item_stats:{item_id}"
        value = self.redis.get(key)

        if value:
            stats = json.loads(value)
            ctr = stats["click_1h"] / max(stats["exposure_1h"], 1)
            return {
                "item_ctr_1h": round(ctr, 4),
                "item_click_1h": stats["click_1h"],
                "item_exposure_1h": stats["exposure_1h"]
            }
        return {"item_ctr_1h": 0.0, "item_click_1h": 0, "item_exposure_1h": 0}

    def enrich_candidates_with_realtime(self, user_id: str, items: list[dict]) -> list[dict]:
        """
        为候选集补充实时特征（精排前的特征增强）
        """
        item_ids = [item["item_id"] for item in items]
        pipeline = self.redis.pipeline()

        for item_id in item_ids:
            pipeline.get(f"rt:item_stats:{item_id}")

        results = pipeline.execute()

        enriched = []
        for item, rt_stats_raw in zip(items, results):
            if rt_stats_raw:
                stats = json.loads(rt_stats_raw)
                ctr = stats["click_1h"] / max(stats["exposure_1h"], 1)
                item["realtime_ctr"] = round(ctr, 4)
                item["realtime_click"] = stats["click_1h"]
            else:
                item["realtime_ctr"] = 0.0
                item["realtime_click"] = 0
            enriched.append(item)

        return enriched


# ─────────────────────────────────────────────
# 推荐引擎集成示例（FastAPI）
# ─────────────────────────────────────────────
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

redis_pool = redis.ConnectionPool(host="redis", port=6379, max_connections=50)
rt_feature_service = RealtimeFeatureService(redis.Redis(connection_pool=redis_pool))


class RecommendRequest(BaseModel):
    user_id: str
    scene: str = "home"
    top_k: int = 20


@app.post("/recommend")
def recommend(req: RecommendRequest):
    # Step 1: 获取用户实时特征（新增！）
    rt_features = rt_feature_service.get_user_realtime_features(req.user_id)

    # Step 2: 多路召回（实时偏好加权，去除已点击）
    candidates =召回_engine.recall(
        user_id=req.user_id,
        user_categories=rt_features.get("category_distribution", {}),
        exclude_items=rt_features.get("click_sequence", []),
    )

    # Step 3: 精排（补充实时特征）
    enriched = rt_feature_service.enrich_candidates_with_realtime(req.user_id, candidates)
    ranked = ranker.rank(enriched, rt_features)

    # Step 4: 重排 + 返回
    final = reranker.rerank(ranked, rt_features, diversity_weight=0.2)

    return {
        "user_id": req.user_id,
        "items": final,
        "realtime_features": {
            "click_count_30m": rt_features["click_count_30m"],
            "top_category": max(
                rt_features.get("category_distribution", {}),
                key=rt_features.get("category_distribution", {}).get,
                default=None
            )
        }
    }
```

---

## 四、Late Events 与 Watermark 处理

### 4.1 乱序问题的根源

```
问题：Kafka 消息可能乱序（网络延迟/重试）

例子（错误）：
- 10:00:03 点击 item_B（正常到达）
- 10:00:01 曝光 item_B（更快到达）
→ 按到达顺序：曝光 → 点击（时序错误！）

正确顺序：
10:00:01 曝光 item_B → 10:00:01 点击 item_A → 10:00:03 点击 item_B
```

### 4.2 Watermark 策略选择

```python
from pyflink.common.watermark_strategy import WatermarkStrategy, Duration

# ─────────────────────────────────────────────
# 策略1：有界乱序（工业首选）
# ─────────────────────────────────────────────
watermark_strategy = (
    WatermarkStrategy
    .for_bounded_out_of_orderness(Duration.of_seconds(5))  # 允许5s乱序
    .with_timestamp_assigner(UserEventTimestampAssigner())
)

# ─────────────────────────────────────────────
# 策略2：会话窗口（更适合用户Session行为分析）
# ─────────────────────────────────────────────
from pyflink.datastream.window import EventTimeSessionWindow

session_stream = (
    keyed_stream
    .window(EventTimeSessionWindow.with_gap(Time.minutes(10)))  # 10分钟无行为则Session结束
    .aggregate(SessionAggregator())
)

# ─────────────────────────────────────────────
# 策略3：侧输出收集迟到事件
# ─────────────────────────────────────────────
late_output_tag = OutputTag[dict]("late-events")

# 迟到超过5s的事件 → 写入单独 Kafka Topic 用于离线分析
late_events_stream = process.get_side_output(late_output_tag)
late_events_stream.add_sink(KafkaSink("late-behavior-events"))
```

### 4.3 三种处理迟到事件的策略对比

| 策略 | 实现方式 | 推荐场景 | 代价 |
|------|---------|---------|------|
| **直接丢弃** | `.without_allow_lateness()` | 实时性 > 准确性（如实时竞价）| 可能丢失有效行为 |
| **侧输出收集** | `OutputTag` | 工业标配，需要回溯分析 | 需要额外存储 |
| **allowedLateness** | `.allowed_lateness(Time.seconds(30))` | 准确性要求高（如金融风控）| 状态存储增加 |

---

## 五、端到端实时特征架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                     推荐系统实时特征架构                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  【数据源层】                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │ APP SDK │  │ Web JS  │  │ 小程序   │  │ 后端日志 │              │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘              │
│       └────────────┴────────────┴────────────┘                    │
│                        │ Kafka Topic: user_behavior_events        │
│                        ▼                                          │
│  【Flink 流计算层】                                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Parallelism=8（= Kafka Partition 数）                       │ │
│  │                                                              │ │
│  │  KeyBy(user_id) ──►  Sliding Window ──► 实时特征计算          │ │
│  │                                                              │ │
│  │  算子1: KeepLastNItems   → 实时点击序列（最近20个）           │ │
│  │  算子2: CategoryDist     → 类目偏好分布（过去1h）             │ │
│  │  算子3: ClickCount       → 点击计数（30m滑动窗口）            │ │
│  │  算子4: RealtimeCTR      → 商品实时CTR（小时窗口）            │ │
│  │  算子5: SessionBehavior  → Session行为序列（10min gap）       │ │
│  │                                                              │ │
│  │  Checkpoint: 每30s，RocksDB状态后端（exactly-once）            │ │
│  └──────────────────────────┬──────────────────────────────────┘ │
│                             │ Redis Sink（批量写入，ms级延迟）   │
│                             ▼                                    │
│  【存储层】                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────────┐ │
│  │ Redis    │ │ Redis    │ │ Redis    │ │ ClickHouse（离线）   │ │
│  │ 实时计数 │ │ 点击序列  │ │ 类目分布  │ │ 全量行为日志归档     │ │
│  │ TTL=1h   │ │ TTL=30m  │ │ TTL=2h   │ │ DWD层 + 物化视图      │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────────┘ │
│                             │                                    │
│                             ▼                                    │
│  【应用层】                                                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  推荐引擎 API                                                  │ │
│  │                                                              │ │
│  │  召回  ──► 精排（实时特征增强） ──► 重排  ──► 响应             │ │
│  │              ↑                                          ↑     │
│  │              │ Redis GET (<1ms)                              │ │
│  │  ┌───────────┴───────────┐                                   │ │
│  │  │ RealtimeFeatureService │  ← 每请求从 Redis 批量拉取       │ │
│  │  └───────────────────────┘                                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                             │                                    │
│                             ▼                                    │
│  【监控层】                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                          │
│  │ Flink UI │ │ Prometheus│ │ Grafana │                          │
│  │ Job监控   │ │ 指标采集  │ │ 看板    │                          │
│  └──────────┘ └──────────┘ └──────────┘                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 六、Flink 作业运维实战

### 6.1 高可用配置（Kubernetes 部署）

```yaml
# flink-job-config.yaml（Flink on K8s）
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: realtime-features
spec:
  flinkVersion: v1_17
  flinkConfiguration:
    # 高可用：ZK 协调，避免单点故障
    high-availability: zookeeper
    high-availability.storageDir: s3://flink-ha/realtime-features
    # Checkpoint 配置
    execution.checkpointing.interval: 30s
    execution.checkpointing.mode: EXACTLY_ONCE
    execution.checkpointing.externalized-checkpoint-retention: RETAIN_ON_CANCELLATION
    # 状态后端：RocksDB（支持大状态 + 增量Checkpoint）
    state.backend: rocksdb
    state.backend.incremental: true
    parallelism.default: 8
  podTemplate:
    spec:
      containers:
        - name: flink-main-container
          resources:
            requests:
              memory: "4Gi"
              cpu: "2"
            limits:
              memory: "6Gi"
              cpu: "4"
```

### 6.2 常见运维问题及处理

| 问题 | 现象 | 原因 | 解决方案 |
|------|------|------|---------|
| **Checkpoint 失败** | Flink UI 红色报警 | RocksDB 写入慢/网络抖动 | 调大 `execution.checkpointing.timeout`；检查磁盘 IO |
| **State 过大** | TaskManager OOM | 窗口太大/状态无清理 | 减小窗口；用增量Checkpoint |
| **Kafka Lag 积压** | 消费延迟 > 5min | 消费速度 < 产生速度 | 扩大并行度至 Partition 数 × 2 |
| **Late Event 过多** | 大量事件进入 side output | 水位线设置过严 | 放宽 watermark 到 10s；加 allowed lateness |
| **Redis 连接耗尽** | 写 Redis 超时 | 连接池过小 | 增大 Redis pool size；加 Pipeline 批量写 |
| **背压（BackPressure）** | Flink UI 显示红色 | Sink 处理速度跟不上 | 增加 Sink 并行度；加 Redis Pipeline 批量写 |

---

## 七、实时 vs 离线特征：效果对比

```
实验设计：某电商推荐系统 A/B Test（流量各 10%），连续 7 天

┌──────────────┬────────────┬─────────────┬──────────┐
│    指标      │  离线特征  │  实时特征   │   提升   │
├──────────────┼────────────┼─────────────┼──────────┤
│  CTR（点击率）│   3.2%    │    4.1%     │ +28.1%  │
│  CVR（转化率）│   1.8%    │    2.4%     │ +33.3%  │
│  人均点击数   │   8.5    │    11.2     │ +31.8%  │
│  停留时长     │  120s    │    145s     │ +20.8%  │
└──────────────┴────────────┴─────────────┴──────────┘

核心洞察：
- 离线特征描述"用户昨天是什么样"
- 实时特征描述"用户此刻在想什么"
→ 推荐系统的本质是"猜用户下一步想要什么"
→ 时间越近的数据越有价值
```

---

## 八、实时特征的三大挑战与应对

### 挑战1：特征覆盖率 vs 延迟的矛盾

```
三层特征降级策略（保障特征可用性）：
┌─────────────────────────────────────────┐
│ L1: 实时特征（Flink 计算，秒级）         │ ← 最优先
│ L2: 小时级特征（Spark 小时批）           │ ← 降级兜底
│ L3: 天级特征（昨日离线特征）              │ ← 保底
└─────────────────────────────────────────┘

代码示例：
def get_user_click_count(user_id: str) -> int:
    # L1: 实时
    val = redis.get(f"rt:click_count:{user_id}")
    if val:
        return json.loads(val)["count"]
    # L2: 小时级
    val = redis.get(f"h:click_count:{user_id}")
    if val:
        return json.loads(val)["count"]
    # L3: 天级（来自离线 Hive）
    val = redis.get(f"d:click_count:{user_id}")
    return int(val) if val else 0
```

### 挑战2：训练-服务一致性（Skew）

```
问题：训练时用实时特征，推理时 Redis 读取失败 → 特征为0，模型判断错误

解决方案：特征签名对比 + PSI 漂移检测
┌─────────────────────────────────────────────────────────┐
│ 训练阶段：                                              │
│   - 离线模拟实时特征获取流程（含失败场景）                │
│   - 记录特征签名：hash(实时特征值)                       │
│                                                          │
│ 推理阶段：                                              │
│   - 实时获取特征 → 记录签名                              │
│   - 上线前：离线签名 vs 在线签名对比                     │
│   - PSI 检测 > 0.2 → 告警，自动降级该特征                │
└─────────────────────────────────────────────────────────┘
```

### 挑战3：流批一体 Feature Store

```
解决方案：Feast Feature Store（推荐系统主流选型）

┌──────────────────────────────────────────────────────┐
│                 Feature Store 架构                    │
├──────────────────────────────────────────────────────┤
│  注册层：统一特征定义（name/type/entities/描述）        │
│           ↓                                           │
│  离线存储：Spark/Hive（Parquet，S3）                   │
│           ↓  ← 训练特征来源（批量读取）                │
│  在线存储：Redis（低延迟读取）                         │
│           ↓  ← 推理特征来源（实时读取）               │
│  同步引擎：FEAST Materialization（批→在线定时同步）   │
│           + Flink（实时流计算直写）                   │
└──────────────────────────────────────────────────────┘

# Feast 配置示例
feature_repos = [
    {
        "name": "user_realtime",
        "entities": [{"name": "user_id", "value_type": "STRING"}],
        "features": [
            {"name": "user:click_count_1h",  "dtype": "INT64"},
            {"name": "user:category_dist",  "dtype": "BYTES"},
        ],
        "online_store": {"redis": {"host": "redis", "port": 6379}},
        "ttl": "7200s",
    },
    {
        "name": "user_offline",
        "entities": [{"name": "user_id", "value_type": "STRING"}],
        "features": [
            {"name": "user:age_range",        "dtype": "STRING"},
            {"name": "user:purchase_power",   "dtype": "FLOAT"},
        ],
        "batch_source": {"parquet": {"uri": "s3://features/user.parquet"}},
        "online_store": {"redis": {"host": "redis", "port": 6379}},
        "ttl": "86400s",
    }
]
```

---

## 九、生产检查清单

```
Flink 实时特征工程上线前检查清单
══════════════════════════════════════════════════════════════════

□ 1. 功能正确性
  □ Kafka 事件 schema 与 Flink 解析一致（含字段兼容性）
  □ Watermark 策略与事件时间戳字段对应
  □ 状态后端（RocksDB）磁盘空间充足（> 50GB per TM）
  □ Checkpoint 成功率和耗时监控（成功率 > 99%，耗时 < 10s）
  □ 所有状态变量已在 open() 中注册（避免TM重启后状态丢失）

□ 2. 性能指标
  □ Kafka Consumer Lag < 10000 条（持续监控）
  □ Redis 写入 P99 < 50ms
  □ Flink Job 无背压（Flink UI 检查）
  □ 并行度 = Kafka Partition 数（或其倍数）

□ 3. 容错能力
  □ Checkpoint 开启 exactly-once
  □ Flink Job 高可用（ZK HA 或 K8s 部署）
  □ Redis 连接池有降级：Flink 写 Redis 失败不阻塞主流程
  □ Late Event side output 有消费（不堆积）

□ 4. 可观测性
  □ Flink 自定义 Metrics 上报 Prometheus（写入计数/延迟/错误数）
  □ Grafana 看板：Lag / Checkpoint / 背压 / Redis 写入延迟
  □ Kafka Topic 消费进度告警（Lag > 阈值 → 钉钉/短信）
  □ Flink Job 重启自动恢复（K8s Deployment 或 YARN）

□ 5. 与推荐引擎集成
  □ 推荐引擎启动时加载实时特征（如 Redis 连接池初始化）
  □ 实时特征获取有超时保护（100ms / 请求级别）
  □ 实时特征缺失时有离线特征降级
  □ 推荐引擎有实时特征版本日志（用于特征 Skew 排查）

□ 6. 安全规范
  □ Kafka/Flink/Redis 网络隔离（不同网段）
  □ 无硬编码密码（统一用 K8s Secret 或 Vault）
  □ Flink UI 有认证（避免内部信息泄露）
```

---

## 十、适用场景速查

| 场景 | 是否需要实时特征 | 推荐实现 | 优先级 |
|------|---------------|---------|--------|
| 首页瀑布流推荐 | ✅ 强需求 | Flink + Redis | P0 |
| 搜索结果排序 | ✅ 强需求 | Flink + Redis | P0 |
| 实时热搜榜单 | ✅ 强需求 | Flink + Redis Sorted Set | P0 |
| 直播电商推荐 | ✅ 强需求 | Flink + Redis（分钟级已足够）| P0 |
| 详情页相关推荐 | 🟡 可选 | Redis 本地缓存（5min TTL）| P1 |
| 用户个人中心推荐 | ❌ 不需要 | 纯离线特征即可 | P2 |
| 邮件/推送推荐 | ❌ 不需要 | 离线批处理 | P2 |

---

## 常见误区

- **误区1：实时特征越多越好**。实时特征带来额外系统复杂度，优先对 CTR/CVR 影响最大的特征实时化
- **误区2：Flink Job 写代码不需要测试**。必须写单元测试（Mock Kafka/Redis），防止 Flink 作业 bug 污染数据
- **误区3：状态无限增长**。必须设计状态清理机制（TTL + allowed lateness），否则 RocksDB OOM
- **误区4：Kafka Lag 不监控**。Lag 积压 = 实时特征已过期，务必设置告警阈值
- **误区5：只管计算不管存储**。Redis 连接池耗尽 = 实时特征无法读取，推理全靠离线特征兜底
