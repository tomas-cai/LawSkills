<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const mode = ref<'login' | 'register'>('login')
const name = ref('')
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const submitting = ref(false)

const route = useRoute()
const { signIn, signUp, signInDemo } = useAuth()

async function submit() {
  errorMessage.value = ''
  submitting.value = true

  try {
    if (mode.value === 'register') {
      if (!name.value.trim() || !email.value.trim() || !password.value) {
        throw new Error('请填写姓名、邮箱和密码。')
      }
      await signUp({
        name: name.value.trim(),
        email: email.value.trim(),
        password: password.value,
      })
    } else {
      await signIn({ email: email.value.trim(), password: password.value })
    }
    await navigateTo((route.query.redirect as string) || '/')
  } catch (error: any) {
    errorMessage.value = error?.data?.statusMessage || error?.message || '操作失败，请稍后重试。'
  } finally {
    submitting.value = false
  }
}

async function demoLogin() {
  errorMessage.value = ''
  submitting.value = true

  try {
    await signInDemo()
    await navigateTo((route.query.redirect as string) || '/')
  } catch (error: any) {
    errorMessage.value = error?.message || '演示账号登录失败。'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="grid w-full max-w-5xl overflow-hidden rounded-3xl border border-default bg-default shadow-2xl">
    <!-- 品牌区 -->
    <aside class="relative hidden overflow-hidden bg-linear-to-br from-brand-700 via-brand-600 to-accent-600 p-10 text-white md:flex md:flex-col md:justify-between">
      <div class="relative z-10">
        <AppLogo name="{{PROJECT_NAME}}" class="[&_span:last-child]:text-white" />
      </div>
      <div class="relative z-10">
        <h2 class="text-3xl font-bold leading-tight">AI 简历智能筛选<br />海量简历自动初筛</h2>
        <p class="mt-3 max-w-sm text-sm text-white/80">录入岗位任职要求，批量导入本地简历，AI 自动解析、计算匹配分值并输出打分排序清单。</p>
        <ul class="mt-6 grid gap-2 text-sm text-white/90">
          <li class="flex items-center gap-2"><UIcon name="i-lucide-check-circle-2" class="size-4" /> 批量本地简历导入</li>
          <li class="flex items-center gap-2"><UIcon name="i-lucide-check-circle-2" class="size-4" /> 简历文本自动抽取</li>
          <li class="flex items-center gap-2"><UIcon name="i-lucide-check-circle-2" class="size-4" /> 岗位-候选人智能匹配打分</li>
          <li class="flex items-center gap-2"><UIcon name="i-lucide-check-circle-2" class="size-4" /> 结果清单导出</li>
        </ul>
      </div>
      <p class="relative z-10 text-xs text-white/70">demo@hr.local / demo1234（演示账号）</p>
    </aside>

    <!-- 表单区 -->
    <section class="flex items-center justify-center p-8 sm:p-10">
      <form class="w-full max-w-sm" @submit.prevent="submit">
        <div class="md:hidden"><AppLogo /></div>
        <p class="mt-6 text-xs font-semibold uppercase tracking-widest text-muted md:mt-0">
          {{PROJECT_NAME}} · AI Resume Matching
        </p>
        <h1 class="mt-2 text-2xl font-bold text-default">
          {{ mode === 'login' ? '登录 HR 工作台' : '创建 HR 账号' }}
        </h1>
        <p class="mt-1 text-sm text-muted">
          AI 简历初筛 · 岗位匹配打分 · 海量简历自动筛选
        </p>

        <div class="mt-5 flex gap-2">
          <UButton :variant="mode === 'login' ? 'solid' : 'outline'" color="primary" label="登录" @click="mode = 'login'" />
          <UButton :variant="mode === 'register' ? 'solid' : 'outline'" color="primary" label="注册" @click="mode = 'register'" />
        </div>

        <div class="mt-5 grid gap-4">
          <UFormField v-if="mode === 'register'" label="姓名">
            <UInput v-model="name" placeholder="你的称呼" />
          </UFormField>

          <UFormField label="邮箱">
            <UInput v-model="email" type="email" placeholder="name@company.com" />
          </UFormField>

          <UFormField label="密码">
            <UInput v-model="password" type="password" :placeholder="mode === 'register' ? '至少 6 位' : '输入密码'" />
          </UFormField>

          <UAlert v-if="errorMessage" color="error" variant="soft" :title="errorMessage" />

          <UButton type="submit" size="lg" block color="primary" :loading="submitting" :label="mode === 'login' ? '进入工作台' : '创建并进入'" />
          <UButton size="lg" block color="secondary" variant="outline" icon="i-lucide-sparkles" :loading="submitting" label="一键体验演示账号" @click="demoLogin" />
        </div>
      </form>
    </section>
  </div>
</template>
