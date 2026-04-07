# Python 案例 — FastAPI 三层架构项目

## 项目背景

一个简单的**商品管理系统**，演示从 MVC 到三层架构的演进。

## 项目结构

```
shop_api/
├── main.py              # 应用入口
├── config.py            # 配置
├── database.py          # 数据库连接
├── schemas.py           # Pydantic 数据模型（API 层）
├── models/
│   └── product.py       # ORM 模型
├── repositories/
│   └── product_repo.py  # 数据层
├── services/
│   └── product_service.py  # 业务层
├── routers/
│   └── product_router.py   # 表现层
└── tests/
    └── test_product_service.py
```

## 1. 配置层

```python
# config.py
import os

class Settings:
    APP_NAME = "商品管理系统"
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/shop")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    PAGE_SIZE_DEFAULT = 20
    PAGE_SIZE_MAX = 100

settings = Settings()
```

## 2. 数据层（Repository）

```python
# repositories/product_repo.py
from sqlalchemy.orm import Session
from models.product import Product
from typing import Optional

class ProductRepository:
    """数据层：只负责 CRUD，不包含业务逻辑"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_all(self, skip: int = 0, limit: int = 20) -> list[Product]:
        return self.db.query(Product).offset(skip).limit(limit).all()

    def get_by_category(self, category: str, skip: int = 0, limit: int = 20) -> list[Product]:
        return self.db.query(Product).filter(Product.category == category).offset(skip).limit(limit).all()

    def create(self, name: str, category: str, price: float, stock: int = 0) -> Product:
        product = Product(name=name, category=category, price=price, stock=stock)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: Product, **kwargs) -> Product:
        for key, value in kwargs.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()

    def count(self) -> int:
        return self.db.query(Product).count()
```

## 3. 业务层（Service）

```python
# services/product_service.py
from sqlalchemy.orm import Session
from repositories.product_repo import ProductRepository
from schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from config import settings
from typing import Optional

class ProductService:
    """业务层：处理业务规则，调用数据层"""

    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def list_products(self, category: Optional[str] = None,
                     page: int = 1, page_size: int = 20) -> dict:
        page_size = min(page_size, settings.PAGE_SIZE_MAX)
        skip = (page - 1) * page_size
        products = (self.repo.get_by_category(category, skip, page_size)
                    if category else self.repo.get_all(skip, page_size))
        return {
            "items": [ProductResponse.model_validate(p) for p in products],
            "total": self.repo.count(),
            "page": page,
            "page_size": page_size,
        }

    def get_product(self, product_id: int) -> ProductResponse:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品 ID {product_id} 不存在")
        return ProductResponse.model_validate(product)

    def create_product(self, data: ProductCreate) -> ProductResponse:
        existing = self.repo.get_all(limit=1000)
        if any(p.name == data.name and p.category == data.category for p in existing):
            raise ValueError("同类商品中已存在同名商品")
        product = self.repo.create(data.name, data.category, data.price, data.stock)
        return ProductResponse.model_validate(product)

    def update_product(self, product_id: int, data: ProductUpdate) -> ProductResponse:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品 ID {product_id} 不存在")
        if data.stock is not None and data.stock < 0:
            raise ValueError("库存不能为负数")
        updated = self.repo.update(product, **data.model_dump(exclude_unset=True))
        return ProductResponse.model_validate(updated)

    def delete_product(self, product_id: int) -> None:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品 ID {product_id} 不存在")
        self.repo.delete(product)
```

## 4. 表现层（Router）

```python
# routers/product_router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from services.product_service import ProductService
from schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from typing import Optional

router = APIRouter(prefix="/products", tags=["商品管理"])

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.get("", response_model=dict)
def list_products(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    svc: ProductService = Depends(get_product_service),
):
    return svc.list_products(category=category, page=page, page_size=page_size)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, svc: ProductService = Depends(get_product_service)):
    try:
        return svc.get_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, svc: ProductService = Depends(get_product_service)):
    try:
        return svc.create_product(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, svc: ProductService = Depends(get_product_service)):
    try:
        return svc.update_product(product_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, svc: ProductService = Depends(get_product_service)):
    try:
        svc.delete_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

## 5. 应用入口

```python
# main.py
from fastapi import FastAPI
from database import engine, Base
from routers import product_router
from config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")
app.include_router(product_router.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# 启动：uvicorn main:app --reload
```

## 架构可视化

```
HTTP 请求
    │
    ▼
┌─────────────────┐
│  Router (路由层)  │  ← 表现层：接收请求、参数校验、返回响应
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Service (服务层) │  ← 业务层：业务规则、数据组装、异常处理
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Repository     │  ← 数据层：SQL 查询、ORM 操作
└────────┬────────┘
         │
         ▼
     PostgreSQL
```

## 关键设计要点

1. **层间单向依赖**：Router → Service → Repository，不反向依赖
2. **Schema 隔离 API**：外部请求用 Pydantic Schema 校验，内部用 ORM Model
3. **Dependency Injection**：通过 FastAPI 的 Depends() 注入数据库会话
4. **异常统一处理**：业务层抛异常，路由层统一转 HTTP 响应
