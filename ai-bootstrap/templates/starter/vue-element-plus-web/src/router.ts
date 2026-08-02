// @agent: codex
import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from './views/DashboardView.vue'
import JobsView from './views/JobsView.vue'
import LoginView from './views/LoginView.vue'
import { useAuth } from './composables/useAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: DashboardView },
    { path: '/jobs', name: 'jobs', component: JobsView },
    { path: '/login', name: 'login', component: LoginView },
  ],
})

// 基础鉴权（mock-first）：未登录跳转登录页
router.beforeEach((to) => {
  const { user } = useAuth()
  if (to.name !== 'login' && !user.value) {
    return { name: 'login' }
  }
})

export default router
