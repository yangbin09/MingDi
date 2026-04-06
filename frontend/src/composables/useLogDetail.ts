/**
 * 日志详情与 AI 诊断 Composable
 * 提取 Logs.vue 中的详情查看、AI 摘要、AI 诊断、文件下载逻辑
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { logApi, aiApi } from '../utils/api.js'
import type { LogEntry, Task } from './useLogSearch'

// ============= 状态定义 =============
const currentLog = ref<LogEntry | null>(null)
const showLogDrawer = ref(false)
const aiSummary = ref<string | null>(null)
const aiDiagnosis = ref<string | null>(null)
const aiSummarizing = ref(false)
const diagnosingLogId = ref<number | null>(null)

// ============= 工具函数 =============
function getTaskName(taskId: number, tasks: Task[]): string {
  const task = tasks.find(t => t.id === taskId)
  return task ? task.name : `任务 #${taskId}`
}

// 精确时间格式 YYYY-MM-DD HH:mm:ss
function formatTimePrecise(timeStr: string | null | undefined): string {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

// 时长格式化
function formatDuration(log: LogEntry): string {
  if (!log.start_time || !log.end_time) return '-'
  const duration = (new Date(log.end_time).getTime() - new Date(log.start_time).getTime()) / 1000
  if (duration < 60) {
    return `${duration.toFixed(1)}秒`
  } else if (duration < 3600) {
    const min = Math.floor(duration / 60)
    const sec = Math.floor(duration % 60)
    return `${min}分${sec}秒`
  } else {
    const hour = Math.floor(duration / 3600)
    const min = Math.floor((duration % 3600) / 60)
    return `${hour}小时${min}分`
  }
}

// 实时时长计算（运行中任务动态跳动）
function getLiveDuration(log: LogEntry): string {
  if (log.end_time) return formatDuration(log)
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

// 获取日志最后N行
function getLastLines(output: string | null, lines = 10): string {
  if (!output) return '// 无输出'
  const allLines = output.split('\n')
  const lastLines = allLines.slice(-lines)
  return lastLines.join('\n') || '// 无输出'
}

// ============= 文件下载 =============
function buildLogContent(log: LogEntry, tasks: Task[]): string {
  return `=== 鸣镝 Log #${log.id} ===
Task: ${getTaskName(log.task_id, tasks)}
Status: ${getStatusLabel(log)}
Start Time: ${formatTimePrecise(log.start_time)}
End Time: ${log.end_time ? formatTimePrecise(log.end_time) : '-'}
Duration: ${log.end_time ? formatDuration(log) : 'In Progress'}

=== Output ===
${log.output || '// No output'}
`
}

function downloadFile(content: string, filename: string): void {
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function downloadSingleLog(log: LogEntry, tasks: Task[]): void {
  const content = buildLogContent(log, tasks)
  const dateStr = new Date().toISOString().slice(0, 10)
  downloadFile(content, `log_${log.id}_${dateStr}.log`)
}

function downloadCurrentLog(tasks: Task[]): void {
  if (!currentLog.value) return
  downloadSingleLog(currentLog.value, tasks)
}

// ============= 状态判断 =============
// 状态判断：pending(等待)、running(运行中)、success(成功)、failed(失败)、timeout(超时)、cancelled(已取消)
function getStatus(log: LogEntry): string {
  if (!log.end_time) return 'running'
  if (log.exit_code === -1) return 'timeout'
  if (log.exit_code === 0) return 'success'
  if (log.exit_code !== null) return 'failed'
  return 'cancelled'
}

function getStatusLabel(log: LogEntry): string {
  const status = getStatus(log)
  const labels: Record<string, string> = {
    running: '运行中',
    success: '成功',
    failed: '失败',
    timeout: '超时',
    cancelled: '已取消',
    pending: '等待中'
  }
  return labels[status] || '未知'
}

function getStatusTagType(log: LogEntry): string {
  const status = getStatus(log)
  const types: Record<string, string> = {
    running: 'primary',
    success: 'success',
    failed: 'danger',
    timeout: 'warning',
    cancelled: 'info',
    pending: 'info'
  }
  return types[status] || 'info'
}

// ============= AI 功能 =============
async function summarizeLog(log: LogEntry): Promise<string | null> {
  if (!log.output) return null
  aiSummarizing.value = true
  try {
    const res = await aiApi.summarizeLog(log.output)
    aiSummary.value = res.data.summary
    return aiSummary.value
  } catch (e) {
    ElMessage.error('AI 摘要失败')
    return null
  } finally {
    aiSummarizing.value = false
  }
}

async function summarizeMultipleLogs(logsToSummarize: LogEntry[], tasks: Task[]): Promise<string | null> {
  if (logsToSummarize.length === 0) return null
  aiSummarizing.value = true
  try {
    const combinedOutput = logsToSummarize.map(l =>
      `=== ${getTaskName(l.task_id, tasks)} (Log #${l.id}) ===\n${l.output || '// 无输出'}`
    ).join('\n\n')
    const res = await aiApi.summarizeLog(combinedOutput)
    aiSummary.value = res.data.summary
    return aiSummary.value
  } catch (e) {
    ElMessage.error('AI 摘要失败')
    return null
  } finally {
    aiSummarizing.value = false
  }
}

async function diagnoseError(log: LogEntry): Promise<string | null> {
  diagnosingLogId.value = log.id
  aiDiagnosis.value = null
  try {
    const res = await aiApi.diagnoseError(log.output || '', '')
    aiDiagnosis.value = res.data.diagnosis
    return aiDiagnosis.value
  } catch (e) {
    ElMessage.error('AI 诊断失败')
    return null
  } finally {
    diagnosingLogId.value = null
  }
}

// ============= 抽屉控制 =============
function viewLogDetail(log: LogEntry): void {
  currentLog.value = log
  aiSummary.value = null
  aiDiagnosis.value = null
  showLogDrawer.value = true
}

function closeDrawer(): void {
  showLogDrawer.value = false
  currentLog.value = null
  aiSummary.value = null
  aiDiagnosis.value = null
}

// ============= 导出 =============
export function useLogDetail() {
  return {
    // 状态
    currentLog,
    showLogDrawer,
    aiSummary,
    aiDiagnosis,
    aiSummarizing,
    diagnosingLogId,

    // 工具函数
    getTaskName,
    formatTimePrecise,
    formatDuration,
    getLiveDuration,
    getLastLines,
    getStatus,
    getStatusLabel,
    getStatusTagType,

    // 文件下载
    downloadSingleLog,
    downloadCurrentLog,

    // AI 功能
    summarizeLog,
    summarizeMultipleLogs,
    diagnoseError,

    // 抽屉控制
    viewLogDetail,
    closeDrawer
  }
}
