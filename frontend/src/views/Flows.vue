<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--text-main);">编排中心</h1>
        <p class="text-sm mt-1" style="color: var(--text-muted);">可视化 DAG 节点编排与流程管理</p>
      </div>
      <button
        @click="createNewFlow"
        class="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all"
        :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
      >
        <PlusIcon class="w-5 h-5" />
        新建流程
      </button>
    </div>

    <!-- Flows List -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="flow in flows"
        :key="flow.id"
        class="card rounded-xl p-5 cursor-pointer theme-transition"
        @click="openFlow(flow)"
        @mouseenter="($event.currentTarget.style.backgroundColor = 'var(--bg-hover)')"
        @mouseleave="($event.currentTarget.style.backgroundColor = 'var(--bg-secondary)')"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :style="{ backgroundColor: 'var(--color-purple-subtle)' }"
            >
              <ViewColumnsIcon class="w-5 h-5" style="color: var(--color-purple);" />
            </div>
            <div>
              <h3 class="font-medium" style="color: var(--text-main);">{{ flow.name }}</h3>
              <p class="text-xs" style="color: var(--text-muted);">{{ flow.description || '无描述' }}</p>
            </div>
          </div>
          <span
            class="px-2 py-0.5 rounded text-xs font-medium"
            :style="flow.is_active
              ? { backgroundColor: 'var(--color-success-subtle)', color: 'var(--color-success)' }
              : { backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }"
          >
            {{ flow.is_active ? '启用' : '禁用' }}
          </span>
        </div>
        <div class="flex items-center justify-between">
          <div class="flex gap-1">
            <button
              @click.stop="executeFlow(flow)"
              class="p-2 rounded-lg transition-colors"
              :style="{ color: 'var(--color-success)' }"
              title="执行流程"
            >
              <PlayIcon class="w-4 h-4" />
            </button>
            <button
              @click.stop="editFlowName(flow)"
              class="p-2 rounded-lg transition-colors"
              :style="{ color: 'var(--text-muted)' }"
              title="编辑名称"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button
              @click.stop="deleteFlow(flow)"
              class="p-2 rounded-lg transition-colors"
              :style="{ color: 'var(--color-danger)' }"
              title="删除"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
          <span class="text-xs" style="color: var(--text-disabled);">
            {{ formatDate(flow.updated_at) }}
          </span>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="flows.length === 0"
        class="col-span-full card rounded-xl p-12 text-center"
      >
        <div
          class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
          :style="{ backgroundColor: 'var(--bg-tertiary)' }"
        >
          <ViewColumnsIcon class="w-8 h-8" style="color: var(--text-muted); opacity: 0.5;" />
        </div>
        <p class="text-lg" style="color: var(--text-muted);">暂无编排流程</p>
        <p class="text-sm mt-1" style="color: var(--text-disabled);">创建第一个节点编排流程</p>
        <button
          @click="createNewFlow"
          class="mt-4 px-4 py-2 rounded-lg font-medium"
          :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
        >
          新建流程
        </button>
      </div>
    </div>

    <!-- Flow Editor Modal -->
    <div v-if="showEditor" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 backdrop-blur-sm" :style="{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }" @click="closeEditor"></div>
      <div
        class="absolute inset-4 md:inset-8 rounded-2xl flex flex-col shadow-2xl overflow-hidden"
        :style="{ backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-subtle)' }"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4" :style="{ backgroundColor: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)' }">
          <div class="flex items-center gap-3">
            <div class="h-1 w-6 rounded-full" :style="{ background: 'linear-gradient(90deg, var(--color-purple), var(--color-primary))' }"></div>
            <input
              v-model="editingFlow.name"
              type="text"
              class="text-lg font-semibold bg-transparent border-none outline-none"
              style="color: var(--text-main);"
              placeholder="流程名称..."
            />
          </div>
          <div class="flex items-center gap-3">
            <button
              @click="saveFlow"
              class="px-4 py-2 rounded-lg font-medium transition-all"
              :style="{ backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }"
            >
              保存
            </button>
            <button
              @click="executeCurrentFlow"
              :disabled="executing"
              class="px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2"
              :style="{ backgroundColor: 'var(--color-success)', color: 'var(--text-inverse)' }"
            >
              <PlayIcon class="w-4 h-4" />
              {{ executing ? '执行中...' : '执行' }}
            </button>
            <button
              @click="closeEditor"
              class="p-2 rounded-lg transition-colors"
              :style="{ color: 'var(--text-muted)' }"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Canvas -->
        <div class="flex-1 relative overflow-hidden flex">
          <!-- Canvas Area -->
          <div
            class="flex-1 relative overflow-auto"
            :style="{ backgroundColor: 'var(--bg-tertiary)' }"
            @mousedown="onCanvasMouseDown"
          >
            <!-- Grid Background -->
            <div class="absolute inset-0 opacity-20" style="background-image: radial-gradient(circle, var(--border-subtle) 1px, transparent 1px); background-size: 20px 20px;"></div>

            <!-- Nodes -->
            <div
              v-for="node in editingFlow.nodes"
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
              <div v-if="node.task_id" class="mt-2 text-xs px-2 py-1 rounded" :style="{ backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }">
                任务 #{{ node.task_id }}
              </div>
            </div>

            <!-- SVG for edges -->
            <svg class="absolute inset-0 pointer-events-none" style="width: 100%; height: 100%;">
              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="var(--color-purple)" />
                </marker>
              </defs>
              <path
                v-for="edge in editingFlow.edges"
                :key="edge.id"
                :d="getEdgePath(edge)"
                fill="none"
                stroke="var(--color-purple)"
                stroke-width="2"
                marker-end="url(#arrowhead)"
              />
            </svg>
          </div>

          <!-- Toolbar -->
          <div class="w-64 p-4 flex flex-col gap-4" :style="{ backgroundColor: 'var(--bg-secondary)', borderLeft: '1px solid var(--border-subtle)' }">
            <!-- Add Node -->
            <div>
              <h4 class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--text-muted);">添加工具</h4>
              <div class="space-y-2">
                <button
                  @click="addNewNode"
                  class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all"
                  :style="{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-main)' }"
                >
                  <PlusIcon class="w-4 h-4" />
                  添加节点
                </button>
              </div>
            </div>

            <!-- Available Tasks -->
            <div class="flex-1 overflow-auto">
              <h4 class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--text-muted);">可用任务</h4>
              <div class="space-y-2">
                <div
                  v-for="task in tasks"
                  :key="task.id"
                  class="p-2 rounded-lg cursor-pointer transition-all"
                  :style="{ backgroundColor: 'var(--bg-tertiary)' }"
                  draggable="true"
                  @dragstart="onTaskDragStart($event, task)"
                  @click="addTaskAsNode(task)"
                >
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: getStatusColor(task.status) }"></span>
                    <span class="text-sm text-gray-200 truncate">{{ task.name }}</span>
                  </div>
                  <div class="text-xs text-gray-500 truncate mt-1">{{ task.script_path }}</div>
                </div>
              </div>
            </div>

            <!-- Edge Mode -->
            <div>
              <h4 class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--text-muted);">连接模式</h4>
              <div class="flex gap-2">
                <button
                  @click="edgeMode = !edgeMode"
                  class="flex-1 px-3 py-2 rounded-lg text-sm transition-all"
                  :style="edgeMode
                    ? { backgroundColor: 'var(--color-primary)', color: 'var(--text-inverse)' }
                    : { backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-muted)' }"
                >
                  {{ edgeMode ? '连接中...' : '连线模式' }}
                </button>
                <button
                  @click="clearAll"
                  class="px-3 py-2 rounded-lg text-sm transition-all"
                  :style="{ backgroundColor: 'var(--color-danger-subtle)', color: 'var(--color-danger)' }"
                >
                  清空
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Execution Result Toast -->
    <div
      v-if="executionResult"
      class="fixed bottom-6 right-6 z-50 rounded-lg p-4 shadow-lg max-w-md"
      :style="{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)' }"
    >
      <div class="flex items-start gap-3">
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center"
          :style="{ backgroundColor: executionResult.success ? 'var(--color-success-subtle)' : 'var(--color-danger-subtle)' }"
        >
          <CheckCircleIcon v-if="executionResult.success" class="w-5 h-5" style="color: var(--color-success);" />
          <XCircleIcon v-else class="w-5 h-5" style="color: var(--color-danger);" />
        </div>
        <div class="flex-1">
          <h4 class="font-medium" style="color: var(--text-main);">{{ executionResult.success ? '执行完成' : '执行失败' }}</h4>
          <p class="text-sm mt-1" style="color: var(--text-muted);">{{ executionResult.message }}</p>
          <div v-if="executionResult.results" class="mt-2 text-xs">
            <div v-for="r in executionResult.results" :key="r.node_id" class="flex gap-2">
              <span style="color: var(--text-muted);">节点 {{ r.node_id }}:</span>
              <span :style="{ color: r.status === 'triggered' ? 'var(--color-success)' : 'var(--color-danger)' }">
                {{ r.status === 'triggered' ? '已触发' : r.status }}
              </span>
            </div>
          </div>
        </div>
        <button @click="executionResult = null" class="p-1">
          <XMarkIcon class="w-4 h-4" style="color: var(--text-muted);" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  PlusIcon, ViewColumnsIcon, PlayIcon, PencilIcon,
  TrashIcon, XMarkIcon, CheckCircleIcon, XCircleIcon
} from '@heroicons/vue/24/outline'
import { taskApi, nodeFlowApi } from '../utils/api.js'

const flows = ref([])
const tasks = ref([])
const showEditor = ref(false)
const editingFlow = ref({ id: null, name: '', nodes: [], edges: [] })
const executing = ref(false)
const executionResult = ref(null)
const edgeMode = ref(false)
const draggedTask = ref(null)
const draggedNode = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const edgeStartNode = ref(null)

async function fetchFlows() {
  try {
    const res = await nodeFlowApi.list()
    flows.value = res.data
  } catch (e) {
    console.error(e)
  }
}

async function fetchTasks() {
  try {
    const res = await taskApi.list()
    tasks.value = res.data
  } catch (e) {
    console.error(e)
  }
}

function createNewFlow() {
  editingFlow.value = {
    id: null,
    name: '新流程 ' + new Date().toLocaleTimeString(),
    nodes: [],
    edges: [],
    is_active: true
  }
  showEditor.value = true
}

function openFlow(flow) {
  try {
    const nodes = typeof flow.nodes === 'string' ? JSON.parse(flow.nodes) : (flow.nodes || [])
    const edges = typeof flow.edges === 'string' ? JSON.parse(flow.edges) : (flow.edges || [])
    editingFlow.value = {
      ...flow,
      nodes,
      edges
    }
    showEditor.value = true
  } catch (e) {
    console.error('Failed to parse flow data:', e)
    editingFlow.value = { ...flow, nodes: [], edges: [] }
    showEditor.value = true
  }
}

function closeEditor() {
  showEditor.value = false
  editingFlow.value = { id: null, name: '', nodes: [], edges: [] }
}

async function saveFlow() {
  try {
    const payload = {
      name: editingFlow.value.name,
      description: '',
      nodes: JSON.stringify(editingFlow.value.nodes),
      edges: JSON.stringify(editingFlow.value.edges),
      is_active: editingFlow.value.is_active
    }
    if (editingFlow.value.id) {
      await nodeFlowApi.update(editingFlow.value.id, payload)
    } else {
      const res = await nodeFlowApi.create(payload)
      editingFlow.value.id = res.data.id
    }
    await fetchFlows()
    closeEditor()
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function executeFlow(flow) {
  if (!flow.id) return
  try {
    executing.value = true
    const res = await nodeFlowApi.execute(flow.id)
    executionResult.value = {
      success: res.data.success,
      message: res.data.success ? '流程执行已触发' : '流程执行失败',
      results: res.data.results
    }
  } catch (e) {
    executionResult.value = {
      success: false,
      message: '执行失败: ' + (e.response?.data?.detail || e.message)
    }
  } finally {
    executing.value = false
    setTimeout(() => { executionResult.value = null }, 5000)
  }
}

async function executeCurrentFlow() {
  if (!editingFlow.value.id) {
    // Save first then execute
    await saveFlow()
  }
  await executeFlow(editingFlow.value)
}

function editFlowName(flow) {
  const newName = prompt('输入新名称:', flow.name)
  if (newName && newName !== flow.name) {
    nodeFlowApi.update(flow.id, { name: newName }).then(fetchFlows)
  }
}

async function deleteFlow(flow) {
  if (!confirm(`确定删除流程 "${flow.name}" 吗？`)) return
  try {
    await nodeFlowApi.delete(flow.id)
    await fetchFlows()
  } catch (e) {
    console.error(e)
  }
}

function addNewNode() {
  const newId = Date.now()
  editingFlow.value.nodes.push({
    id: newId,
    task_id: null,
    label: '新节点',
    description: '双击编辑',
    type: 'task',
    x: 100 + Math.random() * 200,
    y: 100 + Math.random() * 200
  })
}

function addTaskAsNode(task) {
  const newId = Date.now()
  editingFlow.value.nodes.push({
    id: newId,
    task_id: task.id,
    label: task.name,
    description: task.script_path,
    type: 'task',
    x: 100 + Math.random() * 200,
    y: 100 + Math.random() * 200
  })
}

function getNodeColor(type) {
  const colors = { task: '#6366F1', start: '#10B981', end: '#EF4444' }
  return colors[type] || '#6366F1'
}

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

function getEdgePath(edge) {
  const source = editingFlow.value.nodes.find(n => n.id === edge.source)
  const target = editingFlow.value.nodes.find(n => n.id === edge.target)
  if (!source || !target) return ''
  const sx = source.x + 100
  const sy = source.y + 40
  const tx = target.x
  const ty = target.y + 40
  return `M ${sx} ${sy} C ${sx + 50} ${sy}, ${tx - 50} ${ty}, ${tx} ${ty}`
}

function onCanvasMouseDown(e) {
  if (edgeMode.value && edgeStartNode.value) {
    edgeStartNode.value = null
  }
}

function onNodeMouseDown(e, node) {
  if (edgeMode.value) {
    if (!edgeStartNode.value) {
      edgeStartNode.value = node
    } else if (edgeStartNode.value.id !== node.id) {
      // Create edge
      const newId = Date.now()
      editingFlow.value.edges.push({
        id: newId,
        source: edgeStartNode.value.id,
        target: node.id
      })
      edgeStartNode.value = null
    }
    return
  }

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

function onTaskDragStart(e, task) {
  draggedTask.value = task
}

function clearAll() {
  if (confirm('确定清空所有节点和连接吗？')) {
    editingFlow.value.nodes = []
    editingFlow.value.edges = []
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchFlows()
  fetchTasks()
})
</script>
