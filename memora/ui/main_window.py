"""Fenêtre principale de Memora : barre latérale + pile de vues."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from memora import __version__
from memora.ui import icons, theme
from memora.ui.contexte import Contexte
from memora.ui.views.edit_view import EditView
from memora.ui.views.fiche_view import FicheView
from memora.ui.views.home_view import HomeView
from memora.ui.views.import_view import ImportView
from memora.ui.views.library_view import LibraryView
from memora.ui.views.settings_view import SettingsView
from memora.ui.widgets import afficher_toast
from memora.utils.logging_setup import logger

_log = logger("ui.main")

# index des pages du stack
PAGE_ACCUEIL, PAGE_BIBLIOTHEQUE, PAGE_NOUVELLE, PAGE_FAVORIS, PAGE_PARAMETRES, PAGE_FICHE, PAGE_EDITION = range(7)


class FenetrePrincipale(QMainWindow):
    def __init__(self, contexte: Contexte):
        super().__init__()
        self.contexte = contexte
        self.setWindowTitle(f"Memora — tes fiches de révision")
        self.resize(1240, 800)
        self.setMinimumSize(1000, 660)

        self._derniere_page = PAGE_ACCUEIL

        racine = QWidget()
        racine.setObjectName("racine")
        disposition = QHBoxLayout(racine)
        disposition.setContentsMargins(0, 0, 0, 0)
        disposition.setSpacing(0)
        self.setCentralWidget(racine)

        disposition.addWidget(self._construire_barre())
        self.pile = QStackedWidget()

        # --- vues
        self.vue_accueil = HomeView(self.contexte)
        self.vue_bibliotheque = LibraryView(self.contexte, favoris_only=False)
        self.vue_import = ImportView(self.contexte)
        self.vue_favoris = LibraryView(self.contexte, favoris_only=True)
        self.vue_parametres = SettingsView(self.contexte)
        self.vue_fiche = FicheView(self.contexte)
        self.vue_edition = EditView(self.contexte)

        for vue in (self.vue_accueil, self.vue_bibliotheque, self.vue_import,
                    self.vue_favoris, self.vue_parametres, self.vue_fiche, self.vue_edition):
            self.pile.addWidget(self._embaler(vue))

        disposition.addWidget(self.pile, 1)
        self._brancher_signaux()
        self._construire_raccourcis()

        self.appliquer_theme()
        self.aller_a(PAGE_ACCUEIL)

    # ------------------------------------------------------------------ montage
    def _embaler(self, vue: QWidget) -> QScrollArea:
        zone = QScrollArea()
        zone.setWidgetResizable(True)
        zone.setFrameShape(QFrame.Shape.NoFrame)
        conteneur = QWidget()
        colonne = QVBoxLayout(conteneur)
        colonne.setContentsMargins(28, 24, 28, 24)
        colonne.setSpacing(0)
        colonne.addWidget(vue)
        colonne.addStretch(1)
        zone.setWidget(conteneur)
        zone.setStyleSheet("QScrollArea{background:transparent;}")
        return zone

    def _construire_barre(self) -> QFrame:
        self.barre_laterale = QFrame()
        barre = self.barre_laterale
        barre.setObjectName("barreLaterale")
        barre.setFixedWidth(224)
        colonne = QVBoxLayout(barre)
        colonne.setContentsMargins(16, 20, 16, 16)
        colonne.setSpacing(4)

        self.logo = QLabel("🧠  Memora")
        colonne.addWidget(self.logo)

        self._groupe_nav = QButtonGroup(self)
        self._groupe_nav.setExclusive(True)
        self._boutons_nav: dict[int, QPushButton] = {}

        entrees = [
            (PAGE_ACCUEIL, "accueil", "Accueil"),
            (PAGE_BIBLIOTHEQUE, "livre", "Bibliothèque"),
            (PAGE_NOUVELLE, "plus", "Nouvelle fiche"),
            (PAGE_FAVORIS, "etoile", "Favoris"),
            (PAGE_PARAMETRES, "reglages", "Paramètres"),
        ]
        for page, nom_icone, libelle in entrees:
            b = QPushButton(f"  {libelle}")
            b.setProperty("classe", "onglet")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b._nom_icone = nom_icone  # pour re-styler au changement de thème
            b.clicked.connect(lambda _=False, p=page: self.aller_a(p))
            self._groupe_nav.addButton(b, page)
            colonne.addWidget(b)
            self._boutons_nav[page] = b

        colonne.addStretch(1)

        self.bouton_theme = QPushButton()
        self.bouton_theme.setProperty("classe", "onglet")
        self.bouton_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bouton_theme.clicked.connect(self.basculer_theme)
        colonne.addWidget(self.bouton_theme)

        self.version = QLabel(f"Memora {__version__} · révision locale")
        colonne.addWidget(self.version)
        self._styliser_barre()
        return barre

    def _styliser_barre(self) -> None:
        p = self._palette()
        self.barre_laterale.setStyleSheet(
            f"QFrame#barreLaterale{{background:{p['barre']};"
            f"border-right:1px solid {p['bord']};}}"
        )
        self.logo.setStyleSheet(
            f"color:{p['accent']};font-size:21px;font-weight:800;"
            "padding:2px 8px 18px 8px;"
        )
        self.version.setStyleSheet(f"color:{p['texte3']};font-size:11px;padding:6px;")
        for b in self._boutons_nav.values():
            b.setIcon(icons.icone(b._nom_icone, p["texte2"], 19))
        self._maj_bouton_theme()

    def _construire_raccourcis(self) -> None:
        QShortcut(QKeySequence("Ctrl+N"), self, lambda: self.aller_a(PAGE_NOUVELLE))
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self.aller_a(PAGE_BIBLIOTHEQUE))
        QShortcut(QKeySequence("Ctrl+E"), self, lambda: self.aller_a(PAGE_PARAMETRES))

    def _brancher_signaux(self) -> None:
        c = self.contexte
        c.bibliotheque_changee.connect(self._sur_bibliotheque_changee)
        c.theme_change.connect(lambda _: None)

        v = self.vue_accueil
        v.importer_demande.connect(lambda: self.aller_a(PAGE_NOUVELLE))
        v.ouvrir_fiche.connect(self.ouvrir_fiche)
        v.voir_bibliotheque.connect(lambda: self.aller_a(PAGE_BIBLIOTHEQUE))
        v.demo_demande.connect(self.charger_demo)

        self.vue_bibliotheque.ouvrir_fiche.connect(self.ouvrir_fiche)
        self.vue_bibliotheque.importer_demande.connect(lambda: self.aller_a(PAGE_NOUVELLE))
        self.vue_favoris.ouvrir_fiche.connect(self.ouvrir_fiche)
        self.vue_favoris.importer_demande.connect(lambda: self.aller_a(PAGE_NOUVELLE))

        self.vue_import.fiche_creee.connect(self._sur_fiche_creee)

        fv = self.vue_fiche
        fv.retour_demande.connect(self.retour)
        fv.modifier_demande.connect(self.modifier_fiche)
        fv.supprimee.connect(self._sur_fiche_supprimee)
        fv.regenerer_demande.connect(self.regenerer_fiche)

        ev = self.vue_edition
        ev.termine.connect(lambda fiche: self.ouvrir_fiche(fiche.id))
        ev.theme_change.connect(lambda nom: self.appliquer_theme())

        sv = self.vue_parametres
        sv.theme_change.connect(self.appliquer_theme_par_nom)
        sv.demo_chargee.connect(self._sur_bibliotheque_changee)

    # ------------------------------------------------------------------ thème
    def _palette(self) -> dict:
        return theme.palette(self.contexte.reglages.theme if self.contexte.reglages.theme != "systeme" else "clair")

    def appliquer_theme(self) -> None:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        nom = theme.appliquer_theme(app, self.contexte.reglages.theme)
        self.contexte.theme_actuel = nom
        self._styliser_barre()

    def appliquer_theme_par_nom(self, nom: str) -> None:
        self.contexte.reglages.theme = nom
        self.contexte.sauver_reglages()
        self.appliquer_theme()

    def basculer_theme(self) -> None:
        cible = "sombre" if self.contexte.theme_actuel == "clair" else "clair"
        self.appliquer_theme_par_nom(cible)

    def _maj_bouton_theme(self) -> None:
        sombre = self.contexte.theme_actuel == "sombre"
        p = self._palette()
        self.bouton_theme.setText(f"  {'Thème clair' if sombre else 'Thème sombre'}")
        self.bouton_theme.setIcon(icons.icone("soleil" if sombre else "lune", p["texte2"], 18))

    # ------------------------------------------------------------------ navigation
    def aller_a(self, page: int) -> None:
        if self.pile.currentIndex() != page:
            self._derniere_page = self.pile.currentIndex()
        self.pile.setCurrentIndex(page)
        if page in self._boutons_nav:
            self._boutons_nav[page].setChecked(True)
        if page == PAGE_ACCUEIL:
            self.vue_accueil.rafraichir()
        elif page == PAGE_BIBLIOTHEQUE:
            self.vue_bibliotheque.rafraichir()
        elif page == PAGE_FAVORIS:
            self.vue_favoris.rafraichir()
        elif page == PAGE_NOUVELLE:
            self.vue_import.rafraichir()

    def retour(self) -> None:
        cible = self._derniere_page
        if cible in (PAGE_FICHE, PAGE_EDITION):
            cible = PAGE_BIBLIOTHEQUE
        self.aller_a(cible)

    def ouvrir_fiche(self, id_fiche: int) -> None:
        if self.vue_fiche.charge(id_fiche):
            self._derniere_page = self.pile.currentIndex()
            self.pile.setCurrentIndex(PAGE_FICHE)
            self._boutons_nav.get(PAGE_BIBLIOTHEQUE).setChecked(True)

    def modifier_fiche(self, fiche) -> None:
        self.vue_edition.charge(fiche)
        self.pile.setCurrentIndex(PAGE_EDITION)

    def regenerer_fiche(self, fiche) -> None:
        from memora.utils import files

        if fiche.source_chemin and files.fichier_existe(fiche.source_chemin):
            self.vue_import.pre_remplir(fiche.source_chemin, mode=fiche.mode_generation)
            self.aller_a(PAGE_NOUVELLE)
            afficher_toast(self, "Document source rechargé : relance l'analyse pour régénérer la fiche.", "info")
        else:
            QMessageBox.information(
                self, "Régénération impossible",
                "Le document original n'est plus accessible sur ce PC.\n\n"
                "Importe à nouveau le cours depuis l'onglet « Nouvelle fiche ».",
            )

    # ------------------------------------------------------------------ événements
    def _sur_fiche_creee(self, fiche) -> None:
        self.contexte.bibliotheque_changee.emit()
        self.ouvrir_fiche(fiche.id)
        afficher_toast(self, f"Fiche « {fiche.titre} » créée 🎉", "succes")

    def _sur_fiche_supprimee(self) -> None:
        self.contexte.bibliotheque_changee.emit()
        afficher_toast(self, "Fiche supprimée.", "info")
        self.aller_a(PAGE_BIBLIOTHEQUE)

    def _sur_bibliotheque_changee(self) -> None:
        self.vue_accueil.rafraichir()
        self.vue_bibliotheque.rafraichir()
        self.vue_favoris.rafraichir()

    def charger_demo(self) -> None:
        from memora.core.demo import fiches_demo

        nb = 0
        for fiche in fiches_demo():
            self.contexte.base.ajouter_fiche(fiche)
            nb += 1
        self.contexte.reglages.demo_charge = True
        self.contexte.sauver_reglages()
        self.contexte.bibliotheque_changee.emit()
        afficher_toast(self, f"{nb} fiches de démonstration ajoutées (marquées « Démo »).", "succes")
        self.aller_a(PAGE_BIBLIOTHEQUE)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.vue_import.arreter_worker()
        super().closeEvent(event)
