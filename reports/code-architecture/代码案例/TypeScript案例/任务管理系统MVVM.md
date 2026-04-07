# TypeScript MVVM 案例 - 任务管理系统

## 项目结构
```
task_system/
├── models/
│   └── task.model.ts
├── viewmodels/
│   └── task.viewmodel.ts
├── views/
│   └── task.view.vue
├── services/
│   └── task.service.ts
└── main.ts
```

## 代码实现

### Model - 数据模型
```typescript
// models/task.model.ts
export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  createdAt: Date;
  dueDate?: Date;
}

export interface TaskFilter {
  showCompleted?: boolean;
  priority?: Task['priority'];
  searchText?: string;
}
```

### Service - 数据服务层
```typescript
// services/task.service.ts
import { Task, TaskFilter } from '../models/task.model';

const STORAGE_KEY = 'tasks';

export class TaskService {
  // 模拟API调用
  async getAll(): Promise<Task[]> {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  }

  async getById(id: number): Promise<Task | undefined> {
    const tasks = await this.getAll();
    return tasks.find(t => t.id === id);
  }

  async create(task: Omit<Task, 'id' | 'createdAt'>): Promise<Task> {
    const tasks = await this.getAll();
    const newTask: Task = {
      ...task,
      id: Date.now(),
      createdAt: new Date()
    };
    tasks.push(newTask);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    return newTask;
  }

  async update(id: number, updates: Partial<Task>): Promise<Task | null> {
    const tasks = await this.getAll();
    const index = tasks.findIndex(t => t.id === id);
    if (index === -1) return null;
    
    tasks[index] = { ...tasks[index], ...updates };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    return tasks[index];
  }

  async delete(id: number): Promise<boolean> {
    const tasks = await this.getAll();
    const filtered = tasks.filter(t => t.id !== id);
    if (filtered.length === tasks.length) return false;
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
    return true;
  }

  filterTasks(tasks: Task[], filter: TaskFilter): Task[] {
    return tasks.filter(task => {
      if (filter.showCompleted === false && task.completed) return false;
      if (filter.priority && task.priority !== filter.priority) return false;
      if (filter.searchText) {
        const search = filter.searchText.toLowerCase();
        return task.title.toLowerCase().includes(search) ||
               task.description.toLowerCase().includes(search);
      }
      return true;
    });
  }
}

export const taskService = new TaskService();
```

### ViewModel - 视图模型
```typescript
// viewmodels/task.viewmodel.ts
import { Task, TaskFilter } from '../models/task.model';
import { taskService } from '../services/task.service';

export class TaskViewModel {
  // 响应式数据
  tasks: Task[] = [];
  filteredTasks: Task[] = [];
  selectedTask: Task | null = null;
  isLoading = false;
  error: string | null = null;
  
  // 筛选状态
  filter: TaskFilter = {
    showCompleted: true,
    searchText: ''
  };

  // 计算属性
  get pendingCount(): number {
    return this.tasks.filter(t => !t.completed).length;
  }

  get completedCount(): number {
    return this.tasks.filter(t => t.completed).length;
  }

  get totalCount(): number {
    return this.tasks.length;
  }

  get sortedTasks(): Task[] {
    return [...this.filteredTasks].sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }

  // 动作方法
  async loadTasks(): Promise<void> {
    this.isLoading = true;
    this.error = null;
    try {
      this.tasks = await taskService.getAll();
      this.applyFilter();
    } catch (e) {
      this.error = '加载任务失败';
    } finally {
      this.isLoading = false;
    }
  }

  async createTask(title: string, description: string, priority: Task['priority']): Promise<boolean> {
    this.isLoading = true;
    this.error = null;
    try {
      await taskService.create({ title, description, completed: false, priority });
      await this.loadTasks();
      return true;
    } catch (e) {
      this.error = '创建任务失败';
      return false;
    } finally {
      this.isLoading = false;
    }
  }

  async toggleComplete(task: Task): Promise<void> {
    await taskService.update(task.id, { completed: !task.completed });
    task.completed = !task.completed;
    this.applyFilter();
  }

  async deleteTask(taskId: number): Promise<boolean> {
    const success = await taskService.delete(taskId);
    if (success) {
      this.tasks = this.tasks.filter(t => t.id !== taskId);
      this.applyFilter();
    }
    return success;
  }

  setFilter(filter: Partial<TaskFilter>): void {
    this.filter = { ...this.filter, ...filter };
    this.applyFilter();
  }

  clearFilter(): void {
    this.filter = { showCompleted: true, searchText: '' };
    this.applyFilter();
  }

  private applyFilter(): void {
    this.filteredTasks = taskService.filterTasks(this.tasks, this.filter);
  }

  selectTask(task: Task | null): void {
    this.selectedTask = task;
  }

  // 格式化显示
  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('zh-CN');
  }

  getPriorityLabel(priority: Task['priority']): string {
    const labels = { high: '高', medium: '中', low: '低' };
    return labels[priority];
  }

  getPriorityClass(priority: Task['priority']): string {
    return `priority-${priority}`;
  }
}
```

### View - 视图层（Vue组件风格）
```vue
<!-- views/task.view.vue -->
<template>
  <div class="task-app">
    <h1>任务管理系统</h1>
    
    <!-- 筛选器 -->
    <div class="filter-bar">
      <input 
        v-model="viewModel.filter.searchText" 
        placeholder="搜索任务..."
        @input="onFilterChange"
      />
      <label>
        <input 
          type="checkbox" 
          v-model="viewModel.filter.showCompleted"
          @change="onFilterChange"
        />
        显示已完成
      </label>
      <select v-model="viewModel.filter.priority" @change="onFilterChange">
        <option value="">全部优先级</option>
        <option value="high">高</option>
        <option value="medium">中</option>
        <option value="low">低</option>
      </select>
    </div>

    <!-- 统计 -->
    <div class="stats">
      <span>待办: {{ viewModel.pendingCount }}</span>
      <span>已完成: {{ viewModel.completedCount }}</span>
      <span>总计: {{ viewModel.totalCount }}</span>
    </div>

    <!-- 加载状态 -->
    <div v-if="viewModel.isLoading" class="loading">
      加载中...
    </div>

    <!-- 错误提示 -->
    <div v-if="viewModel.error" class="error">
      {{ viewModel.error }}
    </div>

    <!-- 任务列表 -->
    <ul class="task-list">
      <li 
        v-for="task in viewModel.sortedTasks" 
        :key="task.id"
        :class="['task-item', { completed: task.completed }]"
      >
        <input 
          type="checkbox" 
          :checked="task.completed"
          @change="viewModel.toggleComplete(task)"
        />
        <div class="task-content">
          <strong>{{ task.title }}</strong>
          <p>{{ task.description }}</p>
          <small>
            优先级: <span :class="viewModel.getPriorityClass(task.priority)">
              {{ viewModel.getPriorityLabel(task.priority) }}
            </span>
            | 创建于: {{ viewModel.formatDate(task.createdAt) }}
          </small>
        </div>
        <button @click="viewModel.deleteTask(task.id)">删除</button>
      </li>
    </ul>

    <!-- 新建任务 -->
    <div class="new-task-form">
      <h3>新建任务</h3>
      <input v-model="newTitle" placeholder="任务标题" />
      <textarea v-model="newDesc" placeholder="任务描述"></textarea>
      <select v-model="newPriority">
        <option value="low">低优先级</option>
        <option value="medium">中优先级</option>
        <option value="high">高优先级</option>
      </select>
      <button @click="handleCreate">创建</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { TaskViewModel } from '../viewmodels/task.viewmodel';
import type { Task } from '../models/task.model';

const viewModel = new TaskViewModel();

const newTitle = ref('');
const newDesc = ref('');
const newPriority = ref<Task['priority']>('medium');

onMounted(() => {
  viewModel.loadTasks();
});

function onFilterChange() {
  viewModel.setFilter({
    searchText: viewModel.filter.searchText,
    showCompleted: viewModel.filter.showCompleted,
    priority: viewModel.filter.priority as Task['priority'] | undefined
  });
}

async function handleCreate() {
  if (!newTitle.value.trim()) return;
  
  const success = await viewModel.createTask(
    newTitle.value,
    newDesc.value,
    newPriority.value
  );
  
  if (success) {
    newTitle.value = '';
    newDesc.value = '';
    newPriority.value = 'medium';
  }
}
</script>

<style scoped>
.task-app { max-width: 800px; margin: 0 auto; padding: 20px; }
.filter-bar { display: flex; gap: 10px; margin-bottom: 20px; }
.stats { display: flex; gap: 20px; margin-bottom: 20px; }
.task-list { list-style: none; padding: 0; }
.task-item { display: flex; gap: 10px; padding: 10px; border: 1px solid #ddd; margin-bottom: 10px; }
.task-item.completed { opacity: 0.6; }
.priority-high { color: red; }
.priority-medium { color: orange; }
.priority-low { color: green; }
</style>
```

## 架构优势

1. **数据绑定**：ViewModel变化自动更新View
2. **双向通信**：View操作通过ViewModel调用Service
3. **清晰分层**：Model纯粹数据，ViewModel处理逻辑，View专注展示
4. **易于测试**：ViewModel可单独测试
5. **响应式**：计算属性自动更新
