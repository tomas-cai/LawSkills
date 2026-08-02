// 演示种子数据：让首屏不再是空状态（生产环境由真实 API 提供）
import type { JobDto } from './job'

export const SEED_JOBS: JobDto[] = [
  {
    id: 'seed-job-1',
    title: '高级前端工程师（Vue/TS）',
    department: '研发中心',
    requirements: '5 年以上前端经验，精通 Vue 3 / TypeScript / Nuxt，有 AI 应用落地经验者优先。',
    status: 'active',
    createdAt: '2026-07-28T09:00:00.000Z',
  },
  {
    id: 'seed-job-2',
    title: 'AI 产品经理（LLM 方向）',
    department: '产品部',
    requirements: '3 年以上 B 端产品经验，熟悉大模型应用与 RAG 方案，能独立完成需求分析与 MRD。',
    status: 'active',
    createdAt: '2026-07-25T02:30:00.000Z',
  },
  {
    id: 'seed-job-3',
    title: '招聘运营专员',
    department: '人力资源部',
    requirements: '2 年以上招聘运营经验，熟悉招聘渠道与简历初筛流程，数据敏感。',
    status: 'draft',
    createdAt: '2026-07-20T08:00:00.000Z',
  },
  {
    id: 'seed-job-4',
    title: '后端工程师（Node.js）',
    department: '研发中心',
    requirements: '熟悉 Node.js / TypeScript / PostgreSQL，有高并发服务经验，了解 Serverless 部署。',
    status: 'paused',
    createdAt: '2026-07-15T06:20:00.000Z',
  },
]
