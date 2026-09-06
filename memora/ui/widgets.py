"""Composants d'interface réutilisables (cartes, badges, états vides, toasts)."""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractAnimation,
    QPropertyAnimation,
    QEasingCurve,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from memora.ui import icons, theme


# ------------------------------------------------------------------ helpers

def etiquette(texte: str = "", classe: str = "", parent=None) -> QLabel:
    lab = QLabel(texte, parent)
    lab.setProperty("classe", classe)
    lab.setWordWrap(True)
    return lab


def bouton(texte: str, classe: str = "", nom_icone: str = "", taille_icone: int = 18,
           couleur_icone: str = "") -> QPushButton:
    """Bouton stylé par propriété QSS + éventuelle icône vectorielle."""
    b = QPushButton(texte)
    if classe:
        b.setProperty("classe", classe)
    if nom_icone:
        b.setIcon(icons.icone(nom_icone, couleur_icone or couleur_icone_bouton(classe), taille_icone))
        b.setIconSize(b.icon().actualSize(b.size()))
    return b


def couleur_icone_bouton(classe: str) -> str:
    p = theme.palette("clair")
    if classe == "primaire":
        return p["accent_sur"]
    if classe == "danger":
        return p["danger"]
    return p["texte2"]


class Carte(QFrame):
    """Surface arrondie standard."""

    def __init__(self, variante: str = "carte", parent=None):
        super().__init__(parent)
        self.setProperty("classe", variante)
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(20, 18, 20, 18)
        self.layout().setSpacing(12)


class Pastille(QLabel):
    """Petit badge coloré (matière, statut…)."""

    def __init__(self, texte: str, fond: str, texte_couleur: str = "#FFFFFF", parent=None):
        super().__init__(texte, parent)
        self.setStyleSheet(
            f"background:{fond};color:{texte_couleur};border-radius:11px;"
            "padding:3px 12px;font-size:12px;font-weight:700;"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)


class CarteStat(QFrame):
    """Carte de statistique de l'accueil : icône en pastille colorée + valeur."""

    def __init__(self, nom_icone: str, valeur: str, libelle: str, couleur: str, parent=None):
        super().__init__(parent)
        self.setProperty("classe", "carte")
        self.setFixedHeight(96)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(14)

        pastille_icone = QFrame()
        pastille_icone.setFixedSize(48, 48)
        pastille_icone.setStyleSheet(
            f"QFrame{{background:{couleur}1A;border-radius:15px;border: none;}}"  # teinte 10 %
        )
        sous_lay = QVBoxLayout(pastille_icone)
        sous_lay.setContentsMargins(0, 0, 0, 0)
        icone_lab = QLabel()
        icone_lab.setPixmap(icons.icone(nom_icone, couleur, 24).pixmap(24, 24))
        icone_lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sous_lay.addWidget(icone_lab)
        lay.addWidget(pastille_icone)

        colonne = QVBoxLayout()
        colonne.setSpacing(0)
        self.valeur = etiquette(valeur, "titre2")
        self.libelle = etiquette(libelle, "tres_muet")
        colonne.addWidget(self.valeur)
        colonne.addWidget(self.libelle)
        lay.addLayout(colonne)
        lay.addStretch(1)

    def maj(self, valeur: str) -> None:
        self.valeur.setText(valeur)


class EtatVide(QWidget):
    """Message affiché quand une liste est vide."""

    def __init__(self, nom_icone: str, titre: str, sous_titre: str = "", parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 46, 40, 46)
        lay.setSpacing(10)
        p = theme.palette("clair")
        halo = QFrame()
        halo.setFixedSize(88, 88)
        halo.setStyleSheet(
            f"QFrame{{background:{p['accent']}14;border-radius:28px;border:none;}}"
        )
        halo_lay = QVBoxLayout(halo)
        halo_lay.setContentsMargins(0, 0, 0, 0)
        icone_lab = QLabel()
        icone_lab.setPixmap(icons.icone(nom_icone, p["texte3"], 40).pixmap(40, 40))
        icone_lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        halo_lay.addWidget(icone_lab)
        conteneur_halo = QHBoxLayout()
        conteneur_halo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        conteneur_halo.addWidget(halo)
        lay.addLayout(conteneur_halo)
        titre_lab = etiquette(titre, "titre3")
        titre_lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sous_lab = etiquette(sous_titre, "tres_muet")
        sous_lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(titre_lab)
        lay.addWidget(sous_lab)


class LigneFiche(QFrame):
    """Rangée cliquable représentant une fiche (accueil, bibliothèque)."""

    clic = Signal(int)
    favori_bascule = Signal(int)

    def __init__(self, fiche, parent=None):
        super().__init__(parent)
        from memora.core.models import STATUT_COULEURS, couleur_matiere

        self.id_fiche = fiche.id
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("classe", "carte")
        couleur = couleur_matiere(fiche.matiere)
        # barre latérale colorée par matière (le fond vient du thème global)
        self.setStyleSheet(
            f"QFrame{{border-left:4px solid {couleur};}}"
            f"QFrame:hover{{border-left:4px solid {couleur};}}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 14, 12)
        lay.setSpacing(12)

        colonne = QVBoxLayout()
        colonne.setSpacing(4)
        titre = etiquette(fiche.titre, "titre3")
        titre_lay = QHBoxLayout()
        titre_lay.setSpacing(8)
        titre_lay.addWidget(titre)
        if fiche.demo:
            pastille_demo = Pastille("DÉMO", "#9CA3AF")
            titre_lay.addWidget(pastille_demo)
        titre_lay.addStretch(1)
        meta = QHBoxLayout()
        meta.setSpacing(8)
        if fiche.matiere:
            meta.addWidget(Pastille(fiche.matiere, couleur_matiere(fiche.matiere)))
        if fiche.statut in STATUT_COULEURS:
            meta.addWidget(Pastille(fiche.statut_label(), STATUT_COULEURS[fiche.statut]))
        info = "  •  ".join(x for x in (fiche.chapitre, (fiche.date_creation or "")[:10]) if x)
        meta.addWidget(etiquette(info, "tres_muet"))
        meta.addStretch(1)
        colonne.addLayout(titre_lay)
        colonne.addLayout(meta)
        lay.addLayout(colonne, 1)

        self.bouton_favori = QPushButton()
        self.bouton_favori.setFlat(True)
        self.bouton_favori.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bouton_favori.setToolTip("Mettre en favori / retirer")
        couleur = "#F5A524" if fiche.favori else "#C4C9D4"
        self.bouton_favori.setIcon(icons.icone("etoile", couleur, 20))
        self.bouton_favori.setIconSize(QSize(20, 20))
        self.bouton_favori.clicked.connect(
            lambda: self.favori_bascule.emit(self.id_fiche)
        )
        lay.addWidget(self.bouton_favori)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clic.emit(self.id_fiche)
        super().mousePressEvent(event)


# ------------------------------------------------------------------ toast

_TOAST_STYLE = {
    "succes": ("#30A46C", "#E9FBF2"),
    "info": ("#5B5FE9", "#EEF0FE"),
    "erreur": ("#E5484D", "#FDECEC"),
}


def afficher_toast(parent: QWidget, message: str, genre: str = "info", duree_ms: int = 3200) -> None:
    """Notification discrète en bas de fenêtre, avec fondu."""
    bord, fond = _TOAST_STYLE.get(genre, _TOAST_STYLE["info"])
    toast = QLabel(message, parent)
    toast.setWordWrap(True)
    toast.setMaximumWidth(460)
    toast.setStyleSheet(
        f"background:{fond};color:{bord};border:1.5px solid {bord};"
        "border-radius:12px;padding:12px 18px;font-size:13.5px;font-weight:600;"
    )
    toast.adjustSize()
    toast.move(
        (parent.width() - toast.width()) // 2,
        parent.height() - toast.height() - 26,
    )
    effet = QGraphicsOpacityEffect(toast)
    toast.setGraphicsEffect(effet)
    fondu = QPropertyAnimation(effet, b"opacity", toast)
    fondu.setDuration(220)
    fondu.setStartValue(0.0)
    fondu.setEndValue(1.0)
    fondu.setEasingCurve(QEasingCurve.Type.OutCubic)
    fondu.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    toast.show()
    toast.raise_()

    def cacher() -> None:
        sortie = QPropertyAnimation(effet, b"opacity", toast)
        sortie.setDuration(260)
        sortie.setStartValue(1.0)
        sortie.setEndValue(0.0)
        sortie.finished.connect(toast.deleteLater)
        sortie.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    QTimer.singleShot(duree_ms, cacher)


def apparition(widget: QWidget, duree_ms: int = 180) -> None:
    """Léger fondu d'apparition (retour visuel sans ralentir l'usage).

    L'effet est détaché à la fin de l'animation : un QGraphicsOpacityEffect
    resté attaché dégrade le rendu (bordures QSS) et les performances.
    L'animation est parentée au widget pour ne pas être recyclée avant la fin.
    """
    effet = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effet)
    anim = QPropertyAnimation(effet, b"opacity", widget)
    anim.setDuration(duree_ms)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.finished.connect(lambda: widget.setGraphicsEffect(None))
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
