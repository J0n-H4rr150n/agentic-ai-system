# Trading Platform Exploration Workflow

## Quick Start

### Option 1: Load via UI
1. Open the Visual Agent IDE: http://localhost:36300
2. Click **File** → **Load workflow**
3. Select the "Trading Platform Exploration" workflow
4. Click **Run** to execute

### Option 2: Run via API

**Test Mode (no real LLM calls):**
```powershell
$workflow = Get-Content .examples\workflows\trading_platform_exploration.json -Raw
$body = @{
    graph = $workflow | ConvertFrom-Json
    mode = "test"
} | ConvertTo-Json -Depth 10

curl.exe -X POST http://localhost:36301/api/run `
  -H "Content-Type: application/json" `
  -d $body
```

**Simulate Mode (dry run with validation):**
```powershell
$body.mode = "simulate"
curl.exe -X POST http://localhost:36301/api/run `
  -H "Content-Type: application/json" `
  -d $body
```

**Full Run (requires GCP_PROJECT_ID for Vertex AI):**
```powershell
$body.mode = "run"
curl.exe -X POST http://localhost:36301/api/run `
  -H "Content-Type: application/json" `
  -d $body
```

## Workflow Overview

This workflow explores the Trading Platform at http://localhost:41014/:

1. **Start Node** - Initializes with target URL and objective
2. **Browser Node** - Navigates to the target and captures:
   - Screenshot
   - HTML source (cleaned)
   - Network traffic
   - Console logs
3. **LLM Node** - Analyzes the captured data to identify:
   - Application type
   - Interactive elements
   - Authentication mechanisms
   - Interesting features
   - Next testing steps
4. **End Node** - Returns the analysis results

## Expected Output

The workflow will return a JSON analysis with:
- App type description
- List of interactive elements found
- Whether login exists
- Interesting features to test
- Recommended next action

## Next Steps

After this initial exploration, you can create follow-up workflows that:
- Attempt to interact with forms
- Test authentication
- Explore discovered endpoints
- Test for common vulnerabilities
