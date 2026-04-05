<template>
  <div class="ai-assistant space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--text-main);">
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
            placeholder="用自然语言描述你想要实现的脚本功能...
例如：创建一个定时任务，每周一把 /data 目录下的日志文件压缩备份到 /backup"
          />

          <el-button
            class="mt-4 w-full"
            type="primary"
            @click="generateScript"
            :loading="aiGenerating"
            :disabled="!scriptPrompt.trim()"
          >
            <el-icon v-if="!aiGenerating"><MagicStick /></el-icon>
            {{ aiGenerating ? '生成中...' : '生成代码' }}
          </el-button>

          <!-- Generated Code Preview -->
          <div v-if="generatedScript" class="mt-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm" style="color: var(--text-muted);">生成的代码</span>
              <div class="flex gap-2">
                <el-button size="small" @click="copyScript">
                  <el-icon><DocumentCopy /></el-icon>
                </el-button>
                <el-button size="small" type="primary" @click="saveScriptAsTask">
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
            placeholder="输入时间描述...
例如：每个工作日下午5点半"
            @keyup.enter="convertCron"
          />

          <el-button
            class="mt-4 w-full"
            type="primary"
            @click="convertCron"
            :loading="aiCronConverting"
            :disabled="!cronPrompt.trim()"
          >
            <el-icon v-if="!aiCronConverting"><MagicStick /></el-icon>
            {{ aiCronConverting ? '转换中...' : '转换为 Cron' }}
          </el-button>

          <!-- Cron Result -->
          <div v-if="cronResult" class="mt-4">
            <el-alert :title="cronResult.description" type="success" :closable="false">
              <template #default>
                <code class="text-xl font-bold">{{ cronResult.expr }}</code>
              </template>
            </el-alert>
            <div class="flex gap-2 mt-3">
              <el-button class="flex-1" @click="copyCron">
                <el-icon><DocumentCopy /></el-icon>
                复制
              </el-button>
              <el-button class="flex-1" type="primary" @click="applyCronToTask">
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
              :options="{
                minimap: { enabled: false },
                fontSize: 13,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
                tabSize: 4,
                wordWrap: 'on',
                padding: { top: 8 },
                height: '200px'
              }"
            />
          </div>

          <el-button
            class="mt-4 w-full"
            type="warning"
            @click="reviewCodeFn"
            :loading="aiReviewing"
            :disabled="!reviewCode.trim()"
          >
            <el-icon v-if="!aiReviewing"><MagicStick /></el-icon>
            {{ aiReviewing ? '审查中...' : '开始审查' }}
          </el-button>

          <!-- Review Result -->
          <el-alert v-if="reviewResult" :title="'审查结果'" type="info" :closable="true" class="mt-4">
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
            @click="diagnoseError"
            :loading="aiDiagnosing"
            :disabled="!errorInput.trim()"
          >
            <el-icon v-if="!aiDiagnosing"><MagicStick /></el-icon>
            {{ aiDiagnosing ? '诊断中...' : '开始诊断' }}
          </el-button>

          <!-- Diagnosis Result -->
          <el-alert v-if="diagnosisResult" :title="'诊断结果'" type="error" :closable="true" class="mt-4">
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
        placeholder="粘贴日志内容...
支持多行日志、错误堆栈等"
      />

      <el-button
        class="mt-4"
        type="success"
        @click="summarizeLog"
        :loading="aiSummarizing"
        :disabled="!logInput.trim()"
      >
        <el-icon v-if="!aiSummarizing"><MagicStick /></el-icon>
        {{ aiSummarizing ? '分析中...' : '生成摘要' }}
      </el-button>

      <!-- Summary Result -->
      <el-alert v-if="logSummary" :title="'日志摘要'" type="success" :closable="true" class="mt-4">
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
import { aiApi } from '../utils/api.js'

const aiEnabled = ref(false)

// Text to Script
const scriptPrompt = ref('')
const generatedScript = ref('')
const aiGenerating = ref(false)

// NLP to Cron
const cronPrompt = ref('')
const cronResult = ref(null)
const aiCronConverting = ref(false)

// Code Review
const reviewCode = ref('')
const reviewResult = ref('')
const aiReviewing = ref(false)

// Error Diagnosis
const errorInput = ref('')
const errorCode = ref('')
const diagnosisResult = ref('')
const aiDiagnosing = ref(false)

// Log Summary
const logInput = ref('')
const logSummary = ref('')
const aiSummarizing = ref(false)

async function checkAIStatus() {
  try {
    const res = await aiApi.capabilities()
    aiEnabled.value = res.data.ai_enabled
  } catch (e) {
    aiEnabled.value = false
  }
}

async function generateScript() {
  if (!scriptPrompt.value.trim() || aiGenerating.value) return
  aiGenerating.value = true
  try {
    const res = await aiApi.generateScript(scriptPrompt.value)
    if (!res.data.used_ai) {
      ElMessage.warning('AI服务未配置，请前往「系统设置」→「AI设置」配置')
    }
    generatedScript.value = res.data.code
    ElMessage.success('代码生成成功')
  } catch (e) {
    ElMessage.error('生成失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiGenerating.value = false
  }
}

function copyScript() {
  navigator.clipboard.writeText(generatedScript.value)
  ElMessage.success('已复制到剪贴板')
}

function saveScriptAsTask() {
  window.location.href = '/tasks?script=' + encodeURIComponent(generatedScript.value)
}

async function convertCron() {
  if (!cronPrompt.value.trim() || aiCronConverting.value) return
  aiCronConverting.value = true
  try {
    const res = await aiApi.nlpToCron(cronPrompt.value)
    if (!res.data.used_ai) {
      ElMessage.warning('AI服务未配置，请前往「系统设置」→「AI设置」配置')
    }
    cronResult.value = {
      expr: res.data.cron_expr,
      description: res.data.description
    }
    ElMessage.success('Cron 表达式转换成功')
  } catch (e) {
    ElMessage.error('转换失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiCronConverting.value = false
  }
}

function copyCron() {
  if (cronResult.value) {
    navigator.clipboard.writeText(cronResult.value.expr)
    ElMessage.success('已复制到剪贴板')
  }
}

function applyCronToTask() {
  window.location.href = '/tasks?cron=' + encodeURIComponent(cronResult.value?.expr || '')
}

async function reviewCodeFn() {
  if (!reviewCode.value.trim() || aiReviewing.value) return
  aiReviewing.value = true
  try {
    const res = await aiApi.codeReview(reviewCode.value)
    if (!res.data.used_ai) {
      ElMessage.warning('AI服务未配置，请前往「系统设置」→「AI设置」配置')
    }
    reviewResult.value = res.data.review
    ElMessage.success('代码审查完成')
  } catch (e) {
    ElMessage.error('审查失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiReviewing.value = false
  }
}

async function diagnoseError() {
  if (!errorInput.value.trim() || aiDiagnosing.value) return
  aiDiagnosing.value = true
  try {
    const res = await aiApi.diagnoseError(errorInput.value, errorCode.value)
    if (!res.data.used_ai) {
      ElMessage.warning('AI服务未配置，请前往「系统设置」→「AI设置」配置')
    }
    diagnosisResult.value = res.data.diagnosis
    ElMessage.success('错误诊断完成')
  } catch (e) {
    ElMessage.error('诊断失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiDiagnosing.value = false
  }
}

async function summarizeLog() {
  if (!logInput.value.trim() || aiSummarizing.value) return
  aiSummarizing.value = true
  try {
    const res = await aiApi.summarizeLog(logInput.value)
    if (!res.data.used_ai) {
      ElMessage.warning('AI服务未配置，请前往「系统设置」→「AI设置」配置')
    }
    logSummary.value = res.data.summary
    ElMessage.success('日志摘要生成成功')
  } catch (e) {
    ElMessage.error('摘要生成失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiSummarizing.value = false
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
  gap: 12px;
}

.tool-card {
  height: 100%;
  margin-bottom: 16px;
}

.code-preview {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 16px;
  max-height: 300px;
  overflow: auto;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
}

.code-preview pre {
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--text-main);
  margin: 0;
}

.editor-wrapper {
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  overflow: hidden;
}
</style>
