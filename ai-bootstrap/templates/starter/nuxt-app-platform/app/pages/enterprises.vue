<script setup lang="ts">
definePageMeta({ middleware: 'admin-auth' })

// 企业管理（占位页：演示 UDashboardPanel + EmptyState 范式）
</script>

<template>
  <UDashboardPanel id="enterprises">
    <template #header>
      <UDashboardNavbar title="企业管理">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <EmptyState
        title="企业列表待接入"
        description="本页将在接入 app-web-server /api/admin/enterprises 后展示企业 / HR 账号与配额数据。"
        icon="i-lucide-building-2"
      >
        <UButton color="primary" label="查看接口契约" to="/" />
      </EmptyState>
    </template>
  </UDashboardPanel>
</template>
