// API 欢迎页：返回带品牌感的 HTML，避免打开端口时显示裸 JSON。
export default defineEventHandler((event) => {
  setResponseHeader(event, 'content-type', 'text/html; charset=utf-8')
  const name = '{{PROJECT_NAME}} API'
  const svc = '{{PROJECT_SLUG}}-web-server'
  return `<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${name}</title>
    <style>
      body { margin: 0; font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #f6f8fc; color: #172033; display: grid; place-items: center; min-height: 100vh; }
      main { max-width: 560px; padding: 40px; }
      .card { background: #fff; border: 1px solid #d8dee9; border-radius: 16px; padding: 32px; box-shadow: 0 8px 24px rgba(23, 32, 51, .06); }
      h1 { margin: 0 0 8px; font-size: 22px; }
      p { color: #667085; font-size: 14px; line-height: 1.7; margin: 4px 0; }
      .badge { display: inline-block; background: #eef2f7; border-radius: 999px; padding: 4px 12px; font-size: 12px; color: #172033; }
      a { color: #4f46e5; font-weight: 600; text-decoration: none; }
      code { background: #eef2f7; border-radius: 6px; padding: 2px 6px; font-size: 13px; }
    </style>
  </head>
  <body>
    <main>
      <div class="card">
        <span class="badge">${svc} · running</span>
        <h1>${name}</h1>
        <p>后端 API 服务运行正常。前端应用：<a href="http://127.0.0.1:3000">HR 工作台 :3000</a> · <a href="http://127.0.0.1:3002">运营后台 :3002</a></p>
        <p>健康检查：<a href="/health"><code>/health</code></a> · 示例接口：<code>/api/echo?name=world</code></p>
      </div>
    </main>
  </body>
</html>`
})
