#!/usr/bin/env python3
"""
Scaffold project documentation governance structure.

Usage:
  python3 scaffold.py \\
    --dir /path/to/project \\
    --name "MyProject" \\
    --description "..." \\
    --type monorepo \\
    --apps '[...]' \\
    --primary "#00C8A1"
"""

import argparse, json, os, pathlib, sys

TOKEN_DEFAULTS = {
    'primary': '#00C8A1',
    'on_primary': '#ffffff',
    'secondary': '#041527',
    'on_secondary': '#ffffff',
    'background': '#f8fafb',
    'surface': '#ffffff',
    'outline': '#70787a',
    'text_main': '#191c1d',
    'text_muted': '#40484a',
}

PLATFORM_PATHS = {
    'trae': '.trae/skills',
    'codex': '.codex/skills',
    'cursor': '.cursor/skills',
}

TEMPLATE_DIR = pathlib.Path(__file__).parent.parent / 'templates'


def render_template(name, replacements):
    path = TEMPLATE_DIR / name
    content = path.read_text()
    for key, val in replacements.items():
        content = content.replace('{{' + key + '}}', str(val))
    return content


def build_color_table(tokens):
    rows = []
    for key in ['primary', 'on_primary', 'secondary', 'on_secondary',
                'background', 'surface', 'outline', 'text_main', 'text_muted']:
        label = key.replace('_', '-')
        rows.append(f"| `{label}` | `{tokens[key]}` | 核心品牌色 | 见 DESIGN.md |")
    return '\n'.join(rows)


def build_apps_rows(apps):
    rows = []
    for app in apps:
        d = app['dir']
        desc = app.get('desc', '')
        fw = app.get('framework', '')
        rows.append(f"| `apps/{d}/` | {desc} | {fw} | `docs/design/{d}-design.md` |")
    return '\n'.join(rows)


def build_dev_table(apps, ptype):
    if ptype == 'single' or len(apps) <= 1:
        return ''
    lines = ['', '### 开发命令', '', '| 命令 | 用途 |', '|------|------|', '| `pnpm dev` | 并行启动所有应用 |']
    for i, app in enumerate(apps):
        port = 3001 + i if app.get('framework') in ('nuxt', 'next') else 'TBD'
        lines.append(f"| `pnpm dev:{app['dir']}` | {app.get('desc', app['dir'])} (port {port}) |")
    return '\n'.join(lines)


def pick_template(app):
    fw = app.get('framework', '').lower()
    if fw in ('uni-app', 'uniapp', 'mobile'):
        return 'app-mobile.md'
    if fw in ('next', 'next.js', 'nextjs'):
        return 'app-next.md'
    return 'app-nuxt.md'


def gitignore_content(ptype):
    lines = [
        '# Dependencies',
        'node_modules/',
        '.pnpm-store/',
        '',
        '# Build output',
        'dist/',
        '.output/',
        '.nuxt/',
        '.next/',
        '',
        '# Environment',
        '.env',
        '.env.local',
        '.env.*.local',
        '',
        '# IDE',
        '.vscode/',
        '.idea/',
        '*.swp',
        '*.swo',
        '',
        '# OS',
        '.DS_Store',
        'Thumbs.db',
        '',
        '# Logs',
        '*.log',
        'logs/',
    ]
    if ptype == 'monorepo':
        lines.append('')
        lines.append('# Monorepo')
        lines.append('!packages/*/dist/')
        lines.append('!packages/*/.nuxt/')
    return '\n'.join(lines) + '\n'


def scaffold(args):
    dest = pathlib.Path(args.dir).resolve()
    tokens = dict(TOKEN_DEFAULTS)
    for k in ('primary', 'secondary', 'background', 'text_muted'):
        v = getattr(args, k, '')
        if v:
            tokens[k] = v

    apps = json.loads(args.apps) if isinstance(args.apps, str) else list(args.apps)
    is_mono = args.type == 'monorepo' or len(apps) > 1

    # Determine platform skills path
    platform_path = PLATFORM_PATHS.get(args.platform or '', '')
    if not platform_path:
        platform_path = args.platform if args.platform else '.trae/skills'

    # ---- Dry-run: just print what would be created ----
    if args.dry_run:
        print(f'[dry-run] Scaffold to {dest}')
        print(f'  type={args.type}  apps={len(apps)}  platform={platform_path}')
        print()
        print('  Directories:')
        dirs = ['docs/00-research', 'docs/01-requirements', 'docs/02-specs',
                'docs/03-plans', 'docs/04-reviews', 'docs/05-verification',
                'docs/06-decisions', 'docs/design']
        if is_mono:
            dirs += ['packages/design-tokens/src']
        for d in dirs:
            print(f'    {d}/')
        print()
        print('  Files:')
        print(f'    AGENTS.md')
        print(f'    docs/DESIGN.md')
        for app in apps:
            print(f"    docs/design/{app['dir']}-design.md")
        if is_mono:
            print(f'    packages/design-tokens/package.json')
            print(f'    packages/design-tokens/src/index.ts')
        print(f'    .gitignore')
        print(f'    README.md')
        return

    # ---- Actual scaffold ----
    dirs = ['docs/00-research', 'docs/01-requirements', 'docs/02-specs',
            'docs/03-plans', 'docs/04-reviews', 'docs/05-verification',
            'docs/06-decisions', 'docs/design']
    if is_mono:
        dirs += ['packages/design-tokens/src']
    for d in dirs:
        (dest / d).mkdir(parents=True, exist_ok=True)
        readme = dest / d / 'README.md'
        if not readme.exists():
            readme.write_text(f'# {dest.name}/{d.split("/")[-1]}\n\n')

    # Common replacements
    common = {
        'PROJECT_NAME': args.name or dest.name,
        'BRAND_DESCRIPTION': args.description or f'{args.name or dest.name} 品牌',
        'COLOR_TABLE': build_color_table(tokens),
        'APPS_ROWS': build_apps_rows(apps),
        'DEV_TABLE': build_dev_table(apps, args.type),
        'MONOREPO_RULES': '',
        'MONOREPO_NO_IMPORT': '',
        'TOKEN_PRIMARY': tokens['primary'],
        'TOKEN_SECONDARY': tokens['secondary'],
        'TOKEN_BACKGROUND': tokens['background'],
        'TOKEN_TEXT_MUTED': tokens['text_muted'],
        'PLATFORM_SKILLS_PATH': platform_path,
    }
    if is_mono:
        common['MONOREPO_RULES'] = (
            '## Monorepo 规则\n'
            '- 跨应用复用代码抽到 packages/ 目录\n'
            '- 框架无关代码抽到 packages/shared\n'
            '- 主题配置在 packages/design-tokens\n'
            '- 所有 workspace:* 引用\n'
        )
        common['MONOREPO_NO_IMPORT'] = '\n- 在应用目录之间直接互相 import（Monorepo 禁止）'

    # AGENTS.md
    content = render_template('AGENTS.md', common)
    (dest / 'AGENTS.md').write_text(content)
    print(f'  {dest}/AGENTS.md')

    # DESIGN.md
    content = render_template('DESIGN.md', common)
    (dest / 'docs/DESIGN.md').write_text(content)
    print(f'  {dest}/docs/DESIGN.md')

    # Per-app design docs
    for app in apps:
        repl = dict(common, APP_NAME=app['dir'], APP_DESCRIPTION=app.get('desc', ''))
        tmpl = pick_template(app)
        content = render_template(tmpl, repl)
        path = dest / 'docs' / 'design' / f"{app['dir']}-design.md"
        path.write_text(content)
        print(f'  {path}')

    # design-tokens skeleton
    if is_mono:
        pkg = dest / 'packages' / 'design-tokens'
        pkg_json = {
            'name': f'@{args.name or dest.name}/design-tokens',
            'version': '0.1.0', 'private': True, 'type': 'module',
            'exports': {
                '.': './src/index.ts',
                './tailwind': './src/tailwind.config.ts',
            }
        }
        (pkg / 'package.json').write_text(json.dumps(pkg_json, indent=2) + '\n')

        idx = f'''export const colors = {{
  primary: '{tokens["primary"]}',
  'on-primary': '{tokens["on_primary"]}',
  secondary: '{tokens["secondary"]}',
  'on-secondary': '{tokens["on_secondary"]}',
  background: '{tokens["background"]}',
  surface: '{tokens["surface"]}',
  outline: '{tokens["outline"]}',
  'text-main': '{tokens["text_main"]}',
  'text-muted': '{tokens["text_muted"]}',
}} as const;
'''
        (pkg / 'src' / 'index.ts').write_text(idx)
        print(f'  {pkg / "src/index.ts"}')

    # .gitignore
    (dest / '.gitignore').write_text(gitignore_content(args.type))
    print(f'  {dest}/.gitignore')

    # README
    name = args.name or dest.name
    tree_lines = [
        f'{name}/',
        '├── AGENTS.md',
    ]
    if is_mono:
        tree_lines += [
            '├── docs/',
            '│   ├── DESIGN.md',
            '│   ├── 00-06/',
            '│   └── design/',
            '├── .gitignore',
            '└── packages/',
            '    └── design-tokens/',
        ]
    else:
        tree_lines += [
            '├── docs/',
            '│   ├── DESIGN.md',
            '│   ├── 00-06/',
            '│   └── design/',
            '└── .gitignore',
        ]

    readme = [
        f'# {name}',
        '',
        args.description or '',
        '',
        '## 项目结构',
        '',
        '```',
    ] + tree_lines + ['```', '']

    (dest / 'README.md').write_text('\n'.join(readme))
    print(f'  {dest}/README.md')

    print(f'\nDone. {len(apps)} app(s) scaffolded at {dest}')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--dir', required=True)
    p.add_argument('--name', default='')
    p.add_argument('--description', default='')
    p.add_argument('--type', choices=['monorepo', 'single'], default='single')
    p.add_argument('--apps', required=True)
    p.add_argument('--primary', default='')
    p.add_argument('--secondary', default='')
    p.add_argument('--background', default='')
    p.add_argument('--text-muted', default='')
    p.add_argument('--platform', default='trae',
                    help='AI platform (trae/codex/cursor), controls AGENTS.md skill path')
    p.add_argument('--dry-run', action='store_true', help='Preview only, no writes')
    args = p.parse_args()

    if isinstance(args.apps, str):
        try:
            args.apps = json.loads(args.apps)
        except json.JSONDecodeError:
            sys.exit(f'Error: --apps must be valid JSON, got: {args.apps}')

    scaffold(args)
