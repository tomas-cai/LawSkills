#!/usr/bin/env python3
"""
AI Bootstrap — Framework Component Gate（框架组件门禁注册表）

单一事实源：生成器（generate.py）与校验器（validate.py）共用。

职责分层：
- DEPRECATED_COMPONENTS   → validate.py 扫描生成项目源码，拦截已废弃组件名的使用
- FRAMEWORK_CONSTRAINTS   → generate.py 将约束渲染进 DESIGN.md「框架约束」，作为治理记账；
                            official_demo_url / official_docs_url 渲染进 README「与官方 DEMO 对齐」
                            清单与 docs/00-research/design-token-spec.md，
                            保证初始化始终以所选 UI 栈的官方 starter / demo / template 为基准。

新 UI 栈入库时：先查官方 starter / quickstart / template / theming 文档，
登记 official_demo_url / official_docs_url 与约束说明，再接入 generate.py 与 validate.py。
"""

import re

# 已废弃 → 替代组件（扫描 .vue / .ts 源码中的组件使用；键为大小写敏感组件名）
DEPRECATED_COMPONENTS: dict[str, str] = {
    # Nuxt UI v3→v4：UFormGroup 已重命名为 UFormField。
    # v4 不再注册 UFormGroup，会导致 SSR 塌陷（表单字段整体消失）与 hydration mismatch。
    "UFormGroup": "UFormField",
}

# 渲染进 DESIGN.md「框架约束」的说明（按技术栈生效）。
# 每个条目必须登记 official_demo_url（官方 demo / starter / template 站点）与
# official_docs_url（官方安装 / 主题文档），缺失时对齐清单会标记「待登记」。
FRAMEWORK_CONSTRAINTS: list[dict] = [
    {
        "library": "@nuxt/ui",
        "version": "4.x",
        "official_demo_url": "https://nuxt.com/templates",
        "official_docs_url": "https://ui.nuxt.com/docs/getting-started/installation",
        "notes": [
            "Nuxt UI v4 将 `UFormGroup` 重命名为 `UFormField`：表单分组一律使用 `<UFormField label=\"...\">`，"
            "禁止使用已废弃的 `UFormGroup`（v4 不再注册，会导致 SSR 塌陷与 hydration mismatch）。"
            "`validate.py` 的 `framework-component-gate` 校验会拦截该问题。",
            "@nuxt/icon 默认 CSS 模式：图标通过 CSS mask 渲染为 `<span class=\"iconify\">`，属正常行为，"
            "不要误判为空图标或改为内联 SVG。若出现 `[Icon] failed to load icon` 警告，"
            "优先确认图标名在对应 collection 中存在（如新版 lucide 将 `check-circle-2` 更名为 `circle-check-big`）。",
        ],
    },
    {
        "library": "vant",
        "version": "4.x",
        "official_demo_url": "https://vant-ui.github.io/vant/",
        "official_docs_url": "https://vant-ui.github.io/vant/#/zh-CN/home",
        "notes": [
            "Vant 4 起官方移除 `babel-plugin-import`：不要再引入该插件，按官方 quickstart 二选一接入——"
            "常规用法 `import 'vant/lib/index.css'` + `app.use(Button)`（官方推荐，Tree Shaking 默认可用），"
            "或按需用法 `unplugin-vue-components` + `@vant/auto-import-resolver`（`VantResolver`，不引入全量 css）。",
            "禁止同时使用全量 `vant/lib/index.css` 与 VantResolver 按需引入（组件重复注册、样式错乱）。"
            "`validate.py` 的 `ui-stack-conformance` 校验会拦截该反模式。",
            "主题定制使用 700+ 个 `--van-*` CSS 变量：全局在 `:root` 覆盖，组件级用 "
            "`<van-config-provider :theme-vars>`；不要直接改 node_modules 里的样式。",
            "函数式 API（`showToast` / `showDialog` 等）从 `vant` 直接导入即可。",
        ],
    },
    {
        "library": "element-plus",
        "version": "2.x",
        "official_demo_url": "https://github.com/element-plus/element-plus",
        "official_docs_url": "https://element-plus.org/zh-CN/",
        "notes": [
            "Element Plus 2.x 官方 quickstart 二选一接入，禁止混用：完整引入 `import ElementPlus from 'element-plus'` "
            "+ `import 'element-plus/dist/index.css'` + `app.use(ElementPlus)`（快速开始，官方推荐），"
            "或按需用法 `unplugin-vue-components` + `unplugin-auto-import` + `ElementPlusResolver`"
            "（来自 `unplugin-vue-components/resolvers`，此时不引入全量 css 且 vite.config 需配置插件）。",
            "禁止同时使用全量 `element-plus/dist/index.css` 与 ElementPlusResolver（组件重复注册、样式错乱）；"
            "也不要使用 `babel-plugin-import`。`validate.py` 的 `ui-stack-conformance` 校验会拦截该反模式。",
            "主题定制使用 `--el-*` CSS 变量（`:root` 全局覆盖或组件类名作用域覆盖）或 SCSS "
            "`@use 'element-plus/theme-chalk/src/common/var.scss' with (...)`；不要直接改 node_modules 里的样式。",
            "Volar 全局组件类型：tsconfig `compilerOptions.types` 加入 `element-plus/global`；"
            "中文 locale 用 `element-plus/es/locale/lang/zh-cn`，经 `el-config-provider` 或 `app.use` 选项注入。",
        ],
    },
    {
        "library": "antd",
        "version": "6.x",
        "official_demo_url": "https://github.com/ant-design/ant-design",
        "official_docs_url": "https://ant.design/",
        "notes": [
            "Ant Design v6 官方快速上手：`import { ConfigProvider, ... } from 'antd'` + `import zhCN from 'antd/locale/zh_CN'` "
            "+ `dayjs.locale('zh-cn')`；antd 默认 ES modules tree shaking，`import { Button } from 'antd'` 即按需，"
            "无需 babel-plugin-import 或手写按需配置。",
            "主题入口是 `ConfigProvider theme`（`token` + `algorithm`，Design Token），v6 默认启用 CSS variables；"
            "组件色只由 theme.token 驱动，页面不散落 hex 直接覆盖 antd 组件默认色。",
            "v6 必须移除 `@ant-design/v5-patch-for-react-19`（仅 v5 需要），`@ant-design/icons` 需 >= 6。"
            "`validate.py` 的 `ui-stack-conformance` 校验会拦截该反模式。",
            "v6 弃用 API：`bordered` → `variant`、`size='default'` → `'medium'`、children 列表 → `items`、"
            "`dropdownClassName` → `classNames.popup.root`、Button `iconPosition` → `iconPlacement`、"
            "Space `direction` → `orientation`。",
        ],
    },
    {
        "library": "shadcn/ui",
        "version": "3.x（v2 为 legacy）",
        "official_demo_url": "https://ui.shadcn.com/",
        "official_docs_url": "https://v3.shadcn.com/docs/installation/vite",
        "notes": [
            "shadcn/ui 官方安装范式（v3.shadcn.com/docs/installation/vite + Tailwind v4）："
            "不是 npm 依赖，而是‘源码拷贝进项目’的组件库——pnpm dlx shadcn@latest init 生成 components.json、"
            "globals.css 主题变量（--primary / --radius 等 CSS 变量 + 语义类名）与 src/lib/utils.ts（cn()），"
            "组件用 pnpm dlx shadcn@latest add <component> 拷进 src/components/ui/。"
            "Vite 接入：全局 CSS 以 @import \"tailwindcss\" 起步 + vite 插件 @tailwindcss/vite，tsconfig/vite 配 @/* 路径别名。"
            "Next.js App Router 接入：app/ + components/ + lib/ + components.json，PostCSS 插件 @tailwindcss/postcss。"
            "主题色只改 CSS 变量（--primary / --radius），页面使用 bg-primary / text-muted 等语义类名，不散落 hex 直接覆盖组件默认色。"
            "禁止 babel-plugin-import 或运行时按需插件。`validate.py` 的 `ui-stack-conformance` 校验会拦截该反模式。",
        ],
    },
    {
        "library": "naive-ui",
        "version": "2.x",
        "official_demo_url": "https://www.naiveui.com/zh-CN/os-theme",
        "official_docs_url": "https://www.naiveui.com/",
        "notes": [
            "Naive UI 2.x 官方范式（naiveui.com 快速上手 + 主题定制）：不需要导入任何 CSS（组件独立导出、tree-shaking 友好），"
            "禁止 import 'naive-ui/dist/index.css' 之类的全量样式导入；组件直接 import { NButton } from 'naive-ui'。"
            "主题入口是 n-config-provider :theme-overrides（JS 对象，GlobalThemeOverrides；暗色用 darkTheme）"
            "+ locale={zhCN} date-locale={dateZhCN}（均来自 naive-ui，中文环境必须注入）。"
            "按需可配 unplugin-vue-components + NaiveUiResolver + unplugin-auto-import。"
            "主题令牌集中在一个 theme.ts 导出 themeOverrides 对象，页面不散落 hex。"
            "`validate.py` 的 `ui-stack-conformance` 校验会拦截该反模式。",
        ],
    },
]


def _normalize_name(name: str) -> str:
    """归一化库名（去掉 @ / - _ 空白等），使 'nuxt-ui' 与 '@nuxt/ui' 等价。"""
    return "".join(ch for ch in name.lower() if ch.isalnum())


def constraints_for_ui_library(ui_library: str | None) -> list[dict]:
    """按 UI 库名返回适用约束；支持复合名（如 'vant + uni-ui'）与未知库（返回空列表）。"""
    return official_references_for_ui_library(ui_library)


def _library_matches(target: str, library_norm: str) -> bool:
    """注册表命中的别名容忍规则：shadcn ↔ shadcn/ui 等前缀别名视为命中。"""
    if target == library_norm:
        return True
    # 长度 >= 4 时才允许前缀别名，避免过短 token（如 ui、ant）误命中
    return len(target) >= 4 and len(library_norm) >= 4 and (
        library_norm.startswith(target) or target.startswith(library_norm)
    )


def official_references_for_ui_library(ui_library: str | None) -> list[dict]:
    """按 UI 库名返回命中的注册表条目（含 official_demo_url / official_docs_url）。

    支持复合名（如 'vant + uni-ui'）与别名（如 'shadcn' ↔ 'shadcn/ui'）。
    """
    if not ui_library:
        return []
    tokens = re.split(r"[\s,+/]+", str(ui_library).lower())
    targets = {_normalize_name(t) for t in tokens if t}
    if not targets:
        return []
    return [
        item for item in FRAMEWORK_CONSTRAINTS
        if any(_library_matches(target, _normalize_name(item.get("library", ""))) for target in targets)
    ]


def render_constraints_markdown(constraints: list[dict]) -> str:
    """将约束列表渲染为 DESIGN.md 用的 Markdown 片段。"""
    if not constraints:
        return "> 当前技术栈无额外框架约束；涉及 UI 库升级或组件更名时，先查官方迁移指南。"
    lines: list[str] = []
    for item in constraints:
        library = item.get("library", "")
        version = item.get("version", "")
        header = f"- **{library}**" + (f" `{version}`" if version else "")
        lines.append(header)
        demo = item.get("official_demo_url", "")
        docs = item.get("official_docs_url", "")
        lines.append(f"  - **官方 DEMO / 模板**: {demo or '待登记（framework_gate.py 补 official_demo_url）'}")
        if docs:
            lines.append(f"  - **官方文档**: {docs}")
        for note in item.get("notes", []):
            lines.append(f"  - {note}")
    return "\n".join(lines)


def render_official_demo_checklist(
    ui_library: str | None,
    *,
    official_paradigm: str | None = None,
    theme_entry: dict | None = None,
    starter_dirs: list[str] | None = None,
) -> str:
    """渲染「与官方 DEMO 对齐」验收清单（README.md 与 design-token-spec.md 共用）。

    参数来自生成中的 Blueprint：
    - official_paradigm：设计系统声明的官方安装范式摘要（缺失时标记为未对齐项）
    - theme_entry：主题令牌入口声明（framework / global_tokens / components / icon）
    - starter_dirs：本次生成的 starter 模板目录名列表
    任何新 UI 栈必须先登记 official_demo_url 才能输出「已对齐」状态。
    """
    refs = official_references_for_ui_library(ui_library)
    if not refs:
        return (
            "> 当前 UI 栈尚未登记官方 demo 链接：接入前先查官方 starter / quickstart / "
            "template 文档，并在 `framework_gate.py` 的 `FRAMEWORK_CONSTRAINTS` 登记 "
            "`official_demo_url` / `official_docs_url` 后再生成瘦 DEMO。"
        )
    lines = [
        "> 本项目的瘦 DEMO 按所选 UI 栈的**官方 starter / demo / template 最佳实践**初始化；"
        "下列链接与验收项用于持续核对，防止偏离官方推荐做法。",
        "",
    ]
    for item in refs:
        demo = item.get("official_demo_url", "")
        docs = item.get("official_docs_url", "")
        lines.append(
            f"- **{item.get('library', '')}** `{item.get('version', '')}`："
            f"官方 demo/模板 {demo or '待登记'} ｜ 官方文档 {docs or '待登记'}"
        )
    lines.extend(["", "| 对齐项 | 状态 | 说明 |", "|---|---|---|"])

    paradigm_ok = bool(official_paradigm)
    theme_ok = isinstance(theme_entry, dict) and bool(theme_entry)
    starter_ok = bool(starter_dirs)

    lines.append("| 官方 demo/starter 已登记 | ✅ | 见上表链接（`framework_gate.py` 注册表） |")
    lines.append(
        "| 官方安装范式已写入 DESIGN.md | "
        + ("✅" if paradigm_ok else "⚠️")
        + " | "
        + ("第 2 节「UI 库官方范式」" if paradigm_ok else "缺失 `official_paradigm`，接入前必须先补齐官方 quickstart 范式")
        + " |"
    )
    theme_note = "见 design-token-spec 第 3 节「技术栈主题入口」"
    if theme_ok and theme_entry.get("global_tokens"):
        theme_note = f"全局令牌入口 `{theme_entry.get('global_tokens')}`"
    lines.append(
        "| 主题令牌入口已声明 | "
        + ("✅" if theme_ok else "⚠️")
        + " | "
        + (theme_note if theme_ok else "缺失 `theme_entry`，需按官方 theming 文档补齐")
        + " |"
    )
    starter_note = "、".join(starter_dirs) if starter_ok else "该 Blueprint 未启用 starter（仅治理）"
    lines.append("| starter 目录已生成 | " + ("✅" if starter_ok else "—") + f" | {starter_note} |")
    lines.extend([
        "| `ui-stack-conformance` 门禁 | ⚠️ | 生成后可运行 `validate.py --dir <project>` 确认 passed |",
        "| 未对齐项 | " + ("无（按注册表逐项核对）" if paradigm_ok else "官方范式未登记") + " | 发现偏离时先修 starter，再继续业务开发 |",
        "",
    ])
    return "\n".join(lines)
