# 知识点 — MVC vs MVVM 深度对比

## 前置知识

在深入对比之前，先明确两个模式的演进历史：

```
MVC 诞生于 1970s（Smalltalk），最初用于桌面 GUI 应用
MVVM 诞生于 2005（微软 WPF），是 MVC 的变体，专注数据绑定
```

---

## 一、MVC 模式详解

### 数据流向

```
用户操作 → Controller 接收请求 → 调用 Model 处理业务 → Controller 选择 View → 返回给用户
```

**关键特点**：
- Controller 是"总指挥"，协调 Model 和 View
- Model 不知道 View 的存在（解耦）
- View 不知道 Model 的细节，只被动接收数据
- 通常 Controller 承担了部分业务逻辑

### 适用场景

| 场景 | 适合程度 | 说明 |
|------|---------|------|
| REST API 后端 | ⭐⭐⭐⭐⭐ | Controller = 路由，Model = 数据逻辑 |
| 服务器端渲染 Web | ⭐⭐⭐⭐ | Django、Flask 经典模式 |
| 小型前后端分离 | ⭐⭐⭐ | 简单应用足够 |
| 复杂前端应用 | ⭐ | 不适合，数据同步太繁琐 |

### TypeScript (Express) MVC 完整示例

```typescript
// ── Model ──────────────────────────────────────────────
import { Pool } from "pg";
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

interface Product {
  id: number;
  name: string;
  price: number;
  category: string;
}

class ProductModel {
  static async findAll(): Promise<Product[]> {
    const result = await pool.query("SELECT * FROM products");
    return result.rows;
  }

  static async findById(id: number): Promise<Product | null> {
    const result = await pool.query(
      "SELECT * FROM products WHERE id = $1", [id]
    );
    return result.rows[0] || null;
  }

  static async create(data: Omit<Product, "id">): Promise<Product> {
    const result = await pool.query(
      "INSERT INTO products (name, price, category) VALUES ($1,$2,$3) RETURNING *",
      [data.name, data.price, data.category]
    );
    return result.rows[0];
  }
}

// ── View ───────────────────────────────────────────────
// 在 API 架构中，View 就是返回的数据格式
// 用 DTO（Data Transfer Object）规范化输出
interface ProductView {
  id: number;
  name: string;
  price: number;
  category: string;
  price_display: string;  // 格式化价格
}

function toProductView(product: Product): ProductView {
  return {
    ...product,
    price_display: `¥${product.price.toFixed(2)}`,
  };
}

// ── Controller ─────────────────────────────────────────
import { Request, Response } from "express";

class ProductController {
  // GET /products
  async list(req: Request, res: Response) {
    const products = await ProductModel.findAll();
    res.json({
      code: 0,
      data: products.map(toProductView),
      total: products.length,
    });
  }

  // GET /products/:id
  async detail(req: Request, res: Response) {
    const id = parseInt(req.params.id, 10);
    const product = await ProductModel.findById(id);
    if (!product) {
      return res.status(404).json({ code: 404, message: "商品不存在" });
    }
    res.json({ code: 0, data: toProductView(product) });
  }

  // POST /products
  async create(req: Request, res: Response) {
    const { name, price, category } = req.body;
    if (!name || price === undefined) {
      return res.status(400).json({ code: 400, message: "缺少必要参数" });
    }
    const product = await ProductModel.create({ name, price, category });
    res.status(201).json({ code: 0, data: toProductView(product) });
  }
}

export const productController = new ProductController();
```

---

## 二、MVVM 模式详解

### 数据流向

```
用户操作 ↔ View（双向绑定） ↔ ViewModel（状态+逻辑） ↔ Model（数据）
                          ↓（自动同步）
                       View 自动更新
```

**关键特点**：
- **双向数据绑定**：View 的变化自动同步到 ViewModel，反之亦然
- ViewModel 是"有状态的"，持有界面所需的数据
- Model 专注于数据，不关心界面
- 大量减少了手动更新 DOM / UI 的代码

### 适用场景

| 场景 | 适合程度 | 说明 |
|------|---------|------|
| Vue.js 应用 | ⭐⭐⭐⭐⭐ | 天然 MVVM |
| React 应用 | ⭐⭐⭐⭐ | Hooks 实现类似 MVVM |
| Angular 应用 | ⭐⭐⭐⭐⭐ | 原生 MVVM |
| 桌面 WPF/Qt | ⭐⭐⭐⭐⭐ | 原生支持绑定 |
| REST API 后端 | ⭐ | 不适合（无 UI 绑定） |

### Vue 3 Composition API — 完整 MVVM 示例

```vue
<!-- View 层：ProductList.vue -->
<template>
  <div class="product-list">
    <!-- 搜索过滤（双向绑定） -->
    <input v-model="filterCategory" placeholder="筛选分类" />

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">加载中...</div>

    <!-- 空状态 -->
    <div v-else-if="filteredProducts.length === 0">暂无商品</div>

    <!-- 商品列表 -->
    <ul v-else>
      <li v-for="p in filteredProducts" :key="p.id">
        {{ p.name }} — ¥{{ p.price.toFixed(2) }} ({{ p.category }})
      </li>
    </ul>

    <!-- 错误提示 -->
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

// ── ViewModel 层 ────────────────────────────────────────
// 状态（对应 Model 的数据）
const products = ref<Product[]>([]);
const filterCategory = ref("");
const loading = ref(false);
const error = ref("");

// 计算属性（衍生状态）
const filteredProducts = computed(() => {
  if (!filterCategory.value) return products.value;
  return products.value.filter(
    (p) => p.category === filterCategory.value
  );
});

// 业务逻辑
async function fetchProducts() {
  loading.value = true;
  error.value = "";
  try {
    const res = await fetch("/api/products");
    if (!res.ok) throw new Error(`请求失败: ${res.status}`);
    products.value = await res.json();
  } catch (e: any) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

// ── Model 层（API 调用） ─────────────────────────────────
interface Product {
  id: number;
  name: string;
  price: number;
  category: string;
}

// 生命周期钩子（组件挂载时自动调用）
onMounted(() => {
  fetchProducts();
});
</script>

<style scoped>
.loading { color: #888; }
.error { color: red; }
</style>
```

### React + Hooks 实现类 MVVM

```tsx
// ViewModel：自定义 Hook
import { useState, useEffect, useMemo } from "react";

interface Product { id: number; name: string; price: number; category: string; }

function useProductList() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");

  // 计算属性（类似 Vue computed）
  const filtered = useMemo(() => {
    return filter
      ? products.filter((p) => p.category === filter)
      : products;
  }, [products, filter]);

  // 业务逻辑
  async function fetchProducts() {
    setLoading(true);
    try {
      const res = await fetch("/api/products");
      setProducts(await res.json());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchProducts(); }, []);

  return { products: filtered, loading, error, filter, setFilter };
}

// View 层
export default function ProductList() {
  const { products, loading, error, filter, setFilter } = useProductList();

  return (
    <div>
      <input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="筛选分类" />
      {loading && <p>加载中...</p>}
      {error && <p style={{color:"red"}}>{error}</p>}
      <ul>
        {products.map((p) => (
          <li key={p.id}>{p.name} — ¥{p.price} ({p.category})</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 三、MVC vs MVVM 对比总结

| 维度 | MVC | MVVM |
|------|-----|------|
| 核心机制 | Controller 协调 | 数据绑定自动同步 |
| 数据更新方式 | 手动刷新 | 响应式自动更新 |
| 代码量 | 中等 | 较少（少了手动绑定） |
| 学习曲线 | 平缓 | 较陡（需要理解响应式） |
| 适用端 | 后端/API | 前端/桌面 |
| 典型框架 | Django, Flask, Express | Vue, Angular, WPF |
| 可测试性 | Controller 容易测试 | ViewModel 容易测试 |

---

## 四、实际项目选型建议

```
┌──────────────────────────────────────────────────┐
│             项目类型 → 推荐架构                   │
├──────────────────────────────────────────────────┤
│  REST API / 后端微服务  →  三层架构 / MVC         │
│  前后端分离的 SPA       →  MVVM (Vue/React)       │
│  传统服务器渲染网页      →  MVC                   │
│  桌面 GUI 应用          →  MVVM (WPF/Qt)         │
│  移动端 App             →  MVVM / MVI             │
│  数据分析和脚本          →  单层（不需架构）        │
└──────────────────────────────────────────────────┘
```

**记住**：没有最好的架构，只有最适合的架构。先理解业务，再选架构。
