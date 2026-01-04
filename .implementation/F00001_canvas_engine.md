# F00001: Canvas Engine Foundation

**Status:** 🔵 Planned
**Phase:** 1 (MVP)
**Priority:** P0 (Critical)
**Target:** Today

## Overview

Build the core visual canvas where users can drag nodes from a palette, place them on a grid, wire them together with bezier curves, and serialize the graph to JSON for execution.

## Stories

- [ ] S001: Project Setup & Docker Infrastructure
- [ ] S002: Node.js Express Server
- [ ] S003: HTML5 Canvas with Grid
- [ ] S004: Pan and Zoom Controls
- [ ] S005: Base Node Class & Rendering
- [ ] S006: Node Palette Component
- [ ] S007: Drag-Drop from Palette to Canvas
- [ ] S008: Node Selection & Movement
- [ ] S009: Port System (Input/Output)
- [ ] S010: Bezier Curve Wiring
- [ ] S011: Graph Serialization to JSON

## Acceptance Criteria

- [ ] `docker compose up` starts frontend (Node.js) and backend (FastAPI)
- [ ] Canvas renders with grid background (10px cells)
- [ ] Pan with middle-mouse or space+drag
- [ ] Zoom with scroll wheel, clamped 25%-400%
- [ ] Node palette on left side with categorized node types
- [ ] Nodes can be dragged from palette onto canvas
- [ ] Nodes snap to grid when placed
- [ ] Nodes can be selected (click) and moved (drag)
- [ ] Nodes have input/output ports
- [ ] Ports can be wired together by click-drag
- [ ] Wires render as smooth bezier curves
- [ ] "Export JSON" produces valid graph structure
- [ ] JSON includes: nodes, edges, positions, configs

## Technical Notes

- Frontend: Node.js + Express serving static HTML/JS
- Canvas: HTML5 Canvas API (not SVG, not DOM-based)
- No React/Next.js - vanilla JS only
- All code follows file size guidelines (< 200 lines per file)
- Each component in separate file for testability

## Folder Structure

```
frontend/
  ├── server.js                 # Express entry point (~30 lines)
  ├── package.json
  ├── public/
  │   ├── index.html            # Main page structure
  │   ├── css/
  │   │   ├── base.css          # Reset, variables, typography
  │   │   ├── layout.css        # Main layout (palette, canvas, toolbar)
  │   │   ├── canvas.css        # Canvas-specific styles
  │   │   ├── palette.css       # Palette styles
  │   │   └── nodes.css         # Node rendering styles
  │   └── js/
  │       ├── main.js           # App initialization only
  │       ├── canvas/
  │       │   ├── index.js      # CanvasManager - orchestrates all canvas modules
  │       │   ├── grid.js       # Grid rendering (drawGrid, gridSize)
  │       │   ├── pan-zoom.js   # PanZoomController
  │       │   ├── viewport.js   # Viewport transforms (screen <-> world coords)
  │       │   └── renderer.js   # Main render loop
  │       ├── nodes/
  │       │   ├── index.js      # NodeManager - tracks all nodes
  │       │   ├── base.js       # BaseNode class
  │       │   ├── types/
  │       │   │   ├── start.js  # StartNode
  │       │   │   ├── end.js    # EndNode
  │       │   │   ├── llm.js    # LLMNode
  │       │   │   ├── browser.js # BrowserNode
  │       │   │   └── router.js # RouterNode
  │       │   └── port.js       # Port class (input/output)
  │       ├── wires/
  │       │   ├── index.js      # WireManager - tracks all wires
  │       │   ├── wire.js       # Wire class
  │       │   ├── bezier.js     # Bezier curve math utilities
  │       │   └── connection.js # Connection validation logic
  │       ├── palette/
  │       │   ├── index.js      # PaletteManager
  │       │   ├── categories.js # Node category definitions
  │       │   └── drag.js       # DragDropHandler
  │       ├── selection/
  │       │   ├── index.js      # SelectionManager
  │       │   └── box.js        # Box selection (future)
  │       ├── graph/
  │       │   ├── index.js      # GraphManager - owns the graph data
  │       │   └── serializer.js # JSON import/export
  │       └── utils/
  │           ├── events.js     # Custom event helpers
  │           ├── geometry.js   # Point, Rect, distance utils
  │           └── id.js         # UUID generation
```

## Dependencies

None - this is the foundation.
