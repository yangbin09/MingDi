<template>
  <div class="space-y-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Total Tasks -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">总任务数</p>
            <p class="text-3xl font-bold mt-2 text-white">{{ stats.total }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
            <ListBulletIcon class="w-6 h-6 text-blue-400" />
          </div>
        </div>
      </div>

      <!-- Running -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">运行中</p>
            <p class="text-3xl font-bold mt-2 text-emerald-400">{{ stats.running }}</p>
          </div>
          <div class="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
            <PlayIcon class="w-6 h-6 text-emerald-400" />
          </div>
        </div>
      </div>

      <!-- Failed Today -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">今日失败</p>
            <p class="text-3xl font-bold mt-2 text-red-400">{{ stats.failedToday }}</p>
          </div>
          <div class="w-12 h-12 bg-red-500/20 rounded-xl flex items-center justify-center">
            <ExclamationTriangleIcon class="w-6 h-6 text-red-400" />
          </div>
        </div>
      </div>

      <!-- Success Rate -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">成功率</p>
            <p class="text-3xl font-bold mt-2 text-white">{{ stats.successRate }}%</p>
          </div>
          <div class="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
            <ChartPieIcon class="w-6 h-6 text-purple-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity & Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Recent Tasks -->
      <div class="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-xl">
        <div class="p-4 border-b border-gray-800">
          <h2 class="text-lg font-semibold">最近任务</h2>
        </div>
        <div class="p-4">
          <div v-if="recentTasks.length === 0" class="text-center text-gray-500 py-8">
            暂无任务数据
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="task in recentTasks"
              :key="task.id"
              class="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
            >
              <div class="flex items-center gap-3">
                <span class="text-xl" :class="statusEmoji(task.status)"></span>
                <div>
                  <p class="font-medium">{{ task.name }}</p>
                  <p class="text-xs text-gray-500">{{ task.script_path }}</p>
                </div>
              </div>
              <div class="text-right">
                <span :class="statusClass(task.status)" class="px-2 py-1 rounded-full text-xs">
                  {{ statusText(task.status) }}
                </span>
                <p class="text-xs text-gray-500 mt-1">
                  {{ task.last_run_time ? formatTime(task.last_run_time) : '从未运行' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl">
        <div class="p-4 border-b border-gray-800">
          <h2 class="text-lg font-semibold">快捷操作</h2>
        </div>
        <div class="p-4 space-y-3">
          <router-link
            to="/tasks"
            class="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition"
          >
            <PlusIcon class="w-5 h-5 text-emerald-400" />
            <span>新建任务</span>
          </router-link>
          <button
            @click="$router.push('/tasks')"
            class="w-full flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition text-left"
          >
            <PlayIcon class="w-5 h-5 text-blue-400" />
            <span>查看所有任务</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import {
  ListBulletIcon,
  PlayIcon,
  ExclamationTriangleIcon,
  ChartPieIcon,
  PlusIcon
} from '@heroicons/vue/24/outline'

const api = axios.create({
  baseURL: 'http://localhost:8000'
})

const tasks = ref([])
const recentTasks = computed(() => tasks.value.slice(0, 5))

const stats = computed(() => {
  const total = tasks.value.length
  const running = tasks.value.filter(t => t.status === 'running').length
  const failed = tasks.value.filter(t => t.status === 'failed').length
  const success = tasks.value.filter(t => t.status === 'success').length
  const successRate = total > 0 ? Math.round((success / total) * 100) : 100

  return {
    total,
    running,
    failedToday: failed,
    successRate
  }
})

async function fetchTasks() {
  try {
    const res = await api.get('/tasks')
    tasks.value = res.data
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
  }
}

function statusEmoji(status) {
  const emojis = { idle: '⚪', running: '🟢', success: '✅', failed: '🔴', timeout: '🟡' }
  return emojis[status] || '⚪'
}

function statusClass(status) {
  const classes = {
    idle: 'bg-gray-600 text-gray-300',
    running: 'bg-blue-600 text-white',
    success: 'bg-emerald-600 text-white',
    failed: 'bg-red-600 text-white',
    timeout: 'bg-yellow-600 text-white'
  }
  return classes[status] || classes.idle
}

function statusText(status) {
  const texts = { idle: '闲置', running: '运行中', success: '成功', failed: '失败', timeout: '超时' }
  return texts[status] || status
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return d.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchTasks()
  setInterval(fetchTasks, 5000)
})
</script>
