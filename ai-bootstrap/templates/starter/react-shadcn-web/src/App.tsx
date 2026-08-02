// @agent: codex
import { useState } from 'react'
import { BarChart3, Briefcase, LogOut, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuth } from './hooks/useAuth'
import Dashboard from './views/Dashboard'
import Jobs from './views/Jobs'
import Login from './views/Login'

type ViewKey = 'dashboard' | 'jobs' | 'login'

const navItems = [
  { key: 'dashboard' as ViewKey, label: '工作台', icon: BarChart3 },
  { key: 'jobs' as ViewKey, label: '岗位管理', icon: Briefcase },
]

export default function App() {
  const [view, setView] = useState<ViewKey>('dashboard')
  const { user, signOut } = useAuth()
  const current: ViewKey = user ? view : 'login'

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="flex w-56 shrink-0 flex-col border-r border-border bg-card">
        <div className="px-5 py-4 text-base font-semibold text-foreground">{'{{PROJECT_NAME}}'}</div>
        <nav className="flex flex-col gap-1 px-3">
          {navItems.map((item) => (
            <button
              key={item.key}
              onClick={() => setView(item.key)}
              className={
                current === item.key
                  ? 'flex items-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground'
                  : 'flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              }
            >
              <item.icon className="size-4" />
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center justify-end gap-3 border-b border-border bg-card px-6">
          <User className="size-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">{user?.name ?? '未登录'}</span>
          {user && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                signOut()
                setView('login')
              }}
            >
              <LogOut />
              退出
            </Button>
          )}
        </header>
        <main className="flex-1 p-4">
          {current === 'login' ? (
            <Login onSuccess={() => setView('dashboard')} />
          ) : current === 'jobs' ? (
            <Jobs />
          ) : (
            <Dashboard onManage={() => setView('jobs')} />
          )}
        </main>
      </div>
    </div>
  )
}
