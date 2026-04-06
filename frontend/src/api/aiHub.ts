/**
 * AI Hub 模块 API 封装
 * 统一管理 AI 服务商、模型、路由、提示词、RAG、权限、用量、审计的 API 调用
 */
import apiClient from '../utils/api.js'

// ============= 类型定义 =============
export interface AIProvider {
  id: number
  name: string
  display_name: string
  api_base_url: string | null
  api_key: string | null
  is_enabled: boolean
  is_primary: boolean
  priority: number
  rate_limit_rpm: number | null
}

export interface AIModel {
  id: number
  provider_id: number
  model_id: string
  display_name: string
  model_type: 'chat' | 'completion'
  context_window: number | null
  cost_per_input_token: number
  cost_per_output_token: number
  is_enabled: boolean
}

export interface FeatureRouting {
  id: number
  feature: string
  display_name: string
  primary_model_id: number | null
  fallback_model_ids: number[]
  is_enabled: boolean
}

export interface PromptTemplate {
  id: number
  feature: string
  display_name: string
  system_prompt: string
  user_template: string
  temperature: number
  top_p: number
  max_tokens: number
  context_lines: number
  is_enabled: boolean
}

export interface RAGContext {
  id: number
  context_type: 'code' | 'doc' | 'knowledge' | 'other'
  context_key: string
  content: string
  injection_position: 'system' | 'user' | 'context'
  is_enabled: boolean
}

export interface AIPermission {
  id: number
  permission_level: number
  permission_name: string
  description: string
  requires_confirm: boolean
  is_enabled: boolean
}

export interface UsageStats {
  total_requests: number
  total_cost: number
  input_tokens: number
  output_tokens: number
}

export interface AuditLog {
  id: number
  created_at: string
  feature: string
  model_id: number | null
  status: string
  latency_ms: number
  input_tokens: number
  output_tokens: number
  cost_usd: number
}

// ============= AI 服务商 API =============
export const aiProviderApi = {
  list: () => apiClient.get<AIProvider[]>('/ai/providers'),
  create: (data: Partial<AIProvider>) => apiClient.post<AIProvider>('/ai/providers', data),
  update: (id: number, data: Partial<AIProvider>) => apiClient.put<AIProvider>(`/ai/providers/${id}`, data),
  delete: (id: number) => apiClient.delete(`/ai/providers/${id}`)
}

// ============= AI 模型 API =============
export const aiModelApi = {
  list: () => apiClient.get<AIModel[]>('/ai/models'),
  create: (data: Partial<AIModel>) => apiClient.post<AIModel>('/ai/models', data),
  update: (id: number, data: Partial<AIModel>) => apiClient.put<AIModel>(`/ai/models/${id}`, data),
  delete: (id: number) => apiClient.delete(`/ai/models/${id}`)
}

// ============= 功能路由 API =============
export const featureRoutingApi = {
  list: () => apiClient.get<FeatureRouting[]>('/ai/feature-routing'),
  create: (data: Partial<FeatureRouting>) => apiClient.post<FeatureRouting>('/ai/feature-routing', data),
  update: (id: number, data: Partial<FeatureRouting>) => apiClient.put<FeatureRouting>(`/ai/feature-routing/${id}`, data),
  delete: (id: number) => apiClient.delete(`/ai/feature-routing/${id}`)
}

// ============= 提示词模板 API =============
export const promptTemplateApi = {
  list: () => apiClient.get<PromptTemplate[]>('/ai/prompt-templates'),
  create: (data: Partial<PromptTemplate>) => apiClient.post<PromptTemplate>('/ai/prompt-templates', data),
  update: (id: number, data: Partial<PromptTemplate>) => apiClient.put<PromptTemplate>(`/ai/prompt-templates/${id}`, data),
  delete: (id: number) => apiClient.delete(`/ai/prompt-templates/${id}`)
}

// ============= RAG 上下文 API =============
export const ragContextApi = {
  list: () => apiClient.get<RAGContext[]>('/ai/rag-context'),
  create: (data: Partial<RAGContext>) => apiClient.post<RAGContext>('/ai/rag-context', data),
  update: (id: number, data: Partial<RAGContext>) => apiClient.put<RAGContext>(`/ai/rag-context/${id}`, data),
  delete: (id: number) => apiClient.delete(`/ai/rag-context/${id}`)
}

// ============= AI 权限 API =============
export const aiPermissionApi = {
  list: () => apiClient.get<AIPermission[]>('/ai/permissions'),
  create: (data: Partial<AIPermission>) => apiClient.post<AIPermission>('/ai/permissions', data),
  update: (id: number, data: Partial<AIPermission>) => apiClient.put<AIPermission>(`/ai/permissions/${id}`, data),
  delete: (id: number) => apiClient.delete(`/ai/permissions/${id}`)
}

// ============= 用量统计 API =============
export const usageStatsApi = {
  get: () => apiClient.get<UsageStats>('/ai/usage-stats')
}

// ============= 审计日志 API =============
export const auditLogApi = {
  list: () => apiClient.get<AuditLog[]>('/ai/audit-logs')
}
