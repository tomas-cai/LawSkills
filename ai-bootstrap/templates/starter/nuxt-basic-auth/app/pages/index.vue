<script setup lang="ts">
definePageMeta({ middleware: 'author-auth' })

const { user, signOut } = useAuth()
const { projects, refresh } = useProjects()

await refresh()

async function handleSignOut() {
  await signOut()
  await navigateTo('/login')
}
</script>

<template>
  <main class="min-h-screen bg-slate-50">
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">
            Basic Feature Baseline
          </p>
          <p class="font-bold text-slate-900">培训师 AI 助手</p>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-slate-600">{{ user?.name }}</span>
          <UButton
            color="neutral"
            variant="ghost"
            icon="i-lucide-log-out"
            aria-label="退出登录"
            @click="handleSignOut"
          />
        </div>
      </div>
    </header>

    <section class="mx-auto max-w-5xl px-6 py-10">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Projects</p>
          <h1 class="mt-1 text-3xl font-bold text-slate-900">我的客户项目</h1>
        </div>
        <UButton color="primary" icon="i-lucide-plus" label="新建项目" to="/projects/new" />
      </div>

      <div
        v-if="projects.length === 0"
        class="mt-8 rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center"
      >
        <p class="font-semibold text-slate-700">还没有客户培训项目</p>
        <p class="mt-1 text-sm text-slate-500">先创建一个项目，开始你的课程工作流。</p>
      </div>

      <div v-else class="mt-8 grid gap-4 sm:grid-cols-2">
        <UCard v-for="project in projects" :key="project.id" class="rounded-2xl">
          <template #header>
            <div class="flex items-center justify-between text-xs text-slate-500">
              <span>{{ project.clientName }}</span>
              <span>{{ formatProjectDate(project.createdAt) }}</span>
            </div>
          </template>
          <div>
            <UBadge color="warning" variant="subtle" :label="getStatusLabel(project.status)" />
            <h3 class="mt-3 text-lg font-bold text-slate-900">{{ project.title }}</h3>
          </div>
          <template #footer>
            <UButton
              color="neutral"
              variant="link"
              label="编辑项目"
              :to="`/projects/${project.id}/edit`"
            />
          </template>
        </UCard>
      </div>
    </section>
  </main>
</template>
