"""Tests de l'extraction de documents (PDF, DOCX, TXT, images, OCR)."""

from __future__ import annotations

import pytest

from memora.extraction.extractor import ExtractionResult, apercu_png, extraire
from memora.utils.errors import DocumentUnreadableError, UnsupportedFormatError


def test_pdf_textuel(exemples):
    resultat = extraire(exemples["pdf"], client_ia=None)
    assert "hypoténuse" in resultat.texte
    assert resultat.methode == "texte intégré"
    assert resultat.nb_pages >= 1


def test_pdf_scanne_basculer_ocr(exemples, client_mock):
    resultat = extraire(exemples["pdf_scanne"], client_ia=client_mock)
    assert resultat.methode == "OCR Mistral"
    assert "Pythagore" in resultat.texte
    assert any("OCR" in a for a in resultat.avertissements)


def test_pdf_scanne_sans_cle_message_clair(exemples):
    with pytest.raises(Exception) as info:
        extraire(exemples["pdf_scanne"], client_ia=None)
    assert "OCR" in str(info.value) or "clé" in str(info.value)


def test_image_ocr(exemples, client_mock):
    resultat = extraire(exemples["image"], client_ia=client_mock)
    assert resultat.methode == "OCR Mistral"
    assert "Pythagore" in resultat.texte


def test_docx_structure(exemples):
    resultat = extraire(exemples["docx"], client_ia=None)
    assert "## 1. Le théorème" in resultat.texte
    assert "- Si ABC est rectangle en A" in resultat.texte
    assert "## 4. Exemple" in resultat.texte


def test_txt(exemples):
    resultat = extraire(exemples["txt"], client_ia=None)
    assert "réciproque" in resultat.texte


def test_format_non_supporte(tmp_path):
    inconnu = tmp_path / "cours.xyz"
    inconnu.write_text("n'importe", encoding="utf-8")
    with pytest.raises(UnsupportedFormatError):
        extraire(inconnu, client_ia=None)


def test_fichier_inexistant():
    with pytest.raises(DocumentUnreadableError):
        extraire("/chemin/qui/nexiste/pas.pdf", client_ia=None)


def test_document_trop_volumineux(tmp_path, monkeypatch):
    gros = tmp_path / "gros.pdf"
    gros.write_bytes(b"%PDF-1.4" + b"0" * 100)
    from memora.utils import files as module_files

    limite_reelle = module_files.TAILLE_MAX_OCTETS
    monkeypatch.setattr(module_files, "TAILLE_MAX_OCTETS", 50)
    try:
        from memora.utils.errors import DocumentTooLargeError

        with pytest.raises(DocumentTooLargeError):
            extraire(gros, client_ia=None)
    finally:
        module_files.TAILLE_MAX_OCTETS = limite_reelle


def test_apercu_pdf_et_image(exemples):
    assert apercu_png(exemples["pdf"]) is not None
    assert apercu_png(exemples["image"]) is not None


def test_document_presque_vide_signale(tmp_path):
    from memora.extraction.extractor import ExtractionResult as ER

    vide = tmp_path / "vide.txt"
    vide.write_text("ab", encoding="utf-8")
    resultat = extraire(vide, client_ia=None)
    assert resultat.contenu_est_maigre()
    assert resultat.avertissements
    _ = ER
