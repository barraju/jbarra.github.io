# Site personnel — mode d'emploi

Site statique (Jekyll) hébergé par GitHub Pages. Aucun outil à installer :
GitHub construit le site à chaque `git push`.

## Mettre à jour le site (usage courant)

1. Éditer le fichier concerné (tableau ci-dessous) — directement sur
   github.com (bouton ✏️) ou en local.
2. Enregistrer, puis :
   ```bash
   git add .
   git commit -m "Ajout d'une publication"
   git push
   ```
3. Le site est reconstruit automatiquement en 1 à 2 minutes.

| Je veux…                    | J'édite…                         |
|-----------------------------|----------------------------------|
| Ajouter une publication     | `_data/publications.yml`         |
| Ajouter une actualité       | `_data/news.yml`                 |
| Ajouter / modifier un cours | `_data/teaching.yml`             |
| Ajouter un projet           | `_data/projects.yml`             |
| Changer la photo            | remplacer `assets/img/photo.jpg` |
| Mettre à jour le CV PDF     | remplacer `assets/cv.pdf`        |
| Modifier un texte de page   | le fichier `.md` correspondant   |
| Ajouter une rubrique        | créer `ma-page.md` avec `nav: true` et un `order` (position dans le menu) |

Astuce : dans `_data/publications.yml`, écrivez votre nom exactement comme
`author` dans `_config.yml` : il sera mis en gras automatiquement.

## Aperçu local (optionnel)

Nécessite Ruby, puis :

```bash
bundle install
bundle exec jekyll serve   # → http://localhost:4000
```

## En cas de problème

- **Le site ne se met pas à jour** : attendre 2 min puis vider le cache
  du navigateur (Ctrl + F5).
- **Erreur de build** : voir l'onglet *Actions* du dépôt (ou le mail de
  GitHub) ; dans la grande majorité des cas, c'est une indentation YAML
  (2 espaces, jamais de tabulation).
- **URL du site** : elle dépend de l'identifiant GitHub ; le dépôt doit
  s'appeler `<identifiant>.github.io`.
