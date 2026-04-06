/**
 * 环境变量 Composable
 * 管理环境变量的增删改查逻辑
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { envVarApi, type EnvVar } from '../api/settings.ts'

// ============= 类型定义 =============
export interface EnvVarFormData {
  key: string
  value: string
  description: string
  is_secret: boolean
}

// ============= 状态定义 =============
const envVars = ref<EnvVar[]>([])
const loading = ref(false)

// ============= 方法 =============
async function fetchEnvVars(): Promise<void> {
  loading.value = true
  try {
    const res = await envVarApi.list()
    envVars.value = res.data
  } catch (e) {
    console.error('[useEnvVars] fetchEnvVars error:', e)
    ElMessage.error('获取环境变量失败')
  } finally {
    loading.value = false
  }
}

async function createEnvVar(data: EnvVarFormData): Promise<boolean> {
  try {
    await envVarApi.create(data)
    ElMessage.success('环境变量创建成功')
    await fetchEnvVars()
    return true
  } catch (e: any) {
    ElMessage.error('创建失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function updateEnvVar(id: number, data: EnvVarFormData): Promise<boolean> {
  try {
    await envVarApi.update(id, data)
    ElMessage.success('环境变量更新成功')
    await fetchEnvVars()
    return true
  } catch (e: any) {
    ElMessage.error('更新失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function deleteEnvVar(id: number): Promise<boolean> {
  try {
    await envVarApi.delete(id)
    ElMessage.success('环境变量已删除')
    await fetchEnvVars()
    return true
  } catch (e: any) {
    ElMessage.error('删除失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

// ============= 导出 =============
export function useEnvVars() {
  return {
    // 状态
    envVars,
    loading,

    // 方法
    fetchEnvVars,
    createEnvVar,
    updateEnvVar,
    deleteEnvVar
  }
}
