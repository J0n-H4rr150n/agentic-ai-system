# Examples

## Bug Bounty (simulate mode) graph

Graph file:
- `.examples/graphs/bug_bounty_simulate_graph.json`

Request bodies (ready to POST without shell quoting):
- `.examples/requests/create_workflow_bug_bounty_simulate.json`
- `.examples/requests/run_bug_bounty_simulate.json`
- `.examples/requests/run_bug_bounty_test.json`

This graph uses only node types that are already wired in the backend factory and exposed in the frontend palette:
- `start`, `parallel_gate`, `browser` (navigate), `http_request` (GET), `http_fuzzer` (GET), `llm`, `end`

Default target:
- `lab-target` service on `http://lab-target:36303/` (container-to-container, wired in `docker-compose.yml`)

If you run the backend outside Docker, switch to `http://localhost:36303/` in the example JSON.

It is intentionally safe for `mode="simulate"`:
- Browser action is `navigate` only
- HTTP methods are `GET` only

### Create workflow via API

The real API expects `{ "graph": <GraphDefinition> }`.

1) Create a workflow (stores the graph):

Windows (PowerShell):

```powershell
curl.exe -s -X POST http://localhost:36301/api/workflow `
  -H "Content-Type: application/json" `
  --data-binary "@.examples/requests/create_workflow_bug_bounty_simulate.json"
```

2) Run it in simulate mode:

Windows (PowerShell):

```powershell
curl.exe -s -X POST http://localhost:36301/api/run `
  -H "Content-Type: application/json" `
  --data-binary "@.examples/requests/run_bug_bounty_simulate.json"
```

Optional: run the same graph in `mode="test"` (deterministic stubs for browser/http/fuzzer):

```powershell
curl.exe -s -X POST http://localhost:36301/api/run `
  -H "Content-Type: application/json" `
  --data-binary "@.examples/requests/run_bug_bounty_test.json"
```

Optional: to link the run to the saved workflow in run history, add `"workflow_id":"<WORKFLOW_ID>"` to the run request JSON.

3) Poll the run until it completes:

Windows (PowerShell):

```powershell
curl.exe -s http://localhost:36301/api/run/<RUN_ID>
```

Notes:
- In `mode="test"`, the system will use deterministic test doubles for several nodes.
- In `mode="simulate"`, the browser/http nodes should perform safe, non-destructive actions only.
