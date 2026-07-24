@echo off
setlocal
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
  echo Git is not installed or is not available in PATH.
  echo Install Git for Windows or use GitHub Desktop.
  pause
  exit /b 1
)

if not exist ".git" git init

git add .
git commit -m "Initial release of Site Health Auditor"
git branch -M main

git remote remove origin >nul 2>nul
git remote add origin https://github.com/Mohantunde/site-health-auditor.git

echo.
echo Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
  echo.
  echo Push failed. Confirm that:
  echo 1. The GitHub repository exists and is empty.
  echo 2. You are signed in to the correct GitHub account.
  echo 3. Git Credential Manager is installed.
  pause
  exit /b 1
)

echo.
echo Upload completed successfully.
pause
