<script setup lang="ts">
// @agent: codex
import { computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NIcon, dateZhCN, zhCN } from 'naive-ui'
import { GridOutline, ListOutline, LogOutOutline, PersonOutline } from '@vicons/ionicons5'
import { useAuth } from './composables/useAuth'
import { themeOverrides } from './theme'

const { user, signOut } = useAuth()
const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => (route.name === 'jobs' ? '/jobs' : '/'))
const pageTitle = computed(() => {
  if (route.name === 'jobs') return '岗位管理'
  if (route.name === 'login') return '登录'
  return '工作台'
})

const menuOptions = [
  {
    label: '工作台',
    key: '/',
    icon: () => h(NIcon, null, { default: () => h(GridOutline) }),
  },
  {
    label: '岗位管理',
    key: '/jobs',
    icon: () => h(NIcon, null, { default: () => h(ListOutline) }),
  },
]

function onLogout() {
  signOut()
  router.push('/login')
}
</script>

<template>
  <!-- Naive UI 官方主题入口：n-config-provider :theme-overrides + 中文 locale（zhCN / dateZhCN） -->
  <n-config-provider :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-layout class="app-shell" has-sider>
        <n-layout-sider bordered width="220" class="app-sider">
          <div class="brand">{{PROJECT_NAME}}</div>
          <n-menu
            :value="activeMenu"
            :options="menuOptions"
            @update:value="(key) => router.push(String(key))"
          />
        </n-layout-sider>
        <n-layout>
          <n-layout-header bordered class="app-header">
            <div class="page-title">{{ pageTitle }}</div>
            <div class="user-area">
              <n-icon><PersonOutline /></n-icon>
              <span>{{ user?.name ?? '未登录' }}</span>
              <n-button quaternary size="small" @click="onLogout">
                <template #icon><n-icon><LogOutOutline /></n-icon></template>
                退出
              </n-button>
            </div>
          </n-layout-header>
          <n-layout-content class="app-main" content-style="padding: 16px;">
            <router-view />
          </n-layout-content>
        </n-layout>
      </n-layout>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
/* 全局布局使用 tokens.css 语义令牌，页面不散落魔法色值 */
.app-shell {
  min-height: 100vh;
}
.app-sider {
  background: var(--surface, #ffffff);
}
.brand {
  padding: 20px 24px;
  font-size: 17px;
  font-weight: 700;
  color: var(--ink, #172033);
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--surface, #ffffff);
}
.page-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--ink, #172033);
}
.user-area {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--ink-muted, #667085);
}
.app-main {
  background: var(--canvas, #f6f8fc);
}
</style>
