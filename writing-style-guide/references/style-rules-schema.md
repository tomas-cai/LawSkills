# style-rules.json 字段说明

## 规则类型

- `hard_rules`：违反后必须返工，例如不得虚构事实、必须使用简体中文、标题不超过指定字数。
- `soft_preferences`：尽量遵循，例如多用短句、段落控制在 3–5 行。
- `open_questions`：缺少证据或用户选择，不能由下游 Skill 默默决定。

## 可执行性要求

每条规则尽量写成：

```json
{
  "id": "R01",
  "rule": "解释专业术语时先给一句白话定义，再给一个场景例子",
  "priority": "hard",
  "scope": "body",
  "check": "术语首次出现后的同段或下一段存在定义与例子",
  "evidence": ["sample-01:p3"]
}
```

避免只写“有温度”“高级”“有网感”等无法检查的词；应补充具体句式、节奏、视角、词汇或结构表现。

## 风格冲突处理

下游执行顺序：用户当次明确要求 > `hard_rules` > 平台约束 > `soft_preferences`。当两条硬规则冲突时停止静默决策，列入 `open_questions`。
