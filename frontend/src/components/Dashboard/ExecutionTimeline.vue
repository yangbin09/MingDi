<template>
  <el-card shadow="never" class="timeline-card">
    <template #header>
      <div class="timeline-header">
        <div class="flex items-center gap-3">
          <div class="header-indicator"></div>
          <span class="font-semibold">任务执行时间轴</span>
        </div>
        <el-tag size="small">最近 24 小时</el-tag>
      </div>
    </template>

    <el-empty v-if="items.length === 0" description="暂无执行记录" />

    <div v-else class="timeline-container">
      <!-- Timeline track -->
      <div class="timeline-track"></div>

      <!-- Timeline items -->
      <div class="timeline-items">
        <div v-for="item in items" :key="item.id" class="timeline-item">
          <div
            class="timeline-dot"
            :style="{
              backgroundColor: item.status === 'success' ? 'var(--color-success)' : 'var(--color-danger)',
              boxShadow: item.status === 'success' ? 'var(--shadow-glow)' : 'none'
            }"
          ></div>

          <div class="timeline-content">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="font-medium text-sm">{{ item.task_name }}</span>
                <el-tag
                  :type="item.status === 'success' ? 'success' : 'danger'"
                  size="small"
                >
                  {{ item.status === 'success' ? '成功' : '失败' }}
                </el-tag>
              </div>
              <span class="text-xs" style="color: var(--text-muted);">{{ formatTime(item.start_time) }}</span>
            </div>
            <div class="flex items-center gap-4 mt-1 text-xs" style="color: var(--text-muted);">
              <span v-if="item.duration" class="font-mono">{{ item.duration.toFixed(1) }}s</span>
              <span class="font-mono">exit {{ item.exit_code }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
})

function formatTime(timeStr) {
  if (!timeStr) return '-'
  const d = new Date(timeStr)
  return d.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.timeline-card {
  height: 100%;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-indicator {
  width: 24px;
  height: 4px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--color-primary), var(--color-success));
}

.timeline-container {
  position: relative;
}

.timeline-track {
  position: absolute;
  left: 7px;
  top: var(--space-sm);
  bottom: var(--space-sm);
  width: 2px;
  background: linear-gradient(180deg, var(--color-primary), var(--color-success), var(--border-subtle));
}

.timeline-items {
  max-height: 320px;
  overflow-y: auto;
}

.timeline-item {
  position: relative;
  padding-left: 32px;
  padding-bottom: var(--space-md);
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: 4px;
  top: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid var(--bg-secondary);
}

.timeline-content {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-md);
}
</style>
