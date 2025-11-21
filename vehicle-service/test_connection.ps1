# Test kết nối nhanh cho Vehicle Service

Write-Host "`n=== VEHICLE SERVICE CONNECTION TEST ===" -ForegroundColor Cyan

# 1. Check Tailscale
Write-Host "`n[1/6] Checking Tailscale..." -ForegroundColor Yellow
$tailscaleStatus = tailscale status 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tailscale is running" -ForegroundColor Green
    $myIP = tailscale ip -4
    Write-Host "   Your IP: $myIP" -ForegroundColor Gray
} else {
    Write-Host "❌ Tailscale not running!" -ForegroundColor Red
    Write-Host "   Please install and login to Tailscale" -ForegroundColor Red
    exit 1
}

# 2. Ping MongoDB server
Write-Host "`n[2/6] Pinging MongoDB server..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName 100.69.63.99 -Count 2 -Quiet
if ($pingResult) {
    Write-Host "✅ Can reach Lâm's server (100.69.63.99)" -ForegroundColor Green
} else {
    Write-Host "❌ Cannot reach server!" -ForegroundColor Red
    Write-Host "   Make sure Tailscale is connected" -ForegroundColor Red
    exit 1
}

# 3. Test MongoDB port
Write-Host "`n[3/6] Testing MongoDB port 27017..." -ForegroundColor Yellow
$portTest = Test-NetConnection -ComputerName 100.69.63.99 -Port 27017 -WarningAction SilentlyContinue
if ($portTest.TcpTestSucceeded) {
    Write-Host "✅ MongoDB port is open" -ForegroundColor Green
} else {
    Write-Host "❌ MongoDB port is closed!" -ForegroundColor Red
    Write-Host "   Contact Lâm to open firewall port 27017" -ForegroundColor Red
    exit 1
}

# 4. Check Docker
Write-Host "`n[4/6] Checking Docker..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker is installed: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Docker not found!" -ForegroundColor Red
    Write-Host "   Please install Docker Desktop" -ForegroundColor Red
    exit 1
}

# 5. Check Node.js
Write-Host "`n[5/6] Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Node.js is installed: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Node.js not found (OK if using Docker only)" -ForegroundColor Yellow
}

# 6. Test User Service
Write-Host "`n[6/6] Testing User Service..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://100.69.63.99:8001/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ User Service is reachable" -ForegroundColor Green
    Write-Host "   Response: $($response.StatusCode)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  User Service not reachable (may not be running yet)" -ForegroundColor Yellow
}

Write-Host "`n=== TEST COMPLETED ===" -ForegroundColor Cyan
Write-Host "`n✅ All checks passed! You're ready to run the service." -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor White
Write-Host "  1. Run: docker-compose up -d vehicle_service" -ForegroundColor Gray
Write-Host "  2. Check logs: docker-compose logs -f vehicle_service" -ForegroundColor Gray
Write-Host "  3. Test API: curl http://localhost:8002/health" -ForegroundColor Gray
Write-Host "  4. Test API: curl http://localhost:8002/api/vehicles" -ForegroundColor Gray
Write-Host ""
