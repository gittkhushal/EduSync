@echo off
:: setup_windows.bat — EduSync v2 one-click setup for Windows
:: Double-click this file or run it from PowerShell / CMD

echo ==============================================
echo  EduSync v2 — Windows Setup
echo ==============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://python.org
    pause & exit /b 1
)

:: Create venv if it doesn't exist
if not exist ".venv" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
)

:: Activate and install packages
echo [2/3] Installing dependencies (flask + cffi)...
call .venv\Scripts\activate.bat
pip install --quiet --upgrade flask cffi

:: cffi will auto-compile the C code on first import
:: It needs a C compiler. Check for one:
where cl >nul 2>&1
if not errorlevel 1 (
    echo [3/3] MSVC compiler found. C acceleration will be used.
) else (
    where gcc >nul 2>&1
    if not errorlevel 1 (
        echo [3/3] GCC compiler found. C acceleration will be used.
    ) else (
        echo [3/3] No C compiler found - running in pure Python mode.
        echo       (Everything works, just slightly slower.)
        echo       To get C speed: install MinGW from https://winlibs.com
        echo       and add its bin/ folder to PATH.
    )
)

echo.
echo ==============================================
echo  Setup complete! Starting EduSync...
echo  Open http://127.0.0.1:5000 in your browser
echo  Login: student / 123   or   teacher / 123
echo ==============================================
echo.

python app.py
pause
