import { ref, computed, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { taskApi, scriptApi } from '../utils/api.js'

export function useTask() {
  const tasks = ref([])
  const loading = ref(false)
  const currentTask = ref(null)

  // Fetch all tasks
  async function fetchTasks() {
    loading.value = true
    try {
      const res = await taskApi.list()
      tasks.value = res.data
    } catch (e) {
      console.error('Failed to fetch tasks:', e)
    } finally {
      loading.value = false
    }
  }

  // Create a new task
  async function createTask(payload) {
    try {
      const res = await taskApi.create(payload)
      ElMessage.success('任务创建成功')
      await fetchTasks()
      return res.data
    } catch (e) {
      ElMessage.error('创建失败: ' + (e.response?.data?.detail || e.message))
      throw e
    }
  }

  // Update an existing task
  async function updateTask(id, payload) {
    try {
      await taskApi.update(id, payload)
      ElMessage.success('任务更新成功')
      await fetchTasks()
    } catch (e) {
      ElMessage.error('更新失败: ' + (e.response?.data?.detail || e.message))
      throw e
    }
  }

  // Delete a task
  async function deleteTask(id) {
    try {
      await taskApi.delete(id)
      ElMessage.success('任务已删除')
      await fetchTasks()
    } catch (e) {
      ElMessage.error('删除失败: ' + (e.response?.data?.detail || e.message))
      throw e
    }
  }

  // Toggle task active status
  async function toggleTask(id, isActive) {
    try {
      await taskApi.toggle(id, !isActive)
      ElMessage.success(isActive ? '任务已禁用' : '任务已启用')
      await fetchTasks()
    } catch (e) {
      ElMessage.error('操作失败')
      throw e
    }
  }

  // Run a task immediately
  async function runTask(id) {
    try {
      await taskApi.run(id)
      ElMessage.success('任务已启动')
      setTimeout(() => fetchTasks(), 1000)
    } catch (e) {
      ElMessage.error('启动失败: ' + (e.response?.data?.detail || e.message))
      throw e
    }
  }

  // Fetch logs for a task
  async function fetchTaskLogs(taskId) {
    try {
      const res = await taskApi.logs(taskId)
      return res.data
    } catch (e) {
      console.error('Failed to fetch logs:', e)
      return []
    }
  }

  // Enable webhook for a task
  async function enableWebhook(taskId) {
    try {
      await taskApi.enableWebhook(taskId)
      const res = await taskApi.webhookInfo(taskId)
      return res.data
    } catch (e) {
      console.error('Failed to enable webhook:', e)
      return { webhook_token: '' }
    }
  }

  // Get webhook info
  async function getWebhookInfo(taskId) {
    try {
      const res = await taskApi.webhookInfo(taskId)
      return res.data
    } catch (e) {
      console.error('Failed to get webhook info:', e)
      return { webhook_token: '' }
    }
  }

  // Save script content
  async function saveScript(filename, content) {
    try {
      await scriptApi.uploadText(filename, content)
      return './scripts/' + filename
    } catch (e) {
      ElMessage.error('脚本保存失败')
      throw e
    }
  }

  // Get task by ID
  function getTaskById(id) {
    return tasks.value.find(t => t.id === id)
  }

  // Computed properties
  const runningCount = computed(() => tasks.value.filter(t => t.status === 'running').length)
  const totalCount = computed(() => tasks.value.length)

  return {
    tasks,
    loading,
    currentTask,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTask,
    runTask,
    fetchTaskLogs,
    enableWebhook,
    getWebhookInfo,
    saveScript,
    getTaskById,
    runningCount,
    totalCount
  }
}
