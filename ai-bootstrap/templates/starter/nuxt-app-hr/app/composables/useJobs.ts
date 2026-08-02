// 岗位需求 CRUD（mock-first adapter；后端就绪时切换为 $fetch）
import { SEED_JOBS } from '../utils/seed'
import type { JobDto } from '../utils/job'

const MOCK_JOBS_KEY = 'basic-auth:jobs'
const SEED_FLAG_KEY = 'basic-auth:jobs-seeded'

function delay(ms = 350) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function readJobs(): JobDto[] {
  if (!import.meta.client) return []
  const raw = localStorage.getItem(MOCK_JOBS_KEY)
  if (!raw) return []
  return JSON.parse(raw) as JobDto[]
}

function ensureSeeded() {
  if (!import.meta.client) return
  if (!localStorage.getItem(SEED_FLAG_KEY)) {
    localStorage.setItem(MOCK_JOBS_KEY, JSON.stringify(SEED_JOBS))
    localStorage.setItem(SEED_FLAG_KEY, '1')
  }
}

function writeJobs(jobs: JobDto[]) {
  localStorage.setItem(MOCK_JOBS_KEY, JSON.stringify(jobs))
}

export function useJobs() {
  const jobs = useState<JobDto[]>('basic-auth:jobs', () => [])
  const loading = useState<boolean>('basic-auth:jobs-loading', () => false)

  async function refresh() {
    loading.value = true
    try {
      await delay()
      ensureSeeded()
      jobs.value = readJobs().sort((a, b) => b.createdAt.localeCompare(a.createdAt))
      return jobs.value
    } finally {
      loading.value = false
    }
  }

  async function create(payload: { title: string; department: string; requirements: string }) {
    await delay()
    ensureSeeded()
    const job: JobDto = {
      id: crypto.randomUUID(),
      title: payload.title,
      department: payload.department,
      requirements: payload.requirements,
      status: 'draft',
      createdAt: new Date().toISOString(),
    }
    writeJobs([job, ...readJobs()])
    await refresh()
    return job
  }

  async function update(
    id: string,
    payload: { title: string; department: string; requirements: string; status: JobDto['status'] },
  ) {
    await delay()
    ensureSeeded()
    const next = readJobs().map((item) => (item.id === id ? { ...item, ...payload } : item))
    writeJobs(next)
    await refresh()
    return next.find((item) => item.id === id)
  }

  async function getById(id: string) {
    await delay(150)
    ensureSeeded()
    return readJobs().find((item) => item.id === id) || null
  }

  // API adapter 契约（后端就绪时切换）：
  // async function refresh() { return $fetch('/api/jobs') }
  // async function create(payload) { return $fetch('/api/jobs', { method: 'POST', body: payload }) }
  // async function update(id, payload) { return $fetch(`/api/jobs/${id}`, { method: 'PATCH', body: payload }) }
  // async function getById(id) { return $fetch(`/api/jobs/${id}`) }

  return { jobs, loading, refresh, create, update, getById }
}
