"""OCR : Mistral OCR (API) avec repli Tesseract local si installé.

Les images et PDF scannés passent par ici. Mistral OCR fonctionne très bien
avec le français ; Tesseract (binaire + package « tesseract-ocr-fra ») reste
utile hors connexion.
"""

from __future__ import annotations

import base64
from pathlib import Path

from memora.ia.client import TAILLE_MAX_BASE64, MistralClient
from memora.utils.errors import ApiKeyMissingError, DocumentTooLargeError
from memora.utils.logging_setup import logger

_log = logger("extraction.ocr")

MODELE_OCR = "mistral-ocr-latest"
MAX_PAGES_OCR = 40

_MIME = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def tesseract_disponible() -> bool:
    try:
        import pytesseract  # noqa: F401
        import shutil
        return shutil.which("tesseract") is not None
    except ImportError:
        return False


def _data_uri(chemin: str | Path) -> str:
    p = Path(chemin)
    mime = _MIME.get(p.suffix.lower(), "application/octet-stream")
    data = p.read_bytes()
    if len(data) > TAILLE_MAX_BASE64:
        raise DocumentTooLargeError(
            "Ce document est trop volumineux pour l'analyse par OCR (maximum 25 Mo)."
        )
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def ocr_mistral(chemin: str | Path, client: MistralClient) -> str:
    """OCR via l'API Mistral. Renvoie le texte markdown consolidé."""
    return client.ocr(_data_uri(chemin))


def ocr_tesseract(chemin: str | Path, langue: str = "fra") -> str:
    """OCR local via Tesseract (si installé). Renvoie '' si indisponible."""
    if not tesseract_disponible():
        return ""
    import io

    import pytesseract
    from PIL import Image

    texte_pages: list[str] = []
    p = Path(chemin)
    if p.suffix.lower() == ".pdf":
        from memora.extraction import pdf_extractor

        for numero in range(min(nb_pages_sans_ouverture(p), MAX_PAGES_OCR)):
            png = pdf_extractor.page_vers_png(p, numero)
            image = Image.open(io.BytesIO(png))
            texte_pages.append(pytesseract.image_to_string(image, lang=langue))
    else:
        image = Image.open(io.BytesIO(p.read_bytes()))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        texte_pages.append(pytesseract.image_to_string(image, lang=langue))
    return "\n".join(t for t in texte_pages if t).strip()


def nb_pages_sans_ouverture(chemin: Path) -> int:
    from memora.extraction import pdf_extractor

    return pdf_extractor.nb_pages(chemin)


def ocr_document(chemin: str | Path, client: MistralClient | None) -> tuple[str, str]:
    """OCR intelligent : Mistral si possible, sinon Tesseract local.

    Renvoie (texte, methode_utilisee).
    """
    # 1) Mistral OCR — meilleure qualité pour le français
    if client is not None:
        pages = max(nb_pages_sans_ouverture(Path(chemin)), 1) if Path(chemin).suffix.lower() == ".pdf" else 1
        if pages > MAX_PAGES_OCR:
            _log.warning("Document long (%s pages) : OCR limité aux %s premières.",
                         pages, MAX_PAGES_OCR)
        return ocr_mistral(chemin, client), "OCR Mistral"

    # 2) Tesseract local
    if tesseract_disponible():
        texte = ocr_tesseract(chemin)
        if texte:
            return texte, "OCR Tesseract (local)"

    raise ApiKeyMissingError(
        "Ce document nécessite un OCR. Renseigne ta clé API Mistral dans les "
        "paramètres (l'OCR fonctionne alors automatiquement), ou installe "
        "Tesseract avec le package français."
    )
