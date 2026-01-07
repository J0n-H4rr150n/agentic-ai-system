# F00014: Autonomous Agent Node Types

**Status:** � Complete
**Phase:** Phase 10 (Agent Capabilities)
**Depends on:** F00001 (Canvas Engine), F00013 (Canvas UI)
**Completed:** 2026-01-07

---

## Overview

Implement specialized node types to enable autonomous agent workflows with human-in-the-loop oversight. This includes generic input nodes, enhanced LLM capabilities with system prompts and structured outputs, and human approval mechanisms for high-risk or low-confidence actions.

**Based on:** `.docs/scenarios/scenario_1.md`

---

## User Story

As a workflow builder, I want to create autonomous agents that:
- Loop through decision-making steps
- Call different tools based on AI decisions
- Track confidence, findings, and reasoning
- Pause for human approval when needed

So that I can build safe, observable AI agents that can handle complex, multi-step tasks.

---

## Stories

### F00014_S001: Generic Input Node

**Priority:** High
**Status:** 🟢 Complete

**Acceptance Criteria:**
- [x] New `input` node type available in palette
- [x] Configurable label and value
- [x] Specifies output_key for state storage
- [x] Replaces need for hardcoded Start node fields
- [x] Can create multiple input nodes per workflow

**Use Cases:**
- Target URL input
- User prompt input
- System instructions input
- Any string/text data entry point

---

### F00014_S002: Enhanced LLM Node with Structured Output

**Priority:** High
**Status:** 🟢 Complete

**Acceptance Criteria:**
- [x] `system_prompt` field added to LLM node
- [x] `output_schema` field for structured JSON output
- [x] LLM outputs multiple trackable fields (response, confidence, action, findings, etc.)
- [x] Backend enforces JSON schema when provided
- [x] Each schema field stored to state separately

**Benefits:**
- Better AI instruction following
- Structured, parseable outputs
- Confidence scoring for decision-making
- Citations and reasoning captured

---

### F00014_S003: Human Approval Node

**Priority:** High
**Status:** 🟢 Complete

**Acceptance Criteria:**
- [x] New `human_approval` node type
- [x] Pauses workflow execution
- [x] Displays context from state
- [x] Shows approval message/prompt
- [x] Supports approve/reject actions
- [x] Routes to different outputs based on decision
- [x] Optional timeout with default rejection

**Safety Features:**
- Review before high-risk actions
- Verify low-confidence decisions
- Manual oversight for critical workflows
- Audit trail of approvals/rejections

---

## Technical Design

### Node Type Hierarchy

```
Existing Nodes:
├── start - Initial workflow trigger
├── end - Workflow termination
├── llm - AI reasoning (ENHANCED)
├── router - Conditional branching
├── loop - Iteration control
└── browser - Web automation

New Nodes:
├── input - Generic data input (NEW)
└── human_approval - Human oversight (NEW)
```

### State Management

**Input Node:**
```javascript
// Config
{
  "label": "Target URL",
  "value": "http://example.com",
  "output_key": "target_url"
}

// Execution Result
state.target_url = "http://example.com"
```

**Enhanced LLM Node:**
```javascript
// Config
{
  "model": "gemini-2.5-pro",
  "system_prompt": "You are a web security analyst...",
  "prompt": "Analyze {{target_url}}",
  "output_schema": {
    "response": "string",
    "confidence": "number",
    "action": "string",
    "findings": "array",
    "reasoning": "string"
  }
}

// Execution Result
state.llm_response = "I found 3 login forms..."
state.llm_confidence = 0.85
state.llm_action = "click_button"
state.llm_findings = ["form1", "form2", "form3"]
state.llm_reasoning = "Based on the DOM structure..."
```

**Human Approval Node:**
```javascript
// Config
{
  "title": "Review Proposed Action",
  "message": "Agent wants to click login button",
  "show_state_keys": ["llm_action", "llm_confidence", "llm_reasoning"],
  "timeout_seconds": 300
}

// UI Display
┌─────────────────────────────────┐
│ Review Proposed Action          │
├─────────────────────────────────┤
│ Agent wants to click login btn  │
│                                 │
│ Action: click_button            │
│ Confidence: 0.45                │
│ Reasoning: Low confidence...    │
│                                 │
│ [Approve] [Reject]              │
└─────────────────────────────────┘

// Execution Result
state.approval_result = "approved" | "rejected"
// Routes to "approved" or "rejected" output port
```

---

## Example Workflow

**Scenario:** Autonomous web analysis with human oversight

```
[Input: URL] ──────┐
[Input: Prompt] ───┼──→ [Loop (max:10)]
[Input: System] ───┘         │
                             ▼
                    ┌────────────────┐
                    │   LLM Agent    │
                    │ system_prompt: │
                    │ output_schema: │
                    │   {confidence, │
                    │    action, etc}│
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │  Router        │
                    │ confidence>=0.5│
                    └──┬──────────┬──┘
                       │ NO       │ YES
              ┌────────▼┐    ┌───▼──────┐
              │  Human  │    │  Router  │
              │Approval │    │Select Tol│
              └────┬────┘    └──┬───┬───┘
                   │            │   │
              [Approved]   [Browser][HTTP]
                   │            │   │
                   └────────────┴───┴──→ [Loop Back]
```

---

## Implementation Order

1. **F00014_S001: Input Node**
   - Add to `schemas.js`
   - Create template
   - Backend executor (simple state assignment)

2. **F00014_S002: Enhanced LLM**
   - Update LLM schema
   - Modify backend LLM executor
   - Add structured output parsing

3. **F00014_S003: Human Approval**
   - Add to `schemas.js`
   - Create template
   - Backend approval mechanism (async)
   - Frontend approval UI

---

## Testing Strategy

### Unit Tests
- Input node stores to correct state key
- LLM parses output schema correctly
- Approval node handles timeout

### Integration Tests
- End-to-end loop with LLM → Router → Approval
- State preservation across iterations
- Approval affects routing

### Manual Tests
- Build example workflow from scenario_1.md
- Verify confidence-based routing
- Test human approval flow
- Confirm tool execution after approval

---

## Future Enhancements

- **Approval History** - Track all approval decisions
- **Confidence Tuning** - Adjust thresholds per workflow
- **Tool Risk Levels** - Mark tools as high/medium/low risk
- **Approval Groups** - Route to different approvers
- **Slack/Email Notifications** - Alert when approval needed
