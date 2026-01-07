# Scenario 1: Autonomous Agent Workflow

## Overview

This is a complete implementation of the autonomous agent workflow described in `.docs/scenarios/scenario_1.md`.

The agent:
- Loops through analysis steps
- Uses LLM to make decisions with structured output
- Checks confidence scores
- Requires human approval for low-confidence actions
- Executes tools based on AI decisions
- Tracks findings, reasoning, and actions

## File Location

`workflows/examples/scenario_1_autonomous_agent.json`

## How It Works

### 1. Input Nodes (3x)
- **Target URL**: The web page to analyze
- **User Prompt**: What you want the agent to accomplish
- **System Prompt**: Instructions for how the AI should behave

### 2. Loop Node
- Runs up to 10 iterations
- Breaks when `done === true` or `error === true`

### 3. LLM Agent Node
- **Model**: Gemini 2.5 Pro
- **System Prompt**: From input (instructs AI to be conservative with confidence)
- **Prompt**: Combines target URL, user goal, browser output, previous findings
- **Output Schema**:
  ```json
  {
    "response": "string",     // AI's analysis
    "confidence": "number",   // 0-1 confidence score
    "action": "string",       // Next action to take
    "findings": "array",      // Discovered information
    "reasoning": "string",    // Why this decision?
    "done": "boolean"         // Task complete?
  }
  ```

### 4. Confidence Router
- **High Confidence** (≥ 0.5) → Go directly to tool selection
- **Low Confidence** (< 0.5) → Go to human approval

### 5. Human Approval Node
- Shows: action, confidence, reasoning, findings
- **Timeout**: 300 seconds (5 minutes)
- **Approved** → Continue to tools
- **Rejected** → End workflow

### 6. Tool Selection Router
Based on `llm_action`:
- `navigate` or `screenshot` → Browser Tool
- `http_request` → HTTP Tool
- `done === true` → End workflow

### 7. Tool Execution
- **Browser Tool**: Takes screenshot, navigates, etc.
- **HTTP Tool**: Makes HTTP requests

### 8. Loop Back
After tool execution, loops back to LLM with updated context

## Workflow Visualized

```
┌──────────────┐
│ Input: URL   │
│ Input: Prompt│──┐
│ Input: System│  │
└──────────────┘  │
                  ▼
        ┌─────────────────┐
        │   Loop (x10)    │◄────────────────┐
        └────────┬────────┘                 │
                 │                          │
          ┌──────▼───────┐                  │
          │  LLM Agent   │                  │
          │ outputs:     │                  │
          │  confidence  │                  │
          │  action      │                  │
          │  findings    │                  │
          └──────┬───────┘                  │
                 │                          │
          ┌──────▼───────┐                  │
          │  Confidence  │                  │
          │   Router     │                  │
          └──┬────────┬──┘                  │
             │        │                     │
        <0.5 │        │ >=0.5               │
             │        │                     │
    ┌────────▼┐    ┌─▼────────┐            │
    │ Human   │    │   Tool   │            │
    │Approval │    │ Selection│            │
    └────┬────┘    └─┬────┬───┘            │
         │           │    │                │
    [Rejected]  [Browser][HTTP]            │
         │           │    │                │
         ▼           └────┴────────────────┘
     [End]          (Loop Back)
```

## How to Run

### Option 1: Load in UI (not yet implemented)
1. Open the canvas app
2. File → Open Workflow
3. Select `scenario_1_autonomous_agent.json`
4. Click "Run"

### Option 2: API (when backend is ready)
```bash
curl -X POST http://localhost:10301/api/run \
  -H "Content-Type: application/json" \
  -d @workflows/examples/scenario_1_autonomous_agent.json
```

## Expected Behavior

### Iteration 1
1. LLM analyzes target URL with no prior context
2. Decides: "Let's navigate and take a screenshot" (confidence: 0.8)
3. High confidence → Skip approval
4. Browser tool executes
5. Loop continues with screenshot output

### Iteration 2
1. LLM analyzes screenshot
2. Decides: "I see a login form, let's try form-filling" (confidence: 0.4)
3. **Low confidence → Human approval required**
4. Modal appears: "Review Low Confidence Action"
   - Shows: action, confidence, reasoning
   - Human approves or rejects
5. If approved, continues

### Iteration N
1. LLM decides task is complete (done: true)
2. Router sees `done === true`
3. Routes to End node
4. Workflow finishes with findings

## Customization

### Change Confidence Threshold
Edit router conditions in `router-confidence`:
```json
{
  "var": "llm_confidence",
  "op": "greater_equal",
  "value": 0.7,  // Change from 0.5 to 0.7 for more approvals
  "output": "high_confidence"
}
```

### Add More Tools
1. Add new tool node
2. Add condition to `router-tool`:
   ```json
   {
     "var": "llm_action",
     "op": "equals",
     "value": "your_tool_action",
     "output": "your_tool"
   }
   ```
3. Add wire from router to tool
4. Wire tool back to loop

### Change System Prompt
Edit `input-system` value to give different AI instructions

## Testing

### Unit Test Checklist
- [ ] Input nodes populate state correctly
- [ ] LLM outputs match schema
- [ ] Router checks confidence correctly
- [ ] Approval pauses workflow
- [ ] Tool selection works
- [ ] Loop terminates on `done` or max iterations

### Integration Test
- [ ] Full workflow runs end-to-end
- [ ] State persists across iterations
- [ ] Approval affects routing
- [ ] Multiple tool types work

### Manual Test
1. Set target_url to `http://localhost:10303/`
2. Run workflow
3. Verify LLM makes sensible decisions
4. Test human approval when triggered
5. Confirm findings are captured

## Troubleshooting

**Issue**: Workflow loops forever
- **Fix**: Check LLM is setting `done: true` when task is complete

**Issue**: Always goes to approval
- **Fix**: LLM might be too conservative - adjust system prompt

**Issue**: Tools not executing
- **Fix**: Check `llm_action` matches router conditions exactly

## Next Steps

1. Implement backend executors for new node types
2. Add approval UI to frontend
3. Test with real LLM calls
4. Add more example workflows
5. Build workflow import/export feature
