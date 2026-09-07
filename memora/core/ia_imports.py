"""Petits ponts entre modules (évite les imports circulaires)."""

from __future__ import annotations

from memora.config.settings import Reglages
from memora.ia.client import MistralClient


def construire_client(cle_api: str, reglages: Reglages) -> MistralClient | None:
    """Fabrique un client IA si une clé est disponible, sinon None.

    None est acceptable : l'extraction de texte fonctionne sans IA ;
    l'OCR et la génération leveront alors une erreur claire.
    """
    cle = (cle_api or "").strip()
    if not cle:
        return None
    return MistralClient(cle_api=cle, modele=reglages.modele)
