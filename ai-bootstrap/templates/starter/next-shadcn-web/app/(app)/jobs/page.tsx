'use client'

// @agent: codex
import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useJobs, type Job } from '@/hooks/useJobs'

interface JobForm {
  title: string
  department: string
  status: Job['status']
}

const emptyForm: JobForm = { title: '', department: '', status: 'draft' }

export default function JobsPage() {
  const { jobs, createJob, updateJob } = useJobs()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Job | null>(null)
  const [form, setForm] = useState<JobForm>(emptyForm)

  function openCreate() {
    setEditing(null)
    setForm(emptyForm)
    setOpen(true)
  }

  function openEdit(job: Job) {
    setEditing(job)
    setForm({ title: job.title, department: job.department, status: job.status })
    setOpen(true)
  }

  function save() {
    if (!form.title.trim()) return
    if (editing) {
      updateJob(editing.id, form)
    } else {
      createJob(form)
    }
    setOpen(false)
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>岗位列表</CardTitle>
          <Button size="sm" onClick={openCreate}>
            新建岗位
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>岗位</TableHead>
              <TableHead>部门</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>匹配分</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {jobs.map((job) => (
              <TableRow key={job.id}>
                <TableCell>{job.title}</TableCell>
                <TableCell>{job.department}</TableCell>
                <TableCell>
                  <Badge
                    variant={job.status === 'active' ? 'default' : job.status === 'paused' ? 'outline' : 'secondary'}
                  >
                    {job.status}
                  </Badge>
                </TableCell>
                <TableCell>{job.score}</TableCell>
                <TableCell className="text-right">
                  <Button variant="link" size="sm" onClick={() => openEdit(job)}>
                    编辑
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? '编辑岗位' : '新建岗位'}</DialogTitle>
            <DialogDescription>Mock 数据：联调时替换为真实 API</DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-4">
            <Input
              placeholder="岗位名称，如：前端工程师"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
            <Input
              placeholder="所属部门，如：技术部"
              value={form.department}
              onChange={(e) => setForm({ ...form, department: e.target.value })}
            />
            <select
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value as Job['status'] })}
              className="border-input bg-background flex h-9 w-full rounded-md border px-3 text-sm"
            >
              <option value="active">招聘中</option>
              <option value="draft">草稿</option>
              <option value="paused">已暂停</option>
            </select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              取消
            </Button>
            <Button onClick={save}>保存</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
