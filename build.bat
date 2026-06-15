@echo off
REM ============================================================
REM  build.bat — Build JobApplicationAI.exe with PyInstaller
REM  Usage: double-click or run from a Command Prompt in this
REM         directory after installing dependencies.
REM ============================================================

echo.
echo =====================================================
echo   HireMe AI — PyInstaller Build Script
echo =====================================================
echo.

REM -- Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH.
    echo        Install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

REM -- Install / upgrade dependencies
echo [1/3]  Installing Python dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: pip install failed. See above for details.
    pause
    exit /b 1
)
echo        Done.
echo.

REM -- Remove old build artefacts
echo [2/3]  Cleaning previous build...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist
if exist *.spec  del /q *.spec
echo        Done.
echo.

REM -- Build the EXE
echo [3/3]  Building EXE with PyInstaller...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name JobApplicationAI ^
    --add-data "config.json;." ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed. See above for details.
    pause
    exit /b 1
)

echo.
echo =====================================================
echo   Build complete!
echo   EXE location: dist\JobApplicationAI.exe
echo =====================================================
echo.
echo IMPORTANT: Copy config.json next to the EXE before
echo            distributing or running on a new machine.
echo.
pause
