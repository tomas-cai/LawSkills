<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = ref(false)

// 侧边栏导航 —— 对齐官方 nuxt-ui-templates/dashboard 的 UNavigationMenu 范式
const links = [[
  { label: '运营概览', icon: 'i-lucide-layout-dashboard', to: '/', exact: true, onSelect: () => { open.value = false } },
  { label: '企业管理', icon: 'i-lucide-building-2', to: '/enterprises', onSelect: () => { open.value = false } },
  { label: '岗位管理', icon: 'i-lucide-briefcase-business', to: '/jobs', onSelect: () => { open.value = false } },
  { label: '任务与用量', icon: 'i-lucide-gauge', to: '/usage', onSelect: () => { open.value = false } },
  { label: '系统设置', icon: 'i-lucide-settings', to: '/settings', onSelect: () => { open.value = false } },
]] satisfies NavigationMenuItem[][]

const groups = computed(() => [{
  id: 'links',
  label: '前往',
  items: links.flat(),
}])
</script>

<template>
  <UDashboardGroup unit="rem">
    <UDashboardSidebar
      id="default"
      v-model:open="open"
      collapsible
      resizable
      class="bg-elevated/25"
      :ui="{ footer: 'lg:border-t lg:border-default' }"
    >
      <template #header="{ collapsed }">
        <AppSidebarHeader :collapsed="collapsed" />
      </template>

      <template #default="{ collapsed }">
        <UDashboardSearchButton :collapsed="collapsed" class="bg-transparent ring-default" />

        <UNavigationMenu
          :collapsed="collapsed"
          :items="links[0]"
          orientation="vertical"
          tooltip
          popover
        />
      </template>

      <template #footer="{ collapsed }">
        <UserMenu :collapsed="collapsed" />
      </template>
    </UDashboardSidebar>

    <UDashboardSearch :groups="groups" />

    <slot />

    <NotificationsSlideover />
  </UDashboardGroup>
</template>
