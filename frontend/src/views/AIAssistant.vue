<template>
  <div class="ai-assistant space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold" style="color: var(--text-main);">
          <el-icon class="mr-2"><MagicStick /></el-icon>
          AI 助手
        </h1>
        <p class="text-sm mt-1" style="color: var(--text-muted);">智能代码生成、审查与诊断工具</p>
      </div>
      <el-tag :type="aiEnabled ? 'success' : 'warning'">
        {{ aiEnabled ? 'AI 已连接' : 'AI 未配置' }}
      </el-tag>
    </div>

    <!-- AI Tools Grid -->
    <el-row :gutter="24">
      <!-- Text to Script Generator -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="tool-card">
          <template #header>
            <div class="tool-header">
              <el-avatar :style="{ backgroundColor: 'var(--color-primary-subtle)' }">
                <el-icon><MagicStick /></el-icon>
              </el-avatar>
              <div>
                <div class="font-semibold">Text-to-Script</div>
                <div class="text-xs" style="color: var(--text-muted);">自然语言生成 Python 脚本</div>
              </div>
            </div>
          </template>

          <el-input
            v-model="scriptPrompt"
            type="textarea"
            :rows="4"
            placeholder="用自然语言描述你想要实现的脚本功能..."
          />

          <el-button
            class="mt-4 w-full"
            type="primary"
            @click="handleGenerateScript"
            :loading="aiLoading"
            :disabled="!scriptPrompt.trim()"
          >
            {{ aiLoading ? '生成中...' : '生成代码' }}
          </el-button>

          <div v-if="generatedScript" class="mt-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm" style="color: var(--text-muted);">生成的代码</span>
              <div class="flex gap-2">
                <el-button size="small" @click="handleCopyScript">
                  <el-icon><DocumentCopy /></el-icon>
                </el-button>
                <el-button size="small" type="primary" @click="handleSaveAsTask">
                  保存为任务
                </el-button>
              </div>
            </div>
            <div class="code-preview">
              <pre>{{ generatedScript }}</pre>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- NLP to Cron -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="tool-card">
          <template #header>
            <div class="tool-header">
              <el-avatar :style="{ backgroundColor: 'rgba(168, 85, 247, 0.15)' }">
                <el-icon><Clock /></el-icon>
              </el-avatar>
              <div>
                <div class="font-semibold">NLP to Cron</div>
                <div class="text-xs" style="color: var(--text-muted);">自然语言转 Cron 表达式</div>
              </div>
            </div>
          </template>

          <el-input
            v-model="cronPrompt"
            placeholder="例如：每个工作日下午5点半"
            @keyup.enter="handleConvertCron"
          />

          <el-button
            class="mt-4 w-full"
            type="primary"
            @click="handleConvertCron"
            :loading="aiLoading"
            :disabled="!cronPrompt.trim()"
          >
            {{ aiLoading ? '转换中...' : '转换为 Cron' }}
          </el-button>

          <div v-if="cronResult" class="mt-4">
            <el-alert :title="cronResult.description" type="success" :closable="false">
              <template #default>
                <code class="text-xl font-bold">{{ cronResult.expr }}</code>
              </template>
            </el-alert>
            <div class="flex gap-2 mt-3">
              <el-button class="flex-1" @click="handleCopyCron">
                <el-icon><DocumentCopy /></el-icon>
                复制
              </el-button>
              <el-button class="flex-1" type="primary" @click="handleApplyCron">
                应用到任务
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Code Review -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="tool-card">
          <template #header>
            <div class="tool-header">
              <el-avatar :style="{ backgroundColor: 'var(--color-warning-subtle)' }">
                <el-icon><Search /></el-icon>
              </el-avatar>
              <div>
                <div class="font-semibold">AI 代码审查</div>
                <div class="text-xs" style="color: var(--text-muted);">代码性能与安全检查</div>
              </div>
            </div>
          </template>

          <div class="editor-wrapper">
            <vue-monaco-editor
              v-model:value="reviewCode"
              language="python"
              theme="vs-dark"
              :options="editorOptions"
            />
          </div>

          <el-button
            class="mt-4 w-full"
            type="warning"
            @click="handleCodeReview"
            :loading="aiLoading"
            :disabled="!reviewCode.trim()"
          >
            {{ aiLoading ? '审查中...' : '开始审查' }}
          </el-button>

          <el-alert v-if="reviewResult" title="审查结果" type="info" :closable="true" class="mt-4">
            <pre class="text-xs whitespace-pre-wrap">{{ reviewResult }}</pre>
          </el-alert>
        </el-card>
      </el-col>

      <!-- Error Diagnosis -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="tool-card">
          <template #header>
            <div class="tool-header">
              <el-avatar :style="{ backgroundColor: 'var(--color-danger-subtle)' }">
                <el-icon><Warning /></el-icon>
              </el-avatar>
              <div>
                <div class="font-semibold">错误诊断</div>
                <div class="text-xs" style="color: var(--text-muted);">智能错误分析与修复建议</div>
              </div>
            </div>
          </template>

          <el-input
            v-model="errorInput"
            type="textarea"
            :rows="4"
            placeholder="粘贴错误信息或 traceback..."
            class="mb-3"
          />

          <el-input
            v-model="errorCode"
            type="textarea"
            :rows="3"
            placeholder="相关代码 (可选)..."
            class="mb-3"
          />

          <el-button
            class="w-full"
            type="danger"
            @click="handleDiagnoseError"
            :loading="aiLoading"
            :disabled="!errorInput.trim()"
          >
            {{ aiLoading ? '诊断中...' : '开始诊断' }}
          </el-button>

          <el-alert v-if="diagnosisResult" title="诊断结果" type="error" :closable="true" class="mt-4">
            <pre class="text-xs whitespace-pre-wrap">{{ diagnosisResult }}</pre>
          </el-alert>
        </el-card>
      </el-col>
    </el-row>

    <!-- Log Diagnosis Section -->
    <el-card shadow="never">
      <template #header>
        <div class="tool-header">
          <el-avatar :style="{ backgroundColor: 'var(--color-success-subtle)' }">
            <el-icon><Document /></el-icon>
          </el-avatar>
          <div>
            <div class="font-semibold">日志摘要</div>
            <div class="text-xs" style="color: var(--text-muted);">粘贴日志内容，AI 将提炼关键信息</div>
          </div>
        </div>
      </template>

      <el-input
        v-model="logInput"
        type="textarea"
        :rows="5"
        placeholder="粘贴日志内容..."
      />

      <el-button
        class="mt-4"
        type="success"
        @click="handleSummarizeLog"
        :loading="aiLoading"
        :disabled="!logInput.trim()"
      >
        {{ aiLoading ? '分析中...' : '生成摘要' }}
      </el-button>

      <el-alert v-if="logSummary" title="日志摘要" type="success" :closable="true" class="mt-4">
        <pre class="text-sm whitespace-pre-wrap">{{ logSummary }}</pre>
      </el-alert>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  MagicStick, Clock, Search, Warning, Document, DocumentCopy
} from '@element-plus/icons-vue'
import { useAI } from '../composables/useAI.js'

const { aiEnabled, checkAIStatus, generateScript, codeReview, nlpToCron, diagnoseError, summarizeLog, aiLoading } = useAI()

// Text to Script
const scriptPrompt = ref('')
const generatedScript = ref('')

// NLP to Cron
const cronPrompt = ref('')
const cronResult = ref(null)

// Code Review
const reviewCode = ref('')
const reviewResult = ref('')

// Error Diagnosis
const errorInput = ref('')
const errorCode = ref('')
const diagnosisResult = ref('')

// Log Summary
const logInput = ref('')
const logSummary = ref('')

const editorOptions = {
  minimap: { enabled: false },
  fontSize: 13,
  lineNumbers: 'on',
  scrollBeyondLastLine: false,
  automaticLayout: true,
  tabSize: 4,
  wordWrap: 'on',
  padding: { top: 8 },
  height: '200px'
}

async function handleGenerateScript() {
  try {
    const result = await generateScript(scriptPrompt.value)
    generatedScript.value = result.code
    ElMessage.success('代码生成成功')
  } catch (e) {
    console.error(e)
  }
}

function handleCopyScript() {
  navigator.clipboard.writeText(generatedScript.value)
  ElMessage.success('已复制到剪贴板')
}

function handleSaveAsTask() {
  window.location.href = '/tasks?script=' + encodeURIComponent(generatedScript.value)
}

async function handleConvertCron() {
  try {
    const result = await nlpToCron(cronPrompt.value)
    cronResult.value = {
      expr: result.cron_expr,
      description: result.description
    }
    ElMessage.success('Cron 表达式转换成功')
  } catch (e) {
    console.error(e)
  }
}

function handleCopyCron() {
  if (cronResult.value) {
    navigator.clipboard.writeText(cronResult.value.expr)
    ElMessage.success('已复制到剪贴板')
  }
}

function handleApplyCron() {
  window.location.href = '/tasks?cron=' + encodeURIComponent(cronResult.value?.expr || '')
}

async function handleCodeReview() {
  try {
    const result = await codeReview(reviewCode.value)
    reviewResult.value = result.review
    ElMessage.success('代码审查完成')
  } catch (e) {
    console.error(e)
  }
}

async function handleDiagnoseError() {
  try {
    const result = await diagnoseError(errorInput.value, errorCode.value)
    diagnosisResult.value = result.diagnosis
    ElMessage.success('错误诊断完成')
  } catch (e) {
    console.error(e)
  }
}

async function handleSummarizeLog() {
  try {
    const result = await summarizeLog(logInput.value)
    logSummary.value = result.summary
    ElMessage.success('日志摘要生成成功')
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  checkAIStatus()
})
</script>

<style scoped>
.tool-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.tool-card {
  height: 100%;
  margin-bottom: var(--space-md);
}

.code-preview {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  max-height: 300px;
  overflow: auto;
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
}

.code-preview pre {
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--text-main);
  margin: 0;
}

.editor-wrapper {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  overflow: hidden;
}
</style>
