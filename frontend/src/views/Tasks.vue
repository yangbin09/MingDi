<template>
  <div class="tasks-page space-y-6">
    <!-- Page Header -->
    <div class="flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="page-indicator"></div>
        <span class="text-sm" style="color: var(--text-muted);">共 <span style="color: var(--text-main); font-weight: 500;">{{ tasks.length }}</span> 个任务</span>
      </div>
      <el-button type="primary" @click="openCreateDrawer">
        <el-icon><Plus /></el-icon>
        新建任务
      </el-button>
    </div>

    <!-- Tasks Table -->
    <el-card shadow="never" class="tasks-card">
      <el-empty v-if="tasks.length === 0" description="暂无任务，点击右上角按钮创建第一个任务" />

      <el-table
        v-else
        :data="tasks"
        stripe
        style="width: 100%"
        :header-cell-style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }"
      >
        <el-table-column label="状态" width="60" align="center">
          <template #default="{ row }">
            <span class="relative flex h-3 w-3 justify-center">
              <span v-if="row.status === 'running'" class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :style="{ backgroundColor: 'var(--color-primary)' }"></span>
              <span
                class="relative inline-flex rounded-full h-3 w-3"
                :style="{ backgroundColor: getStatusColor(row.status) }"
              ></span>
            </span>
          </template>
        </el-table-column>

        <el-table-column label="任务" min-width="280">
          <template #default="{ row }">
            <div class="font-medium" style="color: var(--text-main);">{{ row.name }}</div>
            <div class="flex items-center gap-2 mt-1">
              <code class="text-xs font-mono" style="color: var(--text-muted);">{{ row.script_path }}</code>
              <el-tag v-if="row.interpreter_path" size="small" type="info">
                {{ row.interpreter_path.split('/').pop().split('\\').pop() }}
              </el-tag>
              <el-tag v-if="row.webhook_enabled" size="small" type="primary">
                <el-icon><Link /></el-icon>
                Webhook
              </el-tag>
              <el-tag v-if="row.use_docker" size="small" type="success">
                <el-icon><Box /></el-icon>
                Docker
              </el-tag>
            </div>
            <div v-if="row.description" class="text-xs mt-1 truncate max-w-md" style="color: var(--text-disabled);">
              {{ row.description }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="依赖" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.depends_on" size="small" type="warning">
              <el-icon><ArrowRight /></el-icon>
              {{ getTaskName(row.depends_on) }}
            </el-tag>
            <span v-else style="color: var(--text-disabled);">-</span>
          </template>
        </el-table-column>

        <el-table-column label="定时" width="140">
          <template #default="{ row }">
            <code
              class="text-xs px-2 py-1 rounded font-mono"
              style="background-color: var(--bg-tertiary); color: var(--color-primary);"
            >{{ row.cron_expr || '-' }}</code>
          </template>
        </el-table-column>

        <el-table-column label="启用" width="80" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active"
              @change="handleToggle(row)"
              active-color="var(--color-success)"
              inactive-color="var(--bg-tertiary)"
            />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="right">
          <template #default="{ row }">
            <el-button-group>
              <el-tooltip content="立即运行" placement="top">
                <el-button :icon="VideoPlay" @click="handleRun(row)" :disabled="row.status === 'running'" size="small" type="success" plain />
              </el-tooltip>
              <el-tooltip content="查看日志" placement="top">
                <el-button :icon="Document" @click="handleViewLogs(row)" size="small" type="primary" plain />
              </el-tooltip>
              <el-tooltip content="编辑" placement="top">
                <el-button :icon="Edit" @click="openEditDrawer(row)" size="small" type="warning" plain />
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <el-button :icon="Delete" @click="handleDelete(row)" size="small" type="danger" plain />
              </el-tooltip>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Task Drawer -->
    <TaskDrawer
      v-model="showDrawer"
      :task="currentTask"
      :tasks="tasks"
      @success="handleTaskSuccess"
    />

    <!-- Log Drawer -->
    <LogDrawer
      v-model="showLogDrawer"
      :task="currentTask"
      :logs="taskLogs"
      @run="handleRun"
      @download="handleDownloadLogs"
      @refresh="fetchTaskLogsData"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { Plus, VideoPlay, Edit, Delete, Document, Link, Box, ArrowRight } from '@element-plus/icons-vue'
import { useTask } from '../composables/useTask.js'
import { usePolling } from '../composables/usePolling.js'
import TaskDrawer from '../components/Task/TaskDrawer.vue'
import LogDrawer from '../components/Task/LogDrawer.vue'

const {
  tasks,
  fetchTasks,
  createTask,
  updateTask,
  deleteTask,
  toggleTask,
  runTask,
  fetchTaskLogs,
  getTaskById
} = useTask()

const showDrawer = ref(false)
const isEditing = ref(false)
const currentTask = ref(null)
const showLogDrawer = ref(false)
const taskLogs = ref([])

// Set up polling
const { start: startPolling, stop: stopPolling } = usePolling(fetchTasks, 5000)

function getStatusColor(status) {
  const colors = {
    running: 'var(--color-primary)',
    success: 'var(--color-primary)',
    failed: 'var(--color-danger)',
    timeout: 'var(--color-warning)',
    idle: 'var(--text-muted)'
  }
  return colors[status] || 'var(--text-muted)'
}

function getTaskName(taskId) {
  const task = getTaskById(taskId)
  return task ? task.name : 'Unknown'
}

function openCreateDrawer() {
  currentTask.value = null
  showDrawer.value = true
}

function openEditDrawer(task) {
  currentTask.value = task
  showDrawer.value = true
}

async function handleTaskSuccess(payload) {
  try {
    if (currentTask.value?.id) {
      await updateTask(currentTask.value.id, payload)
    } else {
      await createTask(payload)
    }
  } catch (e) {
    console.error('Task operation failed:', e)
  }
}

async function handleToggle(task) {
  try {
    await toggleTask(task.id, task.is_active)
  } catch (e) {
    console.error('Toggle failed:', e)
  }
}

async function handleRun(task) {
  if (!task) return
  try {
    await runTask(task.id)
  } catch (e) {
    console.error('Run failed:', e)
  }
}

async function handleDelete(task) {
  try {
    await ElMessageBox.confirm(`确定删除任务 "${task.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteTask(task.id)
  } catch (e) {
    if (e !== 'cancel') {
      console.error('Delete failed:', e)
    }
  }
}

async function handleViewLogs(task) {
  currentTask.value = task
  await fetchTaskLogsData()
  showLogDrawer.value = true
}

async function fetchTaskLogsData() {
  if (currentTask.value?.id) {
    taskLogs.value = await fetchTaskLogs(currentTask.value.id)
  }
}

function handleDownloadLogs({ logs, task }) {
  if (!logs.length) return
  const content = logs.map((l, i) =>
    `=== Session ${i + 1} ===\nTime: ${l.start_time}\nExit: ${l.exit_code}\n\n${l.output || '// No output'}\n`
  ).join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `task_${task.id}_logs_${new Date().toISOString().slice(0,10)}.log`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  fetchTasks()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.tasks-page {
  width: 100%;
}

.page-indicator {
  width: 32px;
  height: 4px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--color-primary), var(--color-success));
}

.tasks-card {
  border-radius: var(--radius-lg);
}
</style>
