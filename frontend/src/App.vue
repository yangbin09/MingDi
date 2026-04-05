<template>
  <div class="flex h-screen bg-gray-950 text-gray-100 noise-overlay">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-900 border-r border-gray-700/50 flex flex-col relative">
      <!-- Subtle gradient overlay -->
      <div class="absolute inset-0 bg-gradient-to-b from-indigo-500/5 via-transparent to-emerald-500/3 pointer-events-none"></div>

      <!-- Breathing glow effect when tasks running -->
      <div v-if="hasRunningTasks" class="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-emerald-500/5 animate-pulse-soft pointer-events-none"></div>

      <!-- Logo -->
      <div class="p-6 border-b border-gray-700/50 relative z-10">
        <h1 class="text-xl font-bold tracking-tight">
          <span class="text-indigo-400">Py</span>Cron<span class="text-indigo-400">Master</span>
        </h1>
        <p class="text-xs text-gray-500 mt-1.5 tracking-wide">脚本定时管理平台</p>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 relative z-10">
        <ul class="space-y-1">
          <li v-for="item in navItems" :key="item.path">
            <router-link
              :to="item.path"
              class="flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group"
              :class="[$route.path === item.path
                ? 'bg-indigo-500/10 text-indigo-400 border-l-2 border-indigo-500 -ml-[2px] pl-[18px]'
                : 'text-gray-400 hover:bg-gray-800/80 hover:text-gray-200 border-l-2 border-transparent']"
            >
              <component :is="item.icon" class="w-5 h-5 transition-transform group-hover:scale-110" />
              <span class="font-medium">{{ item.label }}</span>
              <span v-if="item.path === '/' && runningTaskCount > 0" class="ml-auto flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-emerald-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
            </router-link>
          </li>
        </ul>

        <!-- Quick Scratchpad Button -->
        <div class="mt-6 pt-6 border-t border-gray-700/50">
          <button
            @click="showScratchpad = true"
            class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 text-gray-400 hover:bg-purple-500/10 hover:text-purple-400 group border border-transparent hover:border-purple-500/20"
          >
            <CodeBracketIcon class="w-5 h-5" />
            <span class="font-medium">快速执行代码</span>
          </button>
        </div>
      </nav>

      <!-- Sidebar Footer -->
      <div class="p-4 border-t border-gray-700/50 relative z-10">
        <div class="flex items-center justify-between text-xs">
          <div class="space-y-1">
            <p class="text-gray-500">
              Backend: <span :class="backendOnline ? 'text-emerald-400' : 'text-rose-400'">{{ backendOnline ? 'Online' : 'Offline' }}</span>
            </p>
            <p class="text-gray-600">v1.0.0</p>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="relative flex h-2 w-2">
              <span v-if="backendOnline" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span :class="backendOnline ? 'bg-emerald-500' : 'bg-rose-500'" class="relative inline-flex rounded-full h-2 w-2 shadow-softer"></span>
            </span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <header class="h-16 bg-gray-900/80 backdrop-blur-sm border-b border-gray-700/50 flex items-center justify-between px-6 sticky top-0 z-20">
        <div class="flex items-center gap-3">
          <div class="h-1 w-8 bg-gradient-to-r from-indigo-500 to-emerald-500 rounded-full"></div>
          <span class="text-sm font-medium text-gray-300">{{ pageTitle }}</span>
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="refreshData"
            class="p-2 text-gray-400 hover:text-gray-200 hover:bg-gray-800 rounded-lg transition-all duration-200"
            title="刷新数据"
          >
            <ArrowPathIcon class="w-5 h-5" :class="{'animate-spin': refreshing}" />
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-auto p-6 bg-gradient-to-b from-gray-950 to-gray-900/50">
        <router-view @openScratchpad="showScratchpad = true" />
      </main>
    </div>

    <!-- Scratchpad Modal -->
    <Scratchpad :show="showScratchpad" @close="showScratchpad = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, markRaw } from 'vue'
import axios from 'axios'
import {
  ChartBarIcon,
  ListBulletIcon,
  Cog6ToothIcon,
  ArrowPathIcon,
  CodeBracketIcon
} from '@heroicons/vue/24/outline'
import Scratchpad from './components/Scratchpad.vue'

const api = axios.create({ baseURL: 'http://localhost:8000' })

const refreshing = ref(false)
const backendOnline = ref(false)
const runningTaskCount = ref(0)
const showScratchpad = ref(false)

const navItems = [
  { path: '/', name: 'Dashboard', label: '仪表盘', icon: markRaw(ChartBarIcon) },
  { path: '/tasks', name: 'Tasks', label: '任务管理', icon: markRaw(ListBulletIcon) },
  { path: '/settings', name: 'Settings', label: '系统设置', icon: markRaw(Cog6ToothIcon) },
]

const pageTitle = computed(() => {
  const titles = { Dashboard: '仪表盘概览', Tasks: '任务管理', Settings: '系统设置' }
  return titles[this?.$route?.name] || '仪表盘概览'
})

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
.animate-pulse-soft {
  animation: pulse-soft 3s ease-in-out infinite;
}
</style>
