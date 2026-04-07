# Repository 模式与数据访问层实战

> 理解"数据从哪来、如何组织"——连接领域逻辑与持久化存储的桥梁

---

## 一、为什么需要 Repository 模式

### 1.1 直接 SQL 的问题

```python
# ❌ 反例：业务逻辑和数据访问混在一起
@app.post("/recommend")
async def recommend(user_id: int, scene: str):
    # 直接写 SQL
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM user_profiles WHERE id = $1", user_id
        )
        # 更多 SQL...
    
    # 业务逻辑
    if scene == "home":
        items =召回_协同过滤(rows)
    else:
        items =召回_内容基础(rows)
    
    # 又是一堆 SQL
    async with pool.acquire() as conn:
        for item in items:
            await conn.execute(
                "INSERT INTO recommend_logs VALUES ($1, $2, $3)",
                user_id, item.id, scene
            )
```

**问题清单：**
- ❌ 业务逻辑和 SQL 交织，无法单独测试业务
- ❌ 换数据库（MySQL → PostgreSQL）要改无数处
- ❌ 表结构变化影响所有业务代码
- ❌ 同样的查询逻辑被复制到多处

### 1.2 Repository 模式的核心思想

```
┌─────────────────────────────────────────────┐
│           应用层（用例/UseCase）               │
│   「获取用户推荐结果」「更新用户画像」           │
├─────────────────────────────────────────────┤
│         领域层（Domain / Service）            │
│   「推荐算法逻辑」「用户评分计算」               │
│   （完全不知道数据存在哪、用什么数据库）         │
├─────────────────────────────────────────────┤
│  Repository 接口层（抽象）                    │
│   IUserProfileRepo / IItemRepo / IEventRepo  │
│   （只定义"我能做什么"，不关心"怎么做」）       │
├─────────────────────────────────────────────┤
│     适配器层（Infrastructure / Adapter）      │
│   MySQLUserProfileRepo / RedisCacheRepo      │
│   （真正连接 MySQL/Redis 的代码）             │
└─────────────────────────────────────────────┘
```

**核心价值：**
- ✅ 业务逻辑"不知道"数据存在哪——可测试、可替换
- ✅ 表结构变化只影响 Repository 实现，不影响业务
- ✅ 同一个业务逻辑可以连接 MySQL + Redis + Kafka

---

## 二、Repository 抽象接口设计

### 2.1 推荐系统核心接口

```python
# repositories/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class UserProfile:
    """用户画像 - 领域对象（纯数据，无行为）"""
    user_id: int
    age: int
    gender: str
    tags: List[str]
    embedding: List[float]
    last_active: datetime


@dataclass
class Item:
    """物品 - 领域对象"""
    item_id: str
    category: str
    tags: List[str]
    embedding: List[float]
    popularity: float
    price: Optional[float] = None


@dataclass
class BehaviorEvent:
    """行为事件 - 领域对象"""
    event_id: str
    user_id: int
    item_id: str
    event_type: str  # click/view/purchase/rate
    timestamp: datetime
    metadata: Dict[str, Any]


# ── 基础 Repository 接口 ──────────────────────────

class IUserProfileRepository(ABC):
    """用户画像仓储接口"""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[UserProfile]:
        """根据ID获取用户"""
        ...

    @abstractmethod
    async def get_batch(self, user_ids: List[int]) -> Dict[int, UserProfile]:
        """批量获取用户（解决 N+1 问题）"""
        ...

    @abstractmethod
    async def update_tags(self, user_id: int, tags: List[str]) -> None:
        """更新用户标签"""
        ...

    @abstractmethod
    async def update_embedding(self, user_id: int, embedding: List[float]) -> None:
        """更新用户向量"""
        ...


class IItemRepository(ABC):
    """物品仓储接口"""

    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[Item]:
        ...

    @abstractmethod
    async def get_by_ids(self, item_ids: List[str]) -> Dict[str, Item]:
        """批量获取物品"""
        ...

    @abstractmethod
    async def search_by_category(
        self, category: str, limit: int = 100
    ) -> List[Item]:
        """按分类搜索"""
        ...

    @abstractmethod
    async def get_hot_items(self, days: int = 7, limit: int = 50) -> List[Item]:
        """获取热门物品"""
        ...


class IBehaviorRepository(ABC):
    """行为记录仓储接口"""

    @abstractmethod
    async def record(self, event: BehaviorEvent) -> None:
        """记录一次行为"""
        ...

    @abstractmethod
    async def get_user_events(
        self,
        user_id: int,
        event_types: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[BehaviorEvent]:
        """获取用户历史行为"""
        ...

    @abstractmethod
    async def get_user_item_matrix(
        self, user_id: int, days: int = 30
    ) -> Dict[str, float]:
        """获取用户-物品评分矩阵（用于协同过滤）"""
        ...
```

### 2.2 为什么用 dataclass 而不是 ORM Model

```python
# 领域对象 ≠ 数据表模型
# 领域对象是业务语言，ORM Model 是数据库语言

@dataclass
class UserProfile:
    user_id: int
    tags: List[str]           # 数据库里是 JSON，领域对象直接是 List[str]
    embedding: List[float]    # 数据库里是 vector，领域对象直接是 List[float]

# ❌ 错误做法：直接暴露 ORM Model 给业务层
# class UserProfile(Base):
#     __tablename__ = "users"
#     tags = Column(JSON)  # 业务层被迫理解 JSON 结构
#     embedding = Column(Vector)  # 受限于特定 ORM

# ✅ 正确做法：Repository 负责两者之间的转换
class MySQLUserProfileRepo(IUserProfileRepository):
    async def get_by_id(self, user_id: int) -> Optional[UserProfile]:
        row = await self.db.fetch_one(
            "SELECT * FROM users WHERE id = $1", user_id
        )
        if not row:
            return None
        # 关键：数据库行 → 领域对象的转换
        return UserProfile(
            user_id=row["id"],
            tags=row["tags"],  # JSON → List[str]
            embedding=self._decode_vector(row["embedding"]),  # vector → List[float]
            gender=row["gender"],
            age=row["age"],
            last_active=row["last_active"]
        )
```

---

## 三、Python 实现：FastAPI + PostgreSQL

### 3.1 主适配器：PostgreSQL 实现

```python
# repositories/adapters/mysql_user_profile_repo.py
import asyncpg
import json
from typing import List, Optional, Dict
from repositories.base import IUserProfileRepository, UserProfile
from datetime import datetime


class MySQLUserProfileRepository(IUserProfileRepository):
    """PostgreSQL 实现"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_by_id(self, user_id: int) -> Optional[UserProfile]:
        row = await self.pool.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )
        if not row:
            return None
        return self._row_to_entity(row)

    async def get_batch(self, user_ids: List[int]) -> Dict[int, UserProfile]:
        if not user_ids:
            return {}
        rows = await self.pool.fetch(
            "SELECT * FROM users WHERE id = ANY($1)", user_ids
        )
        return {
            row["id"]: self._row_to_entity(row)
            for row in rows
        }

    async def update_tags(self, user_id: int, tags: List[str]) -> None:
        await self.pool.execute(
            "UPDATE users SET tags = $1, updated_at = NOW() WHERE id = $2",
            tags, user_id
        )

    async def update_embedding(self, user_id: int, embedding: List[float]) -> None:
        vector_str = "[" + ",".join(map(str, embedding)) + "]"
        await self.pool.execute(
            "UPDATE users SET embedding = $1::vector, updated_at = NOW() WHERE id = $2",
            vector_str, user_id
        )

    def _row_to_entity(self, row) -> UserProfile:
        return UserProfile(
            user_id=row["id"],
            age=row["age"],
            gender=row["gender"],
            tags=row["tags"] or [],
            embedding=self._decode_vector(row["embedding"]),
            last_active=row["last_active"]
        )

    def _decode_vector(self, vector) -> List[float]:
        if vector is None:
            return [0.0] * 128
        if isinstance(vector, list):
            return vector
        return json.loads(str(vector))
```

### 3.2 缓存适配器：Redis 实现（读写分离）

```python
# repositories/adapters/redis_user_profile_repo.py
import json, redis.asyncio as redis
from typing import List, Optional, Dict
from repositories.base import IUserProfileRepository, UserProfile
from datetime import datetime


class RedisUserProfileRepository(IUserProfileRepository):
    """
    Redis 缓存实现（只读，用于加速）
    Repository 模式优势：可以同时有 MySQL 实现和 Redis 实现
    """

    CACHE_TTL = 300  # 5分钟

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def _cache_key(self, user_id: int) -> str:
        return f"user:profile:{user_id}"

    async def get_by_id(self, user_id: int) -> Optional[UserProfile]:
        key = self._cache_key(user_id)
        data = await self.redis.get(key)
        if not data:
            return None
        return self._json_to_entity(json.loads(data))

    async def get_batch(self, user_ids: List[int]) -> Dict[int, UserProfile]:
        if not user_ids:
            return {}
        keys = [self._cache_key(uid) for uid in user_ids]
        values = await self.redis.mget(keys)
        result = {}
        for uid, data in zip(user_ids, values):
            if data:
                result[uid] = self._json_to_entity(json.loads(data))
        return result

    async def update_tags(self, user_id: int, tags: List[str]) -> None:
        # 先查再更新，保持其他字段不变
        key = self._cache_key(user_id)
        data = await self.redis.get(key)
        if data:
            entity = json.loads(data)
            entity["tags"] = tags
            await self.redis.set(key, json.dumps(entity), ex=self.CACHE_TTL)

    async def update_embedding(self, user_id: int, embedding: List[float]) -> None:
        key = self._cache_key(user_id)
        data = await self.redis.get(key)
        if data:
            entity = json.loads(data)
            entity["embedding"] = embedding
            await self.redis.set(key, json.dumps(entity), ex=self.CACHE_TTL)

    def _json_to_entity(self, data: dict) -> UserProfile:
        return UserProfile(
            user_id=data["user_id"],
            age=data["age"],
            gender=data["gender"],
            tags=data.get("tags", []),
            embedding=data.get("embedding", [0.0] * 128),
            last_active=datetime.fromisoformat(data["last_active"])
        )
```

### 3.3 应用层：UseCase 使用 Repository

```python
# use_cases/recommend.py
from typing import List, Optional
from repositories.base import (
    IUserProfileRepository, IItemRepository, IBehaviorRepository, UserProfile
)
from services.recall import RecallEngine
from services.ranking import RankingEngine


class GetRecommendUseCase:
    """
    获取推荐结果用例
    特点：完全不依赖具体数据库，只依赖接口
    """

    def __init__(
        self,
        user_repo: IUserProfileRepository,
        item_repo: IItemRepository,
        behavior_repo: IBehaviorRepository,
        recall_engine: RecallEngine,
        ranking_engine: RankingEngine,
    ):
        # 通过接口注入，不关心是 MySQL 还是 Redis
        self.user_repo = user_repo
        self.item_repo = item_repo
        self.behavior_repo = behavior_repo
        self.recall_engine = recall_engine
        self.ranking_engine = ranking_engine

    async def execute(self, user_id: int, scene: str, count: int = 20) -> List[str]:
        # Step 1: 获取用户画像（从 Repository）
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return []

        # Step 2: 获取用户历史行为（从 Repository）
        user_matrix = await self.behavior_repo.get_user_item_matrix(user_id)

        # Step 3: 召回（纯业务逻辑）
        candidates = await self.recall_engine.recall(user, scene)

        # Step 4: 排序（纯业务逻辑）
        ranked = await self.ranking_engine.rank(user, candidates, user_matrix)

        return ranked[:count]
```

### 3.4 依赖注入容器

```python
# containers.py
import asyncpg, redis.asyncio as redis
from repositories.adapters.mysql_user_profile_repo import MySQLUserProfileRepository
from repositories.adapters.redis_user_profile_repo import RedisUserProfileRepository
from repositories.base import IUserProfileRepository, IItemRepository, IBehaviorRepository
from use_cases.recommend import GetRecommendUseCase
from services.recall import RecallEngine
from services.ranking import RankingEngine


class DIContainer:
    """
    简单依赖注入容器
    替换实现只需改这里
    """

    def __init__(self):
        self._db_pool: Optional[asyncpg.Pool] = None
        self._redis: Optional[redis.Redis] = None
        self._repos: Dict[str, object] = {}

    async def initialize(self):
        # 连接外部服务
        self._db_pool = await asyncpg.create_pool(
            host="localhost", database="recommend", user="admin", password="xxx"
        )
        self._redis = redis.Redis(host="localhost", decode_responses=True)

        # 注册 Repository（这里可以切换 MySQL ↔ Redis）
        self._repos["user_profile"] = MySQLUserProfileRepository(self._db_pool)
        # self._repos["user_profile"] = RedisUserProfileRepository(self._redis)

        # 注册 Service
        self._repos["recall"] = RecallEngine()
        self._repos["ranking"] = RankingEngine()

    def get_recommend_usecase(self) -> GetRecommendUseCase:
        return GetRecommendUseCase(
            user_repo=self._repos["user_profile"],
            item_repo=self._repos["item"],
            behavior_repo=self._repos["behavior"],
            recall_engine=self._repos["recall"],
            ranking_engine=self._repos["ranking"],
        )

    async def shutdown(self):
        await self._db_pool.close()
        await self._redis.close()


# FastAPI 集成
container = DIContainer()


async def get_recommend_usecase() -> GetRecommendUseCase:
    return container.get_recommend_usecase()


@app.post("/recommend")
async def recommend(
    user_id: int,
    scene: str = "home",
    usecase: GetRecommendUseCase = Depends(get_recommend_usecase)
):
    result = await usecase.execute(user_id, scene)
    return {"items": result}
```

---

## 四、TypeScript 实现：NestJS + TypeORM

### 4.1 领域模型 + 接口

```typescript
// src/domain/entities/user-profile.entity.ts
export interface UserProfile {
  userId: number;
  age: number;
  gender: 'M' | 'F' | 'unknown';
  tags: string[];
  embedding: number[];
  lastActive: Date;
}

export interface Item {
  itemId: string;
  category: string;
  tags: string[];
  embedding: number[];
  popularity: number;
  price?: number;
}

// src/domain/repositories/interfaces.ts
import { UserProfile, Item } from '../entities/user-profile.entity';

export interface IUserProfileRepository {
  findById(userId: number): Promise<UserProfile | null>;
  findBatch(userIds: number[]): Promise<Map<number, UserProfile>>;
  updateTags(userId: number, tags: string[]): Promise<void>;
}

export interface IItemRepository {
  findById(itemId: string): Promise<Item | null>;
  findByIds(itemIds: string[]): Promise<Map<string, Item>>;
  searchByCategory(category: string, limit?: number): Promise<Item[]>;
  getHotItems(days?: number, limit?: number): Promise<Item[]>;
}
```

### 4.2 TypeORM 实现（PostgreSQL）

```typescript
// src/infrastructure/repositories/postgres-user-profile.repo.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, In } from 'typeorm';
import { UserProfile } from '../../domain/entities/user-profile.entity';
import {
  IUserProfileRepository,
  IItemRepository,
} from '../../domain/repositories/interfaces';
import { UserOrm } from '../orm/user.orm'; // TypeORM Entity

@Injectable()
export class PostgresUserProfileRepository implements IUserProfileRepository {
  constructor(
    @InjectRepository(UserOrm)
    private readonly repo: Repository<UserOrm>,
  ) {}

  async findById(userId: number): Promise<UserProfile | null> {
    const row = await this.repo.findOne({ where: { id: userId } });
    return row ? this.toDomain(row) : null;
  }

  async findBatch(userIds: number[]): Promise<Map<number, UserProfile>> {
    const rows = await this.repo.find({ where: { id: In(userIds) } });
    const map = new Map<number, UserProfile>();
    for (const row of rows) {
      map.set(row.id, this.toDomain(row));
    }
    return map;
  }

  async updateTags(userId: number, tags: string[]): Promise<void> {
    await this.repo.update({ id: userId }, { tags, updatedAt: new Date() });
  }

  // 转换：数据库 ORM 实体 → 领域对象
  private toDomain(orm: UserOrm): UserProfile {
    return {
      userId: orm.id,
      age: orm.age,
      gender: orm.gender,
      tags: orm.tags || [],
      embedding: orm.embedding ? JSON.parse(orm.embedding) : [],
      lastActive: orm.lastActive,
    };
  }
}
```

### 4.3 NestJS 模块绑定

```typescript
// src/infrastructure/repositories/repositories.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UserOrm } from '../orm/user.orm';
import { PostgresUserProfileRepository } from './postgres-user-profile.repo';
import { IUserProfileRepository } from '../../domain/repositories/interfaces';

@Module({
  imports: [TypeOrmModule.forFeature([UserOrm])],
  providers: [
    {
      provide: IUserProfileRepository,
      useClass: PostgresUserProfileRepository,
    },
  ],
  exports: [IUserProfileRepository],
})
export class RepositoriesModule {}

// src/application/use-cases/get-recommend.usecase.ts
@Injectable()
export class GetRecommendUseCase {
  constructor(
    // 只依赖接口，不依赖实现
    @Inject(IUserProfileRepository)
    private readonly userRepo: IUserProfileRepository,
    @Inject(IItemRepository)
    private readonly itemRepo: IItemRepository,
  ) {}

  async execute(userId: number, scene: string): Promise<string[]> {
    const user = await this.userRepo.findById(userId);
    if (!user) return [];

    const candidates = await this.recallEngine.recall(user, scene);
    return this.rankingEngine.rank(user, candidates);
  }
}
```

---

## 五、Unit of Work 模式：批量操作原子性

### 5.1 为什么需要 Unit of Work

```python
# ❌ 没有 Unit of Work：多次保存，无法回滚
async def transfer_favorite(source_user: int, target_user: int, item_id: str):
    await user_repo.remove_favorite(source_user, item_id)
    await user_repo.add_favorite(target_user, item_id)
    await event_repo.record(TransferEvent(...))
    # 如果第三步失败，前两步无法回滚

# ✅ 有 Unit of Work：要么全部成功，要么全部回滚
class UnitOfWork:
    async def __aenter__(self):
        self.transaction = await self.pool.acquire()
        await self.transaction.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.transaction.rollback()
        else:
            await self.transaction.commit()
        await self.transaction.release()

    @property
    def user_repo(self):
        return UserRepository(self.transaction)

    @property
    def event_repo(self):
        return EventRepository(self.transaction)


async def transfer_favorite(source_user: int, target_user: int, item_id: str):
    async with UnitOfWork(pool) as uow:
        await uow.user_repo.remove_favorite(source_user, item_id)
        await uow.user_repo.add_favorite(target_user, item_id)
        await uow.event_repo.record(TransferEvent(...))
        # with 块结束时自动 commit，异常时自动 rollback
```

### 5.2 推荐系统的 Unit of Work 实践

```python
# use_cases/record_behavior_usecase.py

class RecordBehaviorUseCase:
    """
    推荐系统记录用户行为
    需要同时：写行为表 + 更新用户画像 + 发 Kafka 事件
    三步必须原子
    """

    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    async def execute(self, user_id: int, item_id: str, event_type: str):
        async with self.uow_factory() as uow:
            # 1. 记录行为
            await uow.behavior_repo.record(BehaviorEvent(...))

            # 2. 更新用户标签（基于行为）
            if event_type == "click":
                item = await uow.item_repo.get_by_id(item_id)
                user = await uow.user_repo.get_by_id(user_id)
                new_tags = self._merge_tags(user.tags, item.tags)
                await uow.user_repo.update_tags(user_id, new_tags)

            # 3. 发 Kafka 事件（用于实时特征更新）
            await uow.event_publisher.publish("user_behavior", {
                "user_id": user_id,
                "item_id": item_id,
                "event_type": event_type,
                "timestamp": datetime.now().isoformat()
            })
            # with 块退出时自动提交：行为 + 画像 + Kafka 事件要么全成功，要么全回滚
```

---

## 六、单元测试：Mock Repository

```python
# tests/test_recommend_usecase.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from use_cases.recommend import GetRecommendUseCase
from repositories.base import UserProfile, BehaviorEvent
from datetime import datetime


@pytest.fixture
def mock_repos():
    user_repo = AsyncMock()
    item_repo = AsyncMock()
    behavior_repo = AsyncMock()
    recall_engine = AsyncMock()
    ranking_engine = AsyncMock()

    return user_repo, item_repo, behavior_repo, recall_engine, ranking_engine


@pytest.fixture
def usecase(mock_repos):
    return GetRecommendUseCase(*mock_repos)


@pytest.mark.asyncio
async def test_recommend_returns_empty_for_unknown_user(usecase, mock_repos):
    user_repo, *_ = mock_repos
    user_repo.get_by_id.return_value = None

    result = await usecase.execute(user_id=999, scene="home")

    assert result == []
    user_repo.get_by_id.assert_called_once_with(999)


@pytest.mark.asyncio
async def test_recommend_recalls_and_ranks(usecase, mock_repos):
    user_repo, item_repo, behavior_repo, recall_engine, ranking_engine = mock_repos

    # 准备 Mock 数据
    user = UserProfile(
        user_id=1, age=25, gender="M", tags=["篮球", "科技"],
        embedding=[0.1]*128, last_active=datetime.now()
    )
    user_repo.get_by_id.return_value = user
    behavior_repo.get_user_item_matrix.return_value = {"item1": 5.0, "item2": 3.0}
    recall_engine.recall.return_value = ["item1", "item2", "item3"]
    ranking_engine.rank.return_value = ["item1", "item3", "item2"]

    result = await usecase.execute(user_id=1, scene="home", count=3)

    assert result == ["item1", "item3", "item2"]
    recall_engine.recall.assert_called_once_with(user, "home")
    ranking_engine.rank.assert_called_once()


@pytest.mark.asyncio
async def test_batch_users_no_n_plus_1(usecase, mock_repos):
    """验证批量查询不会产生 N+1 问题"""
    user_repo, *_ = mock_repos
    user_ids = [1, 2, 3, 4, 5]

    user_map = {
        uid: UserProfile(uid, 20+uid, "M", [], [0.0]*128, datetime.now())
        for uid in user_ids
    }
    user_repo.get_batch.return_value = user_map

    # 业务代码只调用一次 get_batch
    results = []
    for uid in user_ids:
        user = await user_repo.get_by_id(uid)
        results.append(user)

    # ❌ 错误方式：循环里每次查一次 DB（5次查询）
    # ✅ 正确方式：通过 Repository 批量查（1次查询）
    # 测试只验证 batch 被调用了一次
    user_repo.get_batch.assert_called_once()
```

---

## 七、常见误区与避坑

### 误区 1：Repository 里写业务逻辑

```python
# ❌ 错误：Repository 包含了业务逻辑
class MySQLUserProfileRepo:
    async def get_recommend_profiles(self, user_id):
        # SQL 里有推荐算法的影子
        query = """
            SELECT * FROM users u
            JOIN user_item_scores s ON u.id = s.user_id
            WHERE s.item_id IN (SELECT ...)
        """
        # 业务逻辑混入数据层

# ✅ 正确：Repository 只做数据存取，业务逻辑在上层
class MySQLUserProfileRepo:
    async def get_by_id(self, user_id): ...
    async def get_batch(self, user_ids): ...
    # 不包含任何业务逻辑
```

### 误区 2：一个 Repository 对应一张表

```python
# ❌ 教条主义：每个表建一个 Repository
class UserTableRepo: ...
class UserProfileTableRepo: ...
class UserTagTableRepo: ...
class UserEmbeddingTableRepo: ...
# 表变了，Repository 全要改

# ✅ 按业务需求设计：用户行为相关的读写逻辑封装为一个 Repository
class UserProfileRepository:
    # 一次聚合用户所有相关信息
    async def get_full_profile(self, user_id): ...
    async def update_profile(self, user_id, data): ...
    async def update_embedding(self, user_id, vector): ...
```

### 误区 3：所有查询都走 Repository

```python
# ✅ 读性能关键路径：直接 SQL 查询，不用 ORM
class ClickhouseAnalyticsRepo:
    """
    分析查询走 ClickHouse，不需要走标准的 Repository
    数据仓库的查询模式完全不同（OLAP vs OLTP）
    """
    async def get_user_cohort_analysis(self, cohort_id: int):
        # 复杂分析 SQL 直接写，不走 ORM
        result = await self.clickhouse.fetch(
            f"SELECT ... FROM behavior_events WHERE {cohort_id}"
        )
        return result
```

---

## 八、Repository 模式决策树

```
需要和数据库交互吗？
├── 是 → 数据来源是什么？
│   ├── MySQL/PostgreSQL → PostgresUserProfileRepo
│   ├── Redis → RedisUserProfileRepo
│   ├── MongoDB → MongoUserProfileRepo
│   ├── 向量数据库 → MilvusItemRepo
│   └── 多个数据源 → 组合多个 Repository
├── 否（内存/计算）→ 直接实现接口，不连任何外部服务
└── 需要原子事务吗？
    └── 是 → 引入 Unit of Work 模式
```

---

## 九、与已有知识关联

| 已有知识 | Repository 的关系 |
|----------|-------------------|
| 六边形架构 | Repository = 核心的"入边端口"（Inbound Port）实现 |
| Clean Architecture | Repository = 数据层的抽象，连接领域层和数据层 |
| 依赖注入容器 | 负责注入 Repository 实现，替换实现无需改业务代码 |
| 单元测试 | Mock Repository = 隔离外部依赖的关键 |
| CQRS | Command 用一个 Repository，Query 用另一个（读写分离） |

---

## 十、实践作业

### 作业 1：识别现有项目的 Repository（30分钟）
- 找到项目中所有直接写 SQL/ORM 的地方
- 标注哪些属于"数据访问"，哪些属于"业务逻辑"
- 评估：这些能抽成 Repository 接口吗？

### 作业 2：改造一个小模块（1小时）
- 选一个不超过 200 行的模块
- 抽取 Repository 接口
- 编写单元测试（Mock Repository）
- 对比改造前后的可测试性

### 作业 3：画一张你自己的项目的 Repository 图（30分钟）
- 有哪些领域对象？
- 每个对象的读写操作是什么？
- 哪些操作需要事务？
- 哪些需要缓存？

---

## 📅 更新日志

- 2026-04-06 PM：新增《Repository 模式与数据访问层实战》
  - Repository 抽象接口设计（UserProfile / Item / BehaviorEvent）
  - 为什么用 dataclass 而非 ORM Model（领域对象 vs 数据表）
  - PostgreSQL + Redis 双实现对比（MySQL 实现 vs Redis 缓存实现）
  - 依赖注入容器（Flask/FastAPI 集成）
  - TypeScript NestJS + TypeORM 完整实现
  - Unit of Work 模式（原子操作、事务回滚）
  - 单元测试（Mock Repository，验证无 N+1）
  - 三大常见误区（业务逻辑混入 / 表对Repository / 全走ORM）
  - Repository 决策树 + 与已有知识关联图
