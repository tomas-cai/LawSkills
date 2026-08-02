<script setup lang="ts">
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
        password: password.value
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
  <main class="grid min-h-screen place-items-center bg-slate-50 p-6">
    <form class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8" @submit.prevent="submit">
      <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Basic Feature Baseline</p>
      <h1 class="mt-2 text-2xl font-bold text-slate-900">
        {{ mode === 'login' ? '登录工作台' : '创建作者账号' }}
      </h1>

      <div class="mt-5 flex gap-2">
        <UButton
          :variant="mode === 'login' ? 'solid' : 'outline'"
          color="primary"
          label="登录"
          @click="mode = 'login'"
        />
        <UButton
          :variant="mode === 'register' ? 'solid' : 'outline'"
          color="primary"
          label="注册"
          @click="mode = 'register'"
        />
      </div>

      <div class="mt-5 grid gap-4">
        <UFormField v-if="mode === 'register'" label="姓名">
          <UInput v-model="name" placeholder="你的称呼" />
        </UFormField>

        <UFormField label="邮箱">
          <UInput v-model="email" type="email" placeholder="name@company.com" />
        </UFormField>

        <UFormField label="密码">
          <UInput
            v-model="password"
            type="password"
            :placeholder="mode === 'register' ? '至少 6 位' : '输入密码'"
          />
        </UFormField>

        <UAlert v-if="errorMessage" color="error" variant="soft" :title="errorMessage" />

        <UButton
          type="submit"
          size="lg"
          block
          color="primary"
          :loading="submitting"
          :label="mode === 'login' ? '进入工作台' : '创建并进入'"
        />
        <UButton
          size="lg"
          block
          color="secondary"
          variant="outline"
          :loading="submitting"
          label="使用演示作者账号"
          @click="demoLogin"
        />
      </div>
    </form>
  </main>
</template>
