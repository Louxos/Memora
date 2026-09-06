@echo off
REM ============================================================
REM  Memora — installation des dépendances (à faire une seule fois)
REM ============================================================
where py >nul 2>nul
if %errorlevel%==0 (
    set PY=py -3
) else (
    set PY=python
)

echo [Memora] Creation de l'environnement virtuel...
%PY% -m venv .venv || goto :erreur

echo [Memora] Installation des dependances...
call .venv\Scripts\pip install --upgrade pip || goto :erreur
call .venv\Scripts\pip install -r requirements.txt || goto :erreur

echo.
echo [Memora] Installation terminee ! Lance Memora avec run.bat
pause
exit /b 0

:erreur
echo.
echo [Memora] Une erreur est survenue. Verifie que Python 3.10+ est installe
echo          depuis https://www.python.org/downloads/ (coche "Add to PATH").
pause
exit /b 1
