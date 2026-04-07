# SOLID 原则详解

> 编写可维护、可扩展、健壮代码的五大原则

---

## S - 单一职责原则（Single Responsibility Principle）

### 核心思想
> 一个类只做一件事，只有一个原因让它改变

### 代码示例

#### 反例
```python
# ❌ 一个类干了太多事
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def save_to_database(self):
        """保存用户"""
        db.insert('users', self.__dict__)
    
    def send_email(self, message):
        """发送邮件"""
        smtp.send(self.email, message)
    
    def generate_report(self):
        """生成报告"""
        return f"User: {self.name}"
    
    # 问题：
    # 1. User 类变化的原因太多
    # 2. 数据库变化 → 要改 User
    # 3. 邮件服务变化 → 要改 User
    # 4. 报告格式变化 → 要改 User
```

#### 正例
```python
# ✅ 每个类只做一件事
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    """只负责用户数据的持久化"""
    def save(self, user: User):
        db.insert('users', {'name': user.name, 'email': user.email})
    
    def find(self, user_id):
        return db.select('users', user_id)

class EmailService:
    """只负责发送邮件"""
    def send(self, email: str, message: str):
        smtp.send(email, message)

class UserReportGenerator:
    """只负责生成用户报告"""
    def generate(self, user: User):
        return f"User: {user.name}"
```

---

## O - 开闭原则（Open/Closed Principle）

### 核心思想
> 对扩展开放，对修改封闭

### 代码示例

#### 反例
```python
# ❌ 每次加新支付方式都要改代码
class Payment:
    def pay(self, method: str, amount: float):
        if method == 'alipay':
            # 支付宝逻辑
            pass
        elif method == 'wechat':
            # 微信支付逻辑
            pass
        elif method == 'bankcard':
            # 银行卡逻辑
            pass
        # 每加一个支付方式都要改这里！
        # 风险：可能影响已有功能
```

#### 正例
```python
# ✅ 对扩展开放，新增支付方式无需修改现有代码
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float):
        pass

class Alipay(PaymentStrategy):
    def pay(self, amount: float):
        print(f"支付宝支付: ¥{amount}")

class WechatPay(PaymentStrategy):
    def pay(self, amount: float):
        print(f"微信支付: ¥{amount}")

class BankCardPay(PaymentStrategy):
    def pay(self, amount: float):
        print(f"银行卡支付: ¥{amount}")

class Payment:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def execute(self, amount: float):
        self.strategy.pay(amount)

# 使用
payment = Payment(Alipay())
payment.execute(100.0)

# 新增 Stripe 支付？只需新增一个类，无需修改 Payment
```

---

## L - 里氏替换原则（Liskov Substitution Principle）

### 核心思想
> 子类必须能够替换基类而不影响程序正确性

### 代码示例

#### 反例
```python
# ❌ 正方形继承矩形，违反里氏替换原则
class Rectangle:
    def set_width(self, width):
        self.width = width
    
    def set_height(self, height):
        self.height = height
    
    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, width):
        self.width = width
        self.height = width  # 保持正方形特性
    
    def set_height(self, height):
        self.width = height
        self.height = height

# 问题：
def increase_width(rect: Rectangle):
    rect.set_width(rect.width + 10)

square = Square()
square.set_width(5)  # 宽高都是5
increase_width(square)  # 期望：宽变成15，高不变
# 实际：宽变成15，高也变成15（因为set_width同时改了height）
# 正方形不是"正确的"矩形！
```

#### 正例
```python
# ✅ 重新设计：正方形和矩形是并列关系
class Shape:
    def area(self):
        raise NotImplementedError

class Rectangle(Shape):
    def __init__(self, width, height):
        self._width = width
        self._height = height
    
    def area(self):
        return self._width * self._height

class Square(Shape):
    def __init__(self, side):
        self._side = side
    
    def area(self):
        return self._side * self._side

# 或者：组合优于继承
class Quadrilateral(Shape):
    pass
```

---

## I - 接口隔离原则（Interface Segregation Principle）

### 核心思想
> 多个专用接口优于一个臃肿接口

### 代码示例

#### 反例
```python
# ❌ 一个大接口，所有机器都要实现
class IMachine:
    def print(self, document): pass
    def scan(self, document): pass
    def fax(self, document): pass

class OldPrinter(IMachine):
    def print(self, document):
        print("打印中...")
    def scan(self, document):
        raise NotImplementedError("这台打印机不能扫描")  # ❌
    def fax(self, document):
        raise NotImplementedError("这台打印机不能传真")  # ❌
```

#### 正例
```python
# ✅ 拆分成多个小接口
class Printer:
    def print(self, document): pass

class Scanner:
    def scan(self, document): pass

class Fax:
    def fax(self, document): pass

# 简单打印机：只实现打印功能
class SimplePrinter(Printer):
    def print(self, document):
        print("打印中...")

# 多功能一体机：实现所有功能
class AllInOnePrinter(Printer, Scanner, Fax):
    def print(self, document): print("打印")
    def scan(self, document): print("扫描")
    def fax(self, document): print("传真")
```

---

## D - 依赖倒置原则（Dependency Inversion Principle）

### 核心思想
> 高层模块不依赖低层模块，两者都依赖抽象

### 代码示例

#### 反例
```python
# ❌ 高层模块依赖低层模块
class MySQL:
    def connect(self): pass

class UserService:
    def __init__(self):
        self.db = MySQL()  # 直接依赖具体实现
    
    def get_user(self, user_id):
        self.db.connect()  # 换数据库要改这里
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
```

#### 正例
```python
# ✅ 依赖抽象接口
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def connect(self): pass
    
    @abstractmethod
    def query(self, sql: str): pass

class MySQL(Database):
    def connect(self): print("连接MySQL")
    def query(self, sql: str): return f"结果: {sql}"

class PostgreSQL(Database):
    def connect(self): print("连接PostgreSQL")
    def query(self, sql: str): return f"结果: {sql}"

class UserService:
    def __init__(self, db: Database):  # 依赖抽象
        self.db = db
    
    def get_user(self, user_id):
        self.db.connect()
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

# 轻松切换数据库
user_service = UserService(MySQL())
# user_service = UserService(PostgreSQL())
```

---

## 实践练习

### 练习 1：重构一个订单处理类
检查这个类有哪些职责，拆分成单一职责的多个类。

### 练习 2：设计一个支付系统
使用开闭原则，让系统支持新增支付方式而不修改现有代码。

### 练习 3：检查继承关系
找出代码中所有继承关系，验证是否违反里氏替换原则。

---

## SOLID 记忆口诀

```
S - 一个类，一个责任
O - 扩展开放，修改封闭
L - 子类替换父类，一切正常
I - 接口要小，不要大而全
D - 依赖抽象，不要依赖具体
```

---

## 常见问题

**Q：是不是所有类都要严格遵循 SOLID？**
A：不是。过度工程是另一个极端。对于简单脚本或一次性代码，先跑起来更重要。

**Q：什么时候该重构？**
A：当你需要在一个类上添加新功能，却发现改动会影响其他不相关功能时。

**Q：SOLID 原则冲突怎么办？**
A：有时原则会冲突，此时优先保证代码的可测试性和可维护性。
