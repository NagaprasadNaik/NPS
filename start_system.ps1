# Blockchain DNS System Startup Script
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Blockchain DNS System Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting ML Security API (Port 5000)..." -ForegroundColor Green
Start-Process PowerShell -ArgumentList "-Command", "python app.py; Read-Host 'Press Enter to close'"

Write-Host ""
Write-Host "Waiting 3 seconds for ML API to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting Blockchain DNS Node (Port 5001)..." -ForegroundColor Green
Start-Process PowerShell -ArgumentList "-Command", "python server.py -p 5001; Read-Host 'Press Enter to close'"

Write-Host ""
Write-Host "Waiting 3 seconds for Blockchain node to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   System Started Successfully!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Available Interfaces:" -ForegroundColor White
Write-Host "  • Original Interface: http://127.0.0.1:5000/web" -ForegroundColor Yellow
Write-Host "  • Dashboard:          http://127.0.0.1:5001/dashboard" -ForegroundColor Yellow
Write-Host ""

Write-Host "Opening dashboard in your browser..." -ForegroundColor Green
Start-Process "http://127.0.0.1:5001/dashboard"

Write-Host ""
Write-Host "Press any key to add sample data..." -ForegroundColor Magenta
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Adding sample DNS records..." -ForegroundColor Green
python test_dashboard.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Both services are running. You can now:" -ForegroundColor White
Write-Host "  1. Use the original interface for domain checking" -ForegroundColor Yellow
Write-Host "  2. Use the dashboard for blockchain management" -ForegroundColor Yellow
Write-Host "  3. Add DNS records through the management panel" -ForegroundColor Yellow
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Magenta
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
