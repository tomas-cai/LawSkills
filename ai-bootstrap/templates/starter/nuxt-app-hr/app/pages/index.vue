<script setup lang="ts">
definePageMeta({ middleware: 'author-auth' })

const { user } = useAuth()
const { jobs, refresh } = useJobs()

await refresh()

const stats = computed(() => ({
  total: jobs.value.length,
  active: jobs.value.filter((j) => j.status === 'active').length,
  draft: jobs.value.filter((j) => j.status === 'draft').length,
  paused: jobs.value.filter((j) => j.status === 'paused').length,
}))

const recentJobs = computed(() => jobs.value.slice(0, 5))
</script>

<template>
  <div>
    <!-- 欢迎条 -->
    <section class="relative overflow-hidden rounded-3xl bg-linear-to-br from-brand-700 via-brand-600 to-accent-600 p-8 text-white">
      <div class="relative z-10">
        <p class="text-sm font-medium text-white/80">欢迎回来，{{ user?.name }}</p>
        <h1 class="mt-1 text-2xl font-bold sm:text-3xl">AI 简历智能筛选工作台</h1>
        <p class="mt-2 max-w-xl text-sm text-white/80">录入岗位任职要求 → 导入简历 → AI 自动解析并计算匹配分值 → 输出打分排序清单。</p>
        <div class="mt-5 flex flex-wrap gap-3">
          <UButton to="/jobs/new" color="neutral" class="!bg-white !text-neutral-900 hover:!bg-white/90" icon="i-lucide-plus" label="新建岗位" />
          <UButton color="neutral" variant="outline" class="!text-white !border-white/40 hover:!bg-white/10" icon="i-lucide-upload" label="导入简历（即将上线）" disabled />
        </div>
      </div>
    </section>

    <!-- 指标卡 -->
    <section class="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
      <StatCard label="岗位总数" :value="stats.total" hint="全部岗位需求" />
      <StatCard label="招聘中" :value="stats.active" hint="正在筛选简历" tone="primary" />
      <StatCard label="草稿" :value="stats.draft" hint="待发布" tone="warning" />
      <StatCard label="暂停" :value="stats.paused" hint="暂停招聘" />
    </section>

    <!-- 岗位列表 -->
    <section class="mt-6 overflow-hidden rounded-2xl border border-default bg-default">
      <div class="flex items-center justify-between border-b border-default px-6 py-4">
        <div>
          <h2 class="font-bold text-default">岗位需求</h2>
          <p class="text-sm text-muted">最近的岗位与任职要求</p>
        </div>
        <UButton color="primary" variant="soft" icon="i-lucide-plus" label="新建" to="/jobs/new" />
      </div>

      <EmptyState
        v-if="recentJobs.length === 0"
        title="还没有岗位需求"
        description="先录入第一个岗位的任职要求，再批量导入简历进行匹配打分。"
        icon="i-lucide-briefcase-business"
      >
        <UButton color="primary" label="新建岗位" to="/jobs/new" />
      </EmptyState>

      <ul v-else class="divide-y divide-default">
        <li v-for="job in recentJobs" :key="job.id" class="flex items-center justify-between gap-4 px-6 py-4 transition hover:bg-primary/5">
          <div class="min-w-0">
            <NuxtLink :to="`/jobs/${job.id}/edit`" class="font-semibold text-default hover:underline">
              {{ job.title }}
            </NuxtLink>
            <p class="mt-0.5 truncate text-sm text-muted">
              {{ job.department }} · {{ formatJobDate(job.createdAt) }}
            </p>
          </div>
          <div class="flex shrink-0 items-center gap-3">
            <UBadge :color="getStatusColor(job.status)" variant="soft">{{ getStatusLabel(job.status) }}</UBadge>
            <NuxtLink :to="`/jobs/${job.id}/edit`" class="text-sm font-semibold text-primary">编辑</NuxtLink>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>
