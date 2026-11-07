@echo off
setlocal
rem Clear generated SolidCraft outputs in this project. Use -DryRun to preview.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0components\solidcraft_cleanup\working.ps1" -ProjectRoot "%~dp0." %*
exit /b %errorlevel%
