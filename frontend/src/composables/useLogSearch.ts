/**
 * 日志搜索与分页 Composable
 * 提取 Logs.vue 中的搜索、过滤、分页逻辑
 */
import { ref, computed, watch } from 'vue'
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
  statusFilter: string | number | null  // running | 0 | -99 | -1 | null
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

export interface PaginatedLogs {
  total: number
  items: LogEntry[]
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

// ============= 计算属性 =============
const totalPages = computed(() => Math.ceil(totalLogs.value / pageSize.value))

// ============= API 方法 =============
async function fetchTasks(): Promise<void> {
  try {
    const res = await taskApi.list()
    tasks.value = res.data
  } catch (e) {
    console.error('[useLogSearch] fetchTasks error:', e)
  }
}

async function fetchLogs(): Promise<void> {
  loading.value = true
  try {
    const params: LogSearchParams = {
      page: currentPage.value,
      size: pageSize.value
    }

    if (filters.value.taskId) {
      params.task_id = filters.value.taskId
    }

    // 状态过滤映射
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
  } catch (e) {
    console.error('[useLogSearch] fetchLogs error:', e)
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

// ============= 过滤与分页操作 =============
function applyFilters(): void {
  currentPage.value = 1
  fetchLogs()
}

function resetFilters(): void {
  filters.value = {
    taskId: null,
    statusFilter: null,
    keyword: ''
  }
  dateRange.value = null
  currentPage.value = 1
  fetchLogs()
}

function handlePageChange(page: number): void {
  currentPage.value = page
  fetchLogs()
}

function handleSizeChange(size: number): void {
  pageSize.value = size
  currentPage.value = 1
  fetchLogs()
}

// ============= 行展开管理 =============
function handleExpandChange(row: LogEntry, expanded: boolean): void {
  if (expanded) {
    expandedRows.value = [row.id]
  } else {
    expandedRows.value = []
  }
}

function toggleExpand(row: LogEntry): void {
  const idx = expandedRows.value.indexOf(row.id)
  if (idx >= 0) {
    expandedRows.value.splice(idx, 1)
  } else {
    expandedRows.value = [row.id]
  }
}

function clearSelection(): void {
  expandedRows.value = []
}

// ============= 批量操作 =============
function handleSelectionChange(selectedIds: number[]): void {
  selectedLogIds.value = selectedIds
}

async function batchDeleteLogs(): Promise<boolean> {
  if (selectedLogIds.value.length === 0) return false

  try {
    await logApi.batchDelete(selectedLogIds.value)
    ElMessage.success(`成功删除 ${selectedLogIds.value.length} 条日志`)
    selectedLogIds.value = []
    fetchLogs()
    return true
  } catch (e) {
    ElMessage.error('批量删除失败')
    return false
  }
}

async function deleteSingleLog(logId: number): Promise<boolean> {
  try {
    await logApi.delete(logId)
    ElMessage.success('日志删除成功')
    fetchLogs()
    return true
  } catch (e) {
    ElMessage.error('删除失败')
    return false
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
    fetchTasks,
    fetchLogs,
    applyFilters,
    resetFilters,
    handlePageChange,
    handleSizeChange,
    handleExpandChange,
    toggleExpand,
    clearSelection,
    handleSelectionChange,
    batchDeleteLogs,
    deleteSingleLog
  }
}
