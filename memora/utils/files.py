"""Petits utilitaires autour des fichiers."""

from __future__ import annotations

import os
from pathlib import Path

EXTENSIONS = {
    ".pdf": ("PDF", "pdf"),
    ".docx": ("Word", "docx"),
    ".txt": ("Texte", "texte"),
    ".md": ("Texte", "texte"),
    ".jpg": ("Image", "image"),
    ".jpeg": ("Image", "image"),
    ".png": ("Image", "image"),
    ".webp": ("Image", "image"),
}

TAILLE_MAX_OCTETS = 25 * 1024 * 1024  # 25 Mo (limite prudente pour l'API)


def taille_lisible(nb_octets: int) -> str:
    if nb_octets < 1024:
        return f"{nb_octets} o"
    if nb_octets < 1024 * 1024:
        return f"{nb_octets / 1024:.1f} Ko"
    return f"{nb_octets / (1024 * 1024):.1f} Mo"


def infos_fichier(chemin: str | Path) -> tuple[str, str, str, int]:
    """Renvoie (nom, type lisible, catégorie, taille) pour un fichier."""
    p = Path(chemin)
    ext = p.suffix.lower()
    type_lisible, categorie = EXTENSIONS.get(ext, (ext.lstrip(".").upper() or "?", "autre"))
    try:
        taille = p.stat().st_size
    except OSError:
        taille = 0
    return p.name, type_lisible, categorie, taille


def extension_supportee(chemin: str | Path) -> bool:
    return Path(chemin).suffix.lower() in EXTENSIONS


def lire_texte_souple(chemin: str | Path) -> str:
    """Lit un fichier texte en essayant UTF-8 puis Windows-1252 / Latin-1."""
    brut = Path(chemin).read_bytes()
    for encodage in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return brut.decode(encodage)
        except UnicodeDecodeError:
            continue
    return brut.decode("utf-8", errors="replace")


def chemin_absolu_affichable(chemin: str | Path) -> str:
    try:
        return str(Path(chemin).resolve())
    except OSError:
        return str(chemin)


def fichier_existe(chemin: str | Path) -> bool:
    try:
        return Path(chemin).is_file()
    except OSError:
        return False
