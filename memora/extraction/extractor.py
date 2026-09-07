"""Point d'entrée de l'extraction : dispatch selon le type de document.

Fournit ExtractionResult, le résultat commun à tous les types :
texte extrait, méthode utilisée, avertissements éventuels, aperçu PNG.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from memora.extraction import docx_extractor, pdf_extractor
from memora.utils import files
from memora.utils.errors import (
    DocumentTooLargeError,
    DocumentUnreadableError,
    UnsupportedFormatError,
)
from memora.utils.logging_setup import logger

_log = logger("extraction")


@dataclass
class ExtractionResult:
    chemin: str
    nom: str
    type_lisible: str
    categorie: str            # pdf | docx | texte | image
    taille_octets: int
    texte: str = ""
    methode: str = ""         # « texte intégré », « OCR Mistral »…
    nb_pages: int = 0
    avertissements: list[str] = field(default_factory=list)

    def contenu_est_maigre(self) -> bool:
        """Moins de ~120 caractères utilisables : le document est probablement vide/illisible."""
        return len(self.texte.strip()) < 120


def extraire(chemin: str | Path, client_ia=None, avec_ocr: bool = True) -> ExtractionResult:
    """Extrait le contenu d'un document.

    ``client_ia`` : MistralClient ou None (OCR local / erreur claire si requis).
    Lève UnsupportedFormatError / DocumentTooLargeError / DocumentUnreadableError.
    """
    chemin = Path(chemin)
    if not chemin.is_file():
        raise DocumentUnreadableError("Impossible de lire ce fichier : il n'existe plus ou l'accès est refusé.")

    ext = chemin.suffix.lower()
    if ext not in files.EXTENSIONS:
        raise UnsupportedFormatError(
            f"Format non pris en charge ({ext or 'inconnu'}). "
            "Formats acceptés : PDF, DOCX, TXT, MD, JPG, PNG, WEBP."
        )
    if chemin.stat().st_size > files.TAILLE_MAX_OCTETS:
        raise DocumentTooLargeError(
            "Ce document est trop volumineux (maximum 25 Mo). "
            "Découpe-le en parties plus petites avant de l'importer."
        )

    nom, type_lisible, categorie, taille = files.infos_fichier(chemin)
    resultat = ExtractionResult(
        chemin=str(chemin), nom=nom, type_lisible=type_lisible,
        categorie=categorie, taille_octets=taille,
    )

    if ext == ".pdf":
        _extraire_pdf(chemin, resultat, client_ia, avec_ocr)
    elif ext == ".docx":
        _extraire_docx(chemin, resultat)
    elif ext in (".txt", ".md"):
        resultat.texte = files.lire_texte_souple(chemin)
        resultat.methode = "texte"
    else:  # image → OCR obligatoire
        _extraire_image(chemin, resultat, client_ia, avec_ocr)

    if resultat.contenu_est_maigre():
        resultat.avertissements.append(
            "Le texte extrait est très court : le document est peut-être vide, "
            "mal scanné ou illisible. Vérifie la fiche générée."
        )
    _log.info("Extraction %s (%s) : %s caractères via %s",
              nom, categorie, len(resultat.texte), resultat.methode)
    return resultat


# ------------------------------------------------------------------ privées

def _extraire_pdf(chemin: Path, resultat: ExtractionResult, client_ia, avec_ocr: bool) -> None:
    try:
        res = pdf_extractor.extraire_pdf(chemin)
    except Exception as exc:  # PDF corrompu
        _log.exception("PDF illisible")
        raise DocumentUnreadableError(
            "Impossible de lire ce PDF : le fichier semble corrompu ou protégé par mot de passe."
        ) from exc
    resultat.nb_pages = res.nb_pages
    if not res.semble_scanne and res.texte:
        resultat.texte = res.texte
        resultat.methode = "texte intégré"
        return
    # PDF scanné → OCR
    resultat.avertissements.append(
        "Peu ou pas de texte intégré détecté : OCR appliqué (qualité à vérifier)."
    )
    if avec_ocr:
        from memora.extraction import ocr as module_ocr

        texte, methode = module_ocr.ocr_document(chemin, client_ia)
        resultat.texte = texte
        resultat.methode = methode


def _extraire_docx(chemin: Path, resultat: ExtractionResult) -> None:
    try:
        resultat.texte = docx_extractor.extraire_docx(chemin)
        resultat.methode = "structure Word"
    except Exception as exc:
        _log.exception("DOCX illisible")
        raise DocumentUnreadableError(
            "Impossible de lire ce document Word : le fichier est peut-être "
            "corrompu ou au vieux format .doc (enregistre-le en .docx)."
        ) from exc


def _extraire_image(chemin: Path, resultat: ExtractionResult, client_ia, avec_ocr: bool) -> None:
    if not avec_ocr:
        return
    try:
        import pymupdf as fitz

        pix = fitz.Pixmap(str(chemin))
        resultat.nb_pages = 1
        if pix.width < 80 or pix.height < 80:
            resultat.avertissements.append("Image de très petite taille : l'OCR risque d'être imprécis.")
    except Exception:
        raise DocumentUnreadableError(
            "Impossible de lire cette image : format invalide ou fichier corrompu."
        )
    from memora.extraction import ocr as module_ocr

    texte, methode = module_ocr.ocr_document(chemin, client_ia)
    resultat.texte = texte
    resultat.methode = methode


def apercu_png(chemin: str | Path, largeur: int = 520) -> bytes | None:
    """Aperçu PNG du document (page 1 d'un PDF, image réduite), ou None."""
    chemin = Path(chemin)
    try:
        ext = chemin.suffix.lower()
        if ext == ".pdf":
            return pdf_extractor.apercu_page(chemin, 0, largeur)
        if ext in (".png", ".jpg", ".jpeg", ".webp"):
            import pymupdf as fitz

            pix = fitz.Pixmap(str(chemin))
            if pix.alpha or pix.colorspace is None or pix.n > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            if pix.width > largeur:  # réduction propre
                hauteur = max(1, round(pix.height * largeur / pix.width))
                pix = fitz.Pixmap(pix, largeur, hauteur)
            return pix.tobytes("png")
    except Exception:
        _log.debug("Aperçu indisponible pour %s", chemin, exc_info=True)
    return None
