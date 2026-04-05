<template>
  <div class="logs-page space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--text-main);">
          <el-icon class="mr-2"><Document /></el-icon>
          日志中心
        </h1>
        <p class="text-sm mt-1" style="color: var(--text-muted);">集中查看和管理所有任务执行日志</p>
      </div>
      <el-button :icon="Refresh" circle @click="refreshLogs" :loading="loading" />
    </div>

    <!-- Filters -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="8" :md="6">
          <el-select v-model="filters.taskId" placeholder="选择任务" clearable @change="applyFilters">
            <el-option label="全部任务" :value="null" />
            <el-option v-for="task in tasks" :key="task.id" :label="task.name" :value="task.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-select v-model="filters.exitCode" placeholder="状态" clearable @change="applyFilters">
            <el-option label="全部" :value="null" />
            <el-option label="成功" :value="0" />
            <el-option label="失败" :value="1" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="16" :md="12">
          <el-input v-model="filters.keyword" placeholder="搜索日志内容..." @keyup.enter="applyFilters" clearable>
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
      </el-row>
      <el-row :gutter="16" class="mt-4">
        <el-col :span="12">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="applyFilters"
            style="width: 100%"
          />
        </el-col>
        <el-col :span="12" class="flex justify-end">
          <el-button
            v-if="selectedLogs.length > 0"
            type="primary"
            @click="summarizeSelectedLogs"
            :loading="aiSummarizing"
          >
            <el-icon><MagicStick /></el-icon>
            AI 摘要 ({{ selectedLogs.length }})
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Logs Table -->
    <el-card shadow="never" class="logs-card">
      <el-empty v-if="logs.length === 0" description="暂无日志记录" />

      <el-table
        v-else
        :data="logs"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
        :header-cell-style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }"
        :row-style="{ borderBottom: '1px solid var(--border-subtle)' }"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="任务" min-width="200">
          <template #default="{ row }">
            <div class="font-medium">{{ getTaskName(row.task_id) }}</div>
            <div class="text-xs" style="color: var(--text-muted);">Log #{{ row.id }}</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.exit_code === 0 ? 'success' : 'danger'" size="small">
              {{ row.exit_code === 0 ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="180">
          <template #default="{ row }">{{ formatTime(row.start_time) }}</template>
        </el-table-column>
        <el-table-column label="时长" width="100">
          <template #default="{ row }">
            <span class="font-mono">{{ formatDuration(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="right">
          <template #default="{ row }">
            <el-button-group>
              <el-tooltip content="查看详情" placement="top">
                <el-button size="small" type="primary" plain @click="viewLogDetail(row)">
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip v-if="row.exit_code !== 0" content="AI 诊断" placement="top">
                <el-button size="small" type="warning" plain @click="diagnoseLog(row)" :loading="diagnosingLogId === row.id">
                  <el-icon><MagicStick /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="下载" placement="top">
                <el-button size="small" type="success" plain @click="downloadSingleLog(row)">
                  <el-icon><Download /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-between items-center mt-4">
        <span class="text-sm" style="color: var(--text-muted);">
          第 {{ currentPage }} / {{ totalPages }} 页，共 {{ totalLogs }} 条
        </span>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalLogs"
          layout="prev, pager, next"
          @current-change="applyFilters"
        />
      </div>
    </el-card>

    <!-- Log Detail Drawer -->
    <el-drawer
      v-model="showLogDrawer"
      :title="'日志详情 - ' + (currentLog ? getTaskName(currentLog.task_id) : '')"
      size="700px"
    >
      <!-- Log Toolbar -->
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

      <!-- AI Summary Panel -->
      <el-alert
        v-if="aiSummary"
        :title="'AI 日志摘要'"
        type="success"
        :closable="true"
        @close="aiSummary = null"
        class="mb-3"
      >
        <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ aiSummary }}</pre>
      </el-alert>

      <!-- AI Diagnosis Panel -->
      <el-alert
        v-if="aiDiagnosis"
        :title="'AI 错误诊断'"
        type="error"
        :closable="true"
        @close="aiDiagnosis = null"
        class="mb-3"
      >
        <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ aiDiagnosis }}</pre>
      </el-alert>

      <!-- Log Metadata -->
      <div v-if="currentLog" class="log-metadata">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="状态">
            <el-tag :type="currentLog.exit_code === 0 ? 'success' : 'danger'">
              {{ currentLog.exit_code === 0 ? '成功' : '失败' }} (exit {{ currentLog.exit_code }})
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatTimeFull(currentLog.start_time) }}</el-descriptions-item>
          <el-descriptions-item v-if="currentLog.end_time" label="结束时间">{{ formatTimeFull(currentLog.end_time) }}</el-descriptions-item>
          <el-descriptions-item v-if="getDuration(currentLog)" label="时长">
            <span class="font-mono">{{ getDuration(currentLog) }}s</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- Terminal Output -->
      <div class="terminal-output">
        <pre class="whitespace-pre-wrap">{{ currentLog?.output || '// 无输出' }}</pre>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document, Refresh, Search, View, Download, MagicStick
} from '@element-plus/icons-vue'
import { taskApi, logApi, aiApi } from '../utils/api.js'
import { formatTimeFull } from '../utils/formatters.js'

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

const filters = ref({
  taskId: null,
  exitCode: null,
  keyword: ''
})

const currentPage = ref(1)
const pageSize = 20
const totalLogs = ref(0)

const totalPages = computed(() => Math.ceil(totalLogs.value / pageSize))

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
    const params = {}
    if (filters.value.taskId) params.task_id = filters.value.taskId
    if (filters.value.exitCode !== null && filters.value.exitCode !== '') params.exit_code = filters.value.exitCode
    if (filters.value.keyword) params.keyword = filters.value.keyword

    const res = await logApi.search(params)
    totalLogs.value = res.data.length
    logs.value = res.data.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize)
    selectedLogs.value = []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function refreshLogs() {
  fetchLogs()
}

function applyFilters() {
  currentPage.value = 1
  fetchLogs()
}

function getTaskName(taskId) {
  const task = tasks.value.find(t => t.id === taskId)
  return task ? task.name : `任务 #${taskId}`
}

function formatTime(timeStr) {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatDuration(log) {
  if (!log.start_time || !log.end_time) return '-'
  const duration = (new Date(log.end_time) - new Date(log.start_time)) / 1000
  return duration.toFixed(1)
}

function getDuration(log) {
  return formatDuration(log)
}

function handleSelectionChange(selection) {
  selectedLogs.value = selection.map(l => l.id)
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
Status: ${log.exit_code === 0 ? 'Success' : 'Failed'}
Start Time: ${log.start_time}
End Time: ${log.end_time || '-'}
Duration: ${formatDuration(log)}s

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
})
</script>

<style scoped>
.filter-card {
  border-radius: 12px;
}

.logs-card {
  border-radius: 12px;
}

.log-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.log-metadata {
  margin-bottom: 16px;
}

.terminal-output {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.5;
  max-height: 60vh;
  overflow: auto;
}
</style>
