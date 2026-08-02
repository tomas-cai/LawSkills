// @agent: codex
// Mock-first 鉴权 port：页面 → composable → port（Mock adapter / API adapter）
import { ref } from 'vue'

export interface AuthUser {
  name: string
  email: string
  role: 'author'
}

const demoUser: AuthUser = { name: '演示用户', email: 'demo@hr.local', role: 'author' }

export function useAuth() {
  const user = ref<AuthUser | null>(null)

  function signInDemo(): AuthUser {
    user.value = demoUser
    return user.value
  }

  async function signIn(payload: { email: string; password: string }): Promise<AuthUser> {
    if (payload.email && payload.password) {
      return signInDemo()
    }
    throw new Error('邮箱或密码错误')
  }

  return { user, signIn, signInDemo }
}
