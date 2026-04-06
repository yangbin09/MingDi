/**
 * AI Hub Composable
 * 管理 AI Hub 的 8 个 Tab 的数据加载与 CRUD 操作
 */
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  aiProviderApi,
  aiModelApi,
  featureRoutingApi,
  promptTemplateApi,
  ragContextApi,
  aiPermissionApi,
  usageStatsApi,
  auditLogApi,
  type AIProvider,
  type AIModel,
  type FeatureRouting,
  type PromptTemplate,
  type RAGContext,
  type AIPermission,
  type UsageStats,
  type AuditLog
} from '../api/aiHub.ts'

// ============= 类型定义 =============
export interface ProviderFormData {
  name: string
  display_name: string
  api_base_url: string
  api_key: string
  is_enabled: boolean
  is_primary: boolean
}

export interface ModelFormData {
  provider_id: number | undefined
  model_id: string
  display_name: string
  model_type: 'chat' | 'completion'
  context_window: number | null
  is_enabled: boolean
}

export interface RoutingFormData {
  feature: string
  display_name: string
  primary_model_id: number | undefined
  is_enabled: boolean
}

export interface PromptFormData {
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

export interface RAGFormData {
  context_type: 'code' | 'doc' | 'knowledge' | 'other'
  context_key: string
  content: string
  injection_position: 'system' | 'user' | 'context'
  is_enabled: boolean
}

export interface PermissionFormData {
  permission_level: number
  permission_name: string
  description: string
  requires_confirm: boolean
  is_enabled: boolean
}

// ============= 状态定义 =============
const providers = ref<AIProvider[]>([])
const models = ref<AIModel[]>([])
const featureRouting = ref<FeatureRouting[]>([])
const promptTemplates = ref<PromptTemplate[]>([])
const ragContexts = ref<RAGContext[]>([])
const permissions = ref<AIPermission[]>([])
const auditLogs = ref<AuditLog[]>([])
const usageStats = ref<UsageStats>({
  total_requests: 0,
  total_cost: 0,
  input_tokens: 0,
  output_tokens: 0
})

const loading = ref(false)

// ============= 模型名称辅助 =============
function getModelName(modelId: number | null): string {
  if (!modelId) return '未设置'
  const model = models.value.find(m => m.id === modelId)
  return model ? model.display_name : '未知'
}

function getPermissionColor(level: number): string {
  const colors: Record<number, string> = { 1: 'var(--color-success)', 2: 'var(--color-warning)', 3: 'var(--color-danger)' }
  return colors[level] || 'var(--text-muted)'
}

function getStatusType(status: string): string {
  const types: Record<string, string> = {
    success: 'success',
    error: 'danger',
    fallback: 'warning',
    cached: ''
  }
  return types[status] || 'info'
}

function formatTime(timeStr: string | null): string {
  if (!timeStr) return '-'
  const d = new Date(timeStr)
  return d.toLocaleString('zh-CN')
}

// ============= 数据加载 =============
async function loadProviders(): Promise<void> {
  try {
    const res = await aiProviderApi.list()
    providers.value = res.data
  } catch (e) {
    console.error('[useAIHub] loadProviders error:', e)
  }
}

async function loadModels(): Promise<void> {
  try {
    const res = await aiModelApi.list()
    models.value = res.data
  } catch (e) {
    console.error('[useAIHub] loadModels error:', e)
  }
}

async function loadFeatureRouting(): Promise<void> {
  try {
    const res = await featureRoutingApi.list()
    featureRouting.value = res.data
  } catch (e) {
    console.error('[useAIHub] loadFeatureRouting error:', e)
  }
}

async function loadPromptTemplates(): Promise<void> {
  try {
    const res = await promptTemplateApi.list()
    promptTemplates.value = res.data
  } catch (e) {
    console.error('[useAIHub] loadPromptTemplates error:', e)
  }
}

async function loadRagContexts(): Promise<void> {
  try {
    const res = await ragContextApi.list()
    ragContexts.value = res.data
  } catch (e) {
    console.error('[useAIHub] loadRagContexts error:', e)
  }
}

async function loadPermissions(): Promise<void> {
  try {
    const res = await aiPermissionApi.list()
    permissions.value = res.data
  } catch (e) {
    console.error('[useAIHub] loadPermissions error:', e)
  }
}

async function loadUsageStats(): Promise<void> {
  try {
    const res = await usageStatsApi.get()
    usageStats.value = res.data
  } catch (e) {
    console.error('[useAIHub] loadUsageStats error:', e)
  }
}

async function loadAuditLogs(): Promise<void> {
  try {
    const res = await auditLogApi.list()
    auditLogs.value = res.data
  } catch (e) {
    console.error('[useAIHub] loadAuditLogs error:', e)
  }
}

async function loadAll(): Promise<void> {
  loading.value = true
  await Promise.all([
    loadProviders(),
    loadModels(),
    loadFeatureRouting(),
    loadPromptTemplates(),
    loadRagContexts(),
    loadPermissions(),
    loadUsageStats(),
    loadAuditLogs()
  ])
  loading.value = false
}

// ============= Provider CRUD =============
async function saveProvider(id: number | null, data: ProviderFormData): Promise<boolean> {
  try {
    if (id) {
      await aiProviderApi.update(id, data)
      ElMessage.success('服务商已更新')
    } else {
      await aiProviderApi.create(data)
      ElMessage.success('服务商已创建')
    }
    await loadProviders()
    return true
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function deleteProvider(id: number): Promise<boolean> {
  try {
    await aiProviderApi.delete(id)
    ElMessage.success('已删除')
    await loadProviders()
    return true
  } catch (e: any) {
    ElMessage.error('删除失败')
    return false
  }
}

// ============= Model CRUD =============
async function saveModel(id: number | null, data: ModelFormData): Promise<boolean> {
  try {
    if (id) {
      await aiModelApi.update(id, data)
      ElMessage.success('模型已更新')
    } else {
      await aiModelApi.create(data)
      ElMessage.success('模型已创建')
    }
    await loadModels()
    return true
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function deleteModel(id: number): Promise<boolean> {
  try {
    await aiModelApi.delete(id)
    ElMessage.success('已删除')
    await loadModels()
    return true
  } catch (e: any) {
    ElMessage.error('删除失败')
    return false
  }
}

// ============= Routing CRUD =============
async function saveRouting(id: number | null, data: RoutingFormData): Promise<boolean> {
  try {
    if (id) {
      await featureRoutingApi.update(id, data)
      ElMessage.success('路由已更新')
    } else {
      await featureRoutingApi.create(data)
      ElMessage.success('路由已创建')
    }
    await loadFeatureRouting()
    return true
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function deleteRouting(id: number): Promise<boolean> {
  try {
    await featureRoutingApi.delete(id)
    ElMessage.success('已删除')
    await loadFeatureRouting()
    return true
  } catch (e: any) {
    ElMessage.error('删除失败')
    return false
  }
}

// ============= Prompt CRUD =============
async function savePrompt(id: number | null, data: PromptFormData): Promise<boolean> {
  try {
    if (id) {
      await promptTemplateApi.update(id, data)
      ElMessage.success('模板已更新')
    } else {
      await promptTemplateApi.create(data)
      ElMessage.success('模板已创建')
    }
    await loadPromptTemplates()
    return true
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function deletePrompt(id: number): Promise<boolean> {
  try {
    await promptTemplateApi.delete(id)
    ElMessage.success('已删除')
    await loadPromptTemplates()
    return true
  } catch (e: any) {
    ElMessage.error('删除失败')
    return false
  }
}

// ============= RAG CRUD =============
async function saveRag(id: number | null, data: RAGFormData): Promise<boolean> {
  try {
    if (id) {
      await ragContextApi.update(id, data)
      ElMessage.success('上下文已更新')
    } else {
      await ragContextApi.create(data)
      ElMessage.success('上下文已创建')
    }
    await loadRagContexts()
    return true
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function deleteRag(id: number): Promise<boolean> {
  try {
    await ragContextApi.delete(id)
    ElMessage.success('已删除')
    await loadRagContexts()
    return true
  } catch (e: any) {
    ElMessage.error('删除失败')
    return false
  }
}

// ============= Permission CRUD =============
async function savePermission(id: number | null, data: PermissionFormData): Promise<boolean> {
  try {
    if (id) {
      await aiPermissionApi.update(id, data)
      ElMessage.success('权限已更新')
    } else {
      await aiPermissionApi.create(data)
      ElMessage.success('权限已创建')
    }
    await loadPermissions()
    return true
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function deletePermission(id: number): Promise<boolean> {
  try {
    await aiPermissionApi.delete(id)
    ElMessage.success('已删除')
    await loadPermissions()
    return true
  } catch (e: any) {
    ElMessage.error('删除失败')
    return false
  }
}

// ============= 导出 =============
export function useAIHub() {
  return {
    // 状态
    providers,
    models,
    featureRouting,
    promptTemplates,
    ragContexts,
    permissions,
    auditLogs,
    usageStats,
    loading,

    // 辅助函数
    getModelName,
    getPermissionColor,
    getStatusType,
    formatTime,

    // 加载方法
    loadProviders,
    loadModels,
    loadFeatureRouting,
    loadPromptTemplates,
    loadRagContexts,
    loadPermissions,
    loadUsageStats,
    loadAuditLogs,
    loadAll,

    // Provider CRUD
    saveProvider,
    deleteProvider,

    // Model CRUD
    saveModel,
    deleteModel,

    // Routing CRUD
    saveRouting,
    deleteRouting,

    // Prompt CRUD
    savePrompt,
    deletePrompt,

    // RAG CRUD
    saveRag,
    deleteRag,

    // Permission CRUD
    savePermission,
    deletePermission
  }
}
