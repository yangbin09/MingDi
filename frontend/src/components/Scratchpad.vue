<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="close"></div>
      <div class="absolute inset-4 md:inset-8 lg:inset-16 bg-gray-900 border border-gray-700/50 rounded-2xl flex flex-col shadow-2xl">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700/50">
          <div class="flex items-center gap-3">
            <div class="flex gap-1.5">
              <div class="w-3 h-3 rounded-full bg-rose-500"></div>
              <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div class="w-3 h-3 rounded-full bg-emerald-500"></div>
            </div>
            <span class="text-lg font-semibold text-gray-100">Python Scratchpad</span>
            <span class="text-xs px-2 py-1 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">临时执行</span>
          </div>
          <button @click="close" class="p-2 hover:bg-gray-800 rounded-lg transition-colors">
            <XMarkIcon class="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 flex flex-col md:flex-row overflow-hidden">
          <!-- Editor -->
          <div class="flex-1 flex flex-col border-r border-gray-700/50">
            <div class="bg-gray-800/80 px-4 py-2 text-xs text-gray-400 flex items-center justify-between border-b border-gray-700/50">
              <span>Python 3 Editor</span>
              <div class="flex items-center gap-2">
                <label class="flex items-center gap-1 text-xs">
                  <span class="text-gray-500">venv:</span>
                  <select v-model="interpreterPath" class="bg-gray-700 text-xs px-2 py-1 rounded border border-gray-600 focus:outline-none focus:border-indigo-500">
                    <option value="">系统默认</option>
                    <option v-for="venv in venvs" :key="venv" :value="venv">{{ venv }}</option>
                  </select>
                </label>
              </div>
            </div>
            <div class="flex-1">
              <vue-monaco-editor
                v-model:value="code"
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
              />
            </div>
          </div>

          <!-- Output -->
          <div class="w-full md:w-1/2 flex flex-col bg-gray-950">
            <div class="bg-gray-800/80 px-4 py-2 text-xs text-gray-400 border-b border-gray-700/50 flex items-center justify-between">
              <span>Output</span>
              <div v-if="executionTime" class="text-emerald-400 font-mono">
                执行时间: {{ executionTime }}s
              </div>
            </div>
            <div ref="outputArea" class="flex-1 overflow-auto p-5 font-mono text-sm">
              <div v-if="!running && !output" class="text-gray-500">
                <p class="text-sm">// 输出结果将显示在这里</p>
                <p class="text-emerald-500/70 mt-2 text-sm">// 点击 "运行" 按钮执行代码</p>
              </div>
              <div v-else-if="running" class="text-gray-400">
                <span class="inline-block w-2 h-4 bg-emerald-400 animate-pulse"></span> 执行中...
              </div>
              <pre v-else class="whitespace-pre-wrap text-gray-300 leading-relaxed">{{ output }}</pre>
              <div v-if="exitCode !== null && !running" class="mt-4 pt-4 border-t border-gray-800">
                <span
                  class="px-2 py-1 rounded text-xs font-medium"
                  :class="exitCode === 0
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'"
                >
                  exit {{ exitCode }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between px-6 py-4 border-t border-gray-700/50 bg-gray-900/50">
          <div class="text-xs text-gray-500">
            提示: 代码将在临时文件中执行，超时时间 60 秒
          </div>
          <div class="flex gap-3">
            <button
              @click="clear"
              class="px-4 py-2 border border-gray-700/50 rounded-lg hover:bg-gray-800 transition-all text-gray-400 hover:text-gray-200"
            >
              清空
            </button>
            <button
              @click="run"
              :disabled="running || !code.trim()"
              class="px-6 py-2 bg-indigo-500 hover:bg-indigo-600 text-white font-medium rounded-lg transition-all shadow-soft disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ running ? '运行中...' : '▶ 运行' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({ show: Boolean })
const emit = defineEmits(['close'])

const api = axios.create({ baseURL: 'http://localhost:8000' })

const code = ref(`print("Hello from Scratchpad!")
print("Quick Python execution")

# Try some code:
result = sum(range(1, 101))
print(f"Sum 1-100 = {result}")
`)
const interpreterPath = ref('')
const output = ref('')
const running = ref(false)
const exitCode = ref(null)
const executionTime = ref(null)
const outputArea = ref(null)
const venvs = ref([])

async function fetchVenvs() {
  // Placeholder for venv discovery
}

async function run() {
  if (!code.value.trim() || running.value) return

  running.value = true
  output.value = ''
  exitCode.value = null
  executionTime.value = null

  try {
    const res = await api.post('/scratchpad', {
      code: code.value,
      interpreter_path: interpreterPath.value || null
    })
    output.value = res.data.output
    exitCode.value = res.data.exit_code
    executionTime.value = res.data.execution_time
  } catch (e) {
    output.value = 'Error: ' + (e.response?.data?.detail || e.message)
    exitCode.value = -1
  } finally {
    running.value = false
  }
}

function clear() {
  code.value = ''
  output.value = ''
  exitCode.value = null
  executionTime.value = null
}

function close() {
  emit('close')
}

watch(() => props.show, (val) => {
  if (val) fetchVenvs()
})
</script>
