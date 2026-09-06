@echo off
REM ============================================================
REM  Memora — installation des dépendances (à faire une seule fois)
REM  Préfère Python 3.12 ou 3.13 (compatibilité des bibliothèques)
REM ============================================================
cd /d "%~dp0"

REM -- choix du meilleur Python disponible, dans l'ordre de préférence
set "CHEMIN_PY="
py -3.12 -V >nul 2>nul && if not defined CHEMIN_PY set "CHEMIN_PY=py -3.12"
py -3.13 -V >nul 2>nul && if not defined CHEMIN_PY set "CHEMIN_PY=py -3.13"
py -3 -V >nul 2>nul && if not defined CHEMIN_PY set "CHEMIN_PY=py -3"
python -V >nul 2>nul && if not defined CHEMIN_PY set "CHEMIN_PY=python"

if not defined CHEMIN_PY goto :pas_de_python
echo [Memora] Python utilise : %CHEMIN_PY%

if exist .venv (
    echo [Memora] Nettoyage de l'ancien environnement...
    rmdir /s /q .venv
)

echo [Memora] Creation de l'environnement virtuel...
%CHEMIN_PY% -m venv .venv || goto :erreur

echo [Memora] Mise a jour de pip...
.venv\Scripts\python.exe -m pip install --upgrade pip || echo [Memora] pip non mis a jour, on continue.

echo [Memora] Installation des dependances (2-3 minutes)...
.venv\Scripts\python.exe -m pip install -r requirements.txt || goto :erreur

echo.
echo [Memora] Installation terminee ! Lance Memora avec run.bat
pause
exit /b 0

:pas_de_python
echo.
echo [Memora] Python est introuvable. Installe-le depuis :
echo          https://www.python.org/downloads/release/python-31210/
echo          puis relance install.bat
pause
exit /b 1

:erreur
echo.
echo [Memora] L'installation a echoue.
echo          Si le message parle de "No matching distribution" : installe
echo          Python 3.12 ici (coexistence sans danger, rien a desinstaller) :
echo          https://www.python.org/downloads/release/python-31210/
echo          puis relance install.bat : il choisira 3.12 tout seul.
pause
exit /b 1
