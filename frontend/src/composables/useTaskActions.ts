/**
 * 任务操作 Composable
 * 提取 Tasks.vue 中的任务操作逻辑（CRUD、状态切换、运行、删除）
 */
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi } from '../utils/api.js'
import type { Task } from 'vue'

// ============= 状态定义 =============
const currentTask = ref<Task | null>(null)
const showDrawer = ref(false)
const showLogDrawer = ref(false)
const taskLogs = ref<any[]>([])

// ============= 状态颜色 =============
const STATUS_COLORS: Record<string, string> = {
  running: 'var(--color-primary)',
  success: 'var(--color-primary)',
  failed: 'var(--color-danger)',
  timeout: 'var(--color-warning)',
  idle: 'var(--text-muted)'
}

function getStatusColor(status: string): string {
  return STATUS_COLORS[status] || 'var(--text-muted)'
}

// ============= 任务操作 =============
async function toggleTask(task: Task): Promise<void> {
  try {
    await taskApi.toggle(task.id, !task.is_active)
    ElMessage.success(task.is_active ? '任务已禁用' : '任务已启用')
  } catch (e) {
    ElMessage.error('操作失败')
    throw e
  }
}

async function runTask(taskId: number): Promise<void> {
  try {
    await taskApi.run(taskId)
    ElMessage.success('任务已启动')
    // 延迟刷新让后端有足够时间更新状态
    setTimeout(() => fetchTasks(), 1000)
  } catch (e) {
    ElMessage.error('启动失败: ' + (e as any)?.response?.data?.detail || (e as Error).message)
    throw e
  }
}

async function deleteTask(task: Task, fetchTasks: () => Promise<void>): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `确定删除任务 "${task.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await taskApi.delete(task.id)
    ElMessage.success('任务已删除')
    await fetchTasks()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败: ' + (e as any)?.response?.data?.detail || (e as Error).message)
      throw e
    }
  }
}

// ============= 抽屉控制 =============
function openCreateDrawer(): void {
  currentTask.value = null
  showDrawer.value = true
}

function openEditDrawer(task: Task): void {
  currentTask.value = task
  showDrawer.value = true
}

function closeDrawer(): void {
  showDrawer.value = false
  currentTask.value = null
}

// ============= 日志抽屉 =============
async function openLogDrawer(task: Task, fetchTaskLogsFn: (taskId: number) => Promise<any[]>): Promise<void> {
  currentTask.value = task
  taskLogs.value = await fetchTaskLogsFn(task.id)
  showLogDrawer.value = true
}

function closeLogDrawer(): void {
  showLogDrawer.value = false
  currentTask.value = null
  taskLogs.value = []
}

// ============= 日志下载 =============
function downloadTaskLogs(logs: any[], task: Task): void {
  if (!logs.length) return
  const content = logs.map((l, i) =>
    `=== Session ${i + 1} ===\nTime: ${l.start_time}\nExit: ${l.exit_code}\n\n${l.output || '// No output'}\n`
  ).join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `task_${task.id}_logs_${new Date().toISOString().slice(0, 10)}.log`
  a.click()
  URL.revokeObjectURL(url)
}

// ============= 导出 =============
export function useTaskActions() {
  return {
    // 状态
    currentTask,
    showDrawer,
    showLogDrawer,
    taskLogs,

    // 工具
    getStatusColor,

    // 操作
    toggleTask,
    runTask,
    deleteTask,

    // 抽屉控制
    openCreateDrawer,
    openEditDrawer,
    closeDrawer,
    openLogDrawer,
    closeLogDrawer,

    // 日志下载
    downloadTaskLogs
  }
}
