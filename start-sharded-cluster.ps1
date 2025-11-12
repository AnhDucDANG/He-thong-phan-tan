Write-Host "🚀 Starting MongoDB Sharded Cluster..." -ForegroundColor Green

# Stop old containers
Write-Host "🛑 Stopping old containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.sharded.yml down

# Optional: Remove old volumes
# Write-Host "🗑️  Removing old volumes..." -ForegroundColor Yellow
# docker volume prune -f

# Start sharded cluster
Write-Host "🏗️  Building and starting sharded cluster..." -ForegroundColor Cyan
docker-compose -f docker-compose.sharded.yml up -d --build

# Wait for initialization
Write-Host "⏳ Waiting for initialization (90 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 90

# Check status
Write-Host "📊 Checking cluster status..." -ForegroundColor Cyan
docker-compose -f docker-compose.sharded.yml ps

Write-Host "`n🔍 Checking mongos router logs..." -ForegroundColor Cyan
docker logs mongos-router --tail 30

Write-Host "`n✅ Sharded cluster started!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "1. Check sharding status: .\check-sharding-status.ps1"
Write-Host "2. Test API: curl http://localhost:8000/health"
Write-Host "3. View logs: docker-compose -f docker-compose.sharded.yml logs -f"