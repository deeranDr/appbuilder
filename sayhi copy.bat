@REM @echo off
@REM echo Hi deeran
@REM pause

@echo off
title Premedia Updater
echo ==========================================
echo     🚀 Premedia App Updater
echo ==========================================

REM %1 = new exe path (temporary file)
REM %2 = old exe path (installed file)

set NEW_EXE=%1
set OLD_EXE=%2

echo 🔄 Preparing to update...
echo Old EXE: %OLD_EXE%
echo New EXE: %NEW_EXE%

REM Kill any running instance of the app
echo 🔪 Closing running app if open...
taskkill /f /im "PremediaApp.exe" >nul 2>&1
timeout /t 2 /nobreak >nul

REM Delete old EXE
echo 🗑 Removing old version...
del "%OLD_EXE%" /f /q
if exist "%OLD_EXE%" (
    echo ❌ Failed to delete old EXE. File still locked.
    pause
    exit /b 1
)

REM Move new EXE in place
echo 📦 Installing new version...
move /y "%NEW_EXE%" "%OLD_EXE%"
if errorlevel 1 (
    echo ❌ Failed to move new file.
    pause
    exit /b 1
)

REM Relaunch updated app
echo ▶️ Launching updated app...
start "" "%OLD_EXE%"
echo ✅ Update complete. Enjoy the new version!
timeout /t 2 /nobreak >nul
exit /b 0
