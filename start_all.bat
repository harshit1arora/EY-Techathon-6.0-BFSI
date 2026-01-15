@echo off
echo ================================================
echo  Starting NBFC Loan Assistant - Complete System
echo ================================================

echo.
echo [1/3] Starting MCP Server...
start cmd /k "title MCP Server && cd /d %~dp0 && python MCPServer\server.py"

echo Waiting for MCP to start...
timeout /t 5 /nobreak >nul

echo.
echo [2/3] Starting API Server...
start cmd /k "title API Server && cd /d %~dp0 && python api.py"

echo Waiting for API to start...
timeout /t 8 /nobreak >nul

echo.
echo [3/3] Starting Test Console...
echo ================================================
echo  Services started successfully!
echo  MCP Server:  http://127.0.0.1:8000
echo  API Server:  http://127.0.0.1:8083
echo  Test Client: python test_client.py
echo  Auto Test:   python verify_flow.py
echo ================================================
echo.
echo Choose an option:
echo  1. Run manual test (test_client.py)
echo  2. Run automated test (verify_flow.py)
echo  3. Run quick test (quick_test.py)
echo  4. Exit
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    start cmd /k "title Test Client && cd /d %~dp0 && python test_client.py"
) else if "%choice%"=="2" (
    start cmd /k "title Auto Test && cd /d %~dp0 && python verify_flow.py"
) else if "%choice%"=="3" (
    start cmd /k "title Quick Test && cd /d %~dp0 && python quick_test.py"
)

echo.
echo Press any key to exit this window...
pause >nul