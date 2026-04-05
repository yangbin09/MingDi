/**
 * Unified API Client for PyCron-Master
 * Centralizes axios configuration and provides consistent error handling
 */
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for logging/error handling
apiClient.interceptors.request.use(
  config => {
    // Add timestamp to prevent cached responses
    config.params = {
      ...config.params,
      _t: Date.now()
    }
    return config
  },
  error => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.message
      console.error('API Response Error:', message)
    } else if (error.request) {
      // Request made but no response
      console.error('API Network Error: No response received')
    } else {
      console.error('API Error:', error.message)
    }
    return Promise.reject(error)
  }
)

// Task-related API functions
export const taskApi = {
  list: () => apiClient.get('/tasks'),
  get: (id) => apiClient.get(`/tasks/${id}`),
  create: (data) => {
    console.log('taskApi.create called with', JSON.stringify(data))
    return apiClient.post('/tasks', data)
  },
  update: (id, data) => apiClient.put(`/tasks/${id}`, data),
  delete: (id) => apiClient.delete(`/tasks/${id}`),
  run: (id) => apiClient.post(`/tasks/${id}/run`),
  toggle: (id, isActive) => apiClient.put(`/tasks/${id}`, { is_active: isActive }),
  logs: (id) => apiClient.get(`/tasks/${id}/logs`),
  timeline: () => apiClient.get('/tasks/timeline'),
  webhookInfo: (id) => apiClient.get(`/tasks/${id}/webhook-info`),
  enableWebhook: (id) => apiClient.post(`/tasks/${id}/enable-webhook`),
  disableWebhook: (id) => apiClient.post(`/tasks/${id}/disable-webhook`)
}

// AI-related API functions
export const aiApi = {
  generateScript: (description) => apiClient.post('/ai/generate-script', { description }),
  diagnoseError: (errorTraceback, scriptContent) =>
    apiClient.post('/ai/diagnose-error', { error_traceback: errorTraceback, script_content: scriptContent }),
  codeReview: (code) => apiClient.post('/ai/code-review', { code }),
  nlpToCron: (naturalLanguage) => apiClient.post('/ai/nlp-to-cron', { natural_language: naturalLanguage }),
  summarizeLog: (logContent) => apiClient.post('/ai/summarize-log', { log_content: logContent }),
  generateDoc: (code) => apiClient.post('/ai/generate-doc', { code }),
  humanizeAlert: (alertType, taskName, errorInfo) =>
    apiClient.post('/ai/humanize-alert', { alert_type: alertType, task_name: taskName, error_info: errorInfo }),
  capabilities: () => apiClient.get('/ai/capabilities')
}

// System API functions
export const systemApi = {
  stats: () => apiClient.get('/system/stats'),
  settings: () => apiClient.get('/system/settings'),
  updateSettings: (data) => apiClient.put('/system/settings', data),
  testAI: () => apiClient.post('/system/settings/test-ai')
}

// Log API functions
export const logApi = {
  get: (logId) => apiClient.get(`/logs/${logId}`),
  search: (params) => apiClient.get('/logs/search', { params }),
  searchByTask: (taskId, keyword, startDate, endDate, exitCode) =>
    apiClient.get('/logs/search', { params: { task_id: taskId, keyword, start_date: startDate, end_date: endDate, exit_code: exitCode } }),
  download: (logId) => apiClient.get(`/logs/${logId}/download`, { responseType: 'blob' })
}

// Env Var API functions
export const envVarApi = {
  list: () => apiClient.get('/env-vars'),
  create: (data) => apiClient.post('/env-vars', data),
  update: (id, data) => apiClient.put(`/env-vars/${id}`, data),
  delete: (id) => apiClient.delete(`/env-vars/${id}`)
}

// Alert API functions
export const alertApi = {
  list: () => apiClient.get('/alerts'),
  create: (data) => apiClient.post('/alerts', data),
  update: (id, data) => apiClient.put(`/alerts/${id}`, data),
  delete: (id) => apiClient.delete(`/alerts/${id}`)
}

// Script API functions
export const scriptApi = {
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/scripts/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  uploadText: (filename, content) =>
    apiClient.post('/scripts/upload-text', null, { params: { filename, content } })
}

// Node Flow API functions
export const nodeFlowApi = {
  list: () => apiClient.get('/node-flows'),
  get: (id) => apiClient.get(`/node-flows/${id}`),
  create: (data) => apiClient.post('/node-flows', data),
  update: (id, data) => apiClient.put(`/node-flows/${id}`, data),
  delete: (id) => apiClient.delete(`/node-flows/${id}`),
  execute: (id) => apiClient.post(`/node-flows/${id}/execute`)
}

// Default export
export default apiClient
