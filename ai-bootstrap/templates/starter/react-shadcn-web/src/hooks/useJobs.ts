// @agent: codex
// Mock-first 岗位 port：页面 → hook → port（Mock adapter / API adapter）
import { useCallback, useEffect, useState } from 'react'

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
  const [jobs, setJobs] = useState<Job[]>([])

  const refresh = useCallback(async (): Promise<void> => {
    // Mock adapter：模拟加载延迟；联调时替换为 API adapter
    setJobs([...mockJobs])
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const createJob = useCallback((input: Omit<Job, 'id' | 'score'>) => {
    setJobs((prev) => [{ id: Date.now(), ...input, score: 0 }, ...prev])
  }, [])

  const updateJob = useCallback((id: number, input: Omit<Job, 'id' | 'score'>) => {
    setJobs((prev) => prev.map((job) => (job.id === id ? { ...job, ...input } : job)))
  }, [])

  return { jobs, refresh, createJob, updateJob }
}
