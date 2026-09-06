"""Rendu visuel de chaque type de section dans la vue de lecture.

Chaque type de section a une mise en page adaptée : blocs pour les notions,
boîtes monospace pour les formules, étapes numérotées pour les méthodes,
réponses masquées pour les questions…
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from memora.ui.widgets import Pastille, bouton, etiquette

ICONES_DPE = {"date": "📅", "personne": "👤", "événement": "⚡"}

# Couleur d'accent de chaque section (barre latérale de la carte)
SECTION_ACCENTS = {
    "objectif": "#6366F1",
    "essentiel": "#8B5CF6",
    "notions": "#3B82F6",
    "definitions": "#22C55E",
    "formules": "#F97316",
    "methodes": "#EC4899",
    "dates_personnages": "#EAB308",
    "exemples": "#14B8A6",
    "pieges": "#EF4444",
    "retenir": "#F43F5E",
    "questions": "#64748B",
    "avertissements": "#D97706",
}


# ------------------------------------------------------------------ helpers

def _texte_riche(texte: str, taille: int = 14) -> QLabel:
    """QLabel avec **gras** et *italique* interprétés."""
    label = QLabel()
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setWordWrap(True)
    label.setStyleSheet(f"font-size:{taille}px;line-height:1.45;")
    return label


def _vers_html(texte: str) -> str:
    import html as module_html
    import re

    t = module_html.escape(texte or "")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", t)
    return t


def _bloc_liste(corps: QVBoxLayout, items: list[str], p: dict, puce: str = "•",
                couleur_puce: str | None = None, gras: bool = False) -> None:
    for item in items:
        ligne = QHBoxLayout()
        ligne.setSpacing(10)
        puce_lab = QLabel(puce)
        puce_lab.setStyleSheet(
            f"color:{couleur_puce or p['accent']};font-size:15px;font-weight:800;"
        )
        puce_lab.setFixedWidth(20)
        puce_lab.setAlignment(Qt.AlignmentFlag.AlignTop)
        texte = _texte_riche(item)
        if gras:
            texte.setStyleSheet(
                f"font-size:14.5px;font-weight:600;color:{p['texte']};line-height:1.5;"
            )
        ligne.addWidget(puce_lab)
        ligne.addWidget(texte, 1)
        conteneur = QWidget()
        conteneur.setLayout(ligne)
        corps.addWidget(conteneur)


def _boite(corps: QVBoxLayout, fond: str, bord: str, widget: QWidget) -> None:
    boite = QFrame()
    boite.setStyleSheet(
        f"QFrame{{background:{fond};border:1px solid {bord};border-radius:10px;}}"
    )
    lay = QVBoxLayout(boite)
    lay.setContentsMargins(14, 10, 14, 10)
    lay.addWidget(widget)
    corps.addWidget(boite)


# ------------------------------------------------------------------ dispatch

def rendre_section(corps: QVBoxLayout, cle: str, contenu: dict, p: dict) -> None:
    if cle == "objectif":
        _rendre_objectif(corps, contenu["objectif"], p)
    elif cle == "essentiel":
        _bloc_liste(corps, contenu["essentiel"], p, "◆")
    elif cle == "notions":
        _rendre_notions(corps, contenu["notions"], p)
    elif cle == "definitions":
        _rendre_definitions(corps, contenu["definitions"], p)
    elif cle == "formules":
        _rendre_formules(corps, contenu["formules"], p)
    elif cle == "methodes":
        _rendre_methodes(corps, contenu["methodes"], p)
    elif cle == "dates_personnages":
        _rendre_dpe(corps, contenu["dates_personnages"], p)
    elif cle == "exemples":
        _bloc_liste(corps, contenu["exemples"], p, "💡")
    elif cle == "pieges":
        _rendre_pieges(corps, contenu["pieges"], p)
    elif cle == "retenir":
        _rendre_retenir(corps, contenu["retenir"], p)
    elif cle == "questions":
        _rendre_questions(corps, contenu["questions"], p)
    elif cle == "avertissements":
        _rendre_avertissements(corps, contenu["avertissements"], p)


# ------------------------------------------------------------------ sections

def _rendre_objectif(corps: QVBoxLayout, texte: str, p: dict) -> None:
    label = _texte_riche(texte)
    label.setStyleSheet(
        f"font-size:14.5px;font-style:italic;color:{p['texte']};line-height:1.5;"
    )
    _boite(corps, p["accent_doux"], p["accent"], label)


def _rendre_notions(corps: QVBoxLayout, notions: list[dict], p: dict) -> None:
    for notion in notions:
        bloc = QFrame()
        bloc.setProperty("classe", "carte2")
        lay = QVBoxLayout(bloc)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(4)
        nom = QLabel(notion.get("nom", ""))
        nom.setStyleSheet(f"font-size:14.5px;font-weight:800;color:{p['accent']};")
        nom.setWordWrap(True)
        lay.addWidget(nom)
        if notion.get("explication"):
            explication = _texte_riche(notion["explication"])
            lay.addWidget(explication)
        if notion.get("exemple"):
            exemple = QLabel(f"💡 <i>{_vers_html(notion['exemple'])}</i>")
            exemple.setTextFormat(Qt.TextFormat.RichText)
            exemple.setWordWrap(True)
            exemple.setStyleSheet(f"font-size:13px;color:{p['texte2']};")
            lay.addWidget(exemple)
        corps.addWidget(bloc)


def _rendre_definitions(corps: QVBoxLayout, definitions: list[dict], p: dict) -> None:
    grille = QGridLayout()
    grille.setVerticalSpacing(10)
    grille.setHorizontalSpacing(14)
    for i, definition in enumerate(definitions):
        terme = QLabel(definition.get("terme", ""))
        terme.setStyleSheet(f"font-size:14.5px;font-weight:800;color:{p['succes']};")
        terme.setWordWrap(True)
        texte = _texte_riche(definition.get("definition", ""))
        grille.addWidget(terme, i, 0)
        grille.addWidget(texte, i, 1)
        grille.setColumnStretch(1, 1)
    conteneur = QWidget()
    conteneur.setLayout(grille)
    corps.addWidget(conteneur)


def _rendre_formules(corps: QVBoxLayout, formules: list[dict], p: dict) -> None:
    for formule in formules:
        bloc = QFrame()
        bloc.setProperty("classe", "carte2")
        lay = QVBoxLayout(bloc)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(6)
        formule_lab = QLabel(formule.get("formule", ""))
        formule_lab.setStyleSheet(
            "font-family:'Consolas','Cascadia Mono',monospace;font-size:16px;"
            f"font-weight:700;color:#C2410C;"
        )
        formule_lab.setWordWrap(True)
        formule_lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(formule_lab)
        for cle, libelle in (
            ("signification", ""), ("unite", "Unité : "),
            ("conditions", "Quand l'utiliser : "), ("exemple", "Exemple : "),
        ):
            if formule.get(cle):
                ligne = QLabel(
                    (f"<b>{libelle}</b>" if libelle else "") + _vers_html(formule[cle])
                )
                ligne.setTextFormat(Qt.TextFormat.RichText)
                ligne.setWordWrap(True)
                ligne.setStyleSheet(f"font-size:13.5px;color:{p['texte2']};")
                lay.addWidget(ligne)
        corps.addWidget(bloc)


def _rendre_methodes(corps: QVBoxLayout, methodes: list[dict], p: dict) -> None:
    for methode in methodes:
        bloc = QFrame()
        bloc.setProperty("classe", "carte2")
        lay = QVBoxLayout(bloc)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(8)
        titre = QLabel(methode.get("titre", ""))
        titre.setStyleSheet(f"font-size:14.5px;font-weight:800;color:{p['texte']};")
        titre.setWordWrap(True)
        lay.addWidget(titre)
        etapes = methode.get("etapes") or []
        for i, etape in enumerate(etapes, 1):
            ligne = QHBoxLayout()
            ligne.setSpacing(10)
            numero = QLabel(str(i))
            numero.setFixedSize(22, 22)
            numero.setAlignment(Qt.AlignmentFlag.AlignCenter)
            numero.setStyleSheet(
                f"background:{p['accent']};color:white;border-radius:11px;"
                "font-size:12px;font-weight:800;"
            )
            texte = _texte_riche(etape)
            ligne.addWidget(numero)
            ligne.addWidget(texte, 1)
            conteneur = QWidget()
            conteneur.setLayout(ligne)
            lay.addWidget(conteneur)
        corps.addWidget(bloc)


def _rendre_dpe(corps: QVBoxLayout, elements: list[dict], p: dict) -> None:
    for element in elements:
        ligne = QHBoxLayout()
        ligne.setSpacing(10)
        icone = QLabel(ICONES_DPE.get(element.get("type", ""), "•"))
        icone.setFixedWidth(24)
        icone.setAlignment(Qt.AlignmentFlag.AlignTop)
        colonne = QVBoxLayout()
        colonne.setSpacing(2)
        nom = QLabel(element.get("nom", ""))
        nom.setStyleSheet("font-size:14.5px;font-weight:700;")
        nom.setWordWrap(True)
        info = _texte_riche(element.get("info", ""), 13.5)
        info.setStyleSheet(f"font-size:13.5px;color:{p['texte2']};")
        colonne.addWidget(nom)
        colonne.addWidget(info)
        ligne.addWidget(icone)
        ligne.addLayout(colonne, 1)
        conteneur = QWidget()
        conteneur.setLayout(ligne)
        corps.addWidget(conteneur)


def _rendre_pieges(corps: QVBoxLayout, pieges: list[str], p: dict) -> None:
    _bloc_liste(corps, pieges, p, "⚠️", couleur_puce=p["danger"], gras=True)


def _rendre_retenir(corps: QVBoxLayout, retenir: list[str], p: dict) -> None:
    for item in retenir:
        bloc = QFrame()
        bloc.setStyleSheet(
            f"QFrame{{background:#FFF1F2;border:1.5px solid #BE123C;border-radius:10px;}}"
        )
        lay = QHBoxLayout(bloc)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(10)
        label = QLabel(f"🔥  <b>{_vers_html(item)}</b>")
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setStyleSheet("font-size:14.5px;color:#9F1239;")
        lay.addWidget(label, 1)
        corps.addWidget(bloc)


def _rendre_avertissements(corps: QVBoxLayout, avertissements: list[str], p: dict) -> None:
    for texte in avertissements:
        label = QLabel(f"🔎 <i>{_vers_html(texte)}</i>")
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setStyleSheet(f"font-size:13.5px;color:#92600D;")
        _boite(corps, "#FFFBEB", p["attention"], label)


def _rendre_questions(corps: QVBoxLayout, questions: list[dict], p: dict) -> None:
    reponses: list[QWidget] = []
    for i, question in enumerate(questions, 1):
        bloc = QFrame()
        bloc.setProperty("classe", "carte2")
        lay = QVBoxLayout(bloc)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(6)
        enonce = QLabel(f"<b>{i}.</b>  {_vers_html(question.get('question', ''))}")
        enonce.setTextFormat(Qt.TextFormat.RichText)
        enonce.setWordWrap(True)
        enonce.setStyleSheet("font-size:14.5px;")
        lay.addWidget(enonce)
        if question.get("type"):
            lay.addWidget(Pastille(question["type"], "#EEF0FE", p["accent"]))
        reponse = QLabel(f"<b>Réponse :</b> {_vers_html(question.get('reponse', ''))}")
        reponse.setTextFormat(Qt.TextFormat.RichText)
        reponse.setWordWrap(True)
        reponse.setStyleSheet(
            f"font-size:13.5px;color:{p['texte']};background:{p['surface']};"
            "border-radius:8px;padding:10px 12px;border:1px dashed " + p["bord"] + ";"
        )
        reponse.setVisible(False)
        lay.addWidget(reponse)
        reponses.append(reponse)
        corps.addWidget(bloc)

    bouton_reponses = bouton("👁️  Afficher les réponses", "primaire", "oeil", 18, "#FFFFFF")

    def basculer() -> None:
        visible = not reponses[0].isVisible() if reponses else True
        for r in reponses:
            r.setVisible(visible)
        bouton_reponses.setText("🙈  Masquer les réponses" if visible else "👁️  Afficher les réponses")

    bouton_reponses.clicked.connect(basculer)
    bouton_reponses.setMinimumHeight(42)
    bouton_reponses.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    corps.addSpacing(4)
    corps.addWidget(bouton_reponses)
