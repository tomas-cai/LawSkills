<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const submitting = ref(false)

const route = useRoute()
const { signIn, signInDemo } = useAuth()

async function submit() {
  errorMessage.value = ''
  submitting.value = true

  try {
    if (!email.value.trim() || !password.value) {
      throw new Error('请输入邮箱和密码。')
    }
    await signIn({ email: email.value.trim(), password: password.value })
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
        <h2 class="text-3xl font-bold leading-tight">平台运营管理后台<br />企业 / 岗位 / 简历解析一站式监管</h2>
        <p class="mt-3 max-w-sm text-sm text-white/80">查看企业入驻与岗位发布，监控简历解析量与 AI 匹配调用，统一运营平台数据。</p>
        <ul class="mt-6 grid gap-2 text-sm text-white/90">
          <li class="flex items-center gap-2"><UIcon name="i-lucide-building-2" class="size-4" /> 企业管理与入驻审核</li>
          <li class="flex items-center gap-2"><UIcon name="i-lucide-file-text" class="size-4" /> 简历解析 / AI 匹配用量</li>
          <li class="flex items-center gap-2"><UIcon name="i-lucide-chart-no-axes-combined" class="size-4" /> 平台运营数据看板</li>
          <li class="flex items-center gap-2"><UIcon name="i-lucide-shield-check" class="size-4" /> 运营角色权限隔离</li>
        </ul>
      </div>
      <p class="relative z-10 text-xs text-white/70">admin@{{PROJECT_SLUG}}.local / admin1234（演示账号）</p>
    </aside>

    <!-- 表单区 -->
    <section class="flex items-center justify-center p-8 sm:p-10">
      <form class="w-full max-w-sm" @submit.prevent="submit">
        <div class="md:hidden"><AppLogo /></div>
        <p class="mt-6 text-xs font-semibold uppercase tracking-widest text-muted md:mt-0">
          {{PROJECT_NAME}} · Admin Console
        </p>
        <h1 class="mt-2 text-2xl font-bold text-default">登录运营管理后台</h1>
        <p class="mt-1 text-sm text-muted">
          企业 / 岗位 / 简历解析 / AI 匹配 运营数据
        </p>

        <div class="mt-5 grid gap-4">
          <UFormField label="邮箱">
            <UInput v-model="email" type="email" placeholder="admin@{{PROJECT_SLUG}}.local" />
          </UFormField>

          <UFormField label="密码">
            <UInput v-model="password" type="password" placeholder="输入密码" />
          </UFormField>

          <UAlert v-if="errorMessage" color="error" variant="soft" :title="errorMessage" />

          <UButton type="submit" size="lg" block color="primary" :loading="submitting" label="进入管理后台" />
          <UButton size="lg" block color="secondary" variant="outline" icon="i-lucide-sparkles" :loading="submitting" label="一键体验演示账号" @click="demoLogin" />
        </div>
      </form>
    </section>
  </div>
</template>
