// @agent: codex
import { useState } from 'react'
import { Button, Layout, Menu, theme } from 'antd'
import type { MenuProps } from 'antd'
import {
  BarChartOutlined,
  BriefcaseOutlined,
  LogoutOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { useAuth } from './hooks/useAuth'
import Dashboard from './views/Dashboard'
import Jobs from './views/Jobs'
import Login from './views/Login'

const { Header, Sider, Content } = Layout

type ViewKey = 'dashboard' | 'jobs' | 'login'

const menuItems: MenuProps['items'] = [
  { key: 'dashboard', icon: <BarChartOutlined />, label: '工作台' },
  { key: 'jobs', icon: <BriefcaseOutlined />, label: '岗位管理' },
]

export default function App() {
  const [view, setView] = useState<ViewKey>('dashboard')
  const { user, signOut } = useAuth()
  const { token } = theme.useToken()

  const current: ViewKey = user ? view : 'login'

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={220}>
        <div
          style={{
            color: '#fff',
            padding: 16,
            fontSize: 16,
            fontWeight: 600,
            whiteSpace: 'nowrap',
          }}
        >
          {'{{PROJECT_NAME}}'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[current]}
          items={menuItems}
          onClick={({ key }) => setView(key as ViewKey)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: token.colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            gap: 12,
            paddingInline: 24,
          }}
        >
          <UserOutlined />
          <span>{user?.name ?? '未登录'}</span>
          {user && (
            <Button
              type="text"
              icon={<LogoutOutlined />}
              onClick={() => {
                signOut()
                setView('login')
              }}
            >
              退出
            </Button>
          )}
        </Header>
        <Content style={{ margin: 16 }}>
          {current === 'login' ? (
            <Login onSuccess={() => setView('dashboard')} />
          ) : current === 'jobs' ? (
            <Jobs />
          ) : (
            <Dashboard onManage={() => setView('jobs')} />
          )}
        </Content>
      </Layout>
    </Layout>
  )
}
