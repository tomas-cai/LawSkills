// @agent: codex
import { useState } from 'react'
import { App as AntdApp, Button, Card, Form, Input, Modal, Select, Table, Tag } from 'antd'
import type { TableColumnsType } from 'antd'
import { useJobs, type Job } from '../hooks/useJobs'

interface JobForm {
  title: string
  department: string
  status: Job['status']
}

export default function Jobs() {
  const { jobs, createJob, updateJob } = useJobs()
  const { message } = AntdApp.useApp()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Job | null>(null)
  const [form] = Form.useForm<JobForm>()

  const columns: TableColumnsType<Job> = [
    { title: '岗位', dataIndex: 'title', key: 'title' },
    { title: '部门', dataIndex: 'department', key: 'department', width: 120 },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 110,
      render: (status: Job['status']) => (
        <Tag color={status === 'active' ? 'success' : status === 'paused' ? 'warning' : 'default'}>
          {status}
        </Tag>
      ),
    },
    { title: '匹配分', dataIndex: 'score', key: 'score', width: 100 },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Button
          type="link"
          onClick={() => {
            setEditing(record)
            form.setFieldsValue(record)
            setOpen(true)
          }}
        >
          编辑
        </Button>
      ),
    },
  ]

  function openCreate() {
    setEditing(null)
    form.resetFields()
    setOpen(true)
  }

  async function onSubmit() {
    const values = await form.validateFields()
    if (editing) {
      updateJob(editing.id, values)
      message.success('岗位已更新（Mock）')
    } else {
      createJob(values)
      message.success('岗位已创建（Mock）')
    }
    setOpen(false)
  }

  return (
    <Card
      title="岗位列表"
      extra={
        <Button type="primary" onClick={openCreate}>
          新建岗位
        </Button>
      }
    >
      <Table rowKey="id" columns={columns} dataSource={jobs} pagination={false} />
      <Modal
        title={editing ? '编辑岗位' : '新建岗位'}
        open={open}
        onOk={onSubmit}
        onCancel={() => setOpen(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            name="title"
            label="岗位名称"
            rules={[{ required: true, message: '请输入岗位名称' }]}
          >
            <Input placeholder="如：前端工程师" variant="outlined" />
          </Form.Item>
          <Form.Item name="department" label="所属部门">
            <Input placeholder="如：技术部" variant="outlined" />
          </Form.Item>
          <Form.Item name="status" label="状态" initialValue="draft">
            <Select
              options={[
                { value: 'active', label: '招聘中' },
                { value: 'draft', label: '草稿' },
                { value: 'paused', label: '已暂停' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
