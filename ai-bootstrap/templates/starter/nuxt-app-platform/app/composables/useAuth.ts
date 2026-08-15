// 平台管理后台鉴权：mock-first（localStorage 会话），与 HR 前台 useAuth 同范式。
// 升级到真实 API 时按下方「API adapter 契约」切换，端口契约不变。
export type AuthUser = {
  id: string
  name: string
  email: string
  role: 'admin'
}

const MOCK_DEMO_PASSWORD = 'admin1234'

const MOCK_DEMO_USER: AuthUser = {
  id: 'demo-admin',
  name: '平台管理员',
  email: 'admin@{{PROJECT_SLUG}}.local',
  role: 'admin',
}
const MOCK_USERS_KEY = 'platform-auth:users'
const MOCK_SESSION_KEY = 'platform-auth:session'

type StoredUser = AuthUser & { password: string }

function delay(ms = 350) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function readUsers(): StoredUser[] {
  if (!import.meta.client) return []
  const raw = localStorage.getItem(MOCK_USERS_KEY)
  if (raw) return JSON.parse(raw) as StoredUser[]
  // 首次使用：内置演示账号（后台账号由平台管理员预置，不开放自助注册）
  const seeded: StoredUser[] = [{ ...MOCK_DEMO_USER, password: MOCK_DEMO_PASSWORD }]
  localStorage.setItem(MOCK_USERS_KEY, JSON.stringify(seeded))
  return seeded
}

function readSession(): AuthUser | null {
  if (!import.meta.client) return null
  const raw = localStorage.getItem(MOCK_SESSION_KEY)
  return raw ? JSON.parse(raw) as AuthUser : null
}

export function useAuth() {
  const user = useState<AuthUser | null>('platform-auth:user', () => null)
  const loading = useState<boolean>('platform-auth:loading', () => false)

  async function fetchMe() {
    loading.value = true
    try {
      await delay(200)
      user.value = readSession()
      return user.value
    } finally {
      loading.value = false
    }
  }

  async function signIn(payload: { email: string; password: string }) {
    await delay()
    const stored = readUsers().find((item) => item.email === payload.email)
    if (!stored || stored.password !== payload.password) {
      throw new Error('邮箱或密码不正确。')
    }
    const session: AuthUser = {
      id: stored.id,
      name: stored.name,
      email: stored.email,
      role: stored.role,
    }
    localStorage.setItem(MOCK_SESSION_KEY, JSON.stringify(session))
    user.value = session
    return session
  }

  async function signInDemo() {
    await delay()
    localStorage.setItem(MOCK_SESSION_KEY, JSON.stringify(MOCK_DEMO_USER))
    user.value = MOCK_DEMO_USER
    return MOCK_DEMO_USER
  }

  async function signOut() {
    if (import.meta.client) localStorage.removeItem(MOCK_SESSION_KEY)
    user.value = null
  }

  // API adapter 契约（后端就绪时切换）：
  // async function fetchMe() { return $fetch('/api/auth/me') }
  // async function signIn(payload) { return $fetch('/api/auth/login', { method: 'POST', body: payload }) }
  // async function signOut() { return $fetch('/api/auth/logout', { method: 'POST' }) }

  return { user, loading, fetchMe, signIn, signInDemo, signOut }
}
