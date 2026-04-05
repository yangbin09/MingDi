<template>
  <div class="space-y-6">
    <!-- Header Actions -->
    <div class="flex justify-between items-center">
      <div class="text-sm text-gray-400">
        共 {{ tasks.length }} 个任务
      </div>
      <button
        @click="openCreateDrawer"
        class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-black font-medium px-4 py-2 rounded-lg transition"
      >
        <PlusIcon class="w-5 h-5" />
        新建任务
      </button>
    </div>

    <!-- Tasks Table -->
    <div class="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <div v-if="tasks.length === 0" class="text-center text-gray-500 py-16">
        <InboxIcon class="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>暂无任务</p>
        <p class="text-sm mt-1">点击右上角按钮创建第一个任务</p>
      </div>

      <table v-else class="w-full">
        <thead class="bg-gray-800/50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider w-10">状态</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">任务</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">下次执行</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider w-32">定时</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider w-24">启用</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider w-48">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800">
          <tr
            v-for="task in tasks"
            :key="task.id"
            class="hover:bg-gray-800/30 transition"
          >
            <!-- Status -->
            <td class="px-4 py-4">
              <span class="relative flex h-3 w-3">
                <span
                  v-if="task.status === 'running'"
                  class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
                ></span>
                <span
                  class="relative inline-flex rounded-full h-3 w-3"
                  :class="statusDotClass(task.status)"
                ></span>
              </span>
            </td>

            <!-- Task Info -->
            <td class="px-4 py-4">
              <div class="font-medium">{{ task.name }}</div>
              <div class="text-xs text-gray-500 mt-0.5">{{ task.script_path }}</div>
            </td>

            <!-- Next Run -->
            <td class="px-4 py-4 text-sm text-gray-400">
              <span v-if="task.cron_expr && task.is_active">{{ getNextRun(task.cron_expr) }}</span>
              <span v-else class="text-gray-600">-</span>
            </td>

            <!-- Cron -->
            <td class="px-4 py-4">
              <code class="text-xs bg-gray-800 px-2 py-1 rounded text-emerald-400">{{ task.cron_expr || '-' }}</code>
            </td>

            <!-- Toggle -->
            <td class="px-4 py-4">
              <button
                @click="toggleTask(task)"
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
                :class="task.is_active ? 'bg-emerald-500' : 'bg-gray-700'"
              >
                <span
                  class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                  :class="task.is_active ? 'translate-x-6' : 'translate-x-1'"
                />
              </button>
            </td>

            <!-- Actions -->
            <td class="px-4 py-4">
              <div class="flex items-center justify-end gap-1">
                <button
                  @click="runTask(task)"
                  :disabled="task.status === 'running'"
                  class="p-2 text-gray-400 hover:text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition disabled:opacity-50"
                  title="立即运行"
                >
                  <PlayIcon class="w-4 h-4" />
                </button>
                <button
                  @click="openLogDrawer(task)"
                  class="p-2 text-gray-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition"
                  title="查看日志"
                >
                  <CommandLineIcon class="w-4 h-4" />
                </button>
                <button
                  @click="openEditDrawer(task)"
                  class="p-2 text-gray-400 hover:text-yellow-400 hover:bg-yellow-500/10 rounded-lg transition"
                  title="编辑"
                >
                  <PencilIcon class="w-4 h-4" />
                </button>
                <button
                  @click="deleteTask(task)"
                  class="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition"
                  title="删除"
                >
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Task Drawer -->
  <div
    v-if="showDrawer"
    class="fixed inset-0 z-50 overflow-hidden"
  >
    <div class="absolute inset-0 bg-black/60" @click="closeDrawer"></div>
    <div
      class="absolute right-0 top-0 h-full w-full max-w-xl bg-gray-900 border-l border-gray-800 transform transition-transform"
      :class="showDrawer ? 'translate-x-0' : 'translate-x-full'"
    >
      <div class="flex items-center justify-between p-4 border-b border-gray-800">
        <h2 class="text-lg font-semibold">{{ isEditing ? '编辑任务' : '新建任务' }}</h2>
        <button @click="closeDrawer" class="p-2 hover:bg-gray-800 rounded-lg">
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <div class="p-4 overflow-y-auto h-[calc(100vh-65px)]">
        <form @submit.prevent="submitForm" class="space-y-6">
          <!-- Task Name -->
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">任务名称</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500"
              placeholder="输入任务名称"
            />
          </div>

          <!-- Script Mode -->
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">脚本来源</label>
            <div class="flex gap-4 mb-3">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  v-model="scriptMode"
                  value="path"
                  class="accent-emerald-500"
                />
                <span class="text-sm">服务器路径</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  v-model="scriptMode"
                  value="editor"
                  class="accent-emerald-500"
                />
                <span class="text-sm">在线编辑</span>
              </label>
            </div>

            <!-- Path Mode -->
            <div v-if="scriptMode === 'path'">
              <input
                v-model="form.script_path"
                type="text"
                required
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500 font-mono text-sm"
                placeholder="./scripts/my_script.py"
              />
            </div>

            <!-- Editor Mode -->
            <div v-else class="border border-gray-700 rounded-lg overflow-hidden">
              <div class="bg-gray-800 px-3 py-2 text-xs text-gray-400 border-b border-gray-700 flex items-center justify-between">
                <span>Python Editor</span>
                <span class="text-emerald-500">Python 3</span>
              </div>
              <vue-monaco-editor
                v-model:value="form.script_content"
                language="python"
                theme="vs-dark"
                :options="{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 4,
                  wordWrap: 'on',
                  padding: { top: 8 }
                }"
                height="250px"
              />
            </div>
          </div>

          <!-- Cron Expression -->
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">定时执行</label>
            <div class="grid grid-cols-4 gap-2 mb-3">
              <button
                type="button"
                v-for="preset in cronPresets"
                :key="preset.value"
                @click="form.cron_expr = preset.value"
                class="px-3 py-2 text-xs rounded-lg border transition"
                :class="form.cron_expr === preset.value ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400' : 'border-gray-700 text-gray-400 hover:border-gray-600'"
              >
                {{ preset.label }}
              </button>
            </div>
            <input
              v-model="form.cron_expr"
              type="text"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500 font-mono"
              placeholder="* * * * *"
            />
            <p class="text-xs text-gray-500 mt-2" v-if="form.cron_expr">
              {{ cronHumanText(form.cron_expr) }}
            </p>
          </div>

          <!-- Timeout -->
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">超时时间 (秒)</label>
            <input
              v-model.number="form.timeout"
              type="number"
              min="0"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500"
              placeholder="300"
            />
          </div>

          <!-- Submit -->
          <div class="flex gap-3 pt-4 border-t border-gray-800">
            <button
              type="button"
              @click="closeDrawer"
              class="flex-1 px-4 py-2.5 border border-gray-700 rounded-lg hover:bg-gray-800 transition"
            >
              取消
            </button>
            <button
              type="submit"
              class="flex-1 px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-black font-medium rounded-lg transition"
            >
              {{ isEditing ? '保存' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Log Drawer -->
  <div
    v-if="showLogDrawer"
    class="fixed inset-0 z-50 overflow-hidden"
  >
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="closeLogDrawer"></div>
    <div
      class="absolute right-0 top-0 h-full w-full max-w-3xl bg-black border-l border-gray-800 transform transition-transform duration-300"
      :class="showLogDrawer ? 'translate-x-0' : 'translate-x-full'"
    >
      <!-- Terminal Header -->
      <div class="flex items-center justify-between px-4 py-3 bg-gray-900 border-b border-gray-800">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-red-500"></div>
            <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div class="w-3 h-3 rounded-full bg-emerald-500"></div>
          </div>
          <div>
            <span class="text-sm font-medium">{{ currentTask?.name }}</span>
            <span class="text-xs text-gray-500 ml-2">bash</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="runTask(currentTask)"
            class="px-3 py-1 text-xs bg-emerald-500/20 text-emerald-400 rounded hover:bg-emerald-500/30 transition"
          >
            ▶ 运行
          </button>
          <button
            @click="refreshLogs"
            class="p-1.5 hover:bg-gray-800 rounded transition"
            title="刷新"
          >
            <ArrowPathIcon class="w-4 h-4" />
          </button>
          <button @click="closeLogDrawer" class="p-1.5 hover:bg-gray-800 rounded transition">
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Terminal Content -->
      <div
        ref="terminalContent"
        class="h-[calc(100%-48px)] overflow-auto p-4 bg-black"
      >
        <!-- Terminal Prompt -->
        <div class="space-y-1 font-mono text-sm">
          <div class="text-gray-500">
            <span class="text-emerald-400">pycron</span>:<span class="text-blue-400">~</span>$ python {{ currentTask?.script_path }}
          </div>

          <div v-if="logs.length === 0" class="text-gray-500 py-4">
            <p>// 暂无执行记录</p>
            <p class="text-emerald-500 mt-2">// 点击上方 "运行" 按钮执行任务</p>
          </div>

          <div v-else>
            <div
              v-for="(log, idx) in logs"
              :key="log.id"
              class="border-b border-gray-900 pb-4 mb-4 last:border-0"
            >
              <!-- Session Header -->
              <div class="flex items-center gap-3 text-xs text-gray-600 mb-2">
                <span class="text-emerald-500">[{{ idx + 1 }}]</span>
                <span>{{ formatTime(log.start_time) }}</span>
                <span v-if="log.end_time" class="text-gray-500">
                  → {{ formatTime(log.end_time) }}
                </span>
                <span
                  class="px-1.5 py-0.5 rounded text-xs"
                  :class="log.exit_code === 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'"
                >
                  exit {{ log.exit_code }}
                </span>
              </div>

              <!-- Output -->
              <pre class="whitespace-pre-wrap text-gray-300 leading-relaxed">{{ log.output || '// 无输出' }}</pre>
            </div>
          </div>

          <!-- Blinking Cursor -->
          <div class="mt-4 text-emerald-400">
            <span class="inline-block w-2 h-4 bg-emerald-400 animate-pulse"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import cronParser from 'cron-parser'
import {
  PlusIcon,
  PlayIcon,
  PencilIcon,
  TrashIcon,
  CommandLineIcon,
  XMarkIcon,
  ArrowPathIcon,
  InboxIcon
} from '@heroicons/vue/24/outline'

const api = axios.create({
  baseURL: 'http://localhost:8000'
})

const tasks = ref([])
const showDrawer = ref(false)
const showLogDrawer = ref(false)
const isEditing = ref(false)
const scriptMode = ref('path')
const currentTask = ref(null)
const logs = ref([])

const form = reactive({
  id: null,
  name: '',
  script_path: './scripts/',
  script_content: '',
  cron_expr: '* * * * *',
  timeout: 300,
  is_active: true
})

const cronPresets = [
  { label: '每分钟', value: '* * * * *' },
  { label: '每小时', value: '0 * * * *' },
  { label: '每天凌晨', value: '0 2 * * *' },
  { label: '每周一', value: '0 9 * * 1' }
]

async function fetchTasks() {
  try {
    const res = await api.get('/tasks')
    tasks.value = res.data
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
  }
}

function statusDotClass(status) {
  const classes = {
    idle: 'bg-gray-500',
    running: 'bg-emerald-500',
    success: 'bg-emerald-400',
    failed: 'bg-red-500',
    timeout: 'bg-yellow-500'
  }
  return classes[status] || classes.idle
}

function statusText(status) {
  const texts = { idle: '闲置', running: '运行中', success: '成功', failed: '失败', timeout: '超时' }
  return texts[status] || status
}

function getNextRun(cronExpr) {
  try {
    const interval = cronParser.parseExpression(cronExpr)
    const next = interval.next().toDate()
    const d = new Date(next)
    return d.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return '-'
  }
}

function cronHumanText(expr) {
  try {
    const parts = expr.split(' ')
    if (parts.length !== 5) return ''
    const [min, hour, day, month, week] = parts

    if (expr === '* * * * *') return '每分钟执行一次'
    if (expr === '0 * * * *') return '每小时整点执行'
    if (day === '*' && month === '*' && week === '*') return `每天 ${hour}:${min.padStart(2, '0')} 执行`
    if (week !== '*' && day === '*') {
      const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      return `每周${weekDays[parseInt(week)]} ${hour}:${min.padStart(2, '0')} 执行`
    }
    return `将在 ${expr} 执行`
  } catch {
    return ''
  }
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

function openCreateDrawer() {
  isEditing.value = false
  resetForm()
  showDrawer.value = true
}

function openEditDrawer(task) {
  isEditing.value = true
  currentTask.value = task
  form.id = task.id
  form.name = task.name
  form.script_path = task.script_path
  form.cron_expr = task.cron_expr || '* * * * *'
  form.timeout = task.timeout || 300
  form.is_active = task.is_active
  scriptMode.value = 'path'
  showDrawer.value = true
}

function closeDrawer() {
  showDrawer.value = false
}

function resetForm() {
  form.id = null
  form.name = ''
  form.script_path = './scripts/'
  form.script_content = ''
  form.cron_expr = '* * * * *'
  form.timeout = 300
  form.is_active = true
}

async function submitForm() {
  try {
    const payload = {
      name: form.name,
      script_path: form.script_path,
      cron_expr: form.cron_expr || null,
      is_active: form.is_active
    }

    if (isEditing.value) {
      await api.put(`/tasks/${form.id}`, payload)
    } else {
      await api.post('/tasks', payload)
    }

    closeDrawer()
    fetchTasks()
  } catch (e) {
    console.error('Failed to submit form:', e)
    alert('操作失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function toggleTask(task) {
  try {
    await api.put(`/tasks/${task.id}`, { is_active: !task.is_active })
    fetchTasks()
  } catch (e) {
    console.error('Failed to toggle task:', e)
  }
}

async function runTask(task) {
  if (!task) task = currentTask.value
  try {
    await api.post(`/tasks/${task.id}/run`)
    setTimeout(() => {
      fetchTasks()
      refreshLogs()
    }, 1000)
  } catch (e) {
    console.error('Failed to run task:', e)
    alert('启动失败: ' + (e.response?.data?.detail || e.message))
  }
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

function openLogDrawer(task) {
  currentTask.value = task
  logs.value = []
  showLogDrawer.value = true
  refreshLogs()
}

function closeLogDrawer() {
  showLogDrawer.value = false
}

async function refreshLogs() {
  if (!currentTask.value) return
  try {
    const res = await api.get(`/tasks/${currentTask.value.id}/logs`)
    logs.value = res.data
  } catch (e) {
    console.error('Failed to fetch logs:', e)
  }
}

onMounted(() => {
  fetchTasks()
  setInterval(fetchTasks, 5000)
})
</script>
