// @agent: codex
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useJobs, type Job } from '../hooks/useJobs'

function StatusBadge({ status }: { status: Job['status'] }) {
  return (
    <Badge variant={status === 'active' ? 'default' : status === 'paused' ? 'outline' : 'secondary'}>
      {status}
    </Badge>
  )
}

export default function Dashboard({ onManage }: { onManage: () => void }) {
  const { jobs } = useJobs()
  const active = jobs.filter((job) => job.status === 'active').length
  const maxScore = jobs.reduce((max, job) => Math.max(max, job.score), 0)

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">在招岗位</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-foreground">{active}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">草稿岗位</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-foreground">{jobs.length - active}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">最高匹配分</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-foreground">{maxScore}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>岗位概览</CardTitle>
            <Button size="sm" onClick={onManage}>
              管理岗位
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {jobs.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>岗位</TableHead>
                  <TableHead>部门</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>匹配分</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {jobs.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell>{job.title}</TableCell>
                    <TableCell>{job.department}</TableCell>
                    <TableCell>
                      <StatusBadge status={job.status} />
                    </TableCell>
                    <TableCell>{job.score}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="py-8 text-center text-sm text-muted-foreground">暂无岗位数据</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
