<#
.SYNOPSIS
    Start development environment with exposed ports
.DESCRIPTION
    Starts all services with ports exposed for debugging and MongoDB Compass
#>

Write-Host "🚀 Starting Development Environment" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

# Stop existing containers
Write-Host "`n📦 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down 2>$null

# Start services
Write-Host "`n🔨 Building and starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml --env-file .env up -d --build

# Wait for services to be healthy
Write-Host "`n⏳ Waiting for services to be healthy (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check status
Write-Host "`n📊 Service Status:" -ForegroundColor Green
docker-compose -f docker-compose.dev.yml ps

# Test services
Write-Host "`n🧪 Testing Services:" -ForegroundColor Green

# Test Gateway
Write-Host "  Gateway (http://localhost:8000)..." -ForegroundColor Gray
try {
    $gw = Invoke-RestMethod http://localhost:8000/health -TimeoutSec 5
    Write-Host "  ✅ Gateway: $($gw.status)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Gateway failed" -ForegroundColor Red
}

# Test User Service
Write-Host "  User Service (http://localhost:8001)..." -ForegroundColor Gray
try {
    $us = Invoke-RestMethod http://localhost:8001/health -TimeoutSec 5
    Write-Host "  ✅ User Service: $($us.status)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ User Service failed" -ForegroundColor Red
}

# Test MongoDB
Write-Host "  MongoDB (localhost:27017)..." -ForegroundColor Gray
$mongo = Test-NetConnection -ComputerName localhost -Port 27017 -WarningAction SilentlyContinue
if ($mongo.TcpTestSucceeded) {
    Write-Host "  ✅ MongoDB: Accessible" -ForegroundColor Green
} else {
    Write-Host "  ❌ MongoDB: Not accessible" -ForegroundColor Red
}

# Show useful URLs
Write-Host "`n📝 Development URLs:" -ForegroundColor Cyan
Write-Host "  🌐 API Gateway:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "  🌐 User Service:    http://localhost:8001/docs" -ForegroundColor White
Write-Host "  🍃 MongoDB Compass: mongodb://localhost:27017" -ForegroundColor White

Write-Host "`n✅ Development environment ready!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Gray

# Show commands
Write-Host "`n💡 Useful commands:" -ForegroundColor Yellow
Write-Host "  Stop:      docker-compose -f docker-compose.dev.yml down" -ForegroundColor Gray
Write-Host "  Logs:      docker-compose -f docker-compose.dev.yml logs -f" -ForegroundColor Gray
Write-Host "  Restart:   .\dev.ps1" -ForegroundColor Gray