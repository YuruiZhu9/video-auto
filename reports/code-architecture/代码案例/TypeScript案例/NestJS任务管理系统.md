# TypeScript NestJS 实战：任务管理系统

## 项目结构

```
task-manager/
├── src/
│   ├── tasks/
│   │   ├── dto/
│   │   │   ├── create-task.dto.ts
│   │   │   └── update-task.dto.ts
│   │   ├── entities/
│   │   │   └── task.entity.ts
│   │   ├── tasks.controller.ts
│   │   ├── tasks.service.ts
│   │   └── tasks.module.ts
│   ├── app.module.ts
│   └── main.ts
├── package.json
└── tsconfig.json
```

---

## 1. Entity - 数据模型

```typescript
// src/tasks/entities/task.entity.ts
export enum TaskStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
}

export class Task {
  id: number;
  title: string;
  description: string;
  status: TaskStatus;
  createdAt: Date;
  updatedAt: Date;

  constructor(
    id: number,
    title: string,
    description: string,
    status: TaskStatus = TaskStatus.PENDING,
  ) {
    this.id = id;
    this.title = title;
    this.description = description;
    this.status = status;
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }
}
```

---

## 2. DTO - 数据传输对象

```typescript
// src/tasks/dto/create-task.dto.ts
export class CreateTaskDto {
  title: string;
  description: string;
}

// src/tasks/dto/update-task.dto.ts
import { PartialType } from '@nestjs/mapped-types';
import { CreateTaskDto } from './create-task.dto';

export class UpdateTaskDto extends PartialType(CreateTaskDto) {
  status?: string;
}
```

---

## 3. Service - 业务逻辑层

```typescript
// src/tasks/tasks.service.ts
import { Injectable, NotFoundException } from '@nestjs/common';
import { Task, TaskStatus } from './entities/task.entity';
import { CreateTaskDto } from './dto/create-task.dto';
import { UpdateTaskDto } from './dto/update-task.dto';

@Injectable()
export class TasksService {
  private tasks: Task[] = [];
  private idCounter = 1;

  createTask(createTaskDto: CreateTaskDto): Task {
    const { title, description } = createTaskDto;
    const task = new Task(this.idCounter++, title, description, TaskStatus.PENDING);
    this.tasks.push(task);
    return task;
  }

  getAllTasks(): Task[] {
    return this.tasks;
  }

  getTaskById(id: number): Task {
    const task = this.tasks.find(t => t.id === id);
    if (!task) {
      throw new NotFoundException(`任务 #${id} 不存在`);
    }
    return task;
  }

  updateTask(id: number, updateTaskDto: UpdateTaskDto): Task {
    const task = this.getTaskById(id);
    if (updateTaskDto.title) task.title = updateTaskDto.title;
    if (updateTaskDto.description) task.description = updateTaskDto.description;
    if (updateTaskDto.status) task.status = updateTaskDto.status as TaskStatus;
    task.updatedAt = new Date();
    return task;
  }

  deleteTask(id: number): void {
    const index = this.tasks.findIndex(t => t.id === id);
    if (index === -1) {
      throw new NotFoundException(`任务 #${id} 不存在`);
    }
    this.tasks.splice(index, 1);
  }
}
```

---

## 4. Controller - 请求处理层

```typescript
// src/tasks/tasks.controller.ts
import { 
  Controller, Get, Post, Body, Patch, Param, Delete, ParseIntPipe,
} from '@nestjs/common';
import { TasksService } from './tasks.service';
import { CreateTaskDto } from './dto/create-task.dto';
import { UpdateTaskDto } from './dto/update-task.dto';

@Controller('tasks')
export class TasksController {
  constructor(private readonly tasksService: TasksService) {}

  @Post()
  create(@Body() createTaskDto: CreateTaskDto) {
    return this.tasksService.createTask(createTaskDto);
  }

  @Get()
  findAll() {
    return this.tasksService.getAllTasks();
  }

  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) {
    return this.tasksService.getTaskById(id);
  }

  @Patch(':id')
  update(@Param('id', ParseIntPipe) id: number, @Body() updateTaskDto: UpdateTaskDto) {
    return this.tasksService.updateTask(id, updateTaskDto);
  }

  @Delete(':id')
  remove(@Param('id', ParseIntPipe) id: number) {
    return this.tasksService.deleteTask(id);
  }
}
```

---

## 5. API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /tasks | 创建任务 |
| GET | /tasks | 获取所有任务 |
| GET | /tasks/:id | 获取单个任务 |
| PATCH | /tasks/:id | 更新任务 |
| DELETE | /tasks/:id | 删除任务 |

---

## 架构优势

1. **TypeScript 静态类型**：编译时发现错误
2. **依赖注入**：便于测试和模块化
3. **装饰器语法**：简洁优雅
4. **分层清晰**：Controller → Service → Entity
