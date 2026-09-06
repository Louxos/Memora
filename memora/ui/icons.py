"""Icônes vectorielles de Memora.

Les icônes sont générées à la volée à partir de tracés SVG (style « traits
arrondis », cohérent dans toute l'application) puis rendues en QPixmap
colorées. Aucun fichier binaire externe nécessaire.
"""

from __future__ import annotations

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

# Tracés type Feather (lignes / polygones, stroke uniquement)
_CHEMINS: dict[str, str] = {
    "accueil": (
        '<path d="M3 9.5 12 3l9 6.5V20a1.5 1.5 0 0 1-1.5 1.5H15v-7H9v7H4.5A1.5 1.5 0 0 1 3 20z"/>'
    ),
    "livre": (
        '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z"/>'
        '<path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>'
    ),
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "etoile": (
        '<polygon points="12 2.6 15.1 8.9 22 9.9 17 14.8 18.2 21.6 12 18.4 5.8 21.6 7 14.8 2 9.9 8.9 8.9"/>'
    ),
    "reglages": (
        '<circle cx="12" cy="12" r="3.2"/>'
        '<path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.2 5.2l2.1 2.1M16.7 16.7l2.1 2.1'
        'M18.8 5.2l-2.1 2.1M7.3 16.7l-2.1 2.1"/>'
    ),
    "recherche": '<circle cx="11" cy="11" r="7.5"/><path d="M21 21l-4.7-4.7"/>',
    "importer": (
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<polyline points="17 8 12 3 7 8"/><path d="M12 3v13"/>'
    ),
    "fichier": (
        '<path d="M14 2.5H6.5a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z"/>'
        '<polyline points="14 2.5 14 8 19.5 8"/><path d="M8.5 13h7M8.5 17h7"/>'
    ),
    "image": (
        '<rect x="3" y="3" width="18" height="18" rx="2.5"/>'
        '<circle cx="8.5" cy="8.5" r="1.8"/><polyline points="21 15.5 16 10.5 5 21.5"/>'
    ),
    "crayon": '<path d="M16.8 3.3a2.6 2.6 0 0 1 3.7 3.7L7.2 20.3 2.5 21.5l1.2-4.7z"/>',
    "poubelle": (
        '<polyline points="3.5 6 5.5 6 20.5 6"/>'
        '<path d="M18.5 6v13.5a2 2 0 0 1-2 2h-9a2 2 0 0 1-2-2V6"/>'
        '<path d="M9.5 6V4.5a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2V6"/>'
    ),
    "rafraichir": (
        '<polyline points="22 4.5 22 10 16.5 10"/><polyline points="2 19.5 2 14 7.5 14"/>'
        '<path d="M19.6 9a8.5 8.5 0 0 0-14.7-3L2 9m20 6l-2.9 3a8.5 8.5 0 0 1-14.7-3"/>'
    ),
    "exporter": (
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<polyline points="7 10 12 15 17 10"/><path d="M12 15V3"/>'
    ),
    "copier": (
        '<rect x="9" y="9" width="12.5" height="12.5" rx="2"/>'
        '<path d="M5.5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1.5"/>'
    ),
    "check": '<polyline points="20 6.5 9.5 17.5 4 12"/>',
    "croix": '<path d="M18 6 6 18M6 6l12 12"/>',
    "alerte": (
        '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>'
        '<path d="M12 9v4.5"/><circle cx="12" cy="17.3" r="0.4" fill="currentColor"/>'
    ),
    "retour": '<path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/>',
    "oeil": (
        '<path d="M1.5 12S5.5 4.5 12 4.5 22.5 12 22.5 12 18.5 19.5 12 19.5 1.5 12 1.5 12z"/>'
        '<circle cx="12" cy="12" r="3"/>'
    ),
    "horloge": '<circle cx="12" cy="12" r="9"/><polyline points="12 6.5 12 12 16 14"/>',
    "filtre": '<polygon points="22 3.5 2 3.5 10 12.8 10 19.5 14 21.5 14 12.8"/>',
    "dossier": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    "etincelle": (
        '<path d="M12 2.5l1.9 5.3 5.3 1.9-5.3 1.9L12 17l-1.9-5.4L4.8 9.7l5.3-1.9z"/>'
        '<path d="M19 15.5l.9 2.4 2.4.9-2.4.9-.9 2.4-.9-2.4-2.4-.9 2.4-.9z"/>'
    ),
    "cle": (
        '<circle cx="7.5" cy="15.5" r="4.5"/>'
        '<path d="M10.7 12.3 20.5 2.5M17 6l3 3M14 9l2.5 2.5"/>'
    ),
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 16v-5"/><circle cx="12" cy="8" r="0.5" fill="currentColor"/>',
    "lune": '<path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/>',
    "soleil": (
        '<circle cx="12" cy="12" r="4"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22'
        'M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M19.1 4.9l-1.8 1.8M6.7 17.3l-1.8 1.8"/>'
    ),
    "coeur": (
        '<path d="M20.8 5.6a5.2 5.2 0 0 0-7.4 0L12 7l-1.4-1.4a5.2 5.2 0 0 0-7.4 7.4'
        'L12 21.5l8.8-8.5a5.2 5.2 0 0 0 0-7.4z"/>'
    ),
    "cible": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1" fill="currentColor"/>',
    "liste": '<path d="M8 6h13M8 12h13M8 18h13"/><circle cx="3.7" cy="6" r="1" fill="currentColor"/><circle cx="3.7" cy="12" r="1" fill="currentColor"/><circle cx="3.7" cy="18" r="1" fill="currentColor"/>',
}

_cache: dict[tuple[str, str, int], QIcon] = {}


def _svg(nom: str, couleur: str) -> bytes:
    corps = _CHEMINS[nom]
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{couleur}" stroke-width="1.9" stroke-linecap="round" '
        f'stroke-linejoin="round">{corps}</svg>'
    )
    return svg.encode("utf-8")


def icone(nom: str, couleur: str = "#5B6274", taille: int = 22) -> QIcon:
    """Renvoie l'icône rendue dans la couleur demandée (cache intégré)."""
    cle = (nom, couleur, taille)
    if cle in _cache:
        return _cache[cle]
    if nom not in _CHEMINS:
        return QIcon()
    rendu = QSvgRenderer(QByteArray(_svg(nom, couleur)))
    ratio = 2  # rendu net en écrans haute résolution
    image = QImage(taille * ratio, taille * ratio, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    peintre = QPainter(image)
    peintre.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    rendu.render(peintre, QRectF(0, 0, taille * ratio, taille * ratio))
    peintre.end()
    pix = QPixmap.fromImage(image)
    pix.setDevicePixelRatio(ratio)
    ic = QIcon(pix)
    _cache[cle] = ic
    return ic
