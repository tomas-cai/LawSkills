// @agent: codex
// Mock-first 鉴权 port：页面 → composable → port（Mock adapter / API adapter）
import { computed, ref } from 'vue'

export interface User {
  id: number
  name: string
  role: 'author' | 'admin'
}

const mockUser: User = { id: 1, name: '演示账号', role: 'author' }

const user = ref<User | null>(null)

export function useAuth() {
  const isAuthed = computed(() => user.value !== null)

  function signInDemo(): void {
    user.value = { ...mockUser }
  }

  function signOut(): void {
    user.value = null
  }

  return { user, isAuthed, signInDemo, signOut }
}
