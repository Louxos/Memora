# Dossier d'archivage — Memora

**Date d'archivage : 6 novembre 2026.**
**Dernière version : 1.0.0 (version finale).**
**Page d'archive : <https://louxos.github.io/Memora/>.**

Ce document est le procès-verbal de la mise en archive. Il décrit ce qui a
été fait, ce qui n'a volontairement pas été fait, et les dernières actions
laissées à la main.

---

## 1. La décision

Memora était un logiciel personnel de révision : un cours (PDF, Word, texte ou
photo) entrait, une fiche de révision structurée en sortait, rangée dans une
bibliothèque SQLite locale. Construit pour préparer le brevet, il reposait sur
une interface PySide6, plusieurs extracteurs de documents et l'API Mistral.

Le développement s'arrête pour trois raisons, dans l'ordre de ce qui a pesé :

1. **Une maintenance disproportionnée** pour un seul développeur : interface
   Qt, extraction PDF/DOCX, OCR, base SQLite, exports et 41 tests à revérifier
   à chaque évolution, sur Windows uniquement.
2. **Des dépendances mouvantes** : modèles et tarifs de l'API Mistral, service
   OCR, PySide6, PyMuPDF. Figer une version sans la suivre finirait par
   promettre ce qu'elle ne tient plus.
3. **Un objectif atteint** : le besoin pour lequel Memora a été écrit est
   couvert par la version livrée et, ailleurs, par des outils maintenus par des
   équipes.

L'archivage est une décision, pas un incident : **rien n'a été supprimé** — ni
code, ni commits, ni captures, ni cahier des charges, ni tests. Aucune donnée
personnelle n'était de toute façon présente dans le dépôt (base SQLite, `.env`,
logs et exports exclus par `.gitignore`).

## 2. Ce qui a été fait pour cette archive

| Élément | Contenu |
|---|---|
| **Page d'archive** | Les trois fichiers fournis (`index.html`, `404.html`, `site.css`) repris tels quels dans `site/`, adaptés à Memora : textes, charte indigo/violet, faits, raisons, liens, et suppression des éléments propres à une application web (routes `#`, liens d'appairage, relais de transfert) qui n'existaient pas dans ce projet. |
| **Site statique prêt à publier** | `scripts/build_site.py` résout les marqueurs `{{…}}`, inline le CSS, intègre le logo `favicon.svg` et écrit `docs/` (avec `.nojekyll`). Aucune ressource distante, aucune dépendance. |
| **Nouveau relais de publication** | `.github/workflows/pages.yml` reconstruit et vérifie `docs/` à chaque modification, puis tente un déploiement Pages depuis `main` (`configure-pages` → `upload-pages-artifact` → `deploy-pages`). L'activation automatique de Pages peut être refusée par les permissions du dépôt : elle est alors ignorée sans faire échouer le workflow, et la publication classique par branche (`main` → `/docs`) reste disponible. Le déploiement est de toute façon limité à la branche par défaut à cause des règles de protection de l'environnement `github-pages`. |
| **Nouvelle release finale** | `v1.0.0` — « Memora 1.0.0 — version d'archive », dernière version publiée. Elle fige le code tel qu'il a été laissé et sert de point d'entrée « dernière version » depuis la page. |
| **Documentation adaptée** | `README.md` réécrit au passé avec l'état archivé ; `docs/GUIDE.md` (guide de la dernière version), `docs/TECHNIQUE.md` (architecture, sécurité, limites), `docs/ARCHIVAGE.md` (ce document). |
| **Tous les fichiers d'entrée** | `main.py`, `memora/__init__.py`, `install.bat`, `run.bat`, `requirements.txt`, `.env.example` et `prompt` portent désormais une mention d'archive. Le comportement du code n'a **pas** été modifié. |

## 3. Ce qui n'a pas été fait

- Aucune correction, aucune migration de dépendances, aucune suppression de
  fichier de l'application.
- **Le dépôt GitHub n'a pas été passé en lecture seule technique** via
  l'option « Archive this repository ». Le faire trop tôt aurait empêché la
  publication de la release, le workflow Pages et la fusion de la branche de
  travail. L'archive est donc réelle dans le contenu et la page ; le verrou
  officiel est l'ultime étape manuelle ci-dessous.
- Aucune licence ajoutée (le dépôt n'en a jamais eu).
- Aucune donnée utilisateur publiée : Memora ne stockait rien ailleurs que sur
  l'ordinateur.

## 4. Dernières étapes (à la main, une fois seulement)

1. **Fusionner** la pull request de la branche `arena/7081a176-memora` dans
   `main` : le workflow se déclenche alors et publie la page.
2. **Activer GitHub Pages** — c'est la seule étape qui ne peut pas être faite
   depuis l'agent : l'API Pages répond *« Resource not accessible by
   integration »* au token fourni (permission `pages:write` absente), et
   `actions/configure-pages` ne peut activer un site qu'avec un token
   d'administration dédié. Deux possibilités, une seule manipulation dans les
   deux cas :
   - **Recommandé** : *Settings → Pages → Build and deployment →
     **Deploy from a branch → `main` → `/docs`*** → *Save*. `docs/` est déjà
     versionné, aucun outil ni compilation requis.
   - **Avec le workflow** : *Source : **GitHub Actions***, puis relancer
     *GitHub Pages — archive Memora* depuis l'onglet Actions. Le déploiement
     `deploy-pages` prend alors le relais. Tant que Pages n'est pas activé, le
     workflow émet un avertissement et reste vert.
3. **Vérifier** <https://louxos.github.io/Memora/> et sa page 404
   (par exemple `/Memora/inexistant`).
4. **Optionnel : verrou officiel** — *Settings → General → Archive this
   repository*. Le dépôt devient alors réellement en lecture seule (issues et
   PR fermées, code et releases toujours consultables). À faire **après** la
   publication, car un dépôt archivé ne déclenche plus de workflow.

## 5. Reconstruire la page

```bash
python3 scripts/build_site.py                  # écrit docs/
python3 scripts/build_site.py --sortie _site   # ou ailleurs
python3 -m http.server 8000 --directory docs   # aperçu local
```

Toutes les valeurs éditoriales (date d'archivage, numéro de version, URL du
dépôt, URL du site, URL de la release) sont regroupées en haut de
`scripts/build_site.py`. Les modèles `site/*.html` ne contiennent que des
marqueurs : modifier une valeur ne demande pas de retoucher les fichiers
fournis.

## 6. Notes de la version 1.0.0 — version d'archive

- **État** : version finale, publiée le 6 novembre 2026. Aucune version ne
  suivra.
- **Contenu** : application PySide6 complète (import PDF/DOCX/TXT/images,
  OCR Mistral, génération de fiches par Mistral, bibliothèque SQLite, 4 modes,
  statuts, favoris, édition, exports PDF/Markdown/JSON, thèmes clair/sombre,
  mode démonstration), 41 tests pytest, captures d'écran et cahier des charges.
- **Lancement** : Windows, `install.bat` puis `run.bat` ; clé API Mistral à
  renseigner dans les paramètres ou via `.env`. Voir `docs/GUIDE.md`.
- **Avertissement** : logiciel non maintenu. Les services externes (API
  Mistral, modèles, OCR) et les bibliothèques tierces peuvent avoir changé ;
  aucun correctif ne sera apporté.
- **Licence** : aucune. Code consultable à titre de référence uniquement.

---

*Memora · 2026 — du premier commit à l'archive, sans rien effacer.*
