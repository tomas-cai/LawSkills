// 平台后台种子数据 —— mock-first 边界：页面/组件只消费数据，切换真实 API 时替换数据源即可
export interface MetricCard {
  label: string
  value: string
  hint: string
  trend: string
  tone?: 'default' | 'primary' | 'success' | 'warning'
}

export interface ActivityItem {
  id: string
  type: string
  detail: string
  time: string
  icon: string
  tone: 'primary' | 'success' | 'warning'
}

export const metricCards: MetricCard[] = [
  { label: '注册企业 / HR', value: '128', hint: '较上月 +12%', trend: '+12%', tone: 'primary' },
  { label: '岗位需求数', value: '342', hint: '本月新增 58', trend: '+8%' },
  { label: '简历解析数', value: '1,286', hint: '解析成功率 99.2%', trend: '+21%', tone: 'success' },
  { label: 'AI 匹配调用', value: '4,905', hint: 'DeepSeek 用量统计', trend: '+35%', tone: 'warning' },
]

export const recentActivity: ActivityItem[] = [
  { id: 'act-1', type: '岗位发布', detail: '高级前端工程师（Vue/TS）', time: '10 分钟前', icon: 'i-lucide-briefcase-business', tone: 'primary' },
  { id: 'act-2', type: '简历解析', detail: 'batch-20260802-01 · 共 46 份', time: '26 分钟前', icon: 'i-lucide-file-check-2', tone: 'success' },
  { id: 'act-3', type: '新企业入驻', detail: '示例科技有限公司', time: '1 小时前', icon: 'i-lucide-building-2', tone: 'warning' },
  { id: 'act-4', type: 'AI 匹配', detail: '岗位 #job-102 · 完成 120 份打分', time: '2 小时前', icon: 'i-lucide-sparkles', tone: 'primary' },
]
