// 招聘岗位领域类型与状态辅助（mock-first 基线）
export type JobDto = {
  id: string
  title: string
  department: string
  requirements: string
  status: 'draft' | 'active' | 'paused' | 'archived'
  createdAt: string
}

export const JOB_STATUSES = [
  { value: 'draft', label: '草稿' },
  { value: 'active', label: '招聘中' },
  { value: 'paused', label: '暂停' },
  { value: 'archived', label: '已归档' },
] as const

export function getStatusLabel(status: string) {
  return JOB_STATUSES.find((item) => item.value === status)?.label ?? '草稿'
}

export type StatusColor = 'primary' | 'warning' | 'neutral' | 'success'

export function getStatusColor(status: string): StatusColor {
  const map: Record<string, StatusColor> = {
    draft: 'neutral',
    active: 'primary',
    paused: 'warning',
    archived: 'neutral',
  }
  return map[status] ?? 'neutral'
}

export function formatJobDate(value: string | Date) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
