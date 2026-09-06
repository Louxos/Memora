"""Vue de lecture d'une fiche : page confortable, sections en cartes."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from memora.core.models import (
    SECTIONS,
    SECTION_TITRES,
    STATUTS,
    couleur_matiere,
)
from memora.export.markdown_export import fiche_vers_markdown
from memora.ui import icons, theme
from memora.ui.contexte import Contexte
from memora.ui.widgets import Carte, Pastille, apparition, bouton, etiquette
from memora.utils import files
from memora.utils.logging_setup import logger

_log = logger("ui.fiche")


class SectionCarte(QFrame):
    """Carte d'une section de fiche."""

    def __init__(self, cle: str, titre: str, emoji: str, parent=None):
        super().__init__(parent)
        self.cle = cle
        self.setProperty("classe", "carte")
        disposition = QVBoxLayout(self)
        disposition.setContentsMargins(20, 16, 20, 18)
        disposition.setSpacing(10)
        entete = QHBoxLayout()
        titre_lab = QLabel(f"{emoji}  {titre}")
        titre_lab.setStyleSheet("font-size:16px;font-weight:800;")
        entete.addWidget(titre_lab)
        entete.addStretch(1)
        disposition.addLayout(entete)
        self.corps = QVBoxLayout()
        self.corps.setSpacing(8)
        disposition.addLayout(self.corps)


class FicheView(QWidget):
    retour_demande = Signal()
    modifier_demande = Signal(object)
    regenerer_demande = Signal(object)
    supprimee = Signal()

    def __init__(self, contexte: Contexte, parent=None):
        super().__init__(parent)
        self.contexte = contexte
        self.fiche = None

        racine = QVBoxLayout(self)
        racine.setContentsMargins(0, 4, 0, 20)
        racine.setSpacing(16)

        # --- barre d'entête
        barre = QHBoxLayout()
        barre.setSpacing(10)
        self.bouton_retour = bouton("", "", "retour")
        self.bouton_retour.setFixedSize(40, 40)
        self.bouton_retour.setToolTip("Retour")
        self.bouton_retour.clicked.connect(self.retour_demande.emit)
        barre.addWidget(self.bouton_retour)

        colonne_titre = QVBoxLayout()
        colonne_titre.setSpacing(6)
        self.titre = QLabel("—")
        self.titre.setProperty("classe", "titre1")
        self.titre.setWordWrap(True)
        colonne_titre.addWidget(self.titre)
        self.badges = QHBoxLayout()
        self.badges.setSpacing(8)
        colonne_titre.addLayout(self.badges)
        barre.addLayout(colonne_titre, 1)

        self.bouton_favori = bouton("", "", "etoile")
        self.bouton_favori.setFixedSize(44, 44)
        self.bouton_favori.setToolTip("Favori")
        self.bouton_favori.clicked.connect(self._basculer_favori)
        barre.addWidget(self.bouton_favori)
        racine.addLayout(barre)

        # --- barre d'actions
        actions = QHBoxLayout()
        actions.setSpacing(8)
        p = theme.palette("clair")
        self.combo_statut = QComboBox()
        for code, label, _ in STATUTS:
            self.combo_statut.addItem(f"{label}", code)
        self.combo_statut.currentIndexChanged.connect(self._changer_statut)
        actions.addWidget(etiquette("Statut de révision :", "muet"))
        actions.addWidget(self.combo_statut)
        actions.addSpacing(14)
        for libelle, nom_icone, couleur, raccourci in [
            ("Modifier", "crayon", p["texte2"], self._modifier),
            ("Régénérer", "rafraichir", p["texte2"], self._regenerer),
            ("PDF", "exporter", p["texte2"], lambda: self._exporter_pdf()),
            ("Markdown", "fichier", p["texte2"], lambda: self._exporter_markdown()),
            ("Copier", "copier", p["texte2"], self._copier),
        ]:
            b = bouton(libelle, "", nom_icone, 16, couleur)
            b.clicked.connect(raccourci)
            actions.addWidget(b)
        actions.addStretch(1)
        self.bouton_supprimer = bouton("Supprimer", "danger", "poubelle", 16, p["danger"])
        self.bouton_supprimer.clicked.connect(self._supprimer)
        actions.addWidget(self.bouton_supprimer)
        racine.addLayout(actions)

        # --- zone de contenu défilante
        self.zone = QScrollArea()
        self.zone.setWidgetResizable(True)
        self.zone.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        self.conteneur = QWidget()
        self.colonne_contenu = QVBoxLayout(self.conteneur)
        self.colonne_contenu.setContentsMargins(0, 4, 8, 8)
        self.colonne_contenu.setSpacing(14)
        self.zone.setWidget(self.conteneur)
        racine.addWidget(self.zone, 1)

    # ------------------------------------------------------------------ chargement
    def charge(self, id_fiche: int) -> bool:
        fiche = self.contexte.base.obtenir_fiche(id_fiche)
        if fiche is None:
            return False
        self.fiche = fiche
        self.contexte.base.marquer_revision(id_fiche)
        self._construire_entete()
        self._construire_contenu()
        apparition(self.conteneur)
        return True

    # ------------------------------------------------------------------ entête
    def _construire_entete(self) -> None:
        fiche = self.fiche
        p = theme.palette("clair")
        self.titre.setText(fiche.titre)
        while self.badges.count():
            item = self.badges.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if fiche.demo:
            self.badges.addWidget(Pastille("DÉMO", "#9CA3AF"))
        if fiche.matiere:
            self.badges.addWidget(Pastille(fiche.matiere, couleur_matiere(fiche.matiere)))
        if fiche.niveau:
            self.badges.addWidget(Pastille(f"Niveau {fiche.niveau}", "#EEF0FE", p["accent"]))
        if fiche.chapitre:
            self.badges.addWidget(Pastille(fiche.chapitre, "#F3F4F8", p["texte2"]))
        if fiche.date_creation:
            self.badges.addWidget(etiquette(f"créée le {(fiche.date_creation)[:10]}", "tres_muet"))
        self.badges.addStretch(1)
        couleur = "#F5A524" if fiche.favori else "#C4C9D4"
        self.bouton_favori.setIcon(icons.icone("etoile", couleur, 22))
        index_statut = [code for code, _, _ in STATUTS].index(fiche.statut) if fiche.statut in [c for c, _, _ in STATUTS] else 0
        self.combo_statut.blockSignals(True)
        self.combo_statut.setCurrentIndex(index_statut)
        self.combo_statut.blockSignals(False)

    # ------------------------------------------------------------------ contenu
    def _vider_contenu(self) -> None:
        while self.colonne_contenu.count():
            item = self.colonne_contenu.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _construire_contenu(self) -> None:
        from memora.ui.views import sections_rendu

        self._vider_contenu()
        fiche = self.fiche
        c = fiche.contenu
        p = theme.palette("clair")
        self._affiche_reponses = False

        for cle, titre, emoji in fiche.sections():
            carte = SectionCarte(cle, titre, emoji)
            sections_rendu.rendre_section(carte.corps, cle, c, p)
            self.colonne_contenu.addWidget(carte)

        # pied : provenance
        infos = []
        if fiche.source_nom:
            infos.append(f"Source : {fiche.source_nom}")
        if fiche.mode_generation:
            from memora.config.settings import MODES

            infos.append(f"Mode {MODES.get(fiche.mode_generation, fiche.mode_generation)}")
        if fiche.modele_ia:
            infos.append(f"Modèle {fiche.modele_ia}")
        infos.append(f"Modifiée le {(fiche.date_modification or fiche.date_creation)[:10]}")
        if infos:
            pied = QLabel("  •  ".join(infos))
            pied.setProperty("classe", "tres_muet")
            pied.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.colonne_contenu.addWidget(pied)
        self.colonne_contenu.addStretch(1)

    # ------------------------------------------------------------------ actions
    def _basculer_favori(self) -> None:
        if not self.fiche:
            return
        fiche = self.contexte.base.obtenir_fiche(self.fiche.id)
        if fiche:
            self.contexte.base.maj_champ(fiche.id, "favori", 0 if fiche.favori else 1)
            self.charge(fiche.id)
            self.contexte.bibliotheque_changee.emit()

    def _changer_statut(self) -> None:
        if not self.fiche:
            return
        code = self.combo_statut.currentData()
        self.contexte.base.maj_champ(self.fiche.id, "statut", code)
        self.fiche.statut = code
        self.contexte.bibliotheque_changee.emit()

    def _modifier(self) -> None:
        if self.fiche:
            self.modifier_demande.emit(self.fiche)

    def _regenerer(self) -> None:
        if self.fiche:
            self.regenerer_demande.emit(self.fiche)

    def _nom_fichier_sûr(self, ext: str) -> str:
        titre = "".join(c if c.isalnum() or c in " -_" else "_" for c in self.fiche.titre)
        return f"{titre.strip()[:60]}{ext}"

    def _exporter_pdf(self) -> None:
        from memora.export.pdf_export import exporter_pdf

        if not self.fiche:
            return
        chemin, _ = QFileDialog.getSaveFileName(
            self, "Exporter en PDF", self._nom_fichier_sûr(".pdf"), "PDF (*.pdf)"
        )
        if not chemin:
            return
        try:
            exporter_pdf(self.fiche, chemin)
            from memora.ui.widgets import afficher_toast

            afficher_toast(self.window(), f"PDF exporté : {Path(chemin).name}", "succes")
        except Exception as exc:
            _log.exception("Échec export PDF")
            QMessageBox.warning(self, "Export impossible", f"L'export PDF a échoué : {exc}")

    def _exporter_markdown(self) -> None:
        if not self.fiche:
            return
        chemin, _ = QFileDialog.getSaveFileName(
            self, "Exporter en Markdown", self._nom_fichier_sûr(".md"), "Markdown (*.md)"
        )
        if not chemin:
            return
        try:
            Path(chemin).write_text(fiche_vers_markdown(self.fiche), encoding="utf-8")
            from memora.ui.widgets import afficher_toast

            afficher_toast(self.window(), f"Markdown exporté : {Path(chemin).name}", "succes")
        except Exception as exc:
            QMessageBox.warning(self, "Export impossible", f"L'export a échoué : {exc}")

    def _copier(self) -> None:
        if not self.fiche:
            return
        QApplication.clipboard().setText(fiche_vers_markdown(self.fiche))
        from memora.ui.widgets import afficher_toast

        afficher_toast(self.window(), "Fiche copiée dans le presse-papiers (Markdown).", "info")

    def _supprimer(self) -> None:
        if not self.fiche:
            return
        reponse = QMessageBox.question(
            self, "Supprimer la fiche",
            f"Supprimer définitivement « {self.fiche.titre} » ?\n\n"
            "Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reponse == QMessageBox.StandardButton.Yes:
            self.contexte.base.supprimer_fiche(self.fiche.id)
            self.supprimee.emit()


from pathlib import Path  # noqa: E402  (utilisé par les exports)
