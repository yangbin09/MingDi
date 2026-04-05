/**
 * 日志搜索与分页 Composable
 * 提取 Logs.vue 中的搜索、过滤、分页逻辑
 */
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { logApi, taskApi } from '../utils/api.js'

// ============= 类型定义 =============
export interface LogEntry {
  id: number
  task_id: number
  start_time: string
  end_time: string | null
  output: string | null
  exit_code: number | null
}

export interface Task {
  id: number
  name: string
  status?: string
}

export interface LogFilters {
  taskId: number | null
  statusFilter: string | number | null
  keyword: string
}

export interface LogSearchParams {
  page: number
  size: number
  task_id?: number
  is_running?: boolean
  exit_code_non_zero?: boolean
  exit_code?: number | null
  keyword?: string
  start_date?: string
  end_date?: string
}

// ============= 状态定义 =============
const loading = ref(false)
const logs = ref<LogEntry[]>([])
const tasks = ref<Task[]>([])
const selectedLogIds = ref<number[]>([])

const filters = ref<LogFilters>({
  taskId: null,
  statusFilter: null,
  keyword: ''
})

const currentPage = ref(1)
const pageSize = ref(20)
const totalLogs = ref(0)

const expandedRows = ref<number[]>([])
const dateRange = ref<[Date, Date] | null>(null)

// ============= Abort 控制 =============
let currentController: AbortController | null = null

// ============= 计算属性 =============
const totalPages = computed(() => Math.ceil(totalLogs.value / pageSize.value))

// ============= API 方法 =============
async function fetchTasksAction(): Promise<void> {
  try {
    const res = await taskApi.list()
    tasks.value = res.data
  } catch (e) {
    console.error('[useLogSearch] fetchTasks error:', e)
  }
}

async function fetchLogsAction(): Promise<void> {
  // 取消之前的请求
  if (currentController) {
    currentController.abort()
  }
  currentController = new AbortController()

  loading.value = true
  try {
    const params: LogSearchParams = {
      page: currentPage.value,
      size: pageSize.value
    }

    if (filters.value.taskId) {
      params.task_id = filters.value.taskId
    }

    const status = filters.value.statusFilter
    if (status === 'running') {
      params.is_running = true
    } else if (status === -99) {
      params.exit_code_non_zero = true
    } else if (status !== null) {
      params.exit_code = status as number
    }

    if (filters.value.keyword) {
      params.keyword = filters.value.keyword
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().slice(0, 10)
      params.end_date = dateRange.value[1].toISOString().slice(0, 10)
    }

    const res = await logApi.search(params)
    totalLogs.value = res.data.total
    logs.value = res.data.items
    selectedLogIds.value = []
  } catch (e: any) {
    // 忽略被取消的请求
    if (e.name === 'AbortError' || e.name === 'CanceledError') {
      return
    }
    console.error('[useLogSearch] fetchLogs error:', e)
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

// ============= 过滤与分页操作 =============
function applyFiltersAction(): void {
  currentPage.value = 1
  fetchLogsAction()
}

function resetFiltersAction(): void {
  filters.value = {
    taskId: null,
    statusFilter: null,
    keyword: ''
  }
  dateRange.value = null
  currentPage.value = 1
  fetchLogsAction()
}

function handlePageChangeAction(page: number): void {
  currentPage.value = page
  fetchLogsAction()
}

function handleSizeChangeAction(size: number): void {
  pageSize.value = size
  currentPage.value = 1
  fetchLogsAction()
}

// ============= 行展开管理 =============
function handleExpandChangeAction(row: LogEntry, expanded: boolean): void {
  if (expanded) {
    expandedRows.value = [row.id]
  } else {
    expandedRows.value = []
  }
}

function toggleExpandAction(row: LogEntry): void {
  const idx = expandedRows.value.indexOf(row.id)
  if (idx >= 0) {
    expandedRows.value.splice(idx, 1)
  } else {
    expandedRows.value = [row.id]
  }
}

function clearSelectionAction(): void {
  expandedRows.value = []
}

// ============= 批量操作 =============
function handleSelectionChangeAction(selectedIds: number[]): void {
  selectedLogIds.value = selectedIds
}

async function batchDeleteLogsAction(): Promise<boolean> {
  if (selectedLogIds.value.length === 0) return false

  try {
    await logApi.batchDelete(selectedLogIds.value)
    ElMessage.success(`成功删除 ${selectedLogIds.value.length} 条日志`)
    selectedLogIds.value = []
    fetchLogsAction()
    return true
  } catch (e) {
    ElMessage.error('批量删除失败')
    return false
  }
}

async function deleteSingleLogAction(logId: number): Promise<boolean> {
  try {
    await logApi.delete(logId)
    ElMessage.success('日志删除成功')
    fetchLogsAction()
    return true
  } catch (e) {
    ElMessage.error('删除失败')
    return false
  }
}

// ============= 清理 =============
function cancelPendingRequests(): void {
  if (currentController) {
    currentController.abort()
    currentController = null
  }
}

// ============= 导出函数 =============
export function useLogSearch() {
  return {
    // 状态
    loading,
    logs,
    tasks,
    selectedLogIds,
    filters,
    currentPage,
    pageSize,
    totalLogs,
    totalPages,
    expandedRows,
    dateRange,

    // 方法
    fetchTasks: fetchTasksAction,
    fetchLogs: fetchLogsAction,
    applyFilters: applyFiltersAction,
    resetFilters: resetFiltersAction,
    handlePageChange: handlePageChangeAction,
    handleSizeChange: handleSizeChangeAction,
    handleExpandChange: handleExpandChangeAction,
    toggleExpand: toggleExpandAction,
    clearSelection: clearSelectionAction,
    handleSelectionChange: handleSelectionChangeAction,
    batchDeleteLogs: batchDeleteLogsAction,
    deleteSingleLog: deleteSingleLogAction,
    cancelPendingRequests
  }
}
