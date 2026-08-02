<script setup lang="ts">
// @agent: codex
import { h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NTag, type DataTableColumns } from 'naive-ui'
import { useJobs, type Job } from '../composables/useJobs'

const { jobs, refresh } = useJobs()
const router = useRouter()

onMounted(refresh)

const columns: DataTableColumns<Job> = [
  { title: '岗位', key: 'title' },
  { title: '部门', key: 'department' },
  {
    title: '状态',
    key: 'status',
    render: (row) =>
      h(
        NTag,
        {
          size: 'small',
          type: row.status === 'active' ? 'success' : row.status === 'paused' ? 'warning' : 'default',
        },
        { default: () => row.status },
      ),
  },
  { title: '匹配分', key: 'score' },
]

function goJobs() {
  router.push('/jobs')
}
</script>

<template>
  <div class="dashboard">
    <n-grid :cols="3" :x-gap="16">
      <n-grid-item>
        <n-card :bordered="true" class="stat-card">
          <div class="stat-label">在招岗位</div>
          <div class="stat-value">{{ jobs.filter(j => j.status === 'active').length }}</div>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card :bordered="true" class="stat-card">
          <div class="stat-label">草稿岗位</div>
          <div class="stat-value">{{ jobs.filter(j => j.status === 'draft').length }}</div>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card :bordered="true" class="stat-card">
          <div class="stat-label">最高匹配分</div>
          <div class="stat-value">{{ Math.max(0, ...jobs.map(j => j.score)) }}</div>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card :bordered="true" class="table-card">
      <template #header>
        <div class="card-header">
          <span>岗位概览</span>
          <n-button type="primary" size="small" @click="goJobs">管理岗位</n-button>
        </div>
      </template>
      <n-data-table :columns="columns" :data="jobs" :bordered="false" />
      <n-empty v-if="jobs.length === 0" description="暂无岗位数据" style="padding: 32px 0" />
    </n-card>
  </div>
</template>

<style scoped>
.stat-card {
  margin-bottom: 16px;
}
.stat-label {
  font-size: 13px;
  color: var(--ink-muted, #667085);
}
.stat-value {
  margin-top: 8px;
  font-size: 28px;
  font-weight: 600;
  color: var(--ink, #172033);
}
.table-card {
  margin-top: 16px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  color: var(--ink, #172033);
}
</style>
