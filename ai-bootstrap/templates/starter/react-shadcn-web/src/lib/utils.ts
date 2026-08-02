// @agent: codex
// shadcn 官方 cn()：shadcn init 生成 src/lib/utils.ts（clsx + tailwind-merge）
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
