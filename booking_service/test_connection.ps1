# Script kiểm tra kết nối Booking Service với MongoDB của Lâm
# Dành cho: Ly

Write-Host "`n🔍 KIỂM TRA KẾT NỐI BOOKING SERVICE" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# 1. Kiểm tra Tailscale
Write-Host "`n📡 Bước 1: Kiểm tra Tailscale..." -ForegroundColor Yellow
$tailscaleStatus = tailscale status 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tailscale đang chạy" -ForegroundColor Green
    $myIP = tailscale ip -4
    Write-Host "   IP Tailscale của bạn: $myIP" -ForegroundColor White
} else {
    Write-Host "❌ Tailscale chưa cài đặt hoặc chưa đăng nhập" -ForegroundColor Red
    Write-Host "   Tải tại: https://tailscale.com/download" -ForegroundColor White
    exit 1
}

# 2. Ping IP của Lâm
Write-Host "`n📡 Bước 2: Ping IP máy Lâm..." -ForegroundColor Yellow
$lamIP = "100.69.63.99"
$pingResult = Test-Connection -ComputerName $lamIP -Count 2 -Quiet
if ($pingResult) {
    Write-Host "✅ Có thể ping đến $lamIP" -ForegroundColor Green
} else {
    Write-Host "❌ Không thể ping đến $lamIP" -ForegroundColor Red
    Write-Host "   Kiểm tra Tailscale network" -ForegroundColor White
    exit 1
}

# 3. Test kết nối MongoDB port 27017
Write-Host "`n📡 Bước 3: Kiểm tra MongoDB port 27017..." -ForegroundColor Yellow
$tcpTest = Test-NetConnection -ComputerName $lamIP -Port 27017 -WarningAction SilentlyContinue
if ($tcpTest.TcpTestSucceeded) {
    Write-Host "✅ Port 27017 đang mở - MongoDB có thể kết nối được!" -ForegroundColor Green
} else {
    Write-Host "❌ Port 27017 không mở" -ForegroundColor Red
    Write-Host "   Yêu cầu Lâm kiểm tra firewall và MongoDB service" -ForegroundColor White
    exit 1
}

# 4. Kiểm tra file .env
Write-Host "`n📡 Bước 4: Kiểm tra file .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ File .env tồn tại" -ForegroundColor Green
    
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "mongodb://100\.69\.63\.99:27017/rental_db") {
        Write-Host "✅ MONGO_URL đã được cấu hình đúng" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MONGO_URL chưa đúng, cần cập nhật!" -ForegroundColor Yellow
        Write-Host "   Sửa thành: MONGO_URL=mongodb://100.69.63.99:27017/rental_db" -ForegroundColor White
    }
    
    if ($envContent -match "MONGO_DB=rental_db") {
        Write-Host "✅ MONGO_DB đã đúng (rental_db)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MONGO_DB chưa đúng, cần sửa thành: rental_db" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  File .env không tồn tại" -ForegroundColor Yellow
    Write-Host "   Copy từ .env.example: Copy-Item .env.example .env" -ForegroundColor White
}

# 5. Kiểm tra Python dependencies
Write-Host "`n📡 Bước 5: Kiểm tra Python dependencies..." -ForegroundColor Yellow
$pythonCheck = python --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python đã cài đặt: $pythonCheck" -ForegroundColor Green
    
    $reqFile = "requirements.txt"
    if (Test-Path $reqFile) {
        Write-Host "✅ File requirements.txt tồn tại" -ForegroundColor Green
        Write-Host "   Để cài: pip install -r requirements.txt" -ForegroundColor White
    }
} else {
    Write-Host "⚠️  Python chưa cài đặt hoặc không trong PATH" -ForegroundColor Yellow
}

# 6. Test User Service của Lâm
Write-Host "`n📡 Bước 6: Test User Service của Lâm..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://100.69.63.99:8001/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ User Service đang chạy tốt!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  User Service chưa chạy hoặc không truy cập được" -ForegroundColor Yellow
    Write-Host "   Liên hệ Lâm để khởi động service" -ForegroundColor White
}

# 7. Hướng dẫn chạy service
Write-Host "`n🚀 Bước 7: Hướng dẫn chạy Booking Service" -ForegroundColor Yellow
Write-Host "   Chạy local:" -ForegroundColor White
Write-Host "   > cd booking_service" -ForegroundColor Gray
Write-Host "   > pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "   > uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "   Sau khi chạy, test tại:" -ForegroundColor White
Write-Host "   > http://localhost:8003" -ForegroundColor Gray
Write-Host "   > http://localhost:8003/health" -ForegroundColor Gray

# Tổng kết
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "📊 KẾT QUẢ TỔNG QUAN" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

if ($tailscaleStatus -and $pingResult -and $tcpTest.TcpTestSucceeded) {
    Write-Host "✅ TẤT CẢ KIỂM TRA CƠ BẢN ĐÃ PASS!" -ForegroundColor Green
    Write-Host "   Bạn có thể kết nối đến MongoDB của Lâm" -ForegroundColor Green
    Write-Host ""
    Write-Host "📖 Đọc hướng dẫn chi tiết tại:" -ForegroundColor Yellow
    Write-Host "   HUONG_DAN_KET_NOI_DATABASE.md" -ForegroundColor White
} else {
    Write-Host "⚠️  CÓ MỘT SỐ VẤN ĐỀ CẦN KHẮC PHỤC" -ForegroundColor Yellow
    Write-Host "   Xem lại các bước bên trên" -ForegroundColor White
}

Write-Host "`n💬 Cần hỗ trợ? Liên hệ Lâm qua Tailscale!" -ForegroundColor Cyan
Write-Host ""
