# Run from repository root in PowerShell before the lab.
$ErrorActionPreference = 'Continue'
Write-Host 'GUARDIAN-X preflight'
foreach ($app in @('python', 'node', 'npm', 'docker')) {
    $command = Get-Command $app -ErrorAction SilentlyContinue
    if ($command) { Write-Host "OK: $app ($($command.Source))" }
    else { Write-Warning "Missing: $app" }
}
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker info --format 'Docker daemon: {{.ServerVersion}}' 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Warning 'Docker Desktop is not running' }
}
foreach ($path in @('backend\app\.env', 'deployment\influxdb\.env', 'backend\.venv\Scripts\python.exe', 'frontend\node_modules')) {
    if (Test-Path $path) { Write-Host "OK: $path" }
    else { Write-Warning "Prepare before lab: $path" }
}
Write-Host 'Network interfaces for packet capture:'
if (Get-Command python -ErrorAction SilentlyContinue) {
    python -c 'from scapy.all import show_interfaces; show_interfaces()' 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Warning 'Scapy unavailable; install backend requirements first' }
}
Write-Host 'Verify Arduino IDE, ESP32 board package, USB driver, and PubSubClient library manually.'
