/**
 * Dashboard ECharts 图表 Composable
 * 统一管理 CPU/内存/磁盘 迷你图表的初始化、更新、主题切换、销毁
 */
import { ref, shallowRef, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import type { SystemStats } from './useDashboardStats'

// ============= 类型定义 =============
export interface ChartTheme {
  primary: string
  success: string
  danger: string
}

// ============= 状态定义 =============
// 图表实例（使用 shallowRef 避免深度响应式）
let cpuChartInstance: echarts.ECharts | null = null
let memoryChartInstance: echarts.ECharts | null = null
let diskChartInstance: echarts.ECharts | null = null

const cpuHistory = ref<number[]>(Array(20).fill(0))
const memoryHistory = ref<number[]>(Array(20).fill(0))
const diskHistory = ref<number[]>(Array(20).fill(0))

// ============= 主题配置 =============
const THEMES: Record<string, ChartTheme> = {
  darcula: { primary: '#3592C4', success: '#67965A', danger: '#E43F3F' },
  anying: { primary: '#61AFEF', success: '#98C379', danger: '#E06C75' },
  gruvbox: { primary: '#D65D0E', success: '#98971A', danger: '#CC241D' },
  intellij: { primary: '#3592C4', success: '#488B49', danger: '#D04438' }
}

function getThemeColors(): ChartTheme {
  const theme = document.documentElement.getAttribute('data-theme') || 'darcula'
  return THEMES[theme] || THEMES.darcula
}

// ============= 通用图表配置 =============
const COMMON_OPTIONS = {
  grid: { left: 0, right: 0, top: 2, bottom: 0 },
  xAxis: { type: 'category' as const, show: false, data: Array(20).fill('') },
  yAxis: { type: 'value' as const, min: 0, max: 100, show: false },
  series: [{
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 2 },
    areaStyle: { opacity: 0.2 }
  }],
  animation: true,
  animationDuration: 300
}

// ============= 图表初始化 =============
function initCharts(
  cpuEl: HTMLElement | null,
  memoryEl: HTMLElement | null,
  diskEl: HTMLElement | null
): void {
  const colors = getThemeColors()

  if (cpuEl) {
    cpuChartInstance = echarts.init(cpuEl)
    cpuChartInstance.setOption({
      ...COMMON_OPTIONS,
      series: [{ ...COMMON_OPTIONS.series[0], color: colors.primary, data: cpuHistory.value }]
    })
  }

  if (memoryEl) {
    memoryChartInstance = echarts.init(memoryEl)
    memoryChartInstance.setOption({
      ...COMMON_OPTIONS,
      series: [{ ...COMMON_OPTIONS.series[0], color: colors.success, data: memoryHistory.value }]
    })
  }

  if (diskEl) {
    diskChartInstance = echarts.init(diskEl)
    diskChartInstance.setOption({
      ...COMMON_OPTIONS,
      series: [{ ...COMMON_OPTIONS.series[0], color: colors.danger, data: diskHistory.value }]
    })
  }
}

// ============= 图表更新 =============
function updateCharts(stats: SystemStats): void {
  if (cpuChartInstance) {
    cpuHistory.value.push(stats.cpu_percent)
    cpuHistory.value.shift()
    cpuChartInstance.setOption({ series: [{ data: cpuHistory.value }] })
  }

  if (memoryChartInstance) {
    memoryHistory.value.push(stats.memory_percent)
    memoryHistory.value.shift()
    memoryChartInstance.setOption({ series: [{ data: memoryHistory.value }] })
  }

  if (diskChartInstance) {
    diskHistory.value.push(stats.disk_percent)
    diskHistory.value.shift()
    diskChartInstance.setOption({ series: [{ data: diskHistory.value }] })
  }
}

// ============= 响应式处理 =============
function handleResize(): void {
  cpuChartInstance?.resize()
  memoryChartInstance?.resize()
  diskChartInstance?.resize()
}

function setupResizeListener(): () => void {
  const handler = () => handleResize()
  window.addEventListener('resize', handler)
  return () => window.removeEventListener('resize', handler)
}

// ============= 销毁 =============
function disposeCharts(): void {
  cpuChartInstance?.dispose()
  memoryChartInstance?.dispose()
  diskChartInstance?.dispose()
  cpuChartInstance = null
  memoryChartInstance = null
  diskChartInstance = null
}

// ============= 导出 =============
export function useDashboardCharts() {
  return {
    // 数据
    cpuHistory,
    memoryHistory,
    diskHistory,

    // 方法
    initCharts,
    updateCharts,
    handleResize,
    setupResizeListener,
    disposeCharts
  }
}
