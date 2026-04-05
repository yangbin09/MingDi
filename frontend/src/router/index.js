import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Tasks from '../views/Tasks.vue'
import Settings from '../views/Settings.vue'
import Logs from '../views/Logs.vue'
import AIAssistant from '../views/AIAssistant.vue'
import Flows from '../views/Flows.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: Tasks
  },
  {
    path: '/logs',
    name: 'Logs',
    component: Logs
  },
  {
    path: '/ai',
    name: 'AIAssistant',
    component: AIAssistant
  },
  {
    path: '/flows',
    name: 'Flows',
    component: Flows
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
