/**
 * AI 设置 Composable
 * 管理 AI 配置的获取、保存、测试逻辑
 */
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { systemSettingsApi, type AISettings, type AITestResult } from '../api/settings.ts'

// ============= 类型定义 =============
export interface AISettingsForm {
  minimax_api_key: string
  minimax_group_id: string
  ai_enabled: boolean
}

// ============= 状态定义 =============
const aiSettings = reactive<AISettingsForm>({
  minimax_api_key: '',
  minimax_group_id: '',
  ai_enabled: false
})

const aiSettingsSaved = ref(false)
const aiTesting = ref(false)
const aiTestResult = ref<AITestResult | null>(null)

// ============= 方法 =============
async function fetchAISettings(): Promise<void> {
  try {
    const res = await systemSettingsApi.get()
    aiSettings.minimax_api_key = res.data.minimax_api_key || ''
    aiSettings.minimax_group_id = res.data.minimax_group_id || ''
    aiSettings.ai_enabled = res.data.ai_enabled || false
  } catch (e) {
    console.error('[useAISettings] fetchAISettings error:', e)
  }
}

async function saveAISettings(): Promise<boolean> {
  try {
    await systemSettingsApi.update({
      minimax_api_key: aiSettings.minimax_api_key,
      minimax_group_id: aiSettings.minimax_group_id
    })
    aiSettingsSaved.value = true
    aiSettings.ai_enabled = !!(aiSettings.minimax_api_key && aiSettings.minimax_group_id)
    setTimeout(() => { aiSettingsSaved.value = false }, 2000)
    ElMessage.success('AI 配置已保存')
    return true
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
    return false
  }
}

async function testAIConnection(): Promise<AITestResult | null> {
  aiTesting.value = true
  aiTestResult.value = null
  try {
    // 先保存当前配置
    await systemSettingsApi.update({
      minimax_api_key: aiSettings.minimax_api_key,
      minimax_group_id: aiSettings.minimax_group_id
    })
    // 然后测试
    const res = await systemSettingsApi.testAI()
    aiTestResult.value = res.data
    aiSettings.ai_enabled = res.data.success
    if (res.data.success) {
      ElMessage.success('AI 连接测试成功')
    }
    return res.data
  } catch (e: any) {
    aiTestResult.value = { success: false, message: '测试失败: ' + (e.response?.data?.detail || e.message) }
    return null
  } finally {
    aiTesting.value = false
  }
}

// ============= 导出 =============
export function useAISettings() {
  return {
    // 状态
    aiSettings,
    aiSettingsSaved,
    aiTesting,
    aiTestResult,

    // 方法
    fetchAISettings,
    saveAISettings,
    testAIConnection
  }
}
