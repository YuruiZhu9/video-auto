# DDD 领域驱动设计入门
> 从"和数据说话"到"和业务说话" · 推荐系统工程师视角

---

## 什么是 DDD？

**Domain-Driven Design（领域驱动设计）** 是一种以业务领域为核心的软件设计方法论。

### 一句话总结
> **用代码表达业务概念，而不是用业务逻辑迁就技术实现**

### 对比：传统做法 vs DDD 做法

| 维度 | 传统做法 | DDD 做法 |
|------|---------|---------|
| 核心关注 | 数据表结构 | 业务概念和规则 |
| 贫血模型 | Service 塞满逻辑 | Domain 对象自己知道规则 |
| 团队协作 | 前后端各自理解需求 | 统一语言（Ubiquitous Language） |
| 复杂度应对 | 大一统系统 | bounded context 限界上下文 |
| 变化应对 | 改表/改Service | 改领域模型 |

### 推荐系统中的 DDD 例子

**传统做法（贫血模型）：**
```python
# user_service.py —— 所有逻辑堆在这里
class UserService:
    def recommend(self, user_id: int, item_id: int) -> bool:
        user = db.query("SELECT * FROM users WHERE id = %s", user_id)
        item = db.query("SELECT * FROM items WHERE id = %s", item_id)
        
        # 业务规则散落在 SQL 和 Service 之间
        if user.age < 18 and item.category == "adult":
            return False
        if user.score < 100:
            return False
        return True
```

**DDD 做法（充血模型）：**
```python
# domain/user.py —— 用户自己知道自己的业务规则
class User:
    def __init__(self, age: int, score: int, tags: list[str]):
        self.age = age
        self.score = score
        self.tags = tags
    
    def can_see_item(self, item: "Item") -> bool:
        """用户能否看到这个 item——规则内聚在领域对象里"""
        if self.age < 18 and item.is_adult_content:
            return False
        if self.score < 100:
            return False
        return True
    
    def interest_matches(self, item: "Item") -> bool:
        """用户的标签和 item 标签是否有交集"""
        return bool(set(self.tags) & set(item.tags))


# application/recommend_service.py —— 编排用例
class RecommendService:
    def recommend_for_user(self, user_id: int, candidates: list[Item]) -> list[Item]:
        user = self.user_repo.find(user_id)
        # 业务规则在 domain 里，服务只负责编排
        return [item for item in candidates if user.can_see_item(item)]
```

---

## DDD 核心概念图

```
┌─────────────────────────────────────────────────────────────┐
│                    Bounded Context（限界上下文）              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Domain Layer（领域层）                  │    │
│  │  ┌─────────┐  ┌────────────┐  ┌────────────────┐  │    │
│  │  │ Entity  │  │Value Object│  │  Aggregate     │  │    │
│  │  │ 实体    │  │  值对象     │  │   聚合         │  │    │
│  │  └─────────┘  └────────────┘  └────────────────┘  │    │
│  │  ┌─────────────────────────────────────────────┐  │    │
│  │  │           Domain Service（领域服务）          │  │    │
│  │  │    跨实体的业务规则/计算                      │  │    │
│  │  └─────────────────────────────────────────────┘  │    │
│  │  ┌───────────────┐  ┌─────────────────────────┐  │    │
│  │  │ Domain Event  │  │      Repository        │  │    │
│  │  │   领域事件     │  │  (Port 接口定义)         │  │    │
│  │  └───────────────┘  └─────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↑                                  │
│              Application Layer（应用层）                      │
│                    用例编排 + 事务管理                        │
│                          ↑                                  │
│            Infrastructure（基础设施层）                       │
│           Repository 实现、缓存、外部 API 调用                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心概念详解

### 1. Entity（实体）

**定义：** 有唯一标识，且在生命周期内标识不变的对象。

```python
# ✅ 是 Entity：用户 ID 不变，但年龄、分数会变
class User:
    def __init__(self, user_id: str, age: int, score: int):
        self._id = user_id      # 唯一标识，不变
        self.age = age           # 可变属性
        self.score = score       # 可变属性
    
    @property
    def id(self) -> str:
        return self._id
    
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self._id == other._id  # 按 ID 比较，不是按属性
    
    def __hash__(self):
        return hash(self._id)


# ❌ 不是 Entity：地理位置用经纬度描述，没有固定标识
class Coordinates:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
```

**推荐系统中的 Entity：**
```python
class User(Entity):
    """用户实体——有固定 user_id"""
    pass

class Item(Entity):
    """商品/内容实体——有固定 item_id"""
    pass

class RecommendationResult(Entity):
    """推荐结果——有固定 result_id，用于去重和追踪"""
    pass
```

---

### 2. Value Object（值对象）

**定义：** 没有唯一标识，由属性值定义，相等即相同。

```python
# ✅ 是 Value Object：经纬度相同 = 同一个坐标，不需要 ID
class GeoLocation:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
    
    def __eq__(self, other):
        return self.lat == other.lat and self.lon == other.lon
    
    def distance_to(self, other: "GeoLocation") -> float:
        """计算两点间距离"""
        return haversine(self.lat, self.lon, other.lat, other.lon)


# ✅ 推荐系统中的 Value Object
class UserPreference:
    """用户偏好——只描述属性，不涉及身份"""
    def __init__(self, categories: list[str], price_range: tuple[float, float]):
        self.categories = set(categories)
        self.price_range = price_range
    
    def matches(self, item) -> bool:
        return (
            item.category in self.categories
            and item.price <= self.price_range[1]
            and item.price >= self.price_range[0]
        )


class ScoreCard:
    """推荐评分卡——一组特征分数，无唯一标识"""
    def __init__(self, recall_score: float, rank_score: float, diversity_score: float):
        self.recall_score = recall_score
        self.rank_score = rank_score
        self.diversity_score = diversity_score
    
    def final_score(self, weights: dict[str, float]) -> float:
        return (
            weights["recall"] * self.recall_score +
            weights["rank"] * self.rank_score +
            weights["diversity"] * self.diversity_score
        )
```

**Entity vs Value Object 判断口诀：**
> "能换不换？" —— 换了个属性，还是不是它？是 → Entity，否 → Value Object
> 
> 用户的年龄变了，用户还是那个用户 → Entity
> 坐标的纬度变了，就是另一个坐标了 → Value Object

---

### 3. Aggregate（聚合）

**定义：** 一组相关对象的集合，有一个 Aggregate Root（聚合根）作为唯一入口。

```python
# 推荐系统的聚合示例：用户 + 用户偏好 = 一个聚合
class UserAggregate:
    """用户聚合根——外部只能通过它访问内部对象"""
    
    def __init__(self, user: User, preference: UserPreference, history: list[UserEvent]):
        self._user = user
        self._preference = preference  # 内部值对象
        self._history = history       # 内部实体集合
    
    @property
    def user_id(self) -> str:
        return self._user.id
    
    def update_preference(self, categories: list[str]):
        """通过聚合根修改偏好——保证一致性"""
        if len(categories) > 20:
            raise ValueError("偏好标签不能超过20个")
        self._preference = UserPreference(
            categories=categories,
            price_range=self._preference.price_range
        )
        # 触发领域事件
        self._record_event("preference_updated")
    
    def _record_event(self, event_type: str):
        """内部记录历史"""
        self._history.append(UserEvent(event_type, datetime.now()))
    
    def get_relevant_history(self, days: int = 30) -> list[UserEvent]:
        """聚合根提供的查询接口"""
        cutoff = datetime.now() - timedelta(days=days)
        return [e for e in self._history if e.timestamp > cutoff]


# ❌ 错误做法：绕过聚合根直接修改内部对象
# user_aggregate._preference.categories.add("game")  ← 禁止！
# ✅ 正确做法：通过聚合根方法修改
# user_aggregate.update_preference([...])  ← 正确！
```

**聚合的设计原则：**
1. 聚合要小——只包含真正需要一致性的对象
2. 聚合之间通过 ID 引用，不直接引用内部对象
3. 聚合根是唯一入口，外部不能绕过它修改内部状态

---

### 4. Domain Service（领域服务）

**定义：** 跨越多个实体/聚合的业务逻辑，不属于任何一个实体。

```python
# 推荐系统中的领域服务
class RecommendationDomainService:
    """推荐核心业务逻辑——不属于 User 也不属于 Item"""
    
    def calculate_match_score(
        self, 
        user: User, 
        item: Item,
        context: RecommendationContext
    ) -> float:
        """
        计算用户-物品匹配度
        
        涉及多个实体（user + item + context），不适合放在任何一个里面
        """
        # 1. 基础匹配分
        category_score = 1.0 if item.category in user.tags else 0.3
        
        # 2. 质量分
        quality_score = item.quality_score / 10.0
        
        # 3. 上下文匹配（时间、地点）
        context_score = 1.0
        if context.hour and item.best_hour:
            hour_diff = abs(context.hour - item.best_hour)
            context_score = max(0.5, 1.0 - hour_diff / 12.0)
        
        # 加权汇总
        return (
            category_score * 0.5 +
            quality_score * 0.3 +
            context_score * 0.2
        )
    
    def should_include(
        self, 
        item: Item,
        user: User,
        current_result: list[Item]
    ) -> bool:
        """
        是否应该把 item 加入推荐结果
        涉及多样性判断——属于领域规则
        """
        # 同类别去重
        if any(i.category == item.category for i in current_result[-3:]):
            return False
        
        # 质量门槛
        if item.quality_score < 5.0:
            return False
        
        return True
```

---

### 5. Domain Event（领域事件）

**定义：** 业务领域中发生的重要事件，用于解耦和事件驱动。

```python
from dataclasses import dataclass
from datetime import datetime
from typing import NewType

UserId = NewType("UserId", str)
ItemId = NewType("ItemId", str)


@dataclass
class DomainEvent:
    """领域事件基类"""
    occurred_on: datetime
    event_id: str  # 用于幂等处理
    
    def event_type(self) -> str:
        return self.__class__.__name__


@dataclass
class UserClickedItem(DomainEvent):
    """用户点击了某个物品"""
    user_id: UserId
    item_id: ItemId
    position: int
    context: str  # 推荐位来源
    
    def event_type(self) -> str:
        return "user.clicked"


@dataclass
class UserViewedItem(DomainEvent):
    """用户浏览了某个物品"""
    user_id: UserId
    item_id: ItemId
    duration_seconds: int  # 停留时长


@dataclass
class ItemQualityUpdated(DomainEvent):
    """物品质量分更新"""
    item_id: ItemId
    old_score: float
    new_score: float


# 事件发布（应用层）
class UserEventPublisher:
    """发布领域事件"""
    
    def __init__(self, event_bus: "EventBus"):
        self._event_bus = event_bus
    
    def publish_click(self, user_id: str, item_id: str, position: int):
        event = UserClickedItem(
            occurred_on=datetime.now(),
            event_id=f"{user_id}:{item_id}:{position}",
            user_id=UserId(user_id),
            item_id=ItemId(item_id),
            position=position,
            context="home_feed"
        )
        self._event_bus.publish(event)


# 事件订阅（基础设施/下游服务）
class RecommendationModelUpdater:
    """订阅事件，触发模型更新"""
    
    def __init__(self, model_service: "ModelService"):
        self._model_service = model_service
    
    def handle(self, event: DomainEvent):
        if isinstance(event, UserClickedItem):
            self._model_service.record_click(event.user_id, event.item_id)
        elif isinstance(event, UserViewedItem):
            if event.duration_seconds > 10:  # 有效观看
                self._model_service.record_valid_view(
                    event.user_id, event.item_id
                )
        elif isinstance(event, ItemQualityUpdated):
            self._model_service.update_item_features(
                event.item_id, {"quality_score": event.new_score}
            )
```

---

### 6. Repository（仓储）

**定义：** 领域层定义的持久化接口（抽象），基础设施层负责实现。

```python
# ===== 领域层（Domain Layer）=====
# 只定义接口，不知道用什么存储

class UserRepository(ABC):
    """用户仓储接口——抽象，不关心 MySQL/Redis"""
    
    @abstractmethod
    def find(self, user_id: UserId) -> Optional[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> None:
        pass
    
    @abstractmethod
    def find_by_tag(self, tag: str, limit: int = 100) -> list[User]:
        """按标签查找用户（用于人群包推荐）"""
        pass


class ItemRepository(ABC):
    """物品仓储接口"""
    
    @abstractmethod
    def find(self, item_id: ItemId) -> Optional[Item]:
        pass
    
    @abstractmethod
    def find_by_category(
        self, category: str, limit: int = 100
    ) -> list[Item]:
        pass
    
    @abstractmethod
    def batch_find(self, item_ids: list[ItemId]) -> dict[ItemId, Item]:
        pass


# ===== 基础设施层（Infrastructure Layer）=====
# 实现仓储接口

class MySQLUserRepository(UserRepository):
    """MySQL 实现"""
    
    def __init__(self, db: "Database"):
        self._db = db
    
    def find(self, user_id: UserId) -> Optional[User]:
        row = self._db.query_one(
            "SELECT * FROM users WHERE id = %s", user_id
        )
        if not row:
            return None
        return User(user_id=row["id"], age=row["age"], score=row["score"])
    
    def save(self, user: User) -> None:
        self._db.execute(
            "INSERT INTO users (id, age, score) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE age=%s, score=%s",
            user.id, user.age, user.score, user.age, user.score
        )
    
    def find_by_tag(self, tag: str, limit: int = 100) -> list[User]:
        rows = self._db.query(
            "SELECT u.* FROM users u JOIN user_tags ut ON u.id=ut.user_id "
            "WHERE ut.tag=%s LIMIT %s", tag, limit
        )
        return [User(r["id"], r["age"], r["score"]) for r in rows]


class RedisUserRepository(UserRepository):
    """Redis 实现——用于高频访问"""
    
    def __init__(self, redis: "RedisClient"):
        self._redis = redis
    
    def find(self, user_id: UserId) -> Optional[User]:
        data = self._redis.hgetall(f"user:{user_id}")
        if not data:
            return None
        return User(user_id=user_id, age=float(data["age"]), score=float(data["score"]))
    
    def save(self, user: User) -> None:
        self._redis.hset(f"user:{user.id}", {
            "age": user.age, "score": user.score
        })
    
    def find_by_tag(self, tag: str, limit: int = 100) -> list[User]:
        # Redis Set 实现：SINTER 用户标签集合
        user_ids = self._redis.srandmember(f"tag:{tag}", limit)
        return [self.find(uid) for uid in user_ids if uid]


# ===== 应用层（Application Layer）=====
# 使用仓储，不关心实现细节

class UserProfileService:
    """应用服务——依赖抽象，不依赖具体实现"""
    
    def __init__(self, user_repo: UserRepository, event_publisher: "EventPublisher"):
        self._user_repo = user_repo          # 注入的是接口，不是实现
        self._event_publisher = event_publisher
    
    def get_user(self, user_id: str) -> User:
        return self._user_repo.find(UserId(user_id))
    
    def record_behavior(self, user_id: str, item_id: str, action: str):
        user = self._user_repo.find(UserId(user_id))
        user.record_action(action, item_id)
        self._user_repo.save(user)
        self._event_publisher.publish(
            UserViewedItem(user_id=UserId(user_id), item_id=ItemId(item_id))
        )
```

---

## Bounded Context（限界上下文）

**核心思想：** 一个系统中有多个子域，每个子域对同一个概念有不同的理解。

### 推荐系统中的限界上下文划分

```
┌─────────────────────────────────────────────────────────────────┐
│                        推荐系统整体                                │
├──────────────────┬──────────────────┬───────────────────────────┤
│  用户域           │   内容域          │   推荐引擎域                │
│  (User Context)   │ (Content Context) │ (Recommendation Context)  │
├──────────────────┼──────────────────┼───────────────────────────┤
│  用户注册/登录     │  内容发布/审核    │   召回/排序/重排            │
│  用户画像         │  内容标签         │   推荐算法                  │
│  用户关系链       │  内容质量评分     │   AB 测试                   │
├──────────────────┼──────────────────┼───────────────────────────┤
│  User 实体：      │  Item 实体：      │  RecommendationResult：    │
│  - user_id        │  - item_id        │  - result_id               │
│  - age            │  - category       │  - user_id                 │
│  - score          │  - quality_score │  - item_ids                │
│  - tags           │  - tags           │  - algorithm_version       │
│                  │                  │  - timestamp               │
├──────────────────┴──────────────────┴───────────────────────────┤
│                         跨上下文集成                              │
│  用户域 ←(user_id)→ 推荐引擎域    内容域 ←(item_id)→ 推荐引擎域   │
└─────────────────────────────────────────────────────────────────┘
```

### 跨上下文通信示例

```python
# 推荐引擎域 —— 不直接依赖用户域的内部实现，只通过跨上下文接口交互
class CrossContextAdapter:
    """跨上下文适配器——推荐引擎域用它获取用户信息"""
    
    def __init__(self, user_query_api: "UserQueryAPI", item_query_api: "ItemQueryAPI"):
        self._user_api = user_query_api    # 用户域暴露的查询接口
        self._item_api = item_query_api     # 内容域暴露的查询接口
    
    def get_user_features(self, user_id: str) -> dict:
        """只获取推荐引擎需要的用户特征，不暴露完整用户对象"""
        return self._user_api.query_for_recommend(user_id)
    
    def get_item_features(self, item_ids: list[str]) -> dict[str, dict]:
        """只获取推荐引擎需要的物品特征"""
        return self._item_api.batch_query_for_recommend(item_ids)
```

---

## TypeScript DDD 示例（NestJS）

```typescript
// ===== Domain Layer =====

// 值对象
export class UserPreferenceVO {
  constructor(
    public readonly categories: string[],
    public readonly priceRange: [number, number]
  ) {}

  matches(item: { category: string; price: number }): boolean {
    return (
      this.categories.includes(item.category) &&
      item.price >= this.priceRange[0] &&
      item.price <= this.priceRange[1]
    );
  }
}

// 实体
export class UserEntity {
  private preference: UserPreferenceVO;

  constructor(
    private readonly id: string,
    private age: number,
    private score: number,
    categories: string[] = [],
    priceMin: number = 0,
    priceMax: number = 99999
  ) {
    this.preference = new UserPreferenceVO(categories, [priceMin, priceMax]);
  }

  canSeeItem(item: { isAdultContent: boolean }): boolean {
    if (this.age < 18 && item.isAdultContent) return false;
    if (this.score < 100) return false;
    return true;
  }
}

// 聚合根
export class UserAggregate {
  constructor(
    private entity: UserEntity,
    private history: UserEvent[] = []
  ) {}

  get id(): string { return this.entity.id; }

  updatePreference(categories: string[], priceMin: number, priceMax: number) {
    if (categories.length > 20) {
      throw new Error('标签不能超过20个');
    }
    this.entity = new UserEntity(
      this.entity.id,
      this.entity.age,
      this.entity.score,
      categories,
      priceMin,
      priceMax
    );
    this.history.push(new UserEvent('preference_updated', new Date()));
  }
}

// 仓储接口（Domain 层定义）
export interface IUserRepository {
  find(id: string): Promise<UserAggregate | null>;
  save(aggregate: UserAggregate): Promise<void>;
}

// Domain Service
export class RecommendationDomainService {
  calculateMatchScore(
    user: UserEntity,
    item: { category: string; qualityScore: number; bestHour?: number },
    contextHour?: number
  ): number {
    const categoryScore = 1.0;
    const qualityScore = item.qualityScore / 10.0;
    let contextScore = 1.0;
    if (contextHour && item.bestHour) {
      const diff = Math.abs(contextHour - item.bestHour);
      contextScore = Math.max(0.5, 1 - diff / 12);
    }
    return categoryScore * 0.5 + qualityScore * 0.3 + contextScore * 0.2;
  }
}

// ===== Application Layer =====
export class RecommendApplicationService {
  constructor(
    @Inject('USER_REPOSITORY') private userRepo: IUserRepository,
    private domainService: RecommendationDomainService,
  ) {}

  async recommend(userId: string, candidateItems: any[], hour?: number) {
    const userAgg = await this.userRepo.find(userId);
    if (!userAgg) return [];

    const user = userAgg.entity;
    return candidateItems
      .filter(item => user.canSeeItem(item))
      .map(item => ({
        itemId: item.id,
        score: this.domainService.calculateMatchScore(user, item, hour),
      }))
      .sort((a, b) => b.score - a.score);
  }
}
```

---

## DDD 学习路径

```
第1步：理解核心概念（1-2天）
    → Entity / Value Object / Aggregate / Repository
    → 画自己的推荐系统中哪些是 Entity，哪些是 Value Object

第2步：划分 Bounded Context（1-2天）
    → 画出推荐系统的限界上下文
    → 明确跨上下文边界

第3步：实践仓储模式（2-3天）
    → 用 Repository 接口 + 基础设施实现
    → 理解依赖注入

第4步：引入 Domain Event（1-2天）
    → 识别推荐系统中的关键业务事件
    → 用事件驱动代替同步调用

第5步：DDD + 整洁架构整合（持续）
    → 领域层 ↔ 应用层 ↔ 基础设施层
    → 依赖倒置：领域层不依赖基础设施
```

---

## 常见误区

| 误区 | 正确做法 |
|------|---------|
| "用了 Entity 就是 DDD" | DDD 的核心是**业务概念内聚**，不是套用框架 |
| "所有对象都要是 Entity" | 大多数对象是 Value Object，不要过度设计 |
| "聚合越大越安全" | 聚合要**小**，只包含真正需要一致性的对象 |
| "DDD 就是多写接口" | 接口是为了**解耦**，不是为了让代码看起来更"企业级" |
| "先 DDD 再写代码" | DDD 是**迭代演化**的过程，不是一开始就设计好一切 |
| "领域服务可以放任何逻辑" | 领域服务只放**跨实体**的业务规则，能放在 Entity 里的就放 Entity 里 |

---

## 推荐系统 DDD 自检清单

- [ ] 能说出哪些是 Entity，哪些是 Value Object
- [ ] 能识别推荐系统中的 Aggregate Root
- [ ] Repository 接口定义在领域层，实现放在基础设施层
- [ ] 业务规则从 Service 迁移到了 Domain 层
- [ ] 跨 bounded context 只通过 ID 关联，不直接引用
- [ ] 关键业务事件（点击、曝光、转化）通过 Domain Event 发布
