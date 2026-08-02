// @agent: codex
import { useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useAuth } from '../hooks/useAuth'

export default function Login({ onSuccess }: { onSuccess: () => void }) {
  const { signInDemo } = useAuth()
  const [account, setAccount] = useState('demo@example.com')
  const [password, setPassword] = useState('demo123456')

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    // Mock：联调时替换为真实 JWT API
    signInDemo()
    onSuccess()
  }

  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <Card className="w-[380px]">
        <CardHeader>
          <CardTitle>{'{{PROJECT_NAME}}'}</CardTitle>
          <CardDescription>演示凭据已预填，直接登录即可</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="flex flex-col gap-4">
            <Input
              value={account}
              onChange={(e) => setAccount(e.target.value)}
              placeholder="账号"
            />
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="密码"
            />
            <Button type="submit" className="w-full bg-primary text-primary-foreground">
              登录
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
