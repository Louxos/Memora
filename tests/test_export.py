"""Tests d'export : Markdown et PDF (rendu hors écran, sans imprimante)."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "minimal")

from memora.core.models import Fiche  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def fiche_exemple():
    return Fiche(
        titre="Le théorème de Pythagore",
        matiere="Mathématiques", chapitre="Géométrie", niveau="3e",
        contenu={
            "objectif": "Appliquer Pythagore et sa réciproque.",
            "essentiel": ["BC² = AB² + AC²", "L'hypoténuse est le plus long côté."],
            "notions": [{"nom": "Hypoténuse", "explication": "Côté opposé à l'angle droit.", "exemple": ""}],
            "definitions": [{"terme": "Théorème", "definition": "Égalité dans un triangle **rectangle**."}],
            "formules": [{"formule": "BC² = AB² + AC²", "signification": "côtés du triangle", "unite": "cm", "conditions": "triangle rectangle", "exemple": "3-4-5"}],
            "methodes": [{"titre": "Calculer un côté", "etapes": ["Vérifier l'angle droit", "Appliquer la formule"]}],
            "dates_personnages": [],
            "exemples": ["AB=3, AC=4 → BC=5"],
            "pieges": ["Pythagore exige un triangle rectangle."],
            "retenir": ["Toujours vérifier l'angle droit."],
            "questions": [{"question": "Énonce le théorème.", "reponse": "Carré de l'hypoténuse = somme des carrés.", "type": "définition"}],
            "avertissements": [],
        },
    )


def test_markdown(fiche_exemple):
    from memora.export.markdown_export import fiche_vers_markdown

    md = fiche_vers_markdown(fiche_exemple)
    assert "# Le théorème de Pythagore" in md
    assert "## Formules & règles" in md
    assert "## Méthodes" in md
    assert "→ *Carré de l'hypoténuse" in md          # réponse incluse
    sans = fiche_vers_markdown(fiche_exemple, inclure_reponses=False)
    assert "Carré de l'hypoténuse" not in sans


def test_markdown_sections_vides_absentes(fiche_exemple):
    from memora.export.markdown_export import fiche_vers_markdown

    md = fiche_vers_markdown(fiche_exemple)
    assert "Dates" not in md                          # section absente car vide


def test_pdf(qapp, fiche_exemple, tmp_path):
    from memora.export.pdf_export import exporter_pdf

    sortie = tmp_path / "fiche.pdf"
    chemin = exporter_pdf(fiche_exemple, sortie)
    assert chemin.exists()
    contenu = sortie.read_bytes()
    assert contenu.startswith(b"%PDF-")
    assert len(contenu) > 8000                         # plusieurs pages de mise en page


def test_html(fiche_exemple):
    from memora.export.html_export import fiche_vers_html

    html = fiche_vers_html(fiche_exemple)
    assert "<!DOCTYPE html>" in html
    assert "Pythagore" in html
    assert "background" in html.lower()               # mise en page colorée
