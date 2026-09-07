"""Couche base de données SQLite de Memora.

La base est créée automatiquement au premier lancement, sans aucune
configuration manuelle. Toutes les opérations sont protégées par un verrou
(l'interface et le pipeline de génération peuvent y accéder).
"""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

from memora.core.models import Fiche, maintenant_iso
from memora.utils.logging_setup import logger

_log = logger("database")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS fiches (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    titre              TEXT NOT NULL,
    matiere            TEXT NOT NULL DEFAULT '',
    chapitre           TEXT NOT NULL DEFAULT '',
    theme              TEXT NOT NULL DEFAULT '',
    niveau             TEXT NOT NULL DEFAULT '3e',
    contenu            TEXT NOT NULL DEFAULT '{}',
    statut             TEXT NOT NULL DEFAULT 'a_apprendre',
    favori             INTEGER NOT NULL DEFAULT 0,
    tags               TEXT NOT NULL DEFAULT '',
    source_nom         TEXT NOT NULL DEFAULT '',
    source_chemin      TEXT NOT NULL DEFAULT '',
    source_type        TEXT NOT NULL DEFAULT '',
    taille_octets      INTEGER NOT NULL DEFAULT 0,
    mode_generation    TEXT NOT NULL DEFAULT '',
    modele_ia          TEXT NOT NULL DEFAULT '',
    date_creation      TEXT NOT NULL DEFAULT '',
    date_modification  TEXT NOT NULL DEFAULT '',
    derniere_revision  TEXT NOT NULL DEFAULT '',
    nb_vues            INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_fiches_matiere ON fiches(matiere);
CREATE INDEX IF NOT EXISTS idx_fiches_chapitre ON fiches(chapitre);
CREATE INDEX IF NOT EXISTS idx_fiches_statut ON fiches(statut);
"""

_COLS = (
    "id, titre, matiere, chapitre, theme, niveau, contenu, statut, favori, tags, "
    "source_nom, source_chemin, source_type, taille_octets, mode_generation, modele_ia, "
    "date_creation, date_modification, derniere_revision, nb_vues"
)


class Database:
    """Accès centralisé à la bibliothèque de fiches."""

    def __init__(self, chemin: str | Path):
        self.chemin = Path(chemin)
        self._verrou = threading.Lock()
        self._conn = sqlite3.connect(str(self.chemin), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._verrou:
            self._conn.executescript(_SCHEMA)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.commit()
        _log.info("Base de données prête : %s", self.chemin)

    # ------------------------------------------------------------ utilitaires
    def _rows_vers_fiches(self, rows) -> list[Fiche]:
        return [Fiche.depuis_ligne(dict(r)) for r in rows]

    def fermer(self) -> None:
        with self._verrou:
            self._conn.close()

    # ------------------------------------------------------------ écritures
    def ajouter_fiche(self, fiche: Fiche) -> int:
        ligne = fiche.vers_ligne()
        ligne.pop("id")
        ligne.setdefault("date_creation", maintenant_iso())
        ligne["date_modification"] = ligne["date_creation"]
        colonnes = ", ".join(ligne.keys())
        placeholders = ", ".join("?" for _ in ligne)
        with self._verrou:
            cur = self._conn.execute(
                f"INSERT INTO fiches ({colonnes}) VALUES ({placeholders})",
                list(ligne.values()),
            )
            self._conn.commit()
            fiche.id = cur.lastrowid
            _log.info("Fiche ajoutée #%s : %s", fiche.id, fiche.titre)
            return fiche.id

    def maj_fiche(self, fiche: Fiche) -> None:
        if fiche.id is None:
            self.ajouter_fiche(fiche)
            return
        ligne = fiche.vers_ligne()
        ligne.pop("id")
        ligne["date_modification"] = maintenant_iso()
        assignments = ", ".join(f"{c} = ?" for c in ligne)
        with self._verrou:
            self._conn.execute(
                f"UPDATE fiches SET {assignments} WHERE id = ?",
                [*ligne.values(), fiche.id],
            )
            self._conn.commit()

    def supprimer_fiche(self, id_fiche: int) -> None:
        with self._verrou:
            self._conn.execute("DELETE FROM fiches WHERE id = ?", (id_fiche,))
            self._conn.commit()
        _log.info("Fiche supprimée #%s", id_fiche)

    def maj_champ(self, id_fiche: int, champ: str, valeur) -> None:
        """Met à jour un champ simple (statut, favori…)."""
        if champ not in {"statut", "favori", "tags", "titre", "matiere", "chapitre",
                         "theme", "niveau", "derniere_revision", "nb_vues"}:
            raise ValueError(f"Champ non modifiable : {champ}")
        with self._verrou:
            self._conn.execute(
                f"UPDATE fiches SET {champ} = ?, date_modification = ? WHERE id = ?",
                (valeur, maintenant_iso(), id_fiche),
            )
            self._conn.commit()

    def marquer_revision(self, id_fiche: int) -> None:
        with self._verrou:
            self._conn.execute(
                "UPDATE fiches SET nb_vues = nb_vues + 1, derniere_revision = ? WHERE id = ?",
                (maintenant_iso(), id_fiche),
            )
            self._conn.commit()

    # ------------------------------------------------------------ lectures
    def obtenir_fiche(self, id_fiche: int) -> Fiche | None:
        with self._verrou:
            row = self._conn.execute(
                f"SELECT {_COLS} FROM fiches WHERE id = ?", (id_fiche,)
            ).fetchone()
        return Fiche.depuis_ligne(dict(row)) if row else None

    def lister(
        self,
        matiere: str | None = None,
        chapitre: str | None = None,
        favori: bool | None = None,
        statut: str | None = None,
        recherche: str | None = None,
        tri: str = "recent",
    ) -> list[Fiche]:
        clauses, params = [], []
        if matiere:
            clauses.append("matiere = ?")
            params.append(matiere)
        if chapitre:
            clauses.append("chapitre = ?")
            params.append(chapitre)
        if favori is True:
            clauses.append("favori = 1")
        if statut:
            clauses.append("statut = ?")
            params.append(statut)
        if recherche:
            mot = f"%{recherche.strip()}%"
            clauses.append("(titre LIKE ? OR matiere LIKE ? OR chapitre LIKE ? OR contenu LIKE ? OR tags LIKE ?)")
            params.extend([mot] * 5)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        ordres = {
            "recent": "date_creation DESC",
            "ancien": "date_creation ASC",
            "alpha": "titre COLLATE NOCASE ASC",
        }
        order = ordres.get(tri, ordres["recent"])
        sql = f"SELECT {_COLS} FROM fiches {where} ORDER BY {order}"
        with self._verrou:
            rows = self._conn.execute(sql, params).fetchall()
        return self._rows_vers_fiches(rows)

    def matieres(self) -> list[str]:
        with self._verrou:
            rows = self._conn.execute(
                "SELECT DISTINCT matiere FROM fiches WHERE matiere != '' ORDER BY matiere COLLATE NOCASE"
            ).fetchall()
        return [r["matiere"] for r in rows]

    def chapitres(self, matiere: str | None = None) -> list[str]:
        sql = "SELECT DISTINCT chapitre FROM fiches WHERE chapitre != ''"
        params: list = []
        if matiere:
            sql += " AND matiere = ?"
            params.append(matiere)
        sql += " ORDER BY chapitre COLLATE NOCASE"
        with self._verrou:
            rows = self._conn.execute(sql, params).fetchall()
        return [r["chapitre"] for r in rows]

    def stats(self) -> dict:
        with self._verrou:
            total = self._conn.execute("SELECT COUNT(*) c FROM fiches").fetchone()["c"]
            favoris = self._conn.execute("SELECT COUNT(*) c FROM fiches WHERE favori = 1").fetchone()["c"]
            par_statut = {
                r["statut"]: r["c"]
                for r in self._conn.execute("SELECT statut, COUNT(*) c FROM fiches GROUP BY statut")
            }
        return {
            "total": total,
            "matieres": len(self.matieres()),
            "favoris": favoris,
            "a_apprendre": par_statut.get("a_apprendre", 0),
            "a_revoir": par_statut.get("a_revoir", 0),
            "maitrisees": par_statut.get("maitrisee", 0),
        }

    def taille_octets(self) -> int:
        try:
            return self.chemin.stat().st_size
        except OSError:
            return 0

    # ------------------------------------------------------------ sauvegarde
    def exporter_bibliotheque(self, chemin: str | Path) -> int:
        """Exporte toutes les fiches en JSON (sauvegarde / transfert)."""
        fiches = self.lister(tri="ancien")
        donnees = {
            "format": "memora-bibliotheque",
            "version": 1,
            "nb": len(fiches),
            "fiches": [f.vers_ligne() for f in fiches],
        }
        Path(chemin).write_text(
            json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return len(fiches)

    def importer_bibliotheque(self, chemin: str | Path) -> int:
        """Importe des fiches depuis un export JSON Memora."""
        donnees = json.loads(Path(chemin).read_text(encoding="utf-8"))
        if donnees.get("format") != "memora-bibliotheque":
            raise ValueError("Ce fichier n'est pas une sauvegarde Memora.")
        nb = 0
        for ligne in donnees.get("fiches", []):
            fiche = Fiche.depuis_ligne(ligne)
            fiche.id = None  # nouvelle entrée, pas de collision d'identifiants
            self.ajouter_fiche(fiche)
            nb += 1
        return nb
