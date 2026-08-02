// @agent: codex
import { App as AntdApp, Button, Card, Form, Input } from 'antd'
import { useAuth } from '../hooks/useAuth'

interface LoginForm {
  account: string
  password: string
}

export default function Login({ onSuccess }: { onSuccess: () => void }) {
  const { signInDemo } = useAuth()
  const { message } = AntdApp.useApp()

  function onSubmit(_values: LoginForm) {
    // Mock：联调时替换为真实 JWT API
    signInDemo()
    message.success('登录成功（演示账号）')
    onSuccess()
  }

  return (
    <div
      style={{
        minHeight: '70vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Card title={'{{PROJECT_NAME}}'} style={{ width: 380 }}>
        <p style={{ color: 'rgba(0, 0, 0, 0.45)' }}>演示凭据已预填，直接登录即可</p>
        <Form<LoginForm>
          layout="vertical"
          initialValues={{ account: 'demo@example.com', password: 'demo123456' }}
          onFinish={onSubmit}
        >
          <Form.Item name="account" label="账号" rules={[{ required: true }]}>
            <Input placeholder="账号" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}>
            <Input.Password placeholder="密码" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>
            登录
          </Button>
        </Form>
      </Card>
    </div>
  )
}
