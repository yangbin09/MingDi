<template>
  <div class="space-y-6">
    <!-- System Metrics Cards with Mini Charts -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- CPU -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <CpuChipIcon class="w-4 h-4 text-blue-400" />
            </div>
            <span class="text-sm text-gray-400">CPU</span>
          </div>
          <span class="text-xl font-bold text-white">{{ systemStats.cpu_percent.toFixed(1) }}%</span>
        </div>
        <div ref="cpuChart" class="h-16"></div>
      </div>

      <!-- Memory -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <CircleStackIcon class="w-4 h-4 text-purple-400" />
            </div>
            <span class="text-sm text-gray-400">内存</span>
          </div>
          <span class="text-xl font-bold text-white">{{ systemStats.memory_percent.toFixed(1) }}%</span>
        </div>
        <div ref="memoryChart" class="h-16"></div>
        <div class="text-xs text-gray-500 mt-1">{{ systemStats.memory_used_gb }} / {{ systemStats.memory_total_gb }} GB</div>
      </div>

      <!-- Disk -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-emerald-500/20 rounded-lg flex items-center justify-center">
              <ServerIcon class="w-4 h-4 text-emerald-400" />
            </div>
            <span class="text-sm text-gray-400">磁盘</span>
          </div>
          <span class="text-xl font-bold text-white">{{ systemStats.disk_percent.toFixed(1) }}%</span>
        </div>
        <div ref="diskChart" class="h-16"></div>
        <div class="text-xs text-gray-500 mt-1">{{ systemStats.disk_used_gb }} / {{ systemStats.disk_total_gb }} GB</div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Total Tasks -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">总任务数</p>
            <p class="text-3xl font-bold mt-2 text-white">{{ stats.total }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
            <ListBulletIcon class="w-6 h-6 text-blue-400" />
          </div>
        </div>
      </div>

      <!-- Running -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors relative overflow-hidden">
        <!-- Breathing light effect -->
        <div v-if="stats.running > 0" class="absolute inset-0 bg-emerald-500/5 animate-pulse-slow"></div>
        <div class="relative flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">运行中</p>
            <p class="text-3xl font-bold mt-2 text-emerald-400">{{ stats.running }}</p>
          </div>
          <div class="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
            <PlayIcon class="w-6 h-6 text-emerald-400" />
          </div>
        </div>
      </div>

      <!-- Failed Today -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">今日失败</p>
            <p class="text-3xl font-bold mt-2 text-red-400">{{ stats.failedToday }}</p>
          </div>
          <div class="w-12 h-12 bg-red-500/20 rounded-xl flex items-center justify-center">
            <ExclamationTriangleIcon class="w-6 h-6 text-red-400" />
          </div>
        </div>
      </div>

      <!-- Success Rate -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">成功率</p>
            <p class="text-3xl font-bold mt-2 text-white">{{ stats.successRate }}%</p>
          </div>
          <div class="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
            <ChartPieIcon class="w-6 h-6 text-purple-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- Timeline & Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Task Execution Timeline -->
      <div class="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-xl">
        <div class="p-4 border-b border-gray-800 flex items-center justify-between">
          <h2 class="text-lg font-semibold">任务执行时间轴</h2>
          <span class="text-xs text-gray-500">最近 24 小时</span>
        </div>
        <div class="p-4">
          <div v-if="timeline.length === 0" class="text-center text-gray-500 py-8">
            暂无执行记录
          </div>
          <div v-else class="relative">
            <!-- Timeline track -->
            <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-800"></div>

            <!-- Timeline items -->
            <div class="space-y-4 max-h-80 overflow-y-auto">
              <div v-for="item in timeline" :key="item.id" class="relative pl-10">
                <!-- Timeline dot -->
                <div class="absolute left-2.5 w-3 h-3 rounded-full border-2"
                  :class="item.status === 'success' ? 'bg-emerald-500 border-emerald-500' : 'bg-red-500 border-red-500'"
                ></div>

                <!-- Content -->
                <div class="bg-gray-800/50 rounded-lg p-3 hover:bg-gray-800 transition">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-sm">{{ item.task_name }}</span>
                      <span v-if="item.exit_code === 0" class="text-xs px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400">成功</span>
                      <span v-else class="text-xs px-1.5 py-0.5 rounded bg-red-500/20 text-red-400">失败</span>
                    </div>
                    <span class="text-xs text-gray-500">{{ formatTime(item.start_time) }}</span>
                  </div>
                  <div class="flex items-center gap-4 mt-1 text-xs text-gray-500">
                    <span v-if="item.duration">{{ item.duration.toFixed(1) }}s</span>
                    <span>exit {{ item.exit_code }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl">
        <div class="p-4 border-b border-gray-800">
          <h2 class="text-lg font-semibold">快捷操作</h2>
        </div>
        <div class="p-4 space-y-3">
          <router-link to="/tasks" class="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition">
            <PlusIcon class="w-5 h-5 text-emerald-400" />
            <span>新建任务</span>
          </router-link>
          <router-link to="/tasks" class="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition">
            <PlayIcon class="w-5 h-5 text-blue-400" />
            <span>查看所有任务</span>
          </router-link>
          <button @click="$emit('openScratchpad')" class="w-full flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition text-left">
            <CodeBracketIcon class="w-5 h-5 text-purple-400" />
            <span>快速执行代码</span>
          </button>
          <router-link to="/settings" class="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition">
            <Cog6ToothIcon class="w-5 h-5 text-gray-400" />
            <span>系统设置</span>
          </router-link>
        </div>

        <!-- Recent Tasks Mini List -->
        <div class="p-4 border-t border-gray-800">
          <h3 class="text-sm font-medium text-gray-400 mb-3">最近任务</h3>
          <div v-if="recentTasks.length === 0" class="text-center text-gray-500 py-4 text-sm">
            暂无任务
          </div>
          <div v-else class="space-y-2">
            <div v-for="task in recentTasks" :key="task.id" class="flex items-center justify-between p-2 bg-gray-800/30 rounded-lg">
              <div class="flex items-center gap-2">
                <!-- Breathing dot for running -->
                <span class="relative flex h-2 w-2">
                  <span v-if="task.status === 'running'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2" :class="statusDotClass(task.status)"></span>
                </span>
                <span class="text-sm truncate max-w-[120px]">{{ task.name }}</span>
              </div>
              <span class="text-xs text-gray-500">{{ statusText(task.status) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import {
  ListBulletIcon, PlayIcon, ExclamationTriangleIcon, ChartPieIcon,
  PlusIcon, CpuChipIcon, CircleStackIcon, ServerIcon,
  CodeBracketIcon, Cog6ToothIcon
} from '@heroicons/vue/24/outline'

const emit = defineEmits(['openScratchpad'])

const api = axios.create({ baseURL: 'http://localhost:8000' })

const tasks = ref([])
const timeline = ref([])
const systemStats = ref({ cpu_percent: 0, memory_percent: 0, disk_percent: 0, memory_used_gb: 0, memory_total_gb: 0, disk_used_gb: 0, disk_total_gb: 0 })
const recentTasks = computed(() => tasks.value.slice(0, 5))

// Chart refs
const cpuChart = ref(null)
const memoryChart = ref(null)
const diskChart = ref(null)
let cpuChartInstance = null
let memoryChartInstance = null
let diskChartInstance = null

// History data for charts
const cpuHistory = ref(Array(20).fill(0))
const memoryHistory = ref(Array(20).fill(0))
const diskHistory = ref(Array(20).fill(0))

const stats = computed(() => {
  const total = tasks.value.length
  const running = tasks.value.filter(t => t.status === 'running').length
  const failed = tasks.value.filter(t => t.status === 'failed').length
  const success = tasks.value.filter(t => t.status === 'success').length
  const successRate = total > 0 ? Math.round((success / total) * 100) : 100

  return { total, running, failedToday: failed, successRate }
})

function statusDotClass(status) {
  const classes = { idle: 'bg-gray-500', running: 'bg-emerald-500', success: 'bg-emerald-400', failed: 'bg-red-500', timeout: 'bg-yellow-500' }
  return classes[status] || 'bg-gray-500'
}

function statusText(status) {
  const texts = { idle: '闲置', running: '运行中', success: '成功', failed: '失败', timeout: '超时' }
  return texts[status] || status
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function initCharts() {
  const commonOptions = {
    grid: { left: 0, right: 0, top: 0, bottom: 0 },
    xAxis: { type: 'category', show: false, data: Array(20).fill('') },
    yAxis: { type: 'value', min: 0, max: 100, show: false },
    series: [{ smooth: true, symbol: 'none', lineStyle: { width: 2 }, areaStyle: { opacity: 0.3 } }],
    animation: false
  }

  cpuChartInstance = echarts.init(cpuChart.value)
  cpuChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: '#3b82f6', data: cpuHistory.value }]
  })

  memoryChartInstance = echarts.init(memoryChart.value)
  memoryChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: '#a855f7', data: memoryHistory.value }]
  })

  diskChartInstance = echarts.init(diskChart.value)
  diskChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: '#10b981', data: diskHistory.value }]
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

async function fetchTasks() {
  try {
    const res = await api.get('/tasks')
    tasks.value = res.data
  } catch (e) { console.error(e) }
}

async function fetchTimeline() {
  try {
    const res = await api.get('/tasks/timeline')
    timeline.value = res.data
  } catch (e) { console.error(e) }
}

async function fetchSystemStats() {
  try {
    const res = await api.get('/system/stats')
    systemStats.value = res.data
    updateCharts()
  } catch (e) { console.error(e) }
}

let refreshInterval = null

onMounted(() => {
  fetchTasks()
  fetchTimeline()
  fetchSystemStats()
  initCharts()

  refreshInterval = setInterval(() => {
    fetchTasks()
    fetchTimeline()
    fetchSystemStats()
  }, 5000)

  window.addEventListener('resize', () => {
    cpuChartInstance?.resize()
    memoryChartInstance?.resize()
    diskChartInstance?.resize()
  })
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
  cpuChartInstance?.dispose()
  memoryChartInstance?.dispose()
  diskChartInstance?.dispose()
})
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 0.03; }
  50% { opacity: 0.08; }
}
.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}
</style>
