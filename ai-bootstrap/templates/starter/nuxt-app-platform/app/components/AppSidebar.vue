<script setup lang="ts">
const nav = [
  { label: '运营概览', to: '/', icon: 'i-lucide-layout-dashboard', active: true },
  { label: '企业管理', to: '/enterprises', icon: 'i-lucide-building-2', active: false },
  { label: '岗位管理', to: '/jobs', icon: 'i-lucide-briefcase-business', active: false },
  { label: '任务与用量', to: '/usage', icon: 'i-lucide-gauge', active: false },
  { label: '系统设置', to: '/settings', icon: 'i-lucide-settings', active: false },
]
</script>

<template>
  <aside class="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-default bg-default lg:flex">
    <div class="flex h-16 items-center border-b border-default px-5">
      <AppLogo />
    </div>
    <nav class="mt-3 grid flex-1 gap-1 px-3">
      <NuxtLink
        v-for="item in nav"
        :key="item.label"
        :to="item.to"
        class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition"
        :class="item.active ? 'bg-primary/10 text-primary' : 'text-muted hover:bg-primary/5 hover:text-default'"
      >
        <UIcon :name="item.icon" class="size-4.5" />
        {{ item.label }}
      </NuxtLink>
    </nav>
    <div class="border-t border-default px-5 py-4">
      <p class="text-xs text-muted">平台运营管理后台</p>
    </div>
  </aside>
</template>
