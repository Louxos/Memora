"""Rendu HTML d'une fiche (utilisé pour l'export PDF et l'export HTML).

Mise en page soignée : cartes colorées, badges, encadrés — pas de simple
texte noir sur fond blanc.
"""

from __future__ import annotations

import html
import re

from memora.core.models import Fiche, SECTION_EMOJIS, SECTION_TITRES, couleur_matiere

_COULEURS = {
    "objectif": ("#EEF2FF", "#3730A3"),
    "essentiel": ("#F5F3FF", "#5B21B6"),
    "notions": ("#EFF6FF", "#1D4ED8"),
    "definitions": ("#F0FDF4", "#15803D"),
    "formules": ("#FFF7ED", "#C2410C"),
    "methodes": ("#FDF2F8", "#BE185D"),
    "dates_personnages": ("#FEFCE8", "#A16207"),
    "exemples": ("#F0FDFA", "#0F766E"),
    "pieges": ("#FEF2F2", "#B91C1C"),
    "retenir": ("#FFF1F2", "#BE123C"),
    "questions": ("#F8FAFC", "#334155"),
    "avertissements": ("#FFFBEB", "#B45309"),
}


def _esc(t: str) -> str:
    return html.escape(t or "")


def _md_minimal(t: str) -> str:
    """**gras** et *italique* minimaux vers HTML (sur texte déjà échappé)."""
    t = _esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", t)
    return t


def entete_html(fiche: Fiche) -> str:
    couleur = couleur_matiere(fiche.matiere)
    badges = f"""
      <span style="background:{couleur};color:#ffffff;border-radius:10px;
                   padding:3px 12px;font-size:12px;font-weight:600;">{_esc(fiche.matiere)}</span>"""
    if fiche.niveau:
        badges += f'\n      <span class="badge">Niveau {_esc(fiche.niveau)}</span>'
    if fiche.chapitre:
        badges += f'\n      <span class="badge">{_esc(fiche.chapitre)}</span>'
    return f"""
    <div style="border-left:6px solid {couleur};padding-left:18px;margin-bottom:8px;">
      <h1 style="margin:0;font-size:26px;color:#111827;">{_esc(fiche.titre)}</h1>
      <div style="margin-top:10px;">{badges}
        <span class="badge">Créée le {_esc((fiche.date_creation or '')[:10])}</span>
      </div>
    </div>"""


def _carte(cle: str, titre: str, corps: str) -> str:
    fond, texte = _COULEURS.get(cle, ("#F8FAFC", "#334155"))
    return f"""
  <table class="carte" cellspacing="0" cellpadding="0" style="background:{fond};">
   <tr><td style="padding:16px 20px;">
    <h2 style="margin:0 0 10px 0;font-size:17px;color:{texte};">
        {SECTION_EMOJIS.get(cle, '')}&nbsp; {_esc(titre)}</h2>
    {corps}
   </td></tr>
  </table>"""


def fiche_vers_html(fiche: Fiche, inclure_reponses: bool = True) -> str:
    c = fiche.contenu
    parties: list[str] = []

    for cle, titre, _ in fiche.sections():
        if cle == "objectif":
            corps = f'<p style="margin:0;font-size:14px;">{_md_minimal(c["objectif"])}</p>'
            parties.append(_carte(cle, "Objectif", corps))
            continue
        if cle in ("essentiel", "exemples", "retenir"):
            items = "".join(f'<li style="margin:5px 0;">{_md_minimal(i)}</li>' for i in c[cle])
            corps = f'<ul style="margin:0;padding-left:22px;font-size:14px;">{items}</ul>'
            parties.append(_carte(cle, titre, corps))
            continue
        if cle == "notions":
            blocs = []
            for n in c["notions"]:
                ex = f'<div style="margin-top:5px;color:#374151;font-size:13px;">💡 <i>{_md_minimal(n["exemple"])}</i></div>' if n.get("exemple") else ""
                blocs.append(
                    f'<div style="margin:10px 0;"><b style="font-size:14.5px;">{_esc(n["nom"])}</b>'
                    f'<div style="margin-top:3px;font-size:14px;">{_md_minimal(n["explication"])}</div>{ex}</div>'
                )
            parties.append(_carte(cle, titre, "".join(blocs)))
            continue
        if cle == "definitions":
            blocs = "".join(
                f'<p style="margin:8px 0;font-size:14px;"><b>{_esc(d["terme"])}</b> : {_md_minimal(d["definition"])}</p>'
                for d in c["definitions"]
            )
            parties.append(_carte(cle, titre, blocs))
            continue
        if cle == "formules":
            blocs = []
            for f in c["formules"]:
                details = ""
                if f.get("signification"):
                    details += f"<div>• {_md_minimal(f['signification'])}</div>"
                if f.get("unite"):
                    details += f"<div>• Unité : {_esc(f['unite'])}</div>"
                if f.get("conditions"):
                    details += f"<div>• Quand l'utiliser : {_md_minimal(f['conditions'])}</div>"
                if f.get("exemple"):
                    details += f"<div>• Exemple : <i>{_md_minimal(f['exemple'])}</i></div>"
                blocs.append(
                    f'<div style="margin:10px 0;">'
                    f'<div style="font-family:\'Consolas\',monospace;font-size:15px;font-weight:700;'
                    f'background:#ffffff;border:1px solid #e5e7eb;border-radius:6px;padding:8px 12px;'
                    f'display:inline-block;">{_esc(f["formule"])}</div>'
                    f'<div style="margin-top:5px;font-size:13px;color:#374151;">{details}</div></div>'
                )
            parties.append(_carte(cle, titre, "".join(blocs)))
            continue
        if cle == "methodes":
            blocs = []
            for m in c["methodes"]:
                etapes = m.get("etapes") or []
                pas = "".join(f"<li style='margin:4px 0;'>{_md_minimal(e)}</li>" for e in etapes)
                blocs.append(
                    f'<div style="margin:12px 0;"><b style="font-size:14.5px;">{_esc(m["titre"])}</b>'
                    f'<ol style="margin:6px 0 0 0;padding-left:22px;font-size:14px;">{pas}</ol></div>'
                )
            parties.append(_carte(cle, titre, "".join(blocs)))
            continue
        if cle == "dates_personnages":
            icone = {"date": "📅", "personne": "👤", "événement": "⚡"}
            blocs = "".join(
                f'<p style="margin:8px 0;font-size:14px;">{icone.get(d["type"], "•")} '
                f'<b>{_esc(d["nom"])}</b> — {_md_minimal(d["info"])}</p>'
                for d in c["dates_personnages"]
            )
            parties.append(_carte(cle, titre, blocs))
            continue
        if cle in ("pieges", "avertissements"):
            items = "".join(f"<li style='margin:5px 0;'>{_md_minimal(i)}</li>" for i in c[cle])
            corps = f"<ul style='margin:0;padding-left:22px;font-size:14px;'>{items}</ul>"
            parties.append(_carte(cle, titre, corps))
            continue
        if cle == "questions":
            blocs = []
            for i, q in enumerate(c["questions"], 1):
                reponse = ""
                if inclure_reponses:
                    reponse = (
                        f'<div style="margin-top:5px;padding:8px 12px;background:#ffffff;'
                        f'border-radius:6px;font-size:13.5px;color:#1F2937;">'
                        f'<b>Réponse :</b> {_md_minimal(q["reponse"])}</div>'
                    )
                blocs.append(
                    f'<div style="margin:12px 0;"><b style="font-size:14px;">{i}. {_md_minimal(q["question"])}</b>{reponse}</div>'
                )
            parties.append(_carte(cle, titre, "".join(blocs)))
            continue

    css = """
  <style>
   body { font-family: 'Segoe UI', 'Noto Sans', sans-serif; color:#1F2937; }
   .carte { width:100%; border:none; border-radius:12px; margin:14px 0; }
   .badge { background:#E5E7EB; color:#374151; border-radius:10px; padding:3px 12px;
            font-size:12px; font-weight:600; margin-right:6px; }
   .pied { color:#9CA3AF; font-size:11px; text-align:center; margin-top:26px; }
  </style>"""
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">{css}</head>
<body style="margin:0;">
  {entete_html(fiche)}
  {"".join(parties)}
  <p class="pied">Fiche générée avec Memora — logicielle personnel de révision</p>
</body></html>"""
