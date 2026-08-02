// @agent: codex
// Mock-first 岗位 port：页面 → composable → port（Mock adapter / API adapter）
import { ref } from 'vue'

export interface Job {
  id: number
  title: string
  department: string
  status: 'active' | 'draft' | 'paused'
  score: number
}

const mockJobs: Job[] = [
  { id: 1, title: '前端工程师（AI 方向）', department: '技术部', status: 'active', score: 92 },
  { id: 2, title: '产品经理（AI 原生）', department: '产品部', status: 'active', score: 88 },
  { id: 3, title: 'UI 设计师', department: '设计部', status: 'draft', score: 0 },
]

export function useJobs() {
  const jobs = ref<Job[]>([])

  async function refresh(): Promise<void> {
    // Mock adapter：模拟加载延迟；联调时替换为 API adapter（packages/contracts 共享类型）
    jobs.value = [...mockJobs]
  }

  return { jobs, refresh }
}
