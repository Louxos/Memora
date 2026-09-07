"""Génération de la fiche de révision à partir du contenu extrait.

Orchestration : extraction → consigne IA → JSON validé → objet Fiche.
"""

from __future__ import annotations

import re

from memora.core.models import Fiche, coercer_contenu, maintenant_iso
from memora.ia import prompts
from memora.ia.client import MistralClient
from memora.utils.errors import AiResponseError
from memora.utils.logging_setup import logger
from memora.extraction.extractor import ExtractionResult

_log = logger("ia.generator")


def _nettoyer_texte_ocr(texte: str) -> str:
    """Nettoie les artefacts courants des OCR (repères de position, images vides)."""
    texte = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", texte)          # images markdown
    texte = re.sub(r"\[bbox[^\]]*\]", "", texte)                 # coordonnées bbox
    texte = re.sub(r":::?\s*bbox[^\n]*", "", texte)
    texte = re.sub(r"\n{3,}", "\n\n", texte)
    return texte.strip()


def generer_fiche(
    extraction: ExtractionResult,
    client: MistralClient,
    mode: str = "complete",
    niveau: str = "3e",
    nb_questions: int = 8,
    matiere_imposee: str = "",
    chapitre_impose: str = "",
    titre_impose: str = "",
) -> Fiche:
    """Appelle l'IA et construit la fiche prête à être enregistrée."""
    texte = _nettoyer_texte_ocr(extraction.texte)
    if not texte.strip():
        raise AiResponseError(
            "Le document ne contient pas assez de texte lisible pour créer une fiche."
        )

    invitation = prompts.prompt_utilisateur(
        texte, mode, niveau, nb_questions,
        matiere_indice=matiere_imposee, titre_indice=titre_impose or "",
    )
    _log.info("Génération (mode=%s, modèle=%s, %s caractères de cours)",
              mode, client.modele, len(texte))
    brut = client.chat_json(prompts.SYSTEME, invitation)

    contenu = coercer_contenu(brut)
    if not any(contenu[s] for s in ("essentiel", "notions", "definitions", "retenir")):
        raise AiResponseError(
            "L'IA n'a pas réussi à produire une fiche exploitable à partir de ce "
            "document. Essaie un document plus lisible ou un autre mode."
        )

    titre = (titre_impose or brut.get("titre") or extraction.nom).strip()
    matiere = (matiere_imposee or brut.get("matiere") or "Sans matière").strip()
    if matiere.islower():  # « mathématiques » → « Mathématiques », « svt » → « Svt »
        matiere = matiere.title()
    chapitre = (chapitre_impose or brut.get("chapitre") or "").strip()
    niveau_final = (brut.get("niveau") or niveau or "3e").strip()

    # avertissements d'extraction reportés sur la fiche
    for avert in extraction.avertissements:
        if avert not in contenu["avertissements"]:
            contenu["avertissements"].append(avert)
    if len(extraction.texte) > prompts.MAX_CARACTERES_COURS:
        contenu["avertissements"].append(
            "Document long : la fiche a été générée à partir du début du document."
        )

    return Fiche(
        titre=titre,
        matiere=matiere,
        chapitre=chapitre,
        theme=(brut.get("theme") or "").strip(),
        niveau=niveau_final,
        contenu=contenu,
        source_nom=extraction.nom,
        source_chemin=extraction.chemin,
        source_type=extraction.categorie,
        taille_octets=extraction.taille_octets,
        mode_generation=mode,
        modele_ia=client.modele,
        date_creation=maintenant_iso(),
        date_modification=maintenant_iso(),
    )
