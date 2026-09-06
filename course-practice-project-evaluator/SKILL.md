---
name: course-practice-project-evaluator
description: >-
  评估 AI 软件开发类课程中的实践项目是否值得立项、适合目标学员、能够在课程周期内完成，并能训练真实的产品、AI、工程交付和评测能力。用于课程设计前筛选项目候选、已有课程补充实战项目、比较多个项目方案、判断项目所需素材与 Demo 层级，以及把通过评估的项目输入 course-design；也适用于 AI 产品经理、AI 应用开发和 Vibe Coding 课程的实践项目评估。
---

# AI 软件开发课程实践项目立项评估

## Overview

Use this skill to evaluate an AI software development practice project before adding it to a course, bootcamp, portfolio program, or project library. Focus on four questions:

1. Can the target learner realistically complete the project with available time, tools, materials, and technical prerequisites?
2. Does the project train meaningful AI software development judgment rather than generic prompting or UI imitation?
3. Can the finished project produce credible course evidence, a demo, and a portfolio artifact?
4. Does the project fit the course objectives, difficulty, teaching sequence, and assessment plan?

Default target audience: students, early-career developers, product managers, career switchers, and learners with limited real project experience.

## Inputs To Look For

When evaluating a project, gather what is available from the user's prompt or local files:

- project name and one-sentence brief
- course name, phase, learning objectives, and target learner level
- target user and scenario
- expected learner profile
- available source materials or data
- expected deliverables
- demo, prototype, screenshot, recording, portfolio page, or runnable site expectations
- time budget
- tool or technical assumptions
- evaluation rubric, if one already exists
- prerequisite knowledge, team size, and whether the project is individual or collaborative

If evaluating a project directory, read `project.md` first. If present, also read `materials/`, `templates/`, `examples/`, or overview files only when needed to judge feasibility.

## Evaluation Workflow

### Step 1: Restate The Project And Course Fit

Summarize the project in one compact sentence:

> For [target learner] in [course context], solve [target user pain point] by building [AI product/workflow], and evaluate learning success through [project evidence and metrics].

Also state which course objective(s) the project trains and which objective(s) it does not cover. If the project cannot be restated in this structure, flag it as underdefined.

### Step 2: Score Feasibility

Score each dimension from 1 to 5. Convert weighted score to 100.

| Dimension | Weight | What To Check |
|---|---:|---|
| Learner fit | 20% | Can the target learners understand the domain and complete the work without excessive prerequisites? |
| Time control | 15% | Can a complete version be finished in 1-3 weeks? |
| Material availability | 15% | Are inputs available, such as JD, FAQ, documents, sample data, user cases, competitor examples, or output samples? |
| AI/software execution feasibility | 15% | Can learners complete the core AI workflow with accessible tools, without unjustified model training or infrastructure complexity? |
| Course capability value | 20% | Does the project train product framing, AI workflow design, implementation judgment, evaluation, and delivery rather than only prompt writing or UI imitation? |
| Portfolio and demo value | 15% | Can the result become a credible course artifact, resume/portfolio/interview asset, and visible demo? |

Score bands:

| Score | Judgment | Action |
|---:|---|---|
| 85-100 | Strong flagship project | Prioritize building full materials, templates, and reference output |
| 75-84 | Usable project | Keep in project pool, but patch the weakest dimensions |
| 60-74 | Backup project | Use only after simplifying scope or adding materials |
| < 60 | Not recommended | Redesign or reject |

Flagship constraint: do not label a project "Strong flagship project" unless it has at least an L1 visible portfolio surface and a clear course assessment artifact. Prefer L2 for flagship projects and use L3 only when the implementation scope is teachable and the demo materially improves learning or portfolio value.

### Step 3: Check AI Software Development Authenticity

Flag whether the project contains meaningful AI software development work:

- AI capability fit: why AI is needed instead of a normal rules-based workflow
- input and context design: what data, knowledge, constraints, permissions, and tools the AI needs
- output and interaction design: expected format, quality bar, user action, and failure states
- implementation path: prompt, structured output, RAG, tool calling, Agent workflow, API, or lightweight application
- evaluation: how to judge good vs bad AI output with a test set or rubric
- risk control: hallucination, privacy, bias, compliance, overclaiming, or unsafe automation
- human-in-the-loop: when the user, operator, expert, or reviewer must intervene
- iteration loop: how feedback improves prompt, knowledge base, workflow, code, or product experience

A project with fewer than 5 of these elements is likely too thin for an AI software development course project.

### Step 4: Map Course And Portfolio Capabilities

Identify what completing the project proves about the practitioner. Use this capability map:

| Capability | Evidence In Learner Output |
|---|---|
| Problem framing | Clear target user, scenario, pain point, and success definition |
| User research | Persona, journey map, pain point evidence, interview summary, or behavior analysis |
| Product and technical judgment | Prioritization, tradeoff reasoning, MVP scope, non-goals, and architecture choices |
| AI capability understanding | Prompt/RAG/Agent workflow, model boundaries, input-output constraints |
| Software delivery | Working prototype, API integration, data flow, error handling, versioned project files, or deployment evidence |
| Interaction design | User flow, prototype, information architecture, exception states |
| Evaluation literacy | Metrics, test set, scoring rubric, Bad Case analysis |
| Business thinking | Connection to efficiency, conversion, retention, cost, quality, or risk |
| Risk and ethics | Privacy, hallucination, fairness, misuse prevention, human review |
| Communication | PRD, structured report, decision memo, technical explanation, demo, or 5-minute pitch |
| Portfolio packaging | Demo link, portfolio page, screenshots, recording, or runnable prototype that a recruiter can understand quickly |

Prefer concrete evidence over vague labels. For example, say "demonstrates evaluation literacy through a 20-case test set and Bad Case taxonomy" instead of "shows AI thinking."

### Step 5: Check Portfolio Surface

Evaluate whether the project has a visible outer layer for low-context viewers such as HR screeners, recruiters, or first-round interview coordinators.

Core rule:

> Every flagship practice project must have a shallowly understandable portfolio surface; otherwise strong methodology may be invisible during screening.

Use three levels:

| Level | Surface | Minimum Evidence |
|---|---|---|
| L1 Display demo | Figma prototype, screenshots, portfolio page, or short recording | A viewer can understand the product, target user, and core value in 30 seconds |
| L2 Interactive demo | Coze, Dify, GPTs, Notion, spreadsheet workflow, or clickable prototype that runs the core flow | A viewer can input or inspect sample data and see representative output |
| L3 Runnable demo site | Lightweight web app or deployed prototype | A viewer can complete the main task flow end to end |

Recommended standard:

- All projects: require at least L1.
- Flagship projects: require L2 whenever the project has clear input-output logic.
- Select showcase projects: build L3 when the task flow is simple enough and the demo adds strong recruiting value.

Do not let the demo replace product thinking. The surface layer is for first-glance comprehension; the deeper artifacts still prove PM judgment.

### Step 6: Diagnose Weaknesses

For every score below 4, explain the blocking issue and give a targeted fix. Also state whether the fix belongs in the course objective, project brief, material pack, technical starter, or assessment rubric.

Common fixes:

- If learner fit is weak: add background primer, glossary, sample case, technical starter, or reduce domain complexity
- If time control is weak: narrow to one user role, one core workflow, and one deliverable
- If materials are weak: provide sample data pack, mock cases, source documents, or competitor screenshots
- If AI/software execution is weak: replace model training with prompt workflow, RAG design, prototype, API integration, or evaluation task
- If course capability value is weak: add user journey, prioritization, architecture decision, metrics, risk control, and launch constraints
- If portfolio/demo value is weak: require a portfolio page, demo/prototype link, screenshots or recording, PRD, workflow diagram, evaluation table, demo script, and interview narrative

### Step 7: Recommend Project Level

Assign one project level and one course placement recommendation:

| Level | Definition |
|---|---|
| Intro | Clear daily-life or job-seeking scenario; limited domain complexity; mostly product workflow and prompt/output design |
| Intermediate | Real business workflow; requires metrics, risk control, and cross-role thinking |
| Advanced | B2B, RAG, Agent, evaluation system, data loop, permission, governance, or multi-stakeholder decisions |

Course placement: `core-practice`、`optional-practice`、`flagship-project` 或 `not-ready`。

If the project is valuable but too hard, recommend a simplified version for the current course and an advanced extension for a later module.

## Course Development Integration

Use this Skill as a project-gate between `course-design` and the development of the course practice materials:

```text
course-discovery
→ course-design
→ course-practice-project-evaluator
→ 03-教学材料包/
→ course-polish
→ course-review
```

When the project passes, write `实操项目立项评估.md` in the course project directory. Include the approved scope, target learner, course objectives covered, required materials, technical prerequisites, deliverables, demo level, assessment evidence, risks, and any simplified/advanced variants. Do not silently rewrite the course design; record changes as decisions for `course-design` to consume.

## Output Format

Use this structure unless the user asks otherwise:

```markdown
## Project Approval Verdict

Overall score: X/100
Recommendation: [Flagship / Usable / Backup / Not recommended]
Course placement: [core-practice / optional-practice / flagship-project / not-ready]
Suggested level: [Intro / Intermediate / Advanced]
Portfolio surface level: [None / L1 / L2 / L3]

One-sentence judgment: ...

## Scorecard

| Dimension | Score | Weight | Rationale |
|---|---:|---:|---|
| Learner fit | /5 | 20% | ... |
| Time control | /5 | 15% | ... |
| Material availability | /5 | 15% | ... |
| AI execution feasibility | /5 | 15% | ... |
| Product training value | /5 | 20% | ... |
| Portfolio value | /5 | 15% | ... |

## Course Fit And Portfolio Surface

Current level: ...
Required level: ...
Gap: ...

## Capability Signals

| Capability demonstrated | Evidence expected from this project |
|---|---|
| ... | ... |

## Main Risks

- ...

## Improvement Suggestions

- ...

## Required Materials To Make It Work

- ...
```

For multiple projects, produce a comparison table first, then detailed notes only for projects that are unclear, risky, or high priority.

## Quality Rules

- Be stricter with projects that sound impressive but lack materials, scope, evaluation, implementation evidence, or AI-specific decisions.
- Do not reward generic app ideas unless they include realistic users, inputs, workflows, metrics, and risks.
- Do not require heavy engineering for beginner projects; a lightweight working prototype and product artifacts are valid if they test AI/software development judgment.
- Treat "can be completed" and "worth completing" as separate judgments.
- When the target audience is job seekers, always state how the project can be explained in a resume or interview.
- For flagship course projects, always evaluate the first-glance surface separately from the deep project artifacts and course assessment evidence.
- Penalize projects that have strong PRD or methodology artifacts but no visible demo, prototype, screenshots, recording, or portfolio page.
