"""Contexte applicatif partagé entre les vues (base, réglages, signaux)."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from memora.config.settings import Reglages
from memora.core.database import Database
from memora.ia.client import MistralClient
from memora.utils.logging_setup import logger

_log = logger("ui.contexte")


class Contexte(QObject):
    """Regroupe les services de l'application et les signaux globaux."""

    bibliotheque_changee = Signal()      # une fiche a été créée / modifiée / supprimée
    theme_change = Signal(str)           # nouveau nom de thème appliqué
    reglages_changes = Signal()

    def __init__(self, base: Database, reglages: Reglages, parent=None):
        super().__init__(parent)
        self.base = base
        self.reglages = reglages
        self.theme_actuel = "clair"

    # ------------------------------------------------------------ clé API / client
    def cle_api(self) -> str:
        from memora.config import secure_storage

        return secure_storage.lire_cle() or ""

    def enregistrer_cle(self, cle: str) -> None:
        from memora.config import secure_storage

        secure_storage.enregistrer_cle(cle)

    def effacer_cle(self) -> None:
        from memora.config import secure_storage

        secure_storage.supprimer_cle()

    def client_ia(self) -> MistralClient | None:
        """Client prêt à l'emploi, ou None si aucune clé n'est configurée."""
        from memora.core.ia_imports import construire_client

        return construire_client(self.cle_api(), self.reglages)

    def cle_configures(self) -> bool:
        return bool(self.cle_api())

    # ------------------------------------------------------------ réglages
    def sauver_reglages(self) -> None:
        from memora.config.settings import enregistrer_reglages

        enregistrer_reglages(self.reglages)
        self.reglages_changes.emit()
