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
            <el-button type="primary" @click="openProviderModal()">
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
                <el-button size="small" @click="openProviderModal(provider)">编辑</el-button>
                <el-button size="small" type="danger" plain @click="handleDeleteProvider(provider.id)">删除</el-button>
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
            <el-button type="primary" @click="openModelModal()">
              <el-icon><Plus /></el-icon>
              添加模型
            </el-button>
          </div>
        </template>

        <el-table :data="models" :stripe="!isDarkTheme" style="width: 100%">
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
          <el-table-column label="操作" width="120" align="right">
            <template #default="{ row }">
              <el-button size="small" @click="openModelModal(row)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="handleDeleteModel(row.id)">删除</el-button>
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
            <el-button type="primary" @click="openRoutingModal()">
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
              <div class="routing-actions">
                <el-button size="small" @click="openRoutingModal(routing)">编辑</el-button>
                <el-button size="small" type="danger" plain @click="handleDeleteRouting(routing.id)">删除</el-button>
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
            <el-button type="primary" @click="openPromptModal()">
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
                  <el-button size="small" @click="openPromptModal(template)">编辑</el-button>
                  <el-button size="small" type="danger" plain @click="handleDeletePrompt(template.id)">删除</el-button>
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
            <el-button type="primary" @click="openRagModal()">
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
                <div class="flex gap-2">
                  <el-button size="small" @click="openRagModal(rag)">编辑</el-button>
                  <el-button size="small" type="danger" plain @click="handleDeleteRag(rag.id)">删除</el-button>
                </div>
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
            <el-button type="primary" @click="openPermissionModal()">
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
                  <el-button size="small" @click="openPermissionModal(perm)">编辑</el-button>
                  <el-button size="small" type="danger" plain @click="handleDeletePermission(perm.id)">删除</el-button>
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

        <el-table :data="auditLogs" :stripe="!isDarkTheme" style="width: 100%">
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

    <!-- Provider Dialog -->
    <el-dialog v-model="showProviderModal" :title="editingProvider ? '编辑服务商' : '添加服务商'" width="500px">
      <el-form label-position="top">
        <el-form-item label="服务商名称" required>
          <el-input v-model="providerForm.name" placeholder="ollama" />
        </el-form-item>
        <el-form-item label="显示名称" required>
          <el-input v-model="providerForm.display_name" placeholder="Ollama" />
        </el-form-item>
        <el-form-item label="API Base URL">
          <el-input v-model="providerForm.api_base_url" placeholder="http://localhost:11434" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="providerForm.api_key" placeholder="可选" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="providerForm.is_enabled">启用</el-checkbox>
          <el-checkbox v-model="providerForm.is_primary">主服务商</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeProviderModal">取消</el-button>
        <el-button type="primary" @click="handleSaveProvider">保存</el-button>
      </template>
    </el-dialog>

    <!-- Model Dialog -->
    <el-dialog v-model="showModelModal" :title="editingModel ? '编辑模型' : '添加模型'" width="500px">
      <el-form label-position="top">
        <el-form-item label="服务商">
          <el-select v-model="modelForm.provider_id" class="w-full">
            <el-option v-for="p in providers" :key="p.id" :label="p.display_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型标识符" required>
          <el-input v-model="modelForm.model_id" placeholder="llama3" />
        </el-form-item>
        <el-form-item label="显示名称" required>
          <el-input v-model="modelForm.display_name" placeholder="Llama 3" />
        </el-form-item>
        <el-form-item label="模型类型" required>
          <el-select v-model="modelForm.model_type" class="w-full">
            <el-option label="Chat" value="chat" />
            <el-option label="Completion" value="completion" />
          </el-select>
        </el-form-item>
        <el-form-item label="上下文窗口">
          <el-input-number v-model="modelForm.context_window" :min="0" class="w-full" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="modelForm.is_enabled">启用</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeModelModal">取消</el-button>
        <el-button type="primary" @click="handleSaveModel">保存</el-button>
      </template>
    </el-dialog>

    <!-- Routing Dialog -->
    <el-dialog v-model="showRoutingModal" :title="editingRouting ? '编辑路由' : '添加路由'" width="500px">
      <el-form label-position="top">
        <el-form-item label="功能标识" required>
          <el-input v-model="routingForm.feature" placeholder="generate_script" />
        </el-form-item>
        <el-form-item label="显示名称" required>
          <el-input v-model="routingForm.display_name" placeholder="脚本生成" />
        </el-form-item>
        <el-form-item label="主模型">
          <el-select v-model="routingForm.primary_model_id" placeholder="选择模型" class="w-full">
            <el-option v-for="m in models" :key="m.id" :label="m.display_name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="routingForm.is_enabled">启用</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeRoutingModal">取消</el-button>
        <el-button type="primary" @click="handleSaveRouting">保存</el-button>
      </template>
    </el-dialog>

    <!-- Prompt Template Dialog -->
    <el-dialog v-model="showPromptModal" :title="editingPrompt ? '编辑模板' : '添加模板'" width="600px">
      <el-form label-position="top">
        <el-form-item label="功能标识" required>
          <el-input v-model="promptForm.feature" placeholder="generate_script" />
        </el-form-item>
        <el-form-item label="显示名称" required>
          <el-input v-model="promptForm.display_name" placeholder="脚本生成" />
        </el-form-item>
        <el-form-item label="系统提示词">
          <el-input v-model="promptForm.system_prompt" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="用户模板">
          <el-input v-model="promptForm.user_template" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="参数配置">
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="温度">
                <el-input-number v-model="promptForm.temperature" :min="0" :max="2" :step="0.1" class="w-full" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Top P">
                <el-input-number v-model="promptForm.top_p" :min="0" :max="1" :step="0.1" class="w-full" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="最大Tokens">
                <el-input-number v-model="promptForm.max_tokens" :min="100" :max="32000" class="w-full" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="promptForm.is_enabled">启用</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closePromptModal">取消</el-button>
        <el-button type="primary" @click="handleSavePrompt">保存</el-button>
      </template>
    </el-dialog>

    <!-- RAG Context Dialog -->
    <el-dialog v-model="showRagModal" :title="editingRag ? '编辑上下文' : '添加上下文'" width="600px">
      <el-form label-position="top">
        <el-form-item label="上下文类型" required>
          <el-select v-model="ragForm.context_type" class="w-full">
            <el-option label="代码片段" value="code" />
            <el-option label="文档" value="doc" />
            <el-option label="知识库" value="knowledge" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="上下文键" required>
          <el-input v-model="ragForm.context_key" placeholder="unique_key" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="ragForm.content" type="textarea" :rows="6" />
        </el-form-item>
        <el-form-item label="注入位置">
          <el-select v-model="ragForm.injection_position" class="w-full">
            <el-option label="系统提示词" value="system" />
            <el-option label="用户消息" value="user" />
            <el-option label="上下文" value="context" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="ragForm.is_enabled">启用</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeRagModal">取消</el-button>
        <el-button type="primary" @click="handleSaveRag">保存</el-button>
      </template>
    </el-dialog>

    <!-- Permission Dialog -->
    <el-dialog v-model="showPermissionModal" :title="editingPermission ? '编辑权限' : '添加权限'" width="500px">
      <el-form label-position="top">
        <el-form-item label="权限等级" required>
          <el-input-number v-model="permissionForm.permission_level" :min="1" :max="3" class="w-full" />
        </el-form-item>
        <el-form-item label="权限名称" required>
          <el-input v-model="permissionForm.permission_name" placeholder="完全自主" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="permissionForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="permissionForm.requires_confirm">需要确认</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closePermissionModal">取消</el-button>
        <el-button type="primary" @click="handleSavePermission">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessageBox } from 'element-plus'
import {
  Cpu, Box, Connection, ChatDotRound, Document, Lock,
  DataLine, List, Plus, MagicStick
} from '@element-plus/icons-vue'
import { useAIHub } from '../composables/useAIHub.ts'
import type {
  ProviderFormData,
  ModelFormData,
  RoutingFormData,
  PromptFormData,
  RAGFormData,
  PermissionFormData
} from '../composables/useAIHub.ts'

// ============= Composable 使用 =============
const {
  providers, models, featureRouting, promptTemplates, ragContexts,
  permissions, auditLogs, usageStats,
  getModelName, getPermissionColor, getStatusType, formatTime,
  loadAll
} = useAIHub()

// ============= 主题判断 =============
const isDarkTheme = computed(() => {
  return document.documentElement.classList.contains('dark') ||
    ['darcula', 'xuanmo', 'anying', 'gruvbox'].includes(
      document.documentElement.getAttribute('data-theme') || ''
    )
})

const activeTab = ref('providers')

// ============= Modals =============
const showProviderModal = ref(false)
const showModelModal = ref(false)
const showRoutingModal = ref(false)
const showPromptModal = ref(false)
const showRagModal = ref(false)
const showPermissionModal = ref(false)

// ============= Editing State =============
const editingProvider = ref<any>(null)
const editingModel = ref<any>(null)
const editingRouting = ref<any>(null)
const editingPrompt = ref<any>(null)
const editingRag = ref<any>(null)
const editingPermission = ref<any>(null)

// ============= Forms =============
const providerForm = reactive<ProviderFormData>({
  name: '', display_name: '', api_base_url: '', api_key: '', is_enabled: true, is_primary: false
})

const modelForm = reactive<ModelFormData>({
  provider_id: null, model_id: '', display_name: '', model_type: 'chat', context_window: null, is_enabled: true
})

const routingForm = reactive<RoutingFormData>({
  feature: '', display_name: '', primary_model_id: null, is_enabled: true
})

const promptForm = reactive<PromptFormData>({
  feature: '', display_name: '', system_prompt: '', user_template: '',
  temperature: 0.7, top_p: 0.9, max_tokens: 2048, context_lines: 100, is_enabled: true
})

const ragForm = reactive<RAGFormData>({
  context_type: 'code', context_key: '', content: '', injection_position: 'system', is_enabled: true
})

const permissionForm = reactive<PermissionFormData>({
  permission_level: 1, permission_name: '', description: '', requires_confirm: true, is_enabled: true
})

// ============= Provider CRUD =============
function openProviderModal(provider: any = null) {
  editingProvider.value = provider
  if (provider) {
    Object.assign(providerForm, {
      name: provider.name, display_name: provider.display_name,
      api_base_url: provider.api_base_url || '', api_key: provider.api_key || '',
      is_enabled: provider.is_enabled, is_primary: provider.is_primary
    })
  } else {
    Object.assign(providerForm, { name: '', display_name: '', api_base_url: '', api_key: '', is_enabled: true, is_primary: false })
  }
  showProviderModal.value = true
}

function closeProviderModal() {
  showProviderModal.value = false
  editingProvider.value = null
}

async function handleSaveProvider() {
  const { saveProvider } = useAIHub()
  await saveProvider(editingProvider.value?.id || null, providerForm)
  closeProviderModal()
}

async function handleDeleteProvider(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该服务商吗？', '提示', { type: 'warning' })
    const { deleteProvider } = useAIHub()
    await deleteProvider(id)
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

// ============= Model CRUD =============
function openModelModal(model: any = null) {
  editingModel.value = model
  if (model) {
    Object.assign(modelForm, {
      provider_id: model.provider_id, model_id: model.model_id,
      display_name: model.display_name, model_type: model.model_type,
      context_window: model.context_window, is_enabled: model.is_enabled
    })
  } else {
    Object.assign(modelForm, { provider_id: null, model_id: '', display_name: '', model_type: 'chat', context_window: null, is_enabled: true })
  }
  showModelModal.value = true
}

function closeModelModal() {
  showModelModal.value = false
  editingModel.value = null
}

async function handleSaveModel() {
  const { saveModel } = useAIHub()
  await saveModel(editingModel.value?.id || null, modelForm)
  closeModelModal()
}

async function handleDeleteModel(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该模型吗？', '提示', { type: 'warning' })
    const { deleteModel } = useAIHub()
    await deleteModel(id)
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

// ============= Routing CRUD =============
function openRoutingModal(routing: any = null) {
  editingRouting.value = routing
  if (routing) {
    Object.assign(routingForm, {
      feature: routing.feature, display_name: routing.display_name,
      primary_model_id: routing.primary_model_id, is_enabled: routing.is_enabled
    })
  } else {
    Object.assign(routingForm, { feature: '', display_name: '', primary_model_id: null, is_enabled: true })
  }
  showRoutingModal.value = true
}

function closeRoutingModal() {
  showRoutingModal.value = false
  editingRouting.value = null
}

async function handleSaveRouting() {
  const { saveRouting } = useAIHub()
  await saveRouting(editingRouting.value?.id || null, routingForm)
  closeRoutingModal()
}

async function handleDeleteRouting(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该路由吗？', '提示', { type: 'warning' })
    const { deleteRouting } = useAIHub()
    await deleteRouting(id)
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

// ============= Prompt CRUD =============
function openPromptModal(template: any = null) {
  editingPrompt.value = template
  if (template) {
    Object.assign(promptForm, {
      feature: template.feature, display_name: template.display_name,
      system_prompt: template.system_prompt || '', user_template: template.user_template || '',
      temperature: template.temperature, top_p: template.top_p, max_tokens: template.max_tokens,
      context_lines: template.context_lines, is_enabled: template.is_enabled
    })
  } else {
    Object.assign(promptForm, { feature: '', display_name: '', system_prompt: '', user_template: '', temperature: 0.7, top_p: 0.9, max_tokens: 2048, context_lines: 100, is_enabled: true })
  }
  showPromptModal.value = true
}

function closePromptModal() {
  showPromptModal.value = false
  editingPrompt.value = null
}

async function handleSavePrompt() {
  const { savePrompt } = useAIHub()
  await savePrompt(editingPrompt.value?.id || null, promptForm)
  closePromptModal()
}

async function handleDeletePrompt(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该模板吗？', '提示', { type: 'warning' })
    const { deletePrompt } = useAIHub()
    await deletePrompt(id)
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

// ============= RAG CRUD =============
function openRagModal(rag: any = null) {
  editingRag.value = rag
  if (rag) {
    Object.assign(ragForm, {
      context_type: rag.context_type, context_key: rag.context_key,
      content: rag.content, injection_position: rag.injection_position, is_enabled: rag.is_enabled
    })
  } else {
    Object.assign(ragForm, { context_type: 'code', context_key: '', content: '', injection_position: 'system', is_enabled: true })
  }
  showRagModal.value = true
}

function closeRagModal() {
  showRagModal.value = false
  editingRag.value = null
}

async function handleSaveRag() {
  const { saveRag } = useAIHub()
  await saveRag(editingRag.value?.id || null, ragForm)
  closeRagModal()
}

async function handleDeleteRag(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该上下文吗？', '提示', { type: 'warning' })
    const { deleteRag } = useAIHub()
    await deleteRag(id)
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

// ============= Permission CRUD =============
function openPermissionModal(perm: any = null) {
  editingPermission.value = perm
  if (perm) {
    Object.assign(permissionForm, {
      permission_level: perm.permission_level, permission_name: perm.permission_name,
      description: perm.description || '', requires_confirm: perm.requires_confirm, is_enabled: perm.is_enabled
    })
  } else {
    Object.assign(permissionForm, { permission_level: 1, permission_name: '', description: '', requires_confirm: true, is_enabled: true })
  }
  showPermissionModal.value = true
}

function closePermissionModal() {
  showPermissionModal.value = false
  editingPermission.value = null
}

async function handleSavePermission() {
  const { savePermission } = useAIHub()
  await savePermission(editingPermission.value?.id || null, permissionForm)
  closePermissionModal()
}

async function handleDeletePermission(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该权限吗？', '提示', { type: 'warning' })
    const { deletePermission } = useAIHub()
    await deletePermission(id)
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

// ============= 初始化 =============
onMounted(() => {
  loadAll()
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
.routing-actions,
.rag-footer,
.perm-status {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 12px;
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
