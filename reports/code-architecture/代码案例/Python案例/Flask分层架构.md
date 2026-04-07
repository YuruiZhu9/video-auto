---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5add5f306162ee1f064b1878ca055164
    PropagateID: 5add5f306162ee1f064b1878ca055164
    ReservedCode1: 304502206a4981b2b4e676febeddc63e0bc7ba58541f2e05e905f71c698f6f2f6ea583cf022100c31dcbac64f4403848b6265df109ba7783ccd65682074cd6501a81b08ba407fd
    ReservedCode2: 3046022100b3a8e166f733084d805cdc5eb469bc2bc5bf6c9f9f6b0072da2336c9292ba0e3022100b7c6dd7dd7893d071dc32f7ec409c85f156a1542af80ae3a14172b2a1826c794
---

# Python 代码架构案例

## 案例：从Flask单文件到分层架构

### 原始代码（反例）

```python
# app.py - 两千行的单文件
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# 直接在路由里写所有逻辑
@app.route('/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    # 验证逻辑混在路由里
    if not data.get('name'):
        return jsonify({'error': 'name required'}), 400
    if not data.get('email'):
        return jsonify({'error': 'email required'}), 400
    if '@' not in data.get('email', ''):
        return jsonify({'error': 'invalid email'}), 400
    
    # 业务逻辑混在路由里
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                   (data['name'], data['email']))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    # 发送邮件逻辑也混在这里
    # send_welcome_email(data['email'])
    
    return jsonify({'id': user_id, 'name': data['name'], 'email': data['email']}), 201

# ... 还有几百个类似这样的路由
```

### 重构后（正例）

```
project/
├── app.py
├── config.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── order.py
├── schemas/
│   ├── __init__.py
│   └── user_schema.py
├── services/
│   ├── __init__.py
│   ├── user_service.py
│   └── email_service.py
├── repositories/
│   ├── __init__.py
│   └── user_repository.py
├── routes/
│   ├── __init__.py
│   └── user_routes.py
└── utils/
    ├── __init__.py
    └── validators.py
```

```python
# config.py
class Config:
    DATABASE = 'db.sqlite'
    SECRET_KEY = 'your-secret-key'

# models/user.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int] = None
    name: str = ''
    email: str = ''

# schemas/user_schema.py
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('名字至少2个字符')
        return v

# repositories/user_repository.py
class UserRepository:
    def __init__(self, db):
        self.db = db
    
    def find_all(self):
        self.db.execute("SELECT * FROM users")
        return self.db.fetchall()
    
    def find_by_id(self, user_id):
        self.db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return self.db.fetchone()
    
    def create(self, user: User):
        self.db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (user.name, user.email)
        )
        return self.db.lastrowid

# services/user_service.py
from models.user import User
from repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def get_users(self):
        return self.repo.find_all()
    
    def create_user(self, name: str, email: str):
        user = User(name=name, email=email)
        user.id = self.repo.create(user)
        return user
    
    def get_user_by_id(self, user_id):
        return self.repo.find_by_id(user_id)

# routes/user_routes.py
from flask import Blueprint, request, jsonify
from services.user_service import UserService
from repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate
from pydantic import ValidationError

user_bp = Blueprint('users', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    # 依赖注入
    from app import db
    repo = UserRepository(db)
    service = UserService(repo)
    
    users = service.get_users()
    return jsonify([{'id': u[0], 'name': u[1], 'email': u[2]} for u in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    from app import db
    repo = UserRepository(db)
    service = UserService(repo)
    
    try:
        data = request.json
        user_data = UserCreate(**data)
        user = service.create_user(user_data.name, user_data.email)
        return jsonify({'id': user.id, 'name': user.name, 'email': user.email}), 201
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400

# app.py
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    from routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
```

### 重构收益

| 维度 | 重构前 | 重构后 |
|------|--------|--------|
| 文件行数 | 2000+ | 分散到多个文件 |
| 新增API | 需要找到对应位置 | 在service层添加方法 |
| 测试 | 难以测试 | 各层可单独测试 |
| 团队协作 | 冲突频繁 | 每人负责不同模块 |
| 代码复用 | 大量重复 | Service层可复用 |
