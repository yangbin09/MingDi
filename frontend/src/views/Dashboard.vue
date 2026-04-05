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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { Cpu, Monitor, Box, List, VideoPlay, Warning, PieChart } from '@element-plus/icons-vue'
import { taskApi, systemApi } from '../utils/api.js'
import { usePolling } from '../composables/usePolling.js'
import StatsCard from '../components/Dashboard/StatsCard.vue'
import ExecutionTimeline from '../components/Dashboard/ExecutionTimeline.vue'
import QuickActions from '../components/Dashboard/QuickActions.vue'

const emit = defineEmits(['openScratchpad'])

const tasks = ref([])
const timeline = ref([])
const systemStats = ref({
  cpu_percent: 0,
  memory_percent: 0,
  disk_percent: 0,
  memory_used_gb: 0,
  memory_total_gb: 0,
  disk_used_gb: 0,
  disk_total_gb: 0
})

const recentTasks = computed(() => tasks.value.slice(0, 5))

const stats = computed(() => {
  const total = tasks.value.length
  const running = tasks.value.filter(t => t.status === 'running').length
  const failed = tasks.value.filter(t => t.status === 'failed').length
  const success = tasks.value.filter(t => t.status === 'success').length
  const successRate = total > 0 ? Math.round((success / total) * 100) : 100
  return { total, running, failedToday: failed, successRate }
})

// Chart refs
const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const diskChartRef = ref(null)
let cpuChartInstance = null
let memoryChartInstance = null
let diskChartInstance = null

// History data for charts
const cpuHistory = ref(Array(20).fill(0))
const memoryHistory = ref(Array(20).fill(0))
const diskHistory = ref(Array(20).fill(0))

function getChartColor(theme) {
  if (theme === 'darcula') return '#3592C4'
  if (theme === 'onedark') return '#61AFEF'
  if (theme === 'gruvbox') return '#D65D0E'
  if (theme === 'intellij') return '#3592C4'
  return '#6366F1'
}

function initCharts() {
  const theme = document.documentElement.getAttribute('data-theme') || 'darcula'
  const primaryColor = getChartColor(theme)

  const commonOptions = {
    grid: { left: 0, right: 0, top: 2, bottom: 0 },
    xAxis: { type: 'category', show: false, data: Array(20).fill('') },
    yAxis: { type: 'value', min: 0, max: 100, show: false },
    series: [{ smooth: true, symbol: 'none', lineStyle: { width: 2 }, areaStyle: { opacity: 0.2 } }],
    animation: true,
    animationDuration: 300
  }

  cpuChartInstance = echarts.init(cpuChartRef.value)
  cpuChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: primaryColor, data: cpuHistory.value }]
  })

  memoryChartInstance = echarts.init(memoryChartRef.value)
  const successColor = theme === 'darcula' ? '#67965A' : theme === 'onedark' ? '#98C379' : theme === 'gruvbox' ? '#98971A' : '#488B49'
  memoryChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: successColor, data: memoryHistory.value }]
  })

  diskChartInstance = echarts.init(diskChartRef.value)
  const dangerColor = theme === 'darcula' ? '#E43F3F' : theme === 'onedark' ? '#E06C75' : theme === 'gruvbox' ? '#CC241D' : '#D04438'
  diskChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: dangerColor, data: diskHistory.value }]
  })
}

function updateCharts() {
  if (cpuChartInstance) {
    cpuHistory.value.push(systemStats.value.cpu_percent)
    cpuHistory.value.shift()
    cpuChartInstance.setOption({ series: [{ data: cpuHistory.value }] })
  }
  if (memoryChartInstance) {
    memoryHistory.value.push(systemStats.value.memory_percent)
    memoryHistory.value.shift()
    memoryChartInstance.setOption({ series: [{ data: memoryHistory.value }] })
  }
  if (diskChartInstance) {
    diskHistory.value.push(systemStats.value.disk_percent)
    diskHistory.value.shift()
    diskChartInstance.setOption({ series: [{ data: diskHistory.value }] })
  }
}

async function fetchAllData() {
  await Promise.all([fetchTasks(), fetchTimeline(), fetchSystemStats()])
  updateCharts()
}

async function fetchTasksData() {
  try {
    const res = await taskApi.list()
    tasks.value = res.data
  } catch (e) { console.error(e) }
}

async function fetchTasks() {
  try {
    const res = await taskApi.list()
    tasks.value = res.data
  } catch (e) { console.error(e) }
}

async function fetchTimeline() {
  try {
    const res = await taskApi.timeline()
    timeline.value = res.data
  } catch (e) { console.error(e) }
}

async function fetchSystemStats() {
  try {
    const res = await systemApi.stats()
    systemStats.value = res.data
  } catch (e) { console.error(e) }
}

// Set up polling
const { start: startPolling, stop: stopPolling } = usePolling(fetchAllData, 5000)

function handleQuickAction(action) {
  if (action === 'scratchpad') {
    emit('openScratchpad')
  }
}

onMounted(() => {
  fetchAllData()
  initCharts()
  startPolling()

  window.addEventListener('resize', handleResize)
})

function handleResize() {
  cpuChartInstance?.resize()
  memoryChartInstance?.resize()
  diskChartInstance?.resize()
}

onUnmounted(() => {
  stopPolling()
  window.removeEventListener('resize', handleResize)
  cpuChartInstance?.dispose()
  memoryChartInstance?.dispose()
  diskChartInstance?.dispose()
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
