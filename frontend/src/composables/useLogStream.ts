/**
 * 日志实时刷新 Composable
 * 统一管理 autoRefreshTimer 和 liveDurationTimer
 */
import { ref, watch, onUnmounted } from 'vue'

// ============= 状态定义 =============
const autoRefreshInterval = ref<number | null>(null)
let autoRefreshTimer: ReturnType<typeof setInterval> | null = null
let liveDurationTimer: ReturnType<typeof setInterval> | null = null

// ============= 自动刷新逻辑 =============
function startAutoRefresh(fetchFn: () => void | Promise<void>): void {
  stopAutoRefresh()
  if (autoRefreshInterval.value) {
    autoRefreshTimer = setInterval(() => {
      fetchFn()
    }, autoRefreshInterval.value)
  }
}

function stopAutoRefresh(): void {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
}

function setAutoRefreshInterval(interval: number | null): void {
  autoRefreshInterval.value = interval
}

// ============= 实时时长刷新 =============
function startLiveDurationRefresh(logsRef: { value: any[] }): void {
  stopLiveDurationRefresh()
  liveDurationTimer = setInterval(() => {
    // 触发响应式更新 - 通过替换数组引用实现
    logsRef.value = [...logsRef.value]
  }, 1000)
}

function stopLiveDurationRefresh(): void {
  if (liveDurationTimer) {
    clearInterval(liveDurationTimer)
    liveDurationTimer = null
  }
}

// ============= 组合式监听 =============
function setupAutoRefreshWatch(
  intervalRef: typeof autoRefreshInterval,
  fetchFn: () => void | Promise<void>
): void {
  watch(
    () => intervalRef.value,
    (newVal, oldVal) => {
      if (oldVal) stopAutoRefresh()
      if (newVal) startAutoRefresh(fetchFn)
    }
  )
}

// ============= 清理 =============
function cleanupAll(): void {
  stopAutoRefresh()
  stopLiveDurationRefresh()
}

onUnmounted(() => {
  cleanupAll()
})

// ============= 导出 =============
export function useLogStream() {
  return {
    // 状态
    autoRefreshInterval,

    // 自动刷新
    startAutoRefresh,
    stopAutoRefresh,
    setAutoRefreshInterval,

    // 实时时长
    startLiveDurationRefresh,
    stopLiveDurationRefresh,

    // 监听
    setupAutoRefreshWatch,

    // 清理
    cleanupAll
  }
}
