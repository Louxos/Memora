"""Vue Accueil : salutation, import rapide, statistiques, dernières fiches."""

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
        colonne.setSpacing(20)

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
        colonne.addWidget(date_lab)

        # --- grande carte d'import
        p = theme.palette("clair")
        carte_import = Carte("encadre")
        corps = QHBoxLayout()
        corps.setContentsMargins(6, 4, 6, 4)
        carte_import.layout().addLayout(corps)
        texte_col = QVBoxLayout()
        texte_col.setSpacing(4)
        titre_cta = QLabel("Importer un cours")
        titre_cta.setStyleSheet(f"color:{p['accent']};font-size:17px;font-weight:800;")
        sous_cta = etiquette(
            "PDF, Word, image ou photo — Memora l'analyse et crée une fiche de révision complète.",
            "muet",
        )
        texte_col.addWidget(titre_cta)
        texte_col.addWidget(sous_cta)
        corps.addLayout(texte_col, 1)
        self.bouton_import = bouton("＋ Importer un document", "primaire", "importer", 20, "#FFFFFF")
        self.bouton_import.setMinimumHeight(46)
        self.bouton_import.clicked.connect(self.importer_demande.emit)
        corps.addWidget(self.bouton_import)
        colonne.addWidget(carte_import)

        # --- statistiques
        self.grille_stats = QGridLayout()
        self.grille_stats.setSpacing(14)
        colonne.addLayout(self.grille_stats)

        # --- dernières fiches
        self.titre_recentes = QLabel("Dernières fiches")
        self.titre_recentes.setProperty("classe", "titre2")
        colonne.addWidget(self.titre_recentes)
        self.zone_recentes = QVBoxLayout()
        self.zone_recentes.setSpacing(8)
        colonne.addLayout(self.zone_recentes)

        self.bouton_voir = bouton("Voir toute la bibliothèque", "lien", "liste")
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
