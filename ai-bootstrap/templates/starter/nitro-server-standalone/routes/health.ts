export default defineEventHandler(() => ({
  ok: true,
  service: '{{PROJECT_SLUG}}-web-server',
  version: '1.0.0',
  time: new Date().toISOString(),
}))
