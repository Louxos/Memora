"""Réglages persistants de Memora (<données>/settings.json)."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field

from memora.config import paths

MODES = {
    "rapide": "⚡ Rapide",
    "complete": "📚 Complète",
    "brevet": "🎯 Brevet",
    "active": "🧠 Active",
}

THEMES = ("systeme", "clair", "sombre")

NIVEAUX = ["6e", "5e", "4e", "3e", "2nde", "1re", "Terminale"]

MODELES_CONNUS = ["mistral-small-latest", "mistral-large-latest"]


@dataclass
class Reglages:
    """Préférences de l'application."""

    fournisseur: str = "mistral"
    modele: str = "mistral-small-latest"
    niveau: str = "3e"
    mode_defaut: str = "complete"
    nb_questions: int = 8
    theme: str = "systeme"          # systeme | clair | sombre
    premiere_lancement: bool = True
    demo_charge: bool = False

    # ---------------------------------------------------------------- (dé)sérialisation
    def vers_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def depuis_dict(cls, data: dict) -> "Reglages":
        r = cls()
        for champ in ("fournisseur", "modele", "niveau", "mode_defaut", "theme"):
            val = data.get(champ)
            if isinstance(val, str) and val:
                setattr(r, champ, val)
        nb = data.get("nb_questions")
        if isinstance(nb, (int, float)) and 3 <= nb <= 15:
            r.nb_questions = int(nb)
        r.premiere_lancement = bool(data.get("premiere_lancement", True))
        r.demo_charge = bool(data.get("demo_charge", False))
        return r


def charger_reglages() -> Reglages:
    fichier = paths.settings_path()
    if fichier.is_file():
        try:
            return Reglages.depuis_dict(json.loads(fichier.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass  # réglages corrompus → valeurs par défaut
    return Reglages()


def enregistrer_reglages(r: Reglages) -> None:
    fichier = paths.settings_path()
    try:
        fichier.write_text(
            json.dumps(r.vers_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        pass


def charger_env() -> None:
    """Charge un éventuel fichier .env placé à côté de l'application.

    Ne remplace jamais une variable d'environnement déjà définie.
    """
    for base in (paths.app_root_dir(), paths.data_dir()):
        env = base / ".env"
        if not env.is_file():
            continue
        try:
            for ligne in env.read_text(encoding="utf-8").splitlines():
                ligne = ligne.strip()
                if not ligne or ligne.startswith("#") or "=" not in ligne:
                    continue
                cle, _, valeur = ligne.partition("=")
                cle, valeur = cle.strip(), valeur.strip().strip('"').strip("'")
                if cle and cle not in os.environ:
                    os.environ[cle] = valeur
        except OSError:
            continue
