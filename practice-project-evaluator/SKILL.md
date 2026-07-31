---
name: practice-project-evaluator
description: Evaluate AI product manager practice projects for feasibility, learning value, portfolio value, employability signal, and visible demo readiness. Use when assessing whether a proposed practice project is reasonable, realistic, suitable for students or job seekers, aligned with AI PM work, whether it needs a demo or portfolio surface, or when comparing multiple practice project ideas and identifying what capabilities a practitioner can demonstrate after completing them.
---

# Practice Project Evaluator

## Overview

Use this skill to evaluate AI product manager practice projects before adding them to a course, bootcamp, portfolio program, or project library. Focus on two questions:

1. Can the target learner realistically complete the project with available time, tools, and materials?
2. Will the finished project credibly demonstrate AI product manager capabilities in a resume, portfolio, or interview?
3. Can the finished project be understood by a recruiter or first-round screener within 30 seconds?

Default target audience: graduating students, overseas returnees, early-career job seekers, and career switchers with limited real project experience.

## Inputs To Look For

When evaluating a project, gather what is available from the user's prompt or local files:

- project name and one-sentence brief
- target user and scenario
- expected learner profile
- available source materials or data
- expected deliverables
- demo, prototype, screenshot, recording, portfolio page, or runnable site expectations
- time budget
- tool or technical assumptions
- evaluation rubric, if one already exists

If evaluating a project directory, read `project.md` first. If present, also read `materials/`, `templates/`, `examples/`, or overview files only when needed to judge feasibility.

## Evaluation Workflow

### Step 1: Restate The Project

Summarize the project in one compact sentence:

> For [target user] in [scenario], solve [pain point] by designing [AI product/workflow], and evaluate success through [metrics].

If the project cannot be restated in this structure, flag it as underdefined.

### Step 2: Score Feasibility

Score each dimension from 1 to 5. Convert weighted score to 100.

| Dimension | Weight | What To Check |
|---|---:|---|
| Learner fit | 20% | Can the target learners understand the domain and complete the work without excessive prerequisites? |
| Time control | 15% | Can a complete version be finished in 1-3 weeks? |
| Material availability | 15% | Are inputs available, such as JD, FAQ, documents, sample data, user cases, competitor examples, or output samples? |
| AI execution feasibility | 15% | Can learners complete the core AI workflow with accessible tools, without heavy engineering or model training? |
| Product training value | 20% | Does the project train real AI PM judgment, not just prompt writing, generic research, or UI imagination? |
| Portfolio value | 15% | Can the result become a credible resume/portfolio/interview artifact with a visible demo or portfolio surface? |

Score bands:

| Score | Judgment | Action |
|---:|---|---|
| 85-100 | Strong flagship project | Prioritize building full materials, templates, and reference output |
| 75-84 | Usable project | Keep in project pool, but patch the weakest dimensions |
| 60-74 | Backup project | Use only after simplifying scope or adding materials |
| < 60 | Not recommended | Redesign or reject |

Flagship constraint: do not label a project "Strong flagship project" unless it has at least an L1 visible portfolio surface. For job-seeker-facing programs, prefer L2 for flagship projects and use L3 for the strongest showcase projects.

### Step 3: Check AI PM Authenticity

Flag whether the project contains AI-specific product work:

- AI capability fit: why AI is needed instead of a normal rules-based workflow
- input design: what context, constraints, and user data the AI needs
- output design: expected format, quality bar, and user action after output
- evaluation: how to judge good vs bad AI output
- risk control: hallucination, privacy, bias, compliance, overclaiming, or unsafe automation
- human-in-the-loop: when the user, operator, expert, or reviewer must intervene
- iteration loop: how feedback improves prompt, knowledge base, workflow, or product experience

A project with fewer than 4 of these elements is likely too thin for AI PM training.

### Step 4: Map Demonstrated Capabilities

Identify what completing the project proves about the practitioner. Use this capability map:

| Capability | Evidence In Student Output |
|---|---|
| Problem framing | Clear target user, scenario, pain point, and success definition |
| User research | Persona, journey map, pain point evidence, interview summary, or behavior analysis |
| Product judgment | Prioritization, tradeoff reasoning, MVP scope, and non-goals |
| AI capability understanding | Prompt/RAG/Agent workflow, model boundaries, input-output constraints |
| Interaction design | User flow, prototype, information architecture, exception states |
| Evaluation literacy | Metrics, test set, scoring rubric, Bad Case analysis |
| Business thinking | Connection to efficiency, conversion, retention, cost, quality, or risk |
| Risk and ethics | Privacy, hallucination, fairness, misuse prevention, human review |
| Communication | PRD, structured report, decision memo, demo, or 5-minute pitch |
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

For every score below 4, explain the blocking issue and give a targeted fix.

Common fixes:

- If learner fit is weak: add background primer, glossary, sample case, or reduce domain complexity
- If time control is weak: narrow to one user role, one core workflow, and one deliverable
- If materials are weak: provide sample data pack, mock cases, source documents, or competitor screenshots
- If AI execution is weak: replace model training with prompt workflow, RAG design, prototype, or evaluation task
- If product value is weak: add user journey, prioritization, metrics, and launch constraints
- If portfolio value is weak: require a portfolio page, demo/prototype link, screenshots or recording, PRD, workflow diagram, evaluation table, demo script, and interview narrative

### Step 7: Recommend Project Level

Assign one level:

| Level | Definition |
|---|---|
| Intro | Clear daily-life or job-seeking scenario; limited domain complexity; mostly product workflow and prompt/output design |
| Intermediate | Real business workflow; requires metrics, risk control, and cross-role thinking |
| Advanced | B2B, RAG, Agent, evaluation system, data loop, permission, governance, or multi-stakeholder decisions |

If the project is valuable but too hard, recommend a simplified version and an advanced extension.

## Output Format

Use this structure unless the user asks otherwise:

```markdown
## Feasibility Verdict

Overall score: X/100
Recommendation: [Flagship / Usable / Backup / Not recommended]
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

## Portfolio Surface

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

- Be stricter with projects that sound impressive but lack materials, scope, evaluation, or AI-specific decisions.
- Do not reward generic app ideas unless they include realistic users, inputs, workflows, metrics, and risks.
- Do not require heavy engineering for beginner projects; product artifacts are valid if they test PM judgment.
- Treat "can be completed" and "worth completing" as separate judgments.
- When the target audience is job seekers, always state how the project can be explained in a resume or interview.
- For job-seeker-facing flagship projects, always evaluate the first-glance surface separately from the deep project artifacts.
- Penalize projects that have strong PRD or methodology artifacts but no visible demo, prototype, screenshots, recording, or portfolio page.
