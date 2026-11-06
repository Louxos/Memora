# 🧠 Memora — projet archivé

> ## 🗄️ Archivé le 6 novembre 2026
>
> **Le développement de Memora est définitivement arrêté.** Aucune nouvelle
> fonctionnalité, aucun correctif, aucune réponse de support, aucune reprise
> prévue. Le dépôt reste public, en lecture seule, comme archive de ce qui a
> été construit. Rien n'a été supprimé.
>
> **Page d'archive :** <https://louxos.github.io/Memora/> ·
> **Dernière version :** [1.0.0](https://github.com/Louxos/Memora/releases/tag/v1.0.0) ·
> **Dossier d'archivage :** [docs/ARCHIVAGE.md](docs/ARCHIVAGE.md)

| Accueil | Fiche générée (thème sombre) |
|---|---|
| ![Accueil](docs/captures/01-accueil.png) | ![Fiche](docs/captures/06-fiche-sombre.png) |

*Captures de la dernière version, conservées telles qu'elles ont été livrées.*

---

## État des lieux

| | |
|---|---|
| **Archivé le** | 6 novembre 2026 |
| **Dernière version** | **1.0.0** — version finale, publiée le 6 novembre 2026 |
| **Dépôt** | Public, conservé avec tout son historique |
| **GitHub Page** | Site statique d'archive, servi depuis `docs/` |
| **Développement** | Arrêté — code, versions et commits figés |

Memora **était** un logiciel personnel de révision, pensé pour un élève de 3e
qui préparait le brevet. On lui donnait un cours (PDF, Word, texte, photo), il
en tirait une **fiche de révision claire et complète**, rangée dans une
bibliothèque locale.

> Importer un cours → en comprendre le contenu → produire une fiche → la
> sauvegarder et la retrouver facilement.

Le code fonctionnel de la version 1.0.0 est toujours là, ainsi que les 41
tests, les captures d'écran et le cahier des charges initial
([`prompt`](prompt)). Il est livré **en l'état**, sans garantie : les services
externes (API Mistral, modèles, OCR) et les bibliothèques (PySide6, PyMuPDF)
ont pu évoluer depuis.

## Ce qui reste accessible

- [La page d'archive (GitHub Pages)](https://louxos.github.io/Memora/) — état du
  projet, raisons de l'arrêt, liens vers le code.
- [La version 1.0.0](https://github.com/Louxos/Memora/releases/tag/v1.0.0) —
  dernière version publiée, et le restera.
- [Le code source](https://github.com/Louxos/Memora) et
  [l'historique des commits](https://github.com/Louxos/Memora/commits/main).
- [Guide de la dernière version](docs/GUIDE.md),
  [documentation technique](docs/TECHNIQUE.md),
  [dossier d'archivage](docs/ARCHIVAGE.md) et
  [captures d'écran](docs/captures).
- [Le cahier des charges initial](prompt) — le prompt de développement complet.

## Ce qui s'arrête

Aucune évolution du logiciel, aucune mise à jour de dépendances, aucun
correctif, aucun support. Les issues et les pull requests ne sont plus
traitées. Si vous cherchez un outil de révision maintenu, choisissez-en un qui
l'est. Pour figer officiellement le dépôt côté GitHub (passage en lecture seule
technique), voir [docs/ARCHIVAGE.md](docs/ARCHIVAGE.md) : c'est une action
volontairement laissée à la main, afin de ne pas empêcher la publication de la
page et de la dernière version.

## ✨ Ce que faisait Memora (version 1.0.0)

- **Import de cours** : PDF, DOCX, TXT, MD, JPG, JPEG, PNG, WEBP — au clic ou
  en glisser-déposer, avec aperçu du document.
- **Extraction intelligente** : texte intégré des PDF (détection des PDF
  scannés), structure des DOCX conservée, lecture des TXT, **OCR** des images
  via Mistral OCR avec repli possible sur Tesseract local.
- **Fiches générées par IA (Mistral)** : objectif, l'essentiel, notions,
  définitions, formules, méthodes, dates/personnages, exemples, pièges,
  « Si tu ne dois retenir que ça » et questions à réponses masquées. Sections
  adaptatives : rien de vide, rien d'inventé, les points douteux signalés.
- **4 modes de génération** : ⚡ Rapide, 📚 Complète, 🎯 Brevet, 🧠 Active.
- **Bibliothèque locale** : recherche plein texte, filtres, tri, organisation
  par matière → chapitre, statuts de révision, favoris, édition manuelle
  complète et régénération depuis le document source.
- **Exports** : PDF mis en page, Markdown, presse-papiers, sauvegarde/import
  JSON de toute la bibliothèque.
- **Thèmes clair / sombre / système**, mode démonstration sans clé API, logs
  locaux.

Tout fonctionnait **100 % en local** : aucun serveur distant, aucune donnée
envoyée ailleurs qu'à l'API Mistral lors des analyses.

## 🛠️ Technologies (figées)

| Rôle | Choix |
|---|---|
| Langage | Python 3.10+ |
| Interface | PySide6 (Qt 6) — thèmes QSS |
| Base de données | SQLite (créée automatiquement) |
| IA | API Mistral (`mistral-small-latest` par défaut) : chat + OCR |
| Extraction | PyMuPDF (PDF), python-docx (Word) |
| Sécurité | `keyring` (trousseau système) pour la clé API |
| Publication de l'archive | GitHub Pages, site statique sans dépendance |

## 📦 Utiliser la dernière version (à titre historique)

La procédure ci-dessous est celle de la version 1.0.0, conservée telle quelle.
**Aucune assistance n'est fournie si elle ne fonctionne plus.**

1. Installer **Python 3.10 ou plus récent** (Windows, 64 bits, avec l'option
   *Add Python to PATH*).
2. Double-cliquer sur **`install.bat`** une seule fois.
3. Renseigner une clé **Mistral** dans *Paramètres → Intelligence artificielle*,
   ou créer un fichier `.env` d'après [`.env.example`](.env.example)
   (`MISTRAL_API_KEY=…`), ou définir la variable d'environnement du même nom.
4. Double-cliquer sur **`run.bat`** pour lancer Memora.

Options de `main.py` : `--demo` (fiches de démonstration sans clé API),
`--check-api` (test de la clé), `--version` (affiche `1.0.0`).

Sur Linux/macOS : `python3 -m venv .venv && .venv/bin/pip install -r
requirements.txt`, puis `.venv/bin/python main.py`.

Le guide complet de la dernière version est dans
[docs/GUIDE.md](docs/GUIDE.md), l'architecture dans
[docs/TECHNIQUE.md](docs/TECHNIQUE.md).

## 🌐 La GitHub Page d'archive

Les **trois fichiers fournis** sont conservés dans [`site/`](site) :
[`index.html`](site/index.html), [`404.html`](site/404.html) et
[`site.css`](site/site.css), avec leurs marqueurs `{{…}}`, plus le logo
[`favicon.svg`](site/favicon.svg). Ils sont adaptés au projet (contenu, charte
indigo/violet de Memora, liens), mais leur structure est celle d'origine.

[`scripts/build_site.py`](scripts/build_site.py) résout les marqueurs, injecte
le CSS dans chaque page et écrit le site prêt à publier dans **`docs/`** :

```bash
python3 scripts/build_site.py                 # génère docs/
python3 -m http.server 8000 --directory docs  # aperçu local
```

Aucune dépendance externe ni ressource distante : le site est entièrement
statique. Le workflow
[`.github/workflows/pages.yml`](.github/workflows/pages.yml) reconstruit
`docs/` et le publie sur GitHub Pages à chaque modification (déploiement
depuis la branche `main`). Si Pages n'est pas encore activé : *Settings →
Pages → Build and deployment → Source : GitHub Actions*. Autre possibilité,
sans Actions : *Source : Deploy from a branch → `main` → `/docs`*.

## 📂 Structure du dépôt

```
Memora/
├── README.md                # ce fichier — état archivé
├── prompt                   # cahier des charges initial (historique)
├── main.py                  # point d'entrée de la version 1.0.0
├── run.bat / install.bat    # lancement et installation Windows
├── requirements.txt         # dépendances figées
├── .env.example             # modèle de configuration (aucun secret)
├── memora/                  # application PySide6 (config, core, extraction,
│                            #   ia, export, ui, utils)
├── tests/                   # suite pytest — 41 tests
├── site/                    # modèles de la page d'archive (fichiers fournis)
│   ├── index.html
│   ├── 404.html
│   ├── site.css
│   └── favicon.svg
├── scripts/
│   ├── build_site.py        # génère le site statique
│   └── captures.py          # outil historique de captures d'écran
├── docs/                    # site publié + documentation d'archive
│   ├── index.html · 404.html · site.css · favicon.svg · .nojekyll
│   ├── ARCHIVAGE.md · GUIDE.md · TECHNIQUE.md
│   └── captures/            # 6 captures de la dernière version
└── .github/workflows/pages.yml
```

## 🔒 Sécurité & données personnelles

- `.env`, la base SQLite, les logs et les exports sont exclus de git
  (`.gitignore`) : **aucune fiche, aucun cours, aucune clé n'a jamais été
  publié** dans ce dépôt ni sur la page d'archive.
- La clé API était stockée dans le trousseau du système, masquée dans
  l'interface et jamais journalisée.
- Les documents originaux n'étaient pas dupliqués : la fiche gardait une
  référence (chemin) vers le fichier source.
- Les données vivaient dans `%APPDATA%\Memora` (Windows) ; la sauvegarde se
  faisait depuis *Paramètres → Données*.

## 🧪 Tests (historique)

```bash
python -m pytest tests/ -q
```

41 tests couvraient l'import PDF/DOCX/image, l'OCR, le client API (clé
invalide, quota, réseau, JSON invalide), la génération complète, la base
SQLite, les filtres/recherche, les exports et le démarrage de l'interface.
Ils nécessitent PySide6 et ne sont plus maintenus.

## 📄 Licence

Le dépôt n'a jamais reçu de licence. Le code est consultable, mais pas
librement réutilisable, modifiable ni redistribuable par défaut. L'archivage ne
permet plus d'en ajouter une : lisez-le comme une référence, pas comme une
bibliothèque à réemployer.

---

**Memora · 2026 — du premier commit à l'archive, sans rien effacer.**
