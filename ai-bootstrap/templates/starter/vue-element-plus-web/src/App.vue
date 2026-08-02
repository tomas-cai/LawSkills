<script setup lang="ts">
// @agent: codex
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from './composables/useAuth'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { Briefcase, DataAnalysis, SwitchButton, User } from '@element-plus/icons-vue'

const { user, signOut } = useAuth()
const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => (route.name === 'jobs' ? '/jobs' : '/'))
const pageTitle = computed(() => {
  if (route.name === 'jobs') return '岗位管理'
  if (route.name === 'login') return '登录'
  return '工作台'
})

function onLogout() {
  signOut()
  router.push('/login')
}
</script>

<template>
  <!-- Element Plus 官方 ConfigProvider：中文 locale 统一注入 -->
  <el-config-provider :locale="zhCn">
    <el-container class="app-shell">
      <el-aside width="220px" class="app-aside">
        <div class="brand">{{PROJECT_NAME}}</div>
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/">
            <el-icon><DataAnalysis /></el-icon>
            <span>工作台</span>
          </el-menu-item>
          <el-menu-item index="/jobs">
            <el-icon><Briefcase /></el-icon>
            <span>岗位管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="app-header">
          <div class="page-title">{{ pageTitle }}</div>
          <div class="user-area">
            <el-icon><User /></el-icon>
            <span class="user-name">{{ user?.name ?? '未登录' }}</span>
            <el-button link type="primary" @click="onLogout">
              <el-icon><SwitchButton /></el-icon>
              退出
            </el-button>
          </div>
        </el-header>
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </el-config-provider>
</template>

<style>
/* 全局布局使用 --el-* 语义令牌（tokens.css 定义），页面不散落魔法色值 */
.app-shell {
  min-height: 100vh;
}
.app-aside {
  background: var(--el-bg-color, #f6f8fc);
  border-right: 1px solid var(--el-border-color-lighter, #eef2f7);
}
.brand {
  padding: 20px 24px;
  font-size: 17px;
  font-weight: 700;
  color: var(--el-text-color-primary, #172033);
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--el-fill-color-blank, #ffffff);
  border-bottom: 1px solid var(--el-border-color-lighter, #eef2f7);
}
.page-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary, #172033);
}
.user-area {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-regular, #475467);
}
.app-main {
  background: var(--el-bg-color-page, #f6f8fc);
}
</style>
