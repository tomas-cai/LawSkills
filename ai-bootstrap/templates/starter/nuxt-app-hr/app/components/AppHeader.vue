<script setup lang="ts">
const { user, signOut } = useAuth()

async function handleSignOut() {
  await signOut()
  await navigateTo('/login')
}
</script>

<template>
  <header class="sticky top-0 z-20 border-b border-default bg-default/85 backdrop-blur">
    <div class="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
      <NuxtLink to="/" aria-label="返回工作台">
        <AppLogo />
      </NuxtLink>
      <div class="flex items-center gap-3">
        <span class="hidden text-sm text-muted sm:block">{{ user?.name }}</span>
        <UBadge v-if="user?.role" color="primary" variant="soft">{{ user.role }}</UBadge>
        <UButton color="neutral" variant="ghost" icon="i-lucide-log-out" aria-label="退出登录" @click="handleSignOut" />
      </div>
    </div>
  </header>
</template>
