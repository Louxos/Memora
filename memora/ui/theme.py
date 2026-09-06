"""Thème visuel de Memora : palettes clair / sombre + feuille QSS.

Design volontairement sobre et premium : une couleur d'accent (indigo),
des surfaces en cartes arrondies, une typographie lisible.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QPalette

# ------------------------------------------------------------------ palettes

CLAIR = {
    "nom": "clair",
    "fenetre": "#F3F4F8",
    "surface": "#FFFFFF",
    "surface2": "#F8F9FC",
    "barre": "#FFFFFF",
    "texte": "#1B1F2E",
    "texte2": "#5B6274",
    "texte3": "#9CA3AF",
    "bord": "#E4E7EF",
    "accent": "#5B5FE9",
    "accent_sur": "#FFFFFF",
    "accent_doux": "#EEF0FE",
    "succes": "#30A46C",
    "attention": "#F5A524",
    "danger": "#E5484D",
    "ombre": "rgba(27, 31, 46, 18)",
    "entree": "#FFFFFF",
}

SOMBRE = {
    "nom": "sombre",
    "fenetre": "#12141D",
    "surface": "#1C1F2E",
    "surface2": "#222637",
    "barre": "#171A26",
    "texte": "#E9EBF4",
    "texte2": "#A6ACC2",
    "texte3": "#6E7590",
    "bord": "#2C3145",
    "accent": "#7C7FF2",
    "accent_sur": "#FFFFFF",
    "accent_doux": "#2A2D4A",
    "succes": "#3DD68C",
    "attention": "#FFB224",
    "danger": "#FF6369",
    "ombre": "rgba(0, 0, 0, 90)",
    "entree": "#222637",
}


def palette(nom: str) -> dict:
    return SOMBRE if nom == "sombre" else CLAIR


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
QLabel[classe="titre1"] {{ font-size: 26px; font-weight: 800; }}
QLabel[classe="titre2"] {{ font-size: 18px; font-weight: 700; }}
QLabel[classe="titre3"] {{ font-size: 15px; font-weight: 700; }}
QLabel[classe="muet"] {{ color: {p['texte2']}; }}
QLabel[classe="tres_muet"] {{ color: {p['texte3']}; font-size: 12px; }}
QLabel[classe="accent"] {{ color: {p['accent']}; }}

/* ---------- cartes ---------- */
QFrame[classe="carte"] {{
    background: {p['surface']};
    border: 1px solid {p['bord']};
    border-radius: 14px;
}}
QFrame[classe="carte2"] {{
    background: {p['surface2']};
    border: 1px solid {p['bord']};
    border-radius: 12px;
}}
QFrame[classe="encadre"] {{
    background: {p['accent_doux']};
    border: 1px solid {p['accent']};
    border-radius: 12px;
}}

/* ---------- boutons ---------- */
QPushButton {{
    background: {p['surface']};
    color: {p['texte']};
    border: 1px solid {p['bord']};
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 13.5px;
    font-weight: 600;
}}
QPushButton:hover {{ border-color: {p['accent']}; color: {p['accent']}; }}
QPushButton:pressed {{ background: {p['accent_doux']}; }}
QPushButton:disabled {{ color: {p['texte3']}; border-color: {p['bord']}; }}
QPushButton[classe="primaire"] {{
    background: {p['accent']}; color: {p['accent_sur']}; border: none;
    padding: 10px 20px; font-size: 14px; font-weight: 700;
}}
QPushButton[classe="primaire"]:hover {{ background: {p['accent']}; opacity: 0.92; }}
QPushButton[classe="primaire"]:disabled {{ background: {p['texte3']}; }}
QPushButton[classe="danger"] {{
    background: transparent; color: {p['danger']}; border: 1px solid {p['danger']};
}}
QPushButton[classe="danger"]:hover {{ background: {p['danger']}; color: white; }}
QPushButton[classe="lien"] {{
    background: transparent; border: none; color: {p['accent']};
    padding: 4px 6px; font-weight: 600;
}}
QPushButton[classe="lien"]:hover {{ text-decoration: underline; }}
QPushButton[classe="onglet"] {{
    background: transparent; border: none; border-radius: 10px;
    padding: 10px 14px; text-align: left; font-size: 14px; font-weight: 600;
    color: {p['texte2']};
}}
QPushButton[classe="onglet"]:hover {{ background: {p['surface2']}; color: {p['texte']}; }}
QPushButton[classe="onglet"]:checked {{ background: {p['accent_doux']}; color: {p['accent']}; }}

/* ---------- champs ---------- */
QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox {{
    background: {p['entree']}; color: {p['texte']};
    border: 1px solid {p['bord']}; border-radius: 10px; padding: 8px 12px;
    font-size: 13.5px; selection-background-color: {p['accent']};
}}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 2px solid {p['accent']}; padding: 7px 11px;
}}
QComboBox::drop-down {{ border: none; width: 30px; }}
QComboBox QAbstractItemView {{
    background: {p['surface']}; color: {p['texte']};
    border: 1px solid {p['bord']}; selection-background-color: {p['accent_doux']};
    selection-color: {p['texte']}; border-radius: 8px; padding: 4px;
}}
QComboBox QAbstractItemView::item {{ padding: 6px 10px; border-radius: 6px; }}

/* ---------- liste / table ---------- */
QTableWidget {{
    background: {p['surface']}; border: 1px solid {p['bord']};
    border-radius: 10px; gridline-color: {p['bord']};
}}
QTableWidget::item {{ padding: 6px; }}
QHeaderView::section {{
    background: {p['surface2']}; color: {p['texte2']};
    border: none; border-bottom: 1px solid {p['bord']};
    padding: 8px; font-weight: 700; font-size: 12.5px;
}}
QTableCornerButton::section {{ background: {p['surface2']}; border: none; }}

/* ---------- défilement ---------- */
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QScrollBar:vertical {{
    background: transparent; width: 10px; margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {p['bord']}; border-radius: 5px; min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{ background: {p['texte3']}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {p['bord']}; border-radius: 5px; min-width: 40px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ height: 0; width: 0; }}

/* ---------- divers ---------- */
QToolTip {{
    background: {p['surface']}; color: {p['texte']};
    border: 1px solid {p['bord']}; border-radius: 6px; padding: 6px;
}}
QCheckBox {{ spacing: 8px; color: {p['texte']}; font-size: 13.5px; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border-radius: 5px;
    border: 1px solid {p['bord']}; background: {p['entree']};
}}
QCheckBox::indicator:checked {{ background: {p['accent']}; border-color: {p['accent']}; }}
QGroupBox {{
    border: 1px solid {p['bord']}; border-radius: 12px;
    margin-top: 14px; background: {p['surface']}; font-weight: 700;
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 14px; top: -2px;
    padding: 0 6px; color: {p['texte2']}; font-size: 13px;
}}
QFrame[classe="separateur"] {{ background: {p['bord']}; max-height: 1px; border: none; }}
QLabel[classe="pastille"] {{
    border-radius: 11px; padding: 3px 12px; font-size: 12px; font-weight: 700;
}}

/* ---------- états du pipeline ---------- */
QLabel[etat="attente"] {{ color: {p['texte3']}; }}
QLabel[etat="encours"] {{ color: {p['accent']}; font-weight: 700; }}
QLabel[etat="fait"] {{ color: {p['succes']}; font-weight: 600; }}

/* ---------- boutons à état (modes de génération) ---------- */
QPushButton:checked {{ background: {p['accent_doux']}; border: 1.5px solid {p['accent']}; color: {p['accent']}; }}

/* ---------- barre de progression ---------- */
QProgressBar {{
    background: {p['surface2']}; border: none; border-radius: 4px;
}}
QProgressBar::chunk {{ background: {p['accent']}; border-radius: 4px; }}
"""


# ------------------------------------------------------------------ application

def police_app() -> QFont:
    """Police de base, confortable à lire."""
    for famille in ("Segoe UI", "Inter", "Noto Sans", "Ubuntu", "Helvetica Neue"):
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
    return nom
