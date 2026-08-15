<script setup lang="ts">
const colorMode = useColorMode()

const color = computed(() => (colorMode.value === 'dark' ? '#0b0f19' : '#ffffff'))

useHead({
  meta: [
    { charset: 'utf-8' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1' },
    { key: 'theme-color', name: 'theme-color', content: color },
  ],
  htmlAttrs: {
    lang: 'zh-CN',
  },
})

const title = '{{PROJECT_NAME}} · 平台运营管理后台'
const description = '{{PROJECT_NAME}}（AI 简历智能筛选助手）平台运营管理后台，基于 Nuxt UI 官方 Dashboard 模板范式构建。'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
})
</script>

<template>
  <UApp>
    <NuxtLoadingIndicator color="primary" />

    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
