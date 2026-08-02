<script setup lang="ts">
// 企业管理（占位页：演示侧边栏路由）
</script>

<template>
  <div>
    <header>
      <h1 class="text-2xl font-bold text-default">企业管理</h1>
      <p class="mt-1 text-sm text-muted">企业 / HR 账号与配额管理</p>
    </header>
    <section class="mt-6 rounded-2xl border border-default bg-default">
      <EmptyState title="企业列表待接入" description="本页将在接入 app-web-server /api/admin/enterprises 后展示数据。" icon="i-lucide-building-2">
        <UButton color="primary" label="查看接口契约" to="/" />
      </EmptyState>
    </section>
  </div>
</template>
