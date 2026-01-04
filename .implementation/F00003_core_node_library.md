# F00003: Core Node Library

**Status:** 🔵 Planned
**Phase:** 1 (MVP)
**Priority:** P0 (Critical)
**Target:** Today

## Overview

Implement the essential nodes needed for the security testing MVP workflow:
- Start/End (control flow)
- LLM Call (provider-agnostic)
- Playwright Browser (with observation modes)
- HTTP Request
- Router (conditional branching)

## Stories

- [ ] S001: Start and End Nodes
- [ ] S002: LLM Call Node - Base Interface
- [ ] S003: LLM Call Node - Vertex AI Implementation
- [ ] S004: LLM Tracing (tokens, timing, decision capture)
- [ ] S005: Playwright Browser Node - Session Management
- [ ] S006: Playwright Browser Node - Navigation & Actions
- [ ] S007: Playwright Browser Node - Observation Modes
- [ ] S008: HTTP Request Node
- [ ] S009: Router Node with Conditions
- [ ] S010: Node Registry & Auto-Discovery

## Acceptance Criteria

### Start/End Nodes
- [ ] Start node initializes run state
- [ ] End node finalizes run and returns result

### LLM Call Node
- [ ] Configurable model selection (gemini-2.5-flash, gemini-2.5-pro)
- [ ] Provider-agnostic interface (can swap Vertex AI for Claude later)
- [ ] Structured output support (JSON mode)
- [ ] Tracing captures: input_tokens, output_tokens, elapsed_time_ms
- [ ] Decision capture: llm_decision, llm_reasoning, llm_confidence

### Browser Node
- [ ] Session created on first browser node in run
- [ ] Session shared across all browser nodes in same run
- [ ] Navigate to URL action
- [ ] Click element action (by selector or SoM index)
- [ ] Type text action
- [ ] Observation modes work:
  - `visual`: screenshot + screenshot_som
  - `source_inspector`: html_cleaned with comments extracted
  - `traffic_analyst`: network_log array
  - `full`: everything

### HTTP Request Node
- [ ] Supports GET, POST, PUT, DELETE, PATCH
- [ ] Custom headers
- [ ] JSON/form body
- [ ] Response captured: status, headers, body

### Router Node
- [ ] Multiple output ports based on conditions
- [ ] Conditions evaluate against state variables
- [ ] Supports: equals, contains, regex, greater_than, less_than
- [ ] Default/fallback output port

## Technical Notes

- LLM: google-cloud-aiplatform SDK for Vertex AI
- Browser: playwright-python with persistent context per run
- All nodes inherit from BaseNode with standard interface
- Node outputs flow into state, downstream nodes read from state

## Folder Structure

```
backend/
  ├── nodes/
  │   ├── __init__.py
  │   ├── base.py               # BaseNode abstract class
  │   │                         # - async execute(state, config) -> NodeResult
  │   │                         # - get_input_schema() -> dict
  │   │                         # - get_output_schema() -> dict
  │   ├── registry.py           # NodeRegistry singleton
  │   │                         # - register(type_name, node_class)
  │   │                         # - get(type_name) -> NodeClass
  │   │                         # - list_all() -> [NodeInfo]
  │   │
  │   ├── control/
  │   │   ├── __init__.py
  │   │   ├── start.py          # StartNode - initializes state
  │   │   ├── end.py            # EndNode - finalizes run
  │   │   └── router.py         # RouterNode - conditional branching
  │   │
  │   ├── llm/
  │   │   ├── __init__.py
  │   │   ├── base.py           # BaseLLMNode - common LLM interface
  │   │   ├── vertex.py         # VertexAINode - Gemini implementation
  │   │   ├── config.py         # LLMConfig dataclass
  │   │   └── tracing.py        # LLMTrace dataclass, trace builder
  │   │
  │   ├── browser/
  │   │   ├── __init__.py
  │   │   ├── node.py           # BrowserNode - main entry point
  │   │   ├── session.py        # SessionManager - creates/retrieves sessions
  │   │   ├── actions.py        # navigate, click, type, screenshot
  │   │   └── observation.py    # ObservationBuilder - builds output by mode
  │   │
  │   └── http/
  │       ├── __init__.py
  │       └── request.py        # HTTPRequestNode
```

## Node Interface

```python
class BaseNode(ABC):
    node_type: str
    
    @abstractmethod
    async def execute(
        self, 
        state: StateContainer, 
        config: dict,
        context: ExecutionContext
    ) -> NodeResult:
        """Execute the node and return result."""
        pass
    
    @classmethod
    def get_input_schema(cls) -> dict:
        """JSON Schema for node inputs/config."""
        pass
    
    @classmethod
    def get_output_schema(cls) -> dict:
        """JSON Schema for node outputs."""
        pass

@dataclass
class NodeResult:
    success: bool
    output: dict
    error: Optional[str] = None
    trace: Optional[dict] = None  # LLM-specific tracing
```

## Dependencies

- F00002 (Runner executes the nodes)
