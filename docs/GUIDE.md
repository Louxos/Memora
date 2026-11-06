# Guide de la dernière version — Memora 1.0.0

> 🗄️ **Projet archivé le 6 novembre 2026.** Ce guide décrit la version 1.0.0
> **telle qu'elle a été laissée**. Il est conservé pour l'histoire : aucune
> assistance, aucun correctif et aucune mise à jour ne suivront. Les services
> externes (API Mistral) ont pu évoluer depuis.

---

## 1. Ce que faisait le logiciel

Memora transformait un cours en fiche de révision, puis rangeait cette fiche
dans une bibliothèque locale, sur l'ordinateur. Tout se passait en local, à
l'exception des appels à l'API Mistral nécessaires à l'analyse et à l'OCR.

Formats acceptés : **PDF, DOCX, TXT, MD, JPG, JPEG, PNG, WEBP**.

## 2. Installation (Windows)

1. Installer **Python 3.10 ou plus récent**, en 64 bits, depuis
   <https://www.python.org/downloads/> en cochant *Add Python to PATH*.
   `install.bat` choisit automatiquement le Python le plus récent disponible
   (3.14 → 3.13 → 3.12 → `py -3` → `python`) et refuse les versions 32 bits.
2. Double-cliquer sur **`install.bat`** une seule fois : il crée `.venv` et
   installe `requirements.txt` (2 à 3 minutes).
3. Double-cliquer sur **`run.bat`** pour lancer Memora. En cas d'erreur, le
   script relance avec la console pour afficher le détail.

Sur Linux/macOS :

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

## 3. Clé API Mistral

L'analyse IA et l'OCR utilisaient une clé **Mistral** :

1. Créer un compte sur <https://console.mistral.ai/> et générer une clé API.
2. Dans Memora : **Paramètres → Intelligence artificielle → Clé API** → coller
   la clé → *Enregistrer la clé* → *Tester la connexion*.

Autres méthodes :

- copier `.env.example` en `.env` à côté de `main.py` et y écrire
  `MISTRAL_API_KEY=ta-cle` ;
- ou définir la variable d'environnement `MISTRAL_API_KEY` ;
- `python main.py --check-api` teste la clé en ligne de commande ;
- `python main.py --demo` ajoute des fiches de démonstration **sans clé API**.

La clé était stockée dans le trousseau du système (`keyring`), masquée dans
l'interface et jamais écrite dans les logs. Le modèle par défaut était
`mistral-small-latest`.

## 4. Lancer Memora

```bash
python main.py               # application
python main.py --demo        # fiches de démonstration
python main.py --check-api   # test de la clé
python main.py --version     # affiche 1.0.0
```

## 5. De l'import à la fiche

1. **Nouvelle fiche** → déposer le document (clic ou glisser-déposer), avec
   aperçu.
2. Memora **extrait** le contenu : texte intégré des PDF, structure des DOCX
   (titres, listes, tableaux), texte des TXT/MD, OCR des images et des PDF
   scannés via Mistral OCR. La progression s'affichait étape par étape.
3. L'**IA Mistral** analysait le cours et construisait la fiche en JSON
   structuré, validé puis mis en forme.
4. La fiche était **enregistrée** dans la bibliothèque SQLite : lecture,
   modification de chaque section et des métadonnées, ajout/retrait de
   sections, régénération depuis le document source.

### Modes de génération

| Mode | Intention |
|---|---|
| ⚡ Rapide | aller à l'essentiel |
| 📚 Complète | toutes les sections utiles |
| 🎯 Brevet | orientation épreuve du brevet |
| 🧠 Active | davantage de questions d'auto-évaluation |

### Sections d'une fiche

Objectif · L'essentiel · Notions importantes · Définitions · Formules & règles ·
Méthodes · Dates, personnes & événements · Exemples · Pièges à éviter ·
« Si tu ne dois retenir que ça » · Teste-toi (réponses masquées) · Points
d'attention du document. Les sections vides n'étaient pas affichées ; les
points douteux étaient signalés plutôt qu'inventés.

## 6. Bibliothèque et révision

- Recherche plein texte, filtres (matière, chapitre, statut, favoris), tri
  (récent, ancien, alphabétique), organisation matière → chapitre.
- Statuts : 🔴 À apprendre · 🟡 À revoir · 🟢 Maîtrisée.
- Favoris, édition manuelle complète, régénération, compteur de vues et date
  de dernière révision.
- **Exports** : PDF A4 mis en page, Markdown, copie dans le presse-papiers,
  sauvegarde/import de toute la bibliothèque en JSON.
- Thèmes **clair / sombre / système**, logs locaux.

## 7. Données et sauvegarde

- Base SQLite créée automatiquement dans `%APPDATA%\Memora` (Windows), chemin
  surchargeable avec la variable `MEMORA_HOME`.
- Les documents originaux n'étaient **pas dupliqués** : la fiche conservait
  leur chemin.
- Sauvegarde/restauration depuis **Paramètres → Données** (export/import JSON).
- `.env`, `*.db`, `logs/`, `exports/` et `data/` étaient exclus de git.

## 8. En cas de problème (historique)

| Symptôme | Cause probable |
|---|---|
| « Aucune clé API trouvée » | clé absente des paramètres, de `.env` et de l'environnement |
| « Clé invalide » / quota | clé révoquée ou quota Mistral épuisé |
| « Impossible de joindre le service IA » | réseau, ou service/modèle modifié depuis l'archivage |
| PDF sans texte | PDF scanné : OCR requis (Mistral, ou Tesseract local + langue `fra`) |
| Python 32 bits refusé | PySide6 n'existe qu'en 64 bits |
| Interface qui ne démarre pas | dépendances non installées : relancer `install.bat` |

Aucun de ces cas ne sera corrigé : la version est figée.

## 9. Pour aller plus loin

- [Documentation technique](TECHNIQUE.md) — architecture, sécurité, tests,
  limites.
- [Dossier d'archivage](ARCHIVAGE.md) — décision, publication, release finale.
- [Cahier des charges initial](../prompt) — le prompt de développement complet.
- [Captures d'écran](captures) — l'interface telle qu'elle a été livrée.
- [Page d'archive](https://louxos.github.io/Memora/).
