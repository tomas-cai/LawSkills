<script setup lang="ts">
// @agent: codex
import { ref } from 'vue'
import { showToast } from 'vant'
import { useAuth } from '../../composables/useAuth'

const { signIn } = useAuth()
const mode = ref<'login' | 'register'>('login')
const name = ref('')
const email = ref('')
const password = ref('')
const submitting = ref(false)

async function submit() {
  submitting.value = true
  try {
    if (mode.value === 'register' && (!name.value.trim() || !email.value.trim() || !password.value)) {
      showToast('请填写姓名、邮箱和密码')
      return
    }
    if (!email.value.trim() || !password.value) {
      showToast('请输入邮箱和密码')
      return
    }
    await signIn({ email: email.value.trim(), password: password.value })
    showToast('登录成功（Mock）')
    uni.reLaunch({ url: '/pages/index/index' })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <view class="login-page">
    <view class="brand">
      <text class="brand-title">{{PROJECT_NAME}}</text>
      <text class="brand-sub">AI 简历智能筛选 · 岗位匹配打分</text>
      <text class="brand-demo">demo@hr.local / demo1234（演示账号）</text>
    </view>
    <view class="form">
      <van-field v-if="mode === 'register'" v-model="name" label="姓名" placeholder="你的称呼" />
      <van-field v-model="email" type="email" label="邮箱" placeholder="name@company.com" />
      <van-field v-model="password" type="password" label="密码" :placeholder="mode === 'register' ? '至少 6 位' : '输入密码'" />
      <van-button type="primary" round block :loading="submitting" @click="submit">
        {{ mode === 'login' ? '进入工作台' : '创建并进入' }}
      </van-button>
      <van-button plain round block @click="mode = mode === 'login' ? 'register' : 'login'">
        {{ mode === 'login' ? '注册账号' : '返回登录' }}
      </van-button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: $canvas;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 64rpx 48rpx 140rpx;
}
.brand {
  margin-bottom: 64rpx;
  .brand-title {
    display: block;
    font-size: 56rpx;
    font-weight: 700;
    color: $ink;
  }
  .brand-sub {
    display: block;
    margin-top: 16rpx;
    font-size: 28rpx;
    color: $ink-muted;
  }
  .brand-demo {
    display: block;
    margin-top: 24rpx;
    font-size: 22rpx;
    color: $ink-muted;
  }
}
.form {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
</style>
