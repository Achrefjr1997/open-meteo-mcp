@echo off
REM ============================================
REM Quick GitHub Push Script for Open-Meteo-MCP
REM ============================================

echo.
echo ============================================
echo  Push Open-Meteo MCP to GitHub
echo ============================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo [1/8] Checking Git installation...
git --version
echo.

echo [2/8] Initializing Git repository...
git init
echo.

echo [3/8] Adding all files to Git...
git add .
echo.

echo [4/8] Checking what will be committed...
git status --short
echo.

echo [5/8] Creating initial commit...
git commit -m "Initial commit: Open-Meteo MCP Server

Features:
- 33 MCP tools for weather data
- 25 resources for reference
- 4 prompts for AI guidance  
- Docker support
- 106 passing tests
- GitHub Actions CI"
echo.

echo [6/8] Setting default branch to main...
git branch -M main
echo.

echo ============================================
echo  NEXT STEPS (Manual):
echo ============================================
echo.
echo 1. Go to https://github.com/new
echo 2. Create repository named: open-meteo-mcp
echo 3. DO NOT initialize with README/.gitignore
echo 4. Copy the commands GitHub shows you
echo.
echo Example commands GitHub will show:
echo   git remote add origin https://github.com/YOUR_USERNAME/open-meteo-mcp.git
echo   git push -u origin main
echo.
echo ============================================
echo.

set /p GITHUB_USERNAME="Enter your GitHub username: "
echo.
echo [7/8] Setting up remote (replace YOUR_USERNAME with %GITHUB_USERNAME%)...
echo.
echo Run this command manually after creating the repo:
echo   git remote add origin https://github.com/%GITHUB_USERNAME%/open-meteo-mcp.git
echo.

echo [8/8] Pushing to GitHub...
echo.
echo After creating the repository on GitHub, run:
echo   git push -u origin main
echo.
echo To add version tag:
echo   git tag -a v0.1.0 -m "Release v0.1.0"
echo   git push origin --tags
echo.

echo ============================================
echo  Script Complete!
echo ============================================
echo.
echo Your files are ready to push.
echo Full instructions are in: GITHUB_PUSH_GUIDE.md
echo.
pause
