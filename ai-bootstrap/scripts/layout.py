"""Canonical output layout for AI Bootstrap governance artifacts."""

from pathlib import Path


DOCS_DIR = Path("docs")
AI_DIR = DOCS_DIR / "ai"

# Superpowers / SDD lifecycle stages.
RESEARCH_DIR = DOCS_DIR / "00-research"
DESIGN_TOKEN_SPEC_PATH = RESEARCH_DIR / "design-token-spec.md"
REQUIREMENTS_DIR = DOCS_DIR / "01-requirements"
SPECS_DIR = DOCS_DIR / "02-specs"
PLANS_DIR = DOCS_DIR / "03-plans"
REVIEWS_DIR = DOCS_DIR / "04-reviews"
VERIFICATION_DIR = DOCS_DIR / "05-verification"
DECISIONS_DIR = DOCS_DIR / "06-decisions"

PROJECT_PROFILE_PATH = DOCS_DIR / "PROJECT_PROFILE.md"
DESIGN_PATH = DOCS_DIR / "DESIGN.md"
MEMORY_PATH = AI_DIR / "MEMORY.md"

ADR_DIR = DECISIONS_DIR / "adr"
ADR_INDEX_PATH = ADR_DIR / "INDEX.md"
INITIAL_ADR_PATH = ADR_DIR / "ADR-0001-initial-architecture.md"
DECISION_INDEX_PATH = DECISIONS_DIR / "decisions" / "INDEX.md"
CURRENT_TASKS_PATH = PLANS_DIR / "current.md"
BACKLOG_PATH = PLANS_DIR / "backlog.md"
REVIEW_INDEX_PATH = REVIEWS_DIR / "INDEX.md"

METADATA_DIR = Path(".ai-bootstrap")
MANIFEST_PATH = METADATA_DIR / "bootstrap-manifest.yaml"

PHASE_READMES = {
    RESEARCH_DIR / "README.md": "# 00 · Research\n\n记录调研、现状分析、竞品与技术可行性结论。\n",
    REQUIREMENTS_DIR / "README.md": "# 01 · Requirements\n\n记录目标、范围、用户需求与验收标准。\n",
    SPECS_DIR / "README.md": "# 02 · Specs\n\n记录可实施的功能、接口、数据与交互规格。\n",
    PLANS_DIR / "README.md": "# 03 · Plans\n\n记录实施计划、任务拆分与执行顺序。\n",
    REVIEWS_DIR / "README.md": "# 04 · Reviews\n\n记录设计、代码与架构评审结果。\n",
    VERIFICATION_DIR / "README.md": "# 05 · Verification\n\n记录测试证据、验收结果与发布验证。\n",
    DECISIONS_DIR / "README.md": "# 06 · Decisions\n\n记录架构决策（ADR）和其他可追溯的工程决策。\n",
}

REQUIRED_DIRECTORIES = [
    DOCS_DIR,
    AI_DIR,
    RESEARCH_DIR,
    REQUIREMENTS_DIR,
    SPECS_DIR,
    PLANS_DIR,
    REVIEWS_DIR,
    VERIFICATION_DIR,
    DECISIONS_DIR,
    ADR_DIR,
    DECISION_INDEX_PATH.parent,
    METADATA_DIR,
]
