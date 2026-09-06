"""Extraction du texte des PDF (PyMuPDF).

Détecte les PDF « scannés » (densité de texte trop faible) pour déclencher
l'OCR en remplacement.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pymupdf as fitz  # PyMuPDF

from memora.utils.logging_setup import logger

_log = logger("extraction.pdf")

SEUIL_CARACTERES_PAGE = 60  # en dessous : probablement un scan


@dataclass
class ResultatPdf:
    texte: str
    nb_pages: int
    semble_scanne: bool


def extraire_pdf(chemin: str | Path) -> ResultatPdf:
    """Extrait le texte ; indique si le PDF semble être un scan."""
    doc = fitz.open(str(chemin))
    try:
        morceaux: list[str] = []
        total_caracteres = 0
        for page in doc:
            texte_page = page.get_text("text")
            total_caracteres += len(texte_page.strip())
            morceaux.append(texte_page)
        texte = "\n".join(morceaux).strip()
        nb_pages = doc.page_count
        densite = total_caracteres / max(nb_pages, 1)
        semble_scanne = densite < SEUIL_CARACTERES_PAGE
        _log.info(
            "PDF %s : %s pages, %s caractères, scan=%s",
            Path(chemin).name, nb_pages, total_caracteres, semble_scanne,
        )
        return ResultatPdf(texte=texte, nb_pages=nb_pages, semble_scanne=semble_scanne)
    finally:
        doc.close()


def apercu_page(chemin: str | Path, numero: int = 0, largeur: int = 520) -> bytes:
    """Renvoie la première page du PDF en PNG (aperçu). Lève RuntimeError si échec."""
    doc = fitz.open(str(chemin))
    try:
        page = doc[min(numero, doc.page_count - 1)]
        zoom = largeur / max(page.rect.width, 1)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        return pix.tobytes("png")
    finally:
        doc.close()


def nb_pages(chemin: str | Path) -> int:
    doc = fitz.open(str(chemin))
    try:
        return doc.page_count
    finally:
        doc.close()


def page_vers_png(chemin: str | Path, numero: int, dpi: int = 170) -> bytes:
    """Rend une page en PNG (utilisé pour l'OCR Tesseract local)."""
    doc = fitz.open(str(chemin))
    try:
        page = doc[numero]
        zoom = dpi / 72
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        return pix.tobytes("png")
    finally:
        doc.close()
