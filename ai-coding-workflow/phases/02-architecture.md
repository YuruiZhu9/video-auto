# 02 - 架构设计

> 动手之前先想好结构

## 架构设计流程

```
1. 数据模型设计 → 2. API设计 → 3. 组件结构 → 4. 技术选型确认
```

## 数据模型设计

让AI先画出数据模型，示例：

```
## User表
- id: string (UUID)
- email: string (唯一)
- password_hash: string
- nickname: string
- avatar_url: string (可选)
- created_at: timestamp
- updated_at: timestamp

## Post表
- id: string (UUID)
- user_id: string (外键)
- title: string
- content: text
- published: boolean
- created_at: timestamp
```

## AI协作技巧

### 让AI先画架构图
> "先别写代码帮我画出系统架构图，用Mermaid或ASCII都可以"

### 让AI列出技术选型
> "这个功能涉及[X]，请列出3个可选方案及优缺点"

### 确认依赖关系
> "实现这个功能需要哪些包？列出必需的依赖"

## 架构文档模板

```markdown
## 系统架构

## 数据流

## 核心模块

## 外部依赖
```

## 下一步

架构确认后 → [03-任务规划](./03-planning.md)
