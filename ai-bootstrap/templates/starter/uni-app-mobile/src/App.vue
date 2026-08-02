<script setup lang="ts">
// uni-app 官方约定：App.vue 只承载应用生命周期与全局样式，不渲染页面模板
import { onLaunch } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('{{PROJECT_NAME}} App Launch')
})
</script>

<style lang="scss">
/* ── 全局设计令牌：Vant 4 CSS 变量覆盖（--van-*）──
 * 语义色与 docs/00-research/design-token-spec.md 一致；
 * SCSS 变量定义在 src/uni.scss（编译期注入），这里在 :root 定义 Vant 运行时变量（H5）；
 * 组件级覆盖用 <van-config-provider :theme-vars>。
 */
:root {
  --van-primary-color: #4f46e5;
  --van-success-color: #15803d;
  --van-warning-color: #b45309;
  --van-danger-color: #b42318;
  --van-text-color: #172033;
  --van-text-color-2: #667085;
  --van-border-color: #d8dee9;
  --van-background: #ffffff;
  --van-background-2: #f6f8fc;
  --van-radius-md: 12px;
}

page {
  background-color: var(--van-background-2);
  color: var(--van-text-color);
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', Helvetica, sans-serif;
}
</style>
