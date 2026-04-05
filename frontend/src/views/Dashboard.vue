<template>
  <div class="space-y-6">
    <!-- System Metrics Cards with Mini Charts -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- CPU -->
      <div class="bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-xl p-5 card-hover bg-gradient-card">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-indigo-500/10 rounded-lg flex items-center justify-center border border-indigo-500/20">
              <CpuChipIcon class="w-5 h-5 text-indigo-400" />
            </div>
            <span class="text-sm font-medium text-gray-400">CPU 使用率</span>
          </div>
          <span class="text-2xl font-bold text-gray-100">{{ systemStats.cpu_percent.toFixed(1) }}<span class="text-sm text-gray-500">%</span></span>
        </div>
        <div ref="cpuChart" class="h-16"></div>
      </div>

      <!-- Memory -->
      <div class="bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-xl p-5 card-hover bg-gradient-card">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-emerald-500/10 rounded-lg flex items-center justify-center border border-emerald-500/20">
              <CircleStackIcon class="w-5 h-5 text-emerald-400" />
            </div>
            <span class="text-sm font-medium text-gray-400">内存使用</span>
          </div>
          <span class="text-2xl font-bold text-gray-100">{{ systemStats.memory_percent.toFixed(1) }}<span class="text-sm text-gray-500">%</span></span>
        </div>
        <div ref="memoryChart" class="h-16"></div>
        <div class="text-xs text-gray-500 mt-2">{{ systemStats.memory_used_gb }} / {{ systemStats.memory_total_gb }} GB</div>
      </div>

      <!-- Disk -->
      <div class="bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-xl p-5 card-hover bg-gradient-card">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-rose-500/10 rounded-lg flex items-center justify-center border border-rose-500/20">
              <ServerIcon class="w-5 h-5 text-rose-400" />
            </div>
            <span class="text-sm font-medium text-gray-400">磁盘占用</span>
          </div>
          <span class="text-2xl font-bold text-gray-100">{{ systemStats.disk_percent.toFixed(1) }}<span class="text-sm text-gray-500">%</span></span>
        </div>
        <div ref="diskChart" class="h-16"></div>
        <div class="text-xs text-gray-500 mt-2">{{ systemStats.disk_used_gb }} / {{ systemStats.disk_total_gb }} GB</div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Total Tasks -->
      <div class="bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-xl p-5 card-hover bg-gradient-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 font-medium">总任务数</p>
            <p class="text-3xl font-bold mt-1 text-gray-100">{{ stats.total }}</p>
          </div>
          <div class="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center border border-indigo-500/20">
            <ListBulletIcon class="w-6 h-6 text-indigo-400" />
          </div>
        </div>
      </div>

      <!-- Running -->
      <div class="bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-xl p-5 card-hover bg-gradient-card relative overflow-hidden" :class="{ 'border-emerald-500/30': stats.running > 0 }">
        <div v-if="stats.running > 0" class="absolute inset-0 bg-gradient-to-r from-emerald-500/5 to-transparent animate-pulse-soft"></div>
        <div class="relative flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 font-medium">运行中</p>
            <p class="text-3xl font-bold mt-1" :class="stats.running > 0 ? 'text-emerald-400' : 'text-gray-100'">{{ stats.running }}</p>
          </div>
          <div class="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center border border-emerald-500/20" :class="{ 'shadow-emerald-glow': stats.running > 0 }">
            <PlayIcon class="w-6 h-6 text-emerald-400" />
          </div>
        </div>
      </div>

      <!-- Failed Today -->
      <div class="bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-xl p-5 card-hover bg-gradient-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 font-medium">今日失败</p>
            <p class="text-3xl font-bold mt-1" :class="stats.failedToday > 0 ? 'text-rose-400' : 'text-gray-100'">{{ stats.failedToday }}</p>
          </div>
          <div class="w-12 h-12 bg-rose-500/10 rounded-xl flex items-center justify-center border border-rose-500/20">
            <ExclamationTriangleIcon class="w-6 h-6 text-rose-400" />
          </div>
        </div>
      </div>

      <!-- Success Rate -->
      <div class="bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-xl p-5 card-hover bg-gradient-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 font-medium">成功率</p>
            <p class="text-3xl font-bold mt-1 text-gray-100">{{ stats.successRate }}<span class="text-lg text-gray-500">%</span></p>
          </div>
          <div class="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center border border-purple-500/20">
            <ChartPieIcon class="w-6 h-6 text-purple-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- Timeline & Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Task Execution Timeline -->
      <div class="lg:col-span-2 bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-xl">
        <div class="p-5 border-b border-gray-700/50 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="h-1 w-6 bg-gradient-to-r from-indigo-500 to-emerald-500 rounded-full"></div>
            <h2 class="text-lg font-semibold text-gray-100">任务执行时间轴</h2>
          </div>
          <span class="text-xs text-gray-500 bg-gray-800/50 px-2 py-1 rounded">最近 24 小时</span>
        </div>
        <div class="p-5">
          <div v-if="timeline.length === 0" class="text-center text-gray-500 py-12">
            <div class="w-16 h-16 mx-auto mb-4 bg-gray-800/50 rounded-full flex items-center justify-center">
              <ClockIcon class="w-8 h-8 opacity-50" />
            </div>
            <p>暂无执行记录</p>
            <p class="text-xs mt-1">任务执行后将显示在这里</p>
          </div>
          <div v-else class="relative">
            <!-- Timeline track -->
            <div class="absolute left-4 top-2 bottom-2 w-px bg-gradient-to-b from-indigo-500/50 via-emerald-500/50 to-gray-700/50"></div>

            <!-- Timeline items -->
            <div class="space-y-4 max-h-80 overflow-y-auto pr-2">
              <div v-for="item in timeline" :key="item.id" class="relative pl-10">
                <!-- Timeline dot -->
                <div class="absolute left-2.5 top-3 w-3 h-3 rounded-full border-2"
                  :class="item.status === 'success' ? 'bg-emerald-500 border-emerald-500 shadow-emerald-glow' : 'bg-rose-500 border-rose-500 shadow-rose-glow'"
                ></div>

                <!-- Content -->
                <div class="bg-gray-800/50 rounded-lg p-3 hover:bg-gray-800 transition-all duration-200 border border-gray-700/50">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-sm text-gray-200">{{ item.task_name }}</span>
                      <span v-if="item.exit_code === 0" class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">成功</span>
                      <span v-else class="text-xs px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">失败</span>
                    </div>
                    <span class="text-xs text-gray-500">{{ formatTime(item.start_time) }}</span>
                  </div>
                  <div class="flex items-center gap-4 mt-1 text-xs text-gray-500">
                    <span v-if="item.duration" class="font-mono">{{ item.duration.toFixed(1) }}s</span>
                    <span class="font-mono">exit {{ item.exit_code }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-xl">
        <div class="p-5 border-b border-gray-700/50">
          <div class="flex items-center gap-3">
            <div class="h-1 w-6 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"></div>
            <h2 class="text-lg font-semibold text-gray-100">快捷操作</h2>
          </div>
        </div>
        <div class="p-4 space-y-3">
          <router-link
            to="/tasks"
            class="flex items-center gap-3 p-3 rounded-lg transition-all duration-200 bg-indigo-500/5 border border-indigo-500/10 hover:bg-indigo-500/10 hover:border-indigo-500/20 group"
          >
            <div class="w-8 h-8 bg-indigo-500/10 rounded-lg flex items-center justify-center group-hover:bg-indigo-500/20 transition-colors">
              <PlusIcon class="w-4 h-4 text-indigo-400" />
            </div>
            <span class="font-medium text-gray-200">新建任务</span>
          </router-link>
          <router-link
            to="/tasks"
            class="flex items-center gap-3 p-3 rounded-lg transition-all duration-200 text-gray-400 hover:bg-gray-800 hover:text-gray-200 border border-transparent hover:border-gray-700/50 group"
          >
            <div class="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center group-hover:bg-emerald-500/10 transition-colors">
              <PlayIcon class="w-4 h-4 group-hover:text-emerald-400" />
            </div>
            <span class="font-medium">查看所有任务</span>
          </router-link>
          <button
            @click="$emit('openScratchpad')"
            class="w-full flex items-center gap-3 p-3 rounded-lg transition-all duration-200 text-gray-400 hover:bg-purple-500/10 hover:text-purple-400 border border-transparent hover:border-purple-500/20 group"
          >
            <div class="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center group-hover:bg-purple-500/20 transition-colors">
              <CodeBracketIcon class="w-4 h-4" />
            </div>
            <span class="font-medium">快速执行代码</span>
          </button>
          <router-link
            to="/settings"
            class="flex items-center gap-3 p-3 rounded-lg transition-all duration-200 text-gray-400 hover:bg-gray-800 hover:text-gray-200 border border-transparent hover:border-gray-700/50 group"
          >
            <div class="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center group-hover:bg-gray-700 transition-colors">
              <Cog6ToothIcon class="w-4 h-4" />
            </div>
            <span class="font-medium">系统设置</span>
          </router-link>
        </div>

        <!-- Recent Tasks Mini List -->
        <div class="p-5 border-t border-gray-700/50">
          <h3 class="text-sm font-medium text-gray-500 mb-3">最近任务</h3>
          <div v-if="recentTasks.length === 0" class="text-center text-gray-600 py-4 text-sm">
            暂无任务
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="task in recentTasks"
              :key="task.id"
              class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-800/50 transition-colors"
            >
              <div class="flex items-center gap-2">
                <!-- Status dot -->
                <span class="relative flex h-2 w-2">
                  <span v-if="task.status === 'running'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span
                    class="relative inline-flex rounded-full h-2 w-2"
                    :class="{
                      'bg-emerald-500': task.status === 'running' || task.status === 'success',
                      'bg-rose-500': task.status === 'failed',
                      'bg-yellow-500': task.status === 'timeout',
                      'bg-gray-600': task.status === 'idle'
                    }"
                  ></span>
                </span>
                <span class="text-sm text-gray-300 truncate max-w-[120px]">{{ task.name }}</span>
              </div>
              <span class="text-xs px-2 py-0.5 rounded-full" :class="{
                'bg-emerald-500/10 text-emerald-400': task.status === 'success',
                'bg-rose-500/10 text-rose-400': task.status === 'failed',
                'bg-yellow-500/10 text-yellow-400': task.status === 'timeout',
                'bg-indigo-500/10 text-indigo-400': task.status === 'running',
                'bg-gray-700/50 text-gray-500': task.status === 'idle'
              }">
                {{ statusText(task.status) }}
              </span>
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
  CodeBracketIcon, Cog6ToothIcon, ClockIcon
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
    grid: { left: 0, right: 0, top: 2, bottom: 0 },
    xAxis: { type: 'category', show: false, data: Array(20).fill('') },
    yAxis: { type: 'value', min: 0, max: 100, show: false },
    series: [{ smooth: true, symbol: 'none', lineStyle: { width: 2 }, areaStyle: { opacity: 0.2 } }],
    animation: true,
    animationDuration: 300
  }

  cpuChartInstance = echarts.init(cpuChart.value)
  cpuChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: '#6366F1', data: cpuHistory.value, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(99, 102, 241, 0.3)' }, { offset: 1, color: 'rgba(99, 102, 241, 0.05)' }]) } }]
  })

  memoryChartInstance = echarts.init(memoryChart.value)
  memoryChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: '#10B981', data: memoryHistory.value, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(16, 185, 129, 0.3)' }, { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }]) } }]
  })

  diskChartInstance = echarts.init(diskChart.value)
  diskChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: '#F43F5E', data: diskHistory.value, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(244, 63, 94, 0.3)' }, { offset: 1, color: 'rgba(244, 63, 94, 0.05)' }]) } }]
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
.card-hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.card-hover:hover {
  transform: translateY(-2px);
}
</style>
