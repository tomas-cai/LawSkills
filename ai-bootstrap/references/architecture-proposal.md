# AI Bootstrap Architecture Reference v1.1

> Canonical architecture reference for the current implementation. SKILL.md is the operating guide; this document defines the durable design contracts behind it.

## 1. Purpose

AI Bootstrap injects durable engineering context into a project. It does not generate application code or replace the project's framework-specific scaffold.

The system must:

- detect an existing project's technology signals before asking avoidable questions;
- generate a thin-root, SDD-oriented documentation structure;
- support multiple AI agents with a shared routing contract;
- preserve existing files unless the caller explicitly uses --force;
- validate the generated governance artifacts.

## 2. Canonical output layout

~~~text
project/
├── AGENTS.md
├── README.md                       # New projects only
├── .gitignore                      # New projects only
├── docs/
│   ├── PROJECT_PROFILE.md
│   ├── DESIGN.md
│   ├── ai/MEMORY.md
│   ├── 00-research/
│   ├── 01-requirements/
│   ├── 02-specs/
│   ├── 03-plans/
│   │   ├── current.md
│   │   └── backlog.md
│   ├── 04-reviews/INDEX.md
│   ├── 05-verification/
│   └── 06-decisions/
│       ├── adr/
│       │   ├── INDEX.md
│       │   └── ADR-0001-initial-architecture.md
│       └── decisions/INDEX.md
└── .ai-bootstrap/bootstrap-manifest.yaml
~~~

The root remains an engineering entry point. Human- and Agent-authored SDD artifacts belong under docs/; machine-oriented bootstrap state belongs under .ai-bootstrap/.

## 3. Document responsibilities

| Artifact | Responsibility | Update rule |
|---|---|---|
| AGENTS.md | Agent roles, write constraints, context-reading order | Update when collaboration governance changes |
| docs/PROJECT_PROFILE.md | Project DNA: stack, architecture and agents | Change deliberately; architecture changes require an ADR |
| docs/DESIGN.md | Architecture boundaries and implementation constraints | Keep aligned with the active Blueprint and codebase |
| docs/ai/MEMORY.md | Current collaboration state, blockers and handoffs | Update after meaningful Agent work |
| docs/00–05 | Research through verification evidence | Add artifacts at the corresponding SDD stage |
| docs/06-decisions/adr/ | Architecture Decision Records | Use for durable structural choices |
| docs/06-decisions/decisions/ | Other traceable engineering decisions | Use for non-architectural trade-offs |
| .ai-bootstrap/bootstrap-manifest.yaml | Generated metadata and validation state | Treat as machine-readable state |

An ADR (Architecture Decision Record) records context, options, decision, consequences and status for a significant architecture decision.

## 4. Pipeline contract

~~~text
detect.py → Blueprint resolution → generate.py → validate.py
                 ↑
             wizard.py
~~~

1. detect.py produces structured environment and project signals. It must not mutate the target.
2. The resolver selects an explicit Blueprint, an auto-detected Blueprint, or a clearly labelled generic fallback.
3. generate.py renders only missing governance files by default. --force permits replacement. --dry-run performs no writes.
4. validate.py checks required paths, document syntax, Blueprint-stack consistency, agent definitions, ADR initialization and directory structure.

## 5. Blueprint contract

Blueprints define the selected stack and architectural style. Templates must derive their engineering guidance from Blueprint facts; they must not impose Next.js, DDD, REST, or JavaScript conventions on an unrelated stack.

At a minimum, a Blueprint declares:

~~~yaml
id: example
stack:
  frontend: { framework: none, language: none }
  backend: { framework: example-framework, language: example-language }
  database: { primary: example-db }
architecture:
  style: layered
  pattern: modular-monolith
~~~

The generated profile must preserve the Blueprint's frontend, backend and database values. It must select a meaningful primary language: frontend language when present, otherwise backend language.

## 6. Multi-Agent contract

The --agents argument defines the complete participating Agent set. The same set must be represented in both:

- AGENTS.md, with role and operational constraints;
- docs/PROJECT_PROFILE.md, as project DNA.

The context router is:

~~~text
AGENTS.md → docs/PROJECT_PROFILE.md → docs/DESIGN.md →
docs/ai/MEMORY.md → docs/06-decisions/adr/INDEX.md →
docs/03-plans/current.md
~~~

## 7. Validation contract

Validation success means the required governance structure is present and machine-parseable. It does not prove application code correctness.

The test suite must cover:

- parsing every bundled Blueprint;
- generation and validation for every bundled Blueprint;
- existing-file protection and explicit overwrite;
- auto-resolution for a detected project;
- all supported language-entry paths in detection;
- multi-Agent preservation in profile and routing documents;
- malformed Agent definitions and Blueprint/profile mismatches.

## 8. Compatibility and evolution

New fields may be added to a Blueprint or manifest. Existing paths in the canonical layout are stable within v1.x. Any path migration requires:

1. an ADR explaining the migration and compatibility impact;
2. a generator and validator update in the same change;
3. migration guidance in SKILL.md;
4. regression tests for both fresh and existing projects.

## 9. Non-goals

- generating framework application code;
- overwriting user code or governance documents without --force;
- treating MEMORY.md as a replacement for source control or issue tracking;
- enforcing a single architectural style across all Blueprints.
