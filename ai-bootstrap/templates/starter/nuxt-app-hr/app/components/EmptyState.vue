<script setup lang="ts">
withDefaults(
  defineProps<{ title: string; description?: string; icon?: string }>(),
  { description: '', icon: 'i-lucide-inbox' },
)
</script>

<template>
  <div class="flex flex-col items-center justify-center px-6 py-14 text-center">
    <span class="grid size-12 place-items-center rounded-2xl bg-primary/10 text-primary">
      <UIcon :name="icon" class="size-6" />
    </span>
    <p class="mt-4 font-semibold text-default">{{ title }}</p>
    <p v-if="description" class="mt-1 max-w-md text-sm text-muted">{{ description }}</p>
    <div class="mt-5">
      <slot />
    </div>
  </div>
</template>
