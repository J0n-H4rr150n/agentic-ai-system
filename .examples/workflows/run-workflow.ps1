# Quick test script for Trading Platform workflow
# Usage: .\run-workflow.ps1 [test|simulate|run]

param(
    [Parameter(Position=0)]
    [ValidateSet("test", "simulate", "run")]
    [string]$Mode = "test"
)

Write-Host "🚀 Running Trading Platform Exploration Workflow in '$Mode' mode..." -ForegroundColor Cyan

# Read workflow file
$workflowPath = ".examples\workflows\trading_platform_exploration.json"
if (-not (Test-Path $workflowPath)) {
    Write-Error "Workflow file not found: $workflowPath"
    exit 1
}

$workflow = Get-Content $workflowPath -Raw | ConvertFrom-Json

# Create request body
$body = @{
    graph = $workflow
    mode = $Mode
} | ConvertTo-Json -Depth 10

# Start the run
Write-Host "📡 Sending request to backend API..." -ForegroundColor Yellow
$response = Invoke-RestMethod -Method Post -Uri "http://localhost:36301/api/run" `
    -ContentType "application/json" -Body $body

$runId = $response.run_id
Write-Host "✅ Run started! Run ID: $runId" -ForegroundColor Green
Write-Host ""

# Poll for completion
Write-Host "⏳ Polling for results..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

do {
    Start-Sleep -Seconds 2
    $attempt++

    $status = Invoke-RestMethod -Uri "http://localhost:36301/api/run/$runId"
    Write-Host "  Status: $($status.status) (attempt $attempt/$maxAttempts)" -ForegroundColor Gray

    if ($status.status -in @("completed", "failed", "cancelled")) {
        break
    }
} while ($attempt -lt $maxAttempts)

# Display results
Write-Host ""
Write-Host "📊 Final Status: $($status.status)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Steps executed: $($status.trace.Count)" -ForegroundColor Cyan
Write-Host ""

foreach ($step in $status.trace) {
    $icon = if ($step.status -eq "completed") { "✅" } elseif ($step.status -eq "failed") { "❌" } else { "⏸️" }
    Write-Host "$icon Step $($step.step_id): $($step.node_type) - $($step.duration_ms)ms" -ForegroundColor White
}

# Show final output if available
if ($status.trace.Count -gt 0) {
    $lastStep = $status.trace[-1]
    Write-Host ""
    Write-Host "📄 Final Output:" -ForegroundColor Magenta
    Write-Host ($lastStep.output | ConvertTo-Json -Depth 5) -ForegroundColor White
}

Write-Host ""
Write-Host "🔗 View full trace: http://localhost:36300" -ForegroundColor Cyan
Write-Host "🔗 API endpoint: http://localhost:36301/api/run/$runId" -ForegroundColor Cyan
