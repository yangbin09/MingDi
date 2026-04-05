<template>
  <el-drawer
    v-model="visible"
    :title="'日志查看 - ' + (task?.name || '')"
    size="700px"
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
        @click="handleSummarize"
        :loading="aiSummarizing"
        type="primary"
        plain
      >
        <el-icon><MagicStick /></el-icon>
        AI摘要
      </el-button>
      <el-button @click="handleDownload">
        <el-icon><Download /></el-icon>
      </el-button>
      <el-button type="primary" @click="handleRun">
        <el-icon><VideoPlay /></el-icon>
        运行
      </el-button>
    </div>

    <!-- AI Log Summary -->
    <el-alert
      v-if="aiLogSummary"
      title="AI 日志摘要"
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
      title="AI 错误诊断"
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
        <span style="color: var(--color-primary);">pycron</span>:<span style="color: var(--color-success);">~</span>$ python {{ task?.script_path }}
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
              @click="handleDiagnose(log)"
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
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, Download, VideoPlay } from '@element-plus/icons-vue'
import { useAI } from '../../composables/useAI.js'

const props = defineProps({
  modelValue: Boolean,
  task: Object,
  logs: Array
})

const emit = defineEmits(['update:modelValue', 'run', 'refresh', 'download'])

const { summarizeLog, diagnoseError, aiLoading } = useAI()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const logSearch = ref('')
const logDateFilter = ref('')
const aiLogSummary = ref('')
const aiSummarizing = ref(false)
const aiErrorDiagnosis = ref('')
const aiDiagnosingLogId = ref(null)
const currentLog = ref(null)

const filteredLogs = computed(() => {
  let result = props.logs || []
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

// Watch for logs changes to set currentLog
watch(() => props.logs, (logs) => {
  if (logs && logs.length > 0) {
    currentLog.value = logs[0]
  }
}, { immediate: true })

function formatTime(timeStr) {
  if (!timeStr) return '-'
  const d = new Date(timeStr)
  return d.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function highlightKeyword(text) {
  if (!logSearch.value) return text
  const kw = logSearch.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${kw})`, 'gi'), '<mark style="background-color: var(--color-warning-subtle); color: var(--color-warning); padding: 0 2px; border-radius: 2px;">$1</mark>')
}

async function handleSummarize() {
  if (!currentLog.value?.output || aiSummarizing.value) return
  aiSummarizing.value = true
  try {
    const result = await summarizeLog(currentLog.value.output)
    aiLogSummary.value = result.summary
  } catch (e) {
    console.error('AI 摘要失败:', e)
  } finally {
    aiSummarizing.value = false
  }
}

async function handleDiagnose(log) {
  if (aiDiagnosingLogId.value) return
  aiDiagnosingLogId.value = log.id
  aiErrorDiagnosis.value = null
  try {
    const result = await diagnoseError(log.output, '')
    aiErrorDiagnosis.value = result.diagnosis
  } catch (e) {
    console.error('AI 诊断失败:', e)
  } finally {
    aiDiagnosingLogId.value = null
  }
}

function handleDownload() {
  emit('download', { logs: filteredLogs.value, task: props.task })
}

function handleRun() {
  emit('run', props.task)
}
</script>

<style scoped>
.log-toolbar {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
  flex-wrap: wrap;
}

.log-search {
  width: 200px;
}

.log-date {
  width: 150px;
}

.terminal-content {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-base);
  line-height: var(--line-height-base);
  padding: var(--space-md);
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.terminal-prompt {
  margin-bottom: var(--space-md);
}

.log-sessions {
  margin-top: var(--space-md);
}

.log-session {
  padding-bottom: var(--space-md);
  margin-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-subtle);
}

.log-session:last-child {
  border-bottom: none;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.log-meta {
  display: flex;
  gap: var(--space-md);
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  align-items: center;
}

.log-output {
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--text-main);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-base);
}

.terminal-cursor {
  display: inline-block;
  width: 8px;
  height: 16px;
  animation: blink 1s step-end infinite;
  vertical-align: middle;
  margin-top: var(--space-sm);
}

@keyframes blink {
  50% { opacity: 0; }
}
</style>
