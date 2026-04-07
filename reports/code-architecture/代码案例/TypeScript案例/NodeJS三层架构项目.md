# TypeScript 案例 — Express/NestJS 三层架构项目

## 项目背景

一个**任务管理系统（Task Management API）**，演示 TypeScript 下的三层架构实践。

## 项目结构

```
task_api/
├── src/
│   ├── main.ts              # 入口
│   ├── app.module.ts         # 根模块（NestJS）
│   ├── config/
│   │   └── config.ts         # 配置
│   ├── tasks/
│   │   ├── tasks.module.ts
│   │   ├── tasks.controller.ts    # 表现层
│   │   ├── tasks.service.ts       # 业务层
│   │   ├── tasks.repository.ts    # 数据层
│   │   ├── dto/
│   │   │   ├── create-task.dto.ts
│   │   │   └── update-task.dto.ts
│   │   └── entities/
│   │       └── task.entity.ts
│   └── common/
│       └── filters/
│           └── http-exception.filter.ts
└── package.json
```

## 1. 数据实体

```typescript
// tasks/entities/task.entity.ts
export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  createdAt: Date;
  updatedAt: Date;
  assigneeId?: string;
}

export enum TaskStatus {
  TODO = "TODO",
  IN_PROGRESS = "IN_PROGRESS",
  DONE = "DONE",
  ARCHIVED = "ARCHIVED",
}

export enum TaskPriority {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  URGENT = "URGENT",
}
```

## 2. DTO（Data Transfer Objects）

```typescript
// tasks/dto/create-task.dto.ts
import { IsString, IsEnum, IsOptional, MinLength, MaxLength } from "class-validator";
import { TaskStatus, TaskPriority } from "../entities/task.entity";

export class CreateTaskDto {
  @IsString()
  @MinLength(1)
  @MaxLength(200)
  title: string;

  @IsString()
  @IsOptional()
  @MaxLength(2000)
  description?: string;

  @IsEnum(TaskStatus)
  @IsOptional()
  status?: TaskStatus = TaskStatus.TODO;

  @IsEnum(TaskPriority)
  @IsOptional()
  priority?: TaskPriority = TaskPriority.MEDIUM;

  @IsString()
  @IsOptional()
  assigneeId?: string;
}
```

```typescript
// tasks/dto/update-task.dto.ts
import { PartialType } from "@nestjs/mapped-types";
import { CreateTaskDto } from "./create-task.dto";

export class UpdateTaskDto extends PartialType(CreateTaskDto) {}
```

## 3. 数据层（Repository）

```typescript
// tasks/tasks.repository.ts
import { Injectable } from "@nestjs/common";
import { Task, TaskStatus } from "./entities/task.entity";

@Injectable()
export class TasksRepository {
  private tasks: Task[] = [];
  private idCounter = 1;

  async findAll(filters?: { status?: TaskStatus; assigneeId?: string }): Promise<Task[]> {
    let result = [...this.tasks];
    if (filters?.status) {
      result = result.filter((t) => t.status === filters.status);
    }
    if (filters?.assigneeId) {
      result = result.filter((t) => t.assigneeId === filters.assigneeId);
    }
    return result;
  }

  async findById(id: string): Promise<Task | null> {
    return this.tasks.find((t) => t.id === id) ?? null;
  }

  async create(data: Omit<Task, "id" | "createdAt" | "updatedAt">): Promise<Task> {
    const task: Task = {
      id: String(this.idCounter++),
      ...data,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.tasks.push(task);
    return task;
  }

  async update(id: string, data: Partial<Omit<Task, "id" | "createdAt">>): Promise<Task | null> {
    const idx = this.tasks.findIndex((t) => t.id === id);
    if (idx === -1) return null;
    this.tasks[idx] = { ...this.tasks[idx], ...data, updatedAt: new Date() };
    return this.tasks[idx];
  }

  async delete(id: string): Promise<boolean> {
    const idx = this.tasks.findIndex((t) => t.id === id);
    if (idx === -1) return false;
    this.tasks.splice(idx, 1);
    return true;
  }
}
```

## 4. 业务层（Service）

```typescript
// tasks/tasks.service.ts
import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { TasksRepository } from "./tasks.repository";
import { CreateTaskDto } from "./dto/create-task.dto";
import { UpdateTaskDto } from "./dto/update-task.dto";
import { Task, TaskStatus } from "./entities/task.entity";

@Injectable()
export class TasksService {
  constructor(private readonly repository: TasksRepository) {}

  async listTasks(filters?: { status?: TaskStatus; assigneeId?: string }): Promise<Task[]> {
    return this.repository.findAll(filters);
  }

  async getTask(id: string): Promise<Task> {
    const task = await this.repository.findById(id);
    if (!task) {
      throw new NotFoundException(`任务 ID ${id} 不存在`);
    }
    return task;
  }

  async createTask(dto: CreateTaskDto): Promise<Task> {
    // 业务规则：已完成的不能新建为已完成（除非显式指定）
    if (dto.status === TaskStatus.DONE && !dto.assigneeId) {
      throw new BadRequestException("标记为完成的任务必须指定负责人");
    }
    return this.repository.create({
      title: dto.title,
      description: dto.description ?? "",
      status: dto.status ?? TaskStatus.TODO,
      priority: dto.priority ?? TaskPriority.MEDIUM,
      assigneeId: dto.assigneeId,
    });
  }

  async updateTask(id: string, dto: UpdateTaskDto): Promise<Task> {
    const task = await this.repository.findById(id);
    if (!task) {
      throw new NotFoundException(`任务 ID ${id} 不存在`);
    }

    // 业务规则：已完成的任务不能再改状态为 TODO
    if (
      task.status === TaskStatus.DONE &&
      dto.status === TaskStatus.TODO
    ) {
      throw new BadRequestException("已完成的任务不能重新标记为待办");
    }

    const updated = await this.repository.update(id, {
      ...(dto.title !== undefined && { title: dto.title }),
      ...(dto.description !== undefined && { description: dto.description }),
      ...(dto.status !== undefined && { status: dto.status }),
      ...(dto.priority !== undefined && { priority: dto.priority }),
      ...(dto.assigneeId !== undefined && { assigneeId: dto.assigneeId }),
    });
    return updated!;
  }

  async deleteTask(id: string): Promise<void> {
    const deleted = await this.repository.delete(id);
    if (!deleted) {
      throw new NotFoundException(`任务 ID ${id} 不存在`);
    }
  }
}
```

## 5. 表现层（Controller）

```typescript
// tasks/tasks.controller.ts
import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  UseFilters,
} from "@nestjs/common";
import { TasksService } from "./tasks.service";
import { CreateTaskDto } from "./dto/create-task.dto";
import { UpdateTaskDto } from "./dto/update-task.dto";
import { TaskStatus } from "./entities/task.entity";

@Controller("tasks")
export class TasksController {
  constructor(private readonly tasksService: TasksService) {}

  @Get()
  async listTasks(
    @Query("status") status?: TaskStatus,
    @Query("assigneeId") assigneeId?: string,
  ) {
    return this.tasksService.listTasks(
      status ? { status } : assigneeId ? { assigneeId } : undefined,
    );
  }

  @Get(":id")
  async getTask(@Param("id") id: string) {
    return this.tasksService.getTask(id);
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  async createTask(@Body() dto: CreateTaskDto) {
    return this.tasksService.createTask(dto);
  }

  @Patch(":id")
  async updateTask(@Param("id") id: string, @Body() dto: UpdateTaskDto) {
    return this.tasksService.updateTask(id, dto);
  }

  @Delete(":id")
  @HttpCode(HttpStatus.NO_CONTENT)
  async deleteTask(@Param("id") id: string) {
    await this.tasksService.deleteTask(id);
  }
}
```

## 6. NestJS 模块组装

```typescript
// tasks/tasks.module.ts
import { Module } from "@nestjs/common";
import { TasksController } from "./tasks.controller";
import { TasksService } from "./tasks.service";
import { TasksRepository } from "./tasks.repository";

@Module({
  controllers: [TasksController],
  providers: [TasksService, TasksRepository],
  exports: [TasksService],
})
export class TasksModule {}
```

```typescript
// app.module.ts
import { Module } from "@nestjs/common";
import { TasksModule } from "./tasks/tasks.module";

@Module({
  imports: [TasksModule],
})
export class AppModule {}
```

## 架构可视化

```
HTTP 请求
    │
    ▼
┌─────────────────────────┐
│  Controller (控制器)       │  ← 表现层：路由、参数校验、响应格式
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Service (服务)          │  ← 业务层：业务规则、事务、组合逻辑
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Repository (仓储)       │  ← 数据层：数据存取、数据库操作
└────────────┬────────────┘
             │
             ▼
     PostgreSQL / In-Memory
```

## 关键设计要点

1. **TypeScript 类型安全**：DTO 用 class-validator 做运行时校验，接口在编译期检查
2. **单一职责**：每层只做自己的事，不越界
3. **NestJS 依赖注入**：Controller → Service → Repository 自动组装
4. **业务规则集中在 Service 层**：Controller 只是薄薄的一层转发
5. **DTO 隔离内外**：外部请求进 DTO，内部用 Entity，降低耦合

## 单元测试示例

```typescript
// tasks/tasks.service.spec.ts
import { Test } from "@nestjs/testing";
import { TasksService } from "./tasks.service";
import { TasksRepository } from "./tasks.repository";
import { TaskStatus, TaskPriority } from "./entities/task.entity";

describe("TasksService", () => {
  let service: TasksService;
  let repository: TasksRepository;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        TasksService,
        {
          provide: TasksRepository,
          useValue: {
            findAll: jest.fn().mockResolvedValue([]),
            findById: jest.fn(),
            create: jest.fn(),
            update: jest.fn(),
            delete: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get<TasksService>(TasksService);
    repository = module.get<TasksRepository>(TasksRepository);
  });

  it("should be defined", () => {
    expect(service).toBeDefined();
  });

  it("getTask throws NotFoundException when task not found", async () => {
    jest.spyOn(repository, "findById").mockResolvedValue(null);
    await expect(service.getTask("999")).rejects.toThrow("任务 ID 999 不存在");
  });

  it("createTask with DONE status without assigneeId throws BadRequestException", async () => {
    await expect(
      service.createTask({ title: "Test", status: TaskStatus.DONE }),
    ).rejects.toThrow("标记为完成的任务必须指定负责人");
  });
});
```
