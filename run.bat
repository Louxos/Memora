@echo off
REM ============================================================
REM  Memora — lancement (après avoir exécuté install.bat une fois)
REM ============================================================
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
    echo [Memora] Environnement introuvable : lance d'abord install.bat
    pause
    exit /b 1
)

.venv\Scripts\pythonw.exe main.py
if %errorlevel% neq 0 (
    echo [Memora] Erreur au lancement — réessai avec la console pour afficher le détail...
    .venv\Scripts\python.exe main.py
    pause
)
