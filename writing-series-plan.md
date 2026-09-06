# 写作系列 Skill 方案

## 1. 产品定位

这是一套以“文件契约”协作的写作流水线。每个 Skill 只负责一个稳定环节，前后环节通过 Markdown/JSON 产物衔接，因此可以只调用其中一个，也可以串成完整流程。

## 2. Skill 清单

| 顺序 | Skill | 核心职责 | 主要产物 |
|---:|---|---|---|
| 1 | `writing-style-guide` | 从样文和描述提炼可执行风格 | `style-guide.md`、`style-rules.json` |
| 2 | `writing-content-analyzer` | 建立事实、观点、原话和证据底座 | `content-analysis.md`、`content-analysis.json` |
| 3 | `writing-outline-generator` | 把素材变成可施工的大纲 | `outline.md` |
| 4 | `writing-writer` | 按大纲、素材、风格写初稿 | `draft.md`、`draft-meta.json` |
| 5 | `writing-proofreader` | 先质检，再在边界内润色 | `proofread-report.md`、`revised-draft.md` |
| 6 | `writing-article-illustrator` | 设计配图、图片提示词和视觉素材 | `image-brief.md`、`images/` |
| 7 | `writing-platform-layout` | 按平台重新组织内容、视觉层级和移动端阅读体验 | `platform-layout.md`、`layout-manifest.json`、平台版 HTML/富文本 |

## 3. 推荐文件链

```text
写作项目/
├── style-guide.md              ← writing-style-guide
├── style-rules.json             ← writing-style-guide
├── source/                      ← 原始文章、访谈、会议记录等
├── content-analysis.md          ← writing-content-analyzer
├── content-analysis.json       ← writing-content-analyzer
├── outline.md                   ← writing-outline-generator
├── draft.md                     ← writing-writer
├── draft-meta.json              ← writing-writer
├── proofread-report.md          ← writing-proofreader
├── revised-draft.md             ← writing-proofreader
├── image-brief.md               ← writing-article-illustrator
├── images/                      ← 已确认的图片
├── platform-layout.md           ← writing-platform-layout
├── layout-manifest.json         ← writing-platform-layout
└── article.html                 ← 平台化排版成品，按需生成
```

不强制每次完整跑完。最小可用流程是：`content-analyzer → writer`；质量稳定后加入 `style-guide → outline-generator → proofreader`；需要图文发布时执行 `article-illustrator → platform-layout`。

## 4. 共性工程规则

### 六格需求卡

每个 Skill 开始前先明确：问题、场景、输入、输出、规则、禁止。信息不足时采用最小假设并标记待确认，不把猜测写进正式事实。

### 输入检查与人工确认

- 先检查文件类型、可读性、长度、来源和敏感信息。
- 在素材冲突、标题承诺、原话使用、批量生成图片和最终发布前设置人工确认点。
- 任何 Skill 都不把“没有生成”伪装成“已生成”，不把“未核实”伪装成“已证实”。

### 产物契约

- Markdown 负责解释、审阅和协作。
- JSON 负责被下游 Skill 稳定加载。
- 证据 ID、图片 ID、问题 ID 保持稳定，便于追踪和返工。

### 返工路径

```text
素材冲突/缺证据 → content-analyzer
主旨或顺序不成立 → outline-generator
正文缺失/偏题/事实越界 → writer
表达问题 → proofreader
配图内容问题 → article-illustrator
版式拥挤、移动端不可读、美观度不足或平台阅读习惯不匹配 → platform-layout
```

## 5. 三个平台扩展

平台差异由 `writing-platform-layout` 的参考文件维护，视觉素材仍由 `writing-article-illustrator/EXTEND.md` 提供补充配置，通用 Skill 不被平台细节污染：

- 小红书：3:4/1:1、一个画面一个重点、手机缩略图可读。
- 微信公众号：移动端单列、兼容富文本、按需内嵌图片。
- 今日头条：信息流首屏、标题与正文承诺一致、避免诱导点击并兼顾自然 SEO。

后续可以在用户项目目录创建 `EXTEND.local.md` 覆盖品牌色、固定尺寸和素材路径；不要把 API 密钥放入 Skill 或文章产物。

## 6. 分阶段实施建议

### 第一阶段：最小可用版

先用 `writing-content-analyzer + writing-writer` 跑通一篇真实文章，观察事实准确度、结构完成度和人工返工量。

### 第二阶段：质量稳定版

加入 `writing-style-guide + writing-outline-generator + writing-proofreader`，建立个人风格文件与证据追踪，降低每篇文章的重复沟通。

### 第三阶段：平台阅读体验版

加入 `writing-article-illustrator + writing-platform-layout`，按平台完成图片清单、内容层级、移动端阅读节奏、视觉令牌、alt 文本、版权记录和平台版 HTML/富文本。美观度与可读性必须经过渲染预览和三轮阅读检查。

### 第四阶段：评测与迭代

用 3 类真实任务回测：知识型文章、访谈/案例型文章、平台短内容。每轮记录：事实错误数、结构返工数、语言修改数、图片返工数、人工确认耗时，再调整对应 Skill 的规则，而不是把所有问题堆进 writer。

## 7. 验收标准

- 七个目录均有合法 `SKILL.md` 和 `agents/openai.yaml`。
- 每个 Skill 都声明输入、输出、边界、质量门禁和下游协作方式。
- 产物可以从一个环节交给下一个环节，不依赖隐藏上下文。
- 事实、原话、数字、图片来源和修改意见都有可追踪标记。
- 平台差异通过扩展文件维护，通用流程不因平台分叉。
