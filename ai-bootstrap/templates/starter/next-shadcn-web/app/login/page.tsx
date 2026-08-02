'use client'

// @agent: codex
import { useState } from 'react'
import type { FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/hooks/useAuth'

export default function LoginPage() {
  const router = useRouter()
  const { signInDemo } = useAuth()
  const [account, setAccount] = useState('demo@example.com')
  const [password, setPassword] = useState('demo123456')
  const [loading, setLoading] = useState(false)

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    // Mock：联调时替换为真实 JWT API
    setTimeout(() => {
      signInDemo()
      router.replace('/dashboard')
    }, 300)
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>{'{{PROJECT_NAME}}'}</CardTitle>
          <CardDescription>演示凭据已预填，直接登录即可</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="flex flex-col gap-4">
            <Input value={account} onChange={(e) => setAccount(e.target.value)} placeholder="账号" />
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="密码" />
            <Button type="submit" disabled={loading} className="w-full bg-primary text-primary-foreground">
              {loading ? '登录中…' : '登录'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  )
}
