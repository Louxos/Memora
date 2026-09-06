"""Point d'entrée de l'application Memora.

Utilisation :
    python main.py               → lance l'application
    python main.py --demo        → lance en ajoutant les fiches de démonstration
    python main.py --check-api   → teste la clé API configurée (ligne de commande)
"""

from __future__ import annotations

import sys

from memora import __version__
from memora.utils.logging_setup import configurer_logger, logger


def _ligne_commande() -> None:
    """Traite les options --check-api / --version sans interface graphique."""
    if "--version" in sys.argv:
        print(f"Memora {__version__}")
        raise SystemExit(0)

    if "--check-api" in sys.argv:
        from memora.config.settings import charger_env, charger_reglages
        from memora.config import secure_storage

        charger_env()
        reglages = charger_reglages()
        cle = secure_storage.lire_cle()
        if not cle:
            print("❌ Aucune clé API trouvée (paramètres, fichier .env ou MISTRAL_API_KEY).")
            raise SystemExit(1)
        from memora.ia.client import MistralClient

        client = MistralClient(cle, modele=reglages.modele)
        try:
            message, modeles = client.tester_connexion()
            print(f"✅ {message}")
            print("Modèles disponibles :", ", ".join(modeles[:12]) + ("…" if len(modeles) > 12 else ""))
            raise SystemExit(0)
        except Exception as exc:
            print(f"❌ {getattr(exc, 'message', exc)}")
            raise SystemExit(1)


def main() -> int:
    _log = configurer_logger()

    if len(sys.argv) > 1 and "--check-api" in sys.argv or "--version" in sys.argv:
        _ligne_commande()

    from memora.config.settings import charger_env, charger_reglages

    charger_env()  # charge un éventuel .env avant tout accès aux secrets
    reglages = charger_reglages()

    # option --demo : ajoute les fiches de démonstration au premier lancement
    if "--demo" in sys.argv and not reglages.demo_charge:
        from memora.core.database import Database
        from memora.core.demo import fiches_demo
        from memora.config import paths

        base = Database(paths.database_path())
        for fiche in fiches_demo():
            base.ajouter_fiche(fiche)
        base.fermer()
        reglages.demo_charge = True
        from memora.config.settings import enregistrer_reglages

        enregistrer_reglages(reglages)
        print("Fiches de démonstration ajoutées.")

    from PySide6.QtWidgets import QApplication

    from memora.core.database import Database
    from memora.config import paths
    from memora.ui.contexte import Contexte
    from memora.ui.main_window import FenetrePrincipale
    from memora.ui.theme import police_app

    app = QApplication(sys.argv)
    app.setApplicationName("Memora")
    app.setOrganizationName("Memora")
    app.setFont(police_app())

    base = Database(paths.database_path())
    contexte = Contexte(base, reglages)
    fenetre = FenetrePrincipale(contexte)
    fenetre.show()

    if reglages.premiere_lancement:
        reglages.premiere_lancement = False
        from memora.config.settings import enregistrer_reglages

        enregistrer_reglages(reglages)
        _log.info("Premier lancement de Memora")

    code = app.exec()
    base.fermer()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
