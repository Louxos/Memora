"""Pipeline de génération d'une fiche, exécuté en tâche de fond (QThread).

L'interface suit la progression étape par étape — jamais d'écran de
chargement vide ni d'interface figée.
"""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from memora.config.settings import Reglages
from memora.core import ia_imports
from memora.core.database import Database
from memora.core.models import Fiche
from memora.extraction.extractor import extraire
from memora.ia.generator import generer_fiche
from memora.utils.errors import MemoraError
from memora.utils.logging_setup import logger

_log = logger("pipeline")

# (identifiant, libellé affiché)
ETAPES = [
    ("lecture", "📄 Lecture du document"),
    ("extraction", "🔍 Extraction du contenu"),
    ("ocr", "👁️ Analyse des images / OCR"),
    ("analyse", "🧠 Analyse du cours par l'IA"),
    ("construction", "📝 Construction de la fiche"),
    ("forme", "🎨 Mise en forme"),
    ("sauvegarde", "💾 Sauvegarde dans la bibliothèque"),
]


class GenerationWorker(QThread):
    """Analyse un fichier et génère la fiche associée."""

    etape_changee = Signal(int, str)        # index de l'étape en cours, libellé
    etape_terminee = Signal(int)            # index d'une étape réussie
    terminee = Signal(object)               # Fiche générée
    echouee = Signal(str)                   # message d'erreur utilisateur

    def __init__(self, chemin: str, base: Database, reglages: Reglages,
                 mode: str = "complete", niveau: str = "3e",
                 matiere: str = "", chapitre: str = "", titre: str = "",
                 cle_api: str = "", parent=None):
        super().__init__(parent)
        self.chemin = chemin
        self.base = base
        self.reglages = reglages
        self.mode = mode
        self.niveau = niveau
        self.matiere = matiere
        self.chapitre = chapitre
        self.titre = titre
        self.cle_api = cle_api
        self._annule = False

    def annuler(self) -> None:
        self._annule = True

    # ------------------------------------------------------------------ exécution
    def run(self) -> None:  # noqa: C901 — déroulé volontairement lisible
        try:
            client = ia_imports.construire_client(self.cle_api, self.reglages)

            # 1) lecture du document
            self._debut(0)
            from memora.utils import files

            if not files.extension_supportee(self.chemin):
                raise MemoraError(
                    "Format non pris en charge. Choisis un PDF, un DOCX, un TXT "
                    "ou une image (JPG, PNG, WEBP)."
                )
            self._fin(0)

            # 2) extraction (OCR intégré si nécessaire → couvre l'étape 3)
            self._debut(1)
            resultat = extraire(self.chemin, client_ia=client)
            self._fin(1)
            if resultat.methode.startswith("OCR"):
                self._debut(2)
                self._fin(2)
            else:
                self._etape_ignoree(2, "non nécessaire")

            # 3) analyse IA
            self._debut(3)
            fiche = generer_fiche(
                resultat, client,
                mode=self.mode, niveau=self.niveau,
                nb_questions=self.reglages.nb_questions,
                matiere_imposee=self.matiere,
                chapitre_impose=self.chapitre,
                titre_impose=self.titre,
            )
            self._fin(3)

            # 4) construction + mise en forme
            self._debut(4)
            self._fin(4)
            self._debut(5)
            self._fin(5)

            # 5) sauvegarde
            self._debut(6)
            self.base.ajouter_fiche(fiche)
            self._fin(6)

            self.terminee.emit(fiche)
        except MemoraError as exc:
            _log.warning("Échec de génération : %s", exc.message)
            self.echouee.emit(exc.message)
        except Exception as exc:  # filet de sécurité : jamais de traceback brut
            _log.exception("Erreur inattendue pendant la génération")
            self.echouee.emit(
                "Une erreur inattendue est survenue pendant l'analyse. "
                "Réessaie, et consulte le journal (logs/memora.log) si ça persiste."
            )

    # ------------------------------------------------------------------ helpers
    def _debut(self, index: int) -> None:
        self.etape_changee.emit(index, ETAPES[index][1])

    def _fin(self, index: int) -> None:
        self.etape_terminee.emit(index)

    def _etape_ignoree(self, index: int, raison: str) -> None:
        self.etape_changee.emit(index, raison)
