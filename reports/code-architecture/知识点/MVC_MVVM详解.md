# MVC vs MVVM：选型指南

## MVC 模式

### 概念解释
MVC = Model（模型）+ View（视图）+ Controller（控制器）

```
┌─────────┐      ┌─────────┐      ┌──────────┐
│  View   │◄────►│Controller│◄────►│   Model  │
│  视图   │      │ 控制器  │      │   模型   │
└─────────┘      └─────────┘      └──────────┘
     │                │                │
     │   用户操作      │ 业务逻辑        │ 数据存取
     └────────────────┴────────────────┘
```

**职责分工：**
- **Model（模型）**：数据和业务逻辑
- **View（视图）**：用户界面展示
- **Controller（控制器）**：接收请求、调用模型、返回视图

### 代码示例

#### 反例（耦合严重）
```python
# ❌ 所有逻辑混在一起
@app.route('/user/<int:user_id>')
def get_user(user_id):
    # 数据存取
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    # 业务逻辑
    if user and user[3] > 18:
        user_level = "成人"
    else:
        user_level = "未成年"
    
    # 视图渲染（直接拼接HTML）
    html = f"""
    <html>
    <body>
        <h1>{user[1]} - {user_level}</h1>
        <p>邮箱: {user[2]}</p>
    </body>
    </html>
    """
    return html
```

#### 正例（标准MVC）
```python
# ✅ Model: models/user.py
class User:
    def __init__(self, db):
        self.db = db
    
    def get_by_id(self, user_id):
        cursor = self.db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        )
        return cursor.fetchone()
    
    def get_level(self, user):
        return "成人" if user and user[3] > 18 else "未成年"

# ✅ Controller: controllers/user_controller.py
from flask import render_template

class UserController:
    def __init__(self, user_model):
        self.user_model = user_model
    
    def get_user(self, user_id):
        user = self.user_model.get_by_id(user_id)
        if not user:
            return "用户不存在", 404
        
        level = self.user_model.get_level(user)
        return render_template('user.html', user=user, level=level)

# ✅ View: templates/user.html
# <html><body><h1>{{ user.name }} - {{ level }}</h1></body></html>
```

### 适用场景
- 传统 Web 后端开发
- 需要明确前后端分离的项目
- Flask、Django、Rails 等框架

---

## MVVM 模式

### 概念解释
MVVM = Model（模型）+ View（视图）+ ViewModel（视图模型）

```
┌─────────┐      ┌───────────┐      ┌─────────┐
│  View   │◄────►│ ViewModel │◄────►│  Model  │
│  视图   │ 数据绑定 │ 视图模型  │      │   模型  │
└─────────┘      └───────────┘      └─────────┘
     │                                    │
     │        双向数据绑定                  │
     └────────────────────────────────────┘
```

**核心区别：**
- Controller → ViewModel（ViewModel 替代 Controller）
- **数据绑定**：ViewModel 变化自动更新 View
- **双向绑定**：View 变化自动同步到 Model

### 代码示例

#### 反例（手动更新，容易出错）
```typescript
// ❌ 手动操作 DOM，耦合严重
function renderUser(user: User) {
    const nameEl = document.getElementById('name');
    const ageEl = document.getElementById('age');
    
    nameEl.textContent = user.name;
    ageEl.textContent = user.age.toString();
    
    // 每次数据变化都要手动更新
    // 复杂页面维护噩梦
}

button.addEventListener('click', () => {
    user.age++;
    renderUser(user); // 忘记调用就出问题
});
```

#### 正例（Vue3 MVVM）
```typescript
// ✅ Model: types/user.ts
interface User {
    id: number;
    name: string;
    age: number;
}

// ✅ ViewModel: composables/useUser.ts
import { ref, computed } from 'vue';

export function useUser(initialUser: User) {
    const user = ref(initialUser);
    
    const level = computed(() => 
        user.value.age > 18 ? '成人' : '未成年'
    );
    
    const birthday = () => {
        user.value.age++;
        // 自动触发视图更新，无需手动调用
    };
    
    return { user, level, birthday };
}

// ✅ View: UserProfile.vue
/*
<template>
  <div>
    <h1>{{ user.name }} - {{ level }}</h1>
    <p>年龄: {{ user.age }}</p>
    <button @click="birthday">过生日</button>
  </div>
</template>

<script setup>
const { user, level, birthday } = useUser(initialUser);
</script>
*/
```

### 适用场景
- 前端框架开发（Vue、Angular、React）
- 移动端开发（Flutter、SwiftUI）
- 需要频繁更新视图的场景

---

## 选型决策树

```
你的项目？
├── 后端 API？
│   └── 推荐：MVC（Flask/Django）
├── 前端 SPA？
│   └── 推荐：MVVM（Vue/React）
├── 全栈框架（Next.js/Nuxt）？
│   └── 推荐：MVC + MVVM 混合
└── 简单脚本？
    └── 不需要架构，先跑起来
```

---

## 常见误区

1. **MVC 误区**：
   - ❌ View 中写业务逻辑
   - ❌ Controller 中直接操作数据库
   - ❌ Model 中写视图渲染逻辑

2. **MVVM 误区**：
   - ❌ ViewModel 中操作 DOM
   - ❌ 双向绑定滥用，导致数据流混乱
   - ❌ 一个 ViewModel 处理太多职责

---

## 实践练习

1. 用 Flask 重构一个旧的 Flask 项目，实践 MVC
2. 用 Vue3 实现一个表单，实践 MVVM
3. 对比两者：同样的功能，哪个更简洁？
