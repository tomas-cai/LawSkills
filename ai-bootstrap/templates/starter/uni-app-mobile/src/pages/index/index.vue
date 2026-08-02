<script setup lang="ts">
// @agent: codex
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { showToast } from 'vant'
import { useAuth } from '../../composables/useAuth'
import { useJobs } from '../../composables/useJobs'

const { user, signInDemo } = useAuth()
const { jobs, refresh } = useJobs()
const activeTab = ref(0)

onShow(() => {
  if (!user.value) signInDemo()
  refresh()
})

function createJob() {
  showToast('新建岗位（Mock）')
  uni.navigateTo({ url: '/pages/jobs/jobs' })
}

function goJobs() {
  uni.navigateTo({ url: '/pages/jobs/jobs' })
}

function goLogin() {
  uni.navigateTo({ url: '/pages/login/login' })
}
</script>

<template>
  <van-config-provider class="app-root">
    <view class="page">
      <van-nav-bar title="{{PROJECT_NAME}}" safe-area-inset-top>
        <template #right>
          <view class="nav-user" @click="goLogin">{{ user?.name || '登录' }}</view>
        </template>
      </van-nav-bar>

      <view class="hero">
        <text class="hero-title">AI 简历智能筛选</text>
        <text class="hero-sub">海量简历自动初筛 · 岗位匹配打分</text>
        <van-button type="primary" round block @click="createJob">新建岗位</van-button>
      </view>

      <van-cell-group inset title="岗位概览">
        <van-cell
          v-for="job in jobs.slice(0, 3)"
          :key="job.id"
          :title="job.title"
          :label="`匹配分值 ${job.score}`"
          :value="job.status"
          is-link
          @click="goJobs"
        />
      </van-cell-group>

      <van-tabbar v-model="activeTab" safe-area-inset-bottom>
        <van-tabbar-item icon="home-o">首页</van-tabbar-item>
        <van-tabbar-item icon="apps-o" @click="goJobs">岗位</van-tabbar-item>
        <van-tabbar-item icon="user-o" @click="goLogin">我的</van-tabbar-item>
      </van-tabbar>
    </view>
  </van-config-provider>
</template>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $canvas;
  padding-bottom: 140rpx;
}
.hero {
  margin: 24rpx 32rpx;
  padding: 48rpx 40rpx;
  border-radius: 32rpx;
  background: linear-gradient(135deg, $brand-700, $brand-600 55%, $accent);
  color: #fff;
  .hero-title {
    display: block;
    font-size: 44rpx;
    font-weight: 700;
  }
  .hero-sub {
    display: block;
    margin: 12rpx 0 32rpx;
    font-size: 26rpx;
    opacity: 0.85;
  }
}
.nav-user {
  padding: 0 16rpx;
  font-size: 26rpx;
}
</style>
