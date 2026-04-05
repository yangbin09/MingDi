/**
 * Dashboard 统计数据 Composable
 * 管理任务列表、时间线、系统统计的获取与计算
 */
import { ref, computed, onUnmounted } from 'vue'
import { taskApi, systemApi } from '../utils/api.js'
import { usePolling } from './usePolling.js'
import type { SystemStats } from './useDashboardCharts'

// ============= 类型定义 =============
export interface Task {
  id: number
  name: string
  status: string
  [key: string]: any
}

export interface TimelineItem {
  id: number
  task_id: number
  task_name: string
  start_time: string
  end_time: string | null
  duration: number | null
  exit_code: number | null
  status: string
}

export interface DashboardStats {
  total: number
  running: number
  failedToday: number
  successRate: number
}

// ============= 状态定义 =============
const tasks = ref<Task[]>([])
const timeline = ref<TimelineItem[]>([])
const systemStats = ref<SystemStats>({
  cpu_percent: 0,
  memory_percent: 0,
  disk_percent: 0,
  memory_used_gb: 0,
  memory_total_gb: 0,
  disk_used_gb: 0,
  disk_total_gb: 0
})

// ============= 计算属性 =============
const recentTasks = computed(() => tasks.value.slice(0, 5))

const stats = computed<DashboardStats>(() => {
  const total = tasks.value.length
  const running = tasks.value.filter((t: Task) => t.status === 'running').length
  const failed = tasks.value.filter((t: Task) => t.status === 'failed').length
  const success = tasks.value.filter((t: Task) => t.status === 'success').length
  const successRate = total > 0 ? Math.round((success / total) * 100) : 100
  return { total, running, failedToday: failed, successRate }
})

// ============= API 方法 =============
async function fetchTasks(): Promise<void> {
  try {
    const res = await taskApi.list()
    tasks.value = res.data
  } catch (e) {
    console.error('[useDashboardStats] fetchTasks error:', e)
  }
}

async function fetchTimeline(): Promise<void> {
  try {
    const res = await taskApi.timeline()
    timeline.value = res.data
  } catch (e) {
    console.error('[useDashboardStats] fetchTimeline error:', e)
  }
}

async function fetchSystemStats(): Promise<void> {
  try {
    const res = await systemApi.stats()
    systemStats.value = res.data
  } catch (e) {
    console.error('[useDashboardStats] fetchSystemStats error:', e)
  }
}

// ============= 批量获取 =============
async function fetchAllData(): Promise<void> {
  await Promise.all([fetchTasks(), fetchTimeline(), fetchSystemStats()])
}

// ============= 轮询 =============
const { start: startPolling, stop: stopPolling } = usePolling(fetchAllData, 5000)

// ============= 导出 =============
export function useDashboardStats() {
  return {
    // 状态
    tasks,
    timeline,
    systemStats,

    // 计算属性
    recentTasks,
    stats,

    // API 方法
    fetchTasks,
    fetchTimeline,
    fetchSystemStats,
    fetchAllData,

    // 轮询控制
    startPolling,
    stopPolling
  }
}
