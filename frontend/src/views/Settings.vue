<template>
  <div class="space-y-6">
    <!-- Tabs -->
    <div class="flex gap-1 bg-gray-900 p-1 rounded-lg w-fit">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="px-4 py-2 text-sm rounded-md transition"
        :class="activeTab === tab.id ? 'bg-emerald-500 text-black' : 'text-gray-400 hover:text-white'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Environment Variables Tab -->
    <div v-if="activeTab === 'env'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-semibold">环境变量</h2>
        <button @click="openEnvModal()" class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-black font-medium px-4 py-2 rounded-lg transition">
          <PlusIcon class="w-5 h-5" />
          新增变量
        </button>
      </div>

      <div class="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div v-if="envVars.length === 0" class="text-center text-gray-500 py-12">
          <ShieldCheckIcon class="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无环境变量</p>
        </div>
        <table v-else class="w-full">
          <thead class="bg-gray-800/50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">变量名</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">值</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">描述</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase w-24">保密</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase w-32">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-800">
            <tr v-for="env in envVars" :key="env.id" class="hover:bg-gray-800/30">
              <td class="px-4 py-3">
                <code class="text-sm text-emerald-400 bg-gray-800 px-2 py-1 rounded">{{ env.key }}</code>
              </td>
              <td class="px-4 py-3">
                <span v-if="env.is_secret" class="text-gray-500">••••••••</span>
                <span v-else class="text-gray-300 text-sm font-mono">{{ env.value }}</span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-400">{{ env.description || '-' }}</td>
              <td class="px-4 py-3">
                <span :class="env.is_secret ? 'text-yellow-400' : 'text-gray-500'" class="text-xs">
                  {{ env.is_secret ? '是' : '否' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-end gap-1">
                  <button @click="openEnvModal(env)" class="p-2 text-gray-400 hover:text-yellow-400 hover:bg-yellow-500/10 rounded-lg transition">
                    <PencilIcon class="w-4 h-4" />
                  </button>
                  <button @click="deleteEnv(env)" class="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition">
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Alerts Tab -->
    <div v-if="activeTab === 'alerts'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-semibold">告警配置</h2>
        <button @click="openAlertModal()" class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-black font-medium px-4 py-2 rounded-lg transition">
          <PlusIcon class="w-5 h-5" />
          新增告警
        </button>
      </div>

      <div class="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div v-if="alerts.length === 0" class="text-center text-gray-500 py-12">
          <BellIcon class="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无告警配置</p>
        </div>
        <table v-else class="w-full">
          <thead class="bg-gray-800/50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">名称</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Webhook URL</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">触发事件</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase w-24">状态</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase w-32">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-800">
            <tr v-for="alert in alerts" :key="alert.id" class="hover:bg-gray-800/30">
              <td class="px-4 py-3 font-medium">{{ alert.name }}</td>
              <td class="px-4 py-3">
                <span class="text-xs text-gray-500 font-mono truncate block max-w-xs">{{ alert.webhook_url }}</span>
              </td>
              <td class="px-4 py-3">
                <div class="flex gap-1 flex-wrap">
                  <span v-for="evt in alert.events.split(',')" :key="evt"
                    class="px-2 py-0.5 text-xs rounded"
                    :class="evt.trim() === 'failed' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'">
                    {{ evt.trim() }}
                  </span>
                </div>
              </td>
              <td class="px-4 py-3">
                <button @click="toggleAlert(alert)" class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors" :class="alert.is_active ? 'bg-emerald-500' : 'bg-gray-700'">
                  <span class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform" :class="alert.is_active ? 'translate-x-6' : 'translate-x-1'" />
                </button>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-end gap-1">
                  <button @click="openAlertModal(alert)" class="p-2 text-gray-400 hover:text-yellow-400 hover:bg-yellow-500/10 rounded-lg transition">
                    <PencilIcon class="w-4 h-4" />
                  </button>
                  <button @click="deleteAlert(alert)" class="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition">
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Export/Import Tab -->
    <div v-if="activeTab === 'export'" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Export -->
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <ArrowDownTrayIcon class="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 class="font-semibold">导出配置</h3>
              <p class="text-sm text-gray-500">下载所有任务、环境变量和告警配置</p>
            </div>
          </div>
          <button @click="exportConfig" class="w-full px-4 py-2.5 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition">
            导出 JSON 文件
          </button>
        </div>

        <!-- Import -->
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center">
              <ArrowUpTrayIcon class="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 class="font-semibold">导入配置</h3>
              <p class="text-sm text-gray-500">从 JSON 文件恢复所有配置</p>
            </div>
          </div>
          <label class="block">
            <input type="file" accept=".json" @change="importConfig" class="hidden" ref="importFile" />
            <span class="w-full px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-black font-medium rounded-lg transition cursor-pointer inline-block text-center">
              选择 JSON 文件导入
            </span>
          </label>
        </div>
      </div>
    </div>

    <!-- Env Var Modal -->
    <div v-if="showEnvModal" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-black/60" @click="closeEnvModal"></div>
      <div class="absolute right-0 top-0 h-full w-full max-w-md bg-gray-900 border-l border-gray-800 transform transition-transform" :class="showEnvModal ? 'translate-x-0' : 'translate-x-full'">
        <div class="flex items-center justify-between p-4 border-b border-gray-800">
          <h2 class="text-lg font-semibold">{{ editingEnv ? '编辑变量' : '新增变量' }}</h2>
          <button @click="closeEnvModal" class="p-2 hover:bg-gray-800 rounded-lg">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="p-4 overflow-y-auto h-[calc(100vh-65px)]">
          <form @submit.prevent="saveEnv" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">变量名</label>
              <input v-model="envForm.key" type="text" required class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500 font-mono" placeholder="API_KEY" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">变量值</label>
              <input v-model="envForm.value" type="text" required class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500 font-mono" placeholder="your-secret-value" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">描述</label>
              <input v-model="envForm.description" type="text" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500" placeholder="可选描述信息" />
            </div>
            <div class="flex items-center gap-2">
              <input v-model="envForm.is_secret" type="checkbox" id="is_secret" class="accent-emerald-500" />
              <label for="is_secret" class="text-sm text-gray-400">保密模式（界面上隐藏值）</label>
            </div>
            <div class="flex gap-3 pt-4 border-t border-gray-800">
              <button type="button" @click="closeEnvModal" class="flex-1 px-4 py-2.5 border border-gray-700 rounded-lg hover:bg-gray-800 transition">取消</button>
              <button type="submit" class="flex-1 px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-black font-medium rounded-lg transition">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Alert Modal -->
    <div v-if="showAlertModal" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-black/60" @click="closeAlertModal"></div>
      <div class="absolute right-0 top-0 h-full w-full max-w-md bg-gray-900 border-l border-gray-800 transform transition-transform" :class="showAlertModal ? 'translate-x-0' : 'translate-x-full'">
        <div class="flex items-center justify-between p-4 border-b border-gray-800">
          <h2 class="text-lg font-semibold">{{ editingAlert ? '编辑告警' : '新增告警' }}</h2>
          <button @click="closeAlertModal" class="p-2 hover:bg-gray-800 rounded-lg">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="p-4 overflow-y-auto h-[calc(100vh-65px)]">
          <form @submit.prevent="saveAlert" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">告警名称</label>
              <input v-model="alertForm.name" type="text" required class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500" placeholder="钉钉机器人" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">Webhook URL</label>
              <input v-model="alertForm.webhook_url" type="url" required class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500 font-mono text-sm" placeholder="https://oapi.dingtalk.com/robot/send?access_token=..." />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-400 mb-2">触发事件</label>
              <div class="flex gap-4">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input v-model="alertEvents" type="checkbox" value="failed" class="accent-emerald-500" />
                  <span class="text-sm text-red-400">失败</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input v-model="alertEvents" type="checkbox" value="timeout" class="accent-emerald-500" />
                  <span class="text-sm text-yellow-400">超时</span>
                </label>
              </div>
            </div>
            <div class="flex gap-3 pt-4 border-t border-gray-800">
              <button type="button" @click="closeAlertModal" class="flex-1 px-4 py-2.5 border border-gray-700 rounded-lg hover:bg-gray-800 transition">取消</button>
              <button type="submit" class="flex-1 px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-black font-medium rounded-lg transition">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import {
  PlusIcon, PencilIcon, TrashIcon, XMarkIcon,
  ShieldCheckIcon, BellIcon, ArrowDownTrayIcon, ArrowUpTrayIcon
} from '@heroicons/vue/24/outline'

const api = axios.create({ baseURL: 'http://localhost:8000' })

const tabs = [
  { id: 'env', label: '环境变量' },
  { id: 'alerts', label: '告警配置' },
  { id: 'export', label: '导入导出' }
]
const activeTab = ref('env')

const envVars = ref([])
const alerts = ref([])

const showEnvModal = ref(false)
const showAlertModal = ref(false)
const editingEnv = ref(null)
const editingAlert = ref(null)
const alertEvents = ref(['failed', 'timeout'])

const envForm = reactive({ key: '', value: '', description: '', is_secret: false })
const alertForm = reactive({ name: '', webhook_url: '', events: 'failed,timeout', is_active: true })

const importFile = ref(null)

async function fetchEnvVars() {
  try {
    const res = await api.get('/env-vars')
    envVars.value = res.data
  } catch (e) { console.error(e) }
}

async function fetchAlerts() {
  try {
    const res = await api.get('/alerts')
    alerts.value = res.data
  } catch (e) { console.error(e) }
}

function openEnvModal(env = null) {
  editingEnv.value = env
  if (env) {
    envForm.key = env.key
    envForm.value = env.value
    envForm.description = env.description || ''
    envForm.is_secret = env.is_secret
  } else {
    envForm.key = ''
    envForm.value = ''
    envForm.description = ''
    envForm.is_secret = false
  }
  showEnvModal.value = true
}

function closeEnvModal() {
  showEnvModal.value = false
  editingEnv.value = null
}

async function saveEnv() {
  try {
    if (editingEnv.value) {
      await api.put(`/env-vars/${editingEnv.value.id}`, envForm)
    } else {
      await api.post('/env-vars', envForm)
    }
    closeEnvModal()
    fetchEnvVars()
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function deleteEnv(env) {
  if (!confirm(`确定删除变量 "${env.key}" 吗？`)) return
  try {
    await api.delete(`/env-vars/${env.id}`)
    fetchEnvVars()
  } catch (e) { console.error(e) }
}

function openAlertModal(alert = null) {
  editingAlert.value = alert
  if (alert) {
    alertForm.name = alert.name
    alertForm.webhook_url = alert.webhook_url
    alertForm.is_active = alert.is_active
    alertEvents.value = alert.events.split(',').map(e => e.trim())
  } else {
    alertForm.name = ''
    alertForm.webhook_url = ''
    alertForm.is_active = true
    alertEvents.value = ['failed', 'timeout']
  }
  showAlertModal.value = true
}

function closeAlertModal() {
  showAlertModal.value = false
  editingAlert.value = null
}

async function saveAlert() {
  alertForm.events = alertEvents.value.join(',')
  try {
    if (editingAlert.value) {
      await api.put(`/alerts/${editingAlert.value.id}`, alertForm)
    } else {
      await api.post('/alerts', alertForm)
    }
    closeAlertModal()
    fetchAlerts()
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function deleteAlert(alert) {
  if (!confirm(`确定删除告警 "${alert.name}" 吗？`)) return
  try {
    await api.delete(`/alerts/${alert.id}`)
    fetchAlerts()
  } catch (e) { console.error(e) }
}

async function toggleAlert(alert) {
  try {
    await api.put(`/alerts/${alert.id}`, { is_active: !alert.is_active })
    fetchAlerts()
  } catch (e) { console.error(e) }
}

async function exportConfig() {
  try {
    const res = await api.get('/export')
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `pycron-config-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert('导出失败: ' + e.message)
  }
}

async function importConfig(event) {
  const file = event.target.files[0]
  if (!file) return
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    const res = await api.post('/import', data)
    alert(`导入成功！任务: ${res.data.tasks_imported}, 变量: ${res.data.env_vars_imported}, 告警: ${res.data.alerts_imported}`)
    fetchEnvVars()
    fetchAlerts()
  } catch (e) {
    alert('导入失败: ' + (e.response?.data?.detail || e.message))
  }
  event.target.value = ''
}

onMounted(() => {
  fetchEnvVars()
  fetchAlerts()
})
</script>
