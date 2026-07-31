# AI Bootstrap Blueprint Guide

## 最小规范

每个 Blueprint 使用一个 YAML 文件，至少包含：

```yaml
id: unique-id
name: Human Readable Name
version: 1.0.0
description: Short description
tags: [language, framework]

stack:
  frontend:
    framework: none
    language: none
  backend:
    framework: required-framework
    language: required-language
  database:
    primary: postgres
    version: "16"

architecture:
  style: layered
  pattern: modular-monolith
```

## 约束

- 使用语义化版本号。
- 数据库使用 `stack.database.primary` 表示主数据库，版本放在 `stack.database.version` 或主数据库对象中。
- 所有值必须能被 AI Bootstrap 的依赖无关 YAML 子集解析。
- 新 Blueprint 至少需要一个生成与验证回归测试。
- 不要在 Blueprint 中放入凭据、环境变量值或不可移植的绝对路径。

## 验证

```bash
python3 scripts/generate.py --dir /tmp/example --blueprint <id> --dry-run
python3 scripts/validate.py --dir /tmp/example
```
