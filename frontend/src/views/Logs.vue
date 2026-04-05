<template>
  <div class="logs-page space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold" style="color: var(--text-main);">
          <el-icon class="mr-2"><Document /></el-icon>
          日志中心
        </h1>
        <p class="text-sm mt-1" style="color: var(--text-muted);">集中查看和管理所有任务执行日志</p>
      </div>
      <div class="flex items-center gap-3">
        <el-select v-model="autoRefreshInterval" placeholder="自动刷新" clearable style="width: 120px;">
          <el-option label="5秒刷新" :value="5000" />
          <el-option label="10秒刷新" :value="10000" />
          <el-option label="30秒刷新" :value="30000" />
        </el-select>
        <el-button :icon="Refresh" circle @click="refreshLogs" :loading="loading" />
      </div>
    </div>

    <!-- Filters -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="8" :md="6">
          <el-select v-model="filters.taskId" placeholder="选择任务" clearable>
            <el-option label="全部任务" :value="null" />
            <el-option v-for="task in tasks" :key="task.id" :label="task.name" :value="task.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-select v-model="filters.statusFilter" placeholder="状态" clearable>
            <el-option label="全部" :value="null" />
            <el-option label="运行中" value="running" />
            <el-option label="成功 (exit 0)" :value="0" />
            <el-option label="失败 (exit ≠0)" :value="-99" />
            <el-option label="超时 (exit -1)" :value="-1" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="16" :md="12">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索日志内容..."
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
      </el-row>
      <el-row :gutter="16" class="mt-4">
        <el-col :xs="24" :sm="12" :md="10">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :md="14" class="flex justify-end gap-2">
          <el-button type="primary" @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-col>
      </el-row>

      <!-- Bulk Actions Bar -->
      <el-row v-if="selectedLogs.length > 0" :gutter="16" class="mt-4">
        <el-col :span="24">
          <el-alert type="info" :closable="false" class="bulk-actions-bar">
            <template #title>
              <span>已选择 <strong>{{ selectedLogs.length }}</strong> 项&nbsp;&nbsp;</span>
              <el-button type="danger" plain size="small" @click="handleBatchDelete">
                <el-icon><Delete /></el-icon>
                批量删除
              </el-button>
              <el-button size="small" @click="clearSelection">清空选择</el-button>
            </template>
          </el-alert>
        </el-col>
      </el-row>
    </el-card>

    <!-- Logs Table -->
    <el-card shadow="never" class="logs-card">
      <el-empty v-if="logs.length === 0 && !loading" description="暂无日志记录" />

      <el-table
        v-if="logs.length > 0"
        :data="logs"
        stripe
        @selection-change="handleSelectionChange"
        :header-cell-style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }"
        row-key="id"
        :expand-row-keys="expandedRows"
        @expand-change="handleExpandChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column type="expand" width="50">
          <template #default="{ row }">
            <div class="log-expand-preview">
              <div class="expand-header">
                <span class="text-sm" style="color: var(--text-muted);">日志预览 (最后10行)</span>
                <el-button size="small" type="primary" plain @click="viewLogDetail(row)">
                  <el-icon><FullScreen /></el-icon>
                  进入全屏查看
                </el-button>
              </div>
              <pre class="expand-content">{{ getLastLines(row.output, 10) }}</pre>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="任务" min-width="200">
          <template #default="{ row }">
            <div class="font-medium" @click="toggleExpand(row)" style="cursor: pointer;">
              {{ getTaskName(row.task_id) }}
            </div>
            <div class="text-xs" style="color: var(--text-muted);">Log #{{ row.id }}</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag
              :type="getStatusTagType(row)"
              size="small"
              :disable-transitions="false"
            >
              <el-icon v-if="getStatus(row) === 'running'" class="is-loading"><Loading /></el-icon>
              {{ getStatusLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="180">
          <template #default="{ row }">
            <span class="font-mono text-sm">{{ formatTimePrecise(row.start_time) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="时长" width="120">
          <template #default="{ row }">
            <span class="font-mono" :style="{ color: getStatus(row) === 'running' ? 'var(--color-primary)' : 'var(--text-main)' }">
              {{ getLiveDuration(row) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="right">
          <template #default="{ row }">
            <el-button-group>
              <el-tooltip content="查看详情" placement="top">
                <el-button size="small" type="primary" plain @click="viewLogDetail(row)">
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip v-if="getStatus(row) === 'failed'" content="AI 诊断" placement="top">
                <el-button size="small" type="warning" plain @click="diagnoseLog(row)" :loading="diagnosingLogId === row.id">
                  <el-icon><MagicStick /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="下载" placement="top">
                <el-button size="small" type="success" plain @click="downloadSingleLog(row)">
                  <el-icon><Download /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <el-button size="small" type="danger" plain @click="handleSingleDelete(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div v-if="totalLogs > 0" class="flex justify-between items-center mt-4">
        <span class="text-sm" style="color: var(--text-muted);">
          第 {{ currentPage }} / {{ totalPages }} 页，共 {{ totalLogs }} 条
        </span>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalLogs"
          layout="prev, pager, next, sizes"
          :page-sizes="[10, 20, 50, 100]"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- Log Detail Drawer -->
    <el-drawer
      v-model="showLogDrawer"
      :title="'日志详情 - ' + (currentLog ? getTaskName(currentLog.task_id) : '')"
      size="700px"
    >
      <div class="log-toolbar">
        <el-button
          v-if="currentLog && currentLog.output && currentLog.output.length > 500"
          type="primary"
          @click="summarizeCurrentLog"
          :loading="aiSummarizing"
        >
          <el-icon><MagicStick /></el-icon>
          AI 摘要
        </el-button>
        <el-button @click="downloadCurrentLog">
          <el-icon><Download /></el-icon>
          下载
        </el-button>
      </div>

      <el-alert
        v-if="aiSummary"
        title="AI 日志摘要"
        type="success"
        :closable="true"
        @close="aiSummary = null"
        class="mb-3"
      >
        <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ aiSummary }}</pre>
      </el-alert>

      <el-alert
        v-if="aiDiagnosis"
        title="AI 错误诊断"
        type="error"
        :closable="true"
        @close="aiDiagnosis = null"
        class="mb-3"
      >
        <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ aiDiagnosis }}</pre>
      </el-alert>

      <div v-if="currentLog" class="log-metadata">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentLog)">
              <el-icon v-if="getStatus(currentLog) === 'running'" class="is-loading"><Loading /></el-icon>
              {{ getStatusLabel(currentLog) }} (exit {{ currentLog.exit_code ?? 'running' }})
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatTimePrecise(currentLog.start_time) }}</el-descriptions-item>
          <el-descriptions-item v-if="currentLog.end_time" label="结束时间">{{ formatTimePrecise(currentLog.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="时长">
            <span class="font-mono">{{ currentLog.end_time ? formatDuration(currentLog) : getLiveDuration(currentLog) }}</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="terminal-output">
        <pre>{{ currentLog?.output || '// 无输出' }}</pre>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Refresh, Search, View, Download, MagicStick, Delete, RefreshLeft, FullScreen, DArrowRight, Loading
} from '@element-plus/icons-vue'
import { taskApi, logApi, aiApi } from '../utils/api.js'
import { useDebounce } from '../composables/useDebounce.js'

const { debounced: debouncedSearch } = useDebounce(() => applyFilters(), 300)

const loading = ref(false)
const logs = ref([])
const tasks = ref([])
const selectedLogs = ref([])
const showLogDrawer = ref(false)
const currentLog = ref(null)
const aiSummary = ref(null)
const aiDiagnosis = ref(null)
const aiSummarizing = ref(false)
const diagnosingLogId = ref(null)
const dateRange = ref(null)
const expandedRows = ref([])
const autoRefreshInterval = ref(null)
let autoRefreshTimer = null
let liveDurationTimer = null

const filters = ref({
  taskId: null,
  statusFilter: null,  // running | 0 | -99 | -1 | null
  keyword: ''
})

const currentPage = ref(1)
const pageSize = ref(20)
const totalLogs = ref(0)

const totalPages = computed(() => Math.ceil(totalLogs.value / pageSize.value))

// 自动刷新逻辑
function startAutoRefresh() {
  stopAutoRefresh()
  if (autoRefreshInterval.value) {
    autoRefreshTimer = setInterval(() => {
      fetchLogs()
    }, autoRefreshInterval.value)
  }
}

function stopAutoRefresh() {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
}

// 实时时长刷新：每秒更新运行中任务的时长显示
function startLiveDurationRefresh() {
  stopLiveDurationRefresh()
  liveDurationTimer = setInterval(() => {
    // 触发响应式更新 - 通过强制更新组件Key实现
    logs.value = [...logs.value]
  }, 1000)
}

function stopLiveDurationRefresh() {
  if (liveDurationTimer) {
    clearInterval(liveDurationTimer)
    liveDurationTimer = null
  }
}

watch(autoRefreshInterval, (newVal, oldVal) => {
  if (oldVal) stopAutoRefresh()
  if (newVal) startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  stopLiveDurationRefresh()
})

async function fetchTasks() {
  try {
    const res = await taskApi.list()
    tasks.value = res.data
  } catch (e) {
    console.error(e)
  }
}

async function fetchLogs() {
  loading.value = true
  try {
    const params = { page: currentPage.value, size: pageSize.value }
    if (filters.value.taskId) params.task_id = filters.value.taskId

    // 状态过滤映射
    const status = filters.value.statusFilter
    if (status === 'running') {
      params.is_running = true
    } else if (status === -99) {
      // -99 表示失败（非0退出码）
      params.exit_code_non_zero = true
    } else if (status !== null) {
      params.exit_code = status
    }

    if (filters.value.keyword) params.keyword = filters.value.keyword
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().slice(0, 10)
      params.end_date = dateRange.value[1].toISOString().slice(0, 10)
    }

    const res = await logApi.search(params)
    totalLogs.value = res.data.total
    logs.value = res.data.items
    selectedLogs.value = []
  } catch (e) {
    console.error('[Logs] Fetch error:', e)
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

function refreshLogs() {
  fetchLogs()
}

function handleSearch() {
  currentPage.value = 1
  fetchLogs()
}

function handleReset() {
  filters.value = {
    taskId: null,
    statusFilter: null,
    keyword: ''
  }
  dateRange.value = null
  currentPage.value = 1
  fetchLogs()
}

function handleFilterChange() {
  currentPage.value = 1
  fetchLogs()
}

function handlePageChange(page) {
  currentPage.value = page
  fetchLogs()
}

function handleSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
  fetchLogs()
}

function handleDebouncedSearch() {
  debouncedSearch()
}

function applyFilters() {
  currentPage.value = 1
  fetchLogs()
}

function handleExpandChange(row, expanded) {
  if (expanded) {
    expandedRows.value = [row.id]
  } else {
    expandedRows.value = []
  }
}

function clearSelection() {
  expandedRows.value = []
}

function toggleExpand(row) {
  const idx = expandedRows.value.indexOf(row.id)
  if (idx >= 0) {
    expandedRows.value.splice(idx, 1)
  } else {
    expandedRows.value = [row.id]
  }
}

function getTaskName(taskId) {
  const task = tasks.value.find(t => t.id === taskId)
  return task ? task.name : `任务 #${taskId}`
}

// 精确时间格式 YYYY-MM-DD HH:mm:ss
function formatTimePrecise(timeStr) {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const pad = n => n.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

// ========== 状态机逻辑 ==========
// 状态判断：pending(等待)、running(运行中)、success(成功)、failed(失败)、timeout(超时)、cancelled(已取消)
function getStatus(log) {
  // 运行中：还没有结束时间（exit_code 始终为 null 直到结束）
  if (!log.end_time) return 'running'
  // 已结束：exit_code === -1 表示超时
  if (log.exit_code === -1) return 'timeout'
  // 已结束：exit_code === 0 表示成功
  if (log.exit_code === 0) return 'success'
  // 已结束且非0退出码：表示失败
  if (log.exit_code !== null) return 'failed'
  // 已结束但无 exit_code：已取消
  return 'cancelled'
}

function getStatusLabel(log) {
  const status = getStatus(log)
  const labels = {
    running: '运行中',
    success: '成功',
    failed: '失败',
    timeout: '超时',
    cancelled: '已取消',
    pending: '等待中'
  }
  return labels[status] || '未知'
}

function getStatusTagType(log) {
  const status = getStatus(log)
  const types = {
    running: 'primary',   // 蓝色
    success: 'success',  // 绿色
    failed: 'danger',    // 红色
    timeout: 'warning',  // 橙色
    cancelled: 'info',   // 灰色
    pending: 'info'      // 灰色
  }
  return types[status] || 'info'
}

// 实时时长计算：运行中任务动态跳动
function getLiveDuration(log) {
  // 已结束：直接格式化
  if (log.end_time) return formatDuration(log)
  // 运行中：实时计算
  if (log.start_time && !log.end_time) {
    const start = new Date(log.start_time).getTime()
    const now = Date.now()
    const seconds = Math.floor((now - start) / 1000)
    if (seconds < 60) return `${seconds}秒`
    if (seconds < 3600) {
      const min = Math.floor(seconds / 60)
      const sec = seconds % 60
      return `${min}分${sec}秒`
    }
    const hour = Math.floor(seconds / 3600)
    const min = Math.floor((seconds % 3600) / 60)
    return `${hour}小时${min}分`
  }
  return '-'
}

// 时长格式化，自动转换分钟/秒
function formatDuration(log) {
  if (!log.start_time || !log.end_time) return '-'
  const duration = (new Date(log.end_time) - new Date(log.start_time)) / 1000
  if (duration < 60) {
    return `${duration.toFixed(1)}秒`
  } else if (duration < 3600) {
    const min = Math.floor(duration / 60)
    const sec = (duration % 60).toFixed(0)
    return `${min}分${sec}秒`
  } else {
    const hour = Math.floor(duration / 3600)
    const min = Math.floor((duration % 3600) / 60)
    return `${hour}小时${min}分`
  }
}

function getDuration(log) {
  return formatDuration(log)
}

// 获取日志最后N行
function getLastLines(output, lines = 10) {
  if (!output) return '// 无输出'
  const allLines = output.split('\n')
  const lastLines = allLines.slice(-lines)
  return lastLines.join('\n') || '// 无输出'
}

function handleSelectionChange(selection) {
  selectedLogs.value = selection.map(l => l.id)
}

async function handleBatchDelete() {
  if (selectedLogs.value.length === 0) return

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedLogs.value.length} 条日志吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await logApi.batchDelete(selectedLogs.value)

    ElMessage.success(`成功删除 ${selectedLogs.value.length} 条日志`)
    selectedLogs.value = []
    fetchLogs()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

async function handleSingleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除日志 #${row.id} 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await logApi.delete(row.id)

    ElMessage.success('日志删除成功')
    fetchLogs()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function viewLogDetail(log) {
  currentLog.value = log
  aiSummary.value = null
  aiDiagnosis.value = null
  showLogDrawer.value = true
}

async function summarizeCurrentLog() {
  if (!currentLog.value?.output || aiSummarizing.value) return
  aiSummarizing.value = true
  try {
    const res = await aiApi.summarizeLog(currentLog.value.output)
    aiSummary.value = res.data.summary
  } catch (e) {
    ElMessage.error('AI 摘要失败')
  } finally {
    aiSummarizing.value = false
  }
}

async function summarizeSelectedLogs() {
  if (selectedLogs.value.length === 0 || aiSummarizing.value) return
  const selectedLogData = logs.value.filter(l => selectedLogs.value.includes(l.id))
  const combinedOutput = selectedLogData.map(l => `=== ${getTaskName(l.task_id)} (Log #${l.id}) ===\n${l.output || '// 无输出'}`).join('\n\n')
  aiSummarizing.value = true
  try {
    const res = await aiApi.summarizeLog(combinedOutput)
    aiSummary.value = res.data.summary
  } catch (e) {
    ElMessage.error('AI 摘要失败')
  } finally {
    aiSummarizing.value = false
  }
}

async function diagnoseLog(log) {
  if (diagnosingLogId.value) return
  diagnosingLogId.value = log.id
  aiDiagnosis.value = null
  try {
    const res = await aiApi.diagnoseError(log.output || '', '')
    aiDiagnosis.value = res.data.diagnosis
  } catch (e) {
    ElMessage.error('AI 诊断失败')
  } finally {
    diagnosingLogId.value = null
  }
}

function downloadSingleLog(log) {
  const content = `=== PyCron-Master Log #${log.id} ===
Task: ${getTaskName(log.task_id)}
Status: ${getStatusLabel(log)}
Start Time: ${formatTimePrecise(log.start_time)}
End Time: ${log.end_time ? formatTimePrecise(log.end_time) : '-'}
Duration: ${log.end_time ? formatDuration(log) : 'In Progress'}

=== Output ===
${log.output || '// No output'}
`
  downloadFile(content, `log_${log.id}.log`)
}

function downloadCurrentLog() {
  if (!currentLog.value) return
  downloadSingleLog(currentLog.value)
}

function downloadFile(content, filename) {
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  fetchTasks()
  fetchLogs()
  startLiveDurationRefresh()
})
</script>

<style scoped>
.filter-card,
.logs-card {
  border-radius: var(--radius-lg);
}

.bulk-actions-bar {
  padding: 8px 16px;
}

.bulk-actions-bar :deep(.el-alert__title) {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.log-expand-preview {
  padding: var(--space-md);
  background-color: var(--bg-secondary);
  border-radius: var(--radius-md);
  margin: var(--space-sm) var(--space-md);
}

.expand-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.expand-content {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: var(--space-md);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  line-height: 1.6;
  max-height: 200px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--text-main);
}

.log-toolbar {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.log-metadata {
  margin-bottom: var(--space-md);
}

.terminal-output {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-base);
  max-height: 60vh;
  overflow: auto;
}

.gap-2 {
  gap: var(--space-sm);
}

.gap-3 {
  gap: var(--space-md);
}
</style>
