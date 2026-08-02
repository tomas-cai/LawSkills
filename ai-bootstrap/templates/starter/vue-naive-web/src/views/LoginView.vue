<script setup lang="ts">
// @agent: codex
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAuth } from '../composables/useAuth'

const { signInDemo } = useAuth()
const message = useMessage()
const router = useRouter()

const form = reactive({ account: 'demo@example.com', password: 'demo123456' })

function submit() {
  // Mock：联调时替换为真实 JWT API
  signInDemo()
  message.success('登录成功（演示账号）')
  router.push('/')
}
</script>

<template>
  <div class="login-wrap">
    <n-card class="login-card" :bordered="true">
      <h2 class="login-title">{{PROJECT_NAME}}</h2>
      <p class="login-sub">演示凭据已预填，直接登录即可</p>
      <n-form label-placement="top" @submit.prevent="submit">
        <n-form-item label="账号">
          <n-input v-model:value="form.account" placeholder="账号" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="form.password" type="password" placeholder="任意密码" show-password-on="click" />
        </n-form-item>
        <n-button type="primary" attr-type="submit" block class="login-btn">登 录</n-button>
      </n-form>
    </n-card>
  </div>
</template>

<style scoped>
.login-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
}
.login-card {
  width: 400px;
}
.login-title {
  margin: 0 0 4px;
  font-size: 20px;
  color: var(--ink, #172033);
}
.login-sub {
  margin: 0 0 20px;
  font-size: 13px;
  color: var(--ink-muted, #667085);
}
.login-btn {
  margin-top: 8px;
}
</style>
