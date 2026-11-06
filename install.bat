@echo off
REM ============================================================
REM  ARCHIVE : projet arrete le 6 novembre 2026 - version finale 1.0.0.
REM  Ce script est conserve tel quel, sans maintenance ni garantie.
REM  Memora — installation des dépendances (à faire une seule fois)
REM  Prend le Python le plus recent compatible (3.14 -> 3.13 -> 3.12)
REM  et verifie qu'il s'agit d'une version 64 bits.
REM ============================================================
cd /d "%~dp0"
echo [Memora] Projet archive le 6 novembre 2026 - version 1.0.0, sans maintenance.

REM -- choix du Python le plus recent disponible
set "CHEMIN_PY="
py -3.14 -V >nul 2>nul && if not defined CHEMIN_PY set "CHEMIN_PY=py -3.14"
py -3.13 -V >nul 2>nul && if not defined CHEMIN_PY set "CHEMIN_PY=py -3.13"
py -3.12 -V >nul 2>nul && if not defined CHEMIN_PY set "CHEMIN_PY=py -3.12"
py -3 -V >nul 2>nul && if not defined CHEMIN_PY set "CHEMIN_PY=py -3"
python -V >nul 2>nul && if not defined CHEMIN_PY set "CHEMIN_PY=python"

if not defined CHEMIN_PY goto :pas_de_python
echo [Memora] Python utilise : %CHEMIN_PY%

REM -- refus des Python 32 bits (aucune bibliotheque graphique dispo)
%CHEMIN_PY% -c "import struct; raise SystemExit(0 if struct.calcsize('P')==8 else 1)" >nul 2>nul
if %errorlevel% neq 0 goto :python_32bits

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
echo          https://www.python.org/downloads/
echo          puis relance install.bat
pause
exit /b 1

:python_32bits
echo.
echo [Memora] Ton Python est en 32 bits : les bibliotheques graphiques
echo          n'existent qu'en 64 bits. Installe Python 64 bits ici :
echo          https://www.python.org/downloads/release/python-31210/
echo          (bouton "Windows installer (64-bit)") puis relance install.bat.
echo          Les deux versions cohabitent sans danger.
pause
exit /b 1

:erreur
echo.
echo [Memora] L'installation a echoue. Copie le message affiche ci-dessus
echo          pour obtenir de l'aide.
pause
exit /b 1
