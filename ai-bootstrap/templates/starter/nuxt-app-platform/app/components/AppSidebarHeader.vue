<script setup lang="ts">
defineProps<{
  collapsed?: boolean
}>()
</script>

<template>
  <div class="flex items-center gap-2.5 px-1 py-2">
    <AppLogo class="shrink-0" />

    <div v-if="!collapsed" class="min-w-0">
      <p class="truncate font-bold text-default">{{PROJECT_NAME}}</p>
      <p class="truncate text-xs text-muted">平台运营管理后台</p>
    </div>
  </div>
</template>
