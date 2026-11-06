@echo off
REM ============================================================
REM  ARCHIVE : projet arrete le 6 novembre 2026 - version finale 1.0.0.
REM  Memora — lancement (après avoir exécuté install.bat une fois)
REM ============================================================
cd /d "%~dp0"
echo [Memora] Projet archive le 6 novembre 2026 - aucune maintenance.

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
