/**
 * 日志实时刷新 Composable
 * 管理自动刷新定时器（不再使用 setInterval 触发响应式更新）
 * 实时时长显示改用 Vue 的 nextTick + 标记位方式
 */
import { ref, watch, nextTick } from 'vue'

// ============= 创建 Composable 实例 =============
function createLogStream() {
  // 状态定义 - 每个实例独立
  const autoRefreshInterval = ref<number | null>(null)
  let autoRefreshTimer: ReturnType<typeof setInterval> | null = null
  let isActive = false  // 组件激活标志

  // 实时刷新标记（用于触发表格重新渲染）
  const refreshTick = ref(0)

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

  // ============= 实时时长刷新（改用标记位方式）=============
  function tickLiveDuration(): void {
    if (!isActive) return
    refreshTick.value++
  }

  function startLiveDurationRefresh(): void {
    isActive = true
    // 使用 setInterval 递增标记位，而不是直接触发响应式更新
    const timer = setInterval(() => {
      if (isActive) {
        tickLiveDuration()
      }
    }, 1000)
    // 返回 timer 以便外部清理（不在这里清理）
    return timer as unknown as number
  }

  function stopLiveDurationRefresh(): void {
    isActive = false
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
    refreshTick,

    // 自动刷新
    startAutoRefresh,
    stopAutoRefresh,
    setAutoRefreshInterval,

    // 实时时长
    startLiveDurationRefresh,
    tickLiveDuration,
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
