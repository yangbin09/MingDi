/**
 * 日志实时刷新 Composable
 * 统一管理 autoRefreshTimer 和 liveDurationTimer
 * 每次调用创建独立状态实例
 */
import { ref, watch } from 'vue'

// ============= 创建 Composable 实例 =============
function createLogStream() {
  // 状态定义 - 每个实例独立
  const autoRefreshInterval = ref<number | null>(null)
  let autoRefreshTimer: ReturnType<typeof setInterval> | null = null
  let liveDurationTimer: ReturnType<typeof setInterval> | null = null
  let isActive = false  // 组件激活标志

  // ============= 自动刷新逻辑 =============
  function startAutoRefresh(fetchFn: () => void | Promise<void>): void {
    stopAutoRefresh()
    if (autoRefreshInterval.value) {
      autoRefreshTimer = setInterval(() => {
        if (isActive) {
          fetchFn()
        }
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
    isActive = true
    liveDurationTimer = setInterval(() => {
      if (!isActive) return
      // 强制触发响应式更新
      try {
        logsRef.value = [...logsRef.value]
      } catch (e) {
        // 忽略DOM相关错误
      }
    }, 1000)
  }

  function stopLiveDurationRefresh(): void {
    isActive = false
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
    isActive = false
    stopAutoRefresh()
    stopLiveDurationRefresh()
  }

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

// ============= 导出工厂函数 =============
export function useLogStream() {
  return createLogStream()
}
