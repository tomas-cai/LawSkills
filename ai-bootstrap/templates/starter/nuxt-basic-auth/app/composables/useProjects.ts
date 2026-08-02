// Basic feature baseline: project create/edit with mock-first adapter.
import type { ProjectDto } from '../utils/project'

const MOCK_PROJECTS_KEY = 'basic-auth:projects'

function delay(ms = 350) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function readProjects(): ProjectDto[] {
  if (!import.meta.client) return []
  const raw = localStorage.getItem(MOCK_PROJECTS_KEY)
  return raw ? JSON.parse(raw) as ProjectDto[] : []
}

function writeProjects(projects: ProjectDto[]) {
  localStorage.setItem(MOCK_PROJECTS_KEY, JSON.stringify(projects))
}

export function useProjects() {
  const projects = useState<ProjectDto[]>('basic-auth:projects', () => [])
  const loading = useState<boolean>('basic-auth:projects-loading', () => false)

  async function refresh() {
    loading.value = true
    try {
      await delay()
      projects.value = readProjects().sort((a, b) => b.createdAt.localeCompare(a.createdAt))
      return projects.value
    } finally {
      loading.value = false
    }
  }

  async function create(payload: { clientName: string; title: string }) {
    await delay()
    const project: ProjectDto = {
      id: crypto.randomUUID(),
      clientName: payload.clientName,
      title: payload.title,
      status: 'draft',
      createdAt: new Date().toISOString()
    }
    writeProjects([project, ...readProjects()])
    await refresh()
    return project
  }

  async function update(
    id: string,
    payload: { clientName: string; title: string; status: ProjectDto['status'] }
  ) {
    await delay()
    const next = readProjects().map((item) => (item.id === id ? { ...item, ...payload } : item))
    writeProjects(next)
    await refresh()
    return next.find((item) => item.id === id)
  }

  async function getById(id: string) {
    await delay(150)
    return readProjects().find((item) => item.id === id) || null
  }

  // API adapter contract, switch when the backend is ready:
  // async function refresh() { return $fetch('/api/projects') }
  // async function create(payload) { return $fetch('/api/projects', { method: 'POST', body: payload }) }
  // async function update(id, payload) { return $fetch(`/api/projects/${id}`, { method: 'PATCH', body: payload }) }
  // async function getById(id) { return $fetch(`/api/projects/${id}`) }

  return { projects, loading, refresh, create, update, getById }
}
