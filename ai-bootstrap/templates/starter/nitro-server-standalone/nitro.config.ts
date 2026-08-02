import { defineNitroConfig } from 'nitropack/config'

export default defineNitroConfig({
  compatibilityDate: '2025-07-01',
  runtimeConfig: {
    // AI 模型（DeepSeek，OpenAI 兼容接口）——通过环境变量注入
    deepseekApiKey: '',
    deepseekBaseUrl: 'https://api.deepseek.com',
    deepseekModel: 'deepseek-chat',
    // JWT 鉴权（接入真实 API 时启用）
    jwtSecret: '',
  },
})
