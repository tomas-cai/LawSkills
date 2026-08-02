<script setup lang="ts">
definePageMeta({ middleware: 'author-auth' })

const title = ref('')
const department = ref('')
const requirements = ref('')
const errorMessage = ref('')
const submitting = ref(false)

const { create } = useJobs()

async function submit() {
  errorMessage.value = ''
  if (!title.value.trim() || !department.value.trim() || !requirements.value.trim()) {
    errorMessage.value = '请填写岗位名称、用人部门和任职要求。'
    return
  }

  submitting.value = true
  try {
    await create({
      title: title.value.trim(),
      department: department.value.trim(),
      requirements: requirements.value.trim(),
    })
    await navigateTo('/')
  } catch (error: any) {
    errorMessage.value = error?.message || '创建失败，请稍后重试。'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form class="mx-auto max-w-2xl rounded-2xl border border-default bg-default p-8" @submit.prevent="submit">
    <NuxtLink to="/" class="inline-flex items-center gap-1 text-sm font-semibold text-muted">
      <UIcon name="i-lucide-arrow-left" class="size-4" /> 返回工作台
    </NuxtLink>
    <h1 class="mt-4 text-3xl font-bold text-default">新建招聘岗位</h1>
    <p class="mt-1 text-sm text-muted">任职要求越完整，AI 匹配打分越准。</p>

    <div class="mt-6 grid gap-5">
      <UFormField label="岗位名称">
        <UInput v-model="title" size="lg" placeholder="例如：高级前端工程师" />
      </UFormField>

      <UFormField label="用人部门">
        <UInput v-model="department" size="lg" placeholder="例如：研发中心" />
      </UFormField>

      <UFormField label="任职要求" :hint="`已输入 ${requirements.length} 字`">
        <UTextarea v-model="requirements" :rows="8" placeholder="分点列出学历、经验、技能与加分项，便于 AI 精准匹配" />
      </UFormField>

      <UAlert v-if="errorMessage" color="error" variant="soft" :title="errorMessage" />

      <div class="flex items-center justify-end gap-3">
        <UButton color="neutral" variant="outline" label="取消" to="/" />
        <UButton type="submit" color="primary" icon="i-lucide-check" :loading="submitting" label="创建岗位" />
      </div>
    </div>
  </form>
</template>
