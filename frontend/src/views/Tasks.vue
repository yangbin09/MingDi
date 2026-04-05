<template>
  <div class="space-y-6">
    <!-- Header Actions -->
    <div class="flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="h-1 w-8 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-primary), var(--color-success))' }"></div>
        <span class="text-sm" style="color: var(--text-muted);">共 <span style="color: var(--text-main); font-weight: 500;">{{ tasks.length }}</span> 个任务</span>
      </div>
      <div class="flex items-center gap-2">
        <!-- Node Flow Editor Button -->
        <button
          @click="showNodeFlowEditor = true"
          class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all"
          :style="{ backgroundColor: 'var(--bg-secondary)', color: 'var(--color-purple)', border: '1px solid var(--border-subtle)' }"
          @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
          @mouseleave="($event.currentTarget.style.backgroundColor = 'var(--bg-secondary)')"
        >
          <ViewColumnsIcon class="w-4 h-4" />
          节点编排
        </button>
        <button
          @click="openCreateDrawer"
          class="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200"
          :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
          @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--color-primary-hover)')"
          @mouseleave="($event.currentTarget.style.backgroundColor = 'var(--color-primary)')"
        >
          <PlusIcon class="w-5 h-5" />
          新建任务
        </button>
      </div>
    </div>

    <!-- Tasks Table -->
    <div class="card rounded-xl overflow-hidden theme-transition">
      <div v-if="tasks.length === 0" class="text-center py-20">
        <div class="w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
          <InboxIcon class="w-10 h-10" style="color: var(--text-muted); opacity: 0.5;" />
        </div>
        <p class="text-lg" style="color: var(--text-muted);">暂无任务</p>
        <p class="text-sm mt-1" style="color: var(--text-disabled);">点击右上角按钮创建第一个任务</p>
      </div>

      <table v-else class="w-full">
        <thead :style="{ backgroundColor: 'var(--bg-tertiary)' }">
          <tr>
            <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider w-12" style="color: var(--text-muted);">
              <span class="relative flex h-3 w-3 justify-center">
                <span v-if="runningCount > 0" class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :style="{ backgroundColor: 'var(--color-primary)' }"></span>
              </span>
            </th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">任务</th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">依赖</th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider w-36" style="color: var(--text-muted);">定时</th>
            <th class="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider w-24" style="color: var(--text-muted);">启用</th>
            <th class="px-4 py-3.5 text-right text-xs font-semibold uppercase tracking-wider w-48" style="color: var(--text-muted);">操作</th>
          </tr>
        </thead>
        <tbody style="borderTop: '1px solid var(--border-subtle)'">
          <tr
            v-for="task in tasks"
            :key="task.id"
            class="theme-transition"
            :style="{
              backgroundColor: task.status === 'running' ? 'var(--color-primary-subtle)' : 'transparent',
              borderBottom: '1px solid var(--border-subtle)'
            }"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = task.status === 'running' ? 'var(--color-primary-subtle)' : 'transparent')"
          >
            <!-- Status -->
            <td class="px-4 py-4">
              <span class="relative flex h-3 w-3">
                <span
                  v-if="task.status === 'running'"
                  class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                  :style="{ backgroundColor: 'var(--color-primary)' }"
                ></span>
                <span
                  class="relative inline-flex rounded-full h-3 w-3"
                  :style="{
                    backgroundColor:
                      task.status === 'running' || task.status === 'success' ? 'var(--color-primary)' :
                      task.status === 'failed' ? 'var(--color-danger)' :
                      task.status === 'timeout' ? 'var(--color-warning)' :
                      'var(--text-muted)'
                  }"
                ></span>
              </span>
            </td>

            <!-- Task Info -->
            <td class="px-4 py-4">
              <div class="font-medium" style="color: var(--text-main);">{{ task.name }}</div>
              <div class="text-xs mt-0.5 flex items-center gap-2" style="color: var(--text-muted);">
                <span class="font-mono">{{ task.script_path }}</span>
                <span
                  v-if="task.interpreter_path"
                  class="text-xs px-1.5 py-0.5 rounded"
                  :style="{ backgroundColor: 'rgba(168, 85, 247, 0.15)', color: 'var(--color-purple)' }"
                >
                  {{ task.interpreter_path.split('/').pop().split('\\').pop() }}
                </span>
                <span
                  v-if="task.webhook_enabled"
                  class="text-xs px-1.5 py-0.5 rounded flex items-center gap-1"
                  :style="{ backgroundColor: 'rgba(59, 130, 246, 0.15)', color: 'var(--color-blue)' }"
                  title="Webhook已启用"
                >
                  <WebhookIcon class="w-3 h-3" />
                  Webhook
                </span>
                <span
                  v-if="task.use_docker"
                  class="text-xs px-1.5 py-0.5 rounded flex items-center gap-1"
                  :style="{ backgroundColor: 'rgba(14, 165, 233, 0.15)', color: 'var(--color-cyan)' }"
                  title="Docker沙箱"
                >
                  <CubeIcon class="w-3 h-3" />
                  Docker
                </span>
              </div>
              <div v-if="task.description" class="text-xs mt-1 truncate max-w-md" style="color: var(--text-disabled);">
                {{ task.description }}
              </div>
            </td>

            <!-- Dependency -->
            <td class="px-4 py-4">
              <span
                v-if="task.depends_on"
                class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full"
                :style="{ backgroundColor: 'var(--color-warning-subtle)', color: 'var(--color-warning)' }"
              >
                <ArrowRightIcon class="w-3 h-3" />
                {{ getTaskName(task.depends_on) }}
              </span>
              <span v-else class="text-sm" style="color: var(--text-disabled);">-</span>
            </td>

            <!-- Cron -->
            <td class="px-4 py-4">
              <code
                class="text-xs px-2.5 py-1.5 rounded-lg font-mono"
                :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--color-primary)', border: '1px solid var(--border-subtle)' }"
              >{{ task.cron_expr || '-' }}</code>
            </td>

            <!-- Toggle -->
            <td class="px-4 py-4">
              <button
                @click="toggleTask(task)"
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-300"
                :style="task.is_active
                  ? { backgroundColor: 'var(--color-success-subtle)', border: '1px solid var(--color-success)' }
                  : { backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)' }"
              >
                <span
                  class="inline-block h-4 w-4 transform rounded-full transition-all duration-300"
                  :style="{
                    backgroundColor: task.is_active ? 'var(--color-success)' : 'var(--text-muted)',
                    transform: task.is_active ? 'translateX(22px)' : 'translateX(2px)'
                  }"
                />
              </button>
            </td>

            <!-- Actions -->
            <td class="px-4 py-4">
              <div class="flex items-center justify-end gap-1">
                <button
                  @click="runTask(task)"
                  :disabled="task.status === 'running'"
                  class="p-2 rounded-lg transition-colors"
                  :style="{ color: 'var(--text-muted)' }"
                  :class="{ 'opacity-40': task.status === 'running' }"
                  title="立即运行"
                  @mouseenter="($event.currentTarget.style.color = 'var(--color-success)', $event.currentTarget.style.backgroundColor = 'var(--color-success-subtle)')"
                  @mouseleave="($event.currentTarget.style.color = 'var(--text-muted)', $event.currentTarget.style.backgroundColor = 'transparent')"
                >
                  <PlayIcon class="w-4 h-4" />
                </button>
                <button
                  @click="openLogDrawer(task)"
                  class="p-2 rounded-lg transition-colors"
                  :style="{ color: 'var(--text-muted)' }"
                  title="查看日志"
                  @mouseenter="($event.currentTarget.style.color = 'var(--color-primary)', $event.currentTarget.style.backgroundColor = 'var(--color-primary-subtle)')"
                  @mouseleave="($event.currentTarget.style.color = 'var(--text-muted)', $event.currentTarget.style.backgroundColor = 'transparent')"
                >
                  <CommandLineIcon class="w-4 h-4" />
                </button>
                <button
                  @click="openEditDrawer(task)"
                  class="p-2 rounded-lg transition-colors"
                  :style="{ color: 'var(--text-muted)' }"
                  title="编辑"
                  @mouseenter="($event.currentTarget.style.color = 'var(--color-warning)', $event.currentTarget.style.backgroundColor = 'var(--color-warning-subtle)')"
                  @mouseleave="($event.currentTarget.style.color = 'var(--text-muted)', $event.currentTarget.style.backgroundColor = 'transparent')"
                >
                  <PencilIcon class="w-4 h-4" />
                </button>
                <button
                  @click="deleteTask(task)"
                  class="p-2 rounded-lg transition-colors"
                  :style="{ color: 'var(--text-muted)' }"
                  title="删除"
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

  <!-- Task Drawer -->
  <div v-if="showDrawer" class="fixed inset-0 z-50 overflow-hidden">
    <div class="absolute inset-0 backdrop-blur-sm" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }" @click="closeDrawer"></div>
    <div
      class="absolute right-0 top-0 h-full w-full max-w-xl theme-transition overflow-y-auto"
      :style="{ backgroundColor: 'var(--bg-secondary)', borderLeft: '1px solid var(--border-subtle)' }"
    >
      <div class="flex items-center justify-between p-5" :style="{ borderBottom: '1px solid var(--border-subtle)' }">
        <div class="flex items-center gap-3">
          <div class="h-1 w-6 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-primary), var(--color-success))' }"></div>
          <h2 class="text-lg font-semibold" style="color: var(--text-main);">{{ isEditing ? '编辑任务' : '新建任务' }}</h2>
        </div>
        <button
          @click="closeDrawer"
          class="p-2 rounded-lg transition-colors"
          :style="{ color: 'var(--text-muted)' }"
          @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
          @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
        >
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <div class="p-5 overflow-y-auto" :style="{ height: 'calc(100vh - 73px)' }">
        <form @submit.prevent="submitForm" class="space-y-6">
          <!-- AI: Text-to-Script Generation -->
          <div v-if="!isEditing" class="rounded-lg p-4" :style="{ backgroundColor: 'var(--color-primary-subtle)', border: '1px solid var(--color-primary)' }">
            <div class="flex items-center gap-2 mb-3">
              <SparklesIcon class="w-5 h-5" :style="{ color: 'var(--color-primary)' }" />
              <span class="font-medium" style="color: var(--color-primary);">AI 智能生成脚本</span>
            </div>
            <div class="flex gap-2">
              <input
                v-model="aiDescription"
                type="text"
                class="input flex-1"
                placeholder="用自然语言描述你想要实现的脚本功能..."
              />
              <button
                type="button"
                @click="generateScriptWithAI"
                :disabled="aiGenerating || !aiDescription.trim()"
                class="px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2"
                :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
                :class="{ 'opacity-50': aiGenerating }"
              >
                <SparklesIcon v-if="!aiGenerating" class="w-4 h-4" />
                <span v-if="aiGenerating" class="animate-spin">⟳</span>
                {{ aiGenerating ? '生成中...' : '生成' }}
              </button>
            </div>
          </div>

          <!-- Task Name -->
          <div>
            <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">任务名称</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="input"
              placeholder="输入任务名称"
            />
          </div>

          <!-- Script Mode -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium" style="color: var(--text-muted);">脚本来源</label>
              <!-- AI: Code Review Button -->
              <button
                v-if="scriptMode === 'editor' && form.script_content"
                type="button"
                @click="reviewCodeWithAI"
                :disabled="aiReviewing"
                class="flex items-center gap-1 text-xs px-2 py-1 rounded transition-all"
                :style="{ color: 'var(--color-purple)' }"
                title="AI代码审查"
              >
                <SparklesIcon class="w-3 h-3" :class="{ 'animate-spin': aiReviewing }" />
                AI审查
              </button>
            </div>
            <div class="flex gap-4 mb-3">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" v-model="scriptMode" value="path" class="accent-" :style="{ accentColor: 'var(--color-primary)' }" />
                <span class="text-sm" style="color: var(--text-main);">服务器路径</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" v-model="scriptMode" value="editor" class="" :style="{ accentColor: 'var(--color-primary)' }" />
                <span class="text-sm" style="color: var(--text-main);">在线编辑</span>
              </label>
            </div>

            <div v-if="scriptMode === 'path'">
              <input
                v-model="form.script_path"
                type="text"
                required
                class="input font-mono text-sm"
                placeholder="./scripts/my_script.py"
              />
            </div>
            <div v-else class="rounded-lg overflow-hidden" :style="{ border: '1px solid var(--border-subtle)' }">
              <div
                class="px-3 py-2 text-xs flex items-center justify-between"
                :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }"
              >
                <div class="flex items-center gap-2">
                  <span>Python Editor</span>
                  <span style="color: var(--color-primary);">Python 3</span>
                </div>
                <button
                  v-if="aiCapabilities.docker_available"
                  type="button"
                  @click="form.use_docker = !form.use_docker"
                  class="flex items-center gap-1 text-xs px-2 py-0.5 rounded transition-all"
                  :style="form.use_docker
                    ? { backgroundColor: 'rgba(14, 165, 233, 0.15)', color: 'var(--color-cyan)' }
                    : { color: 'var(--text-disabled)' }"
                  title="Docker沙箱执行"
                >
                  <CubeIcon class="w-3 h-3" />
                  {{ form.use_docker ? '沙箱模式' : '普通模式' }}
                </button>
              </div>
              <vue-monaco-editor
                v-model:value="form.script_content"
                language="python"
                theme="vs-dark"
                :options="{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 4,
                  wordWrap: 'on',
                  padding: { top: 8 }
                }"
                height="200px"
              />
            </div>
          </div>

          <!-- AI Review Result Panel -->
          <div v-if="aiReviewResult" class="rounded-lg p-4" :style="{ backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)' }">
            <div class="flex items-center gap-2 mb-2">
              <SparklesIcon class="w-4 h-4" style="color: var(--color-purple);" />
              <span class="font-medium text-sm" style="color: var(--text-main);">AI 代码审查结果</span>
              <button @click="aiReviewResult = null" class="ml-auto p-1 rounded hover:bg-bg-hover">
                <XMarkIcon class="w-3 h-3" style="color: var(--text-muted);" />
              </button>
            </div>
            <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-muted);">{{ aiReviewResult }}</pre>
          </div>

          <!-- Interpreter Path -->
          <div>
            <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">
              Python 解释器 <span class="text-xs" style="color: var(--text-disabled);">(可选)</span>
            </label>
            <div class="relative">
              <input
                v-model="form.interpreter_path"
                type="text"
                class="input font-mono text-sm pr-12"
                placeholder="/usr/bin/python3"
              />
              <span v-if="form.interpreter_path" class="absolute right-3 top-1/2 -translate-y-1/2 text-xs px-2 py-1 rounded" :style="{ backgroundColor: 'rgba(168, 85, 247, 0.15)', color: 'var(--color-purple)' }">venv</span>
            </div>
            <p class="text-xs mt-1" style="color: var(--text-disabled);">指定任务执行的 Python 解释器路径</p>
          </div>

          <!-- Cron Expression with NLP support -->
          <div>
            <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">定时执行</label>

            <!-- NLP to Cron Input -->
            <div class="mb-3 p-3 rounded-lg" :style="{ backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)' }">
              <div class="flex items-center gap-2 mb-2">
                <SparklesIcon class="w-4 h-4" :style="{ color: 'var(--color-primary)' }" />
                <span class="text-xs" style="color: var(--text-muted);">自然语言设置定时</span>
              </div>
              <div class="flex gap-2">
                <input
                  v-model="nlpCronInput"
                  type="text"
                  class="input flex-1 text-sm"
                  placeholder="例如：每个工作日下午5点半"
                  @keyup.enter="convertNLPCron"
                />
                <button
                  type="button"
                  @click="convertNLPCron"
                  :disabled="aiCronConverting || !nlpCronInput.trim()"
                  class="px-3 py-1.5 text-xs rounded-lg font-medium transition-all flex items-center gap-1"
                  :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
                  :class="{ 'opacity-50': aiCronConverting }"
                >
                  <SparklesIcon v-if="!aiCronConverting" class="w-3 h-3" />
                  <span v-if="aiCronConverting" class="animate-spin">⟳</span>
                  {{ aiCronConverting ? '转换中' : '转Cron' }}
                </button>
              </div>
              <div v-if="nlpCronResult" class="mt-2 text-xs" style="color: var(--color-success);">
                ✓ {{ nlpCronResult }}
              </div>
            </div>

            <!-- Cron Presets -->
            <div class="grid grid-cols-4 gap-2 mb-3">
              <button
                type="button"
                v-for="preset in cronPresets"
                :key="preset.value"
                @click="form.cron_expr = preset.value"
                class="px-3 py-2 text-xs rounded-lg border transition-all duration-200"
                :style="form.cron_expr === preset.value
                  ? { borderColor: 'var(--color-primary)', backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }
                  : { borderColor: 'var(--border-subtle)', color: 'var(--text-muted)' }"
              >
                {{ preset.label }}
              </button>
            </div>
            <input
              v-model="form.cron_expr"
              type="text"
              class="input font-mono"
              placeholder="* * * * *"
            />
            <p class="text-xs mt-2" v-if="form.cron_expr" style="color: var(--text-muted);">{{ cronHumanText(form.cron_expr) }}</p>
          </div>

          <!-- Task Dependency -->
          <div>
            <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">
              前置任务依赖 <span class="text-xs" style="color: var(--text-disabled);">(可选)</span>
            </label>
            <select v-model="form.depends_on" class="input">
              <option :value="null">无依赖</option>
              <option v-for="t in availableDependencies" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
            <p class="text-xs mt-1" style="color: var(--text-disabled);">前置任务成功执行后，自动触发此任务</p>
          </div>

          <!-- Webhook Trigger Setting -->
          <div>
            <div class="flex items-center gap-3 mb-2">
              <label class="text-sm font-medium" style="color: var(--text-muted);">Webhook 触发</label>
              <span class="text-xs px-2 py-0.5 rounded" :style="{ backgroundColor: 'rgba(59, 130, 246, 0.15)', color: 'var(--color-blue)' }">事件驱动</span>
            </div>
            <div class="flex items-center gap-3">
              <button
                type="button"
                @click="form.webhook_enabled = !form.webhook_enabled"
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-300"
                :style="form.webhook_enabled
                  ? { backgroundColor: 'rgba(59, 130, 246, 0.2)', border: '1px solid var(--color-blue)' }
                  : { backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)' }"
              >
                <span
                  class="inline-block h-4 w-4 transform rounded-full transition-all duration-300"
                  :style="{
                    backgroundColor: form.webhook_enabled ? 'var(--color-blue)' : 'var(--text-muted)',
                    transform: form.webhook_enabled ? 'translateX(22px)' : 'translateX(2px)'
                  }"
                />
              </button>
              <span class="text-sm" style="color: var(--text-muted);">
                {{ form.webhook_enabled ? '启用 Webhook URL 触发' : '禁用' }}
              </span>
            </div>
            <div v-if="form.webhook_enabled && isEditing" class="mt-2 text-xs">
              <div class="flex items-center gap-2">
                <code class="px-2 py-1 rounded" :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--color-blue)' }">
                  /webhook/{{ currentWebhookToken }}
                </code>
                <button @click="copyWebhookUrl" class="p-1 rounded hover:bg-bg-hover" title="复制">
                  <ClipboardDocumentIcon class="w-3 h-3" style="color: var(--text-muted);" />
                </button>
              </div>
            </div>
          </div>

          <!-- Timeout -->
          <div>
            <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">超时时间 (秒)</label>
            <input v-model.number="form.timeout" type="number" min="0" class="input" placeholder="300" />
          </div>

          <!-- Auto Doc Generation -->
          <div v-if="!isEditing && form.script_content" class="rounded-lg p-4" :style="{ backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-subtle)' }">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <SparklesIcon class="w-4 h-4" :style="{ color: 'var(--color-success)' }" />
                <span class="text-sm font-medium" style="color: var(--text-main);">AI 自动生成文档</span>
              </div>
              <button
                type="button"
                @click="generateDocWithAI"
                :disabled="aiDocGenerating"
                class="flex items-center gap-1 text-xs px-2 py-1 rounded transition-all"
                :style="{ color: 'var(--color-success)' }"
              >
                <SparklesIcon class="w-3 h-3" :class="{ 'animate-spin': aiDocGenerating }" />
                {{ aiDocGenerating ? '生成中...' : '重新生成' }}
              </button>
            </div>
            <p v-if="aiGeneratedDoc" class="text-xs whitespace-pre-wrap" style="color: var(--text-muted);">{{ aiGeneratedDoc }}</p>
            <p v-else class="text-xs" style="color: var(--text-disabled);">保存时将自动生成文档描述</p>
          </div>

          <!-- Submit -->
          <div class="flex gap-3 pt-4" :style="{ borderTop: '1px solid var(--border-subtle)' }">
            <button
              type="button"
              @click="closeDrawer"
              class="flex-1 px-4 py-2.5 rounded-lg transition-all"
              :style="{ border: '1px solid var(--border-subtle)', color: 'var(--text-main)', backgroundColor: 'transparent' }"
              @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
              @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
            >
              取消
            </button>
            <button
              type="submit"
              class="flex-1 px-4 py-2.5 rounded-lg font-medium transition-all"
              :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
              @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--color-primary-hover)')"
              @mouseleave="($event.currentTarget.style.backgroundColor = 'var(--color-primary)')"
            >
              {{ isEditing ? '保存' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Log Drawer -->
  <div v-if="showLogDrawer" class="fixed inset-0 z-50 overflow-hidden">
    <div class="absolute inset-0 backdrop-blur-sm" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }" @click="closeLogDrawer"></div>
    <div
      class="absolute right-0 top-0 h-full w-full max-w-3xl theme-transition"
      :style="{ backgroundColor: 'var(--bg-primary)', borderLeft: '1px solid var(--border-subtle)' }"
    >
      <!-- Terminal Header -->
      <div class="flex items-center justify-between px-5 py-3" :style="{ backgroundColor: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)' }">
        <div class="flex items-center gap-3">
          <div class="flex gap-1.5">
            <div class="w-3 h-3 rounded-full" style="background-color: #E43F3F;"></div>
            <div class="w-3 h-3 rounded-full" style="background-color: #E5C07B;"></div>
            <div class="w-3 h-3 rounded-full" style="background-color: #98C379;"></div>
          </div>
          <div>
            <span class="text-sm font-medium" style="color: var(--text-main);">{{ currentTask?.name }}</span>
            <span class="text-xs ml-2" style="color: var(--text-muted);">bash</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <!-- Search Filter -->
          <div class="flex items-center gap-2 mr-2">
            <div class="relative">
              <input
                v-model="logSearch"
                type="text"
                placeholder="搜索..."
                class="text-xs px-3 py-1.5 pr-8 rounded-lg font-mono"
                :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-main)', border: '1px solid var(--border-subtle)' }"
              />
              <MagnifyingGlassIcon class="w-3 h-3 absolute right-2 top-1/2 -translate-y-1/2" style="color: var(--text-muted);" />
            </div>
            <input
              v-model="logDateFilter"
              type="date"
              class="text-xs px-2 py-1.5 rounded-lg"
              :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-main)', border: '1px solid var(--border-subtle)' }"
            />
          </div>
          <!-- AI: Log Summarization Button -->
          <button
            v-if="currentLog && currentLog.output && currentLog.output.length > 500"
            @click="summarizeLogWithAI"
            :disabled="aiLogSummarizing"
            class="p-1.5 rounded-lg transition-colors flex items-center gap-1"
            :style="{ color: 'var(--color-purple)' }"
            title="AI日志摘要"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'rgba(168, 85, 247, 0.15)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
          >
            <SparklesIcon class="w-4 h-4" :class="{ 'animate-spin': aiLogSummarizing }" />
            <span class="text-xs">摘要</span>
          </button>
          <button
            @click="downloadLog"
            class="p-1.5 rounded-lg transition-colors"
            :style="{ color: 'var(--text-muted)' }"
            title="下载日志"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
          >
            <ArrowDownTrayIcon class="w-4 h-4" />
          </button>
          <button
            @click="runTask(currentTask)"
            class="px-3 py-1.5 text-xs rounded-lg font-medium transition-colors"
            :style="{ backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--color-primary)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'var(--color-primary-subtle)')"
          >
            ▶ 运行
          </button>
          <button
            @click="refreshLogs"
            class="p-1.5 rounded-lg transition-colors"
            :style="{ color: 'var(--text-muted)' }"
            title="刷新"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
          >
            <ArrowPathIcon class="w-4 h-4" />
          </button>
          <button
            @click="closeLogDrawer"
            class="p-1.5 rounded-lg transition-colors"
            :style="{ color: 'var(--text-muted)' }"
            @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
            @mouseleave="($event.currentTarget.style.backgroundColor = 'transparent')"
          >
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- AI Log Summary Panel -->
      <div v-if="aiLogSummary" class="px-5 py-3" :style="{ backgroundColor: 'var(--color-primary-subtle)', borderBottom: '1px solid var(--border-subtle)' }">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <SparklesIcon class="w-4 h-4" :style="{ color: 'var(--color-primary)' }" />
            <span class="text-sm font-medium" style="color: var(--color-primary);">AI 日志摘要</span>
          </div>
          <button @click="aiLogSummary = null" class="p-1 rounded hover:bg-bg-hover">
            <XMarkIcon class="w-3 h-3" style="color: var(--text-muted);" />
          </button>
        </div>
        <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ aiLogSummary }}</pre>
      </div>

      <!-- AI Error Diagnosis Panel -->
      <div v-if="aiErrorDiagnosis" class="px-5 py-3" :style="{ backgroundColor: 'var(--color-danger-subtle)', borderBottom: '1px solid var(--border-subtle)' }">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <SparklesIcon class="w-4 h-4" style="color: var(--color-danger);" />
            <span class="text-sm font-medium" style="color: var(--color-danger);">AI 错误诊断</span>
          </div>
          <button @click="aiErrorDiagnosis = null" class="p-1 rounded hover:bg-bg-hover">
            <XMarkIcon class="w-3 h-3" style="color: var(--text-muted);" />
          </button>
        </div>
        <pre class="text-xs whitespace-pre-wrap" style="color: var(--text-main);">{{ aiErrorDiagnosis }}</pre>
      </div>

      <!-- Terminal Content -->
      <div ref="terminalContent" class="overflow-auto p-5" :style="{ height: 'calc(100%-48px)', backgroundColor: 'var(--bg-primary)' }">
        <div class="space-y-1 font-mono text-sm">
          <div style="color: var(--text-muted);">
            <span style="color: var(--color-primary);">pycron</span>:<span style="color: var(--color-success);">~</span>$ python {{ currentTask?.script_path }}
          </div>

          <div v-if="filteredLogs.length === 0" class="py-6" style="color: var(--text-muted);">
            <p class="text-sm">// 暂无执行记录</p>
            <p class="text-sm mt-2" style="color: var(--color-success); opacity: 0.7;">// 点击 "运行" 按钮执行任务</p>
          </div>

          <div v-else>
            <div v-for="(log, idx) in filteredLogs" :key="log.id" class="pb-4 mb-4" :style="{ borderBottom: '1px solid var(--border-subtle)' }">
              <div class="flex items-center justify-between text-xs mb-2" style="color: var(--text-muted);">
                <div class="flex items-center gap-3">
                  <span style="color: var(--color-primary);">[{{ idx + 1 }}]</span>
                  <span style="color: var(--text-main);">{{ formatTime(log.start_time) }}</span>
                  <span v-if="log.end_time" style="color: var(--text-disabled);">→ {{ formatTime(log.end_time) }}</span>
                  <span
                    class="px-2 py-0.5 rounded text-xs font-medium"
                    :style="log.exit_code === 0
                      ? { backgroundColor: 'var(--color-success-subtle)', color: 'var(--color-success)' }
                      : { backgroundColor: 'var(--color-danger-subtle)', color: 'var(--color-danger)' }"
                  >
                    exit {{ log.exit_code }}
                  </span>
                </div>
                <!-- AI Diagnose Button for failed logs -->
                <button
                  v-if="log.exit_code !== 0"
                  @click="diagnoseErrorWithAI(log)"
                  :disabled="aiDiagnosingLogId === log.id"
                  class="flex items-center gap-1 px-2 py-0.5 rounded text-xs transition-all"
                  :style="{ color: 'var(--color-warning)' }"
                  title="AI错误诊断"
                >
                  <SparklesIcon class="w-3 h-3" :class="{ 'animate-spin': aiDiagnosingLogId === log.id }" />
                  诊断
                </button>
              </div>
              <pre class="whitespace-pre-wrap leading-relaxed text-sm" style="color: var(--text-main);" v-html="highlightKeyword(log.output || '// 无输出')"></pre>
            </div>
          </div>

          <div class="mt-4" style="color: var(--color-success);">
            <span class="inline-block w-2 h-4 animate-pulse" :style="{ backgroundColor: 'var(--color-success)' }"></span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Node Flow Editor Modal -->
  <div v-if="showNodeFlowEditor" class="fixed inset-0 z-50 overflow-hidden">
    <div class="absolute inset-0 backdrop-blur-sm" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }" @click="showNodeFlowEditor = false"></div>
    <div
      class="absolute inset-4 md:inset-8 lg:inset-16 bg-gray-900 border border-gray-700/50 rounded-2xl flex flex-col shadow-2xl"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700/50">
        <div class="flex items-center gap-3">
          <ViewColumnsIcon class="w-6 h-6" style="color: var(--color-purple);" />
          <span class="text-lg font-semibold text-gray-100">可视化节点编排</span>
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="saveNodeFlow"
            class="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white font-medium rounded-lg transition-all"
          >
            保存
          </button>
          <button @click="showNodeFlowEditor = false" class="p-2 hover:bg-gray-800 rounded-lg transition-colors">
            <XMarkIcon class="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </div>

      <!-- Canvas -->
      <div class="flex-1 relative overflow-hidden bg-gray-800/50">
        <div id="node-flow-canvas" ref="nodeFlowCanvas" class="w-full h-full" @mousedown="onCanvasMouseDown">
          <!-- Nodes will be rendered here -->
          <div
            v-for="node in flowNodes"
            :key="node.id"
            class="absolute bg-gray-800 border border-gray-600 rounded-lg p-4 cursor-move min-w-48 shadow-lg"
            :style="{ left: node.x + 'px', top: node.y + 'px' }"
            @mousedown.stop="onNodeMouseDown($event, node)"
          >
            <div class="flex items-center gap-2 mb-2">
              <span class="w-3 h-3 rounded-full" :style="{ backgroundColor: getNodeColor(node.type) }"></span>
              <span class="text-sm font-medium text-gray-100">{{ node.label }}</span>
            </div>
            <div class="text-xs text-gray-400">{{ node.description }}</div>
          </div>

          <!-- SVG for edges -->
          <svg class="absolute inset-0 pointer-events-none" style="width: 100%; height: 100%;">
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#6366F1" />
              </marker>
            </defs>
            <path
              v-for="edge in flowEdges"
              :key="edge.id"
              :d="getEdgePath(edge)"
              fill="none"
              stroke="#6366F1"
              stroke-width="2"
              marker-end="url(#arrowhead)"
            />
          </svg>
        </div>

        <!-- Toolbar -->
        <div class="absolute top-4 left-4 flex flex-col gap-2">
          <button
            @click="addFlowNode"
            class="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            title="添加节点"
          >
            <PlusIcon class="w-5 h-5 text-gray-300" />
          </button>
        </div>

        <!-- Node Palette -->
        <div class="absolute top-4 right-4 bg-gray-800 border border-gray-700 rounded-lg p-3 w-64">
          <div class="text-xs text-gray-400 mb-2">可用任务</div>
          <div class="space-y-2">
            <div
              v-for="task in tasks"
              :key="task.id"
              class="flex items-center gap-2 p-2 bg-gray-700 rounded cursor-pointer hover:bg-gray-600"
              @click="addTaskToFlow(task)"
            >
              <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: getStatusColor(task.status) }"></span>
              <span class="text-sm text-gray-200 truncate">{{ task.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import cronParser from 'cron-parser'
import {
  PlusIcon, PlayIcon, PencilIcon, TrashIcon, CommandLineIcon,
  XMarkIcon, ArrowPathIcon, InboxIcon, ArrowDownTrayIcon,
  ArrowRightIcon, MagnifyingGlassIcon, SparklesIcon,
  ClipboardDocumentIcon, CubeIcon, ViewColumnsIcon
} from '@heroicons/vue/24/outline'

const api = axios.create({ baseURL: 'http://localhost:8000' })

const tasks = ref([])
const showDrawer = ref(false)
const showLogDrawer = ref(false)
const showNodeFlowEditor = ref(false)
const isEditing = ref(false)
const scriptMode = ref('path')
const currentTask = ref(null)
const logs = ref([])
const logSearch = ref('')
const logDateFilter = ref('')
const currentLog = ref(null)
const aiLogSummary = ref(null)
const aiErrorDiagnosis = ref(null)
const aiDiagnosingLogId = ref(null)

// AI state
const aiDescription = ref('')
const aiGenerating = ref(false)
const aiReviewResult = ref(null)
const aiReviewing = ref(false)
const aiGeneratedDoc = ref('')
const aiDocGenerating = ref(false)
const nlpCronInput = ref('')
const nlpCronResult = ref('')
const aiCronConverting = ref(false)
const aiLogSummarizing = ref(false)
const aiCapabilities = ref({ docker_available: false })
const currentWebhookToken = ref('')

// Node Flow state
const flowNodes = ref([])
const flowEdges = ref([])
const flowId = ref(null)
const draggedNode = ref(null)
const dragOffset = ref({ x: 0, y: 0 })

const form = reactive({
  id: null, name: '', script_path: './scripts/', script_content: '',
  cron_expr: '* * * * *', timeout: 300, is_active: true,
  interpreter_path: null, depends_on: null,
  webhook_enabled: false, description: '', use_docker: false, docker_image: null
})

const runningCount = computed(() => tasks.value.filter(t => t.status === 'running').length)
const availableDependencies = computed(() => tasks.value.filter(t => t.id !== form.id))

const filteredLogs = computed(() => {
  let result = logs.value
  if (logSearch.value) {
    const kw = logSearch.value.toLowerCase()
    result = result.filter(l => (l.output || '').toLowerCase().includes(kw))
  }
  if (logDateFilter.value) {
    const date = new Date(logDateFilter.value).toDateString()
    result = result.filter(l => new Date(l.start_time).toDateString() === date)
  }
  return result
})

const cronPresets = [
  { label: '每分钟', value: '* * * * *' },
  { label: '每小时', value: '0 * * * *' },
  { label: '每天凌晨', value: '0 2 * * *' },
  { label: '每周一', value: '0 9 * * 1' }
]

async function fetchTasks() {
  try {
    const res = await api.get('/tasks')
    tasks.value = res.data
  } catch (e) { console.error(e) }
}

async function fetchAiCapabilities() {
  try {
    const res = await api.get('/ai/capabilities')
    aiCapabilities.value = res.data
  } catch (e) { console.error(e) }
}

function getTaskName(taskId) {
  const t = tasks.value.find(t => t.id === taskId)
  return t ? t.name : 'Unknown'
}

function getNextRun(cronExpr) {
  try {
    const interval = cronParser.parseExpression(cronExpr)
    const next = interval.next().toDate()
    return new Date(next).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch { return '-' }
}

function cronHumanText(expr) {
  try {
    const parts = expr.split(' ')
    if (parts.length !== 5) return ''
    const [min, hour, day, month, week] = parts
    if (expr === '* * * * *') return '每分钟执行一次'
    if (expr === '0 * * * *') return '每小时整点执行'
    if (day === '*' && month === '*' && week === '*') return `每天 ${hour}:${min.padStart(2, '0')} 执行`
    if (week !== '*' && day === '*') {
      const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      return `每周${weekDays[parseInt(week)]} ${hour}:${min.padStart(2, '0')} 执行`
    }
    return `将在 ${expr} 执行`
  } catch { return '' }
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

function highlightKeyword(text) {
  if (!logSearch.value) return text
  const kw = logSearch.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${kw})`, 'gi'), '<mark style="background-color: var(--color-warning-subtle); color: var(--color-warning); padding: 0 2px; border-radius: 2px;">$1</mark>')
}

// ========== AI Functions ==========

async function generateScriptWithAI() {
  if (!aiDescription.value.trim() || aiGenerating.value) return
  aiGenerating.value = true
  try {
    const res = await api.post('/ai/generate-script', { description: aiDescription.value })
    form.script_content = res.data.code
    scriptMode.value = 'editor'
    // Auto-generate doc
    await generateDocWithAI()
  } catch (e) {
    alert('AI生成失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiGenerating.value = false
  }
}

async function reviewCodeWithAI() {
  if (!form.script_content || aiReviewing.value) return
  aiReviewing.value = true
  try {
    const res = await api.post('/ai/code-review', { code: form.script_content })
    aiReviewResult.value = res.data.review
  } catch (e) {
    alert('AI审查失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiReviewing.value = false
  }
}

async function generateDocWithAI() {
  if (!form.script_content || aiDocGenerating.value) return
  aiDocGenerating.value = true
  try {
    const res = await api.post('/ai/generate-doc', { code: form.script_content })
    aiGeneratedDoc.value = res.data.doc
    form.description = res.data.doc
  } catch (e) {
    console.error('AI文档生成失败:', e)
  } finally {
    aiDocGenerating.value = false
  }
}

async function convertNLPCron() {
  if (!nlpCronInput.value.trim() || aiCronConverting.value) return
  aiCronConverting.value = true
  try {
    const res = await api.post('/ai/nlp-to-cron', { natural_language: nlpCronInput.value })
    form.cron_expr = res.data.cron_expr
    nlpCronResult.value = res.data.description
    setTimeout(() => { nlpCronResult.value = '' }, 3000)
  } catch (e) {
    alert('Cron转换失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiCronConverting.value = false
  }
}

async function summarizeLogWithAI() {
  if (!currentLog.value?.output || aiLogSummarizing.value) return
  aiLogSummarizing.value = true
  try {
    const res = await api.post('/ai/summarize-log', { log_content: currentLog.value.output })
    aiLogSummary.value = res.data.summary
  } catch (e) {
    alert('日志摘要失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiLogSummarizing.value = false
  }
}

async function diagnoseErrorWithAI(log) {
  if (aiDiagnosingLogId.value) return
  aiDiagnosingLogId.value = log.id
  aiErrorDiagnosis.value = null
  try {
    const res = await api.post('/ai/diagnose-error', {
      error_traceback: log.output,
      script_content: ''
    })
    aiErrorDiagnosis.value = res.data.diagnosis
  } catch (e) {
    alert('AI诊断失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiDiagnosingLogId.value = null
  }
}

function copyWebhookUrl() {
  navigator.clipboard.writeText(`${window.location.origin}/webhook/${currentWebhookToken.value}`)
}

// ========== Node Flow Functions ==========

function getStatusColor(status) {
  const colors = {
    running: 'var(--color-primary)',
    success: 'var(--color-success)',
    failed: 'var(--color-danger)',
    timeout: 'var(--color-warning)',
    idle: 'var(--text-muted)'
  }
  return colors[status] || 'var(--text-muted)'
}

function getNodeColor(type) {
  const colors = {
    task: '#6366F1',
    start: '#10B981',
    end: '#EF4444'
  }
  return colors[type] || '#6366F1'
}

function getEdgePath(edge) {
  const source = flowNodes.value.find(n => n.id === edge.source)
  const target = flowNodes.value.find(n => n.id === edge.target)
  if (!source || !target) return ''

  const sx = source.x + 100
  const sy = source.y + 40
  const tx = target.x
  const ty = target.y + 40

  return `M ${sx} ${sy} C ${sx + 50} ${sy}, ${tx - 50} ${ty}, ${tx} ${ty}`
}

function addFlowNode() {
  const newId = Date.now()
  flowNodes.value.push({
    id: newId,
    task_id: null,
    label: '新节点',
    description: '双击编辑',
    type: 'task',
    x: 100 + Math.random() * 200,
    y: 100 + Math.random() * 200
  })
}

function addTaskToFlow(task) {
  const newId = Date.now()
  flowNodes.value.push({
    id: newId,
    task_id: task.id,
    label: task.name,
    description: task.script_path,
    type: 'task',
    x: 100 + Math.random() * 200,
    y: 100 + Math.random() * 200
  })
}

function onCanvasMouseDown(e) {
  // Deselect nodes when clicking canvas
}

function onNodeMouseDown(e, node) {
  draggedNode.value = node
  dragOffset.value = {
    x: e.clientX - node.x,
    y: e.clientY - node.y
  }

  document.addEventListener('mousemove', onNodeMouseMove)
  document.addEventListener('mouseup', onNodeMouseUp)
}

function onNodeMouseMove(e) {
  if (!draggedNode.value) return
  draggedNode.value.x = Math.max(0, e.clientX - dragOffset.value.x)
  draggedNode.value.y = Math.max(0, e.clientY - dragOffset.value.y)
}

function onNodeMouseUp() {
  draggedNode.value = null
  document.removeEventListener('mousemove', onNodeMouseMove)
  document.removeEventListener('mouseup', onNodeMouseUp)
}

async function saveNodeFlow() {
  try {
    const payload = {
      name: 'Node Flow ' + new Date().toLocaleTimeString(),
      nodes: JSON.stringify(flowNodes.value),
      edges: JSON.stringify(flowEdges.value),
      is_active: true
    }
    if (flowId.value) {
      await api.put(`/node-flows/${flowId.value}`, payload)
    } else {
      const res = await api.post('/node-flows', payload)
      flowId.value = res.data.id
    }
    alert('保存成功')
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

// ========== Main Functions ==========

function openCreateDrawer() {
  isEditing.value = false
  resetForm()
  showDrawer.value = true
}

function openEditDrawer(task) {
  isEditing.value = true
  currentTask.value = task
  form.id = task.id
  form.name = task.name
  form.script_path = task.script_path
  form.cron_expr = task.cron_expr || '* * * * *'
  form.timeout = task.timeout || 300
  form.is_active = task.is_active
  form.interpreter_path = task.interpreter_path
  form.depends_on = task.depends_on
  form.webhook_enabled = task.webhook_enabled || false
  form.description = task.description || ''
  form.use_docker = task.use_docker || false
  form.docker_image = task.docker_image
  scriptMode.value = 'path'
  aiGeneratedDoc.value = task.description || ''
  // Fetch webhook token if enabled
  if (task.webhook_enabled) {
    fetchWebhookInfo(task.id)
  }
  showDrawer.value = true
}

async function fetchWebhookInfo(taskId) {
  try {
    const res = await api.get(`/tasks/${taskId}/webhook-info`)
    currentWebhookToken.value = res.data.webhook_token || ''
  } catch (e) {
    console.error(e)
  }
}

function closeDrawer() { showDrawer.value = false; aiReviewResult.value = null; aiGeneratedDoc.value = '' }

function resetForm() {
  form.id = null
  form.name = ''
  form.script_path = './scripts/'
  form.script_content = ''
  form.cron_expr = '* * * * *'
  form.timeout = 300
  form.is_active = true
  form.interpreter_path = null
  form.depends_on = null
  form.webhook_enabled = false
  form.description = ''
  form.use_docker = false
  form.docker_image = null
  aiDescription.value = ''
  aiReviewResult.value = null
  aiGeneratedDoc.value = ''
  nlpCronInput.value = ''
  nlpCronResult.value = ''
  currentWebhookToken.value = ''
}

async function submitForm() {
  try {
    const payload = {
      name: form.name,
      script_path: form.script_path || form.script_content ? './scripts/task_' + Date.now() + '.py' : form.script_path,
      cron_expr: form.cron_expr || null,
      is_active: form.is_active,
      interpreter_path: form.interpreter_path || null,
      depends_on: form.depends_on,
      timeout: form.timeout || 300,
      webhook_enabled: form.webhook_enabled,
      description: aiGeneratedDoc.value || form.description,
      use_docker: form.use_docker,
      docker_image: form.docker_image
    }

    // If using editor mode, save the script first
    if (scriptMode.value === 'editor' && form.script_content) {
      const filename = 'task_' + Date.now() + '.py'
      await api.post('/scripts/upload-text', null, {
        params: { filename, content: form.script_content }
      })
      payload.script_path = './scripts/' + filename
    }

    if (isEditing.value) {
      await api.put(`/tasks/${form.id}`, payload)
      if (payload.webhook_enabled) {
        await api.post(`/tasks/${form.id}/enable-webhook`)
      }
    } else {
      const res = await api.post('/tasks', payload)
      // Enable webhook if requested
      if (payload.webhook_enabled) {
        await api.post(`/tasks/${res.data.id}/enable-webhook`)
      }
    }
    closeDrawer()
    fetchTasks()
  } catch (e) { alert('操作失败: ' + (e.response?.data?.detail || e.message)) }
}

async function toggleTask(task) {
  try { await api.put(`/tasks/${task.id}`, { is_active: !task.is_active }); fetchTasks() }
  catch (e) { console.error(e) }
}

async function runTask(task) {
  if (!task) task = currentTask.value
  try {
    await api.post(`/tasks/${task.id}/run`)
    setTimeout(() => { fetchTasks(); refreshLogs() }, 1000)
  } catch (e) { alert('启动失败: ' + (e.response?.data?.detail || e.message)) }
}

async function deleteTask(task) {
  if (!confirm(`确定删除任务 "${task.name}" 吗？`)) return
  try { await api.delete(`/tasks/${task.id}`); fetchTasks() }
  catch (e) { console.error(e) }
}

function openLogDrawer(task) {
  currentTask.value = task
  logs.value = []
  logSearch.value = ''
  logDateFilter.value = ''
  aiLogSummary.value = null
  aiErrorDiagnosis.value = null
  currentLog.value = null
  showLogDrawer.value = true
  refreshLogs()
}

function closeLogDrawer() { showLogDrawer.value = false; aiLogSummary.value = null; aiErrorDiagnosis.value = null }

async function refreshLogs() {
  if (!currentTask.value) return
  try {
    const res = await api.get(`/tasks/${currentTask.value.id}/logs`)
    logs.value = res.data
    if (logs.value.length > 0) {
      currentLog.value = logs.value[0]
    }
  } catch (e) { console.error(e) }
}

async function downloadLog() {
  if (!logs.value.length) return
  const content = logs.value.map((l, i) =>
    `=== Session ${i + 1} ===\nTime: ${formatTime(l.start_time)}\nExit: ${l.exit_code}\n\n${l.output || '// No output'}\n`
  ).join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `task_${currentTask.value.id}_logs_${new Date().toISOString().slice(0,10)}.log`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  fetchTasks()
  fetchAiCapabilities()
  setInterval(fetchTasks, 5000)
})
</script>
