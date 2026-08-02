// Basic feature baseline: author auth with mock-first adapter.
export type AuthUser = {
  id: string
  name: string
  email: string
  role: 'author'
}

const MOCK_DEMO_PASSWORD = 'demo1234'

const MOCK_DEMO_USER: AuthUser = {
  id: 'demo-author',
  name: '演示培训师',
  email: 'demo@trainer.local',
  role: 'author'
}
const MOCK_USERS_KEY = 'basic-auth:users'
const MOCK_SESSION_KEY = 'basic-auth:session'

type StoredUser = AuthUser & { password: string }

function delay(ms = 350) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function readUsers(): StoredUser[] {
  if (!import.meta.client) return []
  const raw = localStorage.getItem(MOCK_USERS_KEY)
  if (raw) return JSON.parse(raw) as StoredUser[]
  // 首次使用：内置演示账号，让页面展示的演示凭据可直接登录
  const seeded: StoredUser[] = [{ ...MOCK_DEMO_USER, password: MOCK_DEMO_PASSWORD }]
  localStorage.setItem(MOCK_USERS_KEY, JSON.stringify(seeded))
  return seeded
}

function writeUsers(users: StoredUser[]) {
  localStorage.setItem(MOCK_USERS_KEY, JSON.stringify(users))
}

function readSession(): AuthUser | null {
  if (!import.meta.client) return null
  const raw = localStorage.getItem(MOCK_SESSION_KEY)
  return raw ? JSON.parse(raw) as AuthUser : null
}

export function useAuth() {
  const user = useState<AuthUser | null>('basic-auth:user', () => null)
  const loading = useState<boolean>('basic-auth:loading', () => false)

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
      role: stored.role
    }
    localStorage.setItem(MOCK_SESSION_KEY, JSON.stringify(session))
    user.value = session
    return session
  }

  async function signUp(payload: { name: string; email: string; password: string }) {
    await delay()
    if (readUsers().some((item) => item.email === payload.email)) {
      throw new Error('该邮箱已注册。')
    }
    const stored: StoredUser = {
      id: crypto.randomUUID(),
      name: payload.name,
      email: payload.email,
      password: payload.password,
      role: 'author'
    }
    writeUsers([...readUsers(), stored])
    const session: AuthUser = {
      id: stored.id,
      name: stored.name,
      email: stored.email,
      role: stored.role
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

  // API adapter contract, switch when the backend is ready:
  // async function fetchMe() { return $fetch('/api/auth/me') }
  // async function signIn(payload) { return $fetch('/api/auth/login', { method: 'POST', body: payload }) }
  // async function signUp(payload) { return $fetch('/api/auth/register', { method: 'POST', body: payload }) }
  // async function signOut() { return $fetch('/api/auth/logout', { method: 'POST' }) }

  return { user, loading, fetchMe, signIn, signUp, signInDemo, signOut }
}
