# CQRS 模式与读写分离实战

> Command Query Responsibility Segregation · 命令查询职责分离

---

## 一、什么是 CQRS？

**核心理念**：把"读操作"和"写操作"分开处理，各自优化。

| 操作类型 | 示例 | 特点 |
|---------|------|------|
| **Command（命令）** | 下单、点赞、收藏 | 写，修改状态 |
| **Query（查询）** | 获取推荐列表、查看商品 | 读，只读取数据 |

**为什么推荐系统需要 CQRS？**

```
推荐系统的读写压力极不对称：

读多写少：
- 首页推荐：每秒 10000+ 请求（读）
- 用户点击：每秒 1000 次（写）
比例 ~10:1

读写的需求完全不同：
- 写：需要严格的事务、数据一致性
- 读：需要高并发、低延迟、多维度聚合
```

---

## 二、 CQRS 的两种形态

### 形态一：简单读写分离（入门级）

```
┌─────────────┐      ┌──────────────┐
│   写操作     │  →   │   MySQL 主库  │
│  (INSERT)   │      └──────────────┘
└─────────────┘
                    ┌──────────────┐
┌─────────────┐  →  │  MySQL 从库  │
│   读操作     │      │  (只读副本)  │
│  (SELECT)   │      └──────────────┘
└─────────────┘
```

**适用场景**：中小型推荐系统，流量在万级 QPS 以下

### 形态二：完全 CQRS（进阶级）

```
┌──────────────────────────────────────────────────┐
│                    命令端 (Command)               │
│  ┌────────┐  ┌────────┐  ┌────────┐            │
│  │ 用户行为 │  │ 订单写入 │  │ 数据写入 │            │
│  │ 事件    │  │ 服务    │  │ 服务    │            │
│  └────┬───┘  └────┬───┘  └────┬───┘            │
│       └───────────┼───────────┘                 │
│                   ↓ 事件总线                       │
├──────────────────────────────────────────────────┤
│                  事件同步层                        │
│       MySQL ──binlog──→ Canal ──→ Kafka          │
├──────────────────────────────────────────────────┤
│                    查询端 (Query)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Redis    │  │ Elastic   │  │ ClickHouse│      │
│  │ (热数据)  │  │ Search    │  │ (分析查询) │      │
│  └──────────┘  │ (全文检索) │  └──────────┘      │
│                └──────────┘                      │
└──────────────────────────────────────────────────┘
```

**适用场景**：大型推荐系统，日活千万以上

---

## 三、代码实现

### Python 实现：简单读写分离

```python
# repositories/user_repo.py
from abc import ABC, abstractmethod
from typing import List, Optional
import pymysql

# =============================================
# 读写分离的 Repository 抽象
# =============================================
class UserRepository(ABC):
    """抽象出读写接口，调用方不关心是哪个库"""
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[dict]:
        pass
    
    @abstractmethod
    def list_by_tag(self, tag: str, limit: int = 20) -> List[dict]:
        pass
    
    @abstractmethod
    def save(self, user_data: dict) -> int:
        pass

# =============================================
# 写库实现（主库）
# =============================================
class MasterUserRepository(UserRepository):
    """写操作：连接主库，支持事务"""
    
    def __init__(self, host='master.db', port=3306):
        self.conn = pymysql.connect(
            host=host, port=port,
            user='app', password='xxx',
            database='recommend_db', charset='utf8mb4',
            autocommit=False  # 手动事务
        )
    
    def get_by_id(self, user_id: int) -> Optional[dict]:
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                "SELECT * FROM users WHERE id = %s", (user_id,)
            )
            return cur.fetchone()
    
    def list_by_tag(self, tag: str, limit: int = 20) -> List[dict]:
        # 读操作不应该走主库！
        raise NotImplementedError("读操作请使用 SlaveUserRepository")
    
    def save(self, user_data: dict) -> int:
        """写操作走主库，事务保护"""
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            try:
                cur.execute(
                    """INSERT INTO users (name, tags, preferences)
                       VALUES (%s, %s, %s)""",
                    (user_data['name'], user_data['tags'], user_data['preferences'])
                )
                self.conn.commit()
                return cur.lastrowid
            except Exception as e:
                self.conn.rollback()
                raise e

# =============================================
# 读库实现（从库）
# =============================================
class SlaveUserRepository(UserRepository):
    """读操作：连接从库，高并发"""
    
    def __init__(self, host='slave.db', port=3306):
        self.conn = pymysql.connect(
            host=host, port=port,
            user='app_readonly', password='xxx',
            database='recommend_db', charset='utf8mb4',
            autocommit=True
        )
    
    def get_by_id(self, user_id: int) -> Optional[dict]:
        """从从库读取，延迟稍高但吞吐量大"""
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                "SELECT * FROM users WHERE id = %s", (user_id,)
            )
            return cur.fetchone()
    
    def list_by_tag(self, tag: str, limit: int = 20) -> List[dict]:
        """复杂查询走从库，不影响主库写入"""
        with self.conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                """SELECT * FROM users 
                   WHERE JSON_CONTAINS(tags, %s)
                   LIMIT %s""",
                (f'"{tag}"', limit)
            )
            return cur.fetchall()
    
    def save(self, user_data: dict) -> int:
        raise NotImplementedError("写操作请使用 MasterUserRepository")

# =============================================
# 工厂模式：根据操作类型选择 Repository
# =============================================
class UserRepositoryFactory:
    """调用方不感知读写分离，工厂自动路由"""
    
    @staticmethod
    def get_repository(is_write: bool = False) -> UserRepository:
        if is_write:
            return MasterUserRepository()
        return SlaveUserRepository()
```

```python
# services/recommend_service.py
from repositories.user_repo import UserRepositoryFactory

class RecommendService:
    """推荐服务：读写分离自动路由"""
    
    def get_home_feed(self, user_id: int, page: int = 1, size: int = 20):
        """读：走从库，不影响写入性能"""
        repo = UserRepositoryFactory.get_repository(is_write=False)
        user = repo.get_by_id(user_id)
        
        # 模拟推荐逻辑
        return {
            'user_id': user_id,
            'feed': [f'item_{i}' for i in range(size)]
        }
    
    def update_user_profile(self, user_id: int, new_tag: str):
        """写：走主库，事务保护"""
        repo = UserRepositoryFactory.get_repository(is_write=True)
        repo.save({
            'name': 'updated',
            'tags': [new_tag],
            'preferences': {}
        })
        return {'status': 'ok'}
```

---

### TypeScript 实现：完全 CQRS

```typescript
// cqrs/commands/create-user.command.ts
// =============================================
// 命令端（Command）— 写操作
// =============================================
export interface CreateUserCommand {
  readonly type: 'CreateUser';
  readonly payload: {
    userId: string;
    name: string;
    tags: string[];
  };
}

export interface UpdatePreferencesCommand {
  readonly type: 'UpdatePreferences';
  readonly payload: {
    userId: string;
    preferences: Record<string, any>;
  };
}

export type Command = CreateUserCommand | UpdatePreferencesCommand;
```

```typescript
// cqrs/queries/user.query.ts
// =============================================
// 查询端（Query）— 读操作
// =============================================
export interface GetUserProfileQuery {
  readonly type: 'GetUserProfile';
  readonly payload: { userId: string };
}

export interface SearchUsersQuery {
  readonly type: 'SearchUsers';
  readonly payload: {
    keyword: string;
    page: number;
    pageSize: number;
  };
}

export type Query = GetUserProfileQuery | SearchUsersQuery;
```

```typescript
// cqrs/handlers/command-handler.ts
// =============================================
// 命令处理器（写路径）
// =============================================
import { Command } from '../commands/create-user.command';
import { UserEntity } from '../../domain/entities/user.entity';
import { EventBus } from '../../infrastructure/events/event-bus';

export class CommandHandler {
  constructor(
    private readonly userRepo: UserEntity,
    private readonly eventBus: EventBus,
  ) {}

  async handle(cmd: Command): Promise<void> {
    switch (cmd.type) {
      case 'CreateUser': {
        const user = UserEntity.create({
          id: cmd.payload.userId,
          name: cmd.payload.name,
          tags: cmd.payload.tags,
        });
        await this.userRepo.save(user);
        // 发布事件 → 触发读模型更新
        await this.eventBus.publish({
          type: 'UserCreated',
          payload: { userId: cmd.payload.userId, name: cmd.payload.name },
        });
        break;
      }
      case 'UpdatePreferences': {
        const user = await this.userRepo.findById(cmd.payload.userId);
        user.updatePreferences(cmd.payload.preferences);
        await this.userRepo.save(user);
        await this.eventBus.publish({
          type: 'PreferencesUpdated',
          payload: { userId: cmd.payload.userId },
        });
        break;
      }
    }
  }
}
```

```typescript
// cqrs/handlers/query-handler.ts
// =============================================
// 查询处理器（读路径）— 直接读优化后的视图
// =============================================
import { Query } from '../queries/user.query';
import { Redis } from 'ioredis';
import { ElasticClient } from '../../infrastructure/search/elastic.client';

export class QueryHandler {
  constructor(
    private readonly redis: Redis,
    private readonly elastic: ElasticClient,
  ) {}

  async handle(query: Query): Promise<any> {
    switch (query.type) {
      case 'GetUserProfile': {
        // 读缓存（Redis）
        const cacheKey = `user:profile:${query.payload.userId}`;
        const cached = await this.redis.get(cacheKey);
        if (cached) return JSON.parse(cached);
        
        // 缓存未命中，查 ES（读模型已物化）
        const profile = await this.elastic.get('user_profiles', query.payload.userId);
        await this.redis.setex(cacheKey, 300, JSON.stringify(profile));  // 5分钟缓存
        return profile;
      }

      case 'SearchUsers': {
        // 复杂搜索走 ES
        const results = await this.elastic.search('user_profiles', {
          query: {
            multi_match: {
              query: query.payload.keyword,
              fields: ['name', 'tags', 'bio'],
            },
          },
          from: (query.payload.page - 1) * query.payload.pageSize,
          size: query.payload.pageSize,
        });
        return results;
      }
    }
  }
}
```

```typescript
// cqrs/index.ts
// =============================================
// CQRS 入口：命令/查询路由
// =============================================
import { CommandHandler } from './handlers/command-handler';
import { QueryHandler } from './handlers/query-handler';
import { Command } from './commands/create-user.command';
import { Query } from './queries/user.query';

export class CqrsBus {
  constructor(
    private readonly cmdHandler: CommandHandler,
    private readonly queryHandler: QueryHandler,
  ) {}

  async dispatchCommand(cmd: Command): Promise<void> {
    await this.cmdHandler.handle(cmd);
  }

  async executeQuery<T>(query: Query): Promise<T> {
    return this.queryHandler.handle(query) as Promise<T>;
  }
}

// 使用示例
// const bus = new CqrsBus(cmdHandler, queryHandler);
//
// // 写操作
// await bus.dispatchCommand({
//   type: 'CreateUser',
//   payload: { userId: 'u123', name: '张三', tags: ['音乐', '技术'] }
// });
//
// // 读操作（走不同路径，Redis缓存）
// const profile = await bus.executeQuery({
//   type: 'GetUserProfile',
//   payload: { userId: 'u123' }
// });
```

---

## 四、推荐系统中的 CQRS 实战场景

### 场景一：用户行为事件处理

```
用户行为（点击/收藏/购买）
  ↓
Command 路径：写入 MySQL + 发布事件
  ↓
事件消费者：更新用户特征向量
  ↓
更新 Redis / Embedding 服务
  ↓
Query 路径：推荐召回时直接读 Redis（毫秒级）
```

### 场景二：推荐结果缓存

| 场景 | 读路径 | 缓存策略 |
|------|--------|---------|
| 首页推荐 | Redis GET | 5-30分钟 TTL |
| 搜索结果 | Elasticsearch | 实时更新 |
| 用户画像 | Redis Hash | 行为触发更新 |
| 热门榜单 | Redis Sorted Set | 定时刷新 |

### 场景三：数据分析与实时推荐分离

```
写入路径：ClickHouse（分析）
读取路径：Elasticsearch（实时检索）
        Redis（高热数据）
        MySQL 从库（兜底）
```

---

## 五、CQRS 在面试中的表达

当面试官问"你们推荐系统怎么做读写分离"时：

> **参考答案**：
> 
> 我们采用了 CQRS 架构，将读写彻底分离。写路径是用户行为事件进入 Kafka，我们消费事件去更新 MySQL 主库，然后通过 Canal 监听 binlog 把变更同步到 Elasticsearch 和 Redis。读路径则直接从 Redis 读热数据（推荐结果缓存），Redis 未命中时读 ES（复杂检索）。这种设计让写库完全不受读流量影响，读服务可以独立扩缩容。我们在双十一大促期间，读 QPS 从 5000 扩到 50000，但写库完全没压力。

---

## 六、常见误区

| 误区 | 正确做法 |
|------|---------|
| "读写分离就是加从库" | 从库只适合简单查询，复杂join另想办法 |
| "缓存一致性好难" | 先接受最终一致，热点数据用写穿透 |
| "CQRS 太复杂了" | 从读写分离开始，逐步演进到完整CQRS |
| "ES 能解决所有读问题" | ES 的写入延迟高，不适合实时性要求极高的场景 |
| "缓存越多越好" | 多级缓存带来一致性维护成本，按热度分级 |

---

## 七、适合你的学习顺序

```
1. 先理解读写分离概念（本文）
2. 部署一套 MySQL 主从（本地实验）
3. 写一个 Repository 抽象类（Python/TS）
4. 用 Redis 做读缓存（推荐结果缓存）
5. 了解 Canal + Kafka 事件同步（进阶）
6. 研究 Elasticsearch 读写分离（进阶）
```
