<template>
  <el-drawer
    v-model="visible"
    :title="isEditing ? '编辑任务' : '新建任务'"
    size="500px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-position="top"
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
              @click="handleGenerateScript"
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
        <el-input v-model="formData.name" placeholder="输入任务名称" />
      </el-form-item>

      <el-form-item label="脚本来源">
        <el-radio-group v-model="scriptMode" class="mb-2">
          <el-radio label="path">服务器路径</el-radio>
          <el-radio label="editor">在线编辑</el-radio>
        </el-radio-group>

        <div v-if="scriptMode === 'path'">
          <el-input
            v-model="formData.script_path"
            placeholder="./scripts/my_script.py"
          />
        </div>
        <div v-else class="editor-wrapper">
          <div class="editor-header">
            <span>Python Editor</span>
            <el-tag v-if="aiCapabilities.docker_available" size="small" :type="formData.use_docker ? 'success' : 'info'">
              <el-icon><Box /></el-icon>
              {{ formData.use_docker ? '沙箱模式' : '普通模式' }}
            </el-tag>
          </div>
          <vue-monaco-editor
            v-model:value="formData.script_content"
            language="python"
            theme="vs-dark"
            :options="editorOptions"
            height="200px"
          />
        </div>
      </el-form-item>

      <!-- AI Review Result -->
      <el-alert
        v-if="aiReviewResult"
        title="AI 代码审查结果"
        type="success"
        :closable="true"
        @close="aiReviewResult = null"
        class="mb-4"
      >
        <template #default>
          <pre class="text-xs whitespace-pre-wrap">{{ aiReviewResult }}</pre>
        </template>
      </el-alert>

      <el-form-item label="Python 解释器 (可选)">
        <el-input
          v-model="formData.interpreter_path"
          placeholder="/usr/bin/python3"
        />
      </el-form-item>

      <el-form-item label="定时执行">
        <!-- NLP to Cron -->
        <el-card shadow="never" class="mb-3">
          <div class="flex items-center gap-2 mb-2">
            <el-icon><MagicStick /></el-icon>
            <span class="text-xs">自然语言设置定时</span>
          </div>
          <div class="flex gap-2">
            <el-input
              v-model="nlpCronInput"
              placeholder="例如：每个工作日下午5点半"
              @keyup.enter="handleConvertCron"
            />
            <el-button
              @click="handleConvertCron"
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
            :type="formData.cron_expr === preset.value ? 'primary' : 'info'"
            class="cursor-pointer"
            @click="formData.cron_expr = preset.value"
          >
            {{ preset.label }}
          </el-tag>
        </div>
        <el-input v-model="formData.cron_expr" placeholder="* * * * *" />
        <p class="text-xs mt-1" v-if="formData.cron_expr">{{ cronHumanText(formData.cron_expr) }}</p>
      </el-form-item>

      <el-form-item label="前置任务依赖 (可选)">
        <el-select v-model="formData.depends_on" placeholder="选择前置任务" clearable>
          <el-option
            v-for="t in availableTasks"
            :key="t.id"
            :label="t.name"
            :value="t.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="Webhook 触发">
        <div class="flex items-center gap-3">
          <el-switch
            v-model="formData.webhook_enabled"
            active-text="启用 Webhook URL 触发"
          />
        </div>
        <div v-if="formData.webhook_enabled && (isEditing || currentWebhookToken)" class="mt-2">
          <code class="px-2 py-1 rounded text-xs" style="background-color: var(--bg-tertiary); color: var(--color-primary);">
            /webhook/{{ currentWebhookToken }}
          </code>
          <el-button size="small" @click="handleCopyWebhook" class="ml-2">
            <el-icon><DocumentCopy /></el-icon>
          </el-button>
        </div>
      </el-form-item>

      <el-form-item label="超时时间 (秒)">
        <el-input-number v-model="formData.timeout" :min="0" placeholder="300" />
      </el-form-item>

      <el-form-item label="日志保留条数">
        <el-input-number v-model="formData.log_retention_count" :min="0" placeholder="100" />
        <p class="text-xs mt-1" style="color: var(--text-muted);">设为0则不限制保留条数</p>
      </el-form-item>

      <!-- Auto Doc Generation -->
      <el-alert
        v-if="!isEditing && formData.script_content"
        title="AI 自动生成文档"
        type="success"
        :closable="false"
        show-icon
        class="mb-4"
      >
        <template #default>
          <div class="flex justify-between items-center">
            <span v-if="aiGeneratedDoc" class="text-xs">{{ aiGeneratedDoc }}</span>
            <span v-else class="text-xs" style="color: var(--text-disabled);">保存时将自动生成文档描述</span>
            <el-button size="small" @click="handleGenerateDoc" :loading="aiDocGenerating">
              {{ aiDocGenerating ? '生成中...' : '重新生成' }}
            </el-button>
          </div>
        </template>
      </el-alert>

      <el-form-item class="form-actions">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEditing ? '保存' : '创建' }}
        </el-button>
      </el-form-item>
    </el-form>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, Box, DocumentCopy } from '@element-plus/icons-vue'
import { useAI } from '../../composables/useAI.js'
import { cronHumanText } from '../../utils/formatters.js'

const props = defineProps({
  modelValue: Boolean,
  task: Object,
  tasks: Array
})

const emit = defineEmits(['update:modelValue', 'success'])

const { generateScript, codeReview, generateDoc, nlpToCron, aiLoading } = useAI()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEditing = computed(() => !!props.task?.id)
const availableTasks = computed(() => props.tasks?.filter(t => t.id !== props.task?.id) || [])

const formRef = ref(null)
const submitting = ref(false)
const scriptMode = ref('path')
const aiDescription = ref('')
const aiGenerating = ref(false)
const aiReviewResult = ref('')
const aiGeneratedDoc = ref('')
const aiDocGenerating = ref(false)
const nlpCronInput = ref('')
const nlpCronResult = ref('')
const aiCronConverting = ref(false)
const currentWebhookToken = ref('')

const aiCapabilities = ref({ docker_available: false })

const formData = reactive({
  id: null,
  name: '',
  script_path: './scripts/',
  script_content: '',
  cron_expr: '* * * * *',
  timeout: 300,
  is_active: true,
  interpreter_path: null,
  depends_on: null,
  webhook_enabled: false,
  description: '',
  use_docker: false,
  docker_image: null,
  log_retention_count: 100
})

const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  script_path: [{ required: true, message: '请输入脚本路径', trigger: 'blur' }]
}

const editorOptions = {
  minimap: { enabled: false },
  fontSize: 14,
  lineNumbers: 'on',
  scrollBeyondLastLine: false,
  automaticLayout: true,
  tabSize: 4,
  wordWrap: 'on',
  padding: { top: 8 }
}

const cronPresets = [
  { label: '每分钟', value: '* * * * *' },
  { label: '每小时', value: '0 * * * *' },
  { label: '每天凌晨', value: '0 2 * * *' },
  { label: '每周一', value: '0 9 * * 1' }
]

// Watch for task changes to populate form
watch(() => props.task, (task) => {
  if (task) {
    formData.id = task.id
    formData.name = task.name
    formData.script_path = task.script_path
    formData.cron_expr = task.cron_expr || '* * * * *'
    formData.timeout = task.timeout || 300
    formData.is_active = task.is_active
    formData.interpreter_path = task.interpreter_path
    formData.depends_on = task.depends_on
    formData.webhook_enabled = task.webhook_enabled || false
    formData.description = task.description || ''
    formData.use_docker = task.use_docker || false
    formData.docker_image = task.docker_image
    formData.log_retention_count = task.log_retention_count ?? 100
    aiGeneratedDoc.value = task.description || ''
    scriptMode.value = 'path'
  }
}, { immediate: true })

async function handleGenerateScript() {
  if (!aiDescription.value.trim() || aiGenerating.value) return
  aiGenerating.value = true
  try {
    const result = await generateScript(aiDescription.value)
    formData.script_content = result.code
    scriptMode.value = 'editor'
    await handleGenerateDoc()
    ElMessage.success('AI 脚本生成成功')
  } finally {
    aiGenerating.value = false
  }
}

async function handleGenerateDoc() {
  if (!formData.script_content || aiDocGenerating.value) return
  aiDocGenerating.value = true
  try {
    const result = await generateDoc(formData.script_content)
    aiGeneratedDoc.value = result.doc
    formData.description = result.doc
  } catch (e) {
    console.error('AI文档生成失败:', e)
  } finally {
    aiDocGenerating.value = false
  }
}

async function handleConvertCron() {
  if (!nlpCronInput.value.trim() || aiCronConverting.value) return
  aiCronConverting.value = true
  try {
    const result = await nlpToCron(nlpCronInput.value)
    formData.cron_expr = result.cron_expr
    nlpCronResult.value = result.description
    ElMessage.success(result.description)
    setTimeout(() => { nlpCronResult.value = '' }, 3000)
  } finally {
    aiCronConverting.value = false
  }
}

function handleCopyWebhook() {
  navigator.clipboard.writeText(`${window.location.origin}/webhook/${currentWebhookToken.value}`)
  ElMessage.success('Webhook URL 已复制')
}

async function handleSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    const payload = {
      name: formData.name,
      script_path: (formData.script_path && formData.script_path.trim()) ? formData.script_path : './scripts/task_' + Date.now() + '.py',
      cron_expr: formData.cron_expr || null,
      is_active: formData.is_active,
      interpreter_path: formData.interpreter_path || null,
      depends_on: formData.depends_on,
      timeout: formData.timeout || 300,
      webhook_enabled: formData.webhook_enabled,
      description: aiGeneratedDoc.value || formData.description,
      use_docker: formData.use_docker,
      docker_image: formData.docker_image,
      log_retention_count: formData.log_retention_count
    }

    // If using editor mode, save the script first
    if (scriptMode.value === 'editor' && formData.script_content) {
      const filename = 'task_' + Date.now() + '.py'
      await window.$scriptApi?.uploadText?.(filename, formData.script_content) || {}
      payload.script_path = './scripts/' + filename
    }

    emit('success', payload)
    handleClose()
  } finally {
    submitting.value = false
  }
}

function handleClose() {
  visible.value = false
  resetForm()
}

function resetForm() {
  formData.id = null
  formData.name = ''
  formData.script_path = './scripts/'
  formData.script_content = ''
  formData.cron_expr = '* * * * *'
  formData.timeout = 300
  formData.is_active = true
  formData.interpreter_path = null
  formData.depends_on = null
  formData.webhook_enabled = false
  formData.description = ''
  formData.use_docker = false
  formData.docker_image = null
  formData.log_retention_count = 100
  aiDescription.value = ''
  aiReviewResult.value = null
  aiGeneratedDoc.value = ''
  nlpCronInput.value = ''
  nlpCronResult.value = ''
  currentWebhookToken.value = ''
  scriptMode.value = 'path'
}
</script>

<style scoped>
.editor-wrapper {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm) var(--space-md);
  background-color: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  border-bottom: 1px solid var(--border-subtle);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  margin-top: var(--space-xl);
  padding-top: var(--space-xl);
  border-top: 1px solid var(--border-subtle);
}
</style>
