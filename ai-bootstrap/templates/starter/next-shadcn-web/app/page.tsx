// @agent: codex
import { redirect } from 'next/navigation'

// Mock-first：首页直接进入登录页；登录成功后进入工作台（/dashboard）
export default function Home() {
  redirect('/login')
}
