<script setup lang="ts">
withDefaults(defineProps<{ name?: string }>(), { name: '{{PROJECT_NAME}}' })
</script>

<template>
  <span class="inline-flex items-center gap-2.5">
    <span class="grid size-9 shrink-0 place-items-center rounded-xl bg-linear-to-br from-brand-600 to-accent-600 text-white shadow-sm">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 3l7 3v5c0 4.5-3 8.2-7 9.5-4-1.3-7-5-7-9.5V6l7-3z" fill="white" fill-opacity="0.92" />
        <path d="M8.5 12.6l2.3 2.3 4.7-4.7" stroke="#172033" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </span>
    <span class="text-base font-bold leading-none tracking-tight text-default">{{ name }}</span>
  </span>
</template>
