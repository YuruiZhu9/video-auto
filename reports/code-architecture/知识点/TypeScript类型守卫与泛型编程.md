# TypeScript 类型守卫与泛型编程

## 概念解释

### 什么是类型守卫（Type Guard）？

类型守卫是运行时检查，让你**在代码中确定一个变量的具体类型**，TypeScript 编译器据此在分支内缩小类型范围。

```typescript
// 问题：不知道 data 的具体类型
function process(data: string | number) {
    // TypeScript 不知道 data 是 string 还是 number
    // 不能盲目调用 .split() 或 .toFixed()
}
```

```typescript
// 解决：类型守卫 + 缩小范围
function process(data: string | number) {
    if (typeof data === "string") {
        // TypeScript 知道这里 data 是 string
        console.log(data.split(",")); // ✅
    } else {
        // TypeScript 知道这里 data 是 number
        console.log(data.toFixed(2)); // ✅
    }
}
```

### 什么是泛型？

泛型 = **类型的变量**。写一次代码，适配多种类型，同时保留类型安全。

```typescript
// 不用泛型：每种类型写一个函数
function firstOfString(arr: string[]): string { return arr[0]; }
function firstOfNumber(arr: number[]): number { return arr[0]; }

// 用泛型：一套代码，适用于所有类型
function first<T>(arr: T[]): T | undefined { return arr[0]; }
const s: string = first(["a", "b"]);      // T = string
const n: number = first([1, 2, 3]);       // T = number
```

---

## 代码示例

### 反例（坏味道）：any 类型泛滥

```typescript
// ❌ 用 any 逃避类型检查，运行时风险巨大
function getUserData(id: any): any {
    return fetch(`/api/users/${id}`).then(r => r.json());
}

const user: any = getUserData(123);
console.log(user.name.toUpperCase()); // 运行时可能报错：user.name 不存在
```

### 正例（改进后）：泛型 + 类型守卫

```typescript
// ✅ 泛型约束：返回类型由调用方决定
async function getUserData<T>(id: number): Promise<T> {
    const res = await fetch(`/api/users/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json() as T;
}

// 类型守卫：缩小 API 返回类型的范围
interface User { id: number; name: string; email: string; }
interface ApiResponse<T> { code: number; data: T; message?: string; }

function isSuccessResponse<T>(resp: unknown): resp is ApiResponse<T> {
    return (
        typeof resp === "object" &&
        resp !== null &&
        "code" in resp &&
        "data" in resp &&
        (resp as ApiResponse<T>).code === 0
    );
}

async function loadUser(id: number): Promise<User> {
    const raw = await getUserData<ApiResponse<User>>(id);
    if (!isSuccessResponse<User>(raw)) {
        throw new Error(raw.message ?? "Unknown error");
    }
    // TypeScript 确认 raw.data 是 User 类型
    return raw.data;
}
```

---

### 实战场景1：推荐结果联合类型

```typescript
// 推荐系统返回多种类型的 item，需要区分处理
type Article = { type: "article"; id: string; title: string; content: string; };
type Video = { type: "video"; id: string; url: string; duration: number; };
type Product = { type: "product"; id: string; name: string; price: number; };
type RecommendItem = Article | Video | Product;

// 类型守卫：缩小范围后再处理
function renderItem(item: RecommendItem): string {
    switch (item.type) {
        case "article":
            return `<h2>${item.title}</h2><p>${item.content}</p>`;
        case "video":
            return `<video src="${item.url}" />`;
        case "product":
            return `<div>${item.name} - ¥${item.price}</div>`;
        default:
            // 穷举保护：如果漏了某个类型，编译期报错
            const _exhaustive: never = item;
            throw new Error(`Unknown item type: ${_exhaustive}`);
    }
}

// 过滤特定类型
function getProducts(items: RecommendItem[]): Product[] {
    return items.filter((item): item is Product => item.type === "product");
}
```

---

### 实战场景2：泛型 Repository（数据库访问层）

```typescript
// 不用泛型：每个实体写一套 CRUD，重复代码爆炸
interface User { id: number; name: string; }
interface Article { id: number; title: string; authorId: number; }

class UserRepository {
    async findById(id: number): Promise<User | null> { /* ... */ }
    async findAll(): Promise<User[]> { /* ... */ }
    async save(user: User): Promise<void> { /* ... */ }
}
// 再写 ArticleRepository、ProductRepository... 代码爆炸

// ✅ 用泛型：一套 Repository 处理所有实体
interface Entity {
    id: number;
}

interface Repository<T extends Entity> {
    findById(id: number): Promise<T | null>;
    findAll(filter?: Partial<T>): Promise<T[]>;
    save(entity: T): Promise<T>;
    delete(id: number): Promise<void>;
}

class InMemoryRepository<T extends Entity> implements Repository<T> {
    private storage: Map<number, T> = new Map();
    private nextId = 1;

    async findById(id: number): Promise<T | null> {
        return this.storage.get(id) ?? null;
    }

    async findAll(filter?: Partial<T>): Promise<T[]> {
        let items = [...this.storage.values()];
        if (filter) {
            items = items.filter(item =>
                Object.entries(filter).every(([k, v]) => (item as any)[k] === v)
            );
        }
        return items;
    }

    async save(entity: T): Promise<T> {
        if ("id" in entity && entity.id > 0) {
            this.storage.set(entity.id, entity);
        } else {
            (entity as any).id = this.nextId++;
            this.storage.set((entity as any).id, entity);
        }
        return entity;
    }

    async delete(id: number): Promise<void> {
        this.storage.delete(id);
    }
}

// 使用：零重复代码
interface User extends Entity { name: string; email: string; }
interface Article extends Entity { title: string; authorId: number; }

const userRepo = new InMemoryRepository<User>();
const articleRepo = new InMemoryRepository<Article>();

await userRepo.save({ id: 0, name: "张三", email: "zhang@example.com" });
const articles = await articleRepo.findAll({ authorId: 1 }); // 自动类型推断
```

---

### 实战场景3：泛型工具函数

```typescript
// groupBy: 将数组按 key 分组
function groupBy<T, K extends string | number>(
    arr: T[],
    getKey: (item: T) => K
): Record<K, T[]> {
    return arr.reduce((groups, item) => {
        const key = getKey(item);
        (groups[key] ??= []).push(item);
        return groups;
    }, {} as Record<K, T[]>);
}

// 使用
interface ClickEvent { userId: string; itemId: string; timestamp: number; }
const events: ClickEvent[] = loadEvents();

const byUser = groupBy(events, e => e.userId);
// Record<string, ClickEvent[]> — 自动推断

const byItem = groupBy(events, e => e.itemId);
// Record<string, ClickEvent[]> — 自动推断

// 统计每个用户的点击数
const clickCounts = Object.fromEntries(
    Object.entries(byUser).map(([userId, userEvents]) => [userId, userEvents.length])
);
```

---

### 实战场景4：条件类型（Conditional Types）

```typescript
// 根据字段类型自动推断查询参数
type QueryParams<T> = {
    [K in keyof T as T[K] extends string | number | boolean
        ? K
        : never]: T[K];
};

// 从实体类自动生成"可查询字段"类型
interface Article {
    id: number;
    title: string;
    content: string;
    views: number;
    published: boolean;
    createdAt: Date;  // Date 不应作为查询参数
}

// 自动得到：{ id?: number; title?: string; views?: number; published?: boolean; }
type ArticleQuery = QueryParams<Article>;

function searchArticles(params: ArticleQuery): Promise<Article[]> {
    // 实现搜索逻辑
    return Promise.resolve([]);
}

// 用法：只允许传入 Article 中"可查询"的字段
searchArticles({ title: "TypeScript", views: 100 });
// searchArticles({ createdAt: new Date() }); // ❌ 编译错误
```

---

## 常见误区

- **误区1：用 `any` 逃避类型检查**。短期方便，长期埋雷。运行时 Bug 才是贵的。
- **误区2：泛型约束写太宽**。`<T extends object>` 太模糊，写 `<T extends Entity>` 或具体接口更安全。
- **误区3：类型守卫没有穷举所有分支**。switch/if 漏了某个 case 时，用 `never` 技巧保护。
- **误区4：泛型嵌套太深**。`Promise<Record<string, Array<Partial<T>>>>` 这种类型维护成本极高，需要拆分或加类型别名。
- **误区5：不写类型守卫，直接断言**。`(data as User).name` 绕过了检查，改为 `if (isUser(data))`。

---

## 适用场景

- **API 响应类型安全**：统一 API → 泛型 `ApiResponse<T>` → 类型守卫校验
- **Entity Repository 层**：一套 CRUD 代码处理所有数据模型
- **前端状态管理**：Redux/Zustand store 用泛型约束 action 和 state
- **工具函数**：groupBy、partition、unique 等通用数据操作
- **表单/列表组件**：React 组件用泛型复用 Table/Form 逻辑
- **推荐系统前端**：不同类型推荐卡片（文章/视频/商品）的统一渲染
