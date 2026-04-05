<template>
  <div class="space-y-6">
    <!-- System Metrics Cards with Mini Charts -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- CPU -->
      <div class="card-hover rounded-xl p-5 theme-transition">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :style="{ backgroundColor: 'var(--color-primary-subtle)', border: '1px solid var(--color-primary)' }"
            >
              <CpuChipIcon class="w-5 h-5" style="color: var(--color-primary);" />
            </div>
            <span class="text-sm font-medium" style="color: var(--text-muted);">CPU 使用率</span>
          </div>
          <span class="text-2xl font-bold" style="color: var(--text-main);">{{ systemStats.cpu_percent.toFixed(1) }}<span class="text-sm" style="color: var(--text-muted);">%</span></span>
        </div>
        <div ref="cpuChart" class="h-16"></div>
      </div>

      <!-- Memory -->
      <div class="card-hover rounded-xl p-5 theme-transition">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :style="{ backgroundColor: 'var(--color-success-subtle)', border: '1px solid var(--color-success)' }"
            >
              <CircleStackIcon class="w-5 h-5" style="color: var(--color-success);" />
            </div>
            <span class="text-sm font-medium" style="color: var(--text-muted);">内存使用</span>
          </div>
          <span class="text-2xl font-bold" style="color: var(--text-main);">{{ systemStats.memory_percent.toFixed(1) }}<span class="text-sm" style="color: var(--text-muted);">%</span></span>
        </div>
        <div ref="memoryChart" class="h-16"></div>
        <div class="text-xs mt-2" style="color: var(--text-muted);">{{ systemStats.memory_used_gb }} / {{ systemStats.memory_total_gb }} GB</div>
      </div>

      <!-- Disk -->
      <div class="card-hover rounded-xl p-5 theme-transition">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :style="{ backgroundColor: 'var(--color-danger-subtle)', border: '1px solid var(--color-danger)' }"
            >
              <ServerIcon class="w-5 h-5" style="color: var(--color-danger);" />
            </div>
            <span class="text-sm font-medium" style="color: var(--text-muted);">磁盘占用</span>
          </div>
          <span class="text-2xl font-bold" style="color: var(--text-main);">{{ systemStats.disk_percent.toFixed(1) }}<span class="text-sm" style="color: var(--text-muted);">%</span></span>
        </div>
        <div ref="diskChart" class="h-16"></div>
        <div class="text-xs mt-2" style="color: var(--text-muted);">{{ systemStats.disk_used_gb }} / {{ systemStats.disk_total_gb }} GB</div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Total Tasks -->
      <div class="card-hover rounded-xl p-5 theme-transition" :style="statsBorder">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm" style="color: var(--text-muted); font-weight: 500;">总任务数</p>
            <p class="text-3xl font-bold mt-1" style="color: var(--text-main);">{{ stats.total }}</p>
          </div>
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center"
            :style="{ backgroundColor: 'var(--color-primary-subtle)', border: '1px solid var(--border-subtle)' }"
          >
            <ListBulletIcon class="w-6 h-6" style="color: var(--color-primary);" />
          </div>
        </div>
      </div>

      <!-- Running -->
      <div
        class="card-hover rounded-xl p-5 theme-transition"
        :style="statsBorder"
        :class="{ 'border-primary': stats.running > 0 }"
      >
        <div v-if="stats.running > 0" class="absolute inset-0 animate-pulse-soft rounded-xl" :style="{ background: 'linear-gradient(90deg, var(--color-primary-subtle), transparent)' }"></div>
        <div class="relative flex items-center justify-between">
          <div>
            <p class="text-sm" style="color: var(--text-muted); font-weight: 500;">运行中</p>
            <p class="text-3xl font-bold mt-1" :style="{ color: stats.running > 0 ? 'var(--color-primary)' : 'var(--text-main)' }">{{ stats.running }}</p>
          </div>
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center"
            :style="{ backgroundColor: 'var(--color-primary-subtle)', border: '1px solid var(--border-subtle)' }"
          >
            <PlayIcon class="w-6 h-6" style="color: var(--color-primary);" />
          </div>
        </div>
      </div>

      <!-- Failed Today -->
      <div class="card-hover rounded-xl p-5 theme-transition" :style="statsBorder">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm" style="color: var(--text-muted); font-weight: 500;">今日失败</p>
            <p class="text-3xl font-bold mt-1" :style="{ color: stats.failedToday > 0 ? 'var(--color-danger)' : 'var(--text-main)' }">{{ stats.failedToday }}</p>
          </div>
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center"
            :style="{ backgroundColor: 'var(--color-danger-subtle)', border: '1px solid var(--border-subtle)' }"
          >
            <ExclamationTriangleIcon class="w-6 h-6" style="color: var(--color-danger);" />
          </div>
        </div>
      </div>

      <!-- Success Rate -->
      <div class="card-hover rounded-xl p-5 theme-transition" :style="statsBorder">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm" style="color: var(--text-muted); font-weight: 500;">成功率</p>
            <p class="text-3xl font-bold mt-1" style="color: var(--text-main);">{{ stats.successRate }}<span class="text-lg" style="color: var(--text-muted);">%</span></p>
          </div>
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center"
            :style="{ backgroundColor: 'rgba(168, 85, 247, 0.15)', border: '1px solid var(--border-subtle)' }"
          >
            <ChartPieIcon class="w-6 h-6" style="color: var(--color-purple);" />
          </div>
        </div>
      </div>
    </div>

    <!-- Timeline & Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Task Execution Timeline -->
      <div class="card rounded-xl lg:col-span-2 theme-transition">
        <div class="p-5 flex items-center justify-between" :style="{ borderBottom: '1px solid var(--border-subtle)' }">
          <div class="flex items-center gap-3">
            <div class="h-1 w-6 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-primary), var(--color-success))' }"></div>
            <h2 class="text-lg font-semibold" style="color: var(--text-main);">任务执行时间轴</h2>
          </div>
          <span class="text-xs px-2 py-1 rounded" :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }">最近 24 小时</span>
        </div>
        <div class="p-5">
          <div v-if="timeline.length === 0" class="text-center py-12">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
              <ClockIcon class="w-8 h-8" style="color: var(--text-muted); opacity: 0.5;" />
            </div>
            <p style="color: var(--text-muted);">暂无执行记录</p>
            <p class="text-xs mt-1" style="color: var(--text-disabled);">任务执行后将显示在这里</p>
          </div>
          <div v-else class="relative">
            <!-- Timeline track -->
            <div
              class="absolute left-4 top-2 bottom-2 w-px"
              :style="{ background: 'linear-gradient(180deg, var(--color-primary), var(--color-success), var(--border-subtle))' }"
            ></div>

            <!-- Timeline items -->
            <div class="space-y-4 max-h-80 overflow-y-auto">
              <div v-for="item in timeline" :key="item.id" class="relative pl-10">
                <!-- Timeline dot -->
                <div
                  class="absolute left-2.5 top-3 w-3 h-3 rounded-full border-2"
                  :style="{
                    backgroundColor: item.status === 'success' ? 'var(--color-success)' : 'var(--color-danger)',
                    boxShadow: item.status === 'success' ? 'var(--shadow-glow)' : 'none'
                  }"
                ></div>

                <!-- Content -->
                <div
                  class="rounded-lg p-3 theme-transition"
                  :style="{ backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)' }"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-sm" style="color: var(--text-main);">{{ item.task_name }}</span>
                      <span
                        class="text-xs px-2 py-0.5 rounded-full"
                        :style="item.status === 'success'
                          ? { backgroundColor: 'var(--color-success-subtle)', color: 'var(--color-success)' }
                          : { backgroundColor: 'var(--color-danger-subtle)', color: 'var(--color-danger)' }"
                      >
                        {{ item.status === 'success' ? '成功' : '失败' }}
                      </span>
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
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="card rounded-xl theme-transition">
        <div class="p-5" :style="{ borderBottom: '1px solid var(--border-subtle)' }">
          <div class="flex items-center gap-3">
            <div class="h-1 w-6 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-primary), var(--color-purple))' }"></div>
            <h2 class="text-lg font-semibold" style="color: var(--text-main);">快捷操作</h2>
          </div>
        </div>
        <div class="p-4 space-y-3">
          <router-link
            to="/tasks"
            class="flex items-center gap-3 p-3 rounded-lg transition-all duration-200"
            :style="{ backgroundColor: 'var(--color-primary-subtle)', border: '1px solid var(--border-subtle)' }"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'var(--color-primary-subtle)')"
          >
            <div
              class="w-8 h-8 rounded-lg flex items-center justify-center"
              :style="{ backgroundColor: 'var(--color-primary-subtle)' }"
            >
              <PlusIcon class="w-4 h-4" style="color: var(--color-primary);" />
            </div>
            <span class="font-medium" style="color: var(--text-main);">新建任务</span>
          </router-link>
          <router-link
            to="/tasks"
            class="flex items-center gap-3 p-3 rounded-lg transition-all duration-200"
            :style="{ border: '1px solid transparent' }"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)', $event.currentTarget.style.borderColor = 'var(--border-subtle)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent', $event.currentTarget.style.borderColor = 'transparent')"
          >
            <div
              class="w-8 h-8 rounded-lg flex items-center justify-center"
              :style="{ backgroundColor: 'var(--bg-tertiary)' }"
            >
              <PlayIcon class="w-4 h-4" style="color: var(--text-muted);" />
            </div>
            <span class="font-medium" style="color: var(--text-main);">查看所有任务</span>
          </router-link>
          <button
            @click="$emit('openScratchpad')"
            class="w-full flex items-center gap-3 p-3 rounded-lg transition-all duration-200"
            :style="{ border: '1px solid transparent' }"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)', $event.currentTarget.style.borderColor = 'var(--border-subtle)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent', $event.currentTarget.style.borderColor = 'transparent')"
          >
            <div
              class="w-8 h-8 rounded-lg flex items-center justify-center"
              :style="{ backgroundColor: 'var(--bg-tertiary)' }"
            >
              <CodeBracketIcon class="w-4 h-4" style="color: var(--text-muted);" />
            </div>
            <span class="font-medium" style="color: var(--text-main);">快速执行代码</span>
          </button>
          <router-link
            to="/settings"
            class="flex items-center gap-3 p-3 rounded-lg transition-all duration-200"
            :style="{ border: '1px solid transparent' }"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)', $event.currentTarget.style.borderColor = 'var(--border-subtle)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent', $event.currentTarget.style.borderColor = 'transparent')"
          >
            <div
              class="w-8 h-8 rounded-lg flex items-center justify-center"
              :style="{ backgroundColor: 'var(--bg-tertiary)' }"
            >
              <Cog6ToothIcon class="w-4 h-4" style="color: var(--text-muted);" />
            </div>
            <span class="font-medium" style="color: var(--text-main);">系统设置</span>
          </router-link>
        </div>

        <!-- Recent Tasks Mini List -->
        <div class="p-5" :style="{ borderTop: '1px solid var(--border-subtle)' }">
          <h3 class="text-sm font-medium mb-3" style="color: var(--text-muted);">最近任务</h3>
          <div v-if="recentTasks.length === 0" class="text-center py-4 text-sm" style="color: var(--text-disabled);">
            暂无任务
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="task in recentTasks"
              :key="task.id"
              class="flex items-center justify-between p-2 rounded-lg theme-transition"
              :style="{ backgroundColor: 'var(--bg-tertiary)' }"
            >
              <div class="flex items-center gap-2">
                <!-- Status dot -->
                <span class="relative flex h-2 w-2">
                  <span
                    v-if="task.status === 'running'"
                    class="animate-ping absolute inline-flex h-full w-full rounded-full"
                    :style="{ backgroundColor: 'var(--color-primary)', opacity: 0.75 }"
                  ></span>
                  <span
                    class="relative inline-flex rounded-full h-2 w-2"
                    :style="{
                      backgroundColor:
                        task.status === 'running' || task.status === 'success' ? 'var(--color-primary)' :
                        task.status === 'failed' ? 'var(--color-danger)' :
                        task.status === 'timeout' ? 'var(--color-warning)' :
                        'var(--text-muted)'
                    }"
                  ></span>
                </span>
                <span class="text-sm" style="color: var(--text-main);" :style="{ maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }">{{ task.name }}</span>
              </div>
              <span
                class="text-xs px-2 py-0.5 rounded-full"
                :style="{
                  backgroundColor: 'var(--bg-hover)',
                  color: 'var(--text-muted)'
                }"
              >
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import {
  ListBulletIcon, PlayIcon, ExclamationTriangleIcon, ChartPieIcon,
  PlusIcon, CpuChipIcon, CircleStackIcon, ServerIcon,
  CodeBracketIcon, Cog6ToothIcon, ClockIcon
} from '@heroicons/vue/24/outline'
import { taskApi, systemApi } from '../utils/api.js'
import { formatTime, statusText } from '../utils/formatters.js'

const emit = defineEmits(['openScratchpad'])

const tasks = ref([])
const timeline = ref([])
const systemStats = ref({ cpu_percent: 0, memory_percent: 0, disk_percent: 0, memory_used_gb: 0, memory_total_gb: 0, disk_used_gb: 0, disk_total_gb: 0 })
const recentTasks = computed(() => tasks.value.slice(0, 5))

const statsBorder = computed(() => ({
  backgroundColor: 'var(--bg-secondary)',
  border: '1px solid var(--border-subtle)'
}))

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

function initCharts() {
  const getChartColor = (theme) => {
    if (theme === 'darcula') return '#3592C4'
    if (theme === 'onedark') return '#61AFEF'
    if (theme === 'gruvbox') return '#D65D0E'
    if (theme === 'intellij') return '#3592C4'
    return '#6366F1'
  }

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

  cpuChartInstance = echarts.init(cpuChart.value)
  cpuChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: primaryColor, data: cpuHistory.value }]
  })

  memoryChartInstance = echarts.init(memoryChart.value)
  const successColor = theme === 'darcula' ? '#67965A' : theme === 'onedark' ? '#98C379' : theme === 'gruvbox' ? '#98971A' : '#488B49'
  memoryChartInstance.setOption({
    ...commonOptions,
    series: [{ ...commonOptions.series[0], color: successColor, data: memoryHistory.value }]
  })

  diskChartInstance = echarts.init(diskChart.value)
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
