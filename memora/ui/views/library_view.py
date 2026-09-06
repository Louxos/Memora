"""Vue Bibliothèque : recherche, filtres, tri et organisation par matière/chapitre."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from memora.core.models import STATUTS, couleur_matiere
from memora.ui import icons, theme
from memora.ui.contexte import Contexte
from memora.ui.widgets import (
    EtatVide,
    LigneFiche,
    bouton,
    etiquette,
)

TRIS = [
    ("recent", "Plus récentes"),
    ("ancien", "Plus anciennes"),
    ("alpha", "Ordre alphabétique"),
]

STATUTS_FILTRES = [("Tous les statuts", "")] + [(label, code) for code, label, _ in STATUTS]


class LibraryView(QWidget):
    ouvrir_fiche = Signal(int)
    importer_demande = Signal()

    def __init__(self, contexte: Contexte, favoris_only: bool = False, parent=None):
        super().__init__(parent)
        self.contexte = contexte
        self.favoris_only = favoris_only
        self._timer_recherche = QTimer(self)
        self._timer_recherche.setSingleShot(True)
        self._timer_recherche.setInterval(260)
        self._timer_recherche.timeout.connect(self.rafraichir)

        colonne = QVBoxLayout(self)
        colonne.setContentsMargins(0, 8, 0, 20)
        colonne.setSpacing(16)

        # --- entête
        titre = QLabel("⭐ Favoris" if favoris_only else "📚 Bibliothèque")
        titre.setProperty("classe", "titre1")
        colonne.addWidget(titre)
        self.sous_titre = etiquette(
            "Tes fiches mises de côté" if favoris_only
            else "Toutes tes fiches, organisées par matière et chapitre",
            "muet",
        )
        colonne.addWidget(self.sous_titre)

        # --- barre de recherche + tri
        p = theme.palette("clair")
        barre = QHBoxLayout()
        barre.setSpacing(10)
        self.champ_recherche = QLineEdit()
        self.champ_recherche.setPlaceholderText("Rechercher (titre, matière, contenu…)")
        self.champ_recherche.setClearButtonEnabled(True)
        self.champ_recherche.addAction(
            self._action_icone(self.champ_recherche, "recherche", p["texte3"]),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.champ_recherche.textChanged.connect(lambda _: self._timer_recherche.start())
        barre.addWidget(self.champ_recherche, 1)

        self.combo_tri = QComboBox()
        for code, libelle in TRIS:
            self.combo_tri.addItem(libelle, code)
        self.combo_tri.currentIndexChanged.connect(self.rafraichir)
        barre.addWidget(self.combo_tri)
        colonne.addLayout(barre)

        # --- filtres
        filtres = QHBoxLayout()
        filtres.setSpacing(10)
        self.combo_matiere = QComboBox()
        self.combo_chapitre = QComboBox()
        self.combo_statut = QComboBox()
        for libelle, code in STATUTS_FILTRES:
            self.combo_statut.addItem(libelle, code)
        self.combo_matiere.currentIndexChanged.connect(self._sur_matiere_changee)
        self.combo_chapitre.currentIndexChanged.connect(self.rafraichir)
        self.combo_statut.currentIndexChanged.connect(self.rafraichir)
        filtres.addWidget(etiquette("Matière", "tres_muet"))
        filtres.addWidget(self.combo_matiere)
        filtres.addSpacing(8)
        filtres.addWidget(etiquette("Chapitre", "tres_muet"))
        filtres.addWidget(self.combo_chapitre)
        filtres.addSpacing(8)
        filtres.addWidget(etiquette("Statut", "tres_muet"))
        filtres.addWidget(self.combo_statut)
        filtres.addStretch(1)
        if not favoris_only:
            self.bouton_favoris = QPushButton("Favoris")
            self.bouton_favoris.setCheckable(True)
            self.bouton_favoris.setToolTip("N'afficher que les favoris")
            self.bouton_favoris.toggled.connect(self.rafraichir)
            filtres.addWidget(self.bouton_favoris)
        colonne.addLayout(filtres)

        # --- zone de résultats
        self.zone_resultats = QVBoxLayout()
        self.zone_resultats.setSpacing(6)
        colonne.addLayout(self.zone_resultats)
        colonne.addStretch(1)

        self.rafraichir()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _action_icone(champ: QLineEdit, nom: str, couleur: str):
        from PySide6.QtGui import QAction

        action = QAction(champ)
        action.setIcon(icons.icone(nom, couleur, 16))
        return action

    # ------------------------------------------------------------------ filtres
    def _sur_matiere_changee(self) -> None:
        self._remplir_chapitres()
        self.rafraichir()

    def _remplir_matieres(self) -> None:
        matieres = self.contexte.base.matieres()
        self.combo_matiere.blockSignals(True)
        self.combo_matiere.clear()
        self.combo_matiere.addItem("Toutes", "")
        for m in matieres:
            self.combo_matiere.addItem(m, m)
        self.combo_matiere.blockSignals(False)

    def _remplir_chapitres(self) -> None:
        matiere = self.combo_matiere.currentData()
        chapitres = self.contexte.base.chapitres(matiere or None)
        self.combo_chapitre.blockSignals(True)
        self.combo_chapitre.clear()
        self.combo_chapitre.addItem("Tous", "")
        for c in chapitres:
            self.combo_chapitre.addItem(c, c)
        self.combo_chapitre.blockSignals(False)

    # ------------------------------------------------------------------ contenu
    def rafraichir(self) -> None:
        base = self.contexte.base
        self._remplir_matieres()
        self._remplir_chapitres()

        favori = True if self.favoris_only else (
            self.bouton_favoris.isChecked() if hasattr(self, "bouton_favoris") else None
        )
        fiches = base.lister(
            matiere=self.combo_matiere.currentData() or None,
            chapitre=self.combo_chapitre.currentData() or None,
            statut=(self.combo_statut.currentData() or None) if self.combo_statut.currentData() else None,
            favori=favori,
            recherche=self.champ_recherche.text().strip() or None,
            tri=self.combo_tri.currentData() or "recent",
        )

        # vide la zone
        while self.zone_resultats.count():
            item = self.zone_resultats.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sous = item.layout().takeAt(0)
                    if sous.widget():
                        sous.widget().deleteLater()

        if not fiches:
            if self.favoris_only:
                vide = EtatVide("etoile", "Aucun favori",
                                "Clique sur l'étoile d'une fiche pour la retrouver ici.")
            else:
                vide = EtatVide("livre", "Aucune fiche trouvée",
                                "Modifie ta recherche ou importe un nouveau cours.")
                bouton_import = bouton("＋ Importer un document", "primaire", "importer", 18, "#FFFFFF")
                bouton_import.clicked.connect(self.importer_demande.emit)
                conteneur = QVBoxLayout()
                conteneur.setContentsMargins(0, 10, 0, 0)
                conteneur.setAlignment(Qt.AlignmentFlag.AlignCenter)
                conteneur.addWidget(bouton_import)
                vide.layout().addLayout(conteneur)
            self.zone_resultats.addWidget(vide)
            return

        # groupement matière → chapitre
        par_matiere: dict[str, dict[str, list]] = {}
        for fiche in fiches:
            matiere = fiche.matiere or "Sans matière"
            chapitre = fiche.chapitre or "Autres"
            par_matiere.setdefault(matiere, {}).setdefault(chapitre, []).append(fiche)

        for matiere, chapitres in sorted(par_matiere.items(), key=lambda x: x[0].lower()):
            couleur = couleur_matiere(matiere)
            entete_matiere = QFrame()
            entete_matiere.setProperty("classe", "carte2")
            lay_m = QHBoxLayout(entete_matiere)
            lay_m.setContentsMargins(16, 10, 16, 10)
            point = QLabel()
            point.setFixedSize(10, 10)
            point.setStyleSheet(f"background:{couleur};border-radius:5px;")
            titre_m = QLabel(matiere)
            titre_m.setStyleSheet(f"font-size:15px;font-weight:800;color:{couleur};")
            nb = sum(len(l) for l in chapitres.values())
            compteur = etiquette(f"{nb} fiche{'s' if nb > 1 else ''}", "tres_muet")
            lay_m.addWidget(point)
            lay_m.addSpacing(10)
            lay_m.addWidget(titre_m)
            lay_m.addStretch(1)
            lay_m.addWidget(compteur)
            self.zone_resultats.addWidget(entete_matiere)

            for chapitre, liste in sorted(chapitres.items(), key=lambda x: x[0].lower()):
                if len(chapitres) > 1 or chapitre != "Autres":
                    titre_c = etiquette(f"→  {chapitre}", "muet")
                    titre_c.setStyleSheet("font-weight:600;padding:2px 4px;")
                    self.zone_resultats.addWidget(titre_c)
                for fiche in liste:
                    ligne = LigneFiche(fiche)
                    ligne.clic.connect(self.ouvrir_fiche.emit)
                    ligne.favori_bascule.connect(self._basculer_favori)
                    self.zone_resultats.addWidget(ligne)

    def _basculer_favori(self, id_fiche: int) -> None:
        fiche = self.contexte.base.obtenir_fiche(id_fiche)
        if fiche:
            self.contexte.base.maj_champ(id_fiche, "favori", 0 if fiche.favori else 1)
            self.rafraichir()
