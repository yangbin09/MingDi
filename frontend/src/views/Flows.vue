<template>
  <div class="flows-page space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--text-main);">
          <el-icon class="mr-2"><Connection /></el-icon>
          编排中心
        </h1>
        <p class="text-sm mt-1" style="color: var(--text-muted);">可视化 DAG 节点编排与流程管理</p>
      </div>
      <el-button type="primary" @click="createNewFlow">
        <el-icon><Plus /></el-icon>
        新建流程
      </el-button>
    </div>

    <!-- Flows List -->
    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8" v-for="flow in flows" :key="flow.id">
        <el-card shadow="hover" class="flow-card" @click="openFlow(flow)">
          <div class="flow-header">
            <el-avatar :style="{ backgroundColor: 'rgba(168, 85, 247, 0.15)' }">
              <el-icon><Connection /></el-icon>
            </el-avatar>
            <div class="flex-1">
              <div class="font-medium">{{ flow.name }}</div>
              <div class="text-xs" style="color: var(--text-muted);">{{ flow.description || '无描述' }}</div>
            </div>
            <el-tag :type="flow.is_active ? 'success' : 'info'" size="small">
              {{ flow.is_active ? '启用' : '禁用' }}
            </el-tag>
          </div>
          <div class="flow-footer">
            <el-button-group>
              <el-tooltip content="执行流程" placement="top">
                <el-button size="small" type="success" plain @click.stop="executeFlow(flow)">
                  <el-icon><VideoPlay /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑" placement="top">
                <el-button size="small" type="primary" plain @click.stop="openFlow(flow)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <el-button size="small" type="danger" plain @click.stop="deleteFlow(flow)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>
            <span class="text-xs" style="color: var(--text-disabled);">
              {{ formatDate(flow.updated_at) }}
            </span>
          </div>
        </el-card>
      </el-col>

      <!-- Empty State -->
      <el-col v-if="flows.length === 0" :span="24">
        <el-card shadow="never" class="empty-card">
          <el-empty description="暂无编排流程" />
          <el-button type="primary" @click="createNewFlow">
            <el-icon><Plus /></el-icon>
            新建流程
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- Flow Editor Dialog -->
    <el-dialog
      v-model="showEditor"
      :title="editingFlow.name || '流程编辑器'"
      width="90%"
      top="5vh"
      destroy-on-close
      class="flow-editor-dialog"
    >
      <div class="editor-toolbar">
        <el-input v-model="editingFlow.name" placeholder="流程名称" class="flow-name-input" />
        <div class="toolbar-actions">
          <el-button type="primary" @click="saveFlow">
            <el-icon><Check /></el-icon>
            保存
          </el-button>
          <el-button type="success" @click="executeCurrentFlow" :loading="executing">
            <el-icon><VideoPlay /></el-icon>
            {{ executing ? '执行中...' : '执行' }}
          </el-button>
        </div>
      </div>

      <div class="editor-container">
        <!-- Canvas Area -->
        <div class="canvas-area" ref="canvasRef">
          <!-- Grid Background -->
          <div class="grid-bg"></div>

          <!-- Nodes -->
          <div
            v-for="node in editingFlow.nodes"
            :key="node.id"
            class="flow-node"
            :style="{ left: node.x + 'px', top: node.y + 'px' }"
            @mousedown="onNodeMouseDown($event, node)"
          >
            <div class="node-header">
              <span class="node-dot" :style="{ backgroundColor: getNodeColor(node.type) }"></span>
              <span class="node-label">{{ node.label }}</span>
            </div>
            <div class="node-desc">{{ node.description }}</div>
            <div v-if="node.task_id" class="node-task">
              任务 #{{ node.task_id }}
            </div>
          </div>

          <!-- SVG for edges -->
          <svg class="edges-svg">
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

        <!-- Sidebar -->
        <div class="editor-sidebar">
          <div class="sidebar-section">
            <h4 class="sidebar-title">添加工具</h4>
            <el-button class="w-full" @click="addNewNode">
              <el-icon><Plus /></el-icon>
              添加节点
            </el-button>
          </div>

          <div class="sidebar-section flex-1 overflow-auto">
            <h4 class="sidebar-title">可用任务</h4>
            <div class="task-list">
              <div
                v-for="task in tasks"
                :key="task.id"
                class="task-item"
                @click="addTaskAsNode(task)"
              >
                <span class="task-dot" :style="{ backgroundColor: getStatusColor(task.status) }"></span>
                <span class="task-name">{{ task.name }}</span>
              </div>
            </div>
          </div>

          <div class="sidebar-section">
            <h4 class="sidebar-title">连接模式</h4>
            <div class="flex gap-2">
              <el-button
                :type="edgeMode ? 'primary' : 'default'"
                @click="edgeMode = !edgeMode"
                class="flex-1"
              >
                {{ edgeMode ? '连线中...' : '连线模式' }}
              </el-button>
              <el-button type="danger" @click="clearAll">清空</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- Execution Result -->
    <el-notification
      v-if="executionResult"
      :title="executionResult.success ? '执行完成' : '执行失败'"
      :type="executionResult.success ? 'success' : 'error'"
      :description="executionResult.message"
      position="bottom-right"
      @close="executionResult = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Connection, Plus, VideoPlay, Edit, Delete, Check
} from '@element-plus/icons-vue'
import { taskApi, nodeFlowApi } from '../utils/api.js'

const flows = ref([])
const tasks = ref([])
const showEditor = ref(false)
const editingFlow = ref({ id: null, name: '', nodes: [], edges: [] })
const executing = ref(false)
const executionResult = ref(null)
const edgeMode = ref(false)
const draggedNode = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const edgeStartNode = ref(null)
const canvasRef = ref(null)

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
      ElMessage.success('流程已保存')
    } else {
      const res = await nodeFlowApi.create(payload)
      editingFlow.value.id = res.data.id
      ElMessage.success('流程已创建')
    }
    await fetchFlows()
    showEditor.value = false
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function executeFlow(flow) {
  if (!flow.id) return
  try {
    executing.value = true
    const res = await nodeFlowApi.execute(flow.id)
    executionResult.value = {
      success: res.data.success,
      message: res.data.success ? '流程执行已触发' : '流程执行失败'
    }
    ElMessage.success('流程执行已触发')
  } catch (e) {
    executionResult.value = {
      success: false,
      message: '执行失败: ' + (e.response?.data?.detail || e.message)
    }
    ElMessage.error('执行失败')
  } finally {
    executing.value = false
  }
}

async function executeCurrentFlow() {
  if (!editingFlow.value.id) {
    await saveFlow()
  }
  await executeFlow(editingFlow.value)
}

async function deleteFlow(flow) {
  try {
    await ElMessageBox.confirm(`确定删除流程 "${flow.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await nodeFlowApi.delete(flow.id)
    await fetchFlows()
    ElMessage.success('流程已删除')
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
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

function onNodeMouseDown(e, node) {
  if (edgeMode.value) {
    if (!edgeStartNode.value) {
      edgeStartNode.value = node
    } else if (edgeStartNode.value.id !== node.id) {
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

function clearAll() {
  editingFlow.value.nodes = []
  editingFlow.value.edges = []
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

<style scoped>
.flow-card {
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.flow-card:hover {
  transform: translateY(-2px);
}

.flow-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.flow-header .flex-1 {
  flex: 1;
  min-width: 0;
}

.flow-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-card {
  text-align: center;
  padding: 48px;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.flow-name-input {
  width: 300px;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
}

.editor-container {
  display: flex;
  height: 60vh;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  overflow: hidden;
}

.canvas-area {
  flex: 1;
  position: relative;
  background-color: var(--bg-tertiary);
  overflow: auto;
}

.grid-bg {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, var(--border-subtle) 1px, transparent 1px);
  background-size: 20px 20px;
  opacity: 0.5;
}

.flow-node {
  position: absolute;
  min-width: 160px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 12px;
  cursor: move;
  box-shadow: var(--shadow-soft);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.node-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.node-label {
  font-weight: 500;
  color: var(--text-main);
}

.node-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.node-task {
  font-size: 11px;
  padding: 2px 8px;
  background-color: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 4px;
}

.edges-svg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  width: 100%;
  height: 100%;
}

.editor-sidebar {
  width: 240px;
  background-color: var(--bg-secondary);
  border-left: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.sidebar-section {
  margin-bottom: 16px;
}

.sidebar-section.flex-1 {
  flex: 1;
  overflow: auto;
}

.sidebar-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background-color: var(--bg-tertiary);
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.task-item:hover {
  background-color: var(--bg-hover);
}

.task-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.task-name {
  font-size: 13px;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
