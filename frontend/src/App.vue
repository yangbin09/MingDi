<template>
  <div class="min-h-screen bg-gray-900 text-white p-8">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">PyCron-Master</h1>
        <button
          @click="showCreateModal = true"
          class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition"
        >
          + 新建任务
        </button>
      </div>

      <!-- Task List -->
      <div class="bg-gray-800 rounded-xl overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-sm font-medium text-gray-300">状态</th>
              <th class="px-6 py-3 text-left text-sm font-medium text-gray-300">任务名称</th>
              <th class="px-6 py-3 text-left text-sm font-medium text-gray-300">脚本路径</th>
              <th class="px-6 py-3 text-left text-sm font-medium text-gray-300">Cron 表达式</th>
              <th class="px-6 py-3 text-left text-sm font-medium text-gray-300">最后运行</th>
              <th class="px-6 py-3 text-left text-sm font-medium text-gray-300">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-700">
            <tr v-for="task in tasks" :key="task.id" class="hover:bg-gray-750">
              <td class="px-6 py-4">
                <span
                  :class="statusClass(task.status)"
                  class="px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ statusText(task.status) }}
                </span>
              </td>
              <td class="px-6 py-4 font-medium">{{ task.name }}</td>
              <td class="px-6 py-4 text-gray-400 text-sm">{{ task.script_path }}</td>
              <td class="px-6 py-4 text-gray-400 text-sm font-mono">{{ task.cron_expr || '-' }}</td>
              <td class="px-6 py-4 text-gray-400 text-sm">
                {{ task.last_run_time ? formatTime(task.last_run_time) : '-' }}
              </td>
              <td class="px-6 py-4">
                <div class="flex gap-2">
                  <button
                    @click="runTask(task)"
                    :disabled="task.status === 'running'"
                    class="text-green-400 hover:text-green-300 disabled:opacity-50 text-sm"
                  >
                    运行
                  </button>
                  <button
                    @click="viewLogs(task)"
                    class="text-blue-400 hover:text-blue-300 text-sm"
                  >
                    日志
                  </button>
                  <button
                    @click="editTask(task)"
                    class="text-yellow-400 hover:text-yellow-300 text-sm"
                  >
                    编辑
                  </button>
                  <button
                    @click="deleteTask(task)"
                    class="text-red-400 hover:text-red-300 text-sm"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="tasks.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                暂无任务，点击右上角按钮创建第一个任务
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">{{ showEditModal ? '编辑任务' : '新建任务' }}</h2>
        <form @submit.prevent="submitForm">
          <div class="mb-4">
            <label class="block text-sm text-gray-400 mb-1">任务名称</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm text-gray-400 mb-1">脚本路径</label>
            <input
              v-model="form.script_path"
              type="text"
              required
              placeholder="./scripts/your_script.py"
              class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div class="mb-4">
            <label class="block text-sm text-gray-400 mb-1">Cron 表达式</label>
            <input
              v-model="form.cron_expr"
              type="text"
              placeholder="* * * * * (分 时 日 月 周)"
              class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>
          <div class="mb-6">
            <label class="flex items-center gap-2">
              <input v-model="form.is_active" type="checkbox" class="w-4 h-4" />
              <span class="text-sm">启用定时执行</span>
            </label>
          </div>
          <div class="flex justify-end gap-3">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 text-gray-400 hover:text-white"
            >
              取消
            </button>
            <button
              type="submit"
              class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
            >
              {{ showEditModal ? '保存' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Log Modal -->
    <div v-if="showLogModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-xl p-6 w-full max-w-4xl max-h-[80vh] flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">任务日志 - {{ currentTask?.name }}</h2>
          <button @click="showLogModal = false" class="text-gray-400 hover:text-white">✕</button>
        </div>
        <div class="flex-1 overflow-auto bg-gray-900 rounded p-4 font-mono text-sm">
          <div v-if="logs.length === 0" class="text-gray-500">暂无日志</div>
          <div v-for="log in logs" :key="log.id" class="mb-4 pb-4 border-b border-gray-700">
            <div class="flex gap-4 text-xs text-gray-400 mb-1">
              <span>开始: {{ formatTime(log.start_time) }}</span>
              <span v-if="log.end_time">结束: {{ formatTime(log.end_time) }}</span>
              <span :class="log.exit_code === 0 ? 'text-green-400' : 'text-red-400'">
                退出码: {{ log.exit_code }}
              </span>
            </div>
            <pre class="text-gray-300 whitespace-pre-wrap">{{ log.output || '无输出' }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const tasks = ref([])
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showLogModal = ref(false)
const currentTask = ref(null)
const logs = ref([])

const form = ref({
  name: '',
  script_path: './scripts/',
  cron_expr: '* * * * *',
  is_active: true
})

const api = axios.create({
  baseURL: 'http://localhost:8000'
})

onMounted(() => {
  fetchTasks()
  setInterval(fetchTasks, 5000)
})

async function fetchTasks() {
  try {
    const res = await api.get('/tasks')
    tasks.value = res.data
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
  }
}

async function submitForm() {
  try {
    if (showEditModal.value) {
      await api.put(`/tasks/${currentTask.value.id}`, form.value)
    } else {
      await api.post('/tasks', form.value)
    }
    closeModal()
    fetchTasks()
  } catch (e) {
    console.error('Failed to submit form:', e)
    alert('操作失败: ' + (e.response?.data?.detail || e.message))
  }
}

function editTask(task) {
  currentTask.value = task
  form.value = {
    name: task.name,
    script_path: task.script_path,
    cron_expr: task.cron_expr,
    is_active: task.is_active
  }
  showEditModal.value = true
}

async function deleteTask(task) {
  if (!confirm(`确定删除任务 "${task.name}" 吗？`)) return
  try {
    await api.delete(`/tasks/${task.id}`)
    fetchTasks()
  } catch (e) {
    console.error('Failed to delete task:', e)
  }
}

async function runTask(task) {
  try {
    await api.post(`/tasks/${task.id}/run`)
    fetchTasks()
  } catch (e) {
    console.error('Failed to run task:', e)
    alert('启动失败: ' + (e.response?.data?.detail || e.message))
  }
}

let logEventSource = null

async function viewLogs(task) {
  currentTask.value = task
  logs.value = []
  showLogModal.value = true

  try {
    const res = await api.get(`/tasks/${task.id}/logs`)
    logs.value = res.data

    if (logEventSource) {
      logEventSource.close()
    }

    logEventSource = new EventSource(`http://localhost:8000/tasks/${task.id}/logs/stream`)

    logEventSource.onmessage = (event) => {
      try {
        const newLog = JSON.parse(event.data)
        const exists = logs.value.find(l => l.id === newLog.id)
        if (!exists) {
          logs.value.unshift(newLog)
        }
      } catch (e) {
        console.error('Failed to parse log:', e)
      }
    }

    logEventSource.onerror = () => {
      console.error('SSE connection error')
    }
  } catch (e) {
    console.error('Failed to fetch logs:', e)
  }
}

function closeModal() {
  showCreateModal.value = false
  showEditModal.value = false
  showLogModal.value = false
  if (logEventSource) {
    logEventSource.close()
    logEventSource = null
  }
  currentTask.value = null
  form.value = {
    name: '',
    script_path: './scripts/',
    cron_expr: '* * * * *',
    is_active: true
  }
}

function statusClass(status) {
  const classes = {
    idle: 'bg-gray-600 text-gray-300',
    running: 'bg-blue-600 text-white',
    success: 'bg-green-600 text-white',
    failed: 'bg-red-600 text-white',
    timeout: 'bg-yellow-600 text-white'
  }
  return classes[status] || classes.idle
}

function statusText(status) {
  const texts = {
    idle: '闲置',
    running: '运行中',
    success: '成功',
    failed: '失败',
    timeout: '超时'
  }
  return texts[status] || status
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return d.toLocaleString('zh-CN')
}
</script>
