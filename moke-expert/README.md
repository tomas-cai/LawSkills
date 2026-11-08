# 磨课 · WorkBuddy 专家包（moke-expert）

「磨课」是一位**培训项目与磨课专家**（Agent 型），把整个培训项目当产品打磨：先定几天、几天实战、客户哪天到场（L2 项目架构），再设计每门课的模块（L3 课程设计）与每一节课的分钟轴（L4/L5 磨课）。

它在四个角色之间**按阶段切换**——课程体系架构师（L1）/ 项目设计师（L2）/ 课程设计师（L3）/ 讲师·磨课师（L4-L5），每个角色判据独立、不互相顶替。能力矩阵见 `skills/course-design/references/roles-and-stages.md`。

- 专家名（中文 / 英文）：磨课 / Moke
- 类型：`agent`（单个专家 + 6 个内置技能，覆盖 L2 项目 / L3 课程 / L4-L5 课次课堂）
- 行业分类：`09-OperationsHR`（运营人力 · 含培训）
- 版本：**1.10.0**（成品双视角契约 / 标题契约 / 术语与口径一致性 / 默认 HTML 课件载体 / 工具卡五点闭环 / 阶段归属矩阵 / 结构模式选型 / L0-L6 层级与术语契约 / **角色×阶段能力矩阵 + L2 项目架构独立成技能**，详见 `CHANGELOG.md`）
- 规范依据：<https://open.workbuddy.cn/docs/expert>、<https://open.workbuddy.cn/docs/skill>

## 目录结构

```text
moke-expert/
├── .codebuddy-plugin/
│   └── plugin.json              # 专家核心配置（必需）
├── agents/
│   └── moke-course-architect.md # 主 Agent 定义（系统提示词 + 技能路由）
├── avatars/
│   └── expert.png               # 512×512 PNG，393 KB
├── skills/
│   ├── course-discovery/                    # P00 培训需求发现（项目设计师）
│   ├── program-design/                      # P02a 培训项目架构 · L2（项目设计师）
│   ├── course-design/                       # P01-P05 课程开发主流程 · L3（课程设计师，10 份 references）
│   ├── course-practice-project-evaluator/   # 实战项目立项门禁（可选）
│   ├── course-polish/                       # 讲师话术与体验润色
│   └── course-review/                       # 交付前质量评审
├── CHANGELOG.md                 # 专家包整体版本变更记录
└── README.md
```

## 6 个技能与角色分工

| 技能 | 触发场景 | 产出物 | 流程位置 |
|:---|:---|:---|:---|
| `course-discovery` | 探索做什么课、评估培训方向 | `00-培训需求spec.md` | P00（可选）· 项目设计师 |
| **`program-design`** | **排几天、实战占几天、客户哪天到场、怎么转化与评估** | **培训项目架构方案（三张卡 + 天级排期 + 6Ds + 评估设计）** | **P02a · 项目设计师（L2）** |
| `course-design` | 开发课程、写目标/大纲/手册/测评 | `01`~`05` + `03-教学材料包/` | P01-P05 主流程 · 课程设计师（L3） |
| `course-practice-project-evaluator` | 判断 AI 类实战项目能否立项 | `实操项目立项评估.md` | Phase 02/03 之间（可选门禁） |
| `course-polish` | 润色话术、节奏、互动、应急 | `02-讲师手册·润色版.md` | **P03 完成条件之一（按课时必做）** · 磨课师 |
| `course-review` | 交付前质量把关（**维度 10 按四角色分别评审**） | 课程质量评审报告 + `QUALITY-REVIEW.md` | 交付前 · 四角色各自独立结论 |

**技能版本映射（包版本 ≠ 技能版本；本表为唯一对照口径）**

| 技能 | 技能版本 | 覆盖到的缺陷代际 | 1.10.0 本轮 |
|:---|:---:|:---|:---:|
| `course-discovery` | 1.0.0 | 需求发现基线（G 序列之前） | 未改 |
| `program-design` | 1.0.0 | G-16 / G-17 / G-18（L2 项目架构） | 未改 |
| `course-design` | **1.10.0** | G-1~G-20（主流程 + 全部硬规则） | 升版 |
| `course-practice-project-evaluator` | 1.0.0 | 立项门禁（独立于 G 序列） | 未改 |
| `course-polish` | 1.5.0 | G-4 / G-5 / G-10~G-12 | 未改 |
| `course-review` | **1.6.0** | G-1~G-22（新增维度 10 四角色判据） | 升版 |

**质量档案**：`QUALITY-REVIEW.md`（1.9.0 整改前评审结论 + 1.10.0 整改后复核证据）。
**已知边界**：L1 体系架构师目前只有角色定义与能力项，**无对应技能**；需要「初中高 + 认证」时须另建 `curriculum-map`，本包不假装能做。

```text
course-discovery → **program-design(02a)** → course-design(02b-05) → [立项评估] → course-polish（完成条件之一） → [course-review 维度 10]

体验层分两个粒度：`course-design` Phase 02 的情绪曲线／旅程地图是**设计约束，不上屏**；`course-polish` 按课时把它兑现为可验收的课堂动作。三条硬规则见 `CHANGELOG.md` 与各技能文件内 Changelog。

**1.2.0 新增三条硬规则**：① 规范变更后须按 10 词表做**全包回归检索**（`common-tools.md`），禁止只改被举证页；② 交付评审先判**适用课程类型 A/B/C**，B/C 类用等价判据、A 类技术项标 N/A；③ 润色版**自检结论须声明作用域**，全包结论只引用 `course-review` 维度 9。对应闭合实战暴露的 G-1 / G-2 / G-3。

**1.10.0 新增一条硬规则**：⑨ **评审按四角色分化，规范升级须同步评审判据** —— 交付前评审须按 `course-review` 维度 10 分别给「项目架构 / 课程设计 / 课堂落地 / 体系适配」四层独立结论；⛔ 一套通用判据评到底 = 视角没切换（V-7）；⛔ 规范层每升一代，评审技能须同步补判据并复测概念命中（`规范写了 ≠ 评审查得出`，G-21）；⛔ 职业名以 `plugin.json` 的 `profession` 为唯一真源，其余位置逐字一致。对应闭合 G-21 / G-22。

**1.9.0 新增一条硬规则**：⑧ **角色随阶段切换，判据不得互相顶替** —— 每进入一个阶段先答「本阶段主责哪个角色（体系架构师 L1 / 项目设计师 L2 / 课程设计师 L3 / 磨课师 L4-L5）+ 此刻用哪两项核心技能」。⛔「排期合理」推不出「课程设计合理」；⛔ 同一阶段不得两个角色同时主责（P03 例外，冲突时以「能不能讲完」删内容、不得延长课时）；⛔ 角色切换须留 4 行交接单，不得靠对话记忆；⛔ **P02 必须拆 P02a（L2 项目架构，`program-design`）与 P02b（L3 课程设计，`course-design`），且 a 在 b 之前**；⛔ S 档（≤2 天、无客户现场、无答辩）不跑全矩阵。`角色齐备 ≠ 视角真切换`（V-7）。见 `skills/course-design/references/roles-and-stages.md`。

**1.8.0 新增一条硬规则**：⑦ **层级先对齐再谈结构** —— L1 课程体系（多门课进阶路径）/ L2 培训项目（一次干预的完整体验）/ L3 课程（一门课的模块）/ L4 课次（一次课的分钟轴）/ L5 课堂（分钟级活动）/ L6 载体。⛔ 结构类文档标题必须带层级标签；⛔ 一章内不得混用两层方法（6Ds 不与 Gagné 同节）；⛔「课程体系」仅在有 ≥3 门课且有进阶关系时使用；⛔ 禁止造「培训项目课程体系」这类跨层词。`术语对 ≠ 层级对`。见 `skills/course-design/references/structure-levels.md`。

**1.7.0 新增一条硬规则**：⑥ **结构模式须显式选型并给依据** —— ≥2 天、或 ≥3 阶段、或含真实项目 / 客户现场 / 结业答辩的项目，定稿前必须落**三张前置卡**（出口绩效 / 任务清单 / 学员起点），并写明所选结构模式（P1 阶段块状 / P2 整体任务螺旋 / P3 案例阶梯 / P4 项目主线 / P5 混合旅程）**及判别矩阵里定案的那一问**。⛔ 缺卡或写不出依据 → 只能标「**假设版结构**」，不得宣称最佳实践；⛔ 学员首次见到完整链路不得晚于倒数第二个单元（否则触「全案后置」，须加回接）；⛔ 把商业约束下的妥协包装成最佳实践同样不合格。见 `skills/course-design/references/program-structure.md`。

**1.6.0 新增一条硬规则**：⑤ **课名即结构，单元不得跨阶段** —— 把课程名按 `·` 拆成阶段清单，每个授课单元（天 / 课次 / 半天）只标称一个阶段，单元内不得出现其他阶段的活动；排期定稿前须产出「活动 → 模块 → 阶段」三列归属矩阵，**跨阶段行须为 0**。⛔ **分钟合计相等 ≠ 分段归属正确**；新增单元必答三问（练哪个阶段 / 前面做过几次 / 第三遍的增量是什么），答不出增量即为「伪新增」；⛔ 时长不得默认均分，须给依据。对应闭合 G-14 / G-15。

**1.5.0 新增一条硬规则**：④ **每件工具卡必须走完五点闭环** —— 定义（`01` 组件表）→ 发放（`02` 时间轴写明发什么、每人几张）→ 上屏可数（宣称「N 问 / N 步 / N 张」必须逐条编号且计数相等，⛔ 不许压成分号串）→ 对手戏（`03` 角色卡对练习所涉每个问题有答法）→ 实物（宣称「附录有卡」就必须真有，悬空落点判 P0，讲师兜底语同样受检）。对应闭合 G-10 / G-11 / G-12。

**1.4.0 新增三条硬规则**：① **默认输出 HTML 课件** —— `05-课程课件/` 默认 `{课次}-{主题}-讲课版.html`（单文件零外链），**只有用户明确说 PPTX / ppt / 幻灯片时才产出 PPTX**；同一课次只允许 1 个可授课载体，多载体并存须有 `00-课件状态说明.md` 并给旧载体标 ⛔；② **同一件东西只有一种叫法、一处时长** —— 组件名 / 表头 / 验收口径与 `01` `04` 逐字一致，白话须有绑定句，同页禁止两种叫法；页内步骤时长合计必须等于页时长并对齐讲师手册分钟轴；③ **改一个载体不算改完** —— 内容变更须对同课次全部载体（含旧 PPTX / 旧 HTML）做口径回归。对应闭合 G-6 / G-7 / G-8 / G-9。

**1.3.0 新增三条硬规则**：① **成品只允许学员视角与讲师视角** —— 上屏正文须「学员能照着读、照着做」，逐页讲解层须「讲师能照着讲」；设计 / 制作视图只是内部中间件，课件生成前须先产出「逐页双视角文案表」并经用户确认；② **面向学员的标题不能是简单词语** —— 禁内部代号 / 制作元数据 / 「切换 ·」指令 / 名词标签，**去剧透 ≠ 压成标签词**；③ **验收不得只跑负向词表** —— 须同时给「正向内容验收 7 项结构判据」分布，缺正向分布不得给维度 9 评分。对应闭合 G-4 / G-5。
```

产出物编号是跨技能接口契约，详见 `agents/moke-course-architect.md` 的「产出物契约」章节。

## 发布步骤（开放平台）

1. 确认 `plugin.json` 中的展示信息（见下方「发布前建议核对」）
2. 打包：`python3 /Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/expert-manager/scripts/package_expert.py <moke-expert 目录> <输出目录>`
   > ⚠️ **输出目录必须在源目录之外**（如 `marketplaces/my-experts/dist/`）。把输出目录建在专家包内部会让脚本把正在生成的 zip 再打进 zip，产生数 GB 文件并被系统 kill（2026-11-08 实测踩坑）。
3. 生成 `moke-expert.zip`，其根目录为 `moke-expert/`（压缩包内须直接包含 `.codebuddy-plugin/plugin.json`）
4. 前往开放平台创建专家，提交 zip；若解析失败，优先检查基础结构与 `plugin.json` 字段
5. 头像为 PNG / 512×512 / ≤500KB，可自行替换 `avatars/expert.png`

本机预览已安装到 `~/.workbuddy/plugins/marketplaces/my-experts/plugins/moke-expert`，并注册进 `marketplace.json`；在 WorkBuddy 客户端【专家 → 我的专家】即可召唤。

## 发布前建议核对

| 项 | 当前值 | 说明 |
|:---|:---|:---|
| `author.email` | `moke@example.com` | 占位邮箱，发布前请替换为真实邮箱 |
| `displayName` | 磨课 / Moke | 花名，可改；`name` / `agentName` / 目录名 / Agent MD 文件名**不可改**，改了需重新创建专家 |
| `categoryId` | `09-OperationsHR` | 若面向开放平台新版分类，也可改为 `15-Education`（含课程设计）；本地旧版校验脚本只认 12 类，改后本地校验会误报 |
| `tags` / `quickPrompts` | 各 3 条 | 固定 3 条；`defaultInitPrompt` 必须与 `quickPrompts[0]` 一致 |
| `displayDescription.zh` | 50 字 | 规范要求 40-50 字 |
| 头像 | `avatars/expert.png` | 右下角带「AI 生成」水印，如需去除请手动替换同规格图片 |

## 与参考模板 design-experts 的差异

参考模板用于理解结构，但其中几处与官方规范不一致，本包已按官方规范修正：

| 项 | 模板 | 本包 |
|:---|:---|:---|
| `categoryId` | `01-Design`（非规范 ID） | `09-OperationsHR` |
| Agent MD frontmatter | 声明了 `tools` | 不声明（工具权限由系统统一分配） |
| `displayName` 双语 | en/zh 内容错位 | en=Moke、zh=磨课 |
| `defaultInitPrompt` 与 `quickPrompts[0]` | 不一致 | 完全一致 |
| `plugin.json` 的 `skills` | 未声明 | 声明 5 个技能目录路径 |
| SKILL.md frontmatter | 自定义字段 | 按技能规范补齐 `display_name` / `display_name_en` / `description_zh` / `description_en` / `examples_zh` / `examples_en` / `version` / `author` |
| `agents/` 与 `skills/` 位置 | 根目录 | 根目录（与规范一致） |

## 本次「理顺」做了什么

1. 把 5 个技能从 `course-design/` 平铺目录搬进标准的 `skills/` 结构，原目录完整保留、未做任何删除
2. 合并各技能里的 `agents/openai.yaml`（OpenAI 界面元数据）信息到 SKILL.md frontmatter，专家包不再携带该文件
3. 统一 `03-教学材料包/` 的编号契约：`00` 大纲 / `01` 学员手册 / `02` 讲师手册 / `03` 实操案例 / `04` 测评方案 / `05` 课件 / `06` 详细大纲，并同步修正 `course-polish`、`course-review` 与 `phase-03-development.md` 中的引用
4. 补上 `phase-00-discovery.md` 的参考索引；把 `course-review` 的维度 6/7/8 明确为「按需启用的扩展检查」（**1.1.0 另增维度 9「学习体验落地」，已产出材料包时必做**）
5. 清理对未随包提供的 `microcourse-*` 微课技能的悬空调用，改为「待补 / 预留扩展位」，避免运行时调用不存在的技能
6. 补齐专家级配置、主 Agent 路由与 SOP、头像、README

## 已知边界

- 不含微课技能；`06-微课补充包/` 仅为预留扩展位，v1.3 仍不自动生成
- 原 `course-design/ai-engineering-governance-series.md` 属于另一套 AI 工程治理技能体系，与课程设计无关，未纳入本专家包（原文件仍保留在源目录）
- `course-practice-project-evaluator` 正文沿用原有英文专业表述，仅补齐中文展示元数据与中文路由说明
