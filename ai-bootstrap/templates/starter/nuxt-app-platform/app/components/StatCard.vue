<script setup lang="ts">
withDefaults(
  defineProps<{ label: string; value: string | number; hint?: string; trend?: string; tone?: 'default' | 'primary' | 'success' | 'warning' }>(),
  { hint: '', trend: '', tone: 'default' },
)

const toneClass = {
  default: 'text-default',
  primary: 'text-primary',
  success: 'text-success',
  warning: 'text-warning',
} as const
</script>

<template>
  <div class="rounded-2xl border border-default bg-default p-5 shadow-sm transition hover:shadow-md">
    <div class="flex items-center justify-between">
      <p class="text-sm font-medium text-muted">{{ label }}</p>
      <UBadge v-if="trend" color="success" variant="soft">{{ trend }}</UBadge>
    </div>
    <p class="mt-2 text-3xl font-bold tracking-tight" :class="toneClass[tone]">{{ value }}</p>
    <p v-if="hint" class="mt-1 text-xs text-muted">{{ hint }}</p>
  </div>
</template>
