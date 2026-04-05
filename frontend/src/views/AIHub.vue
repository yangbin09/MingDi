<template>
  <div class="ai-hub space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--text-main);">
          <el-icon class="mr-2"><MagicStick /></el-icon>
          智能中枢
        </h1>
        <p class="text-sm mt-1" style="color: var(--text-muted);">AI Hub - 多模型路由与智能配置</p>
      </div>
    </div>

    <!-- Tab Navigation -->
    <el-tabs v-model="activeTab" class="ai-hub-tabs">
      <el-tab-pane label="服务商" name="providers">
        <template #label>
          <span class="tab-label">
            <el-icon><Cpu /></el-icon>
            服务商配置
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="模型" name="models">
        <template #label>
          <span class="tab-label">
            <el-icon><Box /></el-icon>
            模型配置
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="路由" name="routing">
        <template #label>
          <span class="tab-label">
            <el-icon><Connection /></el-icon>
            功能路由
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="提示词" name="prompts">
        <template #label>
          <span class="tab-label">
            <el-icon><ChatDotRound /></el-icon>
            提示词模板
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="RAG" name="rag">
        <template #label>
          <span class="tab-label">
            <el-icon><Document /></el-icon>
            RAG 上下文
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="权限" name="permissions">
        <template #label>
          <span class="tab-label">
            <el-icon><Lock /></el-icon>
            权限级别
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="用量" name="usage">
        <template #label>
          <span class="tab-label">
            <el-icon><DataLine /></el-icon>
            用量统计
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="审计" name="audit">
        <template #label>
          <span class="tab-label">
            <el-icon><List /></el-icon>
            审计日志
          </span>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- Tab Content -->
    <div v-if="activeTab === 'providers'">
      <el-card shadow="never" class="provider-card">
        <template #header>
          <div class="card-header">
            <span class="font-semibold">AI 服务商配置</span>
            <el-button type="primary" @click="showProviderModal = true">
              <el-icon><Plus /></el-icon>
              添加服务商
            </el-button>
          </div>
        </template>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" v-for="provider in providers" :key="provider.id">
            <el-card shadow="hover" class="provider-item" :class="{ 'is-enabled': provider.is_enabled }">
              <div class="provider-header">
                <div class="provider-info">
                  <el-avatar :style="{ backgroundColor: 'var(--color-primary-subtle)' }">
                    <el-icon><Cpu /></el-icon>
                  </el-avatar>
                  <div>
                    <div class="font-medium">{{ provider.display_name }}</div>
                    <div class="text-xs" style="color: var(--text-muted);">{{ provider.name }}</div>
                  </div>
                </div>
                <el-tag :type="provider.is_enabled ? 'success' : 'info'" size="small">
                  {{ provider.is_enabled ? '启用' : '禁用' }}
                </el-tag>
              </div>
              <div class="provider-stats">
                <div class="stat-item">
                  <span class="stat-label">优先级</span>
                  <span class="stat-value">{{ provider.priority }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">API 限额</span>
                  <span class="stat-value">{{ provider.rate_limit_rpm || '无限制' }}/分</span>
                </div>
              </div>
              <div class="provider-actions">
                <el-button size="small" @click="editProvider(provider)">编辑</el-button>
                <el-button size="small" type="danger" plain @click="deleteProvider(provider.id)">删除</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-empty v-if="providers.length === 0" description="暂无服务商配置" />
      </el-card>
    </div>

    <div v-if="activeTab === 'models'">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span class="font-semibold">模型配置</span>
            <el-button type="primary" @click="showModelModal = true">
              <el-icon><Plus /></el-icon>
              添加模型
            </el-button>
          </div>
        </template>

        <el-table :data="models" stripe style="width: 100%">
          <el-table-column label="模型" min-width="200">
            <template #default="{ row }">
              <div class="font-medium">{{ row.display_name }}</div>
              <div class="text-xs" style="color: var(--text-muted);">{{ row.model_id }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="model_type" label="类型" width="100" />
          <el-table-column prop="context_window" label="上下文窗口" width="120">
            <template #default="{ row }">{{ row.context_window || '无限制' }}</template>
          </el-table-column>
          <el-table-column label="输入成本" width="120">
            <template #default="{ row }">${{ row.cost_per_input_token }}/1K</template>
          </el-table-column>
          <el-table-column label="输出成本" width="120">
            <template #default="{ row }">${{ row.cost_per_output_token }}/1K</template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_enabled ? 'success' : 'info'" size="small">
                {{ row.is_enabled ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" plain @click="editModel(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="models.length === 0" description="暂无模型配置" />
      </el-card>
    </div>

    <div v-if="activeTab === 'routing'">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span class="font-semibold">功能路由配置</span>
            <el-button type="primary" @click="showRoutingModal = true">
              <el-icon><Plus /></el-icon>
              添加路由
            </el-button>
          </div>
        </template>

        <el-row :gutter="16">
          <el-col :xs="24" :md="12" v-for="routing in featureRouting" :key="routing.id">
            <el-card shadow="hover" class="routing-item">
              <div class="routing-header">
                <div>
                  <div class="font-medium">{{ routing.display_name }}</div>
                  <div class="text-xs" style="color: var(--text-muted);">{{ routing.feature }}</div>
                </div>
                <el-tag :type="routing.is_enabled ? 'success' : 'info'" size="small">
                  {{ routing.is_enabled ? '启用' : '禁用' }}
                </el-tag>
              </div>
              <div class="routing-info">
                <div>
                  <span style="color: var(--text-muted);">主模型:</span>
                  <span>{{ getModelName(routing.primary_model_id) }}</span>
                </div>
                <div>
                  <span style="color: var(--text-muted);">备用模型:</span>
                  <span>{{ routing.fallback_model_ids?.length || 0 }} 个</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-empty v-if="featureRouting.length === 0" description="暂无路由配置" />
      </el-card>
    </div>

    <div v-if="activeTab === 'prompts'">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span class="font-semibold">提示词模板</span>
            <el-button type="primary" @click="showPromptModal = true">
              <el-icon><Plus /></el-icon>
              创建模板
            </el-button>
          </div>
        </template>

        <el-row :gutter="16">
          <el-col :xs="24" :md="12" v-for="template in promptTemplates" :key="template.id">
            <el-card shadow="hover" class="prompt-item">
              <div class="prompt-header">
                <div>
                  <div class="font-medium">{{ template.display_name }}</div>
                  <div class="text-xs" style="color: var(--text-muted);">{{ template.feature }}</div>
                </div>
                <div class="flex gap-2">
                  <el-tag :type="template.is_enabled ? 'success' : 'info'" size="small">
                    {{ template.is_enabled ? '启用' : '禁用' }}
                  </el-tag>
                  <el-button size="small" @click="editPromptTemplate(template)">编辑</el-button>
                </div>
              </div>
              <div class="prompt-config">
                <el-tag size="small">温度: {{ template.temperature }}</el-tag>
                <el-tag size="small">Top P: {{ template.top_p }}</el-tag>
                <el-tag size="small">最大Tokens: {{ template.max_tokens }}</el-tag>
                <el-tag size="small">上下文行数: {{ template.context_lines }}</el-tag>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-empty v-if="promptTemplates.length === 0" description="暂无提示词模板" />
      </el-card>
    </div>

    <div v-if="activeTab === 'rag'">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span class="font-semibold">本地 RAG 上下文</span>
            <el-button type="primary" @click="showRagModal = true">
              <el-icon><Plus /></el-icon>
              添加上下文
            </el-button>
          </div>
        </template>

        <el-row :gutter="16">
          <el-col :xs="24" :md="12" v-for="rag in ragContexts" :key="rag.id">
            <el-card shadow="hover" class="rag-item">
              <div class="rag-header">
                <div>
                  <div class="font-medium">{{ rag.context_key }}</div>
                  <div class="text-xs" style="color: var(--text-muted);">{{ rag.context_type }}</div>
                </div>
                <el-tag :type="rag.is_enabled ? 'success' : 'info'" size="small">
                  {{ rag.is_enabled ? '启用' : '禁用' }}
                </el-tag>
              </div>
              <div class="rag-content">{{ rag.content }}</div>
              <div class="rag-footer">
                <span class="text-xs" style="color: var(--text-disabled);">注入位置: {{ rag.injection_position }}</span>
                <el-button size="small" type="danger" plain @click="deleteRag(rag.id)">删除</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-empty v-if="ragContexts.length === 0" description="暂无 RAG 上下文" />
      </el-card>
    </div>

    <div v-if="activeTab === 'permissions'">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span class="font-semibold">AI 权限级别</span>
            <el-button type="primary" @click="showPermissionModal = true">
              <el-icon><Plus /></el-icon>
              添加权限
            </el-button>
          </div>
        </template>

        <el-row :gutter="16">
          <el-col :xs="24" v-for="perm in permissions" :key="perm.id">
            <el-card shadow="hover" class="perm-item">
              <div class="perm-content">
                <el-avatar :size="48" :style="{ backgroundColor: getPermissionColor(perm.permission_level) + '20', color: getPermissionColor(perm.permission_level) }">
                  L{{ perm.permission_level }}
                </el-avatar>
                <div class="perm-info">
                  <div class="font-medium">{{ perm.permission_name }}</div>
                  <div class="text-sm" style="color: var(--text-muted);">{{ perm.description }}</div>
                </div>
                <div class="perm-status">
                  <el-tag :type="perm.requires_confirm ? 'warning' : 'success'" size="small">
                    {{ perm.requires_confirm ? '需确认' : '自动执行' }}
                  </el-tag>
                  <el-button size="small" @click="editPermission(perm)">编辑</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-empty v-if="permissions.length === 0" description="暂无权限配置" />
      </el-card>
    </div>

    <div v-if="activeTab === 'usage'">
      <el-row :gutter="16" class="mb-4">
        <el-col :xs="12" :md="6">
          <el-card shadow="never" class="stat-card">
            <div class="stat-value">{{ usageStats.total_requests }}</div>
            <div class="stat-label">今日请求</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :md="6">
          <el-card shadow="never" class="stat-card">
            <div class="stat-value" style="color: var(--color-primary);">${{ usageStats.total_cost.toFixed(4) }}</div>
            <div class="stat-label">今日消耗</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :md="6">
          <el-card shadow="never" class="stat-card">
            <div class="stat-value">{{ usageStats.input_tokens.toLocaleString() }}</div>
            <div class="stat-label">输入 Tokens</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :md="6">
          <el-card shadow="never" class="stat-card">
            <div class="stat-value">{{ usageStats.output_tokens.toLocaleString() }}</div>
            <div class="stat-label">输出 Tokens</div>
          </el-card>
        </el-col>
      </el-row>

      <el-card shadow="never">
        <template #header>
          <span class="font-semibold">用量趋势</span>
        </template>
        <div class="h-64 flex items-center justify-center" style="color: var(--text-muted);">
          图表区域 (需要 ECharts 或 Chart.js)
        </div>
      </el-card>
    </div>

    <div v-if="activeTab === 'audit'">
      <el-card shadow="never">
        <template #header>
          <span class="font-semibold">AI 操作审计日志</span>
        </template>

        <el-table :data="auditLogs" stripe style="width: 100%">
          <el-table-column prop="created_at" label="时间" width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column prop="feature" label="功能" width="120" />
          <el-table-column label="模型" width="150">
            <template #default="{ row }">{{ getModelName(row.model_id) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="latency_ms" label="延迟" width="100">
            <template #default="{ row }">{{ row.latency_ms }}ms</template>
          </el-table-column>
          <el-table-column label="Tokens" width="100">
            <template #default="{ row }">{{ row.input_tokens + row.output_tokens }}</template>
          </el-table-column>
          <el-table-column label="成本" width="100">
            <template #default="{ row }">${{ row.cost_usd.toFixed(4) }}</template>
          </el-table-column>
        </el-table>

        <el-empty v-if="auditLogs.length === 0" description="暂无审计日志" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import {
  Cpu, Box, Connection, ChatDotRound, Document, Lock,
  DataLine, List, Plus, MagicStick
} from '@element-plus/icons-vue'

const api = axios.create({ baseURL: 'http://localhost:8000' })

const activeTab = ref('providers')

// Data
const providers = ref([])
const models = ref([])
const featureRouting = ref([])
const promptTemplates = ref([])
const ragContexts = ref([])
const permissions = ref([])
const auditLogs = ref([])

const usageStats = ref({
  total_requests: 0,
  total_cost: 0,
  input_tokens: 0,
  output_tokens: 0
})

// Modals
const showProviderModal = ref(false)
const showModelModal = ref(false)
const showRoutingModal = ref(false)
const showPromptModal = ref(false)
const showRagModal = ref(false)
const showPermissionModal = ref(false)

// Load data
async function loadProviders() {
  try {
    const res = await api.get('/ai/providers')
    providers.value = res.data
  } catch (e) {
    console.error('Failed to load providers:', e)
  }
}

async function loadModels() {
  try {
    const res = await api.get('/ai/models')
    models.value = res.data
  } catch (e) {
    console.error('Failed to load models:', e)
  }
}

async function loadFeatureRouting() {
  try {
    const res = await api.get('/ai/feature-routing')
    featureRouting.value = res.data
  } catch (e) {
    console.error('Failed to load feature routing:', e)
  }
}

async function loadPromptTemplates() {
  try {
    const res = await api.get('/ai/prompt-templates')
    promptTemplates.value = res.data
  } catch (e) {
    console.error('Failed to load prompt templates:', e)
  }
}

async function loadRagContexts() {
  try {
    const res = await api.get('/ai/rag-context')
    ragContexts.value = res.data
  } catch (e) {
    console.error('Failed to load RAG contexts:', e)
  }
}

async function loadPermissions() {
  try {
    const res = await api.get('/ai/permissions')
    permissions.value = res.data
  } catch (e) {
    console.error('Failed to load permissions:', e)
  }
}

async function loadUsageStats() {
  try {
    const res = await api.get('/ai/usage-stats')
    usageStats.value = res.data
  } catch (e) {
    console.error('Failed to load usage stats:', e)
  }
}

async function loadAuditLogs() {
  try {
    const res = await api.get('/ai/audit-logs')
    auditLogs.value = res.data
  } catch (e) {
    console.error('Failed to load audit logs:', e)
  }
}

// Helpers
function getModelName(modelId) {
  if (!modelId) return '未设置'
  const model = models.value.find(m => m.id === modelId)
  return model ? model.display_name : '未知'
}

function getPermissionColor(level) {
  const colors = { 1: 'var(--color-success)', 2: 'var(--color-warning)', 3: 'var(--color-danger)' }
  return colors[level] || 'var(--text-muted)'
}

function getStatusType(status) {
  const types = {
    success: 'success',
    error: 'danger',
    fallback: 'warning',
    cached: ''
  }
  return types[status] || 'info'
}

function formatTime(timeStr) {
  if (!timeStr) return '-'
  const d = new Date(timeStr)
  return d.toLocaleString('zh-CN')
}

// Actions
function editProvider(provider) {
  console.log('Edit provider:', provider)
}

function deleteProvider(id) {
  console.log('Delete provider:', id)
}

function editModel(model) {
  console.log('Edit model:', model)
}

function editPromptTemplate(template) {
  console.log('Edit prompt template:', template)
}

function deleteRag(id) {
  console.log('Delete RAG:', id)
}

function editPermission(perm) {
  console.log('Edit permission:', perm)
}

onMounted(() => {
  loadProviders()
  loadModels()
  loadFeatureRouting()
  loadPromptTemplates()
  loadRagContexts()
  loadPermissions()
  loadUsageStats()
  loadAuditLogs()
})
</script>

<style scoped>
.ai-hub-tabs :deep(.el-tabs__header) {
  margin-bottom: 1rem;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.provider-item,
.routing-item,
.prompt-item,
.rag-item,
.perm-item {
  margin-bottom: 16px;
}

.provider-item.is-enabled {
  border-color: var(--color-primary);
}

.provider-header,
.routing-header,
.prompt-header,
.rag-header,
.perm-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.provider-info,
.perm-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.provider-stats,
.routing-info,
.prompt-config {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 13px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

.stat-value {
  font-weight: 500;
}

.provider-actions,
.rag-footer,
.perm-status {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.rag-content {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.stat-card {
  text-align: center;
}

.stat-card .stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-card .stat-label {
  font-size: 14px;
  color: var(--text-muted);
}
</style>
