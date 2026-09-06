"""Export PDF d'une fiche (rendu HTML → QPdfWriter), sans dépendance externe."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QPageLayout, QPageSize, QTextDocument
from PySide6.QtPrintSupport import QPrinter

from memora.core.models import Fiche
from memora.export.html_export import fiche_vers_html
from memora.utils.logging_setup import logger

_log = logger("export.pdf")


def exporter_pdf(fiche: Fiche, chemin: str | Path, inclure_reponses: bool = True) -> Path:
    """Écrit la fiche en PDF A4, mise en page propre et lisible."""
    chemin = Path(chemin)
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(str(chemin))
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    printer.setPageLayout(QPageLayout(QPageSize(QPageSize.PageSizeId.A4),
                                      QPageLayout.Orientation.Portrait,
                                      QMarginsF(14, 14, 14, 14), QPageLayout.Unit.Millimeter))

    html = fiche_vers_html(fiche, inclure_reponses=inclure_reponses)
    document = QTextDocument()
    document.setHtml(html)
    document.print_(printer)
    _log.info("PDF exporté : %s", chemin)
    return chemin
