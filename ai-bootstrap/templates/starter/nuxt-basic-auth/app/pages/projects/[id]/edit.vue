<script setup lang="ts">
definePageMeta({ middleware: 'author-auth' })

const route = useRoute()
const projectId = String(route.params.id)
const { getById, update } = useProjects()

const project = ref<ProjectDto | null>(null)
const clientName = ref('')
const title = ref('')
const status = ref<'draft' | 'active' | 'completed' | 'archived'>('draft')
const errorMessage = ref('')
const notFound = ref(false)
const submitting = ref(false)
const statusOptions = PROJECT_STATUSES.map((item) => ({ label: item.label, value: item.value }))

project.value = await getById(projectId)
if (project.value) {
  clientName.value = project.value.clientName
  title.value = project.value.title
  status.value = project.value.status
} else {
  notFound.value = true
}

async function submit() {
  errorMessage.value = ''
  if (!clientName.value.trim() || !title.value.trim()) {
    errorMessage.value = '请填写客户名称和项目标题。'
    return
  }

  submitting.value = true
  try {
    await update(projectId, {
      clientName: clientName.value.trim(),
      title: title.value.trim(),
      status: status.value
    })
    await navigateTo('/')
  } catch (error: any) {
    errorMessage.value = error?.message || '保存失败，请稍后重试。'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="min-h-screen bg-slate-50 px-6 py-10">
    <div
      v-if="notFound"
      class="mx-auto max-w-2xl rounded-2xl border border-slate-200 bg-white p-8"
    >
      <h1 class="text-2xl font-bold text-slate-900">项目不存在</h1>
      <UButton class="mt-4" color="primary" label="返回工作台" to="/" />
    </div>

    <form
      v-else
      class="mx-auto max-w-2xl rounded-2xl border border-slate-200 bg-white p-8"
      @submit.prevent="submit"
    >
      <NuxtLink to="/" class="text-sm font-semibold text-slate-500">← 返回工作台</NuxtLink>
      <h1 class="mt-4 text-3xl font-bold text-slate-900">编辑客户培训项目</h1>

      <div class="mt-6 grid gap-5">
        <UFormField label="客户名称">
          <UInput v-model="clientName" size="lg" />
        </UFormField>

        <UFormField label="项目标题">
          <UInput v-model="title" size="lg" />
        </UFormField>

        <UFormField label="项目状态">
          <USelect v-model="status" :items="statusOptions" />
        </UFormField>

        <UAlert v-if="errorMessage" color="error" variant="soft" :title="errorMessage" />

        <UButton type="submit" size="lg" color="primary" :loading="submitting" label="保存项目" />
      </div>
    </form>
  </main>
</template>
