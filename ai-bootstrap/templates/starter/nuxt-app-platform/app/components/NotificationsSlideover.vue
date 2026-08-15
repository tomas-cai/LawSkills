<script setup lang="ts">
import { recentActivity } from '~/utils/dashboard'

const { isNotificationsSlideoverOpen } = useDashboard()
</script>

<template>
  <USlideover
    v-model:open="isNotificationsSlideoverOpen"
    title="最近动态"
  >
    <template #body>
      <ul class="-mx-3 -mb-3 divide-y divide-default first:-mt-3">
        <li
          v-for="item in recentActivity"
          :key="item.id"
          class="flex items-center gap-3 rounded-md px-3 py-2.5 hover:bg-elevated/50"
        >
          <UChip color="success" inset>
            <UIcon :name="item.icon" class="size-4" />
          </UChip>

          <div class="min-w-0 flex-1 text-sm">
            <p class="font-medium text-highlighted">{{ item.type }}</p>
            <p class="truncate text-dimmed">{{ item.detail }}</p>
          </div>

          <time class="shrink-0 text-xs text-muted">{{ item.time }}</time>
        </li>
      </ul>
    </template>
  </USlideover>
</template>
