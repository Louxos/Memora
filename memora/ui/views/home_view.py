"""Vue Accueil : salutation, héros d'importation, statistiques, dernières fiches."""

from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from memora.core.models import STATUT_A_APPRENDRE
from memora.ui import icons, theme
from memora.ui.contexte import Contexte
from memora.ui.widgets import (
    Carte,
    CarteStat,
    EtatVide,
    LigneFiche,
    apparition,
    bouton,
    etiquette,
)

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def _barre_titre() -> QFrame:
    """Petite barre dégradée sous les titres de section."""
    barre = QFrame()
    barre.setProperty("classe", "barre_titre")
    barre.setFixedWidth(64)
    return barre


class HomeView(QWidget):
    importer_demande = Signal()
    ouvrir_fiche = Signal(int)
    voir_bibliotheque = Signal()
    demo_demande = Signal()

    def __init__(self, contexte: Contexte, parent=None):
        super().__init__(parent)
        self.contexte = contexte
        colonne = QVBoxLayout(self)
        colonne.setContentsMargins(0, 8, 0, 20)
        colonne.setSpacing(18)

        # --- salutation
        aujourdhui = date.today()
        salutation = QLabel("Bonjour 👋")
        salutation.setProperty("classe", "titre1")
        question = QLabel("Que veux-tu réviser aujourd'hui ?")
        question.setProperty("classe", "titre2")
        date_lab = etiquette(
            f"{JOURS[aujourdhui.weekday()]} {aujourdhui.day} {MOIS[aujourdhui.month - 1]} {aujourdhui.year}",
            "muet",
        )
        colonne.addWidget(salutation)
        colonne.addWidget(question)
        colonne.addWidget(_barre_titre())
        colonne.addWidget(date_lab)

        # --- héros : grande carte dégradée d'import
        p = theme.palette("clair")
        hero = QFrame()
        hero.setStyleSheet(
            f"QFrame{{border:none;border-radius:18px;"
            f"background:{theme.degrade(p)};}}"
        )
        hero_lay = QHBoxLayout(hero)
        hero_lay.setContentsMargins(30, 26, 30, 26)
        hero_lay.setSpacing(20)

        texte_col = QVBoxLayout()
        texte_col.setSpacing(6)
        kicker = QLabel("NOUVELLE FICHE")
        kicker.setStyleSheet(
            "color:rgba(255,255,255,0.75);font-size:11px;font-weight:800;"
            "letter-spacing:2px;background:transparent;"
        )
        titre_hero = QLabel("Transforme un cours en fiche de révision")
        titre_hero.setStyleSheet(
            "color:#FFFFFF;font-size:21px;font-weight:800;background:transparent;"
        )
        sous_hero = QLabel(
            "PDF, Word, image ou photo — Memora l'analyse et crée une fiche claire, "
            "complète et prête à réviser."
        )
        sous_hero.setWordWrap(True)
        sous_hero.setStyleSheet(
            "color:rgba(255,255,255,0.85);font-size:13.5px;background:transparent;"
        )
        texte_col.addWidget(kicker)
        texte_col.addWidget(titre_hero)
        texte_col.addWidget(sous_hero)
        hero_lay.addLayout(texte_col, 1)

        emoji_hero = QLabel("🚀")
        emoji_hero.setStyleSheet(
            "font-size:56px;background:transparent;border:none;"
        )
        hero_lay.addWidget(emoji_hero)

        self.bouton_import = QPushButton("＋  Importer un document")
        self.bouton_import.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bouton_import.setStyleSheet(
            "QPushButton{background:#FFFFFF;color:#4F46E5;border:none;"
            "border-radius:12px;padding:13px 24px;font-size:14.5px;font-weight:800;}"
            "QPushButton:hover{background:#F0F1FF;}"
        )
        self.bouton_import.setMinimumHeight(50)
        self.bouton_import.clicked.connect(self.importer_demande.emit)
        hero_lay.addWidget(self.bouton_import, 0, Qt.AlignmentFlag.AlignVCenter)
        colonne.addWidget(hero)

        # --- statistiques
        self.grille_stats = QGridLayout()
        self.grille_stats.setSpacing(14)
        colonne.addLayout(self.grille_stats)

        # --- dernières fiches
        entete_recentes = QHBoxLayout()
        self.titre_recentes = QLabel("Dernières fiches")
        self.titre_recentes.setProperty("classe", "titre2")
        entete_recentes.addWidget(self.titre_recentes)
        entete_recentes.addStretch(1)
        colonne.addLayout(entete_recentes)
        self.zone_recentes = QVBoxLayout()
        self.zone_recentes.setSpacing(8)
        colonne.addLayout(self.zone_recentes)

        self.bouton_voir = bouton("Voir toute la bibliothèque  →", "lien", "liste")
        self.bouton_voir.clicked.connect(self.voir_bibliotheque.emit)
        colonne.addWidget(self.bouton_voir)
        colonne.addStretch(1)

        self.rafraichir()

    # ------------------------------------------------------------------ rafraîchissement
    def rafraichir(self) -> None:
        base = self.contexte.base
        stats = base.stats()

        # nettoie puis reconstruit les cartes stats
        while self.grille_stats.count():
            item = self.grille_stats.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        p = theme.palette("clair")
        cartes = [
            CarteStat("fichier", str(stats["total"]), "Fiches", p["accent"]),
            CarteStat("livre", str(stats["matieres"]), "Matières", "#D9730D"),
            CarteStat("coeur", str(stats["favoris"]), "Favoris", "#D6409F"),
            CarteStat("cible", str(stats["a_apprendre"]), "À apprendre", "#E5484D"),
        ]
        for i, carte in enumerate(cartes):
            self.grille_stats.addWidget(carte, 0, i)

        # dernières fiches
        while self.zone_recentes.count():
            item = self.zone_recentes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        recentes = base.lister(tri="recent")[:5]
        self.titre_recentes.setVisible(True)
        self.bouton_voir.setVisible(len(recentes) > 0)

        if not recentes:
            if stats["total"] == 0:
                vide = EtatVide(
                    "etincelle",
                    "Ta bibliothèque est vide",
                    "Importe ton premier cours, ou charge les données de démonstration "
                    "pour découvrir Memora sans clé API.",
                )
                demo = bouton(" Charger les données de démonstration", "primaire", "etincelle")
                demo.clicked.connect(self.demo_demande.emit)
                conteneur = QVBoxLayout()
                conteneur.setContentsMargins(0, 0, 0, 0)
                conteneur.setAlignment(Qt.AlignmentFlag.AlignCenter)
                conteneur.addWidget(demo)
                vide.layout().addLayout(conteneur)
                self.zone_recentes.addWidget(vide)
                self.bouton_voir.setVisible(False)
        else:
            for fiche in recentes:
                ligne = LigneFiche(fiche)
                ligne.clic.connect(self.ouvrir_fiche.emit)
                ligne.favori_bascule.connect(self._basculer_favori)
                self.zone_recentes.addWidget(ligne)

        apparition(self)

    def _basculer_favori(self, id_fiche: int) -> None:
        fiche = self.contexte.base.obtenir_fiche(id_fiche)
        if fiche:
            self.contexte.base.maj_champ(id_fiche, "favori", 0 if fiche.favori else 1)
            self.rafraichir()
