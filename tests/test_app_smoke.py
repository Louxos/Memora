"""Test de démarrage complet de l'interface (hors écran) + captures.

Vérifie que l'application démarre, navigue entre les vues, ouvre une fiche
et produise des captures PNG pour contrôle visuel.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "minimal")

from memora.config.settings import Reglages  # noqa: E402
from memora.core.demo import fiches_demo  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def fenetre(qapp, tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORA_HOME", str(tmp_path / "donnees"))

    from memora.core.database import Database
    from memora.ui.contexte import Contexte
    from memora.ui.main_window import PAGE_ACCUEIL, FenetrePrincipale

    base = Database(tmp_path / "ui.db")
    for fiche in fiches_demo():
        base.ajouter_fiche(fiche)
    contexte = Contexte(base, Reglages())
    fen = FenetrePrincipale(contexte)
    yield fen
    fen.vue_import.arreter_worker()
    base.fermer()


def capture(fenetre, nom: str) -> None:
    """Sauvegarde une capture (répertoire de travail du test : tmp)."""
    import time
    from pathlib import Path

    from PySide6.QtWidgets import QApplication

    # laisse les animations d'apparition se terminer (effet détaché ensuite)
    for _ in range(15):
        QApplication.processEvents()
        time.sleep(0.02)
    dossier = Path("captures")
    dossier.mkdir(exist_ok=True)
    fenetre.grab().save(str(dossier / f"{nom}.png"))


def test_demarrage_et_navigation(fenetre, tmp_path, monkeypatch):
    from memora.ui.main_window import (
        PAGE_BIBLIOTHEQUE,
        PAGE_EDITION,
        PAGE_FAVORIS,
        PAGE_FICHE,
        PAGE_NOUVELLE,
        PAGE_PARAMETRES,
    )

    monkeypatch.chdir(tmp_path)  # captures isolées des tests
    fenetre.show()
    assert fenetre.pile.currentIndex() == 0
    assert fenetre.contexte.base.stats()["total"] >= 2
    capture(fenetre, "01-accueil")

    fenetre.aller_a(PAGE_BIBLIOTHEQUE)
    assert fenetre.pile.currentIndex() == PAGE_BIBLIOTHEQUE
    capture(fenetre, "02-bibliotheque")

    fiches = fenetre.contexte.base.lister()
    fenetre.ouvrir_fiche(fiches[0].id)
    assert fenetre.pile.currentIndex() == PAGE_FICHE
    assert fenetre.vue_fiche.fiche is not None
    capture(fenetre, "03-fiche")

    # réponses masquées puis affichées (bouton présent dans la fiche démo)
    fenetre.vue_fiche.charge(fiches[0].id)
    capture(fenetre, "04-fiche-questions")

    fenetre.modifier_fiche(fiches[0])
    assert fenetre.pile.currentIndex() == PAGE_EDITION
    capture(fenetre, "05-edition")

    fenetre.aller_a(PAGE_NOUVELLE)
    capture(fenetre, "06-import")

    fenetre.aller_a(PAGE_FAVORIS)
    capture(fenetre, "07-favoris")

    fenetre.aller_a(PAGE_PARAMETRES)
    capture(fenetre, "08-parametres")

    # thème sombre
    fenetre.appliquer_theme_par_nom("sombre")
    fenetre.aller_a(PAGE_BIBLIOTHEQUE)
    capture(fenetre, "09-sombre")
    fenetre.appliquer_theme_par_nom("clair")


def test_edition_et_sauvegarde(fenetre):
    base = fenetre.contexte.base
    fiche = base.lister()[0]
    fenetre.vue_edition.charge(fiche)
    fenetre.vue_edition.champ_titre.setText("Titre modifié")
    fenetre.vue_edition.champ_chapitre.setText("Chapitre modifié")
    fenetre.vue_edition._enregistrer()
    relue = base.obtenir_fiche(fiche.id)
    assert relue.titre == "Titre modifié"
    assert relue.chapitre == "Chapitre modifié"
    assert relue.contenu["essentiel"]  # contenu préservé


def test_favoris_et_statut_depuis_vue(fenetre):
    base = fenetre.contexte.base
    fiche = base.lister()[0]
    fenetre.vue_fiche.charge(fiche.id)
    fenetre.vue_fiche.combo_statut.setCurrentIndex(2)  # Maîtrisée
    relue = base.obtenir_fiche(fiche.id)
    assert relue.statut == "maitrisee"
