<script setup lang="ts">
// @agent: codex
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useJobs, type Job } from '../composables/useJobs'

const { jobs, refresh } = useJobs()
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({
  title: '',
  department: '',
  status: 'draft' as Job['status'],
})

onMounted(refresh)

function openCreate() {
  editingId.value = null
  form.title = ''
  form.department = ''
  form.status = 'draft'
  dialogVisible.value = true
}

function openEdit(row: Job) {
  editingId.value = row.id
  form.title = row.title
  form.department = row.department
  form.status = row.status
  dialogVisible.value = true
}

function submit() {
  // Mock：联调时替换为 API adapter
  if (editingId.value) {
    const target = jobs.value.find(j => j.id === editingId.value)
    if (target) Object.assign(target, form)
    ElMessage.success('岗位已更新（Mock）')
  } else {
    jobs.value.unshift({ id: Date.now(), ...form, score: 0 })
    ElMessage.success('岗位已创建（Mock）')
  }
  dialogVisible.value = false
}
</script>

<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>岗位列表</span>
        <el-button type="primary" @click="openCreate">新建岗位</el-button>
      </div>
    </template>

    <el-table :data="jobs">
      <el-table-column prop="title" label="岗位" min-width="180" />
      <el-table-column prop="department" label="部门" width="120" />
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : row.status === 'paused' ? 'warning' : 'info'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="score" label="匹配分" width="100" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="jobs.length === 0" description="暂无岗位，点击右上角新建" />

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑岗位' : '新建岗位'" width="480px">
      <el-form label-width="72px">
        <el-form-item label="岗位名称">
          <el-input v-model="form.title" placeholder="如：前端工程师" />
        </el-form-item>
        <el-form-item label="所属部门">
          <el-input v-model="form.department" placeholder="如：技术部" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="招聘中" value="active" />
            <el-option label="草稿" value="draft" />
            <el-option label="已暂停" value="paused" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
