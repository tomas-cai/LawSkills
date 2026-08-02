// @agent: codex
import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import './globals.css'

export const metadata: Metadata = {
  title: '{{PROJECT_NAME}}',
  description: '{{PROJECT_NAME}} — AI 招聘助手（Next.js App Router + shadcn/ui DEMO）',
}

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-background text-foreground antialiased">{children}</body>
    </html>
  )
}
