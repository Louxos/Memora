"""Export d'une fiche en Markdown (fichier .md, copie presse-papiers…)."""

from __future__ import annotations

from memora.core.models import Fiche, SECTION_TITRES, STATUT_LABELS


def fiche_vers_markdown(fiche: Fiche, inclure_reponses: bool = True) -> str:
    c = fiche.contenu
    lignes: list[str] = [f"# {fiche.titre}", ""]

    meta = " • ".join(x for x in (fiche.matiere, fiche.niveau, fiche.chapitre) if x)
    if meta:
        lignes += [f"*{meta}*", ""]
    lignes += [f"*Statut : {fiche.statut_label()}*", ""]

    def liste(cle: str) -> None:
        for item in c.get(cle, []):
            lignes.append(f"- {item}")
        lignes.append("")

    for cle, titre, _ in fiche.sections():
        lignes.append(f"## {titre}")
        lignes.append("")
        if cle == "objectif":
            lignes += [f"> {c['objectif']}", ""]
        elif cle in ("essentiel", "exemples", "pieges", "retenir", "avertissements"):
            liste(cle)
        elif cle == "notions":
            for n in c["notions"]:
                lignes.append(f"**{n['nom']}** — {n['explication']}")
                if n.get("exemple"):
                    lignes.append(f"  *Exemple : {n['exemple']}*")
                lignes.append("")
        elif cle == "definitions":
            for d in c["definitions"]:
                lignes.append(f"**{d['terme']}** : {d['definition']}")
            lignes.append("")
        elif cle == "formules":
            for f in c["formules"]:
                lignes.append(f"- `{f['formule']}`")
                if f.get("signification"):
                    lignes.append(f"  - {f['signification']}")
                if f.get("unite"):
                    lignes.append(f"  - Unité : {f['unite']}")
                if f.get("conditions"):
                    lignes.append(f"  - Utilisation : {f['conditions']}")
                if f.get("exemple"):
                    lignes.append(f"  - Exemple : {f['exemple']}")
            lignes.append("")
        elif cle == "methodes":
            for m in c["methodes"]:
                lignes += [f"**{m['titre']}**", ""]
                etapes = m.get("etapes") or []
                for i, etape in enumerate(etapes, 1):
                    lignes.append(f"{i}. {etape}")
                lignes.append("")
        elif cle == "dates_personnages":
            for d in c["dates_personnages"]:
                lignes.append(f"- **{d['nom']}** ({d['type']}) : {d['info']}")
            lignes.append("")
        elif cle == "questions":
            for i, q in enumerate(c["questions"], 1):
                lignes.append(f"{i}. {q['question']}")
                if inclure_reponses:
                    lignes.append(f"   → *{q['reponse']}*")
            lignes.append("")

    return "\n".join(lignes).strip() + "\n"


def fiche_vers_texte_simple(fiche: Fiche) -> str:
    """Version texte uni-bloc (copie rapide)."""
    return fiche_vers_markdown(fiche)
