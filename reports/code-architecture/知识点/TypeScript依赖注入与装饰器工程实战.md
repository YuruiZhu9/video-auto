# TypeScript 依赖注入与装饰器工程实战
## —— NestJS 从"会用"到"精通"最后一公里

---

## 🎯 核心问题

NestJS 的 `@Injectable()` 装饰器背后发生了什么？
为什么加了一个 `@Inject(forwardRef(() => BService))` 就解决了循环依赖？
自定义装饰器如何让控制器代码减少 70%？

本文从**原理层**到**工程层**，彻底讲透 TypeScript 装饰器 + 依赖注入的完整体系。

---

## 一、TypeScript 装饰器：底层原理

### 1.1 装饰器是什么？

TypeScript 装饰器（Decorator）是**函数**，在类、方法、属性、参数被定义时执行，用于**增强或修改其行为**。需要启用 `experimentalDecorators: true` 编译选项。

```
decorator执行时机：
    类定义 → 装饰器立即执行（返回一个新类或原类增强）
    方法定义 → 装饰器在方法定义时执行
    属性定义 → 装饰器在属性定义时执行
```

### 1.2 五种装饰器速查表

```typescript
// ═══════════════════════════════════════════════════════
// 装饰器签名（TypeScript 内置签名）
// ═══════════════════════════════════════════════════════

// 1. 类装饰器
type ClassDecorator = (
  target: Function  // 被装饰的类本身
) => Function | void;

// 2. 方法装饰器
type MethodDecorator = (
  target: Object,           // 类的原型（prototype）
  propertyKey: string | symbol,
  descriptor: TypedPropertyDescriptor<T>
) => TypedPropertyDescriptor<T> | void;

// 3. 属性装饰器
type PropertyDecorator = (
  target: Object,
  propertyKey: string | symbol
) => void;

// 4. 参数装饰器
type ParameterDecorator = (
  target: Object,
  propertyKey: string | symbol,
  parameterIndex: number
) => void;

// 5. 访问器装饰器（get/set）
type AccessorDecorator = (
  target: Object,
  propertyKey: string | symbol,
  descriptor: PropertyDescriptor
) => PropertyDescriptor | void;
```

### 1.3 装饰器执行顺序（从内到外，从上到下）

```typescript
// 执行顺序口诀：参数 → 属性 → 方法/访问器 → 类
// 同类型装饰器：从左到右执行

function f1(_: any, __: any, descriptor: PropertyDescriptor) {
  console.log("方法装饰器 - A");
  return descriptor;
}
function f2(_: any, __: any, descriptor: PropertyDescriptor) {
  console.log("方法装饰器 - B");
  return descriptor;
}

class Example {
  @f1
  @f2
  method() {}  // 打印顺序：方法装饰器 - B → 方法装饰器 - A
}
```

### 1.4 元数据反射系统（反射 API 核心）

NestJS 依赖注入的底层依赖：`reflect-metadata` 提供了一个全局反射对象。

```typescript
import "reflect-metadata";

// ═══════════════════════════════════════════════════════
// 核心三个 API
// ═══════════════════════════════════════════════════════

// 1. 定义元数据（通常用 Symbol 做 key）
Reflect.defineMetadata(
  "design:paramtypes",           // 元数据 key
  [String, Number],              // 装饰器关联的值
  MyClass.prototype,             // 附加到哪个对象（原型）
  "methodName"                   // 可选：哪个属性
);

// 2. 读取元数据
const types = Reflect.getMetadata("design:paramtypes", MyClass.prototype, "methodName");
// → [String, Number]

// 3. 检查元数据是否存在
const hasMetadata = Reflect.hasMetadata("design:paramtypes", MyClass.prototype);
```

> **核心原理**：NestJS 在 `@Injectable()` 装饰器内部调用 `Reflect.defineMetadata("design:paramtypes", [...], Target.prototype)`，把每个构造参数的预期类型记录下来。`Injector` 在实例化时读取这些元数据，找到对应的 Provider，自动完成注入。

---

## 二、依赖注入：从前端手动到框架自动化

### 2.1 反例：手动依赖管理（紧耦合 + 难测试）

```typescript
// ❌ 反例：服务自己 new 出依赖，耦合到具体实现
class UserService {
  private db = new MySQLDatabase();    // 写死了！
  private cache = new RedisCache();    // 没法 Mock！
  private logger = new ConsoleLogger(); // 没法换实现！

  async findById(id: string) {
    if (this.cache.has(id)) {
      return this.cache.get(id);
    }
    const user = await this.db.query("SELECT * FROM users WHERE id = ?", [id]);
    this.cache.set(id, user);
    return user;
  }
}

// 问题：
// 1. 换 MySQL → PostgreSQL → 必须改 UserService 源码
// 2. 写单元测试 → 无法 mock db/cache → 必须连真实数据库
// 3. 不同环境（测试/生产）→ 无法切换依赖
```

### 2.2 正例：依赖注入（通过构造函数传入）

```typescript
// ✅ 正例：依赖通过构造函数注入，不关心谁提供
interface IDatabase {
  query(sql: string, params: any[]): Promise<any>;
}
interface ICache {
  has(key: string): boolean;
  get<T>(key: string): T | undefined;
  set<T>(key: string, value: T): void;
}
interface ILogger {
  info(msg: string): void;
}

// ═══════════════════════════════════════════════════════
// 具体实现（可替换）
// ═══════════════════════════════════════════════════════
class MySQLDatabase implements IDatabase {
  async query(sql: string, params: any[]): Promise<any> {
    // 真实 MySQL 连接
    return [];
  }
}

class PostgresDatabase implements IDatabase {
  async query(sql: string, params: any[]): Promise<any> {
    // PostgreSQL 连接
    return [];
  }
}

class RedisCache implements ICache {
  private store = new Map<string, any>();
  has(key: string): boolean { return this.store.has(key); }
  get<T>(key: string): T | undefined { return this.store.get(key); }
  set<T>(key: string, value: T): void { this.store.set(key, value); }
}

class ConsoleLogger implements ILogger {
  info(msg: string): void { console.log(`[INFO] ${msg}`); }
}

// ═══════════════════════════════════════════════════════
// 服务层：只声明需要什么，不关心谁提供
// ═══════════════════════════════════════════════════════
class UserService {
  constructor(
    private db: IDatabase,    // 接口类型，框架负责找实现
    private cache: ICache,
    private logger: ILogger,
  ) {}

  async findById(id: string) {
    this.logger.info(`Finding user: ${id}`);
    if (this.cache.has(id)) {
      this.logger.info("Cache hit");
      return this.cache.get(id);
    }
    const user = await this.db.query("SELECT * FROM users WHERE id = ?", [id]);
    this.cache.set(id, user);
    return user;
  }
}

// ═══════════════════════════════════════════════════════
// 手动 DI 容器（简化版，理解原理）
// ═══════════════════════════════════════════════════════
class SimpleDIContainer {
  private providers = new Map<string, any>();

  register<T>(token: string, instance: T): void {
    this.providers.set(token, instance);
  }

  get<T>(token: string): T {
    const instance = this.providers.get(token);
    if (!instance) throw new Error(`Provider not found: ${token}`);
    return instance;
  }

  // 自动注入：根据构造函数的参数类型找 Provider
  create<T>(Ctor: new (...args: any[]) => T): T {
    // 读取类构造函数的参数类型（通过 reflect-metadata）
    const paramTypes = Reflect.getMetadata("design:paramtypes", Ctor) || [];
    const deps = paramTypes.map((type: any) => this.get(type.name));
    return new Ctor(...deps);
  }
}

// 使用
const container = new SimpleDIContainer();
container.register("IDatabase", new MySQLDatabase());      // 注册实现
container.register("ICache", new RedisCache());
container.register("ILogger", new ConsoleLogger());

const userService = container.create(UserService);           // 自动注入！
// 等价于：new UserService(new MySQLDatabase(), new RedisCache(), new ConsoleLogger())
```

### 2.3 NestJS Provider 完整分类

```typescript
// ═══════════════════════════════════════════════════════
// NestJS Provider 六大类型
// ═══════════════════════════════════════════════════════

// 1️⃣ 值提供（VALUE）：直接提供一个实例
{
  provide: 'CONFIG',        // Token
  useValue: { port: 3000, env: 'production' }  // 固定值
}

// 2️⃣ 类提供（CLASS）：最常用，Token = 类本身
{
  provide: UserService,     // Token = 类
  useClass: UserService     // 实现 = 类
}
// 简写：UserService  ← NestJS 自动展开为上面格式

// 3️⃣ 工厂提供（FACTORY）：动态计算，适合需要参数的 Provider
{
  provide: 'DB_CONNECTION',
  useFactory: (config: ConfigService) => {   // 可以注入其他 Provider
    return createConnection(config.databaseUrl);
  },
  inject: [ConfigService],                   // 声明依赖
}

// 4️⃣ 别名（ALIAS）：给已有 Provider 起别名
{
  provide: 'CACHE_SERVICE',
  useExisting: RedisCacheService,
}

// 5️⃣ 异步提供（ASYNC）：异步初始化
{
  provide: 'DB',
  useFactory: async (config: ConfigService) => {
    const db = await createDatabase(config.url);
    return db;
  },
  inject: [ConfigService],
}

// 6️⃣ 组合提供（多个实例满足一个接口）
{
  provide: 'IRecallStrategy',
  useClass: EmbeddingRecallStrategy,   // 可换成 ItemCFRecallStrategy
}
```

---

## 三、NestJS 依赖注入进阶：循环依赖、作用域、forwardRef

### 3.1 循环依赖：两个服务互相依赖

```typescript
// ❌ 循环依赖错误示例
@Injectable()
class AService {
  constructor(private bService: BService) {}  // 需要 BService
}

@Injectable()
class BService {
  constructor(private aService: AService) {}  // 需要 AService
  // 问题：A 需要 B，B 需要 A → 死锁！
}

// 在模块注册：
@Module({
  providers: [AService, BService],   // ❌ 启动时报错
})
```

### 3.2 解决方案一：forwardRef（推荐临时修复）

```typescript
// ✅ 使用 forwardRef 打破循环（告诉 NestJS 延迟解析）
import { forwardRef } from '@nestjs/common';

@Injectable()
class AService {
  constructor(
    @Inject(forwardRef(() => BService))
    private bService: BService,
  ) {}
}

@Injectable()
class BService {
  constructor(
    @Inject(forwardRef(() => AService))
    private aService: AService,
  ) {}
}

// ⚠️ 注意：forwardRef 是技术债的信号！强烈建议重构掉
```

### 3.3 解决方案二：重构——提取中间层（推荐）

```typescript
// ✅ 根本解法：将共享逻辑提取到第三个服务
@Injectable()
class SharedService {    // 独立服务，不依赖 A/B
  doSomethingShared() {
    return "shared logic";
  }
}

@Injectable()
class AService {
  constructor(private shared: SharedService) {}  // 只依赖 Shared
}

@Injectable()
class BService {
  constructor(
    private shared: SharedService,
    private aService: AService,    // 正常注入，无循环
  ) {}
}

// 设计原则：依赖关系应该是有向无环图（DAG），forwardRef 是打破循环的临时补丁
```

### 3.4 Provider 作用域（重要！）

```typescript
// ═══════════════════════════════════════════════════════
// 三种作用域：决定 Provider 的生命周期
// ═══════════════════════════════════════════════════════

// 1. DEFAULT（单例，默认）：整个应用共享一个实例（性能最优）
@Injectable({ scope: Scope.DEFAULT })
class UserService { }    // ✅ 推荐，99% 的场景

// 2. REQUEST：每个 HTTP 请求创建一个实例，请求结束后销毁
@Injectable({ scope: Scope.REQUEST })
class RequestContextService {
  constructor(private readonly requestId: string) {
    // 每个请求有独立的 requestId
    console.log(`New request: ${requestId}`);
  }
}

// 用法：从 NestJS 内置 REQUEST 对象获取
@Get(':id')
getUser(@Req() req: Request) {
  // req.requestId 是 RequestScope Provider 注入的
}

// 3. TRANSIENT：每次注入创建一个新实例（每次都 new）
@Injectable({ scope: Scope.TRANSIENT })
class Logger {
  constructor() { this.id = Math.random(); }
  log(msg: string) { console.log(`[${this.id}] ${msg}`); }
}

// ═══════════════════════════════════════════════════════
// 作用域选择决策树
// ═══════════════════════════════════════════════════════
什么时候用 REQUEST 作用域？
├─ 需要存储请求级别的状态？→ 是 → REQUEST
├─ 需要每个请求独立的数据库连接？→ 是 → REQUEST
└─ 只是普通业务逻辑？→ 否 → DEFAULT（单例）

什么时候用 TRANSIENT 作用域？
├─ 这个服务不应该在多个地方共享状态？→ 是 → TRANSIENT
└─ 一般业务服务？→ 否 → DEFAULT
```

---

## 四、自定义装饰器：让代码减少 70%

### 4.1 参数装饰器：自动获取当前用户

```typescript
// ═══════════════════════════════════════════════════════
// 反例：在每个 Controller 方法里手动解析
// ═══════════════════════════════════════════════════════
@Post(':id/follow')
followUser(@Req() req: Request, @Param('id') targetId: string) {
  const userId = req.user?.id;      // 重复 100 遍
  if (!userId) throw new UnauthorizedException();
  return this.userService.follow(userId, targetId);
}

@Delete(':id/follow')
unfollowUser(@Req() req: Request, @Param('id') targetId: string) {
  const userId = req.user?.id;      // 又重复一遍
  if (!userId) throw new UnauthorizedException();
  return this.userService.unfollow(userId, targetId);
}
```

```typescript
// ═══════════════════════════════════════════════════════
// 正例：自定义 CurrentUser 装饰器（一行代替 5 行）
// ═══════════════════════════════════════════════════════

import { createParamDecorator, ExecutionContext } from '@nestjs/common';

// ═══════════════════════════════════════════════════════
// 实现：createParamDecorator 自动生成参数装饰器
// ═══════════════════════════════════════════════════════
export const CurrentUser = createParamDecorator(
  (data: string | undefined, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    const user = request.user;       // Passport 设置的

    // 无装饰器参数 → 返回整个 user 对象
    // 有参数 → 返回 user[data]（如 user.id）
    return data ? user?.[data] : user;
  },
);

// ═══════════════════════════════════════════════════════
// 简化后的 Controller：干净得像伪代码
// ═══════════════════════════════════════════════════════
@Post(':id/follow')
followUser(
  @CurrentUser('id') myId: string,    // 自动提取
  @Param('id') targetId: string,
) {
  return this.userService.follow(myId, targetId);
}

@Delete(':id/follow')
unfollowUser(
  @CurrentUser('id') myId: string,
  @Param('id') targetId: string,
) {
  return this.userService.unfollow(myId, targetId);
}
// 代码量：每方法减少 5 行！复用率 100%
```

### 4.2 方法装饰器：自动鉴权

```typescript
// ═══════════════════════════════════════════════════════
// 反例：每个方法都写鉴权逻辑
// ═══════════════════════════════════════════════════════
@Post('recommend')
async recommend(@Req() req: Request) {
  if (!req.user?.roles?.includes('algorithm_engineer')) {
    throw new ForbiddenException('需要算法工程师权限');
  }
  // 业务逻辑...
}
```

```typescript
// ═══════════════════════════════════════════════════════
// 正例：@RequireRoles 装饰器
// ═══════════════════════════════════════════════════════

import { SetMetadata } from '@nestjs/common';

// 定义元数据 key（避免字符串硬编码）
export const ROLES_KEY = 'roles';
export const RequireRoles = (...roles: string[]) => SetMetadata(ROLES_KEY, roles);

// 守卫实现（读取元数据，判断权限）
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    // 读取控制器/方法上的 @RequireRoles 元数据
    const requiredRoles = this.reflector.getAllAndOverride<string[]>(
      ROLES_KEY,
      [context.getHandler(), context.getClass()],  // 方法优先，然后类
    );

    if (!requiredRoles) return true;  // 没声明要求 → 放行

    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.some(role => user.roles?.includes(role));
  }
}

// 使用（装饰器语法）
@Controller('admin')
@RequireRoles('admin')    // 类级别：整个控制器需要 admin
export class AdminController {
  @Get('metrics')
  @RequireRoles('algorithm_engineer')  // 方法级别：单独要求
  getMetrics(@CurrentUser('id') userId: string) { }

  @Post('model/upload')
  @RequireRoles('admin')    // admin 专属
  uploadModel(@CurrentUser('id') userId: string) { }
}
```

### 4.3 方法装饰器：自动记录日志

```typescript
// ═══════════════════════════════════════════════════════
// 实现一个 @LogPerformance 装饰器，自动记录方法耗时
// ═══════════════════════════════════════════════════════

import { Logger as NestLogger } from '@nestjs/common';

export function LogPerformance(tag?: string) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor,
  ) {
    const originalMethod = descriptor.value;
    const logger = new NestLogger(tag || target.constructor.name);

    descriptor.value = function (...args: any[]) {
      const start = Date.now();
      const methodName = propertyKey;

      logger.log(`▶ ${methodName} 开始，参数: ${JSON.stringify(args)}`);

      const result = originalMethod.apply(this, args);

      // 如果返回 Promise
      if (result instanceof Promise) {
        return result
          .then(res => {
            const elapsed = Date.now() - start;
            logger.log(`✓ ${methodName} 完成，耗时: ${elapsed}ms`);
            return res;
          })
          .catch(err => {
            const elapsed = Date.now() - start;
            logger.error(`✗ ${methodName} 失败，耗时: ${elapsed}ms`, err.stack);
            throw err;
          });
      }

      // 同步方法
      const elapsed = Date.now() - start;
      logger.log(`✓ ${methodName} 完成，耗时: ${elapsed}ms`);
      return result;
    };

    return descriptor;
  };
}

// 使用（一行装饰器，全链路耗时自动记录）
@Injectable()
class RecallService {
  @LogPerformance('召回层')
  async generateCandidates(userId: string, count: number): Promise<string[]> {
    // 业务逻辑（自动记录耗时）
    return this.itemCFRecall.findSimilars(userId, count);
  }

  @LogPerformance('排序层')
  async rank(candidates: string[]): Promise<RankingResult> {
    // 业务逻辑（自动记录耗时）
    return this.model.predict(candidates);
  }
}
```

### 4.4 类装饰器 + 元编程：自动注册路由

```typescript
// ═══════════════════════════════════════════════════════
// 场景：推荐系统有大量相似的 CRUD 接口
// 用类装饰器 + 元编程自动批量生成路由
// ═══════════════════════════════════════════════════════

// 定义路由元数据
export const ROUTES_KEY = 'crud_routes';

interface RouteDefinition {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  description: string;
}

export const CrudRoutes = (routes: RouteDefinition[]) =>
  SetMetadata(ROUTES_KEY, routes);

// ═══════════════════════════════════════════════════════
// 自动生成 Controller 的类装饰器
// ═══════════════════════════════════════════════════════
export function AutoCrudController(resource: string) {
  return function <T extends { new (...args: any[]): any }>(Target: T) {
    return class extends Target {
      constructor(...args: any[]) {
        super(...args);

        // 通过反射获取定义的路由元数据
        const routes: RouteDefinition[] =
          Reflect.getMetadata(ROUTES_KEY, Target.prototype) || [];

        // 自动打印路由映射（运行时日志）
        const logger = new NestLogger(Target.name);
        routes.forEach(({ method, path, description }) => {
          logger.log(`${method} /${resource}${path} → ${description}`);
        });
      }
    };
  };
}

// 使用（声明式路由定义）
@AutoCrudController('items')
class ItemsController {
  constructor(private itemsService: ItemsService) {}

  @Get()                     // GET /items
  @CrudRoutes([{ method: 'GET', path: '', description: '查询物品列表' }])
  findAll() { return this.itemsService.findAll(); }

  @Get(':id')               // GET /items/:id
  @CrudRoutes([{ method: 'GET', path: '/:id', description: '查询单个物品' }])
  findOne(@Param('id') id: string) { return this.itemsService.findOne(id); }

  @Post()                   // POST /items
  @CrudRoutes([{ method: 'POST', path: '', description: '创建物品' }])
  create(@Body() dto: CreateItemDto) { return this.itemsService.create(dto); }

  @Delete(':id')           // DELETE /items/:id
  @CrudRoutes([{ method: 'DELETE', path: '/:id', description: '删除物品' }])
  remove(@Param('id') id: string) { return this.itemsService.remove(id); }
}
```

---

## 五、依赖注入在推荐系统中的工程应用

### 5.1 推荐引擎 DI 架构（完整示例）

```typescript
// ═══════════════════════════════════════════════════════
// 推荐引擎 DI 完整架构
// 展示：策略模式 + 依赖注入 + NestJS Provider 完整代码
// ═══════════════════════════════════════════════════════

// --- 端口定义（Interfaces）---
export interface IRecallStrategy {
  name: string;
  recall(userId: string, count: number): Promise<string[]>;
}

export interface IRankingService {
  rank(itemIds: string[], userId: string): Promise<RankingResult>;
}

export interface ICacheService {
  get<T>(key: string): Promise<T | null>;
  set(key: string, value: any, ttlSeconds: number): Promise<void>;
}

// --- 召回策略实现（可替换）---
@Injectable()
class ItemCFRecall implements IRecallStrategy {
  name = 'ItemCF';

  async recall(userId: string, count: number): Promise<string[]> {
    // ItemCF 召回逻辑
    return this.simMatrix.getSimilars(userId, count);
  }
}

@Injectable()
class EmbeddingRecall implements IRecallStrategy {
  name = 'Embedding';

  async recall(userId: string, count: number): Promise<string[]> {
    // Embedding 向量召回逻辑
    return this.milvusService.search(userId, count);
  }
}

@Injectable()
class HotRecall implements IRecallStrategy {
  name = 'Hot';

  async recall(userId: string, count: number): Promise<string[]> {
    return this.redisService.zrevrange(`hot:global`, 0, count - 1);
  }
}

// --- 召回引擎（编排所有策略，策略可热插拔）---
@Injectable()
class RecallEngine {
  // 通过构造器注入，不需要知道具体策略实现
  constructor(
    private strategies: IRecallStrategy[],   // 注入所有实现
    private cache: ICacheService,
  ) {}

  async recall(userId: string, count: number): Promise<string[]> {
    // 1. 先查缓存
    const cacheKey = `recall:${userId}:${count}`;
    const cached = await this.cache.get<string[]>(cacheKey);
    if (cached) return cached;

    // 2. 并行执行所有召回策略
    const results = await Promise.all(
      this.strategies.map(s => s.recall(userId, count)),
    );

    // 3. 合并去重
    const merged = [...new Set(results.flat())];
    await this.cache.set(cacheKey, merged, 300); // 5min TTL

    return merged;
  }
}

// --- 模块注册（关键：如何使用 Token 精确控制）---
@Module({
  providers: [
    // 策略注入：使用 Token = 接口类型（重要！）
    { provide: 'IRecallStrategy', useClass: ItemCFRecall },
    { provide: 'IRecallStrategy', useClass: EmbeddingRecall },
    { provide: 'IRecallStrategy', useClass: HotRecall },

    // 服务注入
    { provide: IRankingService, useClass: RankingService },
    { provide: ICacheService, useClass: RedisCacheService },

    // 引擎注入（自动注入 IRecallStrategy[] 数组所有实例）
    RecallEngine,
  ],
})
export class RecommendationModule {}

// --- Controller 使用 ---
@Controller('recommend')
export class RecommendController {
  constructor(private recallEngine: RecallEngine) {}

  @Get('home')
  async getHomeRecommend(@CurrentUser('id') userId: string) {
    // 引擎内部已自动编排所有召回策略
    return this.recallEngine.recall(userId, 100);
  }
}
```

### 5.2 多环境配置注入（生产 vs 测试切换）

```typescript
// ═══════════════════════════════════════════════════════
// 工厂 Provider：根据环境切换实现
// ═══════════════════════════════════════════════════════

@Module({
  providers: [
    // 工厂模式：开发环境用 Mock，线上用真实服务
    {
      provide: 'IDatabase',
      useFactory: (config: ConfigService): IDatabase => {
        if (config.environment === 'development') {
          console.log('[DI] Using SQLite mock database');
          return new SQLiteDatabase();        // 轻量测试
        }
        console.log('[DI] Using PostgreSQL production database');
        return new PostgresDatabase(config.pgUrl);  // 真实生产
      },
      inject: [ConfigService],                 // 可以注入其他 Provider
    },

    // 异步初始化：等待数据库连接建立后才创建 Provider
    {
      provide: 'REDIS_CLIENT',
      useFactory: async (): Promise<Redis> => {
        const client = createRedisClient();
        await client.connect();
        return client;
      },
    },
  ],
})
export class DatabaseModule {}
```

---

## 六、常见误区与避坑指南

### 误区一：在 Service 构造函数里直接 new 对象

```typescript
// ❌ 错误：在构造函数里创建依赖
@Injectable()
class RecommendationService {
  private cache = new RedisCacheService();  // 应该注入，不应该 new
}

// ✅ 正确：通过依赖注入
@Injectable()
class RecommendationService {
  constructor(private cache: ICacheService) {}  // 由 NestJS 注入
}
```

### 误区二：把所有 Provider 都注册成单例

```typescript
// ❌ 错误：每个请求都新建昂贵的 DB 连接
@Injectable({ scope: Scope.DEFAULT })
class ExpensiveService {
  constructor() { this.connection = createExpensiveConnection(); }
}

// ✅ 正确：昂贵资源应该用 REQUEST 作用域或单例连接池
@Injectable({ scope: Scope.DEFAULT })
class EfficientService {
  constructor(private dbPool: DbPool) {}  // 复用连接池
}
```

### 误区三：滥用 forwardRef 回避循环依赖

```typescript
// ❌ 错误：长期用 forwardRef 掩盖架构问题
@Injectable()
class UserService {
  constructor(
    @Inject(forwardRef(() => OrderService))
    private orderService: OrderService,  // 循环依赖被掩盖了
  ) {}
}

// ✅ 正确：重构提取 SharedService 打破循环
@Injectable()
class SharedService {
  // 两个服务都需要的公共逻辑放这里
}

@Injectable()
class UserService {
  constructor(private shared: SharedService) {}
}

@Injectable()
class OrderService {
  constructor(private shared: SharedService) {}
}
```

### 误区四：接口无法作为 DI Token

```typescript
// ❌ 错误：TypeScript 接口在运行时被擦除（interface → 无类型信息）
// NestJS 读取 "design:paramtypes" 元数据时，interface 找不到类型名
@Injectable()
class MyService {
  constructor(private strategy: IRecallStrategy) {}  // 运行时出错！
}

// ✅ 正确：使用字符串 Token 或 Symbol Token
// 方式一：字符串 Token（推荐，简单明确）
{ provide: 'IRecallStrategy', useClass: EmbeddingRecallStrategy }

// 方式二：Symbol Token（推荐，无魔法字符串）
export const RECALL_STRATEGY = Symbol('IRecallStrategy');
{ provide: RECALL_STRATEGY, useClass: EmbeddingRecallStrategy }

// 方式三：直接用类本身作为 Token
{ provide: UserService, useClass: UserServiceImpl }  // NestJS 自动展开
```

### 误区五：Provider 循环注入没有处理

```typescript
// ❌ 错误：两个服务互相注入，模块启动报错
// a.service.ts
@Injectable()
export class AService {
  constructor(private bService: BService) {}
}

// b.service.ts
@Injectable()
export class BService {
  constructor(private aService: AService) {}
}

// ⚠️ 现象：NestJS 启动时报 "Circular dependency" 错误
// 🔍 排查：用 `npm run start:debug` 看完整的依赖图
// ✅ 修复：将共享逻辑提取到 SharedService
```

---

## 七、适用场景速查表

| 场景 | 用什么 | 为什么 |
|------|--------|--------|
| 推荐引擎多路召回 | `IRecallStrategy[]` 数组注入 | 并行注入所有策略，策略可热插拔 |
| 数据库连接（dev/prod） | 工厂 Provider | 根据环境动态选择实现 |
| 异步初始化（等待连接池就绪） | 异步 Provider | 连接建立前不创建 |
| 每个请求独立的请求 ID | `Scope.REQUEST` | 请求结束即销毁 |
| 两个服务互相依赖 | 提取 SharedService | 打破循环依赖 |
| 临时打破循环 | `forwardRef` | 短期待修复，不要长期用 |
| 当前登录用户 | `@CurrentUser` 自定义装饰器 | 减少 Controller 重复代码 |
| 方法级鉴权 | `@RequireRoles` + Guard | 声明式鉴权，业务逻辑与安全逻辑分离 |
| 自动记录耗时 | `@LogPerformance` 方法装饰器 | 无侵入添加日志 |

---

## 八、推荐系统 DI 最佳实践总结

```
依赖注入最佳实践检查清单：
════════════════════════════════════════════════════════
□ 所有外部依赖（DB/Redis/模型推理）都是接口，不直接依赖实现
□ 注入点只声明需要什么（接口），模块注册决定怎么提供
□ 推荐引擎中的策略（如多路召回）通过数组注入，自动收集所有实现
□ 避免循环依赖：依赖图是有向无环图（DAG）
□ forwardRef 只用于临时修复，长期用必须重构
□ Scope.REQUEST 只用于必须请求隔离的状态（99% 用默认单例）
□ 自定义装饰器代替重复代码（鉴权、获取当前用户）
□ 生产环境通过 useFactory 切换实现（测试用 Mock，生产用真实）
□ 用 NestJS 内置 Logger 的 scope 字段标识来源（[UserService]）
□ 模块间的共享依赖用 SharedModule（全局模块）统一管理
```

---

## 九、生产检查清单（上线前 10 项）

1. **元数据反射开启**：`tsconfig.json` 中 `experimentalDecorators: true`
2. **装饰器顺序正确**：类装饰器 → 方法装饰器 → 参数装饰器
3. **无循环依赖**：用 `nestjs dependency graph` 检查依赖图
4. **接口不漏 Token**：所有接口注入都有对应的 Provider 注册
5. **Guard 执行顺序**：最内层 Guard 先执行，最外层最后失败
6. **Provider 作用域合理**：单例为主，REQUEST 为辅，不用 TRANSIENT
7. **异步 Provider 处理**：`app.useGlobalPipes()` 等应在所有异步模块加载后
8. **forwardRef 已重构**：不在代码中留下长期 forwardRef
9. **自定义装饰器有测试**：用 Jest 测试参数装饰器返回正确的值
10. **模块边界清晰**：Domain 层零外部依赖，Infrastructure 层只实现端口

---

## 十、学习路径与相关文档

| 阶段 | 文档 | 重点 |
|------|------|------|
| 入门 | [NestJS三层架构实战](..//代码案例/TypeScript案例/NestJS三层架构实战.md) | 看懂 @Injectable 基础用法 |
| 进阶 | 本文 | 装饰器原理、循环依赖、工厂 Provider |
| 应用 | [依赖注入实战](./依赖注入实战.md) | 配合 DI 容器完整代码 |
| 综合 | [NestJS分层架构](..//代码案例/TypeScript案例/NestJS分层架构.md) | 看真实项目的 DI 结构 |
| 补充 | [SOLID详解](./SOLID详解.md) | DI 背后的设计原则（DIP 依赖倒置）|

---

> **一句话总结**：依赖注入的本质是"谁