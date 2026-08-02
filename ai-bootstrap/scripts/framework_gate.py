#!/usr/bin/env python3
"""
AI Bootstrap — Framework Component Gate（框架组件门禁注册表）

单一事实源：生成器（generate.py）与校验器（validate.py）共用。

职责分层：
- DEPRECATED_COMPONENTS   → validate.py 扫描生成项目源码，拦截已废弃组件名的使用
- FRAMEWORK_CONSTRAINTS   → generate.py 将约束渲染进 DESIGN.md「框架约束」，作为治理记账

当新 Blueprint 的 ui_library 命中某技术栈（如 nuxt-ui / vant）时，自动生效。
"""

import re

# 已废弃 → 替代组件（扫描 .vue / .ts 源码中的组件使用；键为大小写敏感组件名）
DEPRECATED_COMPONENTS: dict[str, str] = {
    # Nuxt UI v3→v4：UFormGroup 已重命名为 UFormField。
    # v4 不再注册 UFormGroup，会导致 SSR 塌陷（表单字段整体消失）与 hydration mismatch。
    "UFormGroup": "UFormField",
}

# 渲染进 DESIGN.md「框架约束」的说明（按技术栈生效）
FRAMEWORK_CONSTRAINTS: list[dict] = [
    {
        "library": "@nuxt/ui",
        "version": "4.x",
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
]


def _normalize_name(name: str) -> str:
    """归一化库名（去掉 @ / - _ 空白等），使 'nuxt-ui' 与 '@nuxt/ui' 等价。"""
    return "".join(ch for ch in name.lower() if ch.isalnum())


def constraints_for_ui_library(ui_library: str | None) -> list[dict]:
    """按 UI 库名返回适用约束；支持复合名（如 'vant + uni-ui'）与未知库（返回空列表）。"""
    if not ui_library:
        return []
    tokens = re.split(r"[\s,+/]+", str(ui_library).lower())
    targets = {_normalize_name(t) for t in tokens if t}
    if not targets:
        return []
    return [
        item for item in FRAMEWORK_CONSTRAINTS
        if _normalize_name(item.get("library", "")) in targets
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
        for note in item.get("notes", []):
            lines.append(f"  - {note}")
    return "\n".join(lines)
