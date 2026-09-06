"""Génère des captures d'écran de Memora (utile pour la documentation).

Usage :  python scripts/captures.py [dossier_sortie]
Fonctionne sans écran (plateforme Qt « minimal »).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("QT_QPA_PLATFORM", "minimal")


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from memora.config.settings import Reglages
    from memora.core.database import Database
    from memora.core.demo import fiches_demo
    from memora.ui.contexte import Contexte
    from memora.ui.main_window import (
        PAGE_BIBLIOTHEQUE,
        PAGE_FICHE,
        PAGE_NOUVELLE,
        PAGE_PARAMETRES,
        FenetrePrincipale,
    )
    from memora.ui.theme import police_app

    dossier = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/captures")
    dossier.mkdir(parents=True, exist_ok=True)
    bac = dossier / "_bac"
    bac.mkdir(exist_ok=True)
    os.environ["MEMORA_HOME"] = str(bac)

    app = QApplication.instance() or QApplication([])
    app.setFont(police_app())

    base = Database(bac / "captures.db")
    if not base.lister():
        for fiche in fiches_demo():
            base.ajouter_fiche(fiche)

    contexte = Contexte(base, Reglages())
    fenetre = FenetrePrincipale(contexte)
    fenetre.resize(1280, 820)
    fenetre.show()
    app.processEvents()

    def capture(nom: str) -> None:
        import time

        # laisse les animations d'apparition se terminer (180 ms)
        for _ in range(15):
            app.processEvents()
            time.sleep(0.02)
        ok = fenetre.grab().save(str(dossier / f"{nom}.png"))
        print(("✓" if ok else "✗"), nom)

    capture("01-accueil")
    fenetre.aller_a(PAGE_BIBLIOTHEQUE)
    capture("02-bibliotheque")
    fiche = base.lister()[0]
    fenetre.ouvrir_fiche(fiche.id)
    capture("03-fiche")
    fenetre.aller_a(PAGE_NOUVELLE)
    capture("04-import")
    fenetre.aller_a(PAGE_PARAMETRES)
    capture("05-parametres")
    fenetre.appliquer_theme_par_nom("sombre")
    fenetre.aller_a(PAGE_BIBLIOTHEQUE)
    fenetre.ouvrir_fiche(base.lister()[1].id)
    capture("06-fiche-sombre")

    base.fermer()
    print(f"Captures enregistrées dans {dossier}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
