// Nuxt UI 主题入口 —— 语义色映射 + 字体在此统一声明，页面不散落样式细节
// 品牌色阶（brand/accent）在 app/assets/css/main.css 的 @theme static 中定义
export default defineAppConfig({
  ui: {
    colors: {
      primary: 'brand',
      secondary: 'slate',
      accent: 'accent',
      info: 'sky',
      success: 'emerald',
      warning: 'amber',
      error: 'red',
      neutral: 'slate',
    },
    font: {
      sans: '"Inter Variable", "PingFang SC", "Microsoft YaHei", ui-sans-serif, system-ui, sans-serif',
    },
  },
})
