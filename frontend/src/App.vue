<template>
  <div class="flex h-screen bg-gray-950 text-gray-100">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-900 border-r border-gray-800 flex flex-col relative">
      <!-- Breathing glow effect when tasks running -->
      <div v-if="hasRunningTasks" class="absolute inset-0 bg-emerald-500/5 rounded-r-xl animate-pulse-slow pointer-events-none"></div>

      <!-- Logo -->
      <div class="p-6 border-b border-gray-800 relative z-10">
        <h1 class="text-xl font-bold tracking-wider">
          <span class="text-emerald-400">Py</span>Cron<span class="text-emerald-400">Master</span>
        </h1>
        <p class="text-xs text-gray-500 mt-1">脚本定时管理平台</p>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 relative z-10">
        <ul class="space-y-2">
          <li>
            <router-link to="/" class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200"
              :class="[$route.path === '/' ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 hover:bg-gray-800 hover:text-white']">
              <ChartBarIcon class="w-5 h-5" />
              <span>仪表盘</span>
              <span v-if="runningTaskCount > 0" class="ml-auto flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-emerald-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
            </router-link>
          </li>
          <li>
            <router-link to="/tasks" class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200"
              :class="[$route.path === '/tasks' ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 hover:bg-gray-800 hover:text-white']">
              <ListBulletIcon class="w-5 h-5" />
              <span>任务管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/settings" class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200"
              :class="[$route.path === '/settings' ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 hover:bg-gray-800 hover:text-white']">
              <Cog6ToothIcon class="w-5 h-5" />
              <span>系统设置</span>
            </router-link>
          </li>
        </ul>

        <!-- Quick Scratchpad Button -->
        <div class="mt-6 pt-6 border-t border-gray-800">
          <button @click="showScratchpad = true" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-gray-400 hover:bg-purple-500/10 hover:text-purple-400">
            <CodeBracketIcon class="w-5 h-5" />
            <span>快速执行代码</span>
          </button>
        </div>
      </nav>

      <!-- Sidebar Footer -->
      <div class="p-4 border-t border-gray-800 relative z-10">
        <div class="flex items-center justify-between text-xs text-gray-500">
          <div>
            <p>Backend: <span :class="backendOnline ? 'text-emerald-400' : 'text-red-400'">{{ backendOnline ? 'Online' : 'Offline' }}</span></p>
            <p class="mt-1">v1.0.0</p>
          </div>
          <div class="flex items-center gap-1">
            <span class="relative flex h-2 w-2">
              <span v-if="backendOnline" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span :class="backendOnline ? 'bg-emerald-500' : 'bg-red-500'" class="relative inline-flex rounded-full h-2 w-2"></span>
            </span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <header class="h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6">
        <div class="text-sm text-gray-400">
          <span v-if="$route.name === 'Dashboard'">仪表盘概览</span>
          <span v-else-if="$route.name === 'Tasks'">任务管理</span>
          <span v-else-if="$route.name === 'Settings'">系统设置</span>
        </div>
        <div class="flex items-center gap-4">
          <button @click="refreshData" class="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition" title="刷新数据">
            <ArrowPathIcon class="w-5 h-5" :class="{'animate-spin': refreshing}" />
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-auto p-6 bg-gray-950">
        <router-view @openScratchpad="showScratchpad = true" />
      </main>
    </div>

    <!-- Scratchpad Modal -->
    <Scratchpad :show="showScratchpad" @close="showScratchpad = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import {
  ChartBarIcon, ListBulletIcon, Cog6ToothIcon,
  ArrowPathIcon, CodeBracketIcon
} from '@heroicons/vue/24/outline'
import Scratchpad from './components/Scratchpad.vue'

const api = axios.create({ baseURL: 'http://localhost:8000' })

const refreshing = ref(false)
const backendOnline = ref(false)
const runningTaskCount = ref(0)
const showScratchpad = ref(false)

const hasRunningTasks = computed(() => runningTaskCount.value > 0)

async function checkBackend() {
  try {
    await api.get('/')
    backendOnline.value = true
  } catch {
    backendOnline.value = false
  }
}

async function fetchRunningCount() {
  try {
    const res = await api.get('/tasks')
    runningTaskCount.value = res.data.filter(t => t.status === 'running').length
  } catch { runningTaskCount.value = 0 }
}

function refreshData() {
  refreshing.value = true
  setTimeout(() => { refreshing.value = false }, 1000)
  window.location.reload()
}

let refreshInterval = null

onMounted(() => {
  checkBackend()
  fetchRunningCount()
  refreshInterval = setInterval(() => {
    checkBackend()
    fetchRunningCount()
  }, 5000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 0.03; }
  50% { opacity: 0.08; }
}
.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}
</style>
