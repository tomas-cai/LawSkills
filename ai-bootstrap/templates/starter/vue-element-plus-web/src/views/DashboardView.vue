<script setup lang="ts">
// @agent: codex
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useJobs } from '../composables/useJobs'

const { jobs, refresh } = useJobs()
const router = useRouter()

onMounted(refresh)

function goJobs() {
  router.push('/jobs')
}
</script>

<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never" class="stat-card">
          <div class="stat-label">在招岗位</div>
          <div class="stat-value">{{ jobs.filter(j => j.status === 'active').length }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="stat-card">
          <div class="stat-label">草稿岗位</div>
          <div class="stat-value">{{ jobs.filter(j => j.status === 'draft').length }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="stat-card">
          <div class="stat-label">最高匹配分</div>
          <div class="stat-value">{{ Math.max(0, ...jobs.map(j => j.score)) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>岗位概览</span>
          <el-button type="primary" @click="goJobs">管理岗位</el-button>
        </div>
      </template>
      <el-table :data="jobs">
        <el-table-column prop="title" label="岗位" min-width="180" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'paused' ? 'warning' : 'info'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="匹配分" width="100" />
      </el-table>
      <el-empty v-if="jobs.length === 0" description="暂无岗位数据" />
    </el-card>
  </div>
</template>

<style scoped>
.stat-card {
  margin-bottom: 16px;
}
.stat-label {
  color: var(--el-text-color-secondary, #667085);
  font-size: 13px;
}
.stat-value {
  margin-top: 8px;
  font-size: 28px;
  font-weight: 700;
  color: var(--el-text-color-primary, #172033);
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
