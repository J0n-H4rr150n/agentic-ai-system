# F00003: Core Node Library

**Status:** 🟢 Complete
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

- [x] S001: Start and End Nodes
- [x] S002: LLM Call Node - Base Interface
- [x] S003: LLM Call Node - Vertex AI Implementation
- [x] S004: LLM Tracing (tokens, timing, decision capture)
- [x] S005: Playwright Browser Node - Session Management
- [x] S006: Playwright Browser Node - Navigation & Actions
- [x] S007: Playwright Browser Node - Observation Modes
- [x] S008: HTTP Request Node
- [x] S009: Router Node with Conditions
- [x] S010: Node Registry & Auto-Discovery
- [x] S011: Code Executor Node
- [x] S012: HTTP Fuzzer Node

## Acceptance Criteria

### Start/End Nodes
- [x] Start node initializes run state
- [x] End node finalizes run and returns result

### LLM Call Node
- [x] Configurable model selection (gemini-2.5-flash, gemini-2.5-pro)
- [x] Provider-agnostic interface (can swap Vertex AI for Claude later)
- [x] Structured output support (JSON mode)
- [x] Tracing captures: input_tokens, output_tokens, elapsed_time_ms
- [x] Decision capture: llm_decision, llm_reasoning, llm_confidence

### Browser Node
- [x] Session created on first browser node in run
- [x] Session shared across all browser nodes in same run
- [x] Navigate to URL action
- [x] Click element action (by selector or SoM index)
- [x] Type text action
- [x] Observation modes work:
  - `visual`: screenshot + screenshot_som
  - `source_inspector`: html_cleaned with comments extracted
  - `traffic_analyst`: network_log array
  - `full`: everything

### HTTP Request Node
- [x] Supports GET, POST, PUT, DELETE, PATCH
- [x] Custom headers
- [x] JSON/form body
- [x] Response captured: status, headers, body

### Router Node
- [x] Multiple output ports based on conditions
- [x] Conditions evaluate against state variables
- [x] Supports: equals, contains, regex, greater_than, less_than
- [x] Default/fallback output port

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
