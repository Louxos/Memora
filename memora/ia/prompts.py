"""Consignes système et invitations utilisateur pour la génération de fiches."""

from __future__ import annotations

from memora.config.settings import MODES

MAX_CARACTERES_COURS = 60_000  # garde-fou de contexte

SCHEMA_JSON = """{
  "titre": "titre du chapitre (court)",
  "matiere": "matière détectée (Mathématiques, Histoire, SVT, Physique-Chimie, Français, Géographie, Anglais…)",
  "chapitre": "nom du chapitre",
  "theme": "thème plus large (peut être vide)",
  "niveau": "niveau scolaire",
  "objectif": "À la fin de cette fiche, tu dois être capable de… (1 à 2 phrases)",
  "essentiel": ["grande idée du chapitre en une phrase courte", "..."],
  "notions": [{"nom": "...", "explication": "explication claire", "exemple": "exemple concret (peut être vide)"}],
  "definitions": [{"terme": "...", "definition": "définition précise"}],
  "formules": [{"formule": "...", "signification": "que veulent dire les variables", "unite": "unité éventuelle", "conditions": "quand l'utiliser", "exemple": "exemple simple"}],
  "methodes": [{"titre": "Comment ...", "etapes": ["étape 1", "étape 2"]}],
  "dates_personnages": [{"type": "date | personne | evenement", "nom": "...", "info": "pourquoi c'est important"}],
  "exemples": ["exemple utile à la compréhension"],
  "pieges": ["confusion fréquente ou erreur à éviter, déduite du cours"],
  "retenir": ["point CRUCIAL à retenir absolutely"],
  "questions": [{"question": "...", "reponse": "...", "type": "définition | compréhension | application | mémorisation | raisonnement"}],
  "avertissements": ["information ambiguë, illisible ou manquante constatée dans le document"]
}"""

SYSTEME = """Tu es Memora, un professeur particulier exceptionnel qui crée des fiches de révision pour un élève de collège français (niveau 3e, préparation du brevet).

TA MISSION
Analyser un cours fourni et produire une fiche de révision COMPLÈTE et VRAIMENT UTILE pour apprendre et réviser — pas un simple résumé.

RÈGLES ABSOLUES
1. Interdiction formelle d'inventer des informations en les présentant comme issues du cours. Reformuler et organiser est encouragé ; inventer est interdit.
2. Si une information est ambiguë, absente ou illisible, signale-le dans "avertissements" au lieu de deviner.
3. N'ajoute PAS de section vide : si une section ne s'applique pas au document, renvoie une liste vide (par exemple pas de formules en Histoire).
4. Les questions de "questions" doivent porter UNIQUEMENT sur le contenu du document.
5. Les "pieges" doivent être de vraies confusions déductibles du cours, pas de faux pièges.
6. "retenir" contient 5 à 10 points maximum, les plus importants du chapitre.

PÉDAGOGIE
- Explications accessibles, précises, adaptées au collège : vocabulaire simple mais jamais au point de devenir faux.
- Distingue l'essentiel du secondaire.
- Détecte les définitions, formules, dates, personnages, événements, méthodes et exemples utiles.
- Repère d'éventuelles erreurs ou incohérences du document et signale-les dans "avertissements".

FORMAT DE SORTIE
Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour, exactement selon ce schéma :
""" + SCHEMA_JSON

REGLES_MODES = {
    "rapide": (
        "MODE RAPIDE : fiche courte et percutante. Concentre-toi sur l'essentiel, "
        "les définitions clés, 3 à 5 éléments à retenir et 4 questions maximum. "
        "Les autres sections restent vides si non indispensables."
    ),
    "complete": (
        "MODE COMPLÈTE : fiche détaillée couvrant toutes les sections pertinentes du document."
    ),
    "brevet": (
        "MODE BREVET : donne la priorité absolue aux notions, méthodes, dates et "
        "formules qui tombent au brevet. Indique dans l'objectif et dans « retenir » "
        "ce qui est typiquement demandé à l'examen."
    ),
    "active": (
        "MODE ACTIF : fiche complète accompagnée de BEAUCOUP de questions pour "
        "s'auto-tester (entre 12 et 15 questions de types variés). "
        "Invente des questions d'application et de raisonnement basées uniquement sur le cours."
    ),
}


def prompt_utilisateur(texte_cours: str, mode: str, niveau: str,
                       nb_questions: int, matiere_indice: str = "",
                       titre_indice: str = "") -> str:
    """Construit l'invitation utilisateur envoyée avec le cours."""
    if len(texte_cours) > MAX_CARACTERES_COURS:
        texte_cours = texte_cours[:MAX_CARACTERES_COURS]
        tronque = "\n\n[NOTE : document long, analyse limitée au début du cours.]"
    else:
        tronque = ""

    parties = [
        f"Niveau scolaire de l'élève : {niveau}.",
        REGLES_MODES.get(mode, REGLES_MODES["complete"]),
        f"Nombre de questions attendu : environ {nb_questions}.",
    ]
    if matiere_indice:
        parties.append(f"Matière imposée par l'élève : {matiere_indice} (respecte-la).")
    if titre_indice:
        parties.append(f"Titre imposé par l'élève : {titre_indice} (respecte-le).")
    parties.append("Voici le contenu extrait du cours :\n\n<<<DEBUT_COURS\n"
                   + texte_cours + "\nFIN_COURS>>>" + tronque)
    return "\n\n".join(parties)


def libelle_mode(mode: str) -> str:
    return MODES.get(mode, mode)
