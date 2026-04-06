/**
 * 告警配置 Composable
 * 管理告警配置的增删改查逻辑
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { alertApi, type Alert } from '../api/settings.ts'

// ============= 类型定义 =============
export interface AlertFormData {
  name: string
  webhook_url: string
  events: string
  is_active: boolean
  ai_humanize: boolean
}

// ============= 状态定义 =============
const alerts = ref<Alert[]>([])
const loading = ref(false)

// ============= 方法 =============
async function fetchAlerts(): Promise<void> {
  loading.value = true
  try {
    const res = await alertApi.list()
    alerts.value = res.data
  } catch (e) {
    console.error('[useAlerts] fetchAlerts error:', e)
    ElMessage.error('获取告警配置失败')
  } finally {
    loading.value = false
  }
}

async function createAlert(data: AlertFormData): Promise<boolean> {
  try {
    await alertApi.create(data)
    ElMessage.success('告警创建成功')
    await fetchAlerts()
    return true
  } catch (e: any) {
    ElMessage.error('创建失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function updateAlert(id: number, data: AlertFormData): Promise<boolean> {
  try {
    await alertApi.update(id, data)
    ElMessage.success('告警更新成功')
    await fetchAlerts()
    return true
  } catch (e: any) {
    ElMessage.error('更新失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function deleteAlert(id: number): Promise<boolean> {
  try {
    await alertApi.delete(id)
    ElMessage.success('告警已删除')
    await fetchAlerts()
    return true
  } catch (e: any) {
    ElMessage.error('删除失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function toggleAlert(alert: Alert): Promise<boolean> {
  try {
    await alertApi.update(alert.id, { is_active: !alert.is_active })
    ElMessage.success(alert.is_active ? '告警已禁用' : '告警已启用')
    await fetchAlerts()
    return true
  } catch (e: any) {
    ElMessage.error('操作失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

// ============= 导出 =============
export function useAlerts() {
  return {
    // 状态
    alerts,
    loading,

    // 方法
    fetchAlerts,
    createAlert,
    updateAlert,
    deleteAlert,
    toggleAlert
  }
}
