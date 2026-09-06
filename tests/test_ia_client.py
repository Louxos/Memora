"""Tests du client API Mistral (contre serveur mock) : succès + toutes les erreurs."""

from __future__ import annotations

import pytest

from memora.ia.client import MistralClient
from memora.utils.errors import (
    AiResponseError,
    ApiKeyInvalidError,
    ApiKeyMissingError,
    ApiQuotaError,
)


def test_construction_sans_cle():
    with pytest.raises(ApiKeyMissingError):
        MistralClient("")


def test_tester_connexion(client_mock):
    message, modeles = client_mock.tester_connexion()
    assert "réussie" in message
    assert "mistral-small-latest" in modeles


def test_cle_invalide(serveur_mistral):
    from tests.conftest import MockMistralHandler

    MockMistralHandler.comportement = {"models": 401}
    client = MistralClient("mauvaise-cle", base_url=serveur_mistral)
    with pytest.raises(ApiKeyInvalidError):
        client.tester_connexion()


def test_quota(serveur_mistral, monkeypatch):
    client = MistralClient("cle", base_url=serveur_mistral)

    def _429(*args, **kwargs):
        class Reponse:
            status_code = 429
            text = ""

            def json(self):
                return {"message": "rate limited"}

        return Reponse()

    monkeypatch.setattr(client._session, "request", _429)
    with pytest.raises(ApiQuotaError):
        client.tester_connexion()


def test_json_robuste(client_mock):
    reponse = client_mock.chat_json("systeme", "utilisateur")
    assert reponse["titre"] == "Le théorème de Pythagore"
    assert reponse["formules"][0]["formule"].startswith("BC²")


def test_json_invalide_une_seule_relance(serveur_mistral):
    from tests.conftest import MockMistralHandler, OCR_MOCK

    MockMistralHandler.comportement = {"chat": "json_invalide"}
    client = MistralClient("cle", base_url=serveur_mistral, timeout=5)
    with pytest.raises(AiResponseError):
        client.chat_json("s", "u")
    _ = OCR_MOCK


def test_ocr(client_mock):
    texte = client_mock.ocr("data:image/png;base64,QUJD")
    assert "Pythagore" in texte


def test_pas_de_boucle_infinie_sur_erreur_reseau():
    import requests

    client = MistralClient("cle", base_url="http://127.0.0.1:1", timeout=1)
    with pytest.raises(requests.ConnectionError):
        client._session.request("GET", "http://127.0.0.1:1/v1/models", timeout=1)
