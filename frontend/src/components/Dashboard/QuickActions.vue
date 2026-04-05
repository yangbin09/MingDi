<template>
  <el-card shadow="never" class="actions-card">
    <template #header>
      <div class="flex items-center gap-3">
        <div class="header-indicator"></div>
        <span class="font-semibold">快捷操作</span>
      </div>
    </template>

    <div class="actions-list">
      <router-link
        to="/tasks"
        class="action-item action-primary"
        @click="$emit('action', 'new-task')"
      >
        <div class="action-icon">
          <el-icon><Plus /></el-icon>
        </div>
        <span class="font-medium">新建任务</span>
      </router-link>

      <router-link
        to="/tasks"
        class="action-item"
        @click="$emit('action', 'all-tasks')"
      >
        <div class="action-icon">
          <el-icon><VideoPlay /></el-icon>
        </div>
        <span class="font-medium">查看所有任务</span>
      </router-link>

      <button
        class="action-item w-full"
        @click="$emit('action', 'scratchpad')"
      >
        <div class="action-icon">
          <el-icon><Cpu /></el-icon>
        </div>
        <span class="font-medium">快速执行代码</span>
      </button>

      <router-link
        to="/settings"
        class="action-item"
        @click="$emit('action', 'settings')"
      >
        <div class="action-icon">
          <el-icon><Setting /></el-icon>
        </div>
        <span class="font-medium">系统设置</span>
      </router-link>
    </div>

    <!-- Recent Tasks Mini List -->
    <div class="recent-tasks">
      <div class="section-header">最近任务</div>
      <el-empty v-if="tasks.length === 0" description="暂无任务" :image-size="60" />

      <div v-else class="recent-list">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="recent-item"
        >
          <div class="flex items-center gap-2">
            <span class="status-dot" :style="{ backgroundColor: getStatusColor(task.status) }"></span>
            <span class="task-name">{{ task.name }}</span>
          </div>
          <el-tag size="small" :type="getStatusType(task.status)">
            {{ getStatusText(task.status) }}
          </el-tag>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { Plus, VideoPlay, Cpu, Setting } from '@element-plus/icons-vue'

defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
})

defineEmits(['action'])

function getStatusColor(status) {
  const colors = {
    running: 'var(--color-primary)',
    success: 'var(--color-success)',
    failed: 'var(--color-danger)',
    timeout: 'var(--color-warning)',
    idle: 'var(--text-muted)'
  }
  return colors[status] || 'var(--text-muted)'
}

function getStatusType(status) {
  const types = {
    running: '',
    success: 'success',
    failed: 'danger',
    timeout: 'warning',
    idle: 'info'
  }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = {
    running: '运行中',
    success: '成功',
    failed: '失败',
    timeout: '超时',
    idle: '空闲'
  }
  return texts[status] || status
}
</script>

<style scoped>
.actions-card {
  height: 100%;
}

.header-indicator {
  width: 24px;
  height: 4px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--color-primary), var(--color-purple));
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.action-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--text-main);
  background-color: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-base);
}

.action-item:hover {
  background-color: var(--bg-hover);
  border-color: var(--border-subtle);
}

.action-primary {
  background-color: var(--color-primary-subtle);
  border-color: var(--border-subtle);
}

.action-primary:hover {
  background-color: var(--bg-hover);
}

.action-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-primary-subtle);
  color: var(--color-primary);
}

.recent-tasks {
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-subtle);
}

.section-header {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--text-muted);
  margin-bottom: var(--space-md);
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm);
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.task-name {
  font-size: var(--font-size-base);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
