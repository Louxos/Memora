"""Tests de la génération de fiche (client mocké) et du pipeline complet."""

from __future__ import annotations

import pytest

from memora.config.settings import Reglages
from memora.extraction.extractor import extraire


def test_generation_fiche_complete(exemples, client_mock):
    from memora.ia.generator import generer_fiche

    extraction = extraire(exemples["pdf"], client_ia=client_mock)
    fiche = generer_fiche(extraction, client_mock, mode="complete", niveau="3e", nb_questions=8)

    assert fiche.titre == "Le théorème de Pythagore"
    assert fiche.matiere == "Mathématiques"
    assert fiche.contenu["formules"]
    assert fiche.contenu["methodes"][0]["etapes"]
    assert fiche.mode_generation == "complete"
    assert fiche.source_nom == exemples["pdf"].name


def test_generation_matiere_imposee(exemples, client_mock):
    from memora.ia.generator import generer_fiche

    extraction = extraire(exemples["txt"], client_ia=client_mock)
    fiche = generer_fiche(extraction, client_mock, matiere_imposee="SVT", titre_impose="Mon titre")
    assert fiche.matiere == "SVT"
    assert fiche.titre == "Mon titre"


def test_generation_fiche_trop_pauvre(serveur_mistral, exemples):
    from tests.conftest import MockMistralHandler

    from memora.ia.client import MistralClient
    from memora.ia.generator import generer_fiche
    from memora.utils.errors import AiResponseError

    MockMistralHandler.comportement = {"chat": "incomplet"}
    client = MistralClient("cle", base_url=serveur_mistral)
    extraction = extraire(exemples["txt"], client_ia=client)
    with pytest.raises(AiResponseError):
        generer_fiche(extraction, client)


def test_pipeline_complet_hors_interface(exemples, client_mock, base_vierge, monkeypatch):
    """Pipeline complet (fichier → fiche enregistrée), sans Qt."""
    from memora.core import pipeline

    reglages = Reglages()
    worker = pipeline.GenerationWorker(
        chemin=str(exemples["pdf"]), base=base_vierge, reglages=reglages,
        mode="brevet", cle_api="cle-de-test",
    )

    # injecte le client mocké à la place du client réel
    import memora.core.ia_imports as module_ia

    monkeypatch.setattr(module_ia, "construire_client", lambda cle, r: client_mock)

    evenements = {"terminee": None, "echouee": None}
    worker.terminee.connect(lambda fiche: evenements.__setitem__("terminee", fiche))
    worker.echouee.connect(lambda message: evenements.__setitem__("echouee", message))
    worker.run()  # exécution synchrone (pas besoin de boucle d'événements)

    assert evenements["echouee"] is None, evenements["echouee"]
    fiche = evenements["terminee"]
    assert fiche.id is not None
    assert base_vierge.obtenir_fiche(fiche.id).titre == "Le théorème de Pythagore"


def test_pipeline_document_invalide(base_vierge, monkeypatch, tmp_path):
    from memora.core import pipeline
    from memora.config.settings import Reglages

    mauvais = tmp_path / "fichier.xyz"
    mauvais.write_text("x", encoding="utf-8")

    worker = pipeline.GenerationWorker(
        chemin=str(mauvais), base=base_vierge, reglages=Reglages(), cle_api="cle",
    )
    erreurs = []
    worker.echouee.connect(erreurs.append)
    worker.run()
    assert erreurs and "non pris en charge" in erreurs[0]
