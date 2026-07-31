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

- 主按钮：`<UButton color="primary" class="rounded-full">操作</UButton>`
- 次按钮：`<UButton variant="outline" class="rounded-full">取消</UButton>`

## 3. UI 库组件映射

| 场景 | 使用 | 禁止 |
|------|------|------|
| 按钮 | `<UButton>` | `<button class="primary-button">` |
| 卡片 | `<UCard>` | `<div class="feature-card">` |
| 导航 | `<UNavigationMenu>` | `<div class="dropdown-menu">` |
| 弹窗 | `<UModal>` / `<UDialog>` | 自定义弹窗 |
| 表单 | `<UForm>` + `<UInput>` | 自定义（除非 UI 库不满足） |

主题通过 `app.config.ts` 引用设计令牌预设。

## 4. 图标规范

- Lucide Vue Next，2px 线宽
- 推荐双色线性风格
- 图标不成为唯一信息表达方式

## 5. 动画规范

- motion-v，每个 section scroll-triggered 入场
- 卡片列表 stagger children 错帧入场
- hover 微交互：`whileHover={{ y: -4, scale: 1.02 }}`
- 支持 `prefers-reduced-motion`
- 页面切换无过渡（工作台/后台适用）

## 6. 验收清单

除 docs/DESIGN.md 通用验收项外：

- [ ] 页面 metadata 完整（useHead）
- [ ] `nuxi typecheck` 通过
- [ ] 无未使用的自定义 CSS class
- [ ] 每个 section 有入场动画
- [ ] 卡片列表使用 stagger children
- [ ] 交互元素有 hover 微动画
