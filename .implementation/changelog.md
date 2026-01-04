# Changelog

All notable changes to this project will be documented in this file.

---

## 2026-01-04

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
