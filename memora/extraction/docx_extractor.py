"""Extraction du contenu des DOCX (python-docx), en conservant la structure :
titres, paragraphes, listes et tableaux.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document as DocxDocument
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraphe

from memora.utils.logging_setup import logger

_log = logger("extraction.docx")


def _paragraphe_markdown(para: DocxParagraphe) -> str:
    texte = (para.text or "").strip()
    if not texte:
        return ""
    style = (para.style.name if para.style is not None else "") or ""
    style_lower = style.lower()
    if style_lower.startswith("heading") or style_lower.startswith("titre"):
        try:
            niveau = int("".join(c for c in style if c.isdigit()) or "1")
        except ValueError:
            niveau = 1
        return f"{'#' * min(niveau + 1, 6)} {texte}"
    if style_lower.startswith(("list", "liste", "puces")):
        return f"- {texte}"
    if "quote" in style_lower or "citation" in style_lower:
        return f"> {texte}"
    return texte


def _table_markdown(table: DocxTable) -> str:
    lignes = []
    for ligne in table.rows:
        cellules = [(c.text or "").strip().replace("\n", " ") for c in ligne.cells]
        lignes.append("| " + " | ".join(cellules) + " |")
    if not lignes:
        return ""
    separateur = "|" + "---|" * len(table.rows[0].cells)
    lignes.insert(1, separateur)
    return "\n".join(lignes)


def extraire_docx(chemin: str | Path) -> str:
    """Extrait le texte structuré d'un fichier .docx."""
    document = DocxDocument(str(chemin))
    corps = document.element.body
    morceaux: list[str] = []
    for enfant in corps.iterchildren():
        tag = enfant.tag.split("}")[-1]
        if tag == "p":
            morceaux.append(_paragraphe_markdown(DocxParagraphe(enfant, document)))
        elif tag == "tbl":
            morceaux.append(_table_markdown(DocxTable(enfant, document)))
    texte = "\n".join(m for m in morceaux if m).strip()
    _log.info("DOCX %s : %s caractères", Path(chemin).name, len(texte))
    return texte
