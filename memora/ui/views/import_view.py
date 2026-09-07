"""Vue « Nouvelle fiche » : import, glisser-déposer, options et progression."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from memora.config.settings import MODES, NIVEAUX
from memora.core.pipeline import ETAPES, GenerationWorker
from memora.extraction.extractor import apercu_png
from memora.ui import icons, theme
from memora.ui.contexte import Contexte
from memora.ui.widgets import Carte, bouton, etiquette

MATIERES_USUELLES = [
    "Détection automatique", "Mathématiques", "Français", "Histoire",
    "Géographie", "SVT", "Physique-Chimie", "Anglais", "Espagnol",
    "Technologie", "EMC", "Arts plastiques", "Musique", "Autre",
]


class ZoneDepot(QFrame):
    """Zone de glisser-déposer + bouton parcourir."""

    fichier_choisi = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setProperty("classe", "carte")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(190)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p = theme.palette("clair")
        icone = QLabel()
        icone.setPixmap(icons.icone("importer", p["accent"], 42).pixmap(42, 42))
        icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titre = QLabel("Dépose ton document ici")
        titre.setProperty("classe", "titre2")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sous = etiquette("ou clique pour parcourir — PDF, DOCX, TXT, JPG, PNG, WEBP", "muet")
        sous.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icone)
        lay.addWidget(titre)
        lay.addWidget(sous)
        self._style_normal()

    def _style_normal(self) -> None:
        p = theme.palette("clair")
        self.setStyleSheet(
            f"QFrame{{border:2px dashed {p['bord']};border-radius:14px;background:{p['surface2']};}}"
        )

    def _style_survol(self) -> None:
        p = theme.palette("clair")
        self.setStyleSheet(
            f"QFrame{{border:2px dashed {p['accent']};border-radius:14px;"
            f"background:{p['accent_doux']};}}"
        )

    def mousePressEvent(self, event) -> None:
        self._parcourir()

    def _parcourir(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        from memora.utils.files import EXTENSIONS

        filtres = "Documents (*.pdf *.docx *.txt *.md *.jpg *.jpeg *.png *.webp);;Tous les fichiers (*.*)"
        chemin, _ = QFileDialog.getOpenFileName(self, "Choisir un document", "", filtres)
        _ = EXTENSIONS
        if chemin:
            self.fichier_choisi.emit(chemin)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._style_survol()

    def dragLeaveEvent(self, event) -> None:
        self._style_normal()

    def dropEvent(self, event) -> None:
        self._style_normal()
        for url in event.mimeData().urls():
            chemin = url.toLocalFile()
            if chemin:
                self.fichier_choisi.emit(chemin)
                return


class ImportView(QWidget):
    fiche_creee = Signal(object)

    def __init__(self, contexte: Contexte, parent=None):
        super().__init__(parent)
        self.contexte = contexte
        self.chemin: str = ""
        self.worker: GenerationWorker | None = None

        colonne = QVBoxLayout(self)
        colonne.setContentsMargins(0, 8, 0, 20)
        colonne.setSpacing(16)

        titre = QLabel("➕ Nouvelle fiche")
        titre.setProperty("classe", "titre1")
        colonne.addWidget(titre)
        colonne.addWidget(etiquette(
            "Importe un cours : Memora l'analyse et génère une fiche de révision.", "muet"
        ))

        # --- 1) document
        carte_doc = Carte()
        carte_doc.layout().addWidget(etiquette("1 · Choisis ton document", "titre3"))
        self.zone_depot = ZoneDepot()
        self.zone_depot.fichier_choisi.connect(self.charger_fichier)
        carte_doc.layout().addWidget(self.zone_depot)

        self.carte_infos = Carte()
        self.carte_infos.hide()
        carte_doc.layout().addWidget(self.carte_infos)
        colonne.addWidget(carte_doc)

        # --- 2) options
        carte_options = Carte()
        carte_options.layout().addWidget(etiquette("2 · Options de génération", "titre3"))

        grille = QGridLayout()
        grille.setHorizontalSpacing(18)
        grille.setVerticalSpacing(12)

        etiquette_mode = etiquette("Mode de génération", "tres_muet")
        grille.addWidget(etiquette_mode, 0, 0)
        zone_modes = QHBoxLayout()
        zone_modes.setSpacing(8)
        self._groupe_modes = QButtonGroup(self)
        self._groupe_modes.setExclusive(True)
        self.boutons_modes: dict[str, QPushButton] = {}
        descriptions = {
            "rapide": "L'essentiel seulement",
            "complete": "Fiche détaillée",
            "brevet": "Priorité au brevet",
            "active": "Beaucoup de questions",
        }
        for code, libelle in MODES.items():
            b = QPushButton(f"{libelle}")
            b.setCheckable(True)
            b.setToolTip(descriptions.get(code, ""))
            b.clicked.connect(lambda _=False, c=code: self._selectionner_mode(c))
            self._groupe_modes.addButton(b)
            zone_modes.addWidget(b)
            self.boutons_modes[code] = b
        self.mode_choisi = self.contexte.reglages.mode_defaut
        colonne_modes = QVBoxLayout()
        colonne_modes.addLayout(zone_modes)
        self.aide_mode = etiquette("", "tres_muet")
        colonne_modes.addWidget(self.aide_mode)
        grille.addLayout(colonne_modes, 1, 0, 1, 2)
        self._selectionner_mode(self.mode_choisi)

        grille.addWidget(etiquette("Niveau", "tres_muet"), 2, 0)
        self.combo_niveau = QComboBox()
        self.combo_niveau.addItems(NIVEAUX)
        self.combo_niveau.setCurrentText(self.contexte.reglages.niveau)
        grille.addWidget(self.combo_niveau, 2, 1)

        grille.addWidget(etiquette("Matière", "tres_muet"), 3, 0)
        self.combo_matiere = QComboBox()
        self.combo_matiere.setEditable(True)
        self.combo_matiere.addItems(MATIERES_USUELLES)
        grille.addWidget(self.combo_matiere, 3, 1)

        grille.addWidget(etiquette("Chapitre (optionnel)", "tres_muet"), 4, 0)
        self.champ_chapitre = QLineEdit()
        self.champ_chapitre.setPlaceholderText("Laisser l'IA le détecter automatiquement")
        grille.addWidget(self.champ_chapitre, 4, 1)

        grille.addWidget(etiquette("Titre (optionnel)", "tres_muet"), 5, 0)
        self.champ_titre = QLineEdit()
        self.champ_titre.setPlaceholderText("Laisser l'IA le détecter automatiquement")
        grille.addWidget(self.champ_titre, 5, 1)

        grille.setColumnStretch(1, 1)
        carte_options.layout().addLayout(grille)

        self.bouton_generer = bouton("✨  Analyser et créer la fiche", "primaire", "etincelle", 20, "#FFFFFF")
        self.bouton_generer.setMinimumHeight(48)
        self.bouton_generer.setEnabled(False)
        self.bouton_generer.clicked.connect(self.demarrer)
        carte_options.layout().addWidget(self.bouton_generer)
        colonne.addWidget(carte_options)

        # --- 3) progression
        self.carte_progression = Carte()
        self.carte_progression.layout().addWidget(etiquette("3 · Progression", "titre3"))
        self.barre = QProgressBar()
        self.barre.setRange(0, len(ETAPES))
        self.barre.setTextVisible(False)
        self.barre.setFixedHeight(8)
        self.carte_progression.layout().addWidget(self.barre)
        self.etiquettes_etapes: list[QLabel] = []
        for _, libelle in ETAPES:
            lab = etiquette("○  " + libelle, "muet")
            lab.setProperty("etat", "attente")
            self.carte_progression.layout().addWidget(lab)
            self.etiquettes_etapes.append(lab)
        self.message_etat = etiquette("", "muet")
        self.carte_progression.layout().addWidget(self.message_etat)
        bouton_annuler = bouton("Annuler", "", "croix")
        bouton_annuler.clicked.connect(self.annuler)
        self.carte_progression.layout().addWidget(bouton_annuler)
        self.carte_progression.hide()
        colonne.addWidget(self.carte_progression)

        colonne.addStretch(1)

    # ------------------------------------------------------------------ modes
    DESCRIPTIONS_MODES = {
        "rapide": "⚡ Rapide — une fiche courte avec uniquement l'essentiel.",
        "complete": "📚 Complète — fiche détaillée couvrant tout le document.",
        "brevet": "🎯 Brevet — priorité aux notions importantes pour le brevet.",
        "active": "🧠 Active — fiche complète + beaucoup de questions pour se tester.",
    }

    def _selectionner_mode(self, code: str) -> None:
        self.mode_choisi = code
        self.aide_mode.setText(self.DESCRIPTIONS_MODES.get(code, ""))
        for c, bouton_mode in self.boutons_modes.items():
            bouton_mode.setChecked(c == code)

    # ------------------------------------------------------------------ fichier
    def charger_fichier(self, chemin: str) -> None:
        from memora.utils import files
        from memora.utils.errors import MemoraError

        try:
            if not files.extension_supportee(chemin):
                raise MemoraError(
                    "Format non pris en charge. Choisis un PDF, un DOCX, un TXT "
                    "ou une image (JPG, PNG, WEBP)."
                )
            if not files.fichier_existe(chemin):
                raise MemoraError("Impossible de lire ce fichier.")
            if Path(chemin).stat().st_size > files.TAILLE_MAX_OCTETS:
                raise MemoraError("Ce document est trop volumineux (maximum 25 Mo).")
        except MemoraError as exc:
            QMessageBox.warning(self, "Import impossible", exc.message)
            return

        self.chemin = chemin
        self.zone_depot.hide()
        self._afficher_infos_fichier()
        self.bouton_generer.setEnabled(True)

    def _afficher_infos_fichier(self) -> None:
        from memora.utils import files

        # nettoie
        while self.carte_infos.layout().count():
            item = self.carte_infos.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        nom, type_lisible, categorie, taille = files.infos_fichier(self.chemin)
        p = theme.palette("clair")
        disposition = QHBoxLayout()
        disposition.setSpacing(14)
        self.carte_infos.layout().addLayout(disposition)
        icone_nom = {"pdf": "fichier", "docx": "fichier", "texte": "liste", "image": "image"}.get(categorie, "fichier")
        icone_lab = QLabel()
        icone_lab.setPixmap(icons.icone(icone_nom, p["accent"], 34).pixmap(34, 34))
        disposition.addWidget(icone_lab)

        colonne_texte = QVBoxLayout()
        colonne_texte.setSpacing(2)
        colonne_texte.addWidget(etiquette(nom, "titre3"))
        details = f"{type_lisible}  •  {files.taille_lisible(taille)}"
        if categorie == "pdf":
            try:
                from memora.extraction import pdf_extractor

                details += f"  •  {pdf_extractor.nb_pages(self.chemin)} page(s)"
            except Exception:
                pass
        colonne_texte.addWidget(etiquette(details, "tres_muet"))
        disposition.addLayout(colonne_texte, 1)

        bouton_changer = bouton("Changer de fichier", "", "retour")
        bouton_changer.clicked.connect(self.reinitialiser)
        disposition.addWidget(bouton_changer)

        # aperçu (PDF / image) ou extrait texte
        apercu = apercu_png(self.chemin, largeur=560)
        if apercu:
            vignette = QLabel()
            pix = QPixmap()
            pix.loadFromData(apercu)
            vignette.setPixmap(
                pix.scaledToWidth(min(520, pix.width()), Qt.TransformationMode.SmoothTransformation)
            )
            vignette.setMaximumHeight(300)
            vignette.setScaledContents(False)
            vignette.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.carte_infos.layout().addWidget(vignette)
        elif Path(self.chemin).suffix.lower() in (".txt", ".md"):
            try:
                from memora.utils.files import lire_texte_souple

                extrait = lire_texte_souple(self.chemin)[:900]
                apercu_texte = etiquette(extrait + ("…" if len(extrait) == 900 else ""), "muet")
                apercu_texte.setStyleSheet(
                    "font-family:Consolas,monospace;font-size:12px;background:"
                    f"{p['surface2']};border-radius:8px;padding:12px;"
                )
                self.carte_infos.layout().addWidget(apercu_texte)
            except Exception:
                pass

        self.carte_infos.show()

    def reinitialiser(self) -> None:
        self.chemin = ""
        self.carte_infos.hide()
        self.zone_depot.show()
        self.bouton_generer.setEnabled(False)

    def rafraichir(self) -> None:
        self.combo_niveau.setCurrentText(self.contexte.reglages.niveau)
        self._selectionner_mode(self.contexte.reglages.mode_defaut)

    def pre_remplir(self, chemin: str, mode: str = "") -> None:
        self.reinitialiser()
        self.charger_fichier(chemin)
        if mode in self.boutons_modes:
            self._selectionner_mode(mode)

    # ------------------------------------------------------------------ génération
    def demarrer(self) -> None:
        if not self.chemin:
            return
        if not self.contexte.cle_configures():
            reponse = QMessageBox.question(
                self, "Clé API requise",
                "Analyser un cours nécessite l'IA Mistral, donc une clé API.\n\n"
                "Veux-tu ouvrir les paramètres pour la renseigner maintenant ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reponse == QMessageBox.StandardButton.Yes:
                from memora.ui.main_window import PAGE_PARAMETRES

                fenetre = self.window()
                if hasattr(fenetre, "aller_a"):
                    fenetre.aller_a(PAGE_PARAMETRES)
            return

        matiere = self.combo_matiere.currentText().strip()
        if matiere == "Détection automatique":
            matiere = ""
        self.worker = GenerationWorker(
            chemin=self.chemin,
            base=self.contexte.base,
            reglages=self.contexte.reglages,
            mode=self.mode_choisi,
            niveau=self.combo_niveau.currentText(),
            matiere=matiere,
            chapitre=self.champ_chapitre.text().strip(),
            titre=self.champ_titre.text().strip(),
            cle_api=self.contexte.cle_api(),
        )
        self.worker.etape_changee.connect(self._sur_etape_changee)
        self.worker.etape_terminee.connect(self._sur_etape_terminee)
        self.worker.terminee.connect(self._sur_terminee)
        self.worker.echouee.connect(self._sur_echec)

        self._reinitialiser_etapes()
        self.carte_progression.show()
        self.bouton_generer.setEnabled(False)
        self.message_etat.setText("Analyse en cours…")
        self.worker.start()

    def _reinitialiser_etapes(self) -> None:
        self.barre.setValue(0)
        for lab in self.etiquettes_etapes:
            lab.setText("○  " + lab.text().split("  ", 1)[-1])
            lab.setProperty("etat", "attente")
            lab.style().unpolish(lab)
            lab.style().polish(lab)

    def _sur_etape_changee(self, index: int, libelle: str) -> None:
        for i, lab in enumerate(self.etiquettes_etapes):
            if i == index:
                lab.setText("⟳  " + libelle)
                lab.setProperty("etat", "encours")
            elif i > index:
                pass
            lab.style().unpolish(lab)
            lab.style().polish(lab)
        self.message_etat.setText(libelle if index >= 2 else "")

    def _sur_etape_terminee(self, index: int) -> None:
        lab = self.etiquettes_etapes[index]
        lab.setText("✓  " + lab.text().split("  ", 1)[-1])
        lab.setProperty("etat", "fait")
        lab.style().unpolish(lab)
        lab.style().polish(lab)
        self.barre.setValue(index + 1)

    def _sur_terminee(self, fiche) -> None:
        self.barre.setValue(len(ETAPES))
        self.message_etat.setText("✅ Fiche terminée !")
        self.worker = None
        self.carte_progression.hide()
        self.reinitialiser()
        self.fiche_creee.emit(fiche)

    def _sur_echec(self, message: str) -> None:
        self.carte_progression.hide()
        self.bouton_generer.setEnabled(True)
        self.worker = None
        from memora.ui.widgets import afficher_toast

        afficher_toast(self.window(), f"❌ {message}", "erreur", duree_ms=6000)
        QMessageBox.warning(self, "Analyse interrompue", message)

    def annuler(self) -> None:
        if self.worker:
            self.worker.annuler()
            self.message_etat.setText("Annulation…")

    def arreter_worker(self) -> None:
        if self.worker:
            self.worker.annuler()
            self.worker.wait(3000)
