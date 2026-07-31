# {{PROJECT_NAME}} {{APP_NAME}} — 应用设计规范

版本：v1.0
前置依赖：AGENTS.md + docs/DESIGN.md（品牌规范）

---

## 1. 设计定位

{{APP_DESCRIPTION}}

## 2. Tailwind v4 使用规范

```css
@import "tailwindcss";
@theme {
  --color-primary: {{TOKEN_PRIMARY}};
  --color-on-primary: #ffffff;
  --color-secondary: {{TOKEN_SECONDARY}};
  --color-background: {{TOKEN_BACKGROUND}};
  --color-surface: #ffffff;
  --color-text-main: #191c1d;
  --color-text-muted: {{TOKEN_TEXT_MUTED}};
}
```

工具类优先，禁止自定义 CSS class。

### 卡片/按钮实现

卡片容器：`bg-surface rounded-xl shadow-card p-8`

- 主按钮：`<Button variant="default">操作</Button>`
- 次按钮：`<Button variant="outline">取消</Button>`

## 3. UI 库组件映射

| 场景 | 使用 | 禁止 |
|------|------|------|
| 按钮 | `<Button variant="default">` | `<a class="primary-button">` |
| 卡片 | `<Card>` + `<CardContent>` | `<div class="feature-card">` |
| 导航 | `<NavigationMenu>` | `<div class="dropdown-menu">` |

## 4. 图标规范

- Lucide React，2px 线宽
- 推荐双色线性风格

## 5. 动画规范

- framer-motion，每个 section scroll-triggered 入场
- 卡片列表 stagger children 错帧入场（间隔 0.06-0.1s）
- hover 微交互：`whileHover={{ y: -4, scale: 1.02 }}`
- 支持 `prefers-reduced-motion`
- Hero 环境光效可用 CSS `@keyframes`

## 6. 验收清单

除 docs/DESIGN.md 通用验收项外：

- [ ] 页面 metadata、title、description 完整
- [ ] `npx tsc --noEmit` 通过
- [ ] 每个 section 有入场动画
- [ ] 卡片列表使用 stagger children
- [ ] 首屏 H1 可见、不被动效遮挡
