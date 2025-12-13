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


REM Relaunch updated app
echo ▶️ Launching updated app...
start "" "%NEW_EXE%"
echo ✅ Update complete. Enjoy the new version!
timeout /t 2 /nobreak >nul
exit /b 0
