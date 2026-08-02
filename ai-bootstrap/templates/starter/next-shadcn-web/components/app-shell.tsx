'use client'

// @agent: codex
import { useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { BarChart3, Briefcase, LogOut, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'

const navItems = [
  { href: '/dashboard', label: '工作台', icon: BarChart3 },
  { href: '/jobs', label: '岗位管理', icon: Briefcase },
]

export default function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, signOut } = useAuth()

  // Mock-first 路由守卫：未登录一律回登录页
  useEffect(() => {
    if (!user) router.replace('/login')
  }, [user, router])

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="flex w-56 shrink-0 flex-col border-r border-border bg-card">
        <div className="px-5 py-4 text-base font-semibold text-foreground">{'{{PROJECT_NAME}}'}</div>
        <nav className="flex flex-col gap-1 px-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={
                pathname.startsWith(item.href)
                  ? 'flex items-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground'
                  : 'flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              }
            >
              <item.icon className="size-4" />
              {item.label}
            </Link>
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
                router.replace('/login')
              }}
            >
              <LogOut />
              退出
            </Button>
          )}
        </header>
        <main className="flex-1 p-4">{children}</main>
      </div>
    </div>
  )
}
