<script setup lang="ts">
definePageMeta({ middleware: 'author-auth' })

const { create } = useProjects()
const clientName = ref('')
const title = ref('')
const errorMessage = ref('')
const submitting = ref(false)

async function submit() {
  errorMessage.value = ''
  if (!clientName.value.trim() || !title.value.trim()) {
    errorMessage.value = '请填写客户名称和项目标题。'
    return
  }

  submitting.value = true
  try {
    await create({
      clientName: clientName.value.trim(),
      title: title.value.trim()
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
  <main class="min-h-screen bg-slate-50 px-6 py-10">
    <form
      class="mx-auto max-w-2xl rounded-2xl border border-slate-200 bg-white p-8"
      @submit.prevent="submit"
    >
      <NuxtLink to="/" class="text-sm font-semibold text-slate-500">← 返回工作台</NuxtLink>
      <h1 class="mt-4 text-3xl font-bold text-slate-900">新建客户培训项目</h1>

      <div class="mt-6 grid gap-5">
        <UFormField label="客户名称">
          <UInput v-model="clientName" size="lg" placeholder="例如：远岑科技" />
        </UFormField>

        <UFormField label="项目标题">
          <UInput v-model="title" size="lg" placeholder="例如：管理者训练营" />
        </UFormField>

        <UAlert v-if="errorMessage" color="error" variant="soft" :title="errorMessage" />

        <UButton type="submit" size="lg" color="primary" :loading="submitting" label="创建项目" />
      </div>
    </form>
  </main>
</template>
