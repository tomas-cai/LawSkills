// Basic feature baseline: project domain types and status helpers.
export type ProjectDto = {
  id: string
  clientName: string
  title: string
  status: 'draft' | 'active' | 'completed' | 'archived'
  createdAt: string
}

export const PROJECT_STATUSES = [
  { value: 'draft', label: '草稿' },
  { value: 'active', label: '进行中' },
  { value: 'completed', label: '已完成' },
  { value: 'archived', label: '已归档' }
] as const

export function getStatusLabel(status: string) {
  return PROJECT_STATUSES.find((item) => item.value === status)?.label ?? '草稿'
}

export function formatProjectDate(value: string | Date) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return `${date.getMonth() + 1} 月 ${date.getDate()} 日`
}
