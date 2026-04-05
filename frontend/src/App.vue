<template>
  <el-config-provider :theme="isDark ? 'dark' : 'light'">
    <el-container class="app-container theme-transition">
      <!-- Sidebar -->
      <el-aside
        class="app-sidebar"
        :style="{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)' }"
      >
        <!-- Logo -->
        <div class="sidebar-logo" :style="{ borderBottom: '1px solid var(--border-subtle)' }">
          <h1 class="text-xl font-bold tracking-tight">
            <span style="color: var(--color-primary);">Py</span>Cron<span style="color: var(--color-primary);">Master</span>
          </h1>
          <p class="text-xs mt-1.5 tracking-wide" style="color: var(--text-muted);">脚本定时管理平台</p>
        </div>

        <!-- Navigation Menu -->
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu"
          :background-color="'transparent'"
          :text-color="'var(--text-muted)'"
          :active-text-color="'var(--color-primary)'"
          :router="true"
          :collapse="isSidebarCollapsed"
        >
          <el-menu-item index="/">
            <el-icon><PieChart /></el-icon>
            <template #title>仪表盘</template>
          </el-menu-item>
          <el-menu-item index="/tasks">
            <el-icon><List /></el-icon>
            <template #title>任务管理</template>
          </el-menu-item>
          <el-menu-item index="/logs">
            <el-icon><Document /></el-icon>
            <template #title>日志中心</template>
          </el-menu-item>
          <el-menu-item index="/ai">
            <el-icon><MagicStick /></el-icon>
            <template #title>AI 助手</template>
          </el-menu-item>
          <el-menu-item index="/flows">
            <el-icon><Connection /></el-icon>
            <template #title>节点编排</template>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <template #title>系统设置</template>
          </el-menu-item>
        </el-menu>

        <!-- Quick Scratchpad Button -->
        <div class="sidebar-footer" :style="{ borderTop: '1px solid var(--border-subtle)' }">
          <el-button class="scratchpad-btn" @click="showScratchpad = true">
            <el-icon><Cpu /></el-icon>
            <span>快速执行代码</span>
          </el-button>
        </div>
      </el-aside>

      <!-- Main Content -->
      <el-container class="main-container">
        <!-- Header -->
        <el-header class="app-header" :style="{ backgroundColor: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)' }">
          <div class="header-left">
            <div class="header-indicator"></div>
            <span class="text-sm font-medium" :style="{ color: 'var(--text-muted)' }">{{ pageTitle }}</span>
          </div>
          <div class="header-right">
            <ThemeSwitcher @change="onThemeChange" />
            <el-button :icon="Refresh" circle @click="refreshData" :loading="refreshing" />
          </div>
        </el-header>

        <!-- Page Content -->
        <el-main class="app-main" :style="{ backgroundColor: 'var(--bg-primary)' }">
          <router-view @openScratchpad="showScratchpad = true" />
        </el-main>
      </el-container>
    </el-container>

    <!-- Scratchpad Modal -->
    <Scratchpad :show="showScratchpad" @close="showScratchpad = false" />
  </el-config-provider>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { List, Document, MagicStick, Connection, Setting, Refresh, Cpu, PieChart } from '@element-plus/icons-vue'
import ThemeSwitcher from './components/ThemeSwitcher.vue'
import Scratchpad from './components/Scratchpad.vue'

const route = useRoute()
const api = axios.create({ baseURL: 'http://localhost:8000' })

const refreshing = ref(false)
const backendOnline = ref(false)
const runningTaskCount = ref(0)
const showScratchpad = ref(false)
const isSidebarCollapsed = ref(false)
const isDark = ref(false)

const pageTitle = computed(() => {
  const titles = {
    Dashboard: '仪表盘概览',
    Tasks: '任务管理',
    Logs: '日志中心',
    AIAssistant: 'AI 助手',
    Flows: '节点编排',
    Settings: '系统设置'
  }
  return titles[route.name] || '仪表盘概览'
})

function onThemeChange(themeId) {
  // Check if dark theme
  const darkThemes = ['darcula', 'onedark', 'gruvbox']
  isDark.value = darkThemes.includes(themeId)
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
  // Check initial dark mode state
  const savedTheme = localStorage.getItem('pycron-theme')
  const darkThemes = ['darcula', 'onedark', 'gruvbox']
  isDark.value = savedTheme ? darkThemes.includes(savedTheme) : true

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
.app-container {
  height: 100vh;
  overflow: hidden;
}

.app-sidebar {
  width: 240px !important;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-subtle);
  transition: background-color var(--transition-slow), border-color var(--transition-slow);
}

.sidebar-logo {
  padding: var(--space-lg);
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
  padding: var(--space-sm);
}

.sidebar-menu .el-menu-item {
  border-radius: var(--radius-md);
  margin: 2px 0;
  height: 44px;
}

.sidebar-menu .el-menu-item:hover {
  background-color: var(--bg-hover) !important;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: var(--color-primary-subtle) !important;
}

.sidebar-footer {
  padding: var(--space-md);
}

.scratchpad-btn {
  width: 100%;
  justify-content: flex-start;
  padding-left: var(--space-md);
  background-color: transparent !important;
  border: none !important;
  color: var(--text-muted) !important;
}

.scratchpad-btn:hover {
  background-color: var(--bg-hover) !important;
  color: var(--text-main) !important;
}

.main-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.app-header {
  height: 56px !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-lg);
  backdrop-filter: blur(8px);
  transition: background-color var(--transition-slow), border-color var(--transition-slow);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.header-indicator {
  width: 2rem;
  height: 4px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--color-primary), var(--color-success));
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.app-main {
  padding: var(--space-lg);
  overflow-y: auto;
  transition: background-color var(--transition-slow);
}

.theme-transition {
  transition: background-color var(--transition-slow), color var(--transition-slow), border-color var(--transition-slow);
}
</style>
