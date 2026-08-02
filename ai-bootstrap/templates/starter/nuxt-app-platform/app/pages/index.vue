<script setup lang="ts">
// 平台运营概览（骨架占位：数据源待接入 app-web-server /api/admin/stats）
type Tone = 'default' | 'primary' | 'success' | 'warning'
type BadgeTone = 'primary' | 'success' | 'warning'

const metricCards: Array<{ label: string; value: string; hint: string; trend: string; tone?: Tone }> = [
  { label: '注册企业 / HR', value: '128', hint: '较上月 +12%', trend: '+12%', tone: 'primary' },
  { label: '岗位需求数', value: '342', hint: '本月新增 58', trend: '+8%' },
  { label: '简历解析数', value: '1,286', hint: '解析成功率 99.2%', trend: '+21%', tone: 'success' },
  { label: 'AI 匹配调用', value: '4,905', hint: 'DeepSeek 用量统计', trend: '+35%', tone: 'warning' },
]

const recentActivity: Array<{ id: string; type: string; detail: string; time: string; tone: BadgeTone }> = [
  { id: 'act-1', type: '岗位发布', detail: '高级前端工程师（Vue/TS）', time: '10 分钟前', tone: 'primary' },
  { id: 'act-2', type: '简历解析', detail: 'batch-20260802-01 · 共 46 份', time: '26 分钟前', tone: 'success' },
  { id: 'act-3', type: '新企业入驻', detail: '示例科技有限公司', time: '1 小时前', tone: 'warning' },
  { id: 'act-4', type: 'AI 匹配', detail: '岗位 #job-102 · 完成 120 份打分', time: '2 小时前', tone: 'primary' },
]

const toneIconClass: Record<BadgeTone, string> = {
  primary: 'bg-primary/10 text-primary',
  success: 'bg-success/10 text-success',
  warning: 'bg-warning/10 text-warning',
}
</script>

<template>
  <div>
    <header class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-default">运营概览</h1>
        <p class="mt-1 text-sm text-muted">平台级数据看板（骨架占位，接入 API 后展示真实指标）</p>
      </div>
      <UButton color="primary" variant="soft" icon="i-lucide-refresh-cw" label="刷新数据" disabled />
    </header>

    <section class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard v-for="card in metricCards" :key="card.label" v-bind="card" />
    </section>

    <section class="mt-6 overflow-hidden rounded-2xl border border-default bg-default">
      <div class="border-b border-default px-6 py-4">
        <h2 class="font-bold text-default">最近动态</h2>
        <p class="text-sm text-muted">平台关键事件流</p>
      </div>
      <ul class="divide-y divide-default">
        <li v-for="item in recentActivity" :key="item.id" class="flex items-center justify-between gap-4 px-6 py-4">
          <div class="flex min-w-0 items-center gap-3">
            <span class="grid size-9 shrink-0 place-items-center rounded-xl" :class="toneIconClass[item.tone]">
              <UIcon :name="item.tone === 'success' ? 'i-lucide-file-check-2' : item.tone === 'warning' ? 'i-lucide-building-2' : 'i-lucide-briefcase-business'" class="size-4.5" />
            </span>
            <div class="min-w-0">
              <p class="truncate font-medium text-default">{{ item.type }} · {{ item.detail }}</p>
              <p class="text-xs text-muted">{{ item.time }}</p>
            </div>
          </div>
          <UBadge :color="item.tone" variant="soft">{{ item.type }}</UBadge>
        </li>
      </ul>
    </section>
  </div>
</template>
