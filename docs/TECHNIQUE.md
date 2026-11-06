# Documentation technique — Memora 1.0.0 (archive)

> 🗄️ **Projet archivé le 6 novembre 2026.** Ce document décrit l'architecture
> de la dernière version **telle qu'elle a été laissée**, sans rien corriger ni
> promettre. Il est publié à titre de référence.

---

## 1. Vue d'ensemble

Application **desktop locale** en Python 3.10+, interface **PySide6 / Qt 6**,
stockage **SQLite**, analyses confiées à l'**API Mistral** (chat + OCR). Aucun
serveur propre, aucun compte, aucune télémétrie. Seules les requêtes vers
`https://api.mistral.ai` sortaient de l'ordinateur, avec le contenu du cours à
analyser.

```
main.py ──> memora.ui (PySide6) ──> memora.core.pipeline (QThread)
                                        │
                    memora.extraction ──┤──> memora.ia (Mistral)
                                        │
                    memora.core.database (SQLite) ──> memora.export (PDF/MD/HTML)
```

| Module | Rôle |
|---|---|
| `memora/config` | réglages (`settings.py`), chemins (`paths.py`), clé API (`secure_storage.py`, `keyring`) |
| `memora/core` | modèle `Fiche`, base SQLite, pipeline de génération, fiches de démonstration, imports paresseux de l'IA |
| `memora/extraction` | PDF (PyMuPDF), DOCX (python-docx), TXT/MD, OCR (Mistral, repli Tesseract), orchestrateur `extractor.py` |
| `memora/ia` | client HTTP Mistral, prompts, générateur de fiches (JSON validé) |
| `memora/export` | rendu HTML, Markdown, PDF A4 via `QPdfWriter` |
| `memora/ui` | thème QSS clair/sombre, icônes, widgets, vues (accueil, bibliothèque, fiche, import, édition, paramètres) |
| `memora/utils` | journalisation locale, erreurs typées, utilitaires fichiers |
| `tests/` | 41 tests pytest |

## 2. Modèle de données

La fiche (`memora/core/models.py`) est un objet `Fiche` dont le contenu est un
**dictionnaire JSON de sections adaptatives** : seules les sections non vides
sont affichées et exportées. Douze sections étaient définies (objectif,
essentiel, notions, définitions, formules, méthodes, dates/personnages,
exemples, pièges, « à retenir », questions, avertissements). Le JSON renvoyé
par l'IA était normalisé/coercé avant affichage : champs manquants, listes
malformées et méthodes en texte multi-lignes étaient tolérés.

Statuts de révision : `a_apprendre`, `a_revoir`, `maitrisee`. Couleurs par
matière définies dans `MATIERES_COULEURS`.

Une seule table SQLite, créée automatiquement (`memora/core/database.py`) :

```sql
CREATE TABLE fiches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL, matiere TEXT, chapitre TEXT, theme TEXT, niveau TEXT,
    contenu TEXT NOT NULL DEFAULT '{}',   -- JSON des sections
    statut TEXT, favori INTEGER, tags TEXT,
    source_nom TEXT, source_chemin TEXT, source_type TEXT, taille_octets INTEGER,
    mode_generation TEXT, modele_ia TEXT,
    date_creation TEXT, date_modification TEXT, derniere_revision TEXT,
    nb_vues INTEGER
);
-- index sur matiere, chapitre, statut ; journal_mode=WAL
```

Tous les accès passaient par un `threading.Lock` car l'interface et le
`QThread` de génération pouvaient écrire en parallèle. La recherche plein
texte et les filtres étaient implémentés en SQL sur cette table. Les documents
sources n'étaient **pas copiés** : seul leur chemin était conservé.

## 3. Pipeline de génération

`memora/core/pipeline.py` exécutait la génération dans un `QThread` et
émettait des signaux de progression (`etape_changee`, `etape_terminee`,
`terminee`, `echouee`) : sept étapes, de la lecture du document à la
sauvegarde. L'OCR n'était marqué comme étape que si le document le demandait.

1. Vérification de l'extension (`memora/utils/files.py`).
2. `extraire()` : texte PDF, structure DOCX, TXT/MD, ou OCR des images et PDF
   scannés. Détection automatique des PDF sans texte.
3. `generer_fiche()` : envoi du contenu au modèle Mistral avec un prompt
   adapté au mode (rapide, complète, brevet, active), au niveau et au nombre
   de questions ; réception d'un JSON structuré, validé puis coercé.
4. Mise en forme, puis `Database.ajouter_fiche()`.

Le client HTTP (`memora/ia/client.py`) utilisait trois points d'entrée :
`GET /v1/models` (test de connexion), `POST /v1/chat/completions` (fiches,
JSON garanti), `POST /v1/ocr` (images). Erreurs traduites en exceptions
métier (`ApiKeyInvalidError`, `ApiQuotaError`, `NetworkError`,
`AiResponseError`, `DocumentTooLargeError`…), au plus une nouvelle tentative
sur erreur réseau/serveur, jamais sur clé invalide. Limite de 30 Mio pour les
contenus base64.

## 4. Sécurité et vie privée

- Clé API lue depuis le trousseau système (`keyring`), `.env` ou variable
  d'environnement ; jamais versionnée, jamais journalisée, masquée dans l'UI.
- `.gitignore` excluait `.env`, `api_key.bin`, `*.db*`, `data/`, `logs/`,
  `exports/`, `.venv/`, `__pycache__/` et les documents de test.
- Journalisation locale uniquement (`memora/utils/logging_setup.py`).
- Aucune donnée utilisateur sur un serveur : la page d'archive GitHub Pages
  est strictement statique et ne collecte rien.
- Dépendance de confiance assumée : le contenu du cours était envoyé à l'API
  Mistral lors de l'analyse ; c'était le seul flux sortant.

## 5. Interface et exports

Thèmes QSS clair/sombre avec dégradé signature indigo → violet
(`memora/ui/theme.py`, `#5B5FE9` / `#8B5CF6` en clair, `#7C7FF2` /
`#A78BFA` en sombre). La page d'archive reprend ces deux accents sur fond
`#101219`. Vues : accueil, bibliothèque, fiche, import, édition, paramètres,
plus un système de rendu de sections (`sections_rendu.py`).

Exports : `fiche_vers_html()` → Markdown (`markdown_export.py`) ou PDF A4 via
`QTextDocument` + `QPdfWriter` (`pdf_export.py`) ; sauvegarde/import JSON de
la bibliothèque ; copie presse-papiers.

## 6. Tests

```bash
python -m pytest tests/ -q
```

41 tests répartis sur 8 fichiers : modèle de données et coercition JSON,
base SQLite (CRUD, filtres, recherche, statuts), extraction (PDF, DOCX,
images, OCR), client Mistral (clé invalide, quota, réseau, timeout, JSON
invalide), générateur de fiches, exports (Markdown/HTML/PDF) et démarrage de
l'interface avec `QT_QPA_PLATFORM=minimal`. `scripts/captures.py` produisait
les six captures d'écran de `docs/captures/`.

## 7. Limites connues (et désormais définitives)

- **Windows d'abord** : `install.bat` / `run.bat` sont des scripts batch ;
  Linux/macOS fonctionnaient via la ligne de commande mais n'étaient pas la
  cible principale.
- **Dépendance à une API externe** : sans clé Mistral valide, seule la démo
  fonctionnait ; modèles, tarifs et endpoint OCR pouvaient changer.
- **OCR local optionnel** : le repli Tesseract demandait le binaire et le
  module `pytesseract`, non installés par défaut.
- **Pas de synchronisation** : bibliothèque strictement locale, sauvegarde
  manuelle en JSON.
- **Pas de licence** : code consultable, non réutilisable librement.
- **Plus aucune maintenance** : ces limites ne seront pas levées. C'est
  précisément l'une des raisons de l'archivage (voir
  [ARCHIVAGE.md](ARCHIVAGE.md)).

## 8. Publication de l'archive

Le site statique est généré par `scripts/build_site.py` depuis les modèles
`site/` (trois fichiers fournis + `favicon.svg`), résolus dans `docs/` avec le
CSS inline. Le workflow `.github/workflows/pages.yml` construit et déploie sur
GitHub Pages. Détails dans [ARCHIVAGE.md](ARCHIVAGE.md).
