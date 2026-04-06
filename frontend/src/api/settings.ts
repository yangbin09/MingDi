/**
 * Settings 模块 API 封装
 * 统一管理环境变量、告警、系统设置、导入导出的 API 调用
 */
import apiClient from '../utils/api.js'

// ============= 类型定义 =============
export interface EnvVar {
  id: number
  key: string
  value: string
  description: string | null
  is_secret: boolean
}

export interface Alert {
  id: number
  name: string
  webhook_url: string
  events: string
  is_active: boolean
  ai_humanize: boolean
}

export interface AISettings {
  minimax_api_key: string
  minimax_group_id: string
  ai_enabled: boolean
}

export interface AITestResult {
  success: boolean
  message: string
}

export interface ImportResult {
  tasks_imported: number
  env_vars_imported: number
  alerts_imported: number
}

export interface ExportData {
  tasks: any[]
  env_vars: any[]
  alerts: any[]
}

// ============= 环境变量 API =============
export const envVarApi = {
  list: () => apiClient.get<any[]>('/env-vars'),

  create: (data: Partial<EnvVar>) => apiClient.post<EnvVar>('/env-vars', data),

  update: (id: number, data: Partial<EnvVar>) => apiClient.put<EnvVar>(`/env-vars/${id}`, data),

  delete: (id: number) => apiClient.delete(`/env-vars/${id}`)
}

// ============= 告警 API =============
export const alertApi = {
  list: () => apiClient.get<Alert[]>('/alerts'),

  create: (data: Partial<Alert>) => apiClient.post<Alert>('/alerts', data),

  update: (id: number, data: Partial<Alert>) => apiClient.put<Alert>(`/alerts/${id}`, data),

  delete: (id: number) => apiClient.delete(`/alerts/${id}`)
}

// ============= 系统设置 API =============
export const systemSettingsApi = {
  get: () => apiClient.get<AISettings>('/system/settings'),

  update: (data: Partial<AISettings>) => apiClient.put<AISettings>('/system/settings', data),

  testAI: () => apiClient.post<AITestResult>('/system/settings/test-ai')
}

// ============= 导入导出 API =============
export const settingsExportApi = {
  export: () => apiClient.get<ExportData>('/export'),

  import: (data: ExportData) => apiClient.post<ImportResult>('/import', data)
}
