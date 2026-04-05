<template>
  <div class="flex h-screen theme-transition" style="background-color: var(--bg-primary);">
    <!-- Sidebar -->
    <aside
      class="w-64 flex flex-col relative theme-transition"
      :style="{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)' }"
    >
      <!-- Breathing glow effect when tasks running -->
      <div
        v-if="hasRunningTasks"
        class="absolute inset-0 animate-pulse-soft pointer-events-none"
        :style="{ background: 'linear-gradient(90deg, var(--color-primary-subtle), transparent)' }"
      ></div>

      <!-- Logo -->
      <div class="p-6 relative z-10 theme-transition" :style="{ borderBottom: '1px solid var(--border-subtle)' }">
        <h1 class="text-xl font-bold tracking-tight">
          <span style="color: var(--color-primary);">Py</span>Cron<span style="color: var(--color-primary);">Master</span>
        </h1>
        <p class="text-xs mt-1.5 tracking-wide" style="color: var(--text-muted);">脚本定时管理平台</p>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 relative z-10">
        <ul class="space-y-1">
          <li v-for="item in navItems" :key="item.path">
            <router-link
              :to="item.path"
              class="flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group"
              :style="$route.path === item.path
                ? {
                    backgroundColor: 'var(--color-primary-subtle)',
                    color: 'var(--color-primary)',
                    borderLeft: '2px solid var(--color-primary)',
                    paddingLeft: '16px'
                  }
                : {
                    color: 'var(--text-muted)',
                    borderLeft: '2px solid transparent'
                  }"
            >
              <component
                :is="item.icon"
                class="w-5 h-5 transition-transform group-hover:scale-110"
              />
              <span class="font-medium">{{ item.label }}</span>
              <span v-if="item.path === '/' && runningTaskCount > 0" class="ml-auto flex h-2 w-2">
                <span
                  class="animate-ping absolute inline-flex h-2 w-2 rounded-full opacity-75"
                  :style="{ backgroundColor: 'var(--color-primary)' }"
                ></span>
                <span
                  class="relative inline-flex rounded-full h-2 w-2"
                  :style="{ backgroundColor: 'var(--color-primary)' }"
                ></span>
              </span>
            </router-link>
          </li>
        </ul>

        <!-- Quick Scratchpad Button -->
        <div class="mt-6 pt-6" :style="{ borderTop: '1px solid var(--border-subtle)' }">
          <button
            @click="showScratchpad = true"
            class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group"
            :style="{ color: 'var(--text-muted)' }"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)', $event.currentTarget.style.color = 'var(--text-main)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent', $event.currentTarget.style.color = 'var(--text-muted)')"
          >
            <CodeBracketIcon class="w-5 h-5" />
            <span class="font-medium">快速执行代码</span>
          </button>
        </div>
      </nav>

      <!-- Sidebar Footer -->
      <div class="p-4 relative z-10 theme-transition" :style="{ borderTop: '1px solid var(--border-subtle)' }">
        <div class="flex items-center justify-between text-xs">
          <div class="space-y-1">
            <p :style="{ color: 'var(--text-muted)' }">
              Backend: <span :style="{ color: backendOnline ? 'var(--color-success)' : 'var(--color-danger)' }">{{ backendOnline ? 'Online' : 'Offline' }}</span>
            </p>
            <p :style="{ color: 'var(--text-disabled)' }">v1.0.0</p>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="relative flex h-2 w-2">
              <span
                v-if="backendOnline"
                class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                :style="{ backgroundColor: 'var(--color-success)' }"
              ></span>
              <span
                class="relative inline-flex rounded-full h-2 w-2"
                :style="{ backgroundColor: backendOnline ? 'var(--color-success)' : 'var(--color-danger)' }"
              ></span>
            </span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <header
        class="h-14 flex items-center justify-between px-6 sticky top-0 z-20 backdrop-blur-sm theme-transition"
        :style="{ backgroundColor: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)' }"
      >
        <div class="flex items-center gap-3">
          <div
            class="h-1 w-8 rounded-full"
            :style="{ background: 'linear-gradient(90deg, var(--color-primary), var(--color-success))' }"
          ></div>
          <span class="text-sm font-medium" :style="{ color: 'var(--text-muted)' }">{{ pageTitle }}</span>
        </div>
        <div class="flex items-center gap-3">
          <!-- Theme Switcher -->
          <ThemeSwitcher @change="onThemeChange" />

          <button
            @click="refreshData"
            class="p-2 rounded-lg transition-colors"
            :style="{ color: 'var(--text-muted)' }"
            title="刷新数据"
            @mouseenter="($event.currentTarget.style.color = 'var(--text-main)', $event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
            @mouseleave="($event.currentTarget.style.color = 'var(--text-muted)', $event.currentTarget.style.backgroundColor = 'transparent')"
          >
            <ArrowPathIcon class="w-5 h-5" :class="{'animate-spin': refreshing}" />
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <main
        class="flex-1 overflow-auto p-6 theme-transition"
        :style="{ backgroundColor: 'var(--bg-primary)' }"
      >
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
  ChartBarIcon,
  ListBulletIcon,
  Cog6ToothIcon,
  ArrowPathIcon,
  CodeBracketIcon
} from '@heroicons/vue/24/outline'
import ThemeSwitcher from './components/ThemeSwitcher.vue'
import Scratchpad from './components/Scratchpad.vue'

const api = axios.create({ baseURL: 'http://localhost:8000' })

const refreshing = ref(false)
const backendOnline = ref(false)
const runningTaskCount = ref(0)
const showScratchpad = ref(false)

const navItems = [
  { path: '/', name: 'Dashboard', label: '仪表盘', icon: ChartBarIcon },
  { path: '/tasks', name: 'Tasks', label: '任务管理', icon: ListBulletIcon },
  { path: '/settings', name: 'Settings', label: '系统设置', icon: Cog6ToothIcon },
]

const pageTitle = computed(() => {
  const titles = { Dashboard: '仪表盘概览', Tasks: '任务管理', Settings: '系统设置' }
  return titles[this?.$route?.name] || '仪表盘概览'
})

const hasRunningTasks = computed(() => runningTaskCount.value > 0)

function onThemeChange(themeId) {
  console.log('Theme changed to:', themeId)
}

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

@keyframes pulse-soft {
  0%, 100% { opacity: 0.03; }
  50% { opacity: 0.08; }
}
</style>
