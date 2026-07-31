# {{PROJECT_NAME}} {{APP_NAME}} — 应用设计规范

版本：v1.0
前置依赖：AGENTS.md + docs/DESIGN.md（品牌规范）

---

## 1. 设计定位

{{APP_DESCRIPTION}}

设计核心目标：移动优先、操作轻量、加载快速、信息一目了然。

## 2. 技术栈

- 框架：uni-app（Vue 3）
- UI 库：nutui-uniapp
- 样式：SCSS
- 动效：uni-app 原生动画 API

## 3. 布局规范

- 内容区左右安全距离 16px
- 点击目标最小 44x44px
- 底部 Tab 不超过 5 个
- 列表行高 50px（单行）/ 72px（双行）

## 4. 组件使用规范

| 场景 | 使用 | 禁止 |
|------|------|------|
| 按钮 | `<nut-button type="primary">` | 自定义 button |
| 卡片 | `<nut-card>` | 手写卡片容器 |
| 表单 | `<nut-form>` + `<nut-input>` | 手写校验 |
| 弹窗 | `<nut-dialog>` / `<nut-popup>` | 自定义弹窗 |
| 列表 | `<nut-cell>` | 手写列表 |
| 空状态 | `<nut-empty>` | 手写占位图 |

### 卡片/按钮实现

- 卡片：`<nut-card>`，主题已预设 12px 圆角及白色背景
- 主按钮：`<nut-button type="primary" round>`，对应主色
- 次按钮：`<nut-button plain round>`，描边样式

## 5. 交互规范

- 列表支持纵向无限滚动，下拉刷新
- 左滑显示快捷操作（nutui `Swipe`）
- 首次加载使用骨架屏（nutui `Skeleton`）
- 避免点击元素间距小于 8px
- 底部安全区域适配

## 6. 品牌色引用

```scss
$primary-color: {{TOKEN_PRIMARY}};
$text-color: #191c1d;
$page-background-color: #f8fafb;
```

## 7. 验收清单

除 docs/DESIGN.md 通用验收项外：

- [ ] 可点击区域满足 44x44px
- [ ] 列表支持下拉刷新
- [ ] 空数据使用 Empty 组件
- [ ] 首次加载使用骨架屏
- [ ] 底部安全区域已适配
- [ ] 横向滚动视为缺陷
