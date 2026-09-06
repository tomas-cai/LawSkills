# 课程开发系列 Skill 体系

## 系列定位

把课程当作产品开发：从培训机会发现，到课程设计、教学材料润色，再到交付前质量评审。

## Skill 组成

| 顺序 | Skill | 职责 | 主要产物 |
|---:|---|---|---|
| 1 | `course-discovery` | 发现培训需求、聚类痛点、形成课程假设 | `00-培训需求spec.md` |
| 2 | `course-design` | 完成需求分析、课程设计、教学材料、实施和评估 | `01~05` 阶段产物 |
| 3 | `course-practice-project-evaluator` | 评估 AI 软件开发课程实践项目是否值得立项、可完成、可展示 | `实操项目立项评估.md` |
| 4 | `course-polish` | 按课时润色讲师话术、节奏、互动和应急标注 | 润色版讲师手册/课件备注 |
| 5 | `course-review` | 评审结构、一致性、深度、可教性和风险 | 课程评审报告 |

## 推荐协作流程

实践项目评估不是整个课程生命周期的第一步，而是实践项目进入教学材料开发前的立项闸门。根据课程是“课程先行”还是“项目先行”，有两种入口。

### 路径 A：课程先行（默认）

```text
course-discovery
        ↓ 00-培训需求spec.md
course-design
        ↓ 明确课程目标、学员水平和项目候选
course-practice-project-evaluator
        ↓ 实操项目立项评估.md
03-教学材料包/
        ↓ 实操案例、学员手册、讲师手册与测评方案
course-polish
        ↓ 逐课时润色备注与讲师手册增补
course-review
        ↓ 交付前质量评审与迭代清单
```

### 路径 B：项目先行（项目驱动课程）

当课程本身围绕一个 AI 软件项目展开时，可以先验证项目，再用通过评估的项目反向约束课程设计：

```text
course-discovery
        ↓ 目标人群、课程机会和项目候选
course-practice-project-evaluator
        ↓ 立项通过
course-design
        ↓ 将项目嵌入学习目标、教学活动和测评
03-教学材料包/
        ↓
course-polish → course-review
```

无论哪条路径，`course-practice-project-evaluator` 都必须发生在 `03-教学材料包/` 正式开发之前。`course-review` 可以独立评审已有课程项目；`course-polish` 同样可以从已有讲师手册、大纲和 PPT 中间切入。

## 课程设计阶段产物

```text
<course-project-root>/
├── 00-培训需求spec.md
├── 01-需求定位报告.md
├── 02-课程设计方案.md
├── 实操项目立项评估.md       ← course-practice-project-evaluator（项目进入材料开发前）
├── 03-教学材料包/
│   ├── 00-课程大纲.md
│   ├── 01-学员手册.md
│   ├── 02-讲师手册.md
│   ├── 03-实操案例.md
│   ├── 04-测评方案.md
│   └── 05-课程课件/
├── 04-实施记录与反馈.md
└── 05-评估报告与迭代计划.md
```

## `course-polish` 的位置

`course-polish` 不改课程目标、知识点和教学内容，只优化学习体验，因此放在 `course-design` 产出教学材料之后、`course-review` 最终评审之前。

它按单个课时读取三类输入：

- `00-课程大纲.md`：检查课时叙事弧和目标对齐；
- `02-讲师手册.md`：润色讲师话术、转场和互动；
- `05-课程课件/课X-主题.pptx`：检查视觉叙事和临场节奏。

润色版不覆盖原版，必须保留原始教学材料，并在产物中记录 Changelog。

## 入口选择

| 用户需求 | 入口 |
|---|---|
| 不知道做什么课程 | `course-discovery` |
| 已有方向，要开发课程 | `course-design` |
| 想判断 AI 软件开发实战项目是否适合立项 | `course-practice-project-evaluator` |
| 已有讲师手册，想提升课堂表现 | `course-polish` |
| 想检查课程是否能交付 | `course-review` |
| 已有中间产物 | 根据已存在的阶段文件切入对应 Skill |

## 质量边界

- 发现阶段解决“做什么、为谁做、为什么值得做”。
- 设计阶段解决“学什么、如何学、如何评估”，并形成实践项目候选。
- 项目评估阶段解决“实践项目是否值得做、能否完成、如何展示、是否匹配课程目标”。
- 润色阶段解决“怎么讲得更有体验”。
- 评审阶段解决“是否完整、可信、可教、可交付”。
- 不把课件润色当成课程重构，不把评审意见直接当成未经确认的内容修改。

## 微课补充系列（可选扩展）

面授/直播主课开发完成课程设计或教学材料后，如果存在课前基础缺口、重复解释、工具操作复习、课后巩固或岗位迁移需求，可以转入独立的 `microcourse-*` 系列。

| 微课 Skill | 职责 | 产物 |
|---|---|---|
| `microcourse-planner` | 识别候选、筛选价值、安排课前/课后位置 | `06-微课补充包/00-微课补充地图.md` |
| `microcourse-designer` | 设计单一目标、主动行为、反馈和迁移 | `01-微课单元设计/` |
| `microcourse-scriptwriter` | 编写口播、分镜、录屏步骤和字幕 | `02-微课脚本与分镜/` |
| `microcourse-producer` | 组织媒体、课件、练习和交付资源包 | `03-微课交付包/` |
| `microcourse-reviewer` | 评审互补性、教学质量、体验和风险 | `05-微课评审报告.md` |

微课不是 `course-design` 的必经阶段，也不应把直播课按章节平均切成短视频。完整规则见 [`microcourse-development-series.md`](microcourse-development-series.md)。

### 主课与微课接口

```text
course-design（面授/直播主课 01~05）
        ↓ 可选
microcourse-planner → microcourse-designer
        → microcourse-scriptwriter → microcourse-producer
        → microcourse-reviewer
        ↓
06-微课补充包/
```

每个微课必须记录 `MC-ID`、来源课时、来源目标、主课版本和微课状态。主课变更时，先检查微课补充地图的影响关系。
