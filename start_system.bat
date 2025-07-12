@echo off
echo.
echo ========================================
echo   Blockchain DNS System Startup
echo ========================================
echo.

echo Starting ML Security API (Port 5000)...
start "ML Security API" cmd /k "python app.py"

echo.
echo Waiting 3 seconds for ML API to start...
timeout /t 3 /nobreak > nul

echo.
echo Starting Blockchain DNS Node (Port 5001)...
start "Blockchain DNS Node" cmd /k "python server.py -p 5001"

echo.
echo Waiting 3 seconds for Blockchain node to start...
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo   System Started Successfully!
echo ========================================
echo.
echo Available Interfaces:
echo   • Original Interface: http://127.0.0.1:5000/web
echo   • Dashboard:          http://127.0.0.1:5001/dashboard
echo.
echo Opening dashboard in your browser...
start http://127.0.0.1:5001/dashboard

echo.
echo Press any key to add sample data...
pause > nul

echo.
echo Adding sample DNS records...
python test_dashboard.py

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Both services are running. You can now:
echo   1. Use the original interface for domain checking
echo   2. Use the dashboard for blockchain management
echo   3. Add DNS records through the management panel
echo.
echo Press any key to exit...
pause > nul
