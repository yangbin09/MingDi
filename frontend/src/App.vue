<template>
  <div class="flex h-screen bg-gray-950 text-gray-100">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      <!-- Logo -->
      <div class="p-6 border-b border-gray-800">
        <h1 class="text-xl font-bold tracking-wider">
          <span class="text-emerald-400">Py</span>Cron<span class="text-emerald-400">Master</span>
        </h1>
        <p class="text-xs text-gray-500 mt-1">脚本定时管理平台</p>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4">
        <ul class="space-y-2">
          <li>
            <router-link
              to="/"
              class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200"
              :class="[$route.path === '/' ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 hover:bg-gray-800 hover:text-white']"
            >
              <ChartBarIcon class="w-5 h-5" />
              <span>仪表盘</span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/tasks"
              class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200"
              :class="[$route.path === '/tasks' ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 hover:bg-gray-800 hover:text-white']"
            >
              <ListBulletIcon class="w-5 h-5" />
              <span>任务管理</span>
            </router-link>
          </li>
        </ul>
      </nav>

      <!-- Sidebar Footer -->
      <div class="p-4 border-t border-gray-800">
        <div class="text-xs text-gray-500">
          <p>Backend: <span class="text-emerald-400">Online</span></p>
          <p class="mt-1">v1.0.0</p>
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
        </div>
        <div class="flex items-center gap-4">
          <button
            @click="refreshData"
            class="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition"
            title="刷新数据"
          >
            <ArrowPathIcon class="w-5 h-5" :class="{'animate-spin': refreshing}" />
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-auto p-6 bg-gray-950">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  ChartBarIcon,
  ListBulletIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

const refreshing = ref(false)

const refreshData = () => {
  refreshing.value = true
  setTimeout(() => {
    refreshing.value = false
  }, 1000)
  window.location.reload()
}
</script>
