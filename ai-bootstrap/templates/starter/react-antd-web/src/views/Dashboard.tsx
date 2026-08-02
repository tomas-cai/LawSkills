// @agent: codex
import { Button, Card, Col, Empty, Row, Statistic, Table, Tag } from 'antd'
import type { TableColumnsType } from 'antd'
import { useJobs, type Job } from '../hooks/useJobs'

const columns: TableColumnsType<Job> = [
  { title: '岗位', dataIndex: 'title', key: 'title' },
  { title: '部门', dataIndex: 'department', key: 'department', width: 120 },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
    render: (status: Job['status']) => (
      <Tag color={status === 'active' ? 'success' : status === 'paused' ? 'warning' : 'default'}>
        {status}
      </Tag>
    ),
  },
  { title: '匹配分', dataIndex: 'score', key: 'score', width: 100 },
]

export default function Dashboard({ onManage }: { onManage: () => void }) {
  const { jobs } = useJobs()
  const active = jobs.filter((job) => job.status === 'active').length

  return (
    <div>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic title="在招岗位" value={active} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="草稿岗位" value={jobs.length - active} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="最高匹配分"
              value={jobs.reduce((max, job) => Math.max(max, job.score), 0)}
            />
          </Card>
        </Col>
      </Row>
      <Card
        title="岗位概览"
        style={{ marginTop: 16 }}
        extra={
          <Button type="primary" onClick={onManage}>
            管理岗位
          </Button>
        }
      >
        {jobs.length > 0 ? (
          <Table rowKey="id" columns={columns} dataSource={jobs} pagination={false} />
        ) : (
          <Empty description="暂无岗位数据" />
        )}
      </Card>
    </div>
  )
}
