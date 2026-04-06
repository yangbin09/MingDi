/**
 * 日志实时刷新 Composable
 * 管理自动刷新定时器和实时时长更新
 * 包含完整的生命周期清理逻辑，防止组件卸载后异步操作导致的问题
 */
import { ref, watch, type WatchStopHandle } from 'vue'

// ============= 创建 Composable 实例 =============
function createLogStream() {
  // 状态定义 - 每个实例独立
  const autoRefreshInterval = ref<number | null>(null)
  let autoRefreshTimer: ReturnType<typeof setInterval> | null = null
  let liveDurationTimer: ReturnType<typeof setInterval> | null = null
  let isActive = false  // 组件激活标志
  let isUnmounted = false  // 卸载标志，防止卸载后异步回调

  // 实时刷新标记（用于触发表格重新渲染）
  const refreshTick = ref(0)

  // ============= 防御性检查 =============
  function safeTick(): void {
    // 组件已卸载时，跳过所有响应式更新
    if (isUnmounted || !isActive) return
    refreshTick.value++
  }

  // ============= 自动刷新逻辑 =============
  function startAutoRefresh(fetchFn: () => void | Promise<void>): void {
    stopAutoRefresh()
    if (autoRefreshInterval.value) {
      autoRefreshTimer = setInterval(() => {
        // 组件卸载或非活跃状态时，跳过 fetch
        if (!isUnmounted && isActive) {
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
  function startLiveDurationRefresh(): void {
    isActive = true
    // 使用 setInterval 递增标记位
    liveDurationTimer = setInterval(() => {
      safeTick()
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
  ): WatchStopHandle {
    return watch(
      () => intervalRef.value,
      (newVal, oldVal) => {
        if (oldVal) stopAutoRefresh()
        if (newVal) startAutoRefresh(fetchFn)
      }
    )
  }

  // ============= 完整清理 =============
  function cleanupAll(): void {
    isUnmounted = true
    isActive = false
    stopAutoRefresh()
    stopLiveDurationRefresh()
  }

  // ============= 导出工厂函数 =============
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
