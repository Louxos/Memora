"""Vue Paramètres : IA, fiches, apparence, données."""

from __future__ import annotations

from PySide6.QtCore import QUrl, Qt, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from memora import __version__
from memora.config import paths
from memora.config.settings import MODES, MODELES_CONNUS, NIVEAUX
from memora.ui import icons, theme
from memora.ui.contexte import Contexte
from memora.ui.widgets import Carte, afficher_toast, bouton, etiquette


class SettingsView(QWidget):
    theme_change = Signal(str)
    demo_chargee = Signal()

    def __init__(self, contexte: Contexte, parent=None):
        super().__init__(parent)
        self.contexte = contexte
        colonne = QVBoxLayout(self)
        colonne.setContentsMargins(0, 8, 0, 20)
        colonne.setSpacing(16)

        titre = QLabel("⚙️  Paramètres")
        titre.setProperty("classe", "titre1")
        colonne.addWidget(titre)

        colonne.addWidget(self._carte_ia())
        colonne.addWidget(self._carte_fiches())
        colonne.addWidget(self._carte_apparence())
        colonne.addWidget(self._carte_donnees())
        colonne.addWidget(self._carte_apropos())
        colonne.addStretch(1)

    # ------------------------------------------------------------------ IA
    def _carte_ia(self) -> Carte:
        carte = Carte()
        p = theme.palette("clair")
        entete = QHBoxLayout()
        titre = QLabel("🤖  Intelligence artificielle")
        titre.setStyleSheet("font-size:15px;font-weight:800;")
        entete.addWidget(titre)
        entete.addStretch(1)
        self.resultat_test = etiquette("", "tres_muet")
        entete.addWidget(self.resultat_test)
        carte.layout().addLayout(entete)

        carte.layout().addWidget(etiquette("Fournisseur", "tres_muet"))
        combo_fournisseur = QComboBox()
        combo_fournisseur.addItem("Mistral AI", "mistral")
        combo_fournisseur.setEnabled(False)  # un seul fournisseur en V1
        combo_fournisseur.setToolTip("Mistral AI est le seul fournisseur supporté pour l'instant.")
        carte.layout().addWidget(combo_fournisseur)

        carte.layout().addWidget(etiquette("Clé API Mistral", "tres_muet"))
        self.champ_cle = QLineEdit()
        self.champ_cle.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_cle.setPlaceholderText("32 caractères, commence souvent par…")
        carte.layout().addWidget(self.champ_cle)

        self._etiquette_apercu_cle = etiquette("", "tres_muet")
        carte.layout().addWidget(self._etiquette_apercu_cle)
        self._maj_apercu_cle()

        barre = QHBoxLayout()
        enregistrer = bouton("Enregistrer la clé", "primaire", "cle", 16, "#FFFFFF")
        enregistrer.clicked.connect(self._enregistrer_cle)
        effacer = bouton("Effacer", "", "poubelle", 16, p["texte2"])
        effacer.clicked.connect(self._effacer_cle)
        tester = bouton("Tester la connexion", "", "check", 16, p["succes"])
        tester.clicked.connect(self._tester_connexion)
        barre.addWidget(enregistrer)
        barre.addWidget(effacer)
        barre.addWidget(tester)
        barre.addStretch(1)
        carte.layout().addLayout(barre)

        carte.layout().addWidget(etiquette("Modèle utilisé", "tres_muet"))
        self.combo_modele = QComboBox()
        self.combo_modele.setEditable(True)
        self.combo_modele.addItems(MODELES_CONNUS)
        modele_actuel = self.contexte.reglages.modele
        if modele_actuel not in MODELES_CONNUS:
            self.combo_modele.addItem(modele_actuel)
        self.combo_modele.setCurrentText(modele_actuel)
        self.combo_modele.currentTextChanged.connect(self._changer_modele)
        carte.layout().addWidget(self.combo_modele)
        carte.layout().addWidget(etiquette(
            "La clé est stockée dans le trousseau de ton système (ou chiffrée "
            "localement) et n'apparaît jamais en clair après enregistrement.",
            "tres_muet",
        ))
        return carte

    def _maj_apercu_cle(self) -> None:
        from memora.config import secure_storage
        from memora.utils.logging_setup import masquer

        cle = self.contexte.cle_api()
        if cle:
            source = secure_storage.source_cle()
            self._etiquette_apercu_cle.setText(
                f"Clé enregistrée : {masquer(cle)}  ·  stockage : {source}"
            )
            self.champ_cle.setPlaceholderText("••••••••••••••••  (clé déjà enregistrée)")
        else:
            self._etiquette_apercu_cle.setText(
                "Aucune clé enregistrée — la génération IA et l'OCR en ont besoin."
            )

    def _enregistrer_cle(self) -> None:
        cle = self.champ_cle.text().strip()
        if not cle:
            afficher_toast(self.window(), "Saisis d'abord une clé API.", "info")
            return
        self.contexte.enregistrer_cle(cle)
        self.champ_cle.clear()
        self._maj_apercu_cle()
        afficher_toast(self.window(), "Clé API enregistrée 🔐", "succes")

    def _effacer_cle(self) -> None:
        if not self.contexte.cle_api():
            return
        reponse = QMessageBox.question(
            self, "Effacer la clé",
            "Effacer la clé API enregistrée ? Les analyses IA deviendront impossibles.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reponse == QMessageBox.StandardButton.Yes:
            self.contexte.effacer_cle()
            self._maj_apercu_cle()
            afficher_toast(self.window(), "Clé API effacée.", "info")

    def _tester_connexion(self) -> None:
        client = self.contexte.client_ia()
        if client is None:
            self.resultat_test.setText("⚠️ Aucune clé configurée.")
            self.resultat_test.setStyleSheet("color:#B45309;font-size:12.5px;")
            return
        self.resultat_test.setText("⏳ Test en cours…")
        self.resultat_test.setStyleSheet("color:#5B6274;font-size:12.5px;")
        from PySide6.QtWidgets import QApplication

        QApplication.processEvents()
        try:
            message, modeles = client.tester_connexion()
            self.resultat_test.setText(f"✅ {message}  ({len(modeles)} modèles accessibles)")
            self.resultat_test.setStyleSheet("color:#30A46C;font-size:12.5px;font-weight:700;")
        except Exception as exc:
            texte = getattr(exc, "message", str(exc))
            self.resultat_test.setText(f"❌ {texte}")
            self.resultat_test.setStyleSheet("color:#E5484D;font-size:12.5px;font-weight:700;")

    def _changer_modele(self, texte: str) -> None:
        texte = texte.strip()
        if not texte:
            return
        self.contexte.reglages.modele = texte
        self.contexte.sauver_reglages()

    # ------------------------------------------------------------------ fiches
    def _carte_fiches(self) -> Carte:
        carte = Carte()
        titre = QLabel("📚  Fiches")
        titre.setStyleSheet("font-size:15px;font-weight:800;")
        carte.layout().addWidget(titre)

        barre1 = QHBoxLayout()
        barre1.addWidget(etiquette("Niveau scolaire par défaut", "tres_muet"))
        self.combo_niveau = QComboBox()
        self.combo_niveau.addItems(NIVEAUX)
        self.combo_niveau.setCurrentText(self.contexte.reglages.niveau)
        self.combo_niveau.currentTextChanged.connect(self._changer_niveau)
        barre1.addWidget(self.combo_niveau)
        barre1.addStretch(1)
        carte.layout().addLayout(barre1)

        barre2 = QHBoxLayout()
        barre2.addWidget(etiquette("Mode de génération par défaut", "tres_muet"))
        self.combo_mode = QComboBox()
        for code, libelle in MODES.items():
            self.combo_mode.addItem(libelle, code)
        index = list(MODES.keys()).index(self.contexte.reglages.mode_defaut)
        self.combo_mode.setCurrentIndex(index)
        self.combo_mode.currentIndexChanged.connect(self._changer_mode)
        barre2.addWidget(self.combo_mode)
        barre2.addStretch(1)
        carte.layout().addLayout(barre2)

        barre3 = QHBoxLayout()
        barre3.addWidget(etiquette("Nombre de questions par fiche", "tres_muet"))
        self.spin_questions = QSpinBox()
        self.spin_questions.setRange(3, 15)
        self.spin_questions.setValue(self.contexte.reglages.nb_questions)
        self.spin_questions.valueChanged.connect(self._changer_questions)
        barre3.addWidget(self.spin_questions)
        barre3.addStretch(1)
        carte.layout().addLayout(barre3)
        return carte

    def _changer_niveau(self, texte: str) -> None:
        self.contexte.reglages.niveau = texte
        self.contexte.sauver_reglages()

    def _changer_mode(self, index: int) -> None:
        self.contexte.reglages.mode_defaut = self.combo_mode.currentData()
        self.contexte.sauver_reglages()

    def _changer_questions(self, valeur: int) -> None:
        self.contexte.reglages.nb_questions = valeur
        self.contexte.sauver_reglages()

    # ------------------------------------------------------------------ apparence
    def _carte_apparence(self) -> Carte:
        carte = Carte()
        titre = QLabel("🎨  Apparence")
        titre.setStyleSheet("font-size:15px;font-weight:800;")
        carte.layout().addWidget(titre)
        barre = QHBoxLayout()
        barre.setSpacing(18)
        self._radios_theme: dict[str, QRadioButton] = {}
        for code, libelle in (("systeme", "Suivre le système"), ("clair", "Thème clair"), ("sombre", "Thème sombre")):
            radio = QRadioButton(libelle)
            if self.contexte.reglages.theme == code:
                radio.setChecked(True)
            radio.toggled.connect(lambda cocher, c=code: cocher and self._changer_theme(c))
            self._radios_theme[code] = radio
            barre.addWidget(radio)
        barre.addStretch(1)
        carte.layout().addLayout(barre)
        return carte

    def _changer_theme(self, code: str) -> None:
        self.contexte.reglages.theme = code
        self.contexte.sauver_reglages()
        self.theme_change.emit(code)

    # ------------------------------------------------------------------ données
    def _carte_donnees(self) -> Carte:
        carte = Carte()
        p = theme.palette("clair")
        titre = QLabel("💾  Données")
        titre.setStyleSheet("font-size:15px;font-weight:800;")
        carte.layout().addWidget(titre)

        emplacement = etiquette(str(paths.data_dir()), "tres_muet")
        emplacement.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        carte.layout().addWidget(emplacement)

        barre = QHBoxLayout()
        ouvrir = bouton("Ouvrir le dossier", "", "dossier", 16, p["texte2"])
        ouvrir.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(paths.data_dir()))))
        exporter = bouton("Exporter la bibliothèque…", "", "exporter", 16, p["texte2"])
        exporter.clicked.connect(self._exporter_bibliotheque)
        importer = bouton("Importer une sauvegarde…", "", "importer", 16, p["texte2"])
        importer.clicked.connect(self._importer_bibliotheque)
        demo = bouton("Charger les données de démo", "", "etincelle", 16, p["accent"])
        demo.clicked.connect(self._charger_demo)
        for b in (ouvrir, exporter, importer, demo):
            barre.addWidget(b)
        barre.addStretch(1)
        carte.layout().addLayout(barre)

        self._etiquette_stats_donnees = etiquette("", "tres_muet")
        carte.layout().addWidget(self._etiquette_stats_donnees)
        self._maj_stats_donnees()
        return carte

    def _maj_stats_donnees(self) -> None:
        stats = self.contexte.base.stats()
        taille = self.contexte.base.taille_octets()
        self._etiquette_stats_donnees.setText(
            f"{stats['total']} fiche(s) · base SQLite de {taille / 1024:.0f} Ko · "
            "fichiers joints non dupliqués (référence au document original conservée)"
        )

    def _exporter_bibliotheque(self) -> None:
        chemin, _ = QFileDialog.getSaveFileName(
            self, "Exporter la bibliothèque", "memora-sauvegarde.json", "Sauvegarde Memora (*.json)"
        )
        if not chemin:
            return
        try:
            nb = self.contexte.base.exporter_bibliotheque(chemin)
            afficher_toast(self.window(), f"Sauvegarde créée ({nb} fiches) ✅", "succes")
        except Exception as exc:
            QMessageBox.warning(self, "Export impossible", f"L'export a échoué : {exc}")

    def _importer_bibliotheque(self) -> None:
        chemin, _ = QFileDialog.getOpenFileName(
            self, "Importer une sauvegarde", "", "Sauvegarde Memora (*.json)"
        )
        if not chemin:
            return
        try:
            nb = self.contexte.base.importer_bibliotheque(chemin)
            self.contexte.bibliotheque_changee.emit()
            self._maj_stats_donnees()
            afficher_toast(self.window(), f"{nb} fiche(s) importée(s) ✅", "succes")
        except Exception as exc:
            QMessageBox.warning(self, "Import impossible", f"L'import a échoué : {exc}")

    def _charger_demo(self) -> None:
        fenetre = self.window()
        if hasattr(fenetre, "charger_demo"):
            fenetre.charger_demo()
            self._maj_stats_donnees()

    # ------------------------------------------------------------------ à propos
    def _carte_apropos(self) -> Carte:
        carte = Carte()
        titre = QLabel(f"ℹ️  Memora {__version__}")
        titre.setStyleSheet("font-size:15px;font-weight:800;")
        carte.layout().addWidget(titre)
        carte.layout().addWidget(etiquette(
            "Logiciel personnel de révision : importe un cours, obtiens une fiche "
            "claire et structurée, garde-la dans ta bibliothèque locale.",
            "muet",
        ))
        return carte
