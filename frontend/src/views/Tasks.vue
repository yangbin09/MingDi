<template>
  <div class="tasks-page space-y-6">
    <!-- Page Header -->
    <div class="flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="h-1 w-8 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-primary), var(--color-success))' }"></div>
        <span class="text-sm" style="color: var(--text-muted);">共 <span style="color: var(--text-main); font-weight: 500;">{{ tasks.length }}</span> 个任务</span>
      </div>
      <el-button type="primary" @click="openCreateDrawer">
        <el-icon><Plus /></el-icon>
        新建任务
      </el-button>
    </div>

    <!-- Tasks Table -->
    <el-card class="tasks-card" shadow="never">
      <el-empty v-if="tasks.length === 0" description="暂无任务，点击右上角按钮创建第一个任务" />

      <el-table
        v-else
        :data="tasks"
        stripe
        style="width: 100%"
        :header-cell-style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }"
        :row-style="{ borderBottom: '1px solid var(--border-subtle)' }"
      >
        <el-table-column label="状态" width="60" align="center">
          <template #default="{ row }">
            <span class="relative flex h-3 w-3 justify-center">
              <span v-if="row.status === 'running'" class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :style="{ backgroundColor: 'var(--color-primary)' }"></span>
              <span
                class="relative inline-flex rounded-full h-3 w-3"
                :style="{
                  backgroundColor:
                    row.status === 'running' || row.status === 'success' ? 'var(--color-primary)' :
                    row.status === 'failed' ? 'var(--color-danger)' :
                    row.status === 'timeout' ? 'var(--color-warning)' :
                    'var(--text-muted)'
                }"
              ></span>
            </span>
          </template>
        </el-table-column>

        <el-table-column label="任务" min-width="280">
          <template #default="{ row }">
            <div class="font-medium" style="color: var(--text-main);">{{ row.name }}</div>
            <div class="text-xs mt-0.5 flex items-center gap-2" style="color: var(--text-muted);">
              <code class="font-mono">{{ row.script_path }}</code>
              <el-tag v-if="row.interpreter_path" size="small" type="info">{{ row.interpreter_path.split('/').pop().split('\\').pop() }}</el-tag>
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
              class="text-xs px-2.5 py-1.5 rounded-lg font-mono"
              :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--color-primary)', border: '1px solid var(--border-subtle)' }"
            >{{ row.cron_expr || '-' }}</code>
          </template>
        </el-table-column>

        <el-table-column label="启用" width="80" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active"
              @change="toggleTask(row)"
              active-color="var(--color-success)"
              inactive-color="var(--bg-tertiary)"
            />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="right">
          <template #default="{ row }">
            <el-button-group>
              <el-tooltip content="立即运行" placement="top">
                <el-button :icon="VideoPlay" @click="runTask(row)" :disabled="row.status === 'running'" size="small" type="success" plain />
              </el-tooltip>
              <el-tooltip content="查看日志" placement="top">
                <el-button :icon="Document" @click="goToLogs(row)" size="small" type="primary" plain />
              </el-tooltip>
              <el-tooltip content="编辑" placement="top">
                <el-button :icon="Edit" @click="openEditDrawer(row)" size="small" type="warning" plain />
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <el-button :icon="Delete" @click="deleteTask(row)" size="small" type="danger" plain />
              </el-tooltip>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Task Drawer -->
    <el-drawer
      v-model="showDrawer"
      :title="isEditing ? '编辑任务' : '新建任务'"
      size="500px"
      :before-close="closeDrawer"
      class="task-drawer"
    >
      <el-form
        ref="taskFormRef"
        :model="form"
        :rules="formRules"
        label-position="top"
        class="task-form"
      >
        <!-- AI: Text-to-Script Generation -->
        <el-alert
          v-if="!isEditing"
          title="AI 智能生成脚本"
          type="info"
          :closable="false"
          show-icon
          class="mb-4"
        >
          <template #default>
            <div class="flex gap-2 mt-2">
              <el-input
                v-model="aiDescription"
                placeholder="用自然语言描述你想要实现的脚本功能..."
              />
              <el-button
                type="primary"
                @click="generateScriptWithAI"
                :loading="aiGenerating"
                :disabled="!aiDescription.trim()"
              >
                <el-icon v-if="!aiGenerating"><MagicStick /></el-icon>
                {{ aiGenerating ? '生成中...' : '生成' }}
              </el-button>
            </div>
          </template>
        </el-alert>

        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="输入任务名称" />
        </el-form-item>

        <el-form-item label="脚本来源">
          <el-radio-group v-model="scriptMode" class="mb-2">
            <el-radio label="path">服务器路径</el-radio>
            <el-radio label="editor">在线编辑</el-radio>
          </el-radio-group>

          <div v-if="scriptMode === 'path'">
            <el-input
              v-model="form.script_path"
              placeholder="./scripts/my_script.py"
              :rules="[{ required: true, message: '请输入脚本路径', trigger: 'blur' }]"
            />
          </div>
          <div v-else class="editor-wrapper">
            <div class="editor-header">
              <span>Python Editor</span>
              <el-tag v-if="aiCapabilities.docker_available" size="small" :type="form.use_docker ? 'success' : 'info'">
                <el-icon><Box /></el-icon>
                {{ form.use_docker ? '沙箱模式' : '普通模式' }}
              </el-tag>
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
        </el-form-item>

        <!-- AI Review Result -->
        <el-alert
          v-if="aiReviewResult"
          :title="'AI 代码审查结果'"
          type="success"
          :closable="true"
          @close="aiReviewResult = null"
          class="mb-4"
        >
          <template #default>
            <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-muted);">{{ aiReviewResult }}</pre>
          </template>
        </el-alert>

        <el-form-item label="Python 解释器 (可选)">
          <el-input
            v-model="form.interpreter_path"
            placeholder="/usr/bin/python3"
          />
        </el-form-item>

        <el-form-item label="定时执行">
          <!-- NLP to Cron -->
          <el-card shadow="never" class="mb-3">
            <div class="flex items-center gap-2 mb-2">
              <el-icon><MagicStick /></el-icon>
              <span class="text-xs" style="color: var(--text-muted);">自然语言设置定时</span>
            </div>
            <div class="flex gap-2">
              <el-input
                v-model="nlpCronInput"
                placeholder="例如：每个工作日下午5点半"
                @keyup.enter="convertNLPCron"
              />
              <el-button
                @click="convertNLPCron"
                :loading="aiCronConverting"
                :disabled="!nlpCronInput.trim()"
                type="primary"
              >
                {{ aiCronConverting ? '转换中' : '转Cron' }}
              </el-button>
            </div>
            <div v-if="nlpCronResult" class="mt-2 text-xs" style="color: var(--color-success);">
              ✓ {{ nlpCronResult }}
            </div>
          </el-card>

          <!-- Cron Presets -->
          <div class="flex gap-2 mb-3">
            <el-tag
              v-for="preset in cronPresets"
              :key="preset.value"
              :type="form.cron_expr === preset.value ? 'primary' : 'info'"
              class="cursor-pointer"
              @click="form.cron_expr = preset.value"
            >
              {{ preset.label }}
            </el-tag>
          </div>
          <el-input v-model="form.cron_expr" placeholder="* * * * *" />
          <p class="text-xs mt-1" v-if="form.cron_expr" style="color: var(--text-muted);">{{ cronHumanText(form.cron_expr) }}</p>
        </el-form-item>

        <el-form-item label="前置任务依赖 (可选)">
          <el-select v-model="form.depends_on" placeholder="选择前置任务" clearable>
            <el-option
              v-for="t in availableDependencies"
              :key="t.id"
              :label="t.name"
              :value="t.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Webhook 触发">
          <div class="flex items-center gap-3">
            <el-switch
              v-model="form.webhook_enabled"
              active-text="启用 Webhook URL 触发"
            />
          </div>
          <div v-if="form.webhook_enabled && (isEditing || currentWebhookToken)" class="mt-2">
            <code class="px-2 py-1 rounded text-xs" :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--color-primary)' }">
              /webhook/{{ currentWebhookToken }}
            </code>
            <el-button size="small" @click="copyWebhookUrl" class="ml-2">
              <el-icon><DocumentCopy /></el-icon>
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="超时时间 (秒)">
          <el-input-number v-model="form.timeout" :min="0" placeholder="300" />
        </el-form-item>

        <!-- Auto Doc Generation -->
        <el-alert
          v-if="!isEditing && form.script_content"
          :title="'AI 自动生成文档'"
          type="success"
          :closable="false"
          show-icon
          class="mb-4"
        >
          <template #default>
            <div class="flex justify-between items-center">
              <span v-if="aiGeneratedDoc" class="text-xs">{{ aiGeneratedDoc }}</span>
              <span v-else class="text-xs" style="color: var(--text-disabled);">保存时将自动生成文档描述</span>
              <el-button size="small" @click="generateDocWithAI" :loading="aiDocGenerating">
                {{ aiDocGenerating ? '生成中...' : '重新生成' }}
              </el-button>
            </div>
          </template>
        </el-alert>

        <el-form-item class="form-actions">
          <el-button @click="closeDrawer">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="formSubmitting">
            {{ isEditing ? '保存' : '创建' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-drawer>

    <!-- Log Drawer -->
    <el-drawer
      v-model="showLogDrawer"
      :title="'日志查看 - ' + (currentTask?.name || '')"
      size="700px"
      :before-close="closeLogDrawer"
    >
      <!-- Log Toolbar -->
      <div class="log-toolbar">
        <el-input
          v-model="logSearch"
          placeholder="搜索..."
          class="log-search"
          clearable
        />
        <el-date-picker
          v-model="logDateFilter"
          type="date"
          placeholder="选择日期"
          class="log-date"
        />
        <el-button
          v-if="currentLog && currentLog.output && currentLog.output.length > 500"
          @click="summarizeLogWithAI"
          :loading="aiLogSummarizing"
          type="primary"
          plain
        >
          <el-icon><MagicStick /></el-icon>
          AI摘要
        </el-button>
        <el-button @click="downloadLog">
          <el-icon><Download /></el-icon>
        </el-button>
        <el-button type="primary" @click="runTask(currentTask)">
          <el-icon><VideoPlay /></el-icon>
          运行
        </el-button>
      </div>

      <!-- AI Log Summary -->
      <el-alert
        v-if="aiLogSummary"
        :title="'AI 日志摘要'"
        type="success"
        :closable="true"
        @close="aiLogSummary = null"
        class="mb-3"
      >
        <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ aiLogSummary }}</pre>
      </el-alert>

      <!-- AI Error Diagnosis -->
      <el-alert
        v-if="aiErrorDiagnosis"
        :title="'AI 错误诊断'"
        type="error"
        :closable="true"
        @close="aiErrorDiagnosis = null"
        class="mb-3"
      >
        <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ aiErrorDiagnosis }}</pre>
      </el-alert>

      <!-- Terminal Content -->
      <div class="terminal-content">
        <div class="terminal-prompt" style="color: var(--text-muted);">
          <span style="color: var(--color-primary);">pycron</span>:<span style="color: var(--color-success);">~</span>$ python {{ currentTask?.script_path }}
        </div>

        <el-empty v-if="filteredLogs.length === 0" description="暂无执行记录" />

        <div v-else class="log-sessions">
          <div v-for="(log, idx) in filteredLogs" :key="log.id" class="log-session">
            <div class="log-header">
              <div class="log-meta">
                <span style="color: var(--color-primary);">[{{ idx + 1 }}]</span>
                <span>{{ formatTime(log.start_time) }}</span>
                <span v-if="log.end_time">→ {{ formatTime(log.end_time) }}</span>
                <el-tag :type="log.exit_code === 0 ? 'success' : 'danger'" size="small">
                  exit {{ log.exit_code }}
                </el-tag>
              </div>
              <el-button
                v-if="log.exit_code !== 0"
                size="small"
                type="warning"
                @click="diagnoseErrorWithAI(log)"
                :loading="aiDiagnosingLogId === log.id"
              >
                <el-icon><MagicStick /></el-icon>
                诊断
              </el-button>
            </div>
            <pre class="log-output" v-html="highlightKeyword(log.output || '// 无输出')"></pre>
          </div>
        </div>
        <div class="terminal-cursor" :style="{ backgroundColor: 'var(--color-success)' }"></div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import cronParser from 'cron-parser'
import {
  Plus, VideoPlay, Edit, Delete, Document, Link, Box,
  ArrowRight, MagicStick, DocumentCopy, Download
} from '@element-plus/icons-vue'
import { taskApi, aiApi, scriptApi } from '../utils/api.js'
import { formatTimeFull, cronHumanText, statusText } from '../utils/formatters.js'

const tasks = ref([])
const showDrawer = ref(false)
const isEditing = ref(false)
const scriptMode = ref('path')
const currentTask = ref(null)
const taskFormRef = ref(null)
const formSubmitting = ref(false)

// AI state
const aiDescription = ref('')
const aiGenerating = ref(false)
const aiReviewing = ref(false)
const aiReviewResult = ref('')
const aiGeneratedDoc = ref('')
const aiDocGenerating = ref(false)
const nlpCronInput = ref('')
const nlpCronResult = ref('')
const aiCronConverting = ref(false)
const aiCapabilities = ref({ docker_available: false })
const currentWebhookToken = ref('')

const logs = ref([])
const showLogDrawer = ref(false)
const logSearch = ref('')
const logDateFilter = ref('')
const aiLogSummary = ref('')
const aiLogSummarizing = ref(false)
const aiErrorDiagnosis = ref('')
const aiDiagnosingLogId = ref(null)
const currentLog = ref(null)

const form = reactive({
  id: null, name: '', script_path: './scripts/', script_content: '',
  cron_expr: '* * * * *', timeout: 300, is_active: true,
  interpreter_path: null, depends_on: null,
  webhook_enabled: false, description: '', use_docker: false, docker_image: null
})

const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  script_path: [{ required: true, message: '请输入脚本路径', trigger: 'blur' }]
}

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
    const res = await taskApi.list()
    tasks.value = res.data
  } catch (e) { console.error(e) }
}

async function fetchLogs(taskId) {
  try {
    const res = await taskApi.logs(taskId)
    logs.value = res.data
  } catch (e) { console.error(e) }
}

async function fetchAiCapabilities() {
  try {
    const res = await aiApi.capabilities()
    aiCapabilities.value = res.data
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

function highlightKeyword(text) {
  if (!logSearch.value) return text
  const kw = logSearch.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${kw})`, 'gi'), '<mark style="background-color: var(--color-warning-subtle); color: var(--color-warning); padding: 0 2px; border-radius: 2px;">$1</mark>')
}

// ========== AI Functions ==========

async function generateScriptWithAI() {
  if (!aiDescription.value.trim() || aiGenerating.value) return
  aiGenerating.value = true
  try {
    const res = await aiApi.generateScript(aiDescription.value)
    form.script_content = res.data.code
    scriptMode.value = 'editor'
    await generateDocWithAI()
    ElMessage.success('AI 脚本生成成功')
  } catch (e) {
    ElMessage.error('AI生成失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiGenerating.value = false
  }
}

async function reviewCodeWithAI() {
  if (!form.script_content || aiReviewing.value) return
  aiReviewing.value = true
  try {
    const res = await aiApi.codeReview(form.script_content)
    aiReviewResult.value = res.data.review
  } catch (e) {
    ElMessage.error('AI审查失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiReviewing.value = false
  }
}

async function generateDocWithAI() {
  if (!form.script_content || aiDocGenerating.value) return
  aiDocGenerating.value = true
  try {
    const res = await aiApi.generateDoc(form.script_content)
    aiGeneratedDoc.value = res.data.doc
    form.description = res.data.doc
  } catch (e) {
    console.error('AI文档生成失败:', e)
  } finally {
    aiDocGenerating.value = false
  }
}

async function convertNLPCron() {
  if (!nlpCronInput.value.trim() || aiCronConverting.value) return
  aiCronConverting.value = true
  try {
    const res = await aiApi.nlpToCron(nlpCronInput.value)
    form.cron_expr = res.data.cron_expr
    nlpCronResult.value = res.data.description
    ElMessage.success(res.data.description)
    setTimeout(() => { nlpCronResult.value = '' }, 3000)
  } catch (e) {
    ElMessage.error('Cron转换失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiCronConverting.value = false
  }
}

async function summarizeLogWithAI() {
  if (!currentLog.value?.output || aiLogSummarizing.value) return
  aiLogSummarizing.value = true
  try {
    const res = await aiApi.summarizeLog(currentLog.value.output)
    aiLogSummary.value = res.data.summary
  } catch (e) {
    ElMessage.error('日志摘要失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiLogSummarizing.value = false
  }
}

async function diagnoseErrorWithAI(log) {
  if (aiDiagnosingLogId.value) return
  aiDiagnosingLogId.value = log.id
  aiErrorDiagnosis.value = null
  try {
    const res = await aiApi.diagnoseError(log.output, '')
    aiErrorDiagnosis.value = res.data.diagnosis
  } catch (e) {
    ElMessage.error('AI诊断失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiDiagnosingLogId.value = null
  }
}

function copyWebhookUrl() {
  navigator.clipboard.writeText(`${window.location.origin}/webhook/${currentWebhookToken.value}`)
  ElMessage.success('Webhook URL 已复制')
}

// ========== Main Functions ==========

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
  form.webhook_enabled = task.webhook_enabled || false
  form.description = task.description || ''
  form.use_docker = task.use_docker || false
  form.docker_image = task.docker_image
  scriptMode.value = 'path'
  aiGeneratedDoc.value = task.description || ''
  if (task.webhook_enabled) {
    fetchWebhookInfo(task.id)
  }
  showDrawer.value = true
}

async function fetchWebhookInfo(taskId) {
  try {
    const res = await taskApi.webhookInfo(taskId)
    currentWebhookToken.value = res.data.webhook_token || ''
  } catch (e) {
    console.error(e)
  }
}

function closeDrawer() {
  showDrawer.value = false
  aiReviewResult.value = null
  aiGeneratedDoc.value = ''
}

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
  form.webhook_enabled = false
  form.description = ''
  form.use_docker = false
  form.docker_image = null
  aiDescription.value = ''
  aiReviewResult.value = null
  aiGeneratedDoc.value = ''
  nlpCronInput.value = ''
  nlpCronResult.value = ''
  currentWebhookToken.value = ''
}

async function submitForm() {
  if (!taskFormRef.value) return
  try {
    await taskFormRef.value.validate()
  } catch {
    return
  }

  formSubmitting.value = true
  try {
    const payload = {
      name: form.name,
      script_path: (form.script_path && form.script_path.trim()) ? form.script_path : './scripts/task_' + Date.now() + '.py',
      cron_expr: form.cron_expr || null,
      is_active: form.is_active,
      interpreter_path: form.interpreter_path || null,
      depends_on: form.depends_on,
      timeout: form.timeout || 300,
      webhook_enabled: form.webhook_enabled,
      description: aiGeneratedDoc.value || form.description,
      use_docker: form.use_docker,
      docker_image: form.docker_image
    }

    if (scriptMode.value === 'editor' && form.script_content) {
      const filename = 'task_' + Date.now() + '.py'
      await scriptApi.uploadText(filename, form.script_content)
      payload.script_path = './scripts/' + filename
    }

    if (isEditing.value) {
      await taskApi.update(form.id, payload)
      if (payload.webhook_enabled) {
        await taskApi.enableWebhook(form.id)
        await fetchWebhookInfo(form.id)
      }
      ElMessage.success('任务更新成功')
    } else {
      const res = await taskApi.create(payload)
      if (payload.webhook_enabled) {
        await taskApi.enableWebhook(res.data.id)
        await fetchWebhookInfo(res.data.id)
      }
      ElMessage.success('任务创建成功')
    }
    closeDrawer()
    fetchTasks()
  } catch (e) {
    ElMessage.error('操作失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    formSubmitting.value = false
  }
}

async function toggleTask(task) {
  try {
    await taskApi.toggle(task.id, !task.is_active)
    fetchTasks()
    ElMessage.success(task.is_active ? '任务已禁用' : '任务已启用')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function runTask(task) {
  if (!task) task = currentTask.value
  try {
    await taskApi.run(task.id)
    ElMessage.success('任务已启动')
    setTimeout(() => { fetchTasks(); refreshLogs() }, 1000)
  } catch (e) {
    ElMessage.error('启动失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function deleteTask(task) {
  try {
    await ElMessageBox.confirm(`确定删除任务 "${task.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await taskApi.delete(task.id)
    fetchTasks()
    ElMessage.success('任务已删除')
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

function goToLogs(task) {
  currentTask.value = task
  fetchLogs(task.id)
  showLogDrawer.value = true
}

function closeLogDrawer() {
  showLogDrawer.value = false
}

function refreshLogs() {
  if (currentTask.value) {
    fetchLogs(currentTask.value.id)
  }
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

onMounted(() => {
  fetchTasks()
  fetchAiCapabilities()
  setInterval(fetchTasks, 5000)
})
</script>

<style scoped>
.tasks-page {
  width: 100%;
}

.tasks-card {
  border-radius: 12px;
  border: 1px solid var(--border-subtle);
}

.editor-wrapper {
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-subtle);
}

.log-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.log-search {
  width: 200px;
}

.log-date {
  width: 150px;
}

.terminal-content {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  line-height: 1.6;
  padding: 16px;
  background-color: var(--bg-primary);
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}

.terminal-prompt {
  margin-bottom: 16px;
}

.log-sessions {
  margin-top: 16px;
}

.log-session {
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.log-session:last-child {
  border-bottom: none;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.log-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-muted);
  align-items: center;
}

.log-output {
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--text-main);
  font-size: 13px;
  line-height: 1.5;
}

.terminal-cursor {
  display: inline-block;
  width: 8px;
  height: 16px;
  animation: blink 1s step-end infinite;
  vertical-align: middle;
  margin-top: 8px;
}

@keyframes blink {
  50% { opacity: 0; }
}
</style>
