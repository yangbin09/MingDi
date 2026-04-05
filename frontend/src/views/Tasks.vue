<template>
  <div class="space-y-6">
    <!-- Header Actions -->
    <div class="flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="h-1 w-8 bg-gradient-to-r from-indigo-500 to-emerald-500 rounded-full"></div>
        <span class="text-sm text-gray-500">共 <span class="text-gray-300 font-medium">{{ tasks.length }}</span> 个任务</span>
      </div>
      <button
        @click="openCreateDrawer"
        class="flex items-center gap-2 bg-indigo-500 hover:bg-indigo-600 text-white font-medium px-4 py-2 rounded-lg transition-all duration-200 shadow-soft hover:shadow-indigo-glow"
      >
        <PlusIcon class="w-5 h-5" />
        新建任务
      </button>
    </div>

    <!-- Tasks Table -->
    <div class="bg-gray-900/80 backdrop-blur-sm border border-gray-700/50 rounded-xl overflow-hidden">
      <div v-if="tasks.length === 0" class="text-center text-gray-500 py-20">
        <div class="w-20 h-20 mx-auto mb-4 bg-gray-800/50 rounded-full flex items-center justify-center">
          <InboxIcon class="w-10 h-10 opacity-50" />
        </div>
        <p class="text-lg">暂无任务</p>
        <p class="text-sm mt-1 text-gray-600">点击右上角按钮创建第一个任务</p>
      </div>

      <table v-else class="w-full">
        <thead class="bg-gray-800/50">
          <tr>
            <th class="px-4 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-12">
              <span class="relative flex h-3 w-3 justify-center">
                <span v-if="runningCount > 0" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              </span>
            </th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">任务</th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">依赖</th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-36">定时</th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-24">启用</th>
            <th class="px-4 py-3.5 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider w-48">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-700/50">
          <tr
            v-for="task in tasks"
            :key="task.id"
            class="hover:bg-gray-800/30 transition-all duration-200"
            :class="{ 'bg-indigo-500/5': task.status === 'running' }"
          >
            <!-- Status with breathing effect -->
            <td class="px-4 py-4">
              <span class="relative flex h-3 w-3">
                <span
                  v-if="task.status === 'running'"
                  class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
                ></span>
                <span
                  class="relative inline-flex rounded-full h-3 w-3"
                  :class="{
                    'bg-emerald-500 shadow-emerald-glow': task.status === 'running' || task.status === 'success',
                    'bg-rose-500 shadow-rose-glow': task.status === 'failed',
                    'bg-yellow-500': task.status === 'timeout',
                    'bg-gray-600': task.status === 'idle'
                  }"
                ></span>
              </span>
            </td>

            <!-- Task Info -->
            <td class="px-4 py-4">
              <div class="font-medium text-gray-200">{{ task.name }}</div>
              <div class="text-xs text-gray-500 mt-0.5 flex items-center gap-2">
                <span class="font-mono">{{ task.script_path }}</span>
                <span v-if="task.interpreter_path" class="text-xs px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  {{ task.interpreter_path.split('/').pop().split('\\').pop() }}
                </span>
              </div>
            </td>

            <!-- Dependency -->
            <td class="px-4 py-4">
              <span v-if="task.depends_on" class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                <ArrowRightIcon class="w-3 h-3" />
                {{ getTaskName(task.depends_on) }}
              </span>
              <span v-else class="text-gray-600 text-sm">-</span>
            </td>

            <!-- Cron -->
            <td class="px-4 py-4">
              <code class="text-xs bg-gray-800 px-2.5 py-1.5 rounded-lg text-indigo-400 font-mono border border-gray-700/50">{{ task.cron_expr || '-' }}</code>
            </td>

            <!-- Toggle -->
            <td class="px-4 py-4">
              <button
                @click="toggleTask(task)"
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-300"
                :class="task.is_active ? 'bg-emerald-500/20 border border-emerald-500/50' : 'bg-gray-700/50 border border-gray-600'"
              >
                <span
                  class="inline-block h-4 w-4 transform rounded-full transition-all duration-300 shadow-soft"
                  :class="task.is_active ? 'translate-x-6 bg-emerald-400' : 'translate-x-1 bg-gray-400'"
                />
              </button>
            </td>

            <!-- Actions -->
            <td class="px-4 py-4">
              <div class="flex items-center justify-end gap-1">
                <button
                  @click="runTask(task)"
                  :disabled="task.status === 'running'"
                  class="p-2 text-gray-500 hover:text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition-all duration-200 disabled:opacity-40"
                  title="立即运行"
                >
                  <PlayIcon class="w-4 h-4" />
                </button>
                <button
                  @click="openLogDrawer(task)"
                  class="p-2 text-gray-500 hover:text-indigo-400 hover:bg-indigo-500/10 rounded-lg transition-all duration-200"
                  title="查看日志"
                >
                  <CommandLineIcon class="w-4 h-4" />
                </button>
                <button
                  @click="openEditDrawer(task)"
                  class="p-2 text-gray-500 hover:text-yellow-400 hover:bg-yellow-500/10 rounded-lg transition-all duration-200"
                  title="编辑"
                >
                  <PencilIcon class="w-4 h-4" />
                </button>
                <button
                  @click="deleteTask(task)"
                  class="p-2 text-gray-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-all duration-200"
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
  <div v-if="showDrawer" class="fixed inset-0 z-50 overflow-hidden">
    <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="closeDrawer"></div>
    <div
      class="absolute right-0 top-0 h-full w-full max-w-xl bg-gray-900 border-l border-gray-700/50 transform transition-transform duration-300 ease-out"
      :class="showDrawer ? 'translate-x-0' : 'translate-x-full'"
    >
      <div class="flex items-center justify-between p-5 border-b border-gray-700/50">
        <div class="flex items-center gap-3">
          <div class="h-1 w-6 bg-gradient-to-r from-indigo-500 to-emerald-500 rounded-full"></div>
          <h2 class="text-lg font-semibold text-gray-100">{{ isEditing ? '编辑任务' : '新建任务' }}</h2>
        </div>
        <button @click="closeDrawer" class="p-2 hover:bg-gray-800 rounded-lg transition-colors">
          <XMarkIcon class="w-5 h-5 text-gray-400" />
        </button>
      </div>

      <div class="p-5 overflow-y-auto h-[calc(100vh-73px)]">
        <form @submit.prevent="submitForm" class="space-y-6">
          <!-- Task Name -->
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">任务名称</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full bg-gray-800/80 border border-gray-700/50 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-all"
              placeholder="输入任务名称"
            />
          </div>

          <!-- Script Mode -->
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">脚本来源</label>
            <div class="flex gap-4 mb-3">
              <label class="flex items-center gap-2 cursor-pointer group">
                <input type="radio" v-model="scriptMode" value="path" class="accent-indigo-500" />
                <span class="text-sm text-gray-400 group-hover:text-gray-200 transition-colors">服务器路径</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer group">
                <input type="radio" v-model="scriptMode" value="editor" class="accent-indigo-500" />
                <span class="text-sm text-gray-400 group-hover:text-gray-200 transition-colors">在线编辑</span>
              </label>
            </div>

            <div v-if="scriptMode === 'path'">
              <input
                v-model="form.script_path"
                type="text"
                required
                class="w-full bg-gray-800/80 border border-gray-700/50 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-all font-mono text-sm"
                placeholder="./scripts/my_script.py"
              />
            </div>
            <div v-else class="border border-gray-700/50 rounded-lg overflow-hidden">
              <div class="bg-gray-800/80 px-3 py-2 text-xs text-gray-400 border-b border-gray-700/50 flex items-center justify-between">
                <span>Python Editor</span>
                <span class="text-indigo-400">Python 3</span>
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
                height="200px"
              />
            </div>
          </div>

          <!-- Interpreter Path (venv) -->
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">
              Python 解释器
              <span class="text-xs text-gray-500">(可选)</span>
            </label>
            <div class="relative">
              <input
                v-model="form.interpreter_path"
                type="text"
                class="w-full bg-gray-800/80 border border-gray-700/50 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-all font-mono text-sm"
                placeholder="/usr/bin/python3"
              />
              <span v-if="form.interpreter_path" class="absolute right-3 top-1/2 -translate-y-1/2 text-xs px-2 py-1 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">venv</span>
            </div>
            <p class="text-xs text-gray-500 mt-1">指定任务执行的 Python 解释器路径</p>
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
                class="px-3 py-2 text-xs rounded-lg border transition-all duration-200"
                :class="form.cron_expr === preset.value
                  ? 'border-indigo-500 bg-indigo-500/10 text-indigo-400'
                  : 'border-gray-700/50 text-gray-400 hover:border-gray-600'"
              >
                {{ preset.label }}
              </button>
            </div>
            <input
              v-model="form.cron_expr"
              type="text"
              class="w-full bg-gray-800/80 border border-gray-700/50 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-all font-mono"
              placeholder="* * * * *"
            />
            <p class="text-xs text-gray-500 mt-2" v-if="form.cron_expr">{{ cronHumanText(form.cron_expr) }}</p>
          </div>

          <!-- Task Dependency -->
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">
              前置任务依赖
              <span class="text-xs text-gray-500">(可选)</span>
            </label>
            <select
              v-model="form.depends_on"
              class="w-full bg-gray-800/80 border border-gray-700/50 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-all"
            >
              <option :value="null">无依赖</option>
              <option v-for="t in availableDependencies" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">前置任务成功执行后，自动触发此任务</p>
          </div>

          <!-- Timeout -->
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">超时时间 (秒)</label>
            <input
              v-model.number="form.timeout"
              type="number"
              min="0"
              class="w-full bg-gray-800/80 border border-gray-700/50 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-all"
              placeholder="300"
            />
          </div>

          <!-- Submit -->
          <div class="flex gap-3 pt-4 border-t border-gray-700/50">
            <button
              type="button"
              @click="closeDrawer"
              class="flex-1 px-4 py-2.5 border border-gray-700/50 rounded-lg hover:bg-gray-800 transition-all"
            >
              取消
            </button>
            <button
              type="submit"
              class="flex-1 px-4 py-2.5 bg-indigo-500 hover:bg-indigo-600 text-white font-medium rounded-lg transition-all shadow-soft"
            >
              {{ isEditing ? '保存' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Log Drawer -->
  <div v-if="showLogDrawer" class="fixed inset-0 z-50 overflow-hidden">
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="closeLogDrawer"></div>
    <div
      class="absolute right-0 top-0 h-full w-full max-w-3xl bg-gray-950 border-l border-gray-700/50 transform transition-transform duration-300 ease-out"
      :class="showLogDrawer ? 'translate-x-0' : 'translate-x-full'"
    >
      <!-- Terminal Header -->
      <div class="flex items-center justify-between px-5 py-3 bg-gray-900 border-b border-gray-700/50">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full bg-rose-500"></div>
            <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div class="w-3 h-3 rounded-full bg-emerald-500"></div>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-200">{{ currentTask?.name }}</span>
            <span class="text-xs text-gray-500 ml-2">bash</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <!-- Search Filter -->
          <div class="flex items-center gap-2 mr-2">
            <div class="relative">
              <input
                v-model="logSearch"
                type="text"
                placeholder="搜索..."
                class="bg-gray-800/80 text-xs px-3 py-1.5 pr-8 rounded-lg border border-gray-700/50 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 w-36"
              />
              <MagnifyingGlassIcon class="w-3 h-3 absolute right-2 top-1/2 -translate-y-1/2 text-gray-500" />
            </div>
            <input
              v-model="logDateFilter"
              type="date"
              class="bg-gray-800/80 text-xs px-2 py-1.5 rounded-lg border border-gray-700/50 text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
          <button @click="downloadLog" class="p-1.5 hover:bg-gray-800 rounded-lg transition-colors" title="下载日志">
            <ArrowDownTrayIcon class="w-4 h-4 text-gray-400" />
          </button>
          <button @click="runTask(currentTask)" class="px-3 py-1.5 text-xs bg-emerald-500/20 text-emerald-400 rounded-lg hover:bg-emerald-500/30 transition-colors font-medium">
            ▶ 运行
          </button>
          <button @click="refreshLogs" class="p-1.5 hover:bg-gray-800 rounded-lg transition-colors" title="刷新">
            <ArrowPathIcon class="w-4 h-4 text-gray-400" />
          </button>
          <button @click="closeLogDrawer" class="p-1.5 hover:bg-gray-800 rounded-lg transition-colors">
            <XMarkIcon class="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      <!-- Terminal Content -->
      <div ref="terminalContent" class="h-[calc(100%-48px)] overflow-auto p-5 bg-gray-950">
        <div class="space-y-1 font-mono text-sm">
          <div class="text-gray-500">
            <span class="text-indigo-400">pycron</span>:<span class="text-emerald-400">~</span>$ python {{ currentTask?.script_path }}
          </div>

          <div v-if="filteredLogs.length === 0" class="text-gray-500 py-6">
            <p class="text-sm">// 暂无执行记录</p>
            <p class="text-emerald-500/70 mt-2 text-sm">// 点击 "运行" 按钮执行任务</p>
          </div>

          <div v-else>
            <div v-for="(log, idx) in filteredLogs" :key="log.id" class="border-b border-gray-800 pb-4 mb-4 last:border-0 last:pb-0">
              <div class="flex items-center gap-3 text-xs text-gray-500 mb-2">
                <span class="text-indigo-400">[{{ idx + 1 }}]</span>
                <span class="text-gray-400">{{ formatTime(log.start_time) }}</span>
                <span v-if="log.end_time" class="text-gray-600">→ {{ formatTime(log.end_time) }}</span>
                <span
                  class="px-2 py-0.5 rounded text-xs font-medium"
                  :class="log.exit_code === 0
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'"
                >
                  exit {{ log.exit_code }}
                </span>
              </div>
              <pre class="whitespace-pre-wrap text-gray-300 leading-relaxed text-sm" v-html="highlightKeyword(log.output || '// 无输出')"></pre>
            </div>
          </div>

          <div class="mt-4 text-emerald-400">
            <span class="inline-block w-2 h-4 bg-emerald-400 animate-pulse"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import cronParser from 'cron-parser'
import {
  PlusIcon, PlayIcon, PencilIcon, TrashIcon, CommandLineIcon,
  XMarkIcon, ArrowPathIcon, InboxIcon, ArrowDownTrayIcon,
  ArrowRightIcon, MagnifyingGlassIcon
} from '@heroicons/vue/24/outline'

const api = axios.create({ baseURL: 'http://localhost:8000' })

const tasks = ref([])
const showDrawer = ref(false)
const showLogDrawer = ref(false)
const isEditing = ref(false)
const scriptMode = ref('path')
const currentTask = ref(null)
const logs = ref([])
const logSearch = ref('')
const logDateFilter = ref('')

const form = reactive({
  id: null, name: '', script_path: './scripts/', script_content: '',
  cron_expr: '* * * * *', timeout: 300, is_active: true,
  interpreter_path: null, depends_on: null
})

const runningCount = computed(() => tasks.value.filter(t => t.status === 'running').length)
const availableDependencies = computed(() => tasks.value.filter(t => t.id !== form.id))

const filteredLogs = computed(() => {
  let result = logs.value
  if (logSearch.value) {
    const kw = logSearch.value.toLowerCase()
    result = result.filter(l => (l.output || '').toLowerCase().includes(kw))
  }
  if (logDateFilter.value) {
    const date = new Date(logDateFilter.value).toDateString()
    result = result.filter(l => new Date(l.start_time).toDateString() === date)
  }
  return result
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
  } catch (e) { console.error(e) }
}

function getTaskName(taskId) {
  const t = tasks.value.find(t => t.id === taskId)
  return t ? t.name : 'Unknown'
}

function getNextRun(cronExpr) {
  try {
    const interval = cronParser.parseExpression(cronExpr)
    const next = interval.next().toDate()
    return new Date(next).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch { return '-' }
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
  } catch { return '' }
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

function highlightKeyword(text) {
  if (!logSearch.value) return text
  const kw = logSearch.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${kw})`, 'gi'), '<mark class="bg-yellow-500/30 text-yellow-200 px-0.5 rounded">$1</mark>')
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
  form.interpreter_path = task.interpreter_path
  form.depends_on = task.depends_on
  scriptMode.value = 'path'
  showDrawer.value = true
}

function closeDrawer() { showDrawer.value = false }

function resetForm() {
  form.id = null
  form.name = ''
  form.script_path = './scripts/'
  form.script_content = ''
  form.cron_expr = '* * * * *'
  form.timeout = 300
  form.is_active = true
  form.interpreter_path = null
  form.depends_on = null
}

async function submitForm() {
  try {
    const payload = {
      name: form.name,
      script_path: form.script_path,
      cron_expr: form.cron_expr || null,
      is_active: form.is_active,
      interpreter_path: form.interpreter_path || null,
      depends_on: form.depends_on,
      timeout: form.timeout || 300
    }
    if (isEditing.value) { await api.put(`/tasks/${form.id}`, payload) }
    else { await api.post('/tasks', payload) }
    closeDrawer()
    fetchTasks()
  } catch (e) { alert('操作失败: ' + (e.response?.data?.detail || e.message)) }
}

async function toggleTask(task) {
  try { await api.put(`/tasks/${task.id}`, { is_active: !task.is_active }); fetchTasks() }
  catch (e) { console.error(e) }
}

async function runTask(task) {
  if (!task) task = currentTask.value
  try {
    await api.post(`/tasks/${task.id}/run`)
    setTimeout(() => { fetchTasks(); refreshLogs() }, 1000)
  } catch (e) { alert('启动失败: ' + (e.response?.data?.detail || e.message)) }
}

async function deleteTask(task) {
  if (!confirm(`确定删除任务 "${task.name}" 吗？`)) return
  try { await api.delete(`/tasks/${task.id}`); fetchTasks() }
  catch (e) { console.error(e) }
}

function openLogDrawer(task) {
  currentTask.value = task
  logs.value = []
  logSearch.value = ''
  logDateFilter.value = ''
  showLogDrawer.value = true
  refreshLogs()
}

function closeLogDrawer() { showLogDrawer.value = false }

async function refreshLogs() {
  if (!currentTask.value) return
  try {
    const res = await api.get(`/tasks/${currentTask.value.id}/logs`)
    logs.value = res.data
  } catch (e) { console.error(e) }
}

async function downloadLog() {
  if (!logs.value.length) return
  const content = logs.value.map((l, i) =>
    `=== Session ${i + 1} ===\nTime: ${formatTime(l.start_time)}\nExit: ${l.exit_code}\n\n${l.output || '// No output'}\n`
  ).join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `task_${currentTask.value.id}_logs_${new Date().toISOString().slice(0,10)}.log`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => { fetchTasks(); setInterval(fetchTasks, 5000) })
</script>
