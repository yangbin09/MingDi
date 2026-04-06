/**
 * 设置导入导出 Composable
 * 管理配置的导出和导入逻辑
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { settingsExportApi, type ExportData, type ImportResult } from '../api/settings.ts'

// ============= 状态定义 =============
const exporting = ref(false)
const importing = ref(false)

// ============= 方法 =============
async function exportConfig(): Promise<boolean> {
  exporting.value = true
  try {
    const res = await settingsExportApi.export()
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `pycron-config-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
    return true
  } catch (e: any) {
    ElMessage.error('导出失败: ' + (e.response?.data?.detail || e.message))
    return false
  } finally {
    exporting.value = false
  }
}

async function importConfig(data: ExportData): Promise<ImportResult | null> {
  importing.value = true
  try {
    const res = await settingsExportApi.import(data)
    ElMessage.success(`导入成功！任务: ${res.data.tasks_imported}, 变量: ${res.data.env_vars_imported}, 告警: ${res.data.alerts_imported}`)
    return res.data
  } catch (e: any) {
    ElMessage.error('导入失败: ' + (e.response?.data?.detail || e.message))
    return null
  } finally {
    importing.value = false
  }
}

async function handleImportFile(event: Event): Promise<ImportResult | null> {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return null

  try {
    const text = await file.text()
    const data = JSON.parse(text) as ExportData
    const result = await importConfig(data)
    target.value = '' // 清空 input
    return result
  } catch (e) {
    ElMessage.error('导入失败: 文件格式错误')
    target.value = ''
    return null
  }
}

// ============= 导出 =============
export function useSettingsExport() {
  return {
    // 状态
    exporting,
    importing,

    // 方法
    exportConfig,
    importConfig,
    handleImportFile
  }
}
