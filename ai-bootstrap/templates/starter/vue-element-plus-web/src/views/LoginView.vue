<script setup lang="ts">
// @agent: codex
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuth } from '../composables/useAuth'

const { signInDemo } = useAuth()
const router = useRouter()
const form = reactive({ account: 'demo@example.com', password: 'demo123456' })

function submit() {
  // Mock：联调时替换为真实 JWT API
  signInDemo()
  ElMessage.success('登录成功（演示账号）')
  router.push('/')
}
</script>

<template>
  <div class="login-wrap">
    <el-card shadow="never" class="login-card">
      <h2 class="login-title">{{PROJECT_NAME}}</h2>
      <p class="login-sub">演示凭据已预填，直接登录即可</p>
      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item label="账号">
          <el-input v-model="form.account" placeholder="账号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="任意密码" show-password />
        </el-form-item>
        <el-button type="primary" class="login-btn" native-type="submit">登 录</el-button>
      </el-form>
    </el-card>
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
  color: var(--el-text-color-primary, #172033);
}
.login-sub {
  margin: 0 0 20px;
  font-size: 13px;
  color: var(--el-text-color-secondary, #667085);
}
.login-btn {
  width: 100%;
  margin-top: 8px;
}
</style>
