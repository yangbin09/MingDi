<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--text-main);">🤖 智能中枢</h1>
        <p class="text-sm mt-1" style="color: var(--text-muted);">AI Hub - 多模型路由与智能配置</p>
      </div>
    </div>

    <!-- Tab Navigation -->
    <div class="flex gap-1 p-1 rounded-lg" style="background-color: var(--bg-secondary);">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="flex-1 px-4 py-2.5 rounded-md text-sm font-medium transition-all"
        :style="activeTab === tab.id
          ? { backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }
          : { color: 'var(--text-muted)' }"
      >
        <span class="flex items-center justify-center gap-2">
          <component :is="tab.icon" class="w-4 h-4" />
          {{ tab.label }}
        </span>
      </button>
    </div>

    <!-- Tab Content -->
    <div v-if="activeTab === 'providers'">
      <!-- AI Providers Tab -->
      <div class="rounded-lg p-6" style="background-color: var(--bg-secondary); border: 1px solid var(--border-subtle);">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">AI 服务商配置</h2>
          <button
            @click="showProviderModal = true"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style="background-color: var(--color-primary); color: white;"
          >
            + 添加服务商
          </button>
        </div>

        <!-- Provider Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="provider in providers"
            :key="provider.id"
            class="p-4 rounded-lg border transition-all"
            :style="{
              backgroundColor: 'var(--bg-primary)',
              borderColor: provider.is_enabled ? 'var(--color-primary)' : 'var(--border-subtle)'
            }"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center gap-3">
                <div
                  class="w-10 h-10 rounded-lg flex items-center justify-center"
                  :style="{ backgroundColor: 'var(--color-primary-subtle)' }"
                >
                  <CpuChipIcon class="w-5 h-5" style="color: var(--color-primary);" />
                </div>
                <div>
                  <h3 class="font-medium" style="color: var(--text-main);">{{ provider.display_name }}</h3>
                  <p class="text-xs" style="color: var(--text-muted);">{{ provider.name }}</p>
                </div>
              </div>
              <span
                class="px-2 py-0.5 rounded text-xs font-medium"
                :style="{
                  backgroundColor: provider.is_enabled ? 'var(--color-success)' + '20' : 'var(--bg-hover)',
                  color: provider.is_enabled ? 'var(--color-success)' : 'var(--text-muted)'
                }"
              >
                {{ provider.is_enabled ? '启用' : '禁用' }}
              </span>
            </div>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span style="color: var(--text-muted);">优先级</span>
                <span style="color: var(--text-main);">{{ provider.priority }}</span>
              </div>
              <div class="flex justify-between">
                <span style="color: var(--text-muted);">API 限额</span>
                <span style="color: var(--text-main);">{{ provider.rate_limit_rpm || '无限制' }}/分</span>
              </div>
            </div>
            <div class="mt-4 flex gap-2">
              <button
                @click="editProvider(provider)"
                class="flex-1 px-3 py-1.5 rounded text-xs font-medium"
                style="background-color: var(--bg-hover); color: var(--text-main);"
              >
                编辑
              </button>
              <button
                @click="deleteProvider(provider.id)"
                class="px-3 py-1.5 rounded text-xs font-medium"
                style="background-color: var(--color-danger)20; color: var(--color-danger);"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'models'">
      <!-- Models Tab -->
      <div class="rounded-lg p-6" style="background-color: var(--bg-secondary); border: 1px solid var(--border-subtle);">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">模型配置</h2>
          <button
            @click="showModelModal = true"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style="background-color: var(--color-primary); color: white;"
          >
            + 添加模型
          </button>
        </div>

        <!-- Models Table -->
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr style="border-bottom: 1px solid var(--border-subtle);">
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">模型</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">类型</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">上下文窗口</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">输入成本</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">输出成本</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">状态</th>
                <th class="text-right py-3 px-4 font-medium" style="color: var(--text-muted);">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="model in models"
                :key="model.id"
                style="border-bottom: 1px solid var(--border-subtle);"
              >
                <td class="py-3 px-4">
                  <div>
                    <span class="font-medium" style="color: var(--text-main);">{{ model.display_name }}</span>
                    <p class="text-xs" style="color: var(--text-muted);">{{ model.model_id }}</p>
                  </div>
                </td>
                <td class="py-3 px-4" style="color: var(--text-main);">{{ model.model_type }}</td>
                <td class="py-3 px-4" style="color: var(--text-main);">{{ model.context_window || '无限制' }}</td>
                <td class="py-3 px-4" style="color: var(--text-main);">${{ model.cost_per_input_token }}/1K</td>
                <td class="py-3 px-4" style="color: var(--text-main);">${{ model.cost_per_output_token }}/1K</td>
                <td class="py-3 px-4">
                  <span
                    class="px-2 py-0.5 rounded text-xs font-medium"
                    :style="{
                      backgroundColor: model.is_enabled ? 'var(--color-success)' + '20' : 'var(--bg-hover)',
                      color: model.is_enabled ? 'var(--color-success)' : 'var(--text-muted)'
                    }"
                  >
                    {{ model.is_enabled ? '启用' : '禁用' }}
                  </span>
                </td>
                <td class="py-3 px-4 text-right">
                  <button
                    @click="editModel(model)"
                    class="px-3 py-1 rounded text-xs"
                    style="color: var(--color-primary);"
                  >
                    编辑
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'routing'">
      <!-- Feature Routing Tab -->
      <div class="rounded-lg p-6" style="background-color: var(--bg-secondary); border: 1px solid var(--border-subtle);">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">功能路由配置</h2>
          <button
            @click="showRoutingModal = true"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style="background-color: var(--color-primary); color: white;"
          >
            + 添加路由
          </button>
        </div>

        <div class="space-y-4">
          <div
            v-for="routing in featureRouting"
            :key="routing.id"
            class="p-4 rounded-lg border"
            :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-subtle)' }"
          >
            <div class="flex items-center justify-between mb-3">
              <div>
                <h3 class="font-medium" style="color: var(--text-main);">{{ routing.display_name }}</h3>
                <p class="text-xs" style="color: var(--text-muted);">{{ routing.feature }}</p>
              </div>
              <span
                class="px-2 py-0.5 rounded text-xs font-medium"
                :style="{
                  backgroundColor: routing.is_enabled ? 'var(--color-success)' + '20' : 'var(--bg-hover)',
                  color: routing.is_enabled ? 'var(--color-success)' : 'var(--text-muted)'
                }"
              >
                {{ routing.is_enabled ? '启用' : '禁用' }}
              </span>
            </div>
            <div class="flex items-center gap-4 text-sm">
              <div>
                <span style="color: var(--text-muted);">主模型:</span>
                <span style="color: var(--text-main);">{{ getModelName(routing.primary_model_id) }}</span>
              </div>
              <div>
                <span style="color: var(--text-muted);">备用模型:</span>
                <span style="color: var(--text-main);">{{ routing.fallback_model_ids?.length || 0 }} 个</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'prompts'">
      <!-- Prompt Templates Tab -->
      <div class="rounded-lg p-6" style="background-color: var(--bg-secondary); border: 1px solid var(--border-subtle);">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">提示词模板</h2>
          <button
            @click="showPromptModal = true"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style="background-color: var(--color-primary); color: white;"
          >
            + 创建模板
          </button>
        </div>

        <div class="space-y-4">
          <div
            v-for="template in promptTemplates"
            :key="template.id"
            class="p-4 rounded-lg border"
            :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-subtle)' }"
          >
            <div class="flex items-start justify-between mb-3">
              <div>
                <h3 class="font-medium" style="color: var(--text-main);">{{ template.display_name }}</h3>
                <p class="text-xs" style="color: var(--text-muted);">{{ template.feature }}</p>
              </div>
              <div class="flex items-center gap-2">
                <span
                  class="px-2 py-0.5 rounded text-xs font-medium"
                  :style="{
                    backgroundColor: template.is_enabled ? 'var(--color-success)' + '20' : 'var(--bg-hover)',
                    color: template.is_enabled ? 'var(--color-success)' : 'var(--text-muted)'
                  }"
                >
                  {{ template.is_enabled ? '启用' : '禁用' }}
                </span>
                <button
                  @click="editPromptTemplate(template)"
                  class="px-2 py-1 rounded text-xs"
                  style="color: var(--color-primary);"
                >
                  编辑
                </button>
              </div>
            </div>
            <div class="grid grid-cols-4 gap-4 text-sm">
              <div>
                <span style="color: var(--text-muted);">温度</span>
                <p style="color: var(--text-main);">{{ template.temperature }}</p>
              </div>
              <div>
                <span style="color: var(--text-muted);">Top P</span>
                <p style="color: var(--text-main);">{{ template.top_p }}</p>
              </div>
              <div>
                <span style="color: var(--text-muted);">最大 Tokens</span>
                <p style="color: var(--text-main);">{{ template.max_tokens }}</p>
              </div>
              <div>
                <span style="color: var(--text-muted);">上下文行数</span>
                <p style="color: var(--text-main);">{{ template.context_lines }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'rag'">
      <!-- RAG Context Tab -->
      <div class="rounded-lg p-6" style="background-color: var(--bg-secondary); border: 1px solid var(--border-subtle);">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">本地 RAG 上下文</h2>
          <button
            @click="showRagModal = true"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style="background-color: var(--color-primary); color: white;"
          >
            + 添加上下文
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="rag in ragContexts"
            :key="rag.id"
            class="p-4 rounded-lg border"
            :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-subtle)' }"
          >
            <div class="flex items-start justify-between mb-3">
              <div>
                <h3 class="font-medium" style="color: var(--text-main);">{{ rag.context_key }}</h3>
                <p class="text-xs" style="color: var(--text-muted);">{{ rag.context_type }}</p>
              </div>
              <span
                class="px-2 py-0.5 rounded text-xs font-medium"
                :style="{
                  backgroundColor: rag.is_enabled ? 'var(--color-success)' + '20' : 'var(--bg-hover)',
                  color: rag.is_enabled ? 'var(--color-success)' : 'var(--text-muted)'
                }"
              >
                {{ rag.is_enabled ? '启用' : '禁用' }}
              </span>
            </div>
            <p class="text-sm line-clamp-3" style="color: var(--text-muted);">{{ rag.content }}</p>
            <div class="mt-3 flex items-center justify-between">
              <span class="text-xs" style="color: var(--text-disabled);">注入位置: {{ rag.injection_position }}</span>
              <button
                @click="deleteRag(rag.id)"
                class="px-3 py-1 rounded text-xs"
                style="color: var(--color-danger);"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'permissions'">
      <!-- Permission Levels Tab -->
      <div class="rounded-lg p-6" style="background-color: var(--bg-secondary); border: 1px solid var(--border-subtle);">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">AI 权限级别</h2>
          <button
            @click="showPermissionModal = true"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style="background-color: var(--color-primary); color: white;"
          >
            + 添加权限
          </button>
        </div>

        <div class="space-y-4">
          <div
            v-for="perm in permissions"
            :key="perm.id"
            class="p-4 rounded-lg border"
            :style="{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-subtle)' }"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <div
                  class="w-12 h-12 rounded-lg flex items-center justify-center font-bold text-lg"
                  :style="{
                    backgroundColor: getPermissionColor(perm.permission_level) + '20',
                    color: getPermissionColor(perm.permission_level)
                  }"
                >
                  L{{ perm.permission_level }}
                </div>
                <div>
                  <h3 class="font-medium" style="color: var(--text-main);">{{ perm.permission_name }}</h3>
                  <p class="text-sm" style="color: var(--text-muted);">{{ perm.description }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <span
                  class="px-2 py-0.5 rounded text-xs font-medium"
                  :style="{
                    backgroundColor: perm.requires_confirm ? 'var(--color-warning)' + '20' : 'var(--color-success)' + '20',
                    color: perm.requires_confirm ? 'var(--color-warning)' : 'var(--color-success)'
                  }"
                >
                  {{ perm.requires_confirm ? '需确认' : '自动执行' }}
                </span>
                <button
                  @click="editPermission(perm)"
                  class="px-3 py-1.5 rounded text-xs"
                  style="background-color: var(--bg-hover); color: var(--text-main);"
                >
                  编辑
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'usage'">
      <!-- Token Usage Tab -->
      <div class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div
            class="p-4 rounded-lg border"
            :style="{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)' }"
          >
            <p class="text-sm" style="color: var(--text-muted);">今日请求</p>
            <p class="text-2xl font-bold mt-1" style="color: var(--text-main);">{{ usageStats.total_requests }}</p>
          </div>
          <div
            class="p-4 rounded-lg border"
            :style="{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)' }"
          >
            <p class="text-sm" style="color: var(--text-muted);">今日消耗</p>
            <p class="text-2xl font-bold mt-1" style="color: var(--color-primary);">${{ usageStats.total_cost.toFixed(4) }}</p>
          </div>
          <div
            class="p-4 rounded-lg border"
            :style="{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)' }"
          >
            <p class="text-sm" style="color: var(--text-muted);">输入 Tokens</p>
            <p class="text-2xl font-bold mt-1" style="color: var(--text-main);">{{ usageStats.input_tokens.toLocaleString() }}</p>
          </div>
          <div
            class="p-4 rounded-lg border"
            :style="{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)' }"
          >
            <p class="text-sm" style="color: var(--text-muted);">输出 Tokens</p>
            <p class="text-2xl font-bold mt-1" style="color: var(--text-main);">{{ usageStats.output_tokens.toLocaleString() }}</p>
          </div>
        </div>

        <div class="rounded-lg p-6" style="background-color: var(--bg-secondary); border: 1px solid var(--border-subtle);">
          <h2 class="text-lg font-semibold mb-4" style="color: var(--text-main);">用量趋势</h2>
          <div class="h-64 flex items-center justify-center" style="color: var(--text-muted);">
            图表区域 (需要 ECharts 或 Chart.js)
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'audit'">
      <!-- Audit Logs Tab -->
      <div class="rounded-lg p-6" style="background-color: var(--bg-secondary); border: 1px solid var(--border-subtle);">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">AI 操作审计日志</h2>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr style="border-bottom: 1px solid var(--border-subtle);">
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">时间</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">功能</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">模型</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">状态</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">延迟</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">Tokens</th>
                <th class="text-left py-3 px-4 font-medium" style="color: var(--text-muted);">成本</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="log in auditLogs"
                :key="log.id"
                style="border-bottom: 1px solid var(--border-subtle);"
              >
                <td class="py-3 px-4" style="color: var(--text-muted);">{{ formatTime(log.created_at) }}</td>
                <td class="py-3 px-4" style="color: var(--text-main);">{{ log.feature }}</td>
                <td class="py-3 px-4" style="color: var(--text-muted);">{{ getModelName(log.model_id) }}</td>
                <td class="py-3 px-4">
                  <span
                    class="px-2 py-0.5 rounded text-xs font-medium"
                    :style="getStatusStyle(log.status)"
                  >
                    {{ log.status }}
                  </span>
                </td>
                <td class="py-3 px-4" style="color: var(--text-main);">{{ log.latency_ms }}ms</td>
                <td class="py-3 px-4" style="color: var(--text-main);">{{ log.input_tokens + log.output_tokens }}</td>
                <td class="py-3 px-4" style="color: var(--text-main);">${{ log.cost_usd.toFixed(4) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import {
  CpuChipIcon,
  GlobeAltIcon,
  PuzzlePieceIcon,
  CodeBracketIcon,
  BookOpenIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  ClipboardDocumentListIcon
} from '@heroicons/vue/24/outline'

const api = axios.create({ baseURL: 'http://localhost:8000' })

const activeTab = ref('providers')

const tabs = [
  { id: 'providers', label: '服务商', icon: GlobeAltIcon },
  { id: 'models', label: '模型', icon: CpuChipIcon },
  { id: 'routing', label: '路由', icon: PuzzlePieceIcon },
  { id: 'prompts', label: '提示词', icon: CodeBracketIcon },
  { id: 'rag', label: 'RAG 上下文', icon: BookOpenIcon },
  { id: 'permissions', label: '权限', icon: ShieldCheckIcon },
  { id: 'usage', label: '用量统计', icon: ChartBarIcon },
  { id: 'audit', label: '审计日志', icon: ClipboardDocumentListIcon }
]

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

function getStatusStyle(status) {
  const styles = {
    success: { backgroundColor: 'var(--color-success)20', color: 'var(--color-success)' },
    error: { backgroundColor: 'var(--color-danger)20', color: 'var(--color-danger)' },
    fallback: { backgroundColor: 'var(--color-warning)20', color: 'var(--color-warning)' },
    cached: { backgroundColor: 'var(--color-primary)20', color: 'var(--color-primary)' }
  }
  return styles[status] || { backgroundColor: 'var(--bg-hover)', color: 'var(--text-muted)' }
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
