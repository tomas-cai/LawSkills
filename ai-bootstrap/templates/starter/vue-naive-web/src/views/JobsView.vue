<script setup lang="ts">
// @agent: codex
import { h, reactive, ref } from 'vue'
import { NTag, useMessage, type DataTableColumns } from 'naive-ui'
import { useJobs, type Job } from '../composables/useJobs'

const { jobs, createJob, updateJob } = useJobs()
const message = useMessage()

const showModal = ref(false)
const editing = ref<Job | null>(null)
const form = reactive<{ title: string; department: string; status: Job['status'] }>({
  title: '',
  department: '',
  status: 'draft',
})

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
  {
    title: '操作',
    key: 'action',
    render: (row) =>
      h(
        'a',
        {
          style: 'cursor: pointer; color: var(--primary, #2563eb);',
          onClick: () => openEdit(row),
        },
        '编辑',
      ),
  },
]

function openCreate() {
  editing.value = null
  form.title = ''
  form.department = ''
  form.status = 'draft'
  showModal.value = true
}

function openEdit(job: Job) {
  editing.value = job
  form.title = job.title
  form.department = job.department
  form.status = job.status
  showModal.value = true
}

function save() {
  if (!form.title.trim()) {
    message.warning('请输入岗位名称')
    return
  }
  if (editing.value) {
    updateJob(editing.value.id, { ...form })
    message.success('岗位已更新（Mock）')
  } else {
    createJob({ ...form })
    message.success('岗位已创建（Mock）')
  }
  showModal.value = false
}
</script>

<template>
  <n-card :bordered="true">
    <template #header>
      <div class="card-header">
        <span>岗位列表</span>
        <n-button type="primary" size="small" @click="openCreate">新建岗位</n-button>
      </div>
    </template>
    <n-data-table :columns="columns" :data="jobs" :bordered="false" />

    <n-modal
      v-model:show="showModal"
      preset="card"
      :title="editing ? '编辑岗位' : '新建岗位'"
      style="width: 480px"
      :mask-closable="false"
    >
      <n-form label-placement="top">
        <n-form-item label="岗位名称">
          <n-input v-model:value="form.title" placeholder="如：前端工程师" />
        </n-form-item>
        <n-form-item label="所属部门">
          <n-input v-model:value="form.department" placeholder="如：技术部" />
        </n-form-item>
        <n-form-item label="状态">
          <n-select
            v-model:value="form.status"
            :options="[
              { label: '招聘中', value: 'active' },
              { label: '草稿', value: 'draft' },
              { label: '已暂停', value: 'paused' },
            ]"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-footer">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" @click="save">保存</n-button>
        </div>
      </template>
    </n-modal>
  </n-card>
</template>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  color: var(--ink, #172033);
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
