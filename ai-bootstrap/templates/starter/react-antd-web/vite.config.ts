// React + Vite 官方入口：@vitejs/plugin-react
// Ant Design v6 默认 ES modules tree shaking，import { Button } from 'antd' 即按需，无需 babel-plugin-import。
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
