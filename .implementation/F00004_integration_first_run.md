# F00004: Integration & First Run

**Status:** 🟡 In Progress
**Phase:** 1 (MVP)
**Priority:** P0 (Critical)
**Target:** Today

## Overview

Wire everything together: frontend canvas talks to backend runner, add run controls to UI, build a sample multi-agent workflow visually, and execute it against a local lab target.

## Stories

- [x] S001: API Client Module (Frontend)
- [x] S002: Run Controls UI (Run button, status indicator)
- [x] S003: SSE Integration for Real-time Updates
- [x] S004: Execution Trace Viewer (GitHub Actions style)
- [x] S005: Build Sample Security Workflow
- [ ] S006: End-to-End Test Against Local Lab

## Acceptance Criteria

### Frontend Integration
- [x] API client module handles all backend calls
- [x] "Run" button in toolbar sends graph to `/api/run`
- [x] Status indicator shows: idle, running, completed, failed
- [x] SSE stream updates UI in real-time as steps execute

### Execution Trace Viewer
- [x] Panel shows list of steps (collapsible)
- [x] Each step shows: node name, type, status icon, duration
- [x] Expand step to see: input, output, error (if any)
- [x] Screenshot preview for browser nodes
- [x] Auto-scroll to current step during execution

### Sample Workflow
- [ ] Workflow includes: Start → Browser → LLM → Router → End
- [ ] Browser node configured with lab URL
- [ ] LLM node analyzes page source for interesting patterns
- [ ] Router decides next action based on LLM output

### End-to-End Verification
- [ ] Workflow executes successfully against lab target
- [ ] All steps show in trace viewer
- [ ] Screenshots captured and viewable
- [ ] LLM tracing visible (tokens, reasoning)

## Technical Notes

- SSE endpoint: `/api/run/{id}/stream`
- Use EventSource API in browser
- Trace viewer uses virtual scrolling for large traces (future)

## Folder Structure

```
frontend/
  └── public/
      └── js/
          ├── api/
          │   ├── client.js     # Base API client (fetch wrapper)
          │   └── run.js        # RunAPI - start, status, stream
          ├── ui/
          │   ├── toolbar.js    # Toolbar with Run button
          │   ├── status.js     # StatusIndicator component
          │   └── trace/
          │       ├── index.js  # TraceViewer - main component
          │       ├── step.js   # StepRow - individual step display
          │       └── detail.js # StepDetail - expanded view
          └── sse/
              └── stream.js     # SSE handler with reconnect logic
```

## UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Toolbar: [Run ▶] [Stop ■]  Status: ● Running...             │
├─────────────┬───────────────────────────────────────────────┤
│             │                                               │
│   Palette   │              Canvas                           │
│             │                                               │
│  ┌───────┐  │     ┌─────┐     ┌─────┐     ┌─────┐          │
│  │ Start │  │     │Start│────→│Brwsr│────→│ LLM │          │
│  ├───────┤  │     └─────┘     └─────┘     └──┬──┘          │
│  │Browser│  │                                 │             │
│  ├───────┤  │                          ┌──────┴──────┐      │
│  │  LLM  │  │                          ▼             ▼      │
│  ├───────┤  │                      ┌─────┐       ┌─────┐    │
│  │Router │  │                      │Found│       │ End │    │
│  ├───────┤  │                      └─────┘       └─────┘    │
│  │  End  │  │                                               │
│  └───────┘  │                                               │
│             │                                               │
├─────────────┴───────────────────────────────────────────────┤
│  Trace Viewer                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ ✓ Step 1: Start           0ms                          ││
│  │ ✓ Step 2: Browser        523ms  ▼                      ││
│  │   └─ Input: {url: "http://lab.local"}                  ││
│  │   └─ Output: {screenshot: "...", html: "..."}          ││
│  │ ● Step 3: LLM (running)                                ││
│  │ ○ Step 4: Router                                       ││
│  │ ○ Step 5: End                                          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Dependencies

- F00001 (Canvas)
- F00002 (Runner)
- F00003 (Nodes)

## Testing

### Manual Verification

1. Start the system: `docker compose up`
2. Open browser to `http://localhost:36300`
3. Drag nodes onto canvas: Start → Browser → LLM → End
4. Configure Browser node with lab URL
5. Wire the nodes together
6. Click "Run"
7. Verify trace viewer shows each step in real-time
8. Verify browser screenshot captured and viewable
9. Verify LLM analysis returned with tracing data

### Success Criteria for Today's MVP

The MVP is successful when:

1. ✅ User can visually build a multi-agent workflow on canvas
2. ✅ User can run the workflow against a local lab target
3. ✅ User can view execution results and iterate
