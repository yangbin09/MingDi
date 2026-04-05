<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--text-main);">AI 助手</h1>
        <p class="text-sm mt-1" style="color: var(--text-muted);">智能代码生成、审查与诊断工具</p>
      </div>
      <div class="flex items-center gap-2">
        <span
          class="px-3 py-1 text-xs font-medium rounded-full"
          :style="aiEnabled
            ? { backgroundColor: 'var(--color-success-subtle)', color: 'var(--color-success)' }
            : { backgroundColor: 'var(--color-warning-subtle)', color: 'var(--color-warning)' }"
        >
          {{ aiEnabled ? 'AI 已连接' : 'AI 未配置' }}
        </span>
      </div>
    </div>

    <!-- AI Tools Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Text to Script Generator -->
      <div class="card rounded-xl p-6">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center"
            :style="{ backgroundColor: 'var(--color-primary-subtle)' }"
          >
            <SparklesIcon class="w-5 h-5" style="color: var(--color-primary);" />
          </div>
          <div>
            <h3 class="font-semibold" style="color: var(--text-main);">Text-to-Script</h3>
            <p class="text-xs" style="color: var(--text-muted);">自然语言生成 Python 脚本</p>
          </div>
        </div>

        <div class="space-y-4">
          <textarea
            v-model="scriptPrompt"
            class="input min-h-24 resize-none"
            placeholder="用自然语言描述你想要实现的脚本功能...
例如：创建一个定时任务，每周一把 /data 目录下的日志文件压缩备份到 /backup"
          ></textarea>
          <button
            @click="generateScript"
            :disabled="aiGenerating || !scriptPrompt.trim()"
            class="w-full px-4 py-2.5 rounded-lg font-medium transition-all flex items-center justify-center gap-2"
            :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
            :class="{ 'opacity-50': aiGenerating }"
          >
            <SparklesIcon v-if="!aiGenerating" class="w-5 h-5" />
            <span v-if="aiGenerating" class="animate-spin">⟳</span>
            {{ aiGenerating ? '生成中...' : '生成代码' }}
          </button>
        </div>

        <!-- Generated Code Preview -->
        <div v-if="generatedScript" class="mt-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium" style="color: var(--text-muted);">生成的代码</span>
            <div class="flex gap-2">
              <button
                @click="copyScript"
                class="px-2 py-1 rounded text-xs"
                :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }"
              >
                <ClipboardDocumentIcon class="w-3 h-3" />
              </button>
              <button
                @click="saveScriptAsTask"
                class="px-2 py-1 rounded text-xs"
                :style="{ backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }"
              >
                保存为任务
              </button>
            </div>
          </div>
          <div
            class="rounded-lg p-4 font-mono text-sm overflow-auto"
            :style="{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', maxHeight: '300px' }"
          >
            <pre class="whitespace-pre-wrap" style="color: var(--text-main);">{{ generatedScript }}</pre>
          </div>
        </div>
      </div>

      <!-- NLP to Cron -->
      <div class="card rounded-xl p-6">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center"
            :style="{ backgroundColor: 'rgba(168, 85, 247, 0.15)' }"
          >
            <ClockIcon class="w-5 h-5" style="color: var(--color-purple);" />
          </div>
          <div>
            <h3 class="font-semibold" style="color: var(--text-main);">NLP to Cron</h3>
            <p class="text-xs" style="color: var(--text-muted);">自然语言转 Cron 表达式</p>
          </div>
        </div>

        <div class="space-y-4">
          <input
            v-model="cronPrompt"
            type="text"
            class="input"
            placeholder="输入时间描述...
例如：每个工作日下午5点半"
            @keyup.enter="convertCron"
          />
          <button
            @click="convertCron"
            :disabled="aiCronConverting || !cronPrompt.trim()"
            class="w-full px-4 py-2.5 rounded-lg font-medium transition-all flex items-center justify-center gap-2"
            :style="{ backgroundColor: 'var(--color-purple)', color: 'var(--text-inverse)' }"
            :class="{ 'opacity-50': aiCronConverting }"
          >
            <SparklesIcon v-if="!aiCronConverting" class="w-5 h-5" />
            <span v-if="aiCronConverting" class="animate-spin">⟳</span>
            {{ aiCronConverting ? '转换中...' : '转换为 Cron' }}
          </button>
        </div>

        <!-- Cron Result -->
        <div v-if="cronResult" class="mt-4">
          <div class="rounded-lg p-4" :style="{ backgroundColor: 'var(--color-purple-subtle)', border: '1px solid var(--color-purple)' }">
            <div class="text-center">
              <code class="text-xl font-mono font-bold" style="color: var(--color-purple);">{{ cronResult.expr }}</code>
              <p class="text-sm mt-2" style="color: var(--text-muted);">{{ cronResult.description }}</p>
            </div>
            <div class="flex gap-2 mt-3">
              <button
                @click="copyCron"
                class="flex-1 px-3 py-1.5 rounded text-sm"
                :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }"
              >
                <ClipboardDocumentIcon class="w-4 h-4 inline mr-1" />
                复制
              </button>
              <button
                @click="applyCronToTask"
                class="flex-1 px-3 py-1.5 rounded text-sm"
                :style="{ backgroundColor: 'var(--color-purple)', color: 'var(--text-inverse)' }"
              >
                应用到任务
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Code Review -->
      <div class="card rounded-xl p-6">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center"
            :style="{ backgroundColor: 'var(--color-warning-subtle)' }"
          >
            <MagnifyingGlassIcon class="w-5 h-5" style="color: var(--color-warning);" />
          </div>
          <div>
            <h3 class="font-semibold" style="color: var(--text-main);">AI 代码审查</h3>
            <p class="text-xs" style="color: var(--text-muted);">代码性能与安全检查</p>
          </div>
        </div>

        <div class="space-y-4">
          <div
            class="rounded-lg overflow-hidden"
            :style="{ border: '1px solid var(--border-subtle)' }"
          >
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
          <button
            @click="reviewCodeFn"
            :disabled="aiReviewing || !reviewCode.trim()"
            class="w-full px-4 py-2.5 rounded-lg font-medium transition-all flex items-center justify-center gap-2"
            :style="{ backgroundColor: 'var(--color-warning)', color: 'var(--text-inverse)' }"
            :class="{ 'opacity-50': aiReviewing }"
          >
            <SparklesIcon v-if="!aiReviewing" class="w-5 h-5" />
            <span v-if="aiReviewing" class="animate-spin">⟳</span>
            {{ aiReviewing ? '审查中...' : '开始审查' }}
          </button>
        </div>

        <!-- Review Result -->
        <div v-if="reviewResult" class="mt-4">
          <div class="rounded-lg p-4" :style="{ backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)' }">
            <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ reviewResult }}</pre>
          </div>
        </div>
      </div>

      <!-- Error Diagnosis -->
      <div class="card rounded-xl p-6">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center"
            :style="{ backgroundColor: 'var(--color-danger-subtle)' }"
          >
            <ExclamationTriangleIcon class="w-5 h-5" style="color: var(--color-danger);" />
          </div>
          <div>
            <h3 class="font-semibold" style="color: var(--text-main);">错误诊断</h3>
            <p class="text-xs" style="color: var(--text-muted);">智能错误分析与修复建议</p>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm mb-2" style="color: var(--text-muted);">错误信息 / Traceback</label>
            <textarea
              v-model="errorInput"
              class="input min-h-32 font-mono text-sm resize-none"
              placeholder="粘贴错误信息或 traceback..."
            ></textarea>
          </div>
          <div>
            <label class="block text-sm mb-2" style="color: var(--text-muted);">相关代码 (可选)</label>
            <textarea
              v-model="errorCode"
              class="input min-h-20 font-mono text-sm resize-none"
              placeholder="粘贴相关代码片段..."
            ></textarea>
          </div>
          <button
            @click="diagnoseError"
            :disabled="aiDiagnosing || !errorInput.trim()"
            class="w-full px-4 py-2.5 rounded-lg font-medium transition-all flex items-center justify-center gap-2"
            :style="{ backgroundColor: 'var(--color-danger)', color: 'var(--text-inverse)' }"
            :class="{ 'opacity-50': aiDiagnosing }"
          >
            <SparklesIcon v-if="!aiDiagnosing" class="w-5 h-5" />
            <span v-if="aiDiagnosing" class="animate-spin">⟳</span>
            {{ aiDiagnosing ? '诊断中...' : '开始诊断' }}
          </button>
        </div>

        <!-- Diagnosis Result -->
        <div v-if="diagnosisResult" class="mt-4">
          <div class="rounded-lg p-4" :style="{ backgroundColor: 'var(--color-danger-subtle)', border: '1px solid var(--color-danger)' }">
            <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ diagnosisResult }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Log Diagnosis Section -->
    <div class="card rounded-xl p-6">
      <div class="flex items-center gap-3 mb-4">
        <div
          class="w-10 h-10 rounded-lg flex items-center justify-center"
          :style="{ backgroundColor: 'var(--color-success-subtle)' }"
        >
          <DocumentTextIcon class="w-5 h-5" style="color: var(--color-success);" />
        </div>
        <div>
          <h3 class="font-semibold" style="color: var(--text-main);">日志摘要</h3>
          <p class="text-xs" style="color: var(--text-muted);">粘贴日志内容，AI 将提炼关键信息</p>
        </div>
      </div>

      <div class="space-y-4">
        <textarea
          v-model="logInput"
          class="input min-h-40 font-mono text-sm resize-none"
          placeholder="粘贴日志内容...
支持多行日志、错误堆栈等"
        ></textarea>
        <button
          @click="summarizeLog"
          :disabled="aiSummarizing || !logInput.trim()"
          class="px-6 py-2.5 rounded-lg font-medium transition-all flex items-center justify-center gap-2"
          :style="{ backgroundColor: 'var(--color-success)', color: 'var(--text-inverse)' }"
          :class="{ 'opacity-50': aiSummarizing }"
        >
          <SparklesIcon v-if="!aiSummarizing" class="w-5 h-5" />
          <span v-if="aiSummarizing" class="animate-spin">⟳</span>
          {{ aiSummarizing ? '分析中...' : '生成摘要' }}
        </button>
      </div>

      <!-- Summary Result -->
      <div v-if="logSummary" class="mt-4">
        <div class="rounded-lg p-4" :style="{ backgroundColor: 'var(--color-success-subtle)', border: '1px solid var(--color-success)' }">
          <pre class="text-sm whitespace-pre-wrap" style="color: var(--text-main);">{{ logSummary }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  SparklesIcon, ClockIcon, MagnifyingGlassIcon,
  ExclamationTriangleIcon, DocumentTextIcon,
  ClipboardDocumentIcon
} from '@heroicons/vue/24/outline'
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
    generatedScript.value = res.data.code
  } catch (e) {
    alert('生成失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiGenerating.value = false
  }
}

function copyScript() {
  navigator.clipboard.writeText(generatedScript.value)
}

function saveScriptAsTask() {
  // Navigate to tasks page with pre-filled script
  window.location.href = '/tasks?script=' + encodeURIComponent(generatedScript.value)
}

async function convertCron() {
  if (!cronPrompt.value.trim() || aiCronConverting.value) return
  aiCronConverting.value = true
  try {
    const res = await aiApi.nlpToCron(cronPrompt.value)
    cronResult.value = {
      expr: res.data.cron_expr,
      description: res.data.description
    }
  } catch (e) {
    alert('转换失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiCronConverting.value = false
  }
}

function copyCron() {
  if (cronResult.value) {
    navigator.clipboard.writeText(cronResult.value.expr)
  }
}

function applyCronToTask() {
  // Navigate to tasks page with pre-set cron
  window.location.href = '/tasks?cron=' + encodeURIComponent(cronResult.value?.expr || '')
}

async function reviewCodeFn() {
  if (!reviewCode.value.trim() || aiReviewing.value) return
  aiReviewing.value = true
  try {
    const res = await aiApi.codeReview(reviewCode.value)
    reviewResult.value = res.data.review
  } catch (e) {
    alert('审查失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiReviewing.value = false
  }
}

async function diagnoseError() {
  if (!errorInput.value.trim() || aiDiagnosing.value) return
  aiDiagnosing.value = true
  try {
    const res = await aiApi.diagnoseError(errorInput.value, errorCode.value)
    diagnosisResult.value = res.data.diagnosis
  } catch (e) {
    alert('诊断失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiDiagnosing.value = false
  }
}

async function summarizeLog() {
  if (!logInput.value.trim() || aiSummarizing.value) return
  aiSummarizing.value = true
  try {
    const res = await aiApi.summarizeLog(logInput.value)
    logSummary.value = res.data.summary
  } catch (e) {
    alert('摘要生成失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiSummarizing.value = false
  }
}

onMounted(() => {
  checkAIStatus()
})
</script>
