<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--text-main);">日志中心</h1>
        <p class="text-sm mt-1" style="color: var(--text-muted);">集中查看和管理所有任务执行日志</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="refreshLogs"
          class="p-2 rounded-lg transition-colors"
          :style="{ color: 'var(--text-muted)' }"
          title="刷新"
          @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
          @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
        >
          <ArrowPathIcon class="w-5 h-5" :class="{ 'animate-spin': loading }" />
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card rounded-xl p-4">
      <div class="flex flex-wrap gap-4">
        <!-- Task Filter -->
        <div class="flex items-center gap-2">
          <label class="text-sm" style="color: var(--text-muted);">任务:</label>
          <select v-model="filters.taskId" class="input py-1.5 text-sm" @change="applyFilters">
            <option :value="null">全部任务</option>
            <option v-for="task in tasks" :key="task.id" :value="task.id">{{ task.name }}</option>
          </select>
        </div>

        <!-- Status Filter -->
        <div class="flex items-center gap-2">
          <label class="text-sm" style="color: var(--text-muted);">状态:</label>
          <select v-model="filters.exitCode" class="input py-1.5 text-sm" @change="applyFilters">
            <option :value="null">全部</option>
            <option :value="0">成功</option>
            <option :value="1">失败</option>
          </select>
        </div>

        <!-- Date Filter -->
        <div class="flex items-center gap-2">
          <label class="text-sm" style="color: var(--text-muted);">日期:</label>
          <input
            v-model="filters.startDate"
            type="date"
            class="input py-1.5 text-sm"
            @change="applyFilters"
          />
          <span style="color: var(--text-muted);">-</span>
          <input
            v-model="filters.endDate"
            type="date"
            class="input py-1.5 text-sm"
            @change="applyFilters"
          />
        </div>

        <!-- Search -->
        <div class="flex-1 min-w-64">
          <div class="relative">
            <input
              v-model="filters.keyword"
              type="text"
              class="input pl-10 py-1.5 text-sm w-full"
              placeholder="搜索日志内容..."
              @keyup.enter="applyFilters"
            />
            <MagnifyingGlassIcon class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2" style="color: var(--text-muted);" />
          </div>
        </div>

        <!-- AI Summary Button -->
        <button
          v-if="selectedLogs.length > 0"
          @click="summarizeSelectedLogs"
          :disabled="aiSummarizing"
          class="flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-medium transition-all"
          :style="{ backgroundColor: 'var(--color-purple)', color: 'var(--text-inverse)' }"
        >
          <SparklesIcon class="w-4 h-4" :class="{ 'animate-spin': aiSummarizing }" />
          AI 摘要 ({{ selectedLogs.length }})
        </button>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="card rounded-xl overflow-hidden">
      <div v-if="logs.length === 0" class="text-center py-16">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
          <CommandLineIcon class="w-8 h-8" style="color: var(--text-muted); opacity: 0.5;" />
        </div>
        <p class="text-lg" style="color: var(--text-muted);">暂无日志记录</p>
        <p class="text-sm mt-1" style="color: var(--text-disabled);">执行任务后将显示日志</p>
      </div>

      <table v-else class="w-full">
        <thead :style="{ backgroundColor: 'var(--bg-tertiary)' }">
          <tr>
            <th class="px-4 py-3.5 text-left w-8">
              <input
                type="checkbox"
                :checked="allSelected"
                @change="toggleSelectAll"
                class="w-4 h-4"
                :style="{ accentColor: 'var(--color-primary)' }"
              />
            </th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">任务</th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider w-24" style="color: var(--text-muted);">状态</th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">开始时间</th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">时长</th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="log in logs"
            :key="log.id"
            class="theme-transition"
            :style="{ borderBottom: '1px solid var(--border-subtle)' }"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
          >
            <td class="px-4 py-4">
              <input
                type="checkbox"
                :checked="selectedLogs.includes(log.id)"
                @change="toggleSelect(log.id)"
                class="w-4 h-4"
                :style="{ accentColor: 'var(--color-primary)' }"
              />
            </td>
            <td class="px-4 py-4">
              <div class="font-medium" style="color: var(--text-main);">{{ getTaskName(log.task_id) }}</div>
              <div class="text-xs" style="color: var(--text-muted);">Log #{{ log.id }}</div>
            </td>
            <td class="px-4 py-4">
              <span
                class="px-2 py-1 rounded text-xs font-medium"
                :style="log.exit_code === 0
                  ? { backgroundColor: 'var(--color-success-subtle)', color: 'var(--color-success)' }
                  : { backgroundColor: 'var(--color-danger-subtle)', color: 'var(--color-danger)' }"
              >
                {{ log.exit_code === 0 ? '成功' : '失败' }}
              </span>
            </td>
            <td class="px-4 py-4 text-sm" style="color: var(--text-muted);">
              {{ formatTime(log.start_time) }}
            </td>
            <td class="px-4 py-4 text-sm font-mono" style="color: var(--text-muted);">
              {{ formatDuration(log) }}
            </td>
            <td class="px-4 py-4">
              <div class="flex items-center gap-1">
                <button
                  @click="viewLogDetail(log)"
                  class="p-2 rounded-lg transition-colors"
                  :style="{ color: 'var(--text-muted)' }"
                  title="查看详情"
                  @mouseenter="($event.currentTarget.style.color = 'var(--color-primary)', $event.currentTarget.style.backgroundColor = 'var(--color-primary-subtle)')"
                  @mouseleave="($event.currentTarget.style.color = 'var(--text-muted)', $event.currentTarget.style.backgroundColor = 'transparent')"
                >
                  <EyeIcon class="w-4 h-4" />
                </button>
                <button
                  v-if="log.exit_code !== 0"
                  @click="diagnoseLog(log)"
                  :disabled="diagnosingLogId === log.id"
                  class="p-2 rounded-lg transition-colors"
                  :style="{ color: 'var(--color-warning)' }"
                  title="AI 诊断"
                  @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--color-warning-subtle)')"
                  @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
                >
                  <SparklesIcon class="w-4 h-4" :class="{ 'animate-spin': diagnosingLogId === log.id }" />
                </button>
                <button
                  @click="downloadSingleLog(log)"
                  class="p-2 rounded-lg transition-colors"
                  :style="{ color: 'var(--text-muted)' }"
                  title="下载"
                  @mouseenter="($event.currentTarget.style.color = 'var(--color-success)', $event.currentTarget.style.backgroundColor = 'var(--color-success-subtle)')"
                  @mouseleave="($event.currentTarget.style.color = 'var(--text-muted)', $event.currentTarget.style.backgroundColor = 'transparent')"
                >
                  <ArrowDownTrayIcon class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3" :style="{ borderTop: '1px solid var(--border-subtle)' }">
        <div class="text-sm" style="color: var(--text-muted);">
          第 {{ currentPage }} / {{ totalPages }} 页，共 {{ totalLogs }} 条
        </div>
        <div class="flex gap-2">
          <button
            @click="currentPage--; applyFilters()"
            :disabled="currentPage <= 1"
            class="px-3 py-1 rounded text-sm"
            :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)', opacity: currentPage <= 1 ? 0.5 : 1 }"
          >
            上一页
          </button>
          <button
            @click="currentPage++; applyFilters()"
            :disabled="currentPage >= totalPages"
            class="px-3 py-1 rounded text-sm"
            :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)', opacity: currentPage >= totalPages ? 0.5 : 1 }"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- Log Detail Drawer -->
    <div v-if="showLogDrawer" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 backdrop-blur-sm" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }" @click="closeLogDrawer"></div>
      <div
        class="absolute right-0 top-0 h-full w-full max-w-4xl theme-transition overflow-hidden"
        :style="{ backgroundColor: 'var(--bg-primary)', borderLeft: '1px solid var(--border-subtle)' }"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-5 py-4" :style="{ backgroundColor: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)' }">
          <div class="flex items-center gap-3">
            <div class="h-1 w-6 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-primary), var(--color-success))' }"></div>
            <div>
              <h3 class="font-semibold" style="color: var(--text-main);">{{ currentLog ? getTaskName(currentLog.task_id) : '' }}</h3>
              <p class="text-xs" style="color: var(--text-muted);">Log #{{ currentLog?.id }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="currentLog && currentLog.output && currentLog.output.length > 500"
              @click="summarizeCurrentLog"
              :disabled="aiSummarizing"
              class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-all"
              :style="{ color: 'var(--color-purple)', backgroundColor: 'rgba(168, 85, 247, 0.15)' }"
            >
              <SparklesIcon class="w-4 h-4" :class="{ 'animate-spin': aiSummarizing }" />
              AI 摘要
            </button>
            <button
              @click="downloadCurrentLog"
              class="p-2 rounded-lg transition-colors"
              :style="{ color: 'var(--text-muted)' }"
              title="下载日志"
            >
              <ArrowDownTrayIcon class="w-5 h-5" />
            </button>
            <button
              @click="closeLogDrawer"
              class="p-2 rounded-lg transition-colors"
              :style="{ color: 'var(--text-muted)' }"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- AI Summary Panel -->
        <div v-if="aiSummary" class="px-5 py-3" :style="{ backgroundColor: 'var(--color-primary-subtle)', borderBottom: '1px solid var(--border-subtle)' }">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <SparklesIcon class="w-4 h-4" :style="{ color: 'var(--color-primary)' }" />
              <span class="text-sm font-medium" :style="{ color: 'var(--color-primary)' }">AI 日志摘要</span>
            </div>
            <button @click="aiSummary = null" class="p-1 rounded hover:bg-bg-hover">
              <XMarkIcon class="w-3 h-3" style="color: var(--text-muted);" />
            </button>
          </div>
          <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ aiSummary }}</pre>
        </div>

        <!-- AI Diagnosis Panel -->
        <div v-if="aiDiagnosis" class="px-5 py-3" :style="{ backgroundColor: 'var(--color-danger-subtle)', borderBottom: '1px solid var(--border-subtle)' }">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <SparklesIcon class="w-4 h-4" style="color: var(--color-danger);" />
              <span class="text-sm font-medium" style="color: var(--color-danger);">AI 错误诊断</span>
            </div>
            <button @click="aiDiagnosis = null" class="p-1 rounded hover:bg-bg-hover">
              <XMarkIcon class="w-3 h-3" style="color: var(--text-muted);" />
            </button>
          </div>
          <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ aiDiagnosis }}</pre>
        </div>

        <!-- Log Content -->
        <div class="p-5 overflow-auto" :style="{ height: 'calc(100% - 64px)' }">
          <div v-if="currentLog" class="space-y-4">
            <!-- Metadata -->
            <div class="flex flex-wrap gap-4 text-sm" style="color: var(--text-muted);">
              <div>
                <span class="font-medium">状态:</span>
                <span
                  class="ml-1 px-2 py-0.5 rounded text-xs"
                  :style="currentLog.exit_code === 0
                    ? { backgroundColor: 'var(--color-success-subtle)', color: 'var(--color-success)' }
                    : { backgroundColor: 'var(--color-danger-subtle)', color: 'var(--color-danger)' }"
                >
                  {{ currentLog.exit_code === 0 ? '成功' : '失败' }} (exit {{ currentLog.exit_code }})
                </span>
              </div>
              <div>
                <span class="font-medium">开始:</span>
                <span class="ml-1">{{ formatTimeFull(currentLog.start_time) }}</span>
              </div>
              <div v-if="currentLog.end_time">
                <span class="font-medium">结束:</span>
                <span class="ml-1">{{ formatTimeFull(currentLog.end_time) }}</span>
              </div>
              <div v-if="getDuration(currentLog)">
                <span class="font-medium">时长:</span>
                <span class="ml-1 font-mono">{{ getDuration(currentLog) }}s</span>
              </div>
            </div>

            <!-- Terminal Output -->
            <div
              class="rounded-lg p-4 font-mono text-sm overflow-auto"
              :style="{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', maxHeight: 'calc(100% - 100px)' }"
            >
              <pre class="whitespace-pre-wrap" :style="{ color: 'var(--text-main)' }">{{ currentLog.output || '// 无输出' }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  ArrowPathIcon, MagnifyingGlassIcon, SparklesIcon,
  CommandLineIcon, EyeIcon, ArrowDownTrayIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
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

const filters = ref({
  taskId: null,
  exitCode: null,
  startDate: '',
  endDate: '',
  keyword: ''
})

const currentPage = ref(1)
const pageSize = 20
const totalLogs = ref(0)

const totalPages = computed(() => Math.ceil(totalLogs.value / pageSize))
const allSelected = computed(() => logs.value.length > 0 && logs.value.every(l => selectedLogs.value.includes(l.id)))

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
    // Build search params
    const params = {}
    if (filters.value.taskId) params.task_id = filters.value.taskId
    if (filters.value.exitCode !== null && filters.value.exitCode !== '') params.exit_code = filters.value.exitCode
    if (filters.value.startDate) params.start_date = filters.value.startDate
    if (filters.value.endDate) params.end_date = filters.value.endDate
    if (filters.value.keyword) params.keyword = filters.value.keyword

    // For now, fetch all and do client-side pagination (backend doesn't support pagination yet)
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

function toggleSelect(logId) {
  const idx = selectedLogs.value.indexOf(logId)
  if (idx >= 0) {
    selectedLogs.value.splice(idx, 1)
  } else {
    selectedLogs.value.push(logId)
  }
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedLogs.value = []
  } else {
    selectedLogs.value = logs.value.map(l => l.id)
  }
}

function viewLogDetail(log) {
  currentLog.value = log
  aiSummary.value = null
  aiDiagnosis.value = null
  showLogDrawer.value = true
}

function closeLogDrawer() {
  showLogDrawer.value = false
  currentLog.value = null
}

async function summarizeCurrentLog() {
  if (!currentLog.value?.output || aiSummarizing.value) return
  aiSummarizing.value = true
  try {
    const res = await aiApi.summarizeLog(currentLog.value.output)
    aiSummary.value = res.data.summary
  } catch (e) {
    console.error('AI 摘要失败:', e)
  } finally {
    aiSummarizing.value = false
  }
}

async function summarizeSelectedLogs() {
  if (selectedLogs.value.length === 0 || aiSummarizing.value) return
  // Combine all selected logs for summary
  const selectedLogData = logs.value.filter(l => selectedLogs.value.includes(l.id))
  const combinedOutput = selectedLogData.map(l => `=== ${getTaskName(l.task_id)} (Log #${l.id}) ===\n${l.output || '// 无输出'}`).join('\n\n')
  aiSummarizing.value = true
  try {
    const res = await aiApi.summarizeLog(combinedOutput)
    aiSummary.value = res.data.summary
  } catch (e) {
    console.error('AI 摘要失败:', e)
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
    console.error('AI 诊断失败:', e)
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
