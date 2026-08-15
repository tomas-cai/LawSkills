<script setup lang="ts">
definePageMeta({ middleware: 'admin-auth' })

import { metricCards, recentActivity } from '~/utils/dashboard'

const { isNotificationsSlideoverOpen } = useDashboard()

const toneIconClass: Record<string, string> = {
  primary: 'bg-primary/10 text-primary',
  success: 'bg-success/10 text-success',
  warning: 'bg-warning/10 text-warning',
}
</script>

<template>
  <UDashboardPanel id="home">
    <template #header>
      <UDashboardNavbar title="运营概览" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UTooltip text="最近动态" :shortcuts="['N']">
            <UButton
              color="neutral"
              variant="ghost"
              square
              @click="isNotificationsSlideoverOpen = true"
            >
              <UIcon name="i-lucide-bell" class="size-5 shrink-0" />
            </UButton>
          </UTooltip>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard v-for="card in metricCards" :key="card.label" v-bind="card" />
      </section>

      <section class="mt-6 overflow-hidden rounded-2xl border border-default bg-default">
        <div class="border-b border-default px-6 py-4">
          <h2 class="font-bold text-default">最近动态</h2>
          <p class="text-sm text-muted">平台关键事件流（接入 app-web-server /api/admin/stats 后展示真实数据）</p>
        </div>
        <ul class="divide-y divide-default">
          <li v-for="item in recentActivity" :key="item.id" class="flex items-center justify-between gap-4 px-6 py-4">
            <div class="flex min-w-0 items-center gap-3">
              <span class="grid size-9 shrink-0 place-items-center rounded-xl" :class="toneIconClass[item.tone]">
                <UIcon :name="item.icon" class="size-4.5" />
              </span>
              <div class="min-w-0">
                <p class="truncate font-medium text-default">{{ item.type }} · {{ item.detail }}</p>
                <p class="text-xs text-muted">{{ item.time }}</p>
              </div>
            </div>
            <UBadge :color="item.tone" variant="soft">{{ item.type }}</UBadge>
          </li>
        </ul>
      </section>
    </template>
  </UDashboardPanel>
</template>
