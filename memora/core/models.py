"""Modèle de données : la fiche de révision.

Le contenu d'une fiche est un dictionnaire JSON structuré par sections.
Les sections sont **adaptatives** : seules celles qui ont du contenu sont
affichées / exportées.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime

# ------------------------------------------------------------------ statuts

STATUT_A_APPRENDRE = "a_apprendre"
STATUT_A_REVOIR = "a_revoir"
STATUT_MAITRISEE = "maitrisee"

STATUTS = [
    (STATUT_A_APPRENDRE, "À apprendre", "#E5484D"),
    (STATUT_A_REVOIR, "À revoir", "#F5A524"),
    (STATUT_MAITRISEE, "Maîtrisée", "#30A46C"),
]

STATUT_LABELS = {code: label for code, label, _ in STATUTS}
STATUT_COULEURS = {code: couleur for code, _, couleur in STATUTS}

# ------------------------------------------------------------------ sections

# (clé JSON, titre affiché, emoji)
SECTIONS: list[tuple[str, str, str]] = [
    ("objectif", "Objectif", "🎯"),
    ("essentiel", "L'essentiel", "🧠"),
    ("notions", "Notions importantes", "📚"),
    ("definitions", "Définitions", "📌"),
    ("formules", "Formules & règles", "🧮"),
    ("methodes", "Méthodes", "📝"),
    ("dates_personnages", "Dates, personnes & événements", "📅"),
    ("exemples", "Exemples", "💡"),
    ("pieges", "Pièges à éviter", "⚠️"),
    ("retenir", "Si tu ne dois retenir que ça", "🔥"),
    ("questions", "Teste-toi", "❓"),
    ("avertissements", "Points d'attention du document", "🔎"),
]

SECTION_TITRES = {cle: titre for cle, titre, _ in SECTIONS}
SECTION_EMOJIS = {cle: emo for cle, _, emo in SECTIONS}

# Sections qui sont de simples listes de texte
SECTIONS_LISTES = {"essentiel", "exemples", "pieges", "retenir", "avertissements"}

MATIERES_COULEURS = {
    "mathématiques": "#5B5FE9",
    "français": "#D6409F",
    "histoire": "#D9730D",
    "géographie": "#30A46C",
    "svt": "#12A594",
    "sciences physiques": "#E5484D",
    "physique-chimie": "#E5484D",
    "anglais": "#8E4EC6",
    "espagnol": "#F5A524",
    "emc": "#6172F3",
    "technologie": "#76808F",
}


def couleur_matiere(matiere: str) -> str:
    return MATIERES_COULEURS.get((matiere or "").strip().lower(), "#6172F3")


def sections_remplies(contenu: dict) -> list[tuple[str, str, str]]:
    """Sections non vides, dans l'ordre standard : [(clé, titre, emoji)]."""
    resultat = []
    for cle, titre, emoji in SECTIONS:
        valeur = contenu.get(cle)
        if cle == "objectif":
            if isinstance(valeur, str) and valeur.strip():
                resultat.append((cle, titre, emoji))
        elif isinstance(valeur, list) and valeur:
            resultat.append((cle, titre, emoji))
    return resultat


# ------------------------------------------------------------------ coercition

def _texte(v, defaut="") -> str:
    return v.strip() if isinstance(v, str) and v.strip() else defaut


def _liste_texte(v) -> list[str]:
    if not isinstance(v, list):
        return []
    return [str(item).strip() for item in v if item is not None and str(item).strip()]


def _liste_dicts(v, champs: list[str]) -> list[dict]:
    """Normalise une liste d'objets en gardant les champs attendus."""
    if not isinstance(v, list):
        return []
    resultat = []
    for item in v:
        if not isinstance(item, dict):
            continue
        nettoyé = {champ: _texte(item.get(champ)) for champ in champs}
        if any(nettoyé.values()):
            resultat.append(nettoyé)
    return resultat


def _coercer_methodes(brut) -> list[dict]:
    """Les méthodes acceptent les étapes en liste OU en texte multi-lignes."""
    if not isinstance(brut, list):
        return []
    methodes = []
    for methode in brut:
        if not isinstance(methode, dict):
            continue
        titre = _texte(methode.get("titre"))
        etapes = methode.get("etapes")
        if isinstance(etapes, list):
            etapes = _liste_texte(etapes)
        elif isinstance(etapes, str):
            etapes = [ligne.strip() for ligne in etapes.splitlines() if ligne.strip()]
        else:
            etapes = []
        if titre or etapes:
            methodes.append({"titre": titre, "etapes": etapes})
    return methodes


def coercer_contenu(brut: dict) -> dict:
    """Valide et normalise le JSON produit par l'IA (tolérant aux oublis)."""
    if not isinstance(brut, dict):
        brut = {}
    contenu = {
        "objectif": _texte(brut.get("objectif")),
        "essentiel": _liste_texte(brut.get("essentiel")),
        "notions": _liste_dicts(brut.get("notions"), ["nom", "explication", "exemple"]),
        "definitions": _liste_dicts(brut.get("definitions"), ["terme", "definition"]),
        "formules": _liste_dicts(
            brut.get("formules"),
            ["formule", "signification", "unite", "conditions", "exemple"],
        ),
        "methodes": _coercer_methodes(brut.get("methodes")),
        "dates_personnages": _liste_dicts(brut.get("dates_personnages"), ["type", "nom", "info"]),
        "exemples": _liste_texte(brut.get("exemples")),
        "pieges": _liste_texte(brut.get("pieges")),
        "retenir": _liste_texte(brut.get("retenir")),
        "questions": _liste_dicts(brut.get("questions"), ["question", "reponse", "type"]),
        "avertissements": _liste_texte(brut.get("avertissements")),
    }
    # type de question normalisé
    for q in contenu["questions"]:
        if not q["type"]:
            q["type"] = "mémorisation"
    # type date/personne/événement normalisé
    for d in contenu["dates_personnages"]:
        t = d["type"].lower()
        d["type"] = "date" if "date" in t else ("personne" if "personne" in t or "personnage" in t else "événement")
    return contenu


def contenu_est_vide(contenu: dict) -> bool:
    return not sections_remplies(contenu)


# ------------------------------------------------------------------ fiche

def maintenant_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Fiche:
    """Une fiche de révision complète."""

    titre: str = "Sans titre"
    matiere: str = ""
    chapitre: str = ""
    theme: str = ""
    niveau: str = "3e"
    contenu: dict = field(default_factory=dict)
    statut: str = STATUT_A_APPRENDRE
    favori: bool = False
    tags: str = ""
    # --- provenance
    source_nom: str = ""
    source_chemin: str = ""
    source_type: str = ""
    taille_octets: int = 0
    mode_generation: str = ""
    modele_ia: str = ""
    # --- horodatage
    date_creation: str = ""
    date_modification: str = ""
    derniere_revision: str = ""
    nb_vues: int = 0
    # identifiant base de données
    id: int | None = None

    # ------------------------------------------------------------------ helpers
    def statut_label(self) -> str:
        return STATUT_LABELS.get(self.statut, STATUT_A_APPRENDRE)

    def sections(self) -> list[tuple[str, str, str]]:
        return sections_remplies(self.contenu)

    @property
    def demo(self) -> bool:
        return "démo" in (self.tags or "").lower() or "demo" in (self.tags or "").lower()

    # ------------------------------------------------------------------ sérialisation
    def vers_ligne(self) -> dict:
        return {
            "id": self.id,
            "titre": self.titre,
            "matiere": self.matiere,
            "chapitre": self.chapitre,
            "theme": self.theme,
            "niveau": self.niveau,
            "contenu": json.dumps(self.contenu, ensure_ascii=False),
            "statut": self.statut,
            "favori": int(self.favori),
            "tags": self.tags,
            "source_nom": self.source_nom,
            "source_chemin": self.source_chemin,
            "source_type": self.source_type,
            "taille_octets": self.taille_octets,
            "mode_generation": self.mode_generation,
            "modele_ia": self.modele_ia,
            "date_creation": self.date_creation or maintenant_iso(),
            "date_modification": self.date_modification or maintenant_iso(),
            "derniere_revision": self.derniere_revision,
            "nb_vues": self.nb_vues,
        }

    @classmethod
    def depuis_ligne(cls, ligne: dict) -> "Fiche":
        try:
            contenu = json.loads(ligne.get("contenu") or "{}")
        except json.JSONDecodeError:
            contenu = {}
        return cls(
            id=ligne.get("id"),
            titre=ligne.get("titre") or "Sans titre",
            matiere=ligne.get("matiere") or "",
            chapitre=ligne.get("chapitre") or "",
            theme=ligne.get("theme") or "",
            niveau=ligne.get("niveau") or "3e",
            contenu=coercer_contenu(contenu),
            statut=ligne.get("statut") or STATUT_A_APPRENDRE,
            favori=bool(ligne.get("favori", 0)),
            tags=ligne.get("tags") or "",
            source_nom=ligne.get("source_nom") or "",
            source_chemin=ligne.get("source_chemin") or "",
            source_type=ligne.get("source_type") or "",
            taille_octets=ligne.get("taille_octets") or 0,
            mode_generation=ligne.get("mode_generation") or "",
            modele_ia=ligne.get("modele_ia") or "",
            date_creation=ligne.get("date_creation") or "",
            date_modification=ligne.get("date_modification") or "",
            derniere_revision=ligne.get("derniere_revision") or "",
            nb_vues=ligne.get("nb_vues") or 0,
        )
