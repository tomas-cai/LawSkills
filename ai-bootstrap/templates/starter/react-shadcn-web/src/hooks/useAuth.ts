// @agent: codex
// Mock-first 鉴权 port：页面 → hook → store（Mock adapter / API adapter）
import { create } from 'zustand'

export interface User {
  id: number
  name: string
  role: 'author' | 'admin'
}

const mockUser: User = { id: 1, name: '演示账号', role: 'author' }

interface AuthState {
  user: User | null
  signInDemo: () => void
  signOut: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  signInDemo: () => set({ user: { ...mockUser } }),
  signOut: () => set({ user: null }),
}))

export function useAuth() {
  const user = useAuthStore((state) => state.user)
  const signInDemo = useAuthStore((state) => state.signInDemo)
  const signOut = useAuthStore((state) => state.signOut)
  return { user, signInDemo, signOut }
}
