"""Stockage local de la clé API.

Priorité :
 1. Trousseau système via ``keyring`` (Gestionnaire d'identifiants Windows,
    Keychain macOS, Secret Service Linux) — recommandé, chiffré par l'OS.
 2. Fichier local ``api_key.bin`` (obfuscation par clé dérivée de
    l'identifiant de la machine) — repli si aucun trousseau disponible.

La clé n'est jamais stockée dans le code source ni dans un fichier versionné.
"""

from __future__ import annotations

import base64
import hashlib
import os
import platform
from pathlib import Path

from memora.config import paths

_SERVICE = "Memora"
_USER = "mistral_api_key"

try:  # trousseau système (optionnel)
    import keyring
    from keyring.errors import KeyringError
except Exception:  # pragma: no cover - dépend de l'environnement
    keyring = None
    KeyringError = Exception


def keyring_disponible() -> bool:
    """Vérifie qu'un trousseau système utilisable est présent."""
    if keyring is None:
        return False
    try:
        back = keyring.get_keyring()
        return getattr(back, "priority", 0) > 0 or "fail" not in type(back).__name__.lower()
    except Exception:
        return False


# ---------------------------------------------------------------- repli fichier

def _fichier_cle() -> Path:
    return paths.data_dir() / "api_key.bin"


def _sel_machine() -> bytes:
    """Sel local, propre à la machine (pas de secret transportable)."""
    machine = f"{platform.node()}|{platform.system()}|{paths.data_dir()}"
    return hashlib.sha256(machine.encode("utf-8")).digest()


def _ecrire_fichier(cle: str) -> None:
    donnees = bytes(cle.encode("utf-8"))
    melange = bytes(a ^ b for a, b in zip(donnees, _sel_machine() * (len(donnees) // 32 + 1)))
    _fichier_cle().write_bytes(base64.b64encode(melange))


def _lire_fichier() -> str | None:
    fichier = _fichier_cle()
    if not fichier.is_file():
        return None
    try:
        melange = base64.b64decode(fichier.read_bytes())
        donnees = bytes(a ^ b for a, b in zip(melange, _sel_machine() * (len(melange) // 32 + 1)))
        cle = donnees.decode("utf-8")
        return cle if cle else None
    except (OSError, ValueError, UnicodeDecodeError):
        return None


# ---------------------------------------------------------------- API publique

def enregistrer_cle(cle: str) -> None:
    cle = (cle or "").strip()
    if not cle:
        supprimer_cle()
        return
    if keyring_disponible():
        try:
            keyring.set_password(_SERVICE, _USER, cle)
            _fichier_cle().unlink(missing_ok=True)
            return
        except KeyringError:
            pass  # repli fichier ci-dessous
    _ecrire_fichier(cle)


def lire_cle() -> str | None:
    """Clé enregistrée : trousseau → fichier → variable d'environnement."""
    if keyring_disponible():
        try:
            cle = keyring.get_password(_SERVICE, _USER)
            if cle:
                return cle
        except KeyringError:
            pass
    cle = _lire_fichier()
    if cle:
        return cle
    return os.environ.get("MISTRAL_API_KEY") or None


def supprimer_cle() -> None:
    if keyring_disponible():
        try:
            keyring.delete_password(_SERVICE, _USER)
        except KeyringError:
            pass
    _fichier_cle().unlink(missing_ok=True)


def source_cle() -> str:
    """D'où vient la clé active (pour l'affichage des paramètres)."""
    if keyring_disponible():
        try:
            if keyring.get_password(_SERVICE, _USER):
                return "Trousseau système"
        except KeyringError:
            pass
    if _lire_fichier():
        return "Fichier local chiffré"
    if os.environ.get("MISTRAL_API_KEY"):
        return "Variable MISTRAL_API_KEY"
    return ""
