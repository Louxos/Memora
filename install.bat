@echo off
REM ============================================================
REM  Memora — installation des dépendances (à faire une seule fois)
REM ============================================================
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set PY=py -3
) else (
    set PY=python
)

echo [Memora] Creation de l'environnement virtuel...
%PY% -m venv .venv || goto :erreur

echo [Memora] Mise a jour de pip...
.venv\Scripts\python.exe -m pip install --upgrade pip || echo [Memora] pip deja a jour, on continue.

echo [Memora] Installation des dependances (2-3 minutes)...
.venv\Scripts\python.exe -m pip install -r requirements.txt || goto :erreur

echo.
echo [Memora] Installation terminee ! Lance Memora avec run.bat
pause
exit /b 0

:erreur
echo.
echo [Memora] L'installation a echoue. Ouvre une invite de commandes ici
echo          (maj+clic droit sur le dossier ^> "Ouvrir la fenetre PowerShell")
echo          et envoie la trace a ton aide, ou essaie :
echo          .venv\Scripts\python.exe -m pip install -r requirements.txt
pause
exit /b 1
