# {{PROJECT_NAME}} — Codex 执行规则（全局路由层）

## Superpowers 开发方法论

本项目使用 [obra/superpowers](https://github.com/obra/superpowers) 技能系统。
在开始任何任务前，先读取 `{{PLATFORM_SKILLS_PATH}}/using-superpowers/SKILL.md` 并按任务类型调用对应技能。

### 文档产出规范

所有项目文档放在 `docs/` 下，按阶段归档：

```
docs/
  00-research/       # 调研、竞品分析
  01-requirements/   # 需求规格
  02-specs/          # 设计规格
  03-plans/          # 实施计划
  04-reviews/        # 代码审查
  05-verification/   # 验证记录
  06-decisions/      # 决策记录
```

所有品牌共享设计/视觉细节 → `docs/DESIGN.md`
所有应用特定设计规范 → `docs/design/{app}-design.md`

---

## 应用识别与设计文档路由

Agent 开始任务前，必须先确定目标应用，然后加载对应设计文档：

| 路径前缀 | 应用 | 框架 | 设计文档 |
|---------|------|------|---------|
{{APPS_ROWS}}
| 跨 app 或不确定 | — | — | 仅用 AGENTS.md + docs/DESIGN.md |

**规则**：按路径匹配 → 加载设计文档 → 结合全局规则执行。

{{DEV_TABLE}}

---

## 设计令牌约束（不可违反，全应用统一）

{{COLOR_TABLE}}

---

## 排版与布局约束（共享常量）

- 字体系列：`Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- Body 正文：16px / 400 / 1.6
- Button 按钮：16px / 600

应用特有布局见 `docs/design/{app}-design.md`。

---

## 代码生成规则

### Motion 动效（Nuxt 适用）

- 唯一动效库：**motion-v**。GSAP 禁用
- 每个 section 必须 scroll-triggered 入场
- 卡片列表必须 stagger children 错帧入场
- Hover 微交互：`whileHover={{ y: -4, scale: 1.02 }}`
- Hero 环境光效可用 CSS `@keyframes`
- 支持 `prefers-reduced-motion` 降级

### Tailwind v4 与 UI 库

全局规则见 `docs/DESIGN.md`。应用特有组件使用规范见 `docs/design/{app}-design.md`。

{{MONOREPO_RULES}}

---

## 禁止事项

- 自定义 `.primary-button` / `.feature-card` / `.dropdown-menu` 等 class
- 多套 UI 库混用
- 首屏关键文案放进 Canvas / WebGL / 图片
- 为动效引入大体积库（GSAP、Three.js 等）
- 使用未定义颜色或旧版令牌
- 纯 CSS 动画替代 motion-v（Nuxt 应用适用；Hero 环境光效除外）
- 无 metadata、sitemap、canonical 的页面上线（官网适用）
{{MONOREPO_NO_IMPORT}}

---

## 优先级规则

### 通用（所有应用）

1. **设计令牌矩阵**（品牌色约束最高）
2. **验收清单**（可访问性 / 性能 / Monorepo）

### Nuxt 应用（如有）

3. **Motion 规范**（入场动画必须实现）
4. **UI 库规范**（组件标准优先）
5. **Tailwind v4 规范**（工具类优先于自定义 CSS）

---

## 验收清单（通用）

应用特有验收项见 `docs/design/{app}-design.md`。

- [ ] 所有图片有 `alt`
- [ ] 无横向滚动
- [ ] 按钮符合 Pill 形状与对比度要求
- [ ] 卡片符合 12px 圆角、白色背景要求
- [ ] 所有内部共享包引用使用 `workspace:*` 协议
