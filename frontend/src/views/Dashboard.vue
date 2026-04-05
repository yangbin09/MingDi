<template>
  <div class="space-y-6">
    <!-- System Metrics Cards with Mini Charts -->
    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-header">
            <div class="metric-icon" style="background-color: var(--color-primary-subtle);">
              <el-icon :size="20" color="var(--color-primary)"><Cpu /></el-icon>
            </div>
            <span class="metric-label">CPU 使用率</span>
            <span class="metric-value">{{ systemStats.cpu_percent.toFixed(1) }}%</span>
          </div>
          <div ref="cpuChartRef" class="mini-chart"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-header">
            <div class="metric-icon" style="background-color: var(--color-success-subtle);">
              <el-icon :size="20" color="var(--color-success)"><Monitor /></el-icon>
            </div>
            <span class="metric-label">内存使用</span>
            <span class="metric-value">{{ systemStats.memory_percent.toFixed(1) }}%</span>
          </div>
          <div ref="memoryChartRef" class="mini-chart"></div>
          <div class="metric-footer">{{ systemStats.memory_used_gb }} / {{ systemStats.memory_total_gb }} GB</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-header">
            <div class="metric-icon" style="background-color: var(--color-danger-subtle);">
              <el-icon :size="20" color="var(--color-danger)"><Box /></el-icon>
            </div>
            <span class="metric-label">磁盘占用</span>
            <span class="metric-value">{{ systemStats.disk_percent.toFixed(1) }}%</span>
          </div>
          <div ref="diskChartRef" class="mini-chart"></div>
          <div class="metric-footer">{{ systemStats.disk_used_gb }} / {{ systemStats.disk_total_gb }} GB</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Stats Cards -->
    <el-row :gutter="16">
      <el-col :xs="12" :md="6">
        <StatsCard
          label="总任务数"
          :value="stats.total"
          :icon="List"
          icon-bg-color="var(--color-primary-subtle)"
          icon-color="var(--color-primary)"
        />
      </el-col>
      <el-col :xs="12" :md="6">
        <StatsCard
          label="运行中"
          :value="stats.running"
          :icon="VideoPlay"
          icon-bg-color="var(--color-primary-subtle)"
          icon-color="var(--color-primary)"
          :value-color="stats.running > 0 ? 'var(--color-primary)' : 'var(--text-main)'"
        />
      </el-col>
      <el-col :xs="12" :md="6">
        <StatsCard
          label="今日失败"
          :value="stats.failedToday"
          :icon="Warning"
          icon-bg-color="var(--color-danger-subtle)"
          icon-color="var(--color-danger)"
          :value-color="stats.failedToday > 0 ? 'var(--color-danger)' : 'var(--text-main)'"
        />
      </el-col>
      <el-col :xs="12" :md="6">
        <StatsCard
          label="成功率"
          :value="stats.successRate + '%'"
          :icon="PieChart"
          icon-bg-color="rgba(168, 85, 247, 0.15)"
          icon-color="var(--color-purple)"
        />
      </el-col>
    </el-row>

    <!-- Timeline & Quick Actions -->
    <el-row :gutter="24">
      <el-col :xs="24" :lg="16">
        <ExecutionTimeline :items="timeline" />
      </el-col>
      <el-col :xs="24" :lg="8">
        <QuickActions :tasks="recentTasks" @action="handleQuickAction" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Cpu, Monitor, Box, List, VideoPlay, Warning, PieChart } from '@element-plus/icons-vue'
import { useDashboardStats } from '../composables/useDashboardStats.ts'
import { useDashboardCharts } from '../composables/useDashboardCharts.ts'
import StatsCard from '../components/Dashboard/StatsCard.vue'
import ExecutionTimeline from '../components/Dashboard/ExecutionTimeline.vue'
import QuickActions from '../components/Dashboard/QuickActions.vue'

const emit = defineEmits(['openScratchpad'])

// 图表 DOM refs
const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const diskChartRef = ref(null)

// 数据统计
const {
  tasks,
  timeline,
  systemStats,
  recentTasks,
  stats,
  fetchAllData,
  startPolling,
  stopPolling
} = useDashboardStats()

// 图表管理
const {
  updateCharts,
  initCharts,
  setupResizeListener,
  disposeCharts
} = useDashboardCharts()

let cleanupResize = null

function handleQuickAction(action) {
  if (action === 'scratchpad') {
    emit('openScratchpad')
  }
}

onMounted(async () => {
  await fetchAllData()
  initCharts(cpuChartRef.value, memoryChartRef.value, diskChartRef.value)
  updateCharts(systemStats.value)
  startPolling()
  cleanupResize = setupResizeListener()
})

onUnmounted(() => {
  stopPolling()
  cleanupResize?.()
  disposeCharts()
})
</script>

<style scoped>
.metric-card {
  height: 100%;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.metric-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-label {
  flex: 1;
  font-size: var(--font-size-base);
  color: var(--text-muted);
}

.metric-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-main);
}

.mini-chart {
  height: 48px;
  width: 100%;
}

.metric-footer {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  margin-top: var(--space-sm);
}
</style>
