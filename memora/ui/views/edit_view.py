"""Vue d'édition manuelle d'une fiche.

Métadonnées + éditeur par section (texte, listes, tableaux, méthodes,
questions). Sauvegarde explicite avec le bouton « Enregistrer ».
"""

from __future__ import annotations

import copy

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from memora.core.models import SECTIONS, SECTION_TITRES, STATUTS
from memora.ui import theme
from memora.ui.contexte import Contexte
from memora.ui.widgets import Carte, bouton, etiquette

NIVEAUX_EDITION = ["6e", "5e", "4e", "3e", "2nde", "1re", "Terminale"]


# ------------------------------------------------------------------ éditeurs

class EditeurSection(QFrame):
    """Base d'un éditeur de section."""

    def __init__(self, cle: str, titre: str, emoji: str, sur_retrait, parent=None):
        super().__init__(parent)
        self.cle = cle
        self.setProperty("classe", "carte")
        disposition = QVBoxLayout(self)
        disposition.setContentsMargins(18, 14, 18, 16)
        disposition.setSpacing(10)
        entete = QHBoxLayout()
        titre_lab = QLabel(f"{emoji}  {titre}")
        titre_lab.setStyleSheet("font-size:15px;font-weight:800;")
        entete.addWidget(titre_lab)
        entete.addStretch(1)
        bouton_retirer = bouton("Retirer cette section", "", "poubelle", 14, "#E5484D")
        bouton_retirer.setStyleSheet("color:#E5484D;padding:4px 8px;")
        bouton_retirer.clicked.connect(lambda: sur_retrait(cle))
        entete.addWidget(bouton_retirer)
        disposition.addLayout(entete)
        self.zone = QVBoxLayout()
        self.zone.setSpacing(8)
        disposition.addLayout(self.zone)

    def donnees(self):  # à surcharger
        return None


class EditeurTexte(EditeurSection):
    def __init__(self, cle, titre, emoji, valeur: str, sur_retrait, parent=None):
        super().__init__(cle, titre, emoji, sur_retrait, parent)
        self.champ = QPlainTextEdit()
        self.champ.setPlainText(valeur or "")
        self.champ.setMinimumHeight(72)
        self.champ.setMaximumHeight(160)
        self.zone.addWidget(self.champ)

    def donnees(self) -> str:
        return self.champ.toPlainText().strip()


class EditeurListe(EditeurSection):
    def __init__(self, cle, titre, emoji, items: list[str], sur_retrait, parent=None):
        super().__init__(cle, titre, emoji, sur_retrait, parent)
        self.champ = QPlainTextEdit()
        self.champ.setPlainText("\n".join(items))
        self.champ.setMinimumHeight(110)
        aide = etiquette("Un élément par ligne.", "tres_muet")
        self.zone.addWidget(self.champ)
        self.zone.addWidget(aide)

    def donnees(self) -> list[str]:
        return [l.strip() for l in self.champ.toPlainText().splitlines() if l.strip()]


class EditeurTable(EditeurSection):
    """Éditeur générique de listes d'objets sous forme de tableau."""

    def __init__(self, cle, titre, emoji, colonnes: list[tuple[str, str]],
                 lignes: list[dict], sur_retrait, hauteur_max: int = 300, parent=None):
        super().__init__(cle, titre, emoji, sur_retrait, parent)
        self.colonnes = colonnes
        self.table = QTableWidget(max(len(lignes), 1), len(colonnes))
        self.table.setHorizontalHeaderLabels([c for c, _ in colonnes])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setHighlightSections(False)
        for i, ligne in enumerate(lignes):
            for j, (_, cle_champ) in enumerate(colonnes):
                self.table.setItem(i, j, QTableWidgetItem(str(ligne.get(cle_champ, "") or "")))
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked
            | QTableWidget.EditTrigger.EditKeyPressed
            | QTableWidget.EditTrigger.AnyKeyPressed
        )
        hauteur = min(hauteur_max, 48 + 38 * max(len(lignes), 1))
        self.table.setMinimumHeight(min(hauteur, hauteur_max))
        self.table.setMaximumHeight(hauteur_max)
        self.zone.addWidget(self.table)

        barre = QHBoxLayout()
        ajouter = bouton("＋ Ajouter une ligne", "lien", "plus", 14)
        ajouter.clicked.connect(self._ajouter_ligne)
        supprimer = bouton("Supprimer la ligne sélectionnée", "lien", "poubelle", 14)
        supprimer.clicked.connect(self._supprimer_ligne)
        barre.addWidget(ajouter)
        barre.addWidget(supprimer)
        barre.addStretch(1)
        self.zone.addLayout(barre)

    def _ajouter_ligne(self) -> None:
        self.table.insertRow(self.table.rowCount())

    def _supprimer_ligne(self) -> None:
        ligne = self.table.currentRow()
        if ligne >= 0:
            self.table.removeRow(ligne)

    def donnees(self) -> list[dict]:
        resultat = []
        for i in range(self.table.rowCount()):
            objet = {}
            for j, (_, cle_champ) in enumerate(self.colonnes):
                item = self.table.item(i, j)
                objet[cle_champ] = item.text().strip() if item else ""
            if any(objet.values()):
                resultat.append(objet)
        return resultat


class EditeurMethodes(EditeurSection):
    """Éditeur spécifique des méthodes (titre + étapes ligne par ligne)."""

    def __init__(self, cle, titre, emoji, methodes: list[dict], sur_retrait, parent=None):
        super().__init__(cle, titre, emoji, sur_retrait, parent)
        self.blocs: list[dict] = []
        for methode in methodes:
            self._ajouter_bloc(methode.get("titre", ""),
                               methode.get("etapes") or [])
        ajouter = bouton("＋ Ajouter une méthode", "lien", "plus", 14)
        ajouter.clicked.connect(lambda: self._ajouter_bloc("", []))
        self.zone.addStretch(1)
        self.zone.addWidget(ajouter)

    def _ajouter_bloc(self, titre: str, etapes: list[str]) -> None:
        cadre = QFrame()
        cadre.setProperty("classe", "carte2")
        disposition = QVBoxLayout(cadre)
        disposition.setContentsMargins(14, 10, 14, 10)
        disposition.setSpacing(6)
        champ_titre = QLineEdit(titre)
        champ_titre.setPlaceholderText("Titre de la méthode (ex. : Comment factoriser ?)")
        champ_etapes = QPlainTextEdit()
        champ_etapes.setPlainText("\n".join(etapes))
        champ_etapes.setPlaceholderText("Une étape par ligne")
        champ_etapes.setFixedHeight(104)
        bouton_suppr = bouton("Supprimer cette méthode", "lien", "poubelle", 14)
        disposition.addWidget(champ_titre)
        disposition.addWidget(champ_etapes)
        disposition.addWidget(bouton_suppr)
        self.zone.addWidget(cadre)
        bloc = {"cadre": cadre, "titre": champ_titre, "etapes": champ_etapes}
        self.blocs.append(bloc)
        bouton_suppr.clicked.connect(lambda: self._supprimer_bloc(bloc))

    def _supprimer_bloc(self, bloc: dict) -> None:
        bloc["cadre"].setParent(None)
        self.blocs.remove(bloc)

    def donnees(self) -> list[dict]:
        resultat = []
        for bloc in self.blocs:
            titre = bloc["titre"].text().strip()
            etapes = [l.strip() for l in bloc["etapes"].toPlainText().splitlines() if l.strip()]
            if titre or etapes:
                resultat.append({"titre": titre, "etapes": etapes})
        return resultat


# ------------------------------------------------------------------ vue

class EditView(QWidget):
    termine = Signal(object)          # fiche enregistrée (ou édition annulée)
    theme_change = Signal(str)

    def __init__(self, contexte: Contexte, parent=None):
        super().__init__(parent)
        self.contexte = contexte
        self.fiche = None
        self.editeurs: dict[str, EditeurSection] = {}

        disposition = QVBoxLayout(self)
        disposition.setContentsMargins(0, 4, 0, 20)
        disposition.setSpacing(14)

        entete = QHBoxLayout()
        titre = QLabel("✏️  Modifier la fiche")
        titre.setProperty("classe", "titre2")
        entete.addWidget(titre)
        entete.addStretch(1)
        bouton_annuler = bouton("Annuler", "", "croix")
        bouton_annuler.clicked.connect(self._annuler)
        bouton_enregistrer = bouton("💾  Enregistrer", "primaire", "check", 18, "#FFFFFF")
        bouton_enregistrer.clicked.connect(self._enregistrer)
        entete.addWidget(bouton_annuler)
        entete.addWidget(bouton_enregistrer)
        disposition.addLayout(entete)

        colonnes = QHBoxLayout()
        colonnes.setSpacing(16)
        colonnes.addWidget(self._construire_colonne_infos(), 0)
        colonnes.addWidget(self._construire_colonne_sections(), 1)
        disposition.addLayout(colonnes)
        disposition.addStretch(1)

    # ------------------------------------------------------------------ colonnes
    def _construire_colonne_infos(self) -> QWidget:
        carte = Carte()
        carte.setFixedWidth(320)
        carte.layout().addWidget(etiquette("Informations", "titre3"))

        self.champ_titre = QLineEdit()
        self.champ_titre.setPlaceholderText("Titre de la fiche")
        carte.layout().addWidget(etiquette("Titre", "tres_muet"))
        carte.layout().addWidget(self.champ_titre)

        self.combo_matiere = QComboBox()
        self.combo_matiere.setEditable(True)
        self.combo_matiere.addItems(
            ["Mathématiques", "Français", "Histoire", "Géographie", "SVT",
             "Physique-Chimie", "Anglais", "Espagnol", "Technologie", "EMC"]
        )
        carte.layout().addWidget(etiquette("Matière", "tres_muet"))
        carte.layout().addWidget(self.combo_matiere)

        self.champ_chapitre = QLineEdit()
        carte.layout().addWidget(etiquette("Chapitre", "tres_muet"))
        carte.layout().addWidget(self.champ_chapitre)

        self.champ_theme = QLineEdit()
        carte.layout().addWidget(etiquette("Thème", "tres_muet"))
        carte.layout().addWidget(self.champ_theme)

        self.combo_niveau = QComboBox()
        self.combo_niveau.addItems(NIVEAUX_EDITION)
        carte.layout().addWidget(etiquette("Niveau", "tres_muet"))
        carte.layout().addWidget(self.combo_niveau)

        self.champ_tags = QLineEdit()
        self.champ_tags.setPlaceholderText("séparés par des virgules")
        carte.layout().addWidget(etiquette("Tags", "tres_muet"))
        carte.layout().addWidget(self.champ_tags)

        self.combo_statut = QComboBox()
        for code, label, _ in STATUTS:
            self.combo_statut.addItem(label, code)
        carte.layout().addWidget(etiquette("Statut", "tres_muet"))
        carte.layout().addWidget(self.combo_statut)

        self.case_favori = QCheckBox("Fiche en favori")
        carte.layout().addWidget(self.case_favori)
        return carte

    def _construire_colonne_sections(self) -> QWidget:
        conteneur = QScrollArea()
        conteneur.setWidgetResizable(True)
        conteneur.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        interieur = QWidget()
        self.colonne_sections = QVBoxLayout(interieur)
        self.colonne_sections.setContentsMargins(0, 0, 8, 0)
        self.colonne_sections.setSpacing(14)
        conteneur.setWidget(interieur)
        return conteneur

    # ------------------------------------------------------------------ chargement
    def charge(self, fiche) -> None:
        self.fiche = copy.deepcopy(fiche)
        self.editeurs = {}

        self.champ_titre.setText(fiche.titre)
        self.combo_matiere.setCurrentText(fiche.matiere or "")
        self.champ_chapitre.setText(fiche.chapitre or "")
        self.champ_theme.setText(fiche.theme or "")
        self.combo_niveau.setCurrentText(fiche.niveau or "3e")
        self.champ_tags.setText(fiche.tags or "")
        index_statut = max(0, [c for c, _, _ in STATUTS].index(fiche.statut)) if fiche.statut in [c for c, _, _ in STATUTS] else 0
        self.combo_statut.setCurrentIndex(index_statut)
        self.case_favori.setChecked(fiche.favori)

        self._construire_sections()

    def _vider_sections(self) -> None:
        while self.colonne_sections.count():
            item = self.colonne_sections.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _construire_sections(self) -> None:
        self._vider_sections()
        contenu = self.fiche.contenu
        c = contenu

        spec = self._spec_sections()
        for cle in ["objectif", "essentiel", "notions", "definitions", "formules",
                    "methodes", "dates_personnages", "exemples", "pieges",
                    "retenir", "questions", "avertissements"]:
            _, titre, emoji = next(s for s in SECTIONS if s[0] == cle)
            constructeur, args = spec[cle]
            editeur = constructeur(cle, titre, emoji, *args, self._retirer_section)
            self.editeurs[cle] = editeur
            self.colonne_sections.addWidget(editeur)

        # ajout de section
        barre_ajout = QHBoxLayout()
        self.combo_ajout = QComboBox()
        self._remplir_combo_ajout()
        bouton_ajouter = bouton("＋ Ajouter la section", "", "plus", 15)
        bouton_ajouter.clicked.connect(self._ajouter_section)
        barre_ajout.addWidget(self.combo_ajout, 1)
        barre_ajout.addWidget(bouton_ajouter)
        conteneur = QWidget()
        conteneur.setLayout(barre_ajout)
        self.colonne_sections.addWidget(conteneur)
        self.colonne_sections.addStretch(1)

    def _spec_sections(self):
        c = self.fiche.contenu
        return {
            "objectif": (EditeurTexte, (c.get("objectif", ""),)),
            "essentiel": (EditeurListe, (c.get("essentiel", []),)),
            "notions": (EditeurTable, (
                [("Nom", "nom"), ("Explication", "explication"), ("Exemple", "exemple")],
                c.get("notions", []),)),
            "definitions": (EditeurTable, (
                [("Terme", "terme"), ("Définition", "definition")],
                c.get("definitions", []),)),
            "formules": (EditeurTable, (
                [("Formule", "formule"), ("Signification", "signification"),
                 ("Unité", "unite"), ("Conditions", "conditions"), ("Exemple", "exemple")],
                c.get("formules", []),)),
            "methodes": (EditeurMethodes, (c.get("methodes", []),)),
            "dates_personnages": (EditeurTable, (
                [("Type (date / personne / événement)", "type"), ("Nom", "nom"),
                 ("Pourquoi c'est important", "info")],
                c.get("dates_personnages", []),)),
            "exemples": (EditeurListe, (c.get("exemples", []),)),
            "pieges": (EditeurListe, (c.get("pieges", []),)),
            "retenir": (EditeurListe, (c.get("retenir", []),)),
            "questions": (EditeurTable, (
                [("Question", "question"), ("Réponse", "reponse"),
                 ("Type", "type")],
                c.get("questions", []),)),
            "avertissements": (EditeurListe, (c.get("avertissements", []),)),
        }

    def _remplir_combo_ajout(self) -> None:
        self.combo_ajout.clear()
        absentes = [
            (cle, titre) for cle, titre, _ in SECTIONS
            if cle not in self.editeurs
        ]
        if absentes:
            for cle, titre in absentes:
                self.combo_ajout.addItem(titre, cle)
            self.combo_ajout.setEnabled(True)
        else:
            self.combo_ajout.addItem("Toutes les sections sont affichées", "")
            self.combo_ajout.setEnabled(False)

    def _ajouter_section(self) -> None:
        cle = self.combo_ajout.currentData()
        if not cle:
            return
        self.fiche.contenu.setdefault(cle, [] if cle != "objectif" else "")
        self._construire_sections()

    def _retirer_section(self, cle: str) -> None:
        self.editeurs.pop(cle, None)
        self.fiche.contenu.pop(cle, None)
        self._construire_sections()

    # ------------------------------------------------------------------ enregistrement
    def _collecter(self) -> dict:
        contenu = {}
        for cle, editeur in self.editeurs.items():
            contenu[cle] = editeur.donnees()
        return contenu

    def _enregistrer(self) -> None:
        from memora.core.models import coercer_contenu

        fiche = self.fiche
        fiche.titre = self.champ_titre.text().strip() or "Sans titre"
        fiche.matiere = self.combo_matiere.currentText().strip()
        fiche.chapitre = self.champ_chapitre.text().strip()
        fiche.theme = self.champ_theme.text().strip()
        fiche.niveau = self.combo_niveau.currentText().strip()
        fiche.tags = self.champ_tags.text().strip()
        fiche.statut = self.combo_statut.currentData()
        fiche.favori = self.case_favori.isChecked()
        fiche.contenu = coercer_contenu(self._collecter())
        self.contexte.base.maj_fiche(fiche)
        self.contexte.bibliotheque_changee.emit()
        from memora.ui.widgets import afficher_toast

        afficher_toast(self.window(), "Fiche enregistrée ✅", "succes")
        self.termine.emit(fiche)

    def _annuler(self) -> None:
        self.termine.emit(self.fiche)
