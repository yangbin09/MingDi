import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { aiApi } from '../utils/api.js'

export function useAI() {
  const aiEnabled = ref(false)
  const aiLoading = ref(false)

  // Check AI capabilities and status
  async function checkAIStatus() {
    try {
      const res = await aiApi.capabilities()
      aiEnabled.value = res.data.ai_enabled
      return res.data
    } catch (e) {
      aiEnabled.value = false
      return { ai_enabled: false }
    }
  }

  // Generate script from natural language
  async function generateScript(prompt) {
    aiLoading.value = true
    try {
      const res = await aiApi.generateScript(prompt)
      if (!res.data.used_ai) {
        ElMessage.warning('AI服务未配置，请前往「系统设置」配置')
      }
      return res.data
    } catch (e) {
      ElMessage.error('生成失败: ' + (e.response?.data?.detail || e.message))
      throw e
    } finally {
      aiLoading.value = false
    }
  }

  // Code review
  async function codeReview(code) {
    aiLoading.value = true
    try {
      const res = await aiApi.codeReview(code)
      if (!res.data.used_ai) {
        ElMessage.warning('AI服务未配置，请前往「系统设置」配置')
      }
      return res.data
    } catch (e) {
      ElMessage.error('审查失败: ' + (e.response?.data?.detail || e.message))
      throw e
    } finally {
      aiLoading.value = false
    }
  }

  // Generate documentation
  async function generateDoc(code) {
    aiLoading.value = true
    try {
      const res = await aiApi.generateDoc(code)
      return res.data
    } catch (e) {
      console.error('文档生成失败:', e)
      throw e
    } finally {
      aiLoading.value = false
    }
  }

  // NLP to Cron conversion
  async function nlpToCron(text) {
    aiLoading.value = true
    try {
      const res = await aiApi.nlpToCron(text)
      if (!res.data.used_ai) {
        ElMessage.warning('AI服务未配置，请前往「系统设置」配置')
      }
      return res.data
    } catch (e) {
      ElMessage.error('转换失败: ' + (e.response?.data?.detail || e.message))
      throw e
    } finally {
      aiLoading.value = false
    }
  }

  // Summarize log
  async function summarizeLog(logContent) {
    aiLoading.value = true
    try {
      const res = await aiApi.summarizeLog(logContent)
      if (!res.data.used_ai) {
        ElMessage.warning('AI服务未配置，请前往「系统设置」配置')
      }
      return res.data
    } catch (e) {
      ElMessage.error('摘要生成失败: ' + (e.response?.data?.detail || e.message))
      throw e
    } finally {
      aiLoading.value = false
    }
  }

  // Diagnose error
  async function diagnoseError(errorMsg, code = '') {
    aiLoading.value = true
    try {
      const res = await aiApi.diagnoseError(errorMsg, code)
      if (!res.data.used_ai) {
        ElMessage.warning('AI服务未配置，请前往「系统设置」配置')
      }
      return res.data
    } catch (e) {
      ElMessage.error('诊断失败: ' + (e.response?.data?.detail || e.message))
      throw e
    } finally {
      aiLoading.value = false
    }
  }

  return {
    aiEnabled,
    aiLoading,
    checkAIStatus,
    generateScript,
    codeReview,
    generateDoc,
    nlpToCron,
    summarizeLog,
    diagnoseError
  }
}
