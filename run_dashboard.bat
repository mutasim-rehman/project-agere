@echo off
title Project Agere Dashboard
echo Starting Project Agere Analytics Dashboard...
python run_dashboard.py
if errorlevel 1 (
    echo.
    echo Python was not found in PATH or failed to start.
    echo Trying py launcher...
    py run_dashboard.py
)
pause

