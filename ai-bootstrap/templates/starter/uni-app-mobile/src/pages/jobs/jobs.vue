<script setup lang="ts">
// @agent: codex
import { onShow } from '@dcloudio/uni-app'
import { showDialog, showToast } from 'vant'
import { useJobs } from '../../composables/useJobs'

const { jobs, refresh } = useJobs()

onShow(() => {
  refresh()
})

function preview(job: any) {
  showDialog({
    title: job.title,
    message: `当前匹配分值 ${job.score} 分`,
    confirmButtonText: '知道了',
  })
}

function create() {
  showToast('新建岗位（Mock）')
}

function goBack() {
  uni.navigateBack()
}
</script>

<template>
  <view class="page">
    <van-nav-bar title="岗位需求" left-arrow @click-left="goBack" />
    <van-cell-group inset title="岗位列表">
      <van-cell
        v-for="job in jobs"
        :key="job.id"
        :title="job.title"
        :label="`匹配分值 ${job.score}`"
        :value="job.status"
        is-link
        @click="preview(job)"
      />
    </van-cell-group>
    <van-empty v-if="jobs.length === 0" description="还没有岗位需求" />
    <view class="footer">
      <van-button type="primary" round block @click="create">新建岗位</van-button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $canvas;
  padding-bottom: 140rpx;
}
.footer {
  margin: 48rpx 32rpx 0;
}
</style>
