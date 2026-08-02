// Basic feature baseline: protect author-only routes.
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
