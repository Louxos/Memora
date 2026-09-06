"""Données de démonstration : tester Memora sans clé API.

Ces fiches sont clairement identifiées comme démonstration et n'ont rien
à voir avec une génération IA réelle.
"""

from __future__ import annotations

from memora.core.models import Fiche, maintenant_iso

_DEMO_PGMD = {
    "objectif": "À la fin de cette fiche, tu dois être capable de raconter les grandes étapes de la Première Guerre mondiale, d'expliquer ses causes et ses conséquences, et de citer les dates clés attendues au brevet.",
    "essentiel": [
        "La Première Guerre mondiale (1914-1918) oppose la Triple-Entente (France, Royaume-Uni, Russie) à la Triple-Alliance (Allemagne, Autriche-Hongrie, Italie).",
        "Elle commence par l'attentat de Sarajevo (28 juin 1914) et l'entrée en guerre des grandes puissances européennes.",
        "C'est une guerre totale et industrielle : tous les citoyens sont mobilisés (soldats, femmes à l'arrière, économie orientée vers la guerre).",
        "Elle fait environ 10 millions de morts et bouleverse l'Europe : nouvelles frontières, révolutions, effondrement des empires.",
    ],
    "notions": [
        {"nom": "Guerre de mouvement", "explication": "Phase initiale (1914) où les armées se déplacent rapidement, jusqu'à la bataille de la Marne qui stoppe l'avancée allemande.", "exemple": "La bataille de la Marne (septembre 1914)."},
        {"nom": "Guerre de position", "explication": "À partir de fin 1914, les soldats s'enterrent dans des tranchées et le front se fige pendant des années.", "exemple": "Bataille de Verdun (1916) : 10 mois de combats."},
        {"nom": "Guerre totale", "explication": "Toutes les ressources des États (économiques, humaines, scientifiques) sont mobilisées pour la guerre.", "exemple": "Les femmes remplacent les hommes partis au front (« munitionnettes »)."},
    ],
    "definitions": [
        {"terme": "Triple-Entente", "definition": "Alliance de la France, du Royaume-Uni et de la Russie pendant la Première Guerre mondiale."},
        {"terme": "Triple-Alliance", "definition": "Alliance de l'Allemagne, de l'Autriche-Hongrie et de l'Italie (qui change de camp en 1915)."},
        {"terme": "Traité de Versailles", "definition": "Traité de paix signé le 28 juin 1919, qui déclare l'Allemagne responsable de la guerre et lui impose de lourdes pertes territoriales et financières."},
    ],
    "formules": [],
    "methodes": [],
    "dates_personnages": [
        {"type": "date", "nom": "28 juin 1914", "info": "Attentat de Sarajevo : l'archiduc François-Ferdinand est assassiné."},
        {"type": "date", "nom": "1916", "info": "Batailles de Verdun et de la Somme, symboles de la guerre des tranchées."},
        {"type": "date", "nom": "11 novembre 1918", "info": "Armistice : fin des combats."},
        {"type": "personne", "nom": "Clemenceau", "info": "Chef du gouvernement français à partir de 1917, surnommé « le Père la Victoire »."},
        {"type": "evenement", "nom": "Révolution russe", "info": "1917 : la Russie se retire de la guerre après la révolution bolchevique."},
    ],
    "exemples": [],
    "pieges": [
        "Ne confonds pas l'armistice (11 novembre 1918, fin des combats) et le traité de Versailles (28 juin 1919, paix officielle).",
        "L'Italie change de camp en 1915 : elle est dans la Triple-Alliance au départ mais combat aux côtés de l'Entente.",
    ],
    "retenir": [
        "1914-1918 : dates de la Première Guerre mondiale.",
        "Attentat de Sarajevo (28 juin 1914) : élément déclencheur.",
        "Deux phases : mouvement (1914) puis position/tranchées (1915-1918).",
        "Guerre totale : mobilisation de tout le pays, rôle nouveau des femmes.",
        "Verdun 1916 : symbole de la violence de masse.",
        "Armistice le 11 novembre 1918 ; traité de Versailles en 1919.",
        "Environ 10 millions de morts : l'Europe est traumatisée.",
    ],
    "questions": [
        {"question": "Quel événement déclenche la Première Guerre mondiale et à quelle date ?", "reponse": "L'attentat de Sarajevo, le 28 juin 1914 (assassinat de l'archiduc François-Ferdinand d'Autriche-Hongrie).", "type": "mémorisation"},
        {"question": "Quelle différence entre guerre de mouvement et guerre de position ?", "reponse": "La guerre de mouvement (1914) voit les armées avancer rapidement ; la guerre de position (ensuite) fige le front dans des tranchées.", "type": "compréhension"},
        {"question": "Pourquoi parle-t-on de « guerre totale » ?", "reponse": "Parce que toutes les ressources des pays (soldats, économie, femmes à l'arrière, propagande) sont mobilisées pour l'effort de guerre.", "type": "compréhension"},
        {"question": "Que se passe-t-il le 11 novembre 1918 ?", "reponse": "Signature de l'armistice qui met fin aux combats de la Première Guerre mondiale.", "type": "mémorisation"},
    ],
    "avertissements": ["Fiche de démonstration : contenu rédigé à la main, non généré par IA."],
}

_DEMO_MATHS = {
    "objectif": "À la fin de cette fiche, tu dois être capable de développer et factoriser des expressions littérales, en particulier avec les identités remarquables.",
    "essentiel": [
        "Développer, c'est transformer un produit en somme : k(a+b) = ka + kb.",
        "Factoriser, c'est transformer une somme en produit : ka + kb = k(a+b).",
        "Les identités remarquables sont des formules à connaître par cœur pour développer et factoriser plus vite.",
        "Réduire une expression, c'est regrouper les termes de même nature pour l'écrire le plus simplement possible.",
    ],
    "notions": [
        {"nom": "Expression littérale", "explication": "Expression qui contient une ou plusieurs lettres représentant des nombres (par exemple 3x + 2).", "exemple": "Pour x = 5, l'expression 3x + 2 vaut 17."},
        {"nom": "Développer", "explication": "Transformer un produit en une somme ou une différence, en distribuant chaque facteur.", "exemple": "2(x + 4) = 2x + 8."},
        {"nom": "Factoriser", "explication": "Transformer une somme en un produit en repérant un facteur commun.", "exemple": "5x + 10 = 5(x + 2)."},
    ],
    "definitions": [
        {"terme": "Identité remarquable", "definition": "Égalité vraie pour toutes les valeurs des lettres, très utile en calcul littéral."},
    ],
    "formules": [
        {"formule": "(a + b)² = a² + 2ab + b²", "signification": "a et b sont deux nombres quelconques ; le double produit 2ab est essentiel.", "unite": "", "conditions": "Valable pour tous les nombres.", "exemple": "(x + 3)² = x² + 6x + 9."},
        {"formule": "(a − b)² = a² − 2ab + b²", "signification": "Attention au signe moins devant le double produit uniquement.", "unite": "", "conditions": "Valable pour tous les nombres.", "exemple": "(x − 3)² = x² − 6x + 9."},
        {"formule": "(a − b)(a + b) = a² − b²", "signification": "Produit d'une somme par une différence : les termes du milieu s'annulent.", "unite": "", "conditions": "Valable pour tous les nombres.", "exemple": "(x − 5)(x + 5) = x² − 25."},
    ],
    "methodes": [
        {"titre": "Comment factoriser une expression ?", "etapes": ["Chercher un facteur commun aux deux termes (nombre ou lettre).", "Écrire ce facteur commun devant une parenthèse.", "Écrire ce qui reste de chaque terme dans la parenthèse.", "Vérifier en redéveloppant mentalement."]},
        {"titre": "Comment développer avec une identité remarquable ?", "etapes": ["Identifier laquelle des trois identités correspond à l'expression.", "Remplacer a et b par les valeurs de l'expression.", "Appliquer la formule sans oublier le double produit.", "Réduire le résultat."]},
    ],
    "dates_personnages": [],
    "exemples": [
        "Développer : 3(2x + 5) − 4x = 6x + 15 − 4x = 2x + 15.",
        "Factoriser : x² − 9 = (x − 3)(x + 3) grâce à a² − b².",
    ],
    "pieges": [
        "Erreur classique : (a + b)² n'est PAS égal à a² + b² (on oublie le double produit 2ab).",
        "Le signe « moins » devant une parenthèse change TOUS les signes à l'intérieur : −(x − 4) = −x + 4.",
    ],
    "retenir": [
        "k(a + b) = ka + kb (développement) et ka + kb = k(a + b) (factorisation).",
        "(a + b)² = a² + 2ab + b²",
        "(a − b)² = a² − 2ab + b²",
        "(a − b)(a + b) = a² − b²",
        "Toujours réduire le résultat final.",
        "Vérifier une factorisation en redéveloppant.",
    ],
    "questions": [
        {"question": "Développe (x + 5)².", "reponse": "x² + 10x + 25 (double produit : 2 × x × 5 = 10x).", "type": "application"},
        {"question": "Factorise 7x + 21.", "reponse": "7(x + 3) : le facteur commun est 7.", "type": "application"},
        {"question": "Factorise x² − 49.", "reponse": "(x − 7)(x + 7), avec l'identité a² − b² = (a − b)(a + b).", "type": "application"},
        {"question": "Pourquoi (a + b)² ≠ a² + b² ?", "reponse": "Parce que le développement donne aussi le double produit : (a+b)² = a² + 2ab + b².", "type": "raisonnement"},
    ],
    "avertissements": ["Fiche de démonstration : contenu rédigé à la main, non généré par IA."],
}


def fiches_demo() -> list[Fiche]:
    """Construit les fiches de démonstration."""
    maintenant = maintenant_iso()
    return [
        Fiche(
            titre="[Démo] La Première Guerre mondiale",
            matiere="Histoire", chapitre="Première Guerre mondiale", theme="Le monde de 1914 à 1945",
            niveau="3e", contenu=_DEMO_PGMD, tags="démo", statut="a_revoir", favori=True,
            source_nom="Démonstration", source_type="demo",
            date_creation=maintenant, date_modification=maintenant,
        ),
        Fiche(
            titre="[Démo] Calcul littéral et identités remarquables",
            matiere="Mathématiques", chapitre="Calcul littéral", theme="Algèbre",
            niveau="3e", contenu=_DEMO_MATHS, tags="démo", statut="maitrisee", favori=False,
            source_nom="Démonstration", source_type="demo",
            date_creation=maintenant, date_modification=maintenant,
        ),
    ]
