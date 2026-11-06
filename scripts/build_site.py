#!/usr/bin/env python3
"""Construit la GitHub Page d'archive de Memora.

Les trois fichiers fournis (``site/index.html``, ``site/404.html`` et
``site/site.css``) sont conservés tels quels, avec leurs marqueurs
``{{NOM}}``. Ce script les résout et produit un site **entièrement statique**
dans ``docs/`` : la feuille de styles est injectée dans chaque page (aucune
ressource distante), le logo est inline, et les liens pointent vers le dépôt,
la page du projet et la dernière version publiée.

Aucune dépendance externe : Python standard uniquement.

    python3 scripts/build_site.py                # écrit dans docs/
    python3 scripts/build_site.py --sortie _site # autre dossier de sortie
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SORTIE_PAR_DEFAUT = ROOT / "docs"

# ------------------------------------------------------------------ constantes
# Toutes les valeurs éditoriales de l'archive sont ici : pour changer la date,
# la version ou l'adresse du dépôt, on ne touche pas aux fichiers fournis.
ARCHIVED_ON = "6 novembre 2026"
LAST_VERSION = "1.0.0"
LAST_VERSION_ON = "6 novembre 2026"
REPO_URL = "https://github.com/Louxos/Memora"
SITE_URL = "https://louxos.github.io/Memora/"
BASE_URL = "/Memora/"
RELEASE_URL = f"{REPO_URL}/releases/tag/v{LAST_VERSION}"

MOTIF = re.compile(r"\{\{([A-Z_]+)\}\}")


def valeurs() -> dict[str, str]:
    """Les valeurs de substitution, dont le CSS et le logo inline."""
    css = (SITE / "site.css").read_text(encoding="utf-8").rstrip()
    mark = (SITE / "favicon.svg").read_text(encoding="utf-8").strip()
    return {
        "ARCHIVED_ON": ARCHIVED_ON,
        "LAST_VERSION": LAST_VERSION,
        "LAST_VERSION_ON": LAST_VERSION_ON,
        "REPO_URL": REPO_URL,
        "SITE_URL": SITE_URL,
        "BASE_URL": BASE_URL,
        "RELEASE_URL": RELEASE_URL,
        "INLINE_CSS": css,
        "MARK_SVG": mark,
    }


def rendre(nom: str, table: dict[str, str]) -> str:
    """Résout tous les marqueurs d'une page et refuse tout résidu."""
    source = (SITE / nom).read_text(encoding="utf-8")

    def substituer(match: re.Match[str]) -> str:
        cle = match.group(1)
        if cle not in table:
            raise SystemExit(f"Marqueur inconnu {{{{{cle}}}}} dans {nom}")
        return table[cle]

    rendu = MOTIF.sub(substituer, source)
    if MOTIF.search(rendu) or "{{" in rendu:
        raise SystemExit(f"Des marqueurs n'ont pas été résolus dans {nom}")
    return rendu


def construire(sortie: Path) -> None:
    table = valeurs()
    sortie.mkdir(parents=True, exist_ok=True)

    for nom in ("index.html", "404.html"):
        (sortie / nom).write_text(rendre(nom, table), encoding="utf-8")

    # La feuille et le logo restent publiés tels quels, en plus du CSS inline :
    # ce sont exactement les fichiers fournis, disponibles à l'adresse du site.
    shutil.copyfile(SITE / "site.css", sortie / "site.css")
    shutil.copyfile(SITE / "favicon.svg", sortie / "favicon.svg")
    # Empêche Jekyll de toucher au site (notamment aux fichiers .md du dossier).
    (sortie / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Page d'archive Memora générée dans {sortie.relative_to(ROOT)} :")
    for fichier in ("index.html", "404.html", "site.css", "favicon.svg", ".nojekyll"):
        cible = sortie / fichier
        print(f"  · {fichier:12} {cible.stat().st_size:>7} octets")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sortie",
        type=Path,
        default=SORTIE_PAR_DEFAUT,
        help="dossier de publication (par défaut : docs/)",
    )
    args = parser.parse_args()
    construire(args.sortie.resolve())


if __name__ == "__main__":
    main()
