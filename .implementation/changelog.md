# Changelog

All notable changes to this project will be documented in this file.

---

## 2026-01-04

### F00003_S011: Code Executor Node
- Add `code_executor` backend node with restricted expression evaluation
- Wire into node factory and workflow schema inference
- Expose node in palette and fix HTTP node type to `http_request`

### Planning Complete

- Created comprehensive `plan.md` with:
  - Key architectural decisions
  - Documentation & workflow process (JIRA-style Features/Stories)
  - Code organization principles (no god files, folder structure)
  - Core concepts (node contract, execution modes, browser sessions, LLM tracing)
  - Implementation phases (1-6)
  - Tech stack and GKE architecture

- Created Feature docs for MVP:
  - `F00001_canvas_engine.md` - 11 stories for visual canvas
  - `F00002_state_machine_runner.md` - 10 stories for Python executor
  - `F00003_core_node_library.md` - 10 stories for node implementations
  - `F00004_integration_first_run.md` - 6 stories for wiring it together

### Dev Workflow Updates

- Added root `Makefile` with `make run`/`make down` helpers
- Documented convention: Poetry for local backend testing, pip installs in Docker

### F00001_S001: Project Setup & Docker Infrastructure

- Added Docker Compose for `frontend` + `backend`
- Added minimal Express frontend scaffold serving `frontend/public/`
- Added `make run` workflow and documented local usage

### F00001_S002: Node.js Express Server

- Added minimal Express server serving static assets from `frontend/public/`
- Added frontend `/health` endpoint

### F00001_S003: HTML5 Canvas with Grid

- Added canvas layout and render loop
- Implemented 10px grid rendering with resize handling
- Added unit tests for grid line math (`node --test`)

### F00001_S004: Pan and Zoom Controls

- Added middle-mouse pan and space+drag pan
- Added wheel zoom clamped to 25%–400% and anchored at cursor
- Updated grid renderer to respect viewport transforms + added unit tests

### F00001_S005: Base Node Class & Rendering

- Added `BaseNode` primitive (world coords, bounds, hit-test) and `NodeManager`
- Rendered nodes in the main canvas render loop (viewport-aware)
- Added unit tests for geometry and node hit-testing

### F00001_S006: Node Palette Component

- Added categorized node palette in the left sidebar
- Defined MVP palette categories/types as testable data + added unit tests

### F00001_S007: Drag-Drop from Palette to Canvas

- Added palette → canvas drag/drop creating new nodes
- Added world-coordinate drop conversion + 10px grid snapping
- Added unit tests for drop/snap math

### F00001_S008: Node Selection & Movement

- Added click-to-select and drag-to-move in world coordinates
- Added snapping to 10px grid on drag release
- Added unit tests for selection move math and node z-order hit-testing

### F00001_S009: Port System (Input/Output)

- Added `Port` model (input/output) with validation and default ports per node type
- Rendered ports on nodes (viewport-aware)
- Added port layout + hit-testing helpers (NodeManager)

### F00001_S012: Container Detection (Nodes Know Their Parent)

- Added UI-only container nodes and containment detection (`parentId`)
- Ensured container nodes are excluded from serialized graphs to avoid impacting backend execution
- Added unit tests for containment selection and serialization filtering
- Added unit tests for port layout and hit-testing

### F00001_S010: Bezier Curve Wiring

- Added WireManager + Wire model for storing port connections
- Implemented output→input click-drag wiring with live preview
- Rendered wires as smooth cubic beziers (viewport-aware)
- Added unit tests for bezier math and connection validation

### F00001_S011: Graph Serialization to JSON

- Added pure graph serializer producing `{version,nodes,edges}`
- Added minimal "Export JSON" button that downloads `graph.json`
- Included nodes, edges, positions, ports, and configs in exported JSON
- Added unit tests for serialization

### F00002_S001: FastAPI Project Setup & Docker

- Added FastAPI backend scaffold with `/api/health`
- Added container-friendly pytest setup and a minimal health endpoint test
- Added Poetry configuration for local backend testing

### F00002_S002: Pydantic Models for Graph Schema

- Added Pydantic v2 graph schema models (`GraphDefinition`, nodes, edges, ports)
- Added basic referential integrity validation (edges reference existing nodes/ports)
- Added backend unit tests for valid/invalid graphs

### F00002_S006: State Container Class

- Added `StateContainer` abstraction for runner state with key validation and snapshot/to-dict helpers
- Added unit tests covering core state behaviors

### F00002_S007: Async Executor with Parallel Support

- Added `AsyncExecutor` that runs dependency-ready nodes concurrently via asyncio
- Ensured deterministic execution via stable ready ordering and deterministic state merge
- Added unit tests for parallel readiness and dependency gating

### F00002_S008: Step Tracer (Input/Output/Duration)

- Added step trace models and a `StepTracer` collector
- Wired tracing into `AsyncExecutor` (input/output/duration/status)
- Extended executor tests to verify deterministic trace ordering

### F00002_S009: Run API Endpoints

- Added `POST /api/run` and `GET /api/run/{id}` endpoints backed by an in-memory run store
- Runs execute in the background via asyncio tasks and return step traces on GET
- Added unit tests for run endpoint behavior

### F00002_S010: SSE Streaming for Real-time Updates

- Added `GET /api/run/{id}/stream` SSE endpoint for step updates
- Stream emits step events as nodes complete and a terminal status event
- Added unit test validating streaming behavior

### F00003_S001: Start and End Nodes

- Added `StartNode` and `EndNode` under `backend/nodes/control/`
- Start node supports injecting `initial_state` into the run
- End node returns a final state snapshot under a configurable `result_key`
- Wired run execution to instantiate Start/End nodes by type
- Added unit tests for Start/End node behavior

### F00003_S002: LLM Call Node - Base Interface

- Added provider-agnostic `LLMClient` protocol and normalized `LLMResponse` models
- Added `LLMCallNode` that sources prompt from config or state and supports JSON mode
- Added unit tests for prompt sourcing, JSON parsing, and validation

### F00003_S003: LLM Call Node - Vertex AI Implementation

- Added `VertexAILLMClient` implementing `LLMClient` using Vertex AI (Gemini)
- Implemented lazy provider imports and `asyncio.to_thread(...)` execution to keep tests fast and avoid blocking
- Added unit tests with fakes (no network)
- Added `google-cloud-aiplatform` to Poetry + `backend/requirements.txt`

### F00003_S004: LLM Tracing (tokens, timing, decision capture)

- Added `LLMTrace` and helper functions for token/timing/decision fields
- Updated `LLMCallNode` output to include `trace` with elapsed time and usage
- Added unit tests for trace extraction and JSON decision capture

### F00003_S005: Playwright Browser Node - Session Management

- Added `BrowserSessionManager` for per-run session reuse
- Added explicit lifecycle methods (`close`, `close_all`) and unit tests

### F00003_S006: Playwright Browser Node - Navigation & Actions

- Added browser action helpers for navigate/click/type against a page-like protocol
- Added `BrowserNode` that executes one action using `BrowserSessionManager` (unit-tested with fakes)
- Added support for click-by-SoM-index via `state['som_index_to_selector']`

### F00003_S007: Playwright Browser Node - Observation Modes

- Added observation builder with modes: `visual`, `source_inspector`, `traffic_analyst`, `full`
- Browser node can optionally include screenshot/HTML/network data in its output via `config.observation_mode`
- Added unit tests using fakes (no real Playwright required)

### F00003_S008: HTTP Request Node

- Added `HTTPRequestNode` using `httpx.AsyncClient` with configurable method/url/headers/body
- Supports JSON body or form body (mutually exclusive) and captures response status/headers/body
- Added unit tests using `httpx.MockTransport` (no network)

### F00003_S009: Router Node with Conditions

- Added `RouterNode` that selects a route based on state conditions
- Supports operators: equals, contains, regex, greater_than, less_than with a default fallback
- Added unit tests for match ordering, dotted-path state lookups, and invalid config validation

### F00003_S010: Node Registry & Auto-Discovery

- Added `NodeRegistry` supporting register/get/list/is_supported and one-time auto-discovery
- Auto-discovery scans and imports modules under `backend.nodes.*` and registers those exporting `NODE_TYPE`/`NODE_CLASS`
- Updated graph parsing to validate supported node types via the registry
- Added unit tests for discovery idempotency and graph parsing validation

### F00007_S005: Filter/Search (Status + Node Type)

- Added `status` and `node_type` query params to `GET /api/runs` and covered with backend tests
- Persisted node-id→type mapping into run history so node type filtering is fast and graph-independent
- Added minimal Run History filters (status select + node type input) and frontend API tests for query params
- Fixed backend Docker image layout so `backend.*` imports work in-container (enables `make test-backend-docker`)

### F00007_S001: Persist Run Metadata + Step Traces

- Added in-memory run history store for terminal run records
- Persisted terminal run metadata and step traces on run completion/failure/cancel
- Added `GET /api/runs` and `GET /api/runs/{run_id}` endpoints for browsing run history
- Added backend tests covering persistence + API behavior

### F00007_S002: Run List View (Per Workflow)

- Added `workflow_id` association to run creation and run history persistence
- Added `workflow_id` filtering for `GET /api/runs` and returned `workflow_id` in responses
- Added minimal per-workflow run history list UI (backed by last-saved workflow id)
- Added backend and frontend tests for workflow-scoped run history

### F00007_S003: Run Detail View (Steps, Inputs/Outputs, Screenshots)

- Added `getRun(runId)` API client to fetch persisted run detail from run history
- Made the run history list clickable and wired selection into the existing trace viewer
- Added a DOM-free loader that optionally loads the run's workflow graph to enrich node titles/types
- Added frontend unit tests for loader behavior

### F00007_S004: Replay from Checkpoint (Time-travel)

- Persisted optional checkpoint data into run history records ("where available")
- Added `POST /api/runs/{run_id}/replay` to start a new run from a persisted checkpoint
- Added minimal Run History UI replay affordance and frontend API client support
- Added backend integration test and frontend unit test coverage

### F00004_S001: API Client Module (Frontend)

- Added `frontend/public/js/api/client.js` fetch wrapper with JSON handling and typed errors
- Added `frontend/public/js/api/run.js` with helpers for `/api/run` (start/status) and opening `/api/run/{id}/stream`
- Added a minimal same-origin `/api/*` proxy in the frontend Express server (uses `BACKEND_URL`)
- Added unit tests for API modules (`node --test`)

### F00004_S002: Run Controls UI (Run button, status indicator)

- Added a minimal toolbar above the canvas with a Run button and status indicator
- Implemented run control logic: serialize graph, start run, then poll run status until terminal state
- Added unit tests for run-control and status formatting logic

### F00004_S003: SSE Integration for Real-time Updates

- Added SSE stream helper with JSON parsing and reconnect logic
- Updated run controls to prefer SSE terminal status events (polling fallback)
- Added unit tests for SSE reconnect behavior and run-control SSE integration

### F00004_S004: Execution Trace Viewer (GitHub Actions style)

- Added trace viewer panel that renders step traces in real time
- Wired SSE `step` events to append collapsible step rows with input/output/error
- Added screenshot preview support for base64 screenshot fields
- Added unit tests for trace formatting and sanitization

### F00004_S005: Build Sample Security Workflow

- Added a built-in sample workflow loaded on startup: Start → Browser → LLM → Router → End
- Included default node configs for URL, LLM prompt, and router decision placeholders
- Added unit tests for sample workflow graph structure

### F00004_S006: End-to-End Test Against Local Lab

- Added backend node factory to instantiate real node implementations from a graph definition
- Added an HTTP-backed page implementation for browser-node tests (no Playwright dependency)
- Added a backend E2E test that runs a graph against an in-process local HTTP server
- Updated default sample workflow target URL and improved trace screenshot extraction for nested outputs

### F00005_S001: Interrupt Point Configuration on Nodes

- Added `interrupt` configuration to graph node schema with validation (before/after + optional reason)
- Plumbed interrupt configs into the runner execution plan for later pause/resume stories
- Added backend unit tests for interrupt validation and plan plumbing

### F00005_S002: Persist Checkpoint + Pause Execution

- Added backend pause control endpoint (`POST /api/run/{id}/pause`) and paused run status
- Added in-memory run checkpoint model and checkpoint retrieval endpoint (`GET /api/run/{id}/checkpoint`)
- Updated executor to stop at safe batch boundaries and persist a deterministic checkpoint
- Added backend integration tests for pause/checkpoint behavior

### F00005_S003: Resume Execution from Checkpoint

- Added resume control endpoint (`POST /api/run/{id}/resume`) for paused runs
- Updated executor to resume from a persisted checkpoint without re-running completed nodes
- Ensured step tracing continues with monotonically increasing step ids across pause/resume
- Added backend integration tests for pause → resume → completed

### F00005_S004: Force-stop Mechanism (Cancel Run)

- Added cancel control endpoint (`POST /api/run/{id}/cancel`) and terminal `cancelled` run status
- Updated executor to honor cancel requests at safe batch boundaries (no partial batch cancellation)
- Added backend integration tests for cancelling running runs and cancelling paused runs

### F00005_S005: Human-in-the-loop Actions (Allow / Edit / Reject)

- Updated executor to pause automatically on node interrupt points (`interrupt.before`/`interrupt.after`)
- Added run metadata for pending interrupts and pause reason, plus HITL endpoints:
  - `POST /api/run/{id}/hitl/allow`
  - `POST /api/run/{id}/hitl/edit` (shallow state patch)
  - `POST /api/run/{id}/hitl/reject`
- Added backend integration tests for HITL pause → allow/edit/reject flows

### F00005_S006: Runtime Control Channel (WebSocket)

- Added WebSocket run control endpoint: `WS /api/run/{id}/control`
- WebSocket accepts JSON commands for pause/resume/cancel/HITL decisions and returns structured status responses
- Added backend integration tests for WebSocket control behavior

### F00006_S001: Persist Workflows (Save/Load) in Backend

- Added workflow save/load endpoints:
  - `POST /api/workflow` stores a validated graph and returns `workflow_id`
  - `GET /api/workflow/{workflow_id}` returns the stored graph
- Wired workflow router into the FastAPI app
- Added backend tests for workflow create/get behavior

### F00006_S002: “Save as Node” Action (Frontend)

- Added workflow API client module (`createWorkflowApi`) for create/get workflow
- Added a minimal toolbar action “Save as Node” that POSTs the serialized graph to `POST /api/workflow`
- Added workflow status display in the toolbar showing returned `workflow_id`
- Added frontend unit tests covering the workflow API client and save-as-node controller

### F00006_S003: Version History for Saved Agent Nodes

- Versioned workflow storage in-memory (workflow id now has versions starting at 1)
- Added workflow version endpoints:
  - `POST /api/workflow/{workflow_id}/version` creates a new version
  - `GET /api/workflow/{workflow_id}/versions` lists version history
- Updated `GET /api/workflow/{workflow_id}` to support `?version=` (defaults to latest)
- Added backend tests covering version create/list/get behaviors

### F00006_S004: Palette Integration for Saved Agents

- Added `GET /api/workflow` endpoint to list saved workflows (for UI discovery)
- Extended frontend workflow API client with `listWorkflows()`
- Rendered a display-only “Saved Agents” section in the palette populated from backend
- Added backend and frontend unit tests for listing + palette category building

### F00006_S005: Nested Execution (Agent-within-Agent)

- Added shared workflow store module for reuse by API routes and runtime node execution
- Added `agent` node type that loads a saved workflow and executes it as a subgraph
- Nested execution uses parent state as initial state and merges subgraph final state back into the parent
- Included a nested trace boundary under reserved `__agent__` output payload
- Added backend end-to-end test for nested execution via `POST /api/run`

### F00006_S006: Infer Input/Output Schema from Saved Graphs

- Added `GET /api/workflow/{workflow_id}/schema` endpoint returning inferred `inputs`, `outputs`, and `warnings`
- Implemented best-effort schema inference based on node types/config conventions (deterministic)
- Supports nested `agent` nodes by resolving referenced workflows (bounded recursion)
- Added backend tests covering schema inference results and nested agent schema inclusion
