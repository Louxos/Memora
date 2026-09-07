"""Sujets de test communs : documents d'exemple + serveur API Mistral simulé."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


# ------------------------------------------------------------------ documents

TEXTE_COURS = """Le théorème de Pythagore

1. Le théorème
Dans un triangle rectangle, le carré de l'hypoténuse est égal à la somme des carrés des deux autres côtés.
Si ABC est un triangle rectangle en A, alors BC² = AB² + AC².
BC est l'hypoténuse : c'est le côté opposé à l'angle droit, et le plus long côté du triangle.

2. Utilité
Le théorème de Pythagore permet de calculer la longueur d'un côté d'un triangle rectangle
quand on connaît les deux autres. Il sert par exemple à vérifier qu'un angle est droit
ou à calculer des distances sur un plan.

3. Réciproque
Si dans un triangle ABC on a BC² = AB² + AC², alors le triangle est rectangle en A.
La réciproque sert donc à prouver qu'un triangle est rectangle.

4. Exemple
ABC rectangle en A, AB = 3 cm, AC = 4 cm. Alors BC² = 9 + 16 = 25, donc BC = 5 cm.

5. Piège classique
Ne pas appliquer Pythagore dans un triangle qui n'est pas rectangle !
Toujours vérifier que le triangle est rectangle avant de l'utiliser.
"""


def _cree_pdf_texte(chemin, texte: str) -> None:
    import pymupdf as fitz

    doc = fitz.open()
    for morceau in texte.split("\n\n"):
        page = doc.new_page()
        page.insert_textbox(fitz.Rect(50, 50, 545, 790), morceau, fontsize=11)
    doc.save(str(chemin))
    doc.close()


def _cree_pdf_scanne(chemin, nb_pages: int = 2) -> None:
    import pymupdf as fitz

    doc = fitz.open()
    for _ in range(nb_pages):
        doc.new_page()  # pages vides : aucun texte intégré
    doc.save(str(chemin))
    doc.close()


def _cree_image_texte(chemin) -> None:
    import pymupdf as fitz

    doc = fitz.open()
    page = doc.new_page(width=600, height=300)
    page.insert_text(fitz.Point(40, 80), "Le théorème de Pythagore", fontsize=24)
    page.insert_text(fitz.Point(40, 130), "BC2 = AB2 + AC2 dans un triangle rectangle en A", fontsize=14)
    pix = page.get_pixmap(clip=fitz.Rect(0, 0, 600, 300))
    pix.save(str(chemin))
    doc.close()


def _cree_docx(chemin, texte: str) -> None:
    from docx import Document

    document = Document()
    document.add_heading("Le théorème de Pythagore", 0)
    document.add_heading("1. Le théorème", level=1)
    document.add_paragraph(
        "Dans un triangle rectangle, le carré de l'hypoténuse est égal à la somme "
        "des carrés des deux autres côtés."
    )
    document.add_paragraph("Si ABC est rectangle en A, alors BC² = AB² + AC².", style="List Bullet")
    document.add_heading("4. Exemple", level=1)
    document.add_paragraph("AB = 3 cm, AC = 4 cm, donc BC = 5 cm.")
    document.save(str(chemin))


@pytest.fixture()
def exemples(tmp_path):
    """Crée les documents d'exemple et renvoie leurs chemins."""
    pdf = tmp_path / "cours_pythagore.pdf"
    _cree_pdf_texte(pdf, TEXTE_COURS)
    pdf_scanne = tmp_path / "scan_vide.pdf"
    _cree_pdf_scanne(pdf_scanne)
    image = tmp_path / "photo_cours.png"
    _cree_image_texte(image)
    docx = tmp_path / "cours_pythagore.docx"
    _cree_docx(docx, TEXTE_COURS)
    txt = tmp_path / "cours.txt"
    txt.write_text(TEXTE_COURS, encoding="utf-8")
    return {
        "pdf": pdf, "pdf_scanne": pdf_scanne, "image": image,
        "docx": docx, "txt": txt, "txt_contenu": TEXTE_COURS,
    }


# ------------------------------------------------------------------ serveur mock

FICHE_MOCK = {
    "titre": "Le théorème de Pythagore",
    "matiere": "Mathématiques",
    "chapitre": "Théorème de Pythagore",
    "theme": "Géométrie",
    "niveau": "3e",
    "objectif": "À la fin de cette fiche, tu dois être capable d'appliquer le théorème de Pythagore et sa réciproque.",
    "essentiel": [
        "Dans un triangle rectangle, le carré de l'hypoténuse égale la somme des carrés des deux autres côtés.",
        "La réciproque permet de prouver qu'un triangle est rectangle.",
    ],
    "notions": [
        {"nom": "Hypoténuse", "explication": "Côté opposé à l'angle droit, le plus long côté.", "exemple": "BC si le triangle est rectangle en A."},
    ],
    "definitions": [
        {"terme": "Théorème de Pythagore", "definition": "BC² = AB² + AC² dans un triangle rectangle en A."},
    ],
    "formules": [
        {"formule": "BC² = AB² + AC²", "signification": "BC : hypoténuse ; AB, AC : côtés de l'angle droit", "unite": "cm (ou l'unité des côtés)", "conditions": "Triangle rectangle uniquement", "exemple": "AB=3, AC=4 → BC=5"},
    ],
    "methodes": [
        {"titre": "Comment calculer un côté", "etapes": ["Vérifier que le triangle est rectangle.", "Repérer l'hypoténuse.", "Appliquer BC² = AB² + AC².", "Extraire la racine carrée."]},
    ],
    "dates_personnages": [],
    "exemples": ["AB = 3 cm et AC = 4 cm → BC = 5 cm."],
    "pieges": ["Ne pas utiliser Pythagore si le triangle n'est pas rectangle."],
    "retenir": ["BC² = AB² + AC² (triangle rectangle en A).", "L'hypoténuse est le plus long côté."],
    "questions": [
        {"question": "Énonce le théorème de Pythagore.", "reponse": "Dans un triangle rectangle, le carré de l'hypoténuse est égal à la somme des carrés des deux autres côtés.", "type": "définition"},
        {"question": "AB=3 et AC=4 : combien vaut BC ?", "reponse": "BC = 5 car BC² = 9 + 16 = 25.", "type": "application"},
    ],
    "avertissements": [],
}

OCR_MOCK = "Le théorème de Pythagore\n\nBC2 = AB2 + AC2 dans un triangle rectangle en A."


class MockMistralHandler(BaseHTTPRequestHandler):
    """Implémente /v1/models, /v1/chat/completions, /v1/ocr comme Mistral."""

    comportement = {}  # activable depuis les tests (clé → code d'erreur)

    def log_message(self, *args):  # silence
        pass

    def _json(self, code: int, corps: dict) -> None:
        corps_bytes = json.dumps(corps).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corps_bytes)))
        self.end_headers()
        self.wfile.write(corps_bytes)

    def do_GET(self):  # noqa: N802
        if self.path == "/v1/models":
            if MockMistralHandler.comportement.get("models") == 401:
                self._json(401, {"message": "Unauthorized"})
                return
            self._json(200, {"data": [{"id": "mistral-small-latest"}, {"id": "mistral-large-latest"}]})
        else:
            self._json(404, {"message": "not found"})

    def do_POST(self):  # noqa: N802
        longueur = int(self.headers.get("Content-Length", 0))
        corps = json.loads(self.rfile.read(longueur) or b"{}")

        if self.path == "/v1/chat/completions":
            if MockMistralHandler.comportement.get("chat") == "json_invalide":
                self._json(200, {"choices": [{"message": {"content": "voici pas du json"}}]})
                return
            if MockMistralHandler.comportement.get("chat") == "incomplet":
                self._json(200, {"choices": [{"message": {"content": json.dumps({"titre": "Fiche vide"})}}]})
                return
            contenu = json.dumps(FICHE_MOCK, ensure_ascii=False)
            self._json(200, {"choices": [{"message": {"content": contenu}}]})
            return

        if self.path == "/v1/ocr":
            self._json(200, {"pages": [{"index": 0, "markdown": OCR_MOCK}]})
            return

        self._json(404, {"message": "not found"})


@pytest.fixture()
def serveur_mistral():
    """Démarre le serveur mock sur un port libre ; renvoie l'URL de base."""
    serveur = ThreadingHTTPServer(("127.0.0.1", 0), MockMistralHandler)
    thread = threading.Thread(target=serveur.serve_forever, daemon=True)
    thread.start()
    MockMistralHandler.comportement = {}
    yield f"http://127.0.0.1:{serveur.server_address[1]}"
    serveur.shutdown()
    serveur.server_close()


@pytest.fixture()
def client_mock(serveur_mistral):
    from memora.ia.client import MistralClient

    return MistralClient(cle_api="cle-de-test", modele="mistral-small-latest",
                         base_url=serveur_mistral, timeout=10)


@pytest.fixture()
def base_vierge(tmp_path, monkeypatch):
    """Base SQLite isolée dans un répertoire temporaire."""
    monkeypatch.setenv("MEMORA_HOME", str(tmp_path / "donnees"))
    from memora.core.database import Database

    base = Database(tmp_path / "test.db")
    yield base
    base.fermer()
