"""Thème visuel de Memora : palettes clair / sombre + feuille QSS.

Design premium : accent indigo→violet en dégradé, surfaces en cartes
arrondies, accents colorés par section, typographie hiérarchisée.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QPalette

# ------------------------------------------------------------------ palettes

CLAIR = {
    "nom": "clair",
    "fenetre": "#F2F3F9",
    "surface": "#FFFFFF",
    "surface2": "#F7F8FC",
    "barre": "#FFFFFF",
    "texte": "#171B2B",
    "texte2": "#5B6274",
    "texte3": "#9CA3AF",
    "bord": "#E5E8F0",
    "accent": "#5B5FE9",
    "accent2": "#8B5CF6",
    "accent_sur": "#FFFFFF",
    "accent_doux": "#EEF0FE",
    "succes": "#30A46C",
    "attention": "#F5A524",
    "danger": "#E5484D",
    "ombre": "rgba(27, 31, 46, 18)",
    "entree": "#FFFFFF",
    "survol": "#F7F8FD",
}

SOMBRE = {
    "nom": "sombre",
    "fenetre": "#101219",
    "surface": "#1A1D2B",
    "surface2": "#212536",
    "barre": "#151823",
    "texte": "#ECEEF6",
    "texte2": "#A6ACC2",
    "texte3": "#6E7590",
    "bord": "#2A2F44",
    "accent": "#7C7FF2",
    "accent2": "#A78BFA",
    "accent_sur": "#FFFFFF",
    "accent_doux": "#262A47",
    "succes": "#3DD68C",
    "attention": "#FFB224",
    "danger": "#FF6369",
    "ombre": "rgba(0, 0, 0, 90)",
    "entree": "#20243592",
    "survol": "#202435",
}


def palette(nom: str) -> dict:
    return SOMBRE if nom == "sombre" else CLAIR


def degrade(p: dict, horizontal: bool = True) -> str:
    """Dégradé signature indigo → violet (pour QSS/feuilles locales)."""
    if horizontal:
        return (f"qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                f"stop:0 {p['accent']}, stop:1 {p['accent2']})")
    return (f"qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            f"stop:0 {p['accent']}, stop:1 {p['accent2']})")


def theme_systeme() -> str:
    """Détecte le thème du système (Qt) : 'clair' ou 'sombre'."""
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            return "clair"
        if app.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            return "sombre"
    except Exception:
        pass
    return "clair"


# ------------------------------------------------------------------ QSS

def qss(p: dict) -> str:
    return f"""
* {{ outline: none; }}
QMainWindow, QWidget#racine {{ background: {p['fenetre']}; }}

/* ---------- texte ---------- */
QLabel {{ color: {p['texte']}; font-size: 14px; background: transparent; }}
QLabel[classe="titre1"] {{ font-size: 27px; font-weight: 800; letter-spacing: 0.4px; }}
QLabel[classe="titre2"] {{ font-size: 18px; font-weight: 800; letter-spacing: 0.2px; }}
QLabel[classe="titre3"] {{ font-size: 15px; font-weight: 700; }}
QLabel[classe="muet"] {{ color: {p['texte2']}; }}
QLabel[classe="tres_muet"] {{ color: {p['texte3']}; font-size: 12px; }}
QLabel[classe="accent"] {{ color: {p['accent']}; }}

/* ---------- cartes ---------- */
QFrame[classe="carte"] {{
    background: {p['surface']};
    border: 1px solid {p['bord']};
    border-radius: 16px;
}}
QFrame[classe="carte"]:hover {{ background: {p['survol']}; }}
QFrame[classe="carte2"] {{
    background: {p['surface2']};
    border: 1px solid {p['bord']};
    border-radius: 13px;
}}
QFrame[classe="encadre"] {{
    background: {p['accent_doux']};
    border: 1px solid {p['accent']};
    border-radius: 16px;
}}

/* ---------- boutons ---------- */
QPushButton {{
    background: {p['surface']};
    color: {p['texte']};
    border: 1px solid {p['bord']};
    border-radius: 11px;
    padding: 8px 16px;
    font-size: 13.5px;
    font-weight: 600;
}}
QPushButton:hover {{ border-color: {p['accent']}; color: {p['accent']}; background: {p['survol']}; }}
QPushButton:pressed {{ background: {p['accent_doux']}; }}
QPushButton:disabled {{ color: {p['texte3']}; border-color: {p['bord']}; }}
QPushButton[classe="primaire"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {p['accent']}, stop:1 {p['accent2']});
    color: {p['accent_sur']}; border: none;
    padding: 11px 22px; font-size: 14px; font-weight: 700;
}}
QPushButton[classe="primaire"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {p['accent2']}, stop:1 {p['accent']});
}}
QPushButton[classe="primaire"]:pressed {{ background: {p['accent']}; }}
QPushButton[classe="primaire"]:disabled {{ background: {p['texte3']}; }}
QPushButton[classe="danger"] {{
    background: transparent; color: {p['danger']}; border: 1.5px solid {p['danger']};
}}
QPushButton[classe="danger"]:hover {{ background: {p['danger']}; color: white; }}
QPushButton[classe="lien"] {{
    background: transparent; border: none; color: {p['accent']};
    padding: 4px 6px; font-weight: 700;
}}
QPushButton[classe="lien"]:hover {{ text-decoration: underline; }}
QPushButton[classe="onglet"] {{
    background: transparent; border: none;
    border-left: 3px solid transparent;
    border-top-left-radius: 5px; border-bottom-left-radius: 5px;
    border-top-right-radius: 11px; border-bottom-right-radius: 11px;
    padding: 10px 12px; text-align: left; font-size: 14px; font-weight: 700;
    color: {p['texte2']};
}}
QPushButton[classe="onglet"]:hover {{ background: {p['surface2']}; color: {p['texte']}; }}
QPushButton[classe="onglet"]:checked {{
    background: {p['accent_doux']}; color: {p['accent']};
    border-left: 3px solid {p['accent']};
}}

/* ---------- champs ---------- */
QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox {{
    background: {p['entree']}; color: {p['texte']};
    border: 1.5px solid {p['bord']}; border-radius: 11px; padding: 8px 12px;
    font-size: 13.5px; selection-background-color: {p['accent']};
    selection-color: white;
}}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 2px solid {p['accent']}; padding: 7px 11px;
}}
QComboBox::drop-down {{ border: none; width: 30px; }}
QComboBox QAbstractItemView {{
    background: {p['surface']}; color: {p['texte']};
    border: 1px solid {p['bord']}; selection-background-color: {p['accent_doux']};
    selection-color: {p['texte']}; border-radius: 10px; padding: 4px;
}}
QComboBox QAbstractItemView::item {{ padding: 7px 10px; border-radius: 7px; }}

/* ---------- liste / table ---------- */
QTableWidget {{
    background: {p['surface']}; border: 1px solid {p['bord']};
    border-radius: 12px; gridline-color: {p['bord']};
    alternate-background-color: {p['surface2']};
}}
QTableWidget::item {{ padding: 6px; border-radius: 6px; }}
QTableWidget::item:selected {{ background: {p['accent_doux']}; color: {p['texte']}; }}
QHeaderView::section {{
    background: {p['surface2']}; color: {p['texte2']};
    border: none; border-bottom: 1.5px solid {p['bord']};
    padding: 9px; font-weight: 800; font-size: 12px;
}}
QTableCornerButton::section {{ background: {p['surface2']}; border: none; }}

/* ---------- défilement ---------- */
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 9px; margin: 2px; }}
QScrollBar::handle:vertical {{
    background: {p['bord']}; border-radius: 4px; min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{ background: {p['texte3']}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 9px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {p['bord']}; border-radius: 4px; min-width: 40px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ height: 0; width: 0; }}

/* ---------- divers ---------- */
QToolTip {{
    background: {p['texte']}; color: {p['surface']};
    border: none; border-radius: 7px; padding: 7px 10px; font-weight: 600;
}}
QCheckBox {{ spacing: 8px; color: {p['texte']}; font-size: 13.5px; }}
QCheckBox::indicator {{
    width: 19px; height: 19px; border-radius: 6px;
    border: 1.5px solid {p['bord']}; background: {p['entree']};
}}
QCheckBox::indicator:checked {{ background: {p['accent']}; border-color: {p['accent']}; }}
QCheckBox::indicator:checked:hover {{ background: {p['accent2']}; }}
QGroupBox {{
    border: 1px solid {p['bord']}; border-radius: 14px;
    margin-top: 14px; background: {p['surface']}; font-weight: 800;
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 14px; top: -2px;
    padding: 0 6px; color: {p['texte2']}; font-size: 13px;
}}
QFrame[classe="separateur"] {{ background: {p['bord']}; max-height: 1px; border: none; }}
QLabel[classe="pastille"] {{
    border-radius: 11px; padding: 3px 12px; font-size: 12px; font-weight: 800;
}}
QFrame[classe="barre_titre"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {p['accent']}, stop:1 {p['accent2']});
    border-radius: 2px; max-height: 4px;
}}

/* ---------- états du pipeline ---------- */
QLabel[etat="attente"] {{ color: {p['texte3']}; }}
QLabel[etat="encours"] {{ color: {p['accent']}; font-weight: 800; }}
QLabel[etat="fait"] {{ color: {p['succes']}; font-weight: 700; }}

/* ---------- boutons à état (modes de génération) ---------- */
QPushButton:checked {{
    background: {p['accent_doux']}; border: 1.5px solid {p['accent']}; color: {p['accent']};
}}

/* ---------- barre de progression ---------- */
QProgressBar {{
    background: {p['surface2']}; border: none; border-radius: 4px;
}}
QProgressBar::chunk {{
    border-radius: 4px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {p['accent']}, stop:1 {p['accent2']});
}}
"""


# ------------------------------------------------------------------ application

def police_app() -> QFont:
    """Police de base, confortable à lire."""
    for famille in ("Segoe UI Variable Display", "Segoe UI", "Inter",
                    "Noto Sans", "Ubuntu", "Helvetica Neue"):
        police = QFont(famille, 10)
        if police.exactMatch() or famille == "Segoe UI":
            return police
    return QFont()


def appliquer_theme(app, nom_theme: str) -> str:
    """Applique la feuille de style ; renvoie le nom réellement utilisé."""
    if nom_theme == "systeme":
        nom = theme_systeme()
    else:
        nom = nom_theme
    app.setStyleSheet(qss(palette(nom)))
    # couleurs de base pour les widgets hors QSS (sélections, menus contextuels…)
    p = palette(nom)
    base = QPalette()
    base.setColor(QPalette.ColorRole.Window, QColor(p["fenetre"]))
    base.setColor(QPalette.ColorRole.Base, QColor(p["surface"]))
    base.setColor(QPalette.ColorRole.Text, QColor(p["texte"]))
    base.setColor(QPalette.ColorRole.Highlight, QColor(p["accent"]))
    base.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(base)
    return nom
