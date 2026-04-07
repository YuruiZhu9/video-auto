# NestJS项目架构 - TypeScript示例

## NestJS核心概念

NestJS是基于Node.js的企业级框架，核心思想是**依赖注入**和**模块化**。

## 目录结构

```
src/
├── modules/
│   ├── user/
│   │   ├── dto/           # 数据传输对象
│   │   ├── entities/      # 实体
│   │   ├── user.controller.ts
│   │   ├── user.service.ts
│   │   └── user.module.ts
│   └── recommendation/
│       ├── dto/
│       ├── entities/
│       ├── recommendation.controller.ts
│       ├── recommendation.service.ts
│       └── recommendation.module.ts
├── common/
│   ├── decorators/        # 自定义装饰器
│   ├── filters/           # 异常过滤器
│   └── interceptors/      # 拦截器
├── config/                # 配置
└── main.ts                # 入口
```

## 代码示例：推荐模块

```typescript
// modules/recommendation/recommendation.service.ts
import { Injectable, Logger } from '@nestjs/common';
import { RecommendationRepository } from './recommendation.repository';
import { UserService } from '../user/user.service';

@Injectable()
export class RecommendationService {
  private readonly logger = new Logger(RecommendationService.name);

  constructor(
    private readonly recommendationRepo: RecommendationRepository,
    private readonly userService: UserService,
  ) {}

  async getRecommendations(userId: number, limit: number = 10) {
    // 1. 获取用户画像
    const userProfile = await this.userService.getProfile(userId);
    
    // 2. 召回候选集
    const candidates = await this.recallCandidates(userProfile);
    
    // 3. 模型排序
    const ranked = await this.rankItems(userProfile, candidates);
    
    return ranked.slice(0, limit);
  }

  private async recallCandidates(profile: UserProfile): Promise<Item[]> {
    // 召回逻辑
    return this.recommendationRepo.findBySimilarUsers(profile.userId);
  }

  private async rankItems(profile: UserProfile, items: Item[]): Promise<Item[]> {
    // 排序逻辑 - 可接入ML模型
    return items.sort((a, b) => b.score - a.score);
  }
}
```

## 控制器层

```typescript
// modules/recommendation/recommendation.controller.ts
import { Controller, Get, Param, Query } from '@nestjs/common';
import { RecommendationService } from './recommendation.service';

@Controller('recommendations')
export class RecommendationController {
  constructor(private readonly service: RecommendationService) {}

  @Get('users/:userId')
  async getUserRecommendations(
    @Param('userId') userId: string,
    @Query('limit') limit?: string,
  ) {
    const recommendations = await this.service.getRecommendations(
      parseInt(userId),
      limit ? parseInt(limit) : 10,
    );
    return { data: recommendations };
  }
}
```

## DTO数据校验

```typescript
// modules/recommendation/dto/get-recommendation.dto.ts
import { IsNumber, IsOptional, Min, Max } from 'class-validator';
import { Transform } from 'class-transformer';

export class GetRecommendationDto {
  @Transform(({ value }) => parseInt(value))
  @IsNumber()
  @Min(1)
  userId: number;

  @Transform(({ value }) => parseInt(value))
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(50)
  limit?: number = 10;
}
```

## 模块依赖

```typescript
// modules/recommendation/recommendation.module.ts
import { Module } from '@nestjs/common';
import { RecommendationService } from './recommendation.service';
import { RecommendationController } from './recommendation.controller';
import { RecommendationRepository } from './recommendation.repository';
import { UserModule } from '../user/user.module';

@Module({
  imports: [UserModule],
  controllers: [RecommendationController],
  providers: [RecommendationService, RecommendationRepository],
  exports: [RecommendationService],
})
export class RecommendationModule {}
```

## NestJS vs Flask对比

| 特性 | NestJS | Flask |
|------|--------|-------|
| 架构 | 模块化、依赖注入 | 灵活、自由 |
| 类型安全 | TypeScript原生 | 需额外配置 |
| 装饰器 | 原生支持 | 需扩展 |
| 适合场景 | 企业级后端 | 快速原型/Micro |
