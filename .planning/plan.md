# Visual Agent IDE — Project Plan

> **Vision:** A visual IDE for building stateful AI agents with drag-and-drop canvas, custom state machine execution, and reusable agent components.

---

## Key Architectural Decisions

| Decision | Choice |
|----------|--------|
| Starting point | Fresh codebase |
| Execution engine | Custom lightweight state machine (no LangGraph) |
| Frontend | Custom HTML5 Canvas + vanilla JS (no React Flow) |
| Backend | Python FastAPI |
| State storage | Redis (hot) + Postgres/pgvector (cold) |
| Browser automation | Playwright with shared session per run |
| LLM integration | Provider-agnostic nodes (GCP Vertex AI default) |
| Reusability | Save graph → becomes palette node with version history |
| Frontend server | Node.js (Express) — avoid Next.js/React due to CVE concerns |
| Real-time updates | SSE for streaming (not WebSocket unless 2-way needed) |

---

## Documentation & Workflow Process

All AI agents (and humans) must follow this consistent process when implementing features.

### Folder Structure

```
.planning/
  └── plan.md              # This file - master architecture & phases
  └── brainstorm.md        # Raw ideas and requirements gathering

.implementation/
  └── changelog.md         # Running log of all completed work
  └── BUGFIXES/             # Bugfix notes (non-story work)
  │   └── BUGFIX_{slug}.md
  └── F00001_canvas_engine.md         # Feature spec (epic-level)
  └── F00001_canvas_engine/           # Stories for this feature
  │   └── F00001_S001_{slug}.md
  │   └── F00001_S002_{slug}.md
  └── F00002_state_machine_runner.md  # Next feature
  └── F00002_state_machine_runner/    # Stories for this feature
  │   └── F00002_S001_{slug}.md
  └── ...
```

### Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `F{XXXXX}_{slug}.md` | `F00001_canvas_engine.md` |
| Story | `F{XXXXX}_S{XXX}_{slug}.md` | `F00001_S001_drag_drop_nodes.md` |

**Location rules:**
- Feature docs live at `.implementation/F{XXXXX}_{slug}.md`
- Story docs live under the feature folder: `.implementation/F{XXXXX}_{slug}/F{XXXXX}_S{XXX}_{slug}.md`
- Bugfix docs live under `.implementation/BUGFIXES/`

### Feature Document Template

```markdown
# F00001: Canvas Engine

**Status:** 🟡 In Progress | 🟢 Complete | 🔴 Blocked
**Phase:** 1
**Priority:** P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low)

## Overview
Brief description of the feature and why it matters.

## Stories
- [ ] S001: Drag and Drop Nodes
- [ ] S002: Bezier Curve Wiring
- [ ] S003: Container Detection

## Acceptance Criteria
- User can drag nodes from palette onto canvas
- Nodes can be wired together with curves
- ...

## Technical Notes
Architecture decisions, gotchas, dependencies.

## Related Files
- `frontend/canvas.js`
- `frontend/nodes/`
```

### Story Document Template

```markdown
# F00001_S001: Drag and Drop Nodes

**Status:** 🟡 In Progress
**Assignee:** AI Agent / Human Name
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
What this story accomplishes.

## Tasks
- [x] Create node base class
- [x] Implement drag handlers
- [ ] Add snap-to-grid
- [ ] Write tests

## Implementation Notes
Detailed notes as work progresses. AI agents should update this section
as they work through the story.

## Files Changed
- `frontend/canvas.js` - Added DragManager class
- `frontend/nodes/base.js` - Created BaseNode

## Testing
How to verify this story works.

## Blockers / Questions
Any issues encountered.
```

### Changelog Format

```markdown
# Changelog

## 2026-01-04

### F00001_S001: Drag and Drop Nodes
- Created `BaseNode` class with drag handlers
- Implemented snap-to-grid (10px increments)
- Added palette → canvas drag support

### F00001_S002: Bezier Curve Wiring
- ...
```

### AI Agent Workflow

1. **Before starting work:**
   - Check `plan.md` for current phase priorities
   - Find or create the Feature doc (`F{XXXXX}_{slug}.md`)
  - Find or create the Story doc (`F{XXXXX}_S{XXX}_{slug}.md`) in the corresponding feature folder
   - Update Story status to 🟡 In Progress

2. **During work:**
   - Update Story's Tasks checklist as items complete
   - Add Implementation Notes with decisions/context
   - List Files Changed

3. **After completing work:**
   - Update Story status to 🟢 Complete
   - Add entry to `changelog.md`
   - Update Feature doc's story checklist
   - If Feature complete, update Feature status to 🟢 Complete

---

## Local Dev Conventions

### Port Range Policy

To avoid conflicts with system ports and other local services, **all runtime ports used by this repo must be in the range `36300–36399`**.

Current allocations:
- Frontend (Express): `36300`
- Backend (FastAPI): `36301`

### Makefile Commands

This repo uses a root `Makefile` to standardize common dev commands.

- `make run` → `docker compose down` then `docker compose up --build -d`
- `make down` → stop containers
- `make logs` → tail container logs

### Python Dependency Management (Poetry vs Docker)

- **Local development/testing:** use **Poetry** in the `backend/` folder.
  - Example: `cd backend && poetry install && poetry run pytest`
- **Docker images:** install dependencies via **pip** using `backend/requirements.txt`.
  - This keeps container builds simple and predictable.

### Code Organization Principles

> **Rule #1: No God Files.** Every piece of code must be testable in isolation.

#### File Size Guidelines

| Max Lines | Action Required |
|-----------|-----------------|
| < 200 | ✅ Ideal |
| 200-300 | ⚠️ Consider splitting |
| > 300 | 🔴 Must refactor |

#### Folder Structure Requirements

```
frontend/
  ├── server.js                 # Express entry point only
  ├── public/
  │   ├── index.html
  │   ├── css/
  │   │   ├── base.css          # Variables, reset, typography
  │   │   ├── canvas.css        # Canvas-specific styles
  │   │   ├── palette.css       # Palette-specific styles
  │   │   └── components.css    # Reusable component styles
  │   └── js/
  │       ├── main.js           # App initialization only
  │       ├── canvas/
  │       │   ├── index.js      # Canvas manager
  │       │   ├── grid.js       # Grid rendering
  │       │   ├── pan-zoom.js   # Pan/zoom handlers
  │       │   └── selection.js  # Selection handling
  │       ├── nodes/
  │       │   ├── index.js      # Node registry
  │       │   ├── base.js       # BaseNode class
  │       │   ├── llm.js        # LLM node
  │       │   ├── browser.js    # Browser node
  │       │   └── router.js     # Router node
  │       ├── wires/
  │       │   ├── index.js      # Wire manager
  │       │   ├── bezier.js     # Bezier curve math
  │       │   └── connection.js # Connection validation
  │       ├── palette/
  │       │   ├── index.js      # Palette manager
  │       │   └── drag.js       # Drag-drop handling
  │       ├── api/
  │       │   ├── client.js     # API client base
  │       │   └── run.js        # Run-specific API calls
  │       └── utils/
  │           ├── events.js     # Event helpers
  │           └── geometry.js   # Geometry utilities

backend/
  ├── main.py                   # FastAPI entry point only
  ├── api/
  │   ├── __init__.py
  │   ├── routes/
  │   │   ├── __init__.py
  │   │   ├── run.py            # /api/run endpoints
  │   │   ├── workflow.py       # /api/workflow endpoints
  │   │   └── node.py           # /api/node endpoints
  │   └── deps.py               # Dependency injection
  ├── runner/
  │   ├── __init__.py
  │   ├── graph_parser.py       # JSON → execution plan
  │   ├── executor.py           # Main execution loop
  │   ├── state.py              # State management
  │   ├── tracer.py             # Step tracing
  │   └── checkpoint.py         # Redis checkpointing
  ├── nodes/
  │   ├── __init__.py
  │   ├── base.py               # BaseNode abstract class
  │   ├── registry.py           # Node type registry
  │   ├── llm/
  │   │   ├── __init__.py
  │   │   ├── base.py           # LLM base class
  │   │   ├── vertex.py         # Vertex AI implementation
  │   │   └── tracing.py        # LLM-specific tracing
  │   ├── browser/
  │   │   ├── __init__.py
  │   │   ├── session.py        # Session management
  │   │   ├── actions.py        # Click, type, navigate
  │   │   └── observation.py    # Screenshot, HTML, network
  │   ├── http/
  │   │   ├── __init__.py
  │   │   ├── request.py        # HTTP request node
  │   │   └── fuzzer.py         # Batch fuzzing node
  │   └── control/
  │       ├── __init__.py
  │       ├── router.py         # Conditional routing
  │       ├── loop.py           # Loop control
  │       └── gate.py           # Parallel fork/join
  ├── models/
  │   ├── __init__.py
  │   ├── graph.py              # Graph data models
  │   ├── run.py                # Run/trace models
  │   └── node.py               # Node config models
  └── utils/
      ├── __init__.py
      ├── redis.py              # Redis client
      └── postgres.py           # Postgres client
```

#### Testability Requirements

1. **Each file should have a corresponding test file**
   - `frontend/js/canvas/grid.js` → `frontend/tests/canvas/grid.test.js`
   - `backend/nodes/llm/vertex.py` → `backend/tests/nodes/llm/test_vertex.py`

2. **Dependencies must be injectable**
   - No hardcoded imports of external services
   - Use dependency injection for Redis, Postgres, LLM clients

3. **Pure functions where possible**
   - Separate business logic from I/O
   - Makes unit testing straightforward

## Core Concepts

### Node Contract (MCP-Style Universal Format)

Every node (tool, LLM, router, saved agent) follows the same contract:

```json
{
  "id": "node-uuid",
  "type": "browser_tool | llm_call | router | custom_agent",
  "version": "1.0.0",
  "inputs": { "url": "string", "session_id?": "string" },
  "outputs": { "screenshot": "base64", "html_source": "string", ... },
  "config": { "observation_mode": "visual | source_inspector | traffic_analyst" }
}
```

### Execution Modes

| Mode | Description |
|------|-------------|
| **Validate** | Check graph structure, connections, type compatibility |
| **Test** | Run with mocked inputs/outputs |
| **Simulate** | Dry-run with real calls but no side effects |
| **Run** | Full execution with session history |

### Browser Session Management

- **One session per run** by default (maintains auth cookies/headers)
- Nodes can request `new_session: true` to spawn isolated browser
- Sessions NOT persisted across runs — each run is self-contained
- Session stored in Redis with TTL, rehydrated via WebSocket

### Browser Output + Observation Modes

Browser node produces rich output:
```json
{
  "screenshot": "base64",
  "screenshot_som": "base64 (Set-of-Mark overlays)",
  "html_source": "full HTML",
  "html_cleaned": "comments extracted, scripts removed",
  "network_log": [{ "url": "...", "method": "...", "response": "..." }],
  "cookies": [...],
  "console_log": [...]
}
```

Downstream LLM nodes select observation mode:
- `visual` → screenshot_som for click decisions
- `source_inspector` → html_cleaned for secrets/comments
- `traffic_analyst` → network_log for API patterns
- `full` → everything (expensive)

### LLM Node Observability

Every LLM call captures structured tracing data:

```json
{
  "trace": {
    "elapsed_time_ms": 1234,
    "input_tokens": 500,
    "output_tokens": 150,
    "model": "gemini-2.5-pro",
    "provider": "vertex_ai"
  },
  "decision": {
    "llm_decision": "login_with_credentials",
    "llm_reasoning": "Found dev comment with username/password...",
    "llm_confidence": 0.92,
    "alternatives_considered": ["brute_force", "sql_injection"]
  },
  "scoring": {
    "llm_score": 0.85,
    "score_target": "idor_vulnerability_likelihood",
    "score_reasoning": "Sequential integer IDs in URL path..."
  }
}
```

All tracing data stored in Postgres for analysis and debugging.

### LLM Memory & RAG Integration

**When to query pgvector:**
- **Planning phase**: Pull relevant playbooks/runbooks for the task type
- **Similar patterns**: "Have I seen this before?" → query episodic memory
- **Grounding**: Security best practices, vulnerability patterns

**Memory types:**
| Type | Source | Use Case |
|------|--------|----------|
| Playbooks | Pre-loaded docs | IDOR patterns, XSS testing, auth bypass |
| Episodic | Past run summaries | "Last time I saw this pattern..." |
| Lessons Learned | Human feedback | Corrections from reject/edit actions |

**Injection points:**
- Router nodes can query for "what pattern is this?"
- Planner agents pull relevant playbooks before generating tasks
- Judge agents query lessons learned before validating

### Human-in-the-Loop

- **Interrupt points** defined on nodes (like LangGraph)
- **Non-modal UI** — human sees full execution state, not blocked by popups
- **Actions:** Allow, Edit (modify node input), Reject (stops entire run)
- **Pause/Force-Stop** controls available at runtime

### Run History (GitHub Actions Style)

- Every step traced: input, output, duration, status
- Collapsible step-by-step view with expandable details
- Stored per-run in Postgres for replay/debugging

---

## Implementation Phases

### Phase 1: Canvas Engine Foundation

**Goal:** Draggable nodes, containers, bezier wiring on HTML5 canvas.

- [x] HTML5 Canvas grid with pan/zoom
- [x] Draggable node primitives (rectangle, diamond)
- [x] Container detection (nodes know their parent)
- [x] Bezier curve wiring with connection validation
- [x] Serialization to JSON graph format
- [x] Basic node palette (static nodes)

**Deliverable:** Canvas where you can place nodes, wire them, export JSON.

---

### Phase 2: State Machine Runner

**Goal:** Python backend that executes graph JSON with parallel node support.

- [x] FastAPI endpoint: `POST /api/run` accepts graph JSON
- [x] Graph parser → execution plan with dependency resolution
- [x] Parallel node execution (asyncio)
- [x] State object passed through graph
- [x] Redis integration for checkpoints
- [x] Execution modes: validate, test, simulate, run
- [x] Step-by-step tracing/logging

**Deliverable:** API that runs a graph and returns execution trace.

---

### Phase 3: Core Node Library

**Goal:** Essential nodes for the security testing MVP.

#### Action Nodes
- [x] **LLM Call** — Provider-agnostic (Vertex AI default), model selection per-node
- [x] **HTTP Request** — Raw HTTP with headers/body
- [x] **Code Executor** — Python snippet execution
- [ ] **HTTP Fuzzer** — Batched requests with LLM-driven analysis loop

#### Browser Nodes
- [x] **Playwright Browser** — All observation modes (screenshot, SoM, HTML, network)
- [x] **Browser Action** — Click, type, navigate (consumes session_id)

#### Control Nodes
- [x] **Router** — Conditional branching with dynamic output ports
- [ ] **Loop** — Iterate with break condition
- [ ] **Parallel Gate** — Fork/join for parallel branches

**Deliverable:** Node library sufficient for web security testing workflow.

---

### Phase 4: Execution Control & Human-in-the-Loop

**Goal:** Interrupt handling, pause/resume, approval gates.

- [ ] Interrupt point configuration on nodes
- [ ] Pause execution → persist state to Redis
- [ ] Resume from checkpoint
- [ ] Human-in-the-loop UI (non-modal)
- [ ] Allow/Edit/Reject actions
- [ ] Force-stop mechanism
- [ ] WebSocket for real-time execution updates

**Deliverable:** Full execution control with human oversight.

---

### Phase 5: Fractal Architecture (Reusable Agents)

**Goal:** Save graphs as reusable palette nodes with versioning.

- [ ] "Save as Node" action on containers
- [ ] Version history in Postgres
- [ ] Saved agents appear in palette
- [ ] Nested execution (agent-within-agent)
- [ ] Input/output schema inference from graph

**Deliverable:** Build complex agents from saved sub-agents.

---

### Phase 6: Run History & Debugging

**Goal:** GitHub Actions-style run viewer.

- [ ] Run list view (all runs for a workflow)
- [ ] Collapsible step tree per run
- [ ] Expand step → see inputs, outputs, screenshots
- [ ] Time-travel: replay from any checkpoint
- [ ] Filter/search by status, node type

**Deliverable:** Full observability into past runs.

---

## MVP Target: CTF Lab Solver

A working end-to-end workflow that:

1. Takes target URL + initial prompt
2. Supervisor agent creates plan (task list)
3. Browser tool navigates to target
4. Source Inspector finds dev comments with credentials
5. Browser tool logs in with credentials
6. Browser tool explores, finds potential IDOR patterns
7. HTTP Fuzzer tests IDOR in batches
8. LLM analyzes responses, forms hypothesis
9. Judge agent validates findings
10. System captures FLAG{}

This validates the entire architecture: canvas, runner, browser integration, LLM orchestration, human-in-the-loop.

---

## Tech Stack Summary

```
┌─────────────────────────────────────────────────────────┐
│              Frontend (Node.js + Express)               │
│  HTML5 Canvas + Vanilla JS + SSE Streaming              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                       │
│  /api/run, /api/validate, /api/workflows, /api/nodes    │
└─────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│    Redis     │  │   Postgres   │  │  Playwright Pool │
│  Checkpoints │  │  Workflows   │  │  Browser Sessions│
│  Sessions    │  │  Run History │  │                  │
│              │  │  Vectors     │  │                  │
└──────────────┘  └──────────────┘  └──────────────────┘
```

---

## GCP Cloud Architecture (Future)

For production deployment with ephemeral container runners using **GKE + Kubernetes Jobs**:

```
┌──────────────────────────────────────────────────────────────┐
│                  GKE Cluster (Autopilot)                     │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Deployment: FastAPI Backend (API + Orchestration)      │ │
│  │  - Persistent pods, LoadBalancer service                │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                 │
│            ┌───────────────┼───────────────┐                 │
│            ▼               ▼               ▼                 │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐    │
│  │  K8s Job       │ │  K8s Job       │ │  K8s Job       │    │
│  │  (Run Worker)  │ │  (Run Worker)  │ │  (Run Worker)  │    │
│  │  Ephemeral     │ │  Ephemeral     │ │  Ephemeral     │    │
│  └────────────────┘ └────────────────┘ └────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Namespace: sandbox (NetworkPolicy isolated)            │ │
│  │  - XSS/reflection testing pods                          │ │
│  │  - Egress only to target domains                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**Ephemeral Run Workers (Kubernetes Jobs):**
- Created per-run, auto-deleted on completion (TTL)
- Contains: Playwright, Python runtime, node executor
- Resource limits enforced per-job
- Logs streamed to Cloud Logging

**Dangerous Operation Isolation:**
- Separate `sandbox` namespace with NetworkPolicy
- Egress firewall: only allow target domain
- No access to internal services (Redis, Postgres)
- Results passed via shared PVC or Pub/Sub

**Local Development:**
- Docker Compose mirrors the GKE structure
- Same container images used locally and in prod

---

## Open Questions / Future Considerations

1. **Playbooks/Runbooks:** How to ground LLM decision-making for common patterns (IDOR in URL, IDOR in header, etc.) — answered: RAG over security playbooks in pgvector.

2. **Judge Agent Pattern:** Formal implementation of hypothesis → judge validation loop.

3. **Multi-model Orchestration:** Rules for when to use Flash vs Pro (cost/speed tradeoffs).

4. **Scope Boundaries:** Safety rails to prevent attacking out-of-scope domains.

---

## Next Steps

1. Begin Phase 4: Execution Control & Human-in-the-Loop
2. Add Redis checkpoints + pause/resume/force-stop control surface
3. Add WebSocket-based runtime controls (2-way)
