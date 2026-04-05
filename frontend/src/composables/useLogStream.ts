/**
 * 日志实时刷新 Composable
 * 统一管理 autoRefreshTimer 和 liveDurationTimer
 * 使用显式清理模式，避免 onUnmounted 时机问题
 */
import { ref, watch } from 'vue'

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
  // 记录初始长度，避免每次都创建新数组
  let lastLength = logsRef.value.length
  liveDurationTimer = setInterval(() => {
    // 只有在数据实际变化时才触发更新
    if (logsRef.value.length !== lastLength) {
      lastLength = logsRef.value.length
      // 强制触发响应式更新（Vue 3）
      logsRef.value = [...logsRef.value]
    }
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
