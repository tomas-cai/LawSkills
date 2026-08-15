// 平台管理后台鉴权中间件：未登录访问后台页面一律跳转登录页（保留 redirect 回跳）。
export default defineNuxtRouteMiddleware(async (to) => {
  const { user, fetchMe } = useAuth()

  if (!user.value) {
    try {
      await fetchMe()
    } catch {
      // Stay anonymous.
    }
  }

  if (!user.value) {
    return navigateTo({ path: '/login', query: { redirect: to.fullPath } })
  }
})
