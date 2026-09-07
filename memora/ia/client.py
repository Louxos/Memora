"""Client HTTP de l'API Mistral.

Points d'entrée utilisés :
  - GET  /v1/models             → test de connexion
  - POST /v1/chat/completions   → génération des fiches (JSON garanti)
  - POST /v1/ocr                → OCR des images / PDF scannés

Gestion d'erreurs volontairement stricte : messages clairs, jamais de
tentatives infinies (au maximum une nouvelle tentative pour les erreurs
réseau / serveur, aucune pour une clé invalide).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

from memora.utils.errors import (
    AiResponseError,
    ApiKeyInvalidError,
    ApiQuotaError,
    ApiUnavailableError,
    DocumentTooLargeError,
    NetworkError,
)
from memora.utils.logging_setup import logger

_log = logger("ia.client")

BASE_URL_DEFAUT = "https://api.mistral.ai"
TAILLE_MAX_BASE64 = 30 * 1024 * 1024  # limite API pour les contenus base64


class MistralClient:
    """Client minimal et robuste pour les besoins de Memora."""

    def __init__(self, cle_api: str, modele: str = "mistral-small-latest",
                 base_url: str = BASE_URL_DEFAUT, timeout: int = 180):
        if not cle_api:
            from memora.utils.errors import ApiKeyMissingError

            raise ApiKeyMissingError(
                "Aucune clé API Mistral n'est configurée. Ouvre les paramètres "
                "pour renseigner ta clé."
            )
        self.cle_api = cle_api
        self.modele = modele
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {cle_api}"})

    # ------------------------------------------------------------ bas niveau
    def _requete(self, methode: str, chemin: str, payload: dict | None = None,
                 tentatives: int = 2) -> requests.Response:
        """Exécute une requête, avec au plus ``tentatives`` essais pour le réseau."""
        derniere_erreur: Exception | None = None
        for essai in range(tentatives):
            try:
                reponse = self._session.request(
                    methode, f"{self.base_url}{chemin}", json=payload,
                    timeout=self.timeout,
                )
                return self._traduire_erreur(reponse)
            except requests.Timeout:
                derniere_erreur = NetworkError(
                    "Le service IA met trop de temps à répondre. Vérifie ta connexion internet."
                )
                _log.warning("Timeout API (%s)", chemin)
            except requests.ConnectionError:
                derniere_erreur = NetworkError(
                    "Impossible de joindre le service IA. Vérifie ta connexion internet."
                )
                _log.warning("Connexion impossible (%s)", chemin)
            if essai < tentatives - 1:
                time.sleep(1.5 * (essai + 1))
        raise derniere_erreur or NetworkError("Erreur réseau inattendue.")

    @staticmethod
    def _traduire_erreur(reponse: requests.Response) -> requests.Response:
        code = reponse.status_code
        if code < 400:
            return reponse
        extrait = ""
        try:
            corps = reponse.json()
            extrait = str(corps.get("message", corps.get("detail", "")))[:200]
        except ValueError:
            extrait = reponse.text[:200]
        _log.warning("Erreur API %s : %s", code, extrait)
        if code in (401, 403):
            raise ApiKeyInvalidError(
                "La clé API Mistral est invalide ou n'a pas les droits nécessaires. "
                "Vérifie-la dans les paramètres."
            )
        if code == 429:
            raise ApiQuotaError(
                "Quota ou débit atteint côté Mistral : patiente un instant "
                "puis relance l'analyse."
            )
        if code == 413 or "too large" in extrait.lower():
            raise DocumentTooLargeError(
                "Ce document est trop volumineux pour l'API. Découpe-le en parties plus petites."
            )
        if code >= 500:
            raise ApiUnavailableError(
                "Le service IA est temporairement indisponible. Réessaie dans quelques instants."
            )
        raise ApiUnavailableError(
            f"Erreur inattendue du service IA (code {code}). {extrait}".strip()
        )

    # ------------------------------------------------------------ modèles
    def tester_connexion(self) -> tuple[str, list[str]]:
        """Vérifie la clé. Renvoie (message_résultat, liste_des_modeles)."""
        reponse = self._requete("GET", "/v1/models")
        try:
            modeles = sorted(m["id"] for m in reponse.json().get("data", []) if m.get("id"))
        except ValueError:
            modeles = []
        return "Connexion réussie ✅ — la clé API Mistral fonctionne.", modeles

    def lister_modeles(self) -> list[str]:
        try:
            _, modeles = self.tester_connexion()
            return modeles
        except Exception:
            return []

    # ------------------------------------------------------------ chat JSON
    def chat_json(self, systeme: str, utilisateur: str, temperature: float = 0.3,
                  max_tokens: int = 8000) -> dict:
        """Dialogue en mode JSON strict. Relance une fois si le JSON est invalide."""
        for essai in range(2):
            payload = {
                "model": self.modele,
                "messages": [
                    {"role": "system", "content": systeme},
                    {"role": "user", "content": utilisateur},
                ],
                "temperature": temperature if essai == 0 else 0.1,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"},
            }
            reponse = self._requete("POST", "/v1/chat/completions", payload)
            try:
                data = reponse.json()
                contenu = data["choices"][0]["message"]["content"]
            except (ValueError, KeyError, IndexError) as exc:
                _log.warning("Réponse chat inattendue : %s", exc)
                raise AiResponseError(
                    "La réponse du service IA est illisible. Réessaie — si le "
                    "problème persiste, choisis un autre modèle dans les paramètres."
                ) from exc
            try:
                return _extraire_json(contenu)
            except AiResponseError:
                if essai == 1:
                    raise
                _log.warning("JSON invalide, nouvelle tentative…")

        raise AiResponseError("La réponse de l'IA n'a pas pu être interprétée.")  # inatteignable

    # ------------------------------------------------------------ OCR
    def ocr(self, data_uri: str, pages_max: int = 40) -> str:
        """OCR Mistral : PDF (document) ou image. Renvoie le texte markdown."""
        est_pdf = data_uri.startswith("data:application/pdf")
        if est_pdf:
            payload = {
                "model": "mistral-ocr-latest",
                "document": {"type": "document_url", "document_url": data_uri},
                "pages": list(range(min(pages_max, 40))),
            }
        else:
            payload = {
                "model": "mistral-ocr-latest",
                "document": {"type": "image_url", "image_url": data_uri},
            }
        reponse = self._requete("POST", "/v1/ocr", payload, tentatives=2)
        try:
            corps = reponse.json()
            pages = corps.get("pages", [])
            textes = [p.get("markdown", "") for p in pages if isinstance(p, dict)]
        except ValueError as exc:
            raise AiResponseError("La réponse OCR du service IA est illisible.") from exc
        return "\n\n".join(t for t in textes if t).strip()


def _extraire_json(contenu: str) -> dict:
    """Parse le JSON renvoyé par le modèle, en tolérant les enrobages markdown."""
    contenu = (contenu or "").strip()
    if not contenu:
        raise AiResponseError("Réponse vide du service IA.")
    try:
        return json.loads(contenu)
    except json.JSONDecodeError:
        pass
    # enrobage ```json … ``` ou texte autour du premier '{' au dernier '}'
    if "```" in contenu:
        morceaux = contenu.split("```")
        for morceau in morceaux:
            morceau = morceau.strip()
            if morceau.startswith("json"):
                morceau = morceau[4:].strip()
            if morceau.startswith("{"):
                try:
                    return json.loads(morceau)
                except json.JSONDecodeError:
                    continue
    debut, fin = contenu.find("{"), contenu.rfind("}")
    if debut >= 0 and fin > debut:
        try:
            return json.loads(contenu[debut:fin + 1])
        except json.JSONDecodeError:
            pass
    raise AiResponseError("La réponse de l'IA n'est pas au format attendu.")
