"""Résolution des chemins de données de Memora.

Toutes les données (base SQLite, réglages, logs, exports) vivent dans un
répertoire utilisateur dédié, créé automatiquement au premier lancement :
  - Windows : %APPDATA%\\Memora
  - macOS   : ~/Library/Application Support/Memora
  - Linux   : $XDG_DATA_HOME/Memora ou ~/.local/share/Memora
La variable d'environnement MEMORA_HOME permet de tout rediriger
(utile pour les tests).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ENV_OVERRIDE = "MEMORA_HOME"


def _base_dir() -> Path:
    override = os.environ.get(_ENV_OVERRIDE)
    if override:
        base = Path(override)
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        base = Path(appdata) / "Memora"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "Memora"
    else:
        xdg = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg) / "Memora" if xdg else Path.home() / ".local" / "share" / "Memora"
    base.mkdir(parents=True, exist_ok=True)
    return base


def data_dir() -> Path:
    """Répertoire racine des données Memora."""
    return _base_dir()


def database_path() -> Path:
    return data_dir() / "memora.db"


def settings_path() -> Path:
    return data_dir() / "settings.json"


def logs_dir() -> Path:
    d = data_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def exports_dir() -> Path:
    d = data_dir() / "exports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def app_root_dir() -> Path:
    """Répertoire contenant l'application (main.py)."""
    return Path(__file__).resolve().parent.parent
