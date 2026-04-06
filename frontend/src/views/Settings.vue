<template>
  <div class="settings-page space-y-6">
    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="settings-tabs">
      <el-tab-pane label="环境变量" name="env">
        <template #label>
          <span class="tab-label">
            <el-icon><Key /></el-icon>
            环境变量
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="告警配置" name="alerts">
        <template #label>
          <span class="tab-label">
            <el-icon><Bell /></el-icon>
            告警配置
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="AI 设置" name="ai">
        <template #label>
          <span class="tab-label">
            <el-icon><MagicStick /></el-icon>
            AI 设置
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="导入导出" name="export">
        <template #label>
          <span class="tab-label">
            <el-icon><Upload /></el-icon>
            导入导出
          </span>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- Environment Variables Tab -->
    <div v-if="activeTab === 'env'">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <div class="flex items-center gap-3">
              <div class="header-indicator"></div>
              <span class="font-semibold">环境变量</span>
            </div>
            <el-button type="primary" @click="openEnvModal()">
              <el-icon><Plus /></el-icon>
              新增变量
            </el-button>
          </div>
        </template>

        <el-table :data="envVars" :stripe="!isDarkTheme">
          <el-table-column label="变量名" width="200">
            <template #default="{ row }">
              <code class="px-2 py-1 rounded" style="background-color: var(--color-primary-subtle); color: var(--color-primary);">{{ row.key }}</code>
            </template>
          </el-table-column>
          <el-table-column label="值" min-width="200">
            <template #default="{ row }">
              <span v-if="row.is_secret" style="color: var(--text-disabled);">••••••••</span>
              <span v-else class="font-mono">{{ row.value }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="150" />
          <el-table-column label="保密" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_secret ? 'warning' : 'info'" size="small">
                {{ row.is_secret ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="right">
            <template #default="{ row }">
              <el-button-group>
                <el-button size="small" @click="openEnvModal(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" type="danger" plain @click="handleDeleteEnv(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="envVars.length === 0" description="暂无环境变量" />
      </el-card>
    </div>

    <!-- Alerts Tab -->
    <div v-if="activeTab === 'alerts'">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <div class="flex items-center gap-3">
              <div class="header-indicator-danger"></div>
              <span class="font-semibold">告警配置</span>
            </div>
            <el-button type="primary" @click="openAlertModal()">
              <el-icon><Plus /></el-icon>
              新增告警
            </el-button>
          </div>
        </template>

        <el-table :data="alerts" :stripe="!isDarkTheme">
          <el-table-column prop="name" label="名称" width="150" />
          <el-table-column label="Webhook URL" min-width="250">
            <template #default="{ row }">
              <span class="text-xs font-mono truncate block max-w-xs">{{ row.webhook_url }}</span>
            </template>
          </el-table-column>
          <el-table-column label="触发事件" width="150">
            <template #default="{ row }">
              <el-tag v-for="evt in row.events.split(',')" :key="evt" :type="evt.trim() === 'failed' ? 'danger' : 'warning'" size="small" class="mr-1">
                {{ evt.trim() }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-switch
                :model-value="row.is_active"
                @change="handleToggleAlert(row)"
                active-color="var(--color-success)"
                inactive-color="var(--bg-tertiary)"
              />
            </template>
          </el-table-column>
          <el-table-column label="AI" width="80" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.ai_humanize" type="info" size="small">
                <el-icon><MagicStick /></el-icon>
                AI
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="right">
            <template #default="{ row }">
              <el-button-group>
                <el-button size="small" @click="openAlertModal(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" type="danger" plain @click="handleDeleteAlert(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="alerts.length === 0" description="暂无告警配置" />
      </el-card>
    </div>

    <!-- AI Settings Tab -->
    <div v-if="activeTab === 'ai'">
      <el-card shadow="never" class="mb-4">
        <template #header>
          <div class="flex items-center gap-4">
            <el-avatar :style="{ backgroundColor: 'rgba(168, 85, 247, 0.15)' }">
              <el-icon><MagicStick /></el-icon>
            </el-avatar>
            <div class="flex-1">
              <span class="font-semibold">Minimax API 配置</span>
              <p class="text-xs mt-1" style="color: var(--text-muted);">配置大模型 API 凭证以启用 AI 功能</p>
            </div>
            <el-tag :type="aiSettings.ai_enabled ? 'success' : 'info'">
              {{ aiSettings.ai_enabled ? '已启用' : '未启用' }}
            </el-tag>
          </div>
        </template>

        <el-form label-position="top" class="ai-settings-form">
          <el-form-item label="API Key">
            <el-input
              v-model="aiSettings.minimax_api_key"
              type="password"
              placeholder="输入您的 Minimax API Key"
              show-password
            />
          </el-form-item>
          <el-form-item label="Group ID">
            <el-input
              v-model="aiSettings.minimax_group_id"
              placeholder="输入您的 Minimax Group ID"
            />
          </el-form-item>
          <el-form-item>
            <div class="flex gap-3">
              <el-button
                @click="handleTestAI"
                :loading="aiTesting"
                :disabled="!aiSettings.minimax_api_key || !aiSettings.minimax_group_id"
              >
                {{ aiTesting ? '测试中...' : '测试连接' }}
              </el-button>
              <el-button type="primary" @click="handleSaveAI">
                {{ aiSettingsSaved ? '已保存' : '保存配置' }}
              </el-button>
            </div>
          </el-form-item>
          <el-alert
            v-if="aiTestResult"
            :title="aiTestResult.message"
            :type="aiTestResult.success ? 'success' : 'error'"
            :closable="true"
            @close="aiTestResult = null"
          />
        </el-form>
      </el-card>

      <el-card shadow="never">
        <template #header>
          <span class="font-semibold">支持的 AI 功能</span>
        </template>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" v-for="feature in aiFeatures" :key="feature.name">
            <div class="feature-card">
              <div class="flex items-center gap-2 mb-1">
                <el-icon :style="{ color: feature.color }"><MagicStick /></el-icon>
                <span class="font-medium">{{ feature.name }}</span>
              </div>
              <p class="text-xs" style="color: var(--text-muted);">{{ feature.desc }}</p>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- Export/Import Tab -->
    <div v-if="activeTab === 'export'">
      <el-row :gutter="24">
        <el-col :xs="24" :md="12">
          <el-card shadow="never" class="export-card">
            <div class="export-header">
              <el-avatar :style="{ backgroundColor: 'var(--color-primary-subtle)' }">
                <el-icon><Download /></el-icon>
              </el-avatar>
              <div>
                <h3 class="font-semibold">导出配置</h3>
                <p class="text-sm" style="color: var(--text-muted);">下载所有任务、环境变量和告警配置</p>
              </div>
            </div>
            <el-button type="primary" @click="handleExport" class="w-full mt-4">
              <el-icon><Download /></el-icon>
              导出 JSON 文件
            </el-button>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-card shadow="never" class="export-card">
            <div class="export-header">
              <el-avatar :style="{ backgroundColor: 'var(--color-success-subtle)' }">
                <el-icon><Upload /></el-icon>
              </el-avatar>
              <div>
                <h3 class="font-semibold">导入配置</h3>
                <p class="text-sm" style="color: var(--text-muted);">从 JSON 文件恢复所有配置</p>
              </div>
            </div>
            <input type="file" accept=".json" @change="handleImport" ref="importFileRef" class="hidden" />
            <el-button type="success" @click="$refs.importFileRef.click()" class="w-full mt-4">
              <el-icon><Upload /></el-icon>
              选择 JSON 文件导入
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Env Var Dialog -->
    <el-dialog v-model="showEnvModal" :title="editingEnv ? '编辑变量' : '新增变量'" width="500px">
      <el-form label-position="top">
        <el-form-item label="变量名" required>
          <el-input v-model="envForm.key" placeholder="API_KEY" />
        </el-form-item>
        <el-form-item label="变量值" required>
          <el-input v-model="envForm.value" placeholder="your-secret-value" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="envForm.description" placeholder="可选描述信息" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="envForm.is_secret">保密模式（界面上隐藏值）</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeEnvModal">取消</el-button>
        <el-button type="primary" @click="handleSaveEnv">保存</el-button>
      </template>
    </el-dialog>

    <!-- Alert Dialog -->
    <el-dialog v-model="showAlertModal" :title="editingAlert ? '编辑告警' : '新增告警'" width="500px">
      <el-form label-position="top">
        <el-form-item label="告警名称" required>
          <el-input v-model="alertForm.name" placeholder="钉钉机器人" />
        </el-form-item>
        <el-form-item label="Webhook URL" required>
          <el-input v-model="alertForm.webhook_url" placeholder="https://oapi.dingtalk.com/robot/send?access_token=..." />
        </el-form-item>
        <el-form-item label="触发事件">
          <el-checkbox-group v-model="alertEvents">
            <el-checkbox label="failed">
              <el-tag type="danger" size="small">失败</el-tag>
            </el-checkbox>
            <el-checkbox label="timeout">
              <el-tag type="warning" size="small">超时</el-tag>
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item>
          <div class="ai-humanize-wrapper">
            <div>
              <div class="flex items-center gap-2">
                <el-icon><MagicStick /></el-icon>
                <span class="font-medium">AI 拟人化告警</span>
              </div>
              <p class="text-xs mt-1" style="color: var(--text-disabled);">将冷冰冰的错误信息转化为友好的提示</p>
            </div>
            <el-switch v-model="alertForm.ai_humanize" />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeAlertModal">取消</el-button>
        <el-button type="primary" @click="handleSaveAlert">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import {
  Key, Bell, MagicStick, Upload, Plus, Edit, Delete, Download
} from '@element-plus/icons-vue'

const api = axios.create({ baseURL: 'http://localhost:8000/api' })

// 判断是否为暗色主题
const isDarkTheme = computed(() => {
  return document.documentElement.classList.contains('dark') ||
    ['darcula', 'xuanmo', 'anying', 'gruvbox'].includes(
      document.documentElement.getAttribute('data-theme') || ''
    )
})

const activeTab = ref('env')
const importFileRef = ref(null)

const envVars = ref([])
const alerts = ref([])

const showEnvModal = ref(false)
const showAlertModal = ref(false)
const editingEnv = ref(null)
const editingAlert = ref(null)
const alertEvents = ref(['failed', 'timeout'])

const envForm = reactive({ key: '', value: '', description: '', is_secret: false })
const alertForm = reactive({ name: '', webhook_url: '', events: 'failed,timeout', is_active: true, ai_humanize: false })

const aiSettings = reactive({
  minimax_api_key: '',
  minimax_group_id: '',
  ai_enabled: false
})
const aiSettingsSaved = ref(false)
const aiTesting = ref(false)
const aiTestResult = ref(null)

const aiFeatures = [
  { name: 'Text-to-Script', desc: '自然语言生成 Python 脚本', color: 'var(--color-primary)' },
  { name: 'AI 代码审查', desc: '代码性能与安全检查', color: 'var(--color-purple)' },
  { name: '错误诊断', desc: '智能错误分析与修复建议', color: 'var(--color-warning)' },
  { name: 'NLP to Cron', desc: '自然语言转 Cron 表达式', color: 'var(--color-success)' },
  { name: '日志摘要', desc: 'AI 提炼日志关键信息', color: 'var(--color-cyan)' },
  { name: '拟人化告警', desc: '友好的告警消息推送', color: 'var(--color-blue)' }
]

async function fetchEnvVars() {
  try {
    const res = await api.get('/env-vars')
    envVars.value = res.data
  } catch (e) {
    console.error(e)
  }
}

async function fetchAlerts() {
  try {
    const res = await api.get('/alerts')
    alerts.value = res.data
  } catch (e) {
    console.error(e)
  }
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

async function handleSaveEnv() {
  try {
    if (editingEnv.value) {
      await api.put(`/env-vars/${editingEnv.value.id}`, envForm)
    } else {
      await api.post('/env-vars', envForm)
    }
    closeEnvModal()
    fetchEnvVars()
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function handleDeleteEnv(env) {
  try {
    await ElMessageBox.confirm(`确定删除变量 "${env.key}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/env-vars/${env.id}`)
    fetchEnvVars()
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

function openAlertModal(alert = null) {
  editingAlert.value = alert
  if (alert) {
    alertForm.name = alert.name
    alertForm.webhook_url = alert.webhook_url
    alertForm.is_active = alert.is_active
    alertForm.ai_humanize = alert.ai_humanize || false
    alertEvents.value = alert.events.split(',').map(e => e.trim())
  } else {
    alertForm.name = ''
    alertForm.webhook_url = ''
    alertForm.is_active = true
    alertForm.ai_humanize = false
    alertEvents.value = ['failed', 'timeout']
  }
  showAlertModal.value = true
}

function closeAlertModal() {
  showAlertModal.value = false
  editingAlert.value = null
}

async function handleSaveAlert() {
  alertForm.events = alertEvents.value.join(',')
  try {
    if (editingAlert.value) {
      await api.put(`/alerts/${editingAlert.value.id}`, alertForm)
    } else {
      await api.post('/alerts', alertForm)
    }
    closeAlertModal()
    fetchAlerts()
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function handleDeleteAlert(alert) {
  try {
    await ElMessageBox.confirm(`确定删除告警 "${alert.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/alerts/${alert.id}`)
    fetchAlerts()
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

async function handleToggleAlert(alert) {
  try {
    await api.put(`/alerts/${alert.id}`, { is_active: !alert.is_active })
    fetchAlerts()
    ElMessage.success(alert.is_active ? '告警已禁用' : '告警已启用')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function handleExport() {
  try {
    const res = await api.get('/export')
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `pycron-config-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败: ' + e.message)
  }
}

async function handleImport(event) {
  const file = event.target.files[0]
  if (!file) return
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    const res = await api.post('/import', data)
    ElMessage.success(`导入成功！任务: ${res.data.tasks_imported}, 变量: ${res.data.env_vars_imported}, 告警: ${res.data.alerts_imported}`)
    fetchEnvVars()
    fetchAlerts()
  } catch (e) {
    ElMessage.error('导入失败: ' + (e.response?.data?.detail || e.message))
  }
  event.target.value = ''
}

async function fetchAISettings() {
  try {
    const res = await api.get('/system/settings')
    aiSettings.minimax_api_key = res.data.minimax_api_key || ''
    aiSettings.minimax_group_id = res.data.minimax_group_id || ''
    aiSettings.ai_enabled = res.data.ai_enabled || false
  } catch (e) {
    console.error(e)
  }
}

async function handleSaveAI() {
  try {
    await api.put('/system/settings', {
      minimax_api_key: aiSettings.minimax_api_key,
      minimax_group_id: aiSettings.minimax_group_id
    })
    aiSettingsSaved.value = true
    aiSettings.ai_enabled = !!(aiSettings.minimax_api_key && aiSettings.minimax_group_id)
    setTimeout(() => { aiSettingsSaved.value = false }, 2000)
    ElMessage.success('AI 配置已保存')
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function handleTestAI() {
  aiTesting.value = true
  aiTestResult.value = null
  try {
    await api.put('/system/settings', {
      minimax_api_key: aiSettings.minimax_api_key,
      minimax_group_id: aiSettings.minimax_group_id
    })
    const res = await api.post('/system/settings/test-ai')
    aiTestResult.value = res.data
    aiSettings.ai_enabled = res.data.success
    if (res.data.success) {
      ElMessage.success('AI 连接测试成功')
    }
  } catch (e) {
    aiTestResult.value = { success: false, message: '测试失败: ' + (e.response?.data?.detail || e.message) }
  } finally {
    aiTesting.value = false
  }
}

onMounted(() => {
  fetchEnvVars()
  fetchAlerts()
  fetchAISettings()
})
</script>

<style scoped>
.settings-tabs :deep(.el-tabs__header) {
  margin-bottom: 1rem;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-indicator {
  width: 24px;
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--color-success), var(--color-primary));
}

.header-indicator-danger {
  width: 24px;
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--color-danger), var(--color-warning));
}

.ai-settings-form {
  max-width: 500px;
}

.ai-humanize-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: var(--bg-tertiary);
  border-radius: 8px;
  width: 100%;
}

.export-card,
.import-card {
  height: 100%;
}

.export-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-card {
  margin-bottom: 16px;
}
</style>
