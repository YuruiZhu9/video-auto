# 代码规范 - 团队编码约定

> 来源：AI Coding 工作流最佳实践 (Addy Osmani 2026)

## 通用原则

### 命名规范
- 变量/函数：camelCase
- 类/组件：PascalCase
- 常量：UPPER_SNAKE_CASE
- 文件：kebab-case

### 函数设计
- 单一职责：一个函数只做一件事
- 参数简洁：最好≤3个参数
- 返回明确：有明确的返回值

### 注释规范
- 解释"为什么"，不解释"是什么"
- 复杂逻辑必须注释
- TODO/FIXME标注待办

---

## AI 协作规则 (Addy Osmani)

### 核心原则
- 将 AI 生成的代码当作**初级开发者的代码**对待
- 永远不盲目信任 LLM 的输出
- 人类工程师仍是**导演**，AI 是**执行者**

### 减少幻觉
```
规则：
- 如果不确定或缺少代码上下文，请提问而非编造答案
- 修复 bug 时始终在注释中简要解释原因
- 测试通过前不能宣布任务完成
```

### 项目规范文件
- 创建 `CLAUDE.md` 或 `GEMINI.md` 文件
- 包含：项目风格偏好、规则、缩进偏好、需要避免的函数

## TypeScript规范

### 类型定义
```typescript
// ✅ 好的类型定义
interface User {
  id: string;
  email: string;
  nickname?: string; // 可选
}

// ❌ 避免
type User = {
  [key: string]: any;
};
```

### 类型推断
- 尽量让TS自动推断
- 复杂类型显式声明

## React规范

### 组件设计
```typescript
// ✅ 函数组件 + Hooks
function UserCard({ user }: UserCardProps) {
  const [loading, setLoading] = useState(false);
  
  return <div>{user.name}</div>;
}
```

### Hooks规范
- use开头：useAuth, useUser
- 自定义Hooks抽离复用逻辑
- 依赖数组必须完整

## Git提交规范

### 提交信息格式
```
type(scope): description

[optional body]
```

### Type类型
- feat: 新功能
- fix: 修复bug
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 杂项

### 示例
```
feat(auth): 添加用户注册功能

- 邮箱验证码验证
- 密码强度校验
- 统一错误提示
```
