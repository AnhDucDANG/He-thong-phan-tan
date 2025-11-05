# Team Connection Information

## Gateway Server (Leader)

### Tailscale Setup
1. Install Tailscale: https://tailscale.com/download
2. Login with account: **[Chia sẻ email/password chung]**
3. Verify connection: `tailscale ip -4`

### Server Information
- **Tailscale IP:** 100.69.63.99
- **API Gateway:** http://100.69.63.99:8000
- **User Service:** http://100.69.63.99:8001
- **MongoDB:** 100.69.63.99:27017

### JWT Configuration (CRITICAL - Must match exactly!)
```env
SECRET_KEY=35a91c468c0a8a62d3669ba143ddf1db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Testing Gateway Connection
```powershell
# Health check
curl http://100.69.63.99:8000/health

# Login
$body = @{
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri http://100.69.63.99:8000/api/users/login -Method POST -Body $body -ContentType "application/json"
$token = $response.access_token
Write-Host "Token: $token"
```

## Team Members Setup

### Member 1: Vehicle Service
- Port: 8002
- Database: PostgreSQL
- After setup, share your Tailscale IP

### Member 2: Booking Service
- Port: 8003
- Database: PostgreSQL
- After setup, share your Tailscale IP

### Member 3: Payment Service
- Port: 8004
- Database: MongoDB
- After setup, share your Tailscale IP

## Important Notes
1. All members MUST use the SAME Tailscale account
2. All services MUST use the SAME SECRET_KEY
3. Test your service health endpoint before notifying team
4. Update Gateway .env with your Tailscale IP after setup

## Troubleshooting
- Cannot connect? Check Tailscale is running: `tailscale status`
- 401 Error? Verify SECRET_KEY matches exactly
- Timeout? Check service is running: `docker-compose ps`
- Network issue? Test connectivity: `ping 100.69.63.99`