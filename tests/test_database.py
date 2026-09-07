"""Tests de la base SQLite : CRUD, recherche, filtres, tri, sauvegarde."""

from __future__ import annotations

from memora.core.models import Fiche, maintenant_iso


def _fiche(titre, matiere, chapitre, **kwargs):
    return Fiche(
        titre=titre, matiere=matiere, chapitre=chapitre,
        contenu={"essentiel": ["idée"], "questions": [{"question": "Q", "reponse": "R", "type": "mémorisation"}]},
        date_creation=maintenant_iso(),
        **kwargs,
    )


def test_crud_complet(base_vierge):
    base = base_vierge
    fiche = _fiche("Verdun", "Histoire", "Première Guerre mondiale")
    identifiant = base.ajouter_fiche(fiche)
    assert identifiant > 0

    lue = base.obtenir_fiche(identifiant)
    assert lue.titre == "Verdun"
    assert lue.contenu["essentiel"] == ["idée"]

    lue.titre = "Verdun 1916"
    lue.statut = "maitrisee"
    base.maj_fiche(lue)
    relue = base.obtenir_fiche(identifiant)
    assert relue.titre == "Verdun 1916" and relue.statut == "maitrisee"

    base.supprimer_fiche(identifiant)
    assert base.obtenir_fiche(identifiant) is None


def test_recherche_et_filtres(base_vierge):
    base = base_vierge
    base.ajouter_fiche(_fiche("Verdun", "Histoire", "Guerre 14-18"))
    base.ajouter_fiche(_fiche("Pythagore", "Mathématiques", "Géométrie", favori=True))
    base.ajouter_fiche(_fiche("Thalès", "Mathématiques", "Géométrie", statut="a_revoir"))

    assert len(base.lister()) == 3
    assert len(base.lister(matiere="Mathématiques")) == 2
    assert len(base.lister(chapitre="Géométrie")) == 2
    assert len(base.lister(favori=True)) == 1
    assert len(base.lister(statut="a_revoir")) == 1

    trouve = base.lister(recherche="pythagore")
    assert len(trouve) == 1 and trouve[0].titre == "Pythagore"
    introuvable = base.lister(recherche="photosynthèse")
    assert introuvable == []


def test_tri(base_vierge):
    base = base_vierge
    import time

    for titre in ("Aaa", "Bbb"):
        fiche = _fiche(titre, "Français", "x")
        base.ajouter_fiche(fiche)
        time.sleep(1.1)  # dates ISO à la seconde
    recents = [f.titre for f in base.lister(tri="recent")]
    anciens = [f.titre for f in base.lister(tri="ancien")]
    alphabet = [f.titre for f in base.lister(tri="alpha")]
    assert recents == list(reversed(anciens))
    assert alphabet == ["Aaa", "Bbb"]


def test_matiere_chapitre_stats(base_vierge):
    base = base_vierge
    base.ajouter_fiche(_fiche("V", "Histoire", "Guerre 14-18"))
    base.ajouter_fiche(_fiche("P", "Mathématiques", "Géométrie", favori=True, statut="maitrisee"))
    assert base.matieres() == ["Histoire", "Mathématiques"]
    assert base.chapitres("Mathématiques") == ["Géométrie"]
    stats = base.stats()
    assert stats["total"] == 2 and stats["favoris"] == 1 and stats["maitrisees"] == 1


def test_export_import(base_vierge, tmp_path):
    base = base_vierge
    base.ajouter_fiche(_fiche("V", "Histoire", "Guerre"))
    sauvegarde = tmp_path / "sauvegarde.json"
    assert base.exporter_bibliotheque(sauvegarde) == 1

    import json

    contenu = json.loads(sauvegarde.read_text(encoding="utf-8"))
    assert contenu["format"] == "memora-bibliotheque"
    assert base.importer_bibliotheque(sauvegarde) == 1
    assert len(base.lister()) == 2


def test_revision(base_vierge):
    base = base_vierge
    identifiant = base.ajouter_fiche(_fiche("V", "Histoire", "G"))
    base.marquer_revision(identifiant)
    base.marquer_revision(identifiant)
    fiche = base.obtenir_fiche(identifiant)
    assert fiche.nb_vues == 2 and fiche.derniere_revision
