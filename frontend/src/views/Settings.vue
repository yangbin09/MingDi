<template>
  <div class="space-y-6">
    <!-- Tabs -->
    <div
      class="inline-flex gap-1 p-1 rounded-xl w-fit"
      :style="{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)' }"
    >
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="px-5 py-2 text-sm font-medium rounded-lg transition-all duration-200"
        :style="activeTab === tab.id
          ? { backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }
          : { color: 'var(--text-muted)' }"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Environment Variables Tab -->
    <div v-if="activeTab === 'env'" class="space-y-4">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-3">
          <div class="h-1 w-6 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-success), var(--color-primary))' }"></div>
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">环境变量</h2>
        </div>
        <button
          @click="openEnvModal()"
          class="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all"
          :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
        >
          <PlusIcon class="w-5 h-5" />
          新增变量
        </button>
      </div>

      <div class="card rounded-xl overflow-hidden">
        <div v-if="envVars.length === 0" class="text-center py-16">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
            <ShieldCheckIcon class="w-8 h-8" style="color: var(--text-muted); opacity: 0.5;" />
          </div>
          <p class="text-lg" style="color: var(--text-muted);">暂无环境变量</p>
          <p class="text-sm mt-1" style="color: var(--text-disabled);">配置敏感信息和全局变量</p>
        </div>
        <table v-else class="w-full">
          <thead :style="{ backgroundColor: 'var(--bg-tertiary)' }">
            <tr>
              <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">变量名</th>
              <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">值</th>
              <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">描述</th>
              <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider w-24" style="color: var(--text-muted);">保密</th>
              <th class="px-4 py-3.5 text-right text-xs font-semibold uppercase tracking-wider w-32" style="color: var(--text-muted);">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="env in envVars"
              :key="env.id"
              class="theme-transition"
              :style="{ borderBottom: '1px solid var(--border-subtle)' }"
              @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
              @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
            >
              <td class="px-4 py-4">
                <code class="text-sm px-2.5 py-1 rounded-lg font-mono" :style="{ backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }">{{ env.key }}</code>
              </td>
              <td class="px-4 py-4">
                <span v-if="env.is_secret" class="font-mono" style="color: var(--text-disabled);">••••••••</span>
                <span v-else class="text-sm font-mono" style="color: var(--text-main);">{{ env.value }}</span>
              </td>
              <td class="px-4 py-4 text-sm" style="color: var(--text-muted);">{{ env.description || '-' }}</td>
              <td class="px-4 py-4">
                <span
                  class="text-xs px-2 py-1 rounded-full"
                  :style="env.is_secret
                    ? { backgroundColor: 'var(--color-warning-subtle)', color: 'var(--color-warning)' }
                    : { backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }"
                >
                  {{ env.is_secret ? '是' : '否' }}
                </span>
              </td>
              <td class="px-4 py-4">
                <div class="flex items-center justify-end gap-1">
                  <button
                    @click="openEnvModal(env)"
                    class="p-2 rounded-lg transition-colors"
                    :style="{ color: 'var(--text-muted)' }"
                    @mouseenter="($event.currentTarget.style.color = 'var(--color-warning)', $event.currentTarget.style.backgroundColor = 'var(--color-warning-subtle)')"
                    @mouseleave="($event.currentTarget.style.color = 'var(--text-muted)', $event.currentTarget.style.backgroundColor = 'transparent')"
                  >
                    <PencilIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="deleteEnv(env)"
                    class="p-2 rounded-lg transition-colors"
                    :style="{ color: 'var(--text-muted)' }"
                    @mouseenter="($event.currentTarget.style.color = 'var(--color-danger)', $event.currentTarget.style.backgroundColor = 'var(--color-danger-subtle)')"
                    @mouseleave="($event.currentTarget.style.color = 'var(--text-muted)', $event.currentTarget.style.backgroundColor = 'transparent')"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Alerts Tab -->
    <div v-if="activeTab === 'alerts'" class="space-y-4">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-3">
          <div class="h-1 w-6 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-danger), var(--color-warning))' }"></div>
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">告警配置</h2>
        </div>
        <button
          @click="openAlertModal()"
          class="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all"
          :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
        >
          <PlusIcon class="w-5 h-5" />
          新增告警
        </button>
      </div>

      <div class="card rounded-xl overflow-hidden">
        <div v-if="alerts.length === 0" class="text-center py-16">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
            <BellIcon class="w-8 h-8" style="color: var(--text-muted); opacity: 0.5;" />
          </div>
          <p class="text-lg" style="color: var(--text-muted);">暂无告警配置</p>
          <p class="text-sm mt-1" style="color: var(--text-disabled);">配置 Webhook 接收任务失败通知</p>
        </div>
        <table v-else class="w-full">
          <thead :style="{ backgroundColor: 'var(--bg-tertiary)' }">
            <tr>
              <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">名称</th>
              <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">Webhook URL</th>
              <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">触发事件</th>
              <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider w-24" style="color: var(--text-muted);">状态</th>
              <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider w-20" style="color: var(--text-muted);">AI</th>
              <th class="px-4 py-3.5 text-right text-xs font-semibold uppercase tracking-wider w-32" style="color: var(--text-muted);">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="alert in alerts"
              :key="alert.id"
              class="theme-transition"
              :style="{ borderBottom: '1px solid var(--border-subtle)' }"
              @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
              @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
            >
              <td class="px-4 py-4 font-medium" style="color: var(--text-main);">{{ alert.name }}</td>
              <td class="px-4 py-4">
                <span class="text-xs font-mono truncate block max-w-xs" style="color: var(--text-muted);">{{ alert.webhook_url }}</span>
              </td>
              <td class="px-4 py-4">
                <div class="flex gap-1.5 flex-wrap">
                  <span
                    v-for="evt in alert.events.split(',')"
                    :key="evt"
                    class="px-2 py-0.5 text-xs rounded-full"
                    :style="evt.trim() === 'failed'
                      ? { backgroundColor: 'var(--color-danger-subtle)', color: 'var(--color-danger)' }
                      : { backgroundColor: 'var(--color-warning-subtle)', color: 'var(--color-warning)' }"
                  >
                    {{ evt.trim() }}
                  </span>
                </div>
              </td>
              <td class="px-4 py-4">
                <button
                  @click="toggleAlert(alert)"
                  class="relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-300"
                  :style="alert.is_active
                    ? { backgroundColor: 'var(--color-success-subtle)', border: '1px solid var(--color-success)' }
                    : { backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)' }"
                >
                  <span
                    class="inline-block h-4 w-4 transform rounded-full transition-all duration-300"
                    :style="{
                      backgroundColor: alert.is_active ? 'var(--color-success)' : 'var(--text-muted)',
                      transform: alert.is_active ? 'translateX(22px)' : 'translateX(2px)'
                    }"
                  />
                </button>
              </td>
              <td class="px-4 py-4">
                <div class="flex items-center gap-2">
                  <span
                    v-if="alert.ai_humanize"
                    class="flex items-center gap-1 text-xs px-2 py-1 rounded"
                    :style="{ backgroundColor: 'rgba(168, 85, 247, 0.15)', color: 'var(--color-purple)' }"
                    title="AI拟人化告警"
                  >
                    <SparklesIcon class="w-3 h-3" />
                    AI
                  </span>
                </div>
              </td>
              <td class="px-4 py-4">
                <div class="flex items-center justify-end gap-1">
                  <button
                    @click="openAlertModal(alert)"
                    class="p-2 rounded-lg transition-colors"
                    :style="{ color: 'var(--text-muted)' }"
                    @mouseenter="($event.currentTarget.style.color = 'var(--color-warning)', $event.currentTarget.style.backgroundColor = 'var(--color-warning-subtle)')"
                    @mouseleave="($event.currentTarget.style.color = 'var(--text-muted)', $event.currentTarget.style.backgroundColor = 'transparent')"
                  >
                    <PencilIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="deleteAlert(alert)"
                    class="p-2 rounded-lg transition-colors"
                    :style="{ color: 'var(--text-muted)' }"
                    @mouseenter="($event.currentTarget.style.color = 'var(--color-danger)', $event.currentTarget.style.backgroundColor = 'var(--color-danger-subtle)')"
                    @mouseleave="($event.currentTarget.style.color = 'var(--text-muted)', $event.currentTarget.style.backgroundColor = 'transparent')"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Export/Import Tab -->
    <div v-if="activeTab === 'export'" class="space-y-6">
      <div class="flex items-center gap-3">
        <div class="h-1 w-6 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-primary), var(--color-purple))' }"></div>
        <h2 class="text-lg font-semibold" style="color: var(--text-main);">导入导出配置</h2>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Export -->
        <div class="card-hover rounded-xl p-6">
          <div class="flex items-center gap-4 mb-5">
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center"
              :style="{ backgroundColor: 'var(--color-primary-subtle)', border: '1px solid var(--border-subtle)' }"
            >
              <ArrowDownTrayIcon class="w-6 h-6" style="color: var(--color-primary);" />
            </div>
            <div>
              <h3 class="font-semibold" style="color: var(--text-main);">导出配置</h3>
              <p class="text-sm" style="color: var(--text-muted);">下载所有任务、环境变量和告警配置</p>
            </div>
          </div>
          <button
            @click="exportConfig"
            class="w-full px-4 py-3 rounded-lg font-medium transition-all"
            :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--color-primary-hover)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'var(--color-primary)')"
          >
            导出 JSON 文件
          </button>
        </div>

        <!-- Import -->
        <div class="card-hover rounded-xl p-6">
          <div class="flex items-center gap-4 mb-5">
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center"
              :style="{ backgroundColor: 'var(--color-success-subtle)', border: '1px solid var(--border-subtle)' }"
            >
              <ArrowUpTrayIcon class="w-6 h-6" style="color: var(--color-success);" />
            </div>
            <div>
              <h3 class="font-semibold" style="color: var(--text-main);">导入配置</h3>
              <p class="text-sm" style="color: var(--text-muted);">从 JSON 文件恢复所有配置</p>
            </div>
          </div>
          <label class="block">
            <input type="file" accept=".json" @change="importConfig" class="hidden" ref="importFile" />
            <span
              class="w-full px-4 py-3 rounded-lg font-medium transition-all cursor-pointer inline-block text-center"
              :style="{ backgroundColor: 'var(--color-success)', color: 'var(--text-inverse)' }"
            >
              选择 JSON 文件导入
            </span>
          </label>
        </div>
      </div>
    </div>

    <!-- AI Settings Tab -->
    <div v-if="activeTab === 'ai'" class="space-y-6">
      <div class="flex items-center gap-3">
        <div class="h-1 w-6 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-purple), var(--color-primary))' }"></div>
        <h2 class="text-lg font-semibold" style="color: var(--text-main);">AI 与告警设置</h2>
      </div>

      <!-- Minimax API Configuration -->
      <div class="card rounded-xl p-6">
        <div class="flex items-center gap-4 mb-5">
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center"
            :style="{ backgroundColor: 'rgba(168, 85, 247, 0.15)', border: '1px solid var(--border-subtle)' }"
          >
            <SparklesIcon class="w-6 h-6" style="color: var(--color-purple);" />
          </div>
          <div>
            <h3 class="font-semibold" style="color: var(--text-main);">Minimax API 配置</h3>
            <p class="text-sm" style="color: var(--text-muted);">配置大模型 API 凭证以启用 AI 功能</p>
          </div>
          <div class="ml-auto">
            <span
              class="px-3 py-1 text-xs font-medium rounded-full"
              :style="aiSettings.ai_enabled
                ? { backgroundColor: 'var(--color-success-subtle)', color: 'var(--color-success)' }
                : { backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }"
            >
              {{ aiSettings.ai_enabled ? '已启用' : '未启用' }}
            </span>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">API Key</label>
            <input
              v-model="aiSettings.minimax_api_key"
              type="password"
              class="input font-mono text-sm"
              placeholder="输入您的 Minimax API Key"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">Group ID</label>
            <input
              v-model="aiSettings.minimax_group_id"
              type="text"
              class="input font-mono text-sm"
              placeholder="输入您的 Minimax Group ID"
            />
          </div>

          <div class="flex items-center gap-3 pt-2">
            <button
              @click="testAIConnection"
              :disabled="aiTesting || !aiSettings.minimax_api_key || !aiSettings.minimax_group_id"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2"
              :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-main)', border: '1px solid var(--border-subtle)' }"
              :class="{ 'opacity-50': aiTesting }"
            >
              <SparklesIcon v-if="!aiTesting" class="w-4 h-4" />
              <span v-if="aiTesting" class="animate-spin">⟳</span>
              {{ aiTesting ? '测试中...' : '测试连接' }}
            </button>
            <button
              @click="saveAISettings"
              :disabled="aiSettingsSaved"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
              :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
            >
              {{ aiSettingsSaved ? '已保存' : '保存配置' }}
            </button>
          </div>

          <div v-if="aiTestResult" class="mt-3 p-3 rounded-lg text-sm" :style="aiTestResult.success
            ? { backgroundColor: 'var(--color-success-subtle)', color: 'var(--color-success)' }
            : { backgroundColor: 'var(--color-danger-subtle)', color: 'var(--color-danger)' }">
            {{ aiTestResult.message }}
          </div>
        </div>
      </div>

      <!-- AI Features Info -->
      <div class="card rounded-xl p-6">
        <h3 class="font-semibold mb-4" style="color: var(--text-main);">支持的 AI 功能</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="p-3 rounded-lg" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
            <div class="flex items-center gap-2 mb-1">
              <SparklesIcon class="w-4 h-4" style="color: var(--color-primary);" />
              <span class="text-sm font-medium" style="color: var(--text-main);">Text-to-Script</span>
            </div>
            <p class="text-xs" style="color: var(--text-muted);">自然语言生成 Python 脚本</p>
          </div>
          <div class="p-3 rounded-lg" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
            <div class="flex items-center gap-2 mb-1">
              <SparklesIcon class="w-4 h-4" style="color: var(--color-purple);" />
              <span class="text-sm font-medium" style="color: var(--text-main);">AI 代码审查</span>
            </div>
            <p class="text-xs" style="color: var(--text-muted);">代码性能与安全检查</p>
          </div>
          <div class="p-3 rounded-lg" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
            <div class="flex items-center gap-2 mb-1">
              <SparklesIcon class="w-4 h-4" style="color: var(--color-warning);" />
              <span class="text-sm font-medium" style="color: var(--text-main);">错误诊断</span>
            </div>
            <p class="text-xs" style="color: var(--text-muted);">智能错误分析与修复建议</p>
          </div>
          <div class="p-3 rounded-lg" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
            <div class="flex items-center gap-2 mb-1">
              <SparklesIcon class="w-4 h-4" style="color: var(--color-success);" />
              <span class="text-sm font-medium" style="color: var(--text-main);">NLP to Cron</span>
            </div>
            <p class="text-xs" style="color: var(--text-muted);">自然语言转 Cron 表达式</p>
          </div>
          <div class="p-3 rounded-lg" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
            <div class="flex items-center gap-2 mb-1">
              <SparklesIcon class="w-4 h-4" style="color: var(--color-cyan);" />
              <span class="text-sm font-medium" style="color: var(--text-main);">日志摘要</span>
            </div>
            <p class="text-xs" style="color: var(--text-muted);">AI 提炼日志关键信息</p>
          </div>
          <div class="p-3 rounded-lg" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
            <div class="flex items-center gap-2 mb-1">
              <SparklesIcon class="w-4 h-4" style="color: var(--color-blue);" />
              <span class="text-sm font-medium" style="color: var(--text-main);">拟人化告警</span>
            </div>
            <p class="text-xs" style="color: var(--text-muted);">友好的告警消息推送</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Env Var Modal -->
    <div v-if="showEnvModal" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 backdrop-blur-sm" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }" @click="closeEnvModal"></div>
      <div
        class="absolute right-0 top-0 h-full w-full max-w-md theme-transition"
        :style="{ backgroundColor: 'var(--bg-secondary)', borderLeft: '1px solid var(--border-subtle)' }"
      >
        <div class="flex items-center justify-between p-5" :style="{ borderBottom: '1px solid var(--border-subtle)' }">
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">{{ editingEnv ? '编辑变量' : '新增变量' }}</h2>
          <button @click="closeEnvModal" class="p-2 rounded-lg transition-colors" :style="{ color: 'var(--text-muted)' }">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="p-5 overflow-y-auto" :style="{ height: 'calc(100vh - 73px)' }">
          <form @submit.prevent="saveEnv" class="space-y-5">
            <div>
              <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">变量名</label>
              <input v-model="envForm.key" type="text" required class="input font-mono" placeholder="API_KEY" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">变量值</label>
              <input v-model="envForm.value" type="text" required class="input font-mono" placeholder="your-secret-value" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">描述</label>
              <input v-model="envForm.description" type="text" class="input" placeholder="可选描述信息" />
            </div>
            <div class="flex items-center gap-2">
              <input v-model="envForm.is_secret" type="checkbox" id="is_secret" class="w-4 h-4" :style="{ accentColor: 'var(--color-primary)' }" />
              <label for="is_secret" class="text-sm" style="color: var(--text-muted);">保密模式（界面上隐藏值）</label>
            </div>
            <div class="flex gap-3 pt-4" :style="{ borderTop: '1px solid var(--border-subtle)' }">
              <button type="button" @click="closeEnvModal" class="flex-1 px-4 py-2.5 rounded-lg transition-all" :style="{ border: '1px solid var(--border-subtle)', color: 'var(--text-main)' }">取消</button>
              <button type="submit" class="flex-1 px-4 py-2.5 rounded-lg font-medium transition-all" :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Alert Modal -->
    <div v-if="showAlertModal" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 backdrop-blur-sm" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }" @click="closeAlertModal"></div>
      <div
        class="absolute right-0 top-0 h-full w-full max-w-md theme-transition"
        :style="{ backgroundColor: 'var(--bg-secondary)', borderLeft: '1px solid var(--border-subtle)' }"
      >
        <div class="flex items-center justify-between p-5" :style="{ borderBottom: '1px solid var(--border-subtle)' }">
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">{{ editingAlert ? '编辑告警' : '新增告警' }}</h2>
          <button @click="closeAlertModal" class="p-2 rounded-lg transition-colors" :style="{ color: 'var(--text-muted)' }">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="p-5 overflow-y-auto" :style="{ height: 'calc(100vh - 73px)' }">
          <form @submit.prevent="saveAlert" class="space-y-5">
            <div>
              <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">告警名称</label>
              <input v-model="alertForm.name" type="text" required class="input" placeholder="钉钉机器人" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">Webhook URL</label>
              <input v-model="alertForm.webhook_url" type="url" required class="input font-mono text-sm" placeholder="https://oapi.dingtalk.com/robot/send?access_token=..." />
            </div>
            <div>
              <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">触发事件</label>
              <div class="flex gap-4">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input v-model="alertEvents" type="checkbox" value="failed" class="w-4 h-4" :style="{ accentColor: 'var(--color-danger)' }" />
                  <span class="text-sm" style="color: var(--color-danger);">失败</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input v-model="alertEvents" type="checkbox" value="timeout" class="w-4 h-4" :style="{ accentColor: 'var(--color-warning)' }" />
                  <span class="text-sm" style="color: var(--color-warning);">超时</span>
                </label>
              </div>
            </div>

            <!-- AI Humanized Alert -->
            <div class="rounded-lg p-3" :style="{ backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)' }">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <SparklesIcon class="w-4 h-4" :style="{ color: 'var(--color-purple)' }" />
                  <div>
                    <span class="text-sm font-medium" style="color: var(--text-main);">AI 拟人化告警</span>
                    <p class="text-xs" style="color: var(--text-disabled);">将冷冰冰的错误信息转化为友好的提示</p>
                  </div>
                </div>
                <button
                  type="button"
                  @click="alertForm.ai_humanize = !alertForm.ai_humanize"
                  class="relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-300"
                  :style="alertForm.ai_humanize
                    ? { backgroundColor: 'rgba(168, 85, 247, 0.2)', border: '1px solid var(--color-purple)' }
                    : { backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)' }"
                >
                  <span
                    class="inline-block h-4 w-4 transform rounded-full transition-all duration-300"
                    :style="{
                      backgroundColor: alertForm.ai_humanize ? 'var(--color-purple)' : 'var(--text-muted)',
                      transform: alertForm.ai_humanize ? 'translateX(22px)' : 'translateX(2px)'
                    }"
                  />
                </button>
              </div>
            </div>
            <div class="flex gap-3 pt-4" :style="{ borderTop: '1px solid var(--border-subtle)' }">
              <button type="button" @click="closeAlertModal" class="flex-1 px-4 py-2.5 rounded-lg transition-all" :style="{ border: '1px solid var(--border-subtle)', color: 'var(--text-main)' }">取消</button>
              <button type="submit" class="flex-1 px-4 py-2.5 rounded-lg font-medium transition-all" :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import {
  PlusIcon, PencilIcon, TrashIcon, XMarkIcon,
  ShieldCheckIcon, BellIcon, ArrowDownTrayIcon, ArrowUpTrayIcon,
  SparklesIcon
} from '@heroicons/vue/24/outline'

const api = axios.create({ baseURL: 'http://localhost:8000' })

const tabs = [
  { id: 'env', label: '环境变量' },
  { id: 'alerts', label: '告警配置' },
  { id: 'ai', label: 'AI 设置' },
  { id: 'export', label: '导入导出' }
]
const activeTab = ref('env')

const envVars = ref([])
const alerts = ref([])

const showEnvModal = ref(false)
const showAlertModal = ref(false)
const editingEnv = ref(null)
const editingAlert = ref(null)
const alertEvents = ref(['failed', 'timeout'])

const envForm = reactive({ key: '', value: '', description: '', is_secret: false })
const alertForm = reactive({ name: '', webhook_url: '', events: 'failed,timeout', is_active: true, ai_humanize: false })

const importFile = ref(null)

// AI Settings
const aiSettings = reactive({
  minimax_api_key: '',
  minimax_group_id: '',
  ai_enabled: false
})
const aiSettingsSaved = ref(false)
const aiTesting = ref(false)
const aiTestResult = ref(null)

async function fetchEnvVars() {
  try { const res = await api.get('/env-vars'); envVars.value = res.data }
  catch (e) { console.error(e) }
}

async function fetchAlerts() {
  try { const res = await api.get('/alerts'); alerts.value = res.data }
  catch (e) { console.error(e) }
}

function openEnvModal(env = null) {
  editingEnv.value = env
  if (env) {
    envForm.key = env.key; envForm.value = env.value
    envForm.description = env.description || ''; envForm.is_secret = env.is_secret
  } else {
    envForm.key = ''; envForm.value = ''; envForm.description = ''; envForm.is_secret = false
  }
  showEnvModal.value = true
}

function closeEnvModal() { showEnvModal.value = false; editingEnv.value = null }

async function saveEnv() {
  try {
    if (editingEnv.value) { await api.put(`/env-vars/${editingEnv.value.id}`, envForm) }
    else { await api.post('/env-vars', envForm) }
    closeEnvModal(); fetchEnvVars()
  } catch (e) { alert('保存失败: ' + (e.response?.data?.detail || e.message)) }
}

async function deleteEnv(env) {
  if (!confirm(`确定删除变量 "${env.key}" 吗？`)) return
  try { await api.delete(`/env-vars/${env.id}`); fetchEnvVars() }
  catch (e) { console.error(e) }
}

function openAlertModal(alert = null) {
  editingAlert.value = alert
  if (alert) {
    alertForm.name = alert.name; alertForm.webhook_url = alert.webhook_url
    alertForm.is_active = alert.is_active
    alertForm.ai_humanize = alert.ai_humanize || false
    alertEvents.value = alert.events.split(',').map(e => e.trim())
  } else {
    alertForm.name = ''; alertForm.webhook_url = ''; alertForm.is_active = true
    alertForm.ai_humanize = false
    alertEvents.value = ['failed', 'timeout']
  }
  showAlertModal.value = true
}

function closeAlertModal() { showAlertModal.value = false; editingAlert.value = null }

async function saveAlert() {
  alertForm.events = alertEvents.value.join(',')
  try {
    if (editingAlert.value) { await api.put(`/alerts/${editingAlert.value.id}`, alertForm) }
    else { await api.post('/alerts', alertForm) }
    closeAlertModal(); fetchAlerts()
  } catch (e) { alert('保存失败: ' + (e.response?.data?.detail || e.message)) }
}

async function deleteAlert(alert) {
  if (!confirm(`确定删除告警 "${alert.name}" 吗？`)) return
  try { await api.delete(`/alerts/${alert.id}`); fetchAlerts() }
  catch (e) { console.error(e) }
}

async function toggleAlert(alert) {
  try { await api.put(`/alerts/${alert.id}`, { is_active: !alert.is_active }); fetchAlerts() }
  catch (e) { console.error(e) }
}

async function exportConfig() {
  try {
    const res = await api.get('/export')
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `pycron-config-${new Date().toISOString().slice(0, 10)}.json`
    a.click(); URL.revokeObjectURL(url)
  } catch (e) { alert('导出失败: ' + e.message) }
}

async function importConfig(event) {
  const file = event.target.files[0]
  if (!file) return
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    const res = await api.post('/import', data)
    alert(`导入成功！任务: ${res.data.tasks_imported}, 变量: ${res.data.env_vars_imported}, 告警: ${res.data.alerts_imported}`)
    fetchEnvVars(); fetchAlerts()
  } catch (e) { alert('导入失败: ' + (e.response?.data?.detail || e.message)) }
  event.target.value = ''
}

async function fetchAISettings() {
  try {
    const res = await api.get('/system/settings')
    aiSettings.minimax_api_key = res.data.minimax_api_key || ''
    aiSettings.minimax_group_id = res.data.minimax_group_id || ''
    aiSettings.ai_enabled = res.data.ai_enabled || false
  } catch (e) { console.error(e) }
}

async function saveAISettings() {
  try {
    await api.put('/system/settings', {
      minimax_api_key: aiSettings.minimax_api_key,
      minimax_group_id: aiSettings.minimax_group_id
    })
    aiSettingsSaved.value = true
    aiSettings.ai_enabled = !!(aiSettings.minimax_api_key && aiSettings.minimax_group_id)
    setTimeout(() => { aiSettingsSaved.value = false }, 2000)
  } catch (e) { alert('保存失败: ' + (e.response?.data?.detail || e.message)) }
}

async function testAIConnection() {
  aiTesting.value = true
  aiTestResult.value = null
  try {
    // First save current settings
    await api.put('/system/settings', {
      minimax_api_key: aiSettings.minimax_api_key,
      minimax_group_id: aiSettings.minimax_group_id
    })
    // Then test
    const res = await api.post('/system/settings/test-ai')
    aiTestResult.value = res.data
    aiSettings.ai_enabled = res.data.success
  } catch (e) {
    aiTestResult.value = { success: false, message: '测试失败: ' + (e.response?.data?.detail || e.message) }
  } finally {
    aiTesting.value = false
  }
}

onMounted(() => { fetchEnvVars(); fetchAlerts(); fetchAISettings() })
</script>
