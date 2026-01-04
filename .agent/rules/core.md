---
description: 'Primary Coding Agent: Enforces CORE rules for all AI agents working on this project.'
---
# CORE Rules for AI Agents

> **This document governs all AI agent behavior on this project.**
> Every AI must read and follow these rules before making any changes.

---

## Project Overview

This is a **Visual Agent IDE** for building stateful AI agents with drag-and-drop canvas, custom state machine execution, and reusable agent components. Think "Alteryx for AI Logic" — not linear data pipelines, but cyclic state machines.

### Critical Files

| File | Purpose | Action |
|------|---------|--------|
| `.planning/plan.md` | Master architecture, tech decisions, phases | **READ FIRST** before any work |
| `.planning/brainstorm.md` | Raw ideas and requirements | Reference for context |
| `.implementation/changelog.md` | Running log of all completed work | **UPDATE** after completing work |
| `.implementation/F*.md` | Feature and Story specifications | Follow these specs exactly |

---

## The Workflow Process

### Before Starting ANY Work

1. **Read `.planning/plan.md`** — Understand the current architecture and phase
2. **Find the Feature doc** — Look in `.implementation/F{XXXXX}_{slug}.md`
3. **Find or create the Story doc** — Pattern: `F{XXXXX}_S{XXX}_{slug}.md`
4. **Update Story status** to 🟡 In Progress
5. **Understand dependencies** — Check what must exist before your work

### During Work

1. **Update the Story doc** as you make progress:
   - Check off completed tasks `[x]`
   - Add Implementation Notes with context and decisions
   - List all Files Changed with brief descriptions
2. **Follow the folder structure** defined in plan.md exactly
3. **Write tests** alongside implementation code
4. **Commit logical chunks** — don't wait until everything is done

### After Completing Work

1. **Update Story status** to 🟢 Complete
2. **Update Feature doc** — Check off the completed story
3. **Add entry to `changelog.md`** with date and summary
4. **If Feature is complete**, update Feature status to 🟢 Complete

---

## Dependency Management Conventions

This repo intentionally uses **two** Python dependency workflows:

- **Local development/testing:** use **Poetry** from the `backend/` folder.
    - Example: `cd backend` then `poetry install` and `poetry run pytest -q`
- **Docker images:** install Python dependencies via **pip** using `backend/requirements.txt`.

If you add/remove backend dependencies, keep `backend/pyproject.toml` and `backend/requirements.txt` in sync.

---

## Code Organization Principles

### Rule #1: No God Files

Every piece of code must be testable in isolation. If you cannot write a unit test for a function without mocking the entire universe, the code is too coupled.

### File Size Limits

| Lines | Status |
|-------|--------|
| < 200 | ✅ Ideal — aim for this |
| 200-300 | ⚠️ Consider splitting |
| > 300 | 🔴 **MUST refactor** — not acceptable |

### One Responsibility Per File

- A file should do ONE thing well
- If describing what a file does requires "and", split it
- Name files after their single responsibility

### Folder Structure Is Law

The folder structure in `plan.md` is not a suggestion. Follow it exactly:

```
frontend/js/
  ├── canvas/           # Canvas rendering, pan/zoom, grid
  ├── nodes/            # Node classes and rendering
  ├── wires/            # Wire classes and bezier math
  ├── palette/          # Palette UI and drag-drop
  ├── graph/            # Graph data and serialization
  ├── api/              # Backend communication
  └── utils/            # Pure utility functions

backend/
  ├── api/routes/       # HTTP endpoints only
  ├── runner/           # State machine execution
  ├── nodes/            # Node implementations by category
  ├── models/           # Pydantic data models
  └── utils/            # Shared utilities
```

---

## Coding Standards

### No Placeholders

```python
# ❌ NEVER DO THIS
def process_data(data):
    # TODO: implement later
    pass

# ✅ ALWAYS DO THIS - or don't write the function yet
def process_data(data: ProcessInput) -> ProcessOutput:
    validated = validate_input(data)
    transformed = apply_transformation(validated)
    return ProcessOutput(result=transformed)
```

### No Shortcuts

```javascript
// ❌ NEVER DO THIS - "I'll fix it later"
const result = data && data.items && data.items[0] && data.items[0].value;

// ✅ ALWAYS DO THIS - handle properly
function getFirstItemValue(data) {
    if (!data?.items?.length) {
        return null;
    }
    return data.items[0].value ?? null;
}
```

### No Rush

- Quality over speed, always
- If something feels hacky, stop and redesign
- Ask for clarification rather than assume
- One well-designed solution beats three quick fixes

---

## Secure Coding Practices

### Input Validation

```python
# ✅ ALWAYS validate and sanitize inputs
from pydantic import BaseModel, validator

class NodeConfig(BaseModel):
    node_type: str
    url: str

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
```

### No Secrets in Code

```python
# ❌ NEVER hardcode secrets
API_KEY = "sk-12345..."

# ✅ ALWAYS use environment variables
import os
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise EnvironmentError("API_KEY environment variable required")
```

### Parameterized Queries

```python
# ❌ NEVER concatenate SQL
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ ALWAYS use parameterized queries
query = "SELECT * FROM users WHERE id = $1"
result = await db.fetch(query, user_id)
```

### Output Encoding

```javascript
// ❌ NEVER insert raw user content
element.innerHTML = userContent;

// ✅ ALWAYS encode or use safe methods
element.textContent = userContent;
// or
element.innerHTML = DOMPurify.sanitize(userContent);
```

### Principle of Least Privilege

- Request only permissions you need
- Scope access tokens narrowly
- Don't store more data than necessary

---

## Testability Requirements

### Every File Has Tests

```
frontend/js/canvas/grid.js  →  frontend/tests/canvas/grid.test.js
backend/nodes/llm/vertex.py →  backend/tests/nodes/llm/test_vertex.py
```

### Dependency Injection

```python
# ❌ HARD TO TEST - direct import
from redis import Redis

class Checkpointer:
    def __init__(self):
        self.redis = Redis()  # Can't mock this

# ✅ EASY TO TEST - injection
class Checkpointer:
    def __init__(self, redis_client):
        self.redis = redis_client  # Mock in tests
```

### Pure Functions First

```python
# ❌ HARD TO TEST - side effects everywhere
def process_node(node_id):
    node = database.get(node_id)  # Side effect
    result = calculate(node.data)
    database.save(result)         # Side effect
    return result

# ✅ EASY TO TEST - pure logic separated
def calculate_result(node_data: NodeData) -> Result:
    # Pure function - same input always gives same output
    return Result(value=node_data.value * 2)

async def process_node(node_id, db):
    node = await db.get(node_id)
    result = calculate_result(node.data)  # Test this separately
    await db.save(result)
    return result
```

### Test Types Required

| Type | When | Coverage Target |
|------|------|-----------------|
| Unit | Every function with logic | 80%+ |
| Integration | API endpoints, DB queries | Key paths |
| E2E | Critical user flows | Happy path + main errors |

---

## Error Handling

### Never Swallow Errors

```python
# ❌ NEVER do this
try:
    risky_operation()
except:
    pass  # Silent failure

# ✅ ALWAYS handle explicitly
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise OperationError(f"Could not complete: {e}") from e
```

### Use Specific Exceptions

```python
# ❌ Generic exceptions hide problems
raise Exception("Something went wrong")

# ✅ Specific exceptions enable handling
class NodeExecutionError(Exception):
    def __init__(self, node_id: str, message: str):
        self.node_id = node_id
        super().__init__(f"Node {node_id}: {message}")
```

### Fail Fast

```python
# ✅ Validate early, fail early
def execute_graph(graph_json: dict) -> RunResult:
    # Validate immediately
    graph = GraphDefinition.parse_obj(graph_json)  # Fails fast if invalid

    # Check dependencies before starting
    missing = find_missing_nodes(graph)
    if missing:
        raise GraphValidationError(f"Unknown node types: {missing}")

    # Now safe to execute
    return run_graph(graph)
```

---

## Documentation Standards

### Code Comments

```python
# ❌ Don't state the obvious
i = i + 1  # Increment i

# ✅ Explain the WHY
# Offset by 1 because browser node indexes are 1-based (SoM convention)
element_index = raw_index + 1
```

### Docstrings Required

```python
def calculate_bezier_point(t: float, p0: Point, p1: Point, p2: Point, p3: Point) -> Point:
    """
    Calculate a point on a cubic bezier curve.

    Args:
        t: Parameter from 0.0 (start) to 1.0 (end)
        p0: Start point
        p1: First control point
        p2: Second control point
        p3: End point

    Returns:
        The point on the curve at parameter t

    Example:
        >>> midpoint = calculate_bezier_point(0.5, start, ctrl1, ctrl2, end)
    """
```

### README for Each Package

Every folder with `__init__.py` or `index.js` should have a brief README or module docstring explaining:
- What this module does
- Key classes/functions
- Usage example

---

## Naming Conventions

### Files

| Type | Convention | Example |
|------|------------|---------|
| Python modules | snake_case | `graph_parser.py` |
| JS modules | kebab-case or camelCase | `pan-zoom.js` or `panZoom.js` |
| Test files | test_ prefix (Python) | `test_graph_parser.py` |
| Test files | .test.js suffix (JS) | `pan-zoom.test.js` |

### Code

| Type | Python | JavaScript |
|------|--------|------------|
| Classes | PascalCase | PascalCase |
| Functions | snake_case | camelCase |
| Constants | SCREAMING_SNAKE | SCREAMING_SNAKE |
| Variables | snake_case | camelCase |

### Feature/Story IDs

- Features: `F{5 digits}` — `F00001`, `F00002`
- Stories: `S{3 digits}` — `S001`, `S002`
- Full reference: `F00001_S003`

---

## Git Practices

### Core Principles

- **`main` stays green**: no direct pushes; changes land via PR after tests pass.
- **One Story Per PR**: a PR should complete exactly one story (or one bugfix).
- **Story-first documentation**: story doc, feature doc, and changelog updates are part of “done” and belong in the same PR as the code.

### Recommended Branching Model (Team GitHub)

This repo is designed to merge incrementally:

- **Branch per story or bugfix** (default): implement `F{XXXXX}_S{XXX}` on its own branch and PR it into `main`.
- **Feature branches are optional**: only use a `feature/F{XXXXX}-...` long-lived branch if you truly need an integration branch across multiple stories (e.g., risky refactor, parallel workstreams). Otherwise, merge each story PR directly into `main`.

### AI Agent Workflow (Required)

1. **Sync from `main`**
    - Start work from the latest `main`.
    - Keep your branch current (prefer rebasing your own branch; never rewrite shared history).
2. **Create a branch**
    - Story: `story/F00002-S005-base-node-interface`
    - Bugfix: `fix/F00002-import-paths`
3. **Commit in logical chunks**
    - Every commit should leave the repo in a runnable/testable state.
    - Use the story/bugfix ID in the subject.
4. **Before opening a PR**
    - Run the smallest relevant test set first, then the broader suite if practical.
    - Update docs *in the same branch*:
      - Mark the story 🟢 Complete
      - Check off the story in the feature doc
      - Add a dated entry to `.implementation/changelog.md`
      - For bugfixes, add a note under `.implementation/BUGFIXES/`
5. **Open a PR to `main`**
    - Title format: `F00002_S005: Base node executor interface`
    - PR description must include:
      - What changed (1–3 bullets)
      - How to test (exact commands)
      - Docs updated (story/feature/changelog links)
6. **Address review feedback**
    - Push follow-up commits; do not “argue via code”.
    - Keep tests green after each iteration.

### Merge Strategy

- Preferred: **Squash merge** story PRs into `main` so each story lands as one coherent commit.
  - Squash commit message should keep the story ID (e.g., `F00002_S005: ...`).
- Acceptable: **Rebase + merge** if the team prefers linear history.
- Avoid: merging unrelated work into a story PR; if scope grows, split into a new story.

### Commit Messages

```
F00001_S003: Add bezier curve rendering

- Implement cubic bezier calculation
- Add wire rendering with curves
- Include hover highlight effect
```

### Branch Naming

```
feature/F00001-canvas-engine
story/F00001-S003-bezier-wiring
fix/F00001-wire-connection-bug
```

### One Story Per PR

- Each PR should complete one story
- Include story ID in PR title
- Link to Feature doc in PR description

---

## Red Lines — Never Cross These

1. **Never commit broken code** — If it doesn't run, don't commit
2. **Never skip tests** — Untested code is unfinished code
3. **Never ignore security** — Validate inputs, encode outputs, never trust user data
4. **Never use hardcoded secrets** — Environment variables only
5. **Never create god files** — Max 300 lines, prefer < 200
6. **Never leave placeholders** — Implement it or don't write it
7. **Never rush** — Quality first, always
8. **Never assume** — Ask for clarification if uncertain

---

## Getting Help

If you're stuck or uncertain:

1. **Check plan.md** — The answer might be there
2. **Check Feature/Story docs** — Detailed specs exist
3. **Ask the human** — Better to ask than guess wrong
4. **Document the question** — Add to Blockers/Questions in Story doc

---

## Summary Checklist

Before submitting any work, verify:

- [ ] Code follows folder structure from plan.md
- [ ] No file exceeds 300 lines
- [ ] All functions have docstrings
- [ ] Tests exist and pass
- [ ] No hardcoded secrets or credentials
- [ ] Inputs are validated
- [ ] Errors are handled explicitly
- [ ] Story doc is updated
- [ ] Changelog is updated
