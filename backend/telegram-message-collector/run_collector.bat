@echo off
echo ===============================================
echo    Telegram Message Collector
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import telethon" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Dependencies OK!
echo.
echo Starting Telegram Message Collector...
echo.

REM Run the main script
python telegram_collector.py

echo.
echo Script completed. Press any key to exit...
pause >nul
