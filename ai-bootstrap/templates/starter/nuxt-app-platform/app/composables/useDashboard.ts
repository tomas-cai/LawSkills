// 平台后台共享状态与键盘快捷键 —— 对齐官方 nuxt-ui-templates/dashboard 的 useDashboard 范式。
// 使用 useState 保证 SSR 安全的共享状态，不额外引入 @vueuse/core。
// 注意：useState 必须在组件 setup / Nuxt 上下文中调用，因此放在函数体内，
// 相同 key 的 useState 在应用内天然共享，无需模块级调用。
let shortcutsRegistered = false

export const useDashboard = () => {
  const route = useRoute()
  const router = useRouter()
  const isNotificationsSlideoverOpen = useState('platform-notifications-open', () => false)

  // 键盘导航：g-h 运营概览 / g-e 企业管理 / g-j 岗位管理 / g-s 系统设置 / n 最近动态
  if (!shortcutsRegistered) {
    shortcutsRegistered = true
    defineShortcuts({
      'g-h': () => router.push('/'),
      'g-e': () => router.push('/enterprises'),
      'g-j': () => router.push('/jobs'),
      'g-s': () => router.push('/settings'),
      n: () => (isNotificationsSlideoverOpen.value = !isNotificationsSlideoverOpen.value),
    })
  }

  watch(() => route.fullPath, () => {
    isNotificationsSlideoverOpen.value = false
  })

  return {
    isNotificationsSlideoverOpen,
  }
}
