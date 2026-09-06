"""Tests du modèle de données (contenu de fiche, coercition, sections)."""

from __future__ import annotations

from memora.core.models import (
    Fiche,
    coercer_contenu,
    contenu_est_vide,
    sections_remplies,
)


def test_coercion_champs_manquants():
    contenu = coercer_contenu({"titre_x": "ignoré", "essentiel": [" Idée 1 ", "", None]})
    assert contenu["essentiel"] == ["Idée 1"]
    assert contenu["notions"] == []
    assert contenu["objectif"] == ""


def test_coercion_types_bizarres():
    contenu = coercer_contenu({
        "definitions": [{"terme": "Pythagore", "definition": "…"}, "pas un dict", {}],
        "questions": [{"question": "Q?", "reponse": "R."}],
        "dates_personnages": [{"type": "Date importante", "nom": "1914", "info": "x"}],
        "methodes": [{"titre": "M", "etapes": ["a", "b"]}],
    })
    assert len(contenu["definitions"]) == 1
    assert contenu["questions"][0]["type"] == "mémorisation"
    assert contenu["dates_personnages"][0]["type"] == "date"
    assert contenu["methodes"][0]["etapes"] == ["a", "b"]


def test_sections_adaptatives():
    contenu = coercer_contenu({"essentiel": ["a"], "retenir": ["b"]})
    cles = [cle for cle, _, _ in sections_remplies(contenu)]
    assert "essentiel" in cles and "retenir" in cles
    assert "formules" not in cles          # section absente car vide
    assert "definitions" not in cles
    assert not contenu_est_vide(contenu)


def test_fiche_aller_retour_bdd():
    fiche = Fiche(titre="Test", matiere="SVT", contenu={"essentiel": ["x"]})
    ligne = fiche.vers_ligne()
    fiche2 = Fiche.depuis_ligne(ligne)
    assert fiche2.titre == "Test"
    assert fiche2.contenu["essentiel"] == ["x"]
    assert fiche2.statut == "a_apprendre"
