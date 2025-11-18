# Quadratic Labs Web Scraper

Programme Python pour scraper le site web quadratic-labs.com et retourner la liste des pages trouvées.

## Fonctionnalités

- ✅ Scraping automatique du site quadratic-labs.com
- ✅ Récupération de toutes les pages accessibles
- ✅ Export des résultats en JSON et TXT
- ✅ **Visualisation de l'arborescence du site**
- ✅ **Arborescence colorisée par profondeur** (nouveau !)
- ✅ **Export de la structure hiérarchique**
- ✅ **Statistiques par profondeur**
- ✅ Gestion des erreurs de connexion
- ✅ Respect des bonnes pratiques (délai entre requêtes)
- ✅ Logging détaillé du processus

## Installation

### Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

### Utilisation basique

```bash
python scraper.py
```

Cette commande va :
1. Scraper le site quadratic-labs.com
2. Afficher la liste des pages trouvées dans le terminal
3. **Afficher l'arborescence hiérarchique du site**
4. **Afficher des statistiques (profondeur max, répartition par niveau)**
5. Sauvegarder les résultats dans trois fichiers :
   - `quadratic_labs_pages.json` (liste simple des URLs)
   - `quadratic_labs_pages.txt` (liste texte des URLs)
   - `quadratic_labs_tree.json` (arborescence hiérarchique)

### Utilisation avancée (en tant que module)

```python
from scraper import QuadraticLabsScraper

# Créer une instance du scraper (avec couleurs activées par défaut)
scraper = QuadraticLabsScraper()

# Ou désactiver les couleurs
# scraper = QuadraticLabsScraper(use_colors=False)

# Lancer le scraping (max 100 pages, délai de 0.5s entre requêtes)
pages = scraper.scrape(max_pages=100, delay=0.5)

# Afficher les résultats
print(f"Pages trouvées: {len(pages)}")
for page in pages:
    print(page)

# Sauvegarder les résultats
scraper.save_to_json("my_results.json")
scraper.save_to_txt("my_results.txt")

# Afficher l'arborescence dans le terminal (avec couleurs)
scraper.print_tree()

# Sauvegarder l'arborescence en JSON
scraper.save_tree_to_json("my_tree.json")

# Obtenir des statistiques
stats = scraper.get_tree_stats()
print(f"Profondeur maximale: {stats['max_depth']}")
print(f"Pages par niveau: {stats['pages_by_depth']}")
```

## Configuration

Vous pouvez configurer le scraper avec ces paramètres :

### Paramètres du constructeur
- `base_url` : URL de base à scraper (défaut: "https://quadratic-labs.com")
- `use_colors` : Active/désactive la colorisation de l'arborescence (défaut: True)

### Paramètres de scraping
- `max_pages` : Nombre maximum de pages à scraper (défaut: 100)
- `delay` : Délai en secondes entre chaque requête (défaut: 0.5)

### Palette de couleurs
- **Niveau 0 (racine)** : Cyan brillant
- **Niveau 1** : Vert
- **Niveau 2** : Jaune
- **Niveau 3** : Magenta
- **Niveau 4+** : Rouge
- **Connecteurs** : Gris dim
- **Info profondeur** : Gris dim

## Format de sortie

### Fichier JSON (`quadratic_labs_pages.json`)

```json
{
  "base_url": "https://quadratic-labs.com",
  "total_pages": 42,
  "pages": [
    "https://quadratic-labs.com",
    "https://quadratic-labs.com/about",
    "https://quadratic-labs.com/contact",
    ...
  ]
}
```

### Fichier TXT (`quadratic_labs_pages.txt`)

```
https://quadratic-labs.com
https://quadratic-labs.com/about
https://quadratic-labs.com/contact
...
```

### Arborescence hiérarchique (`quadratic_labs_tree.json`)

```json
{
  "url": "https://quadratic-labs.com",
  "depth": 0,
  "children": [
    {
      "url": "https://quadratic-labs.com/join-us",
      "depth": 1,
      "children": []
    },
    {
      "url": "https://quadratic-labs.com/mentions-legales",
      "depth": 1,
      "children": []
    }
  ]
}
```

### Affichage de l'arborescence dans le terminal

```
https://quadratic-labs.com (racine)
+-- /join-us [profondeur: 1]
|   +-- /?subject=Recrutement [profondeur: 2]
+-- /mentions-legales [profondeur: 1]
+-- /politique-de-confidentialite [profondeur: 1]
|   +-- /modele-pionnier-dao [profondeur: 2]
+-- /quadratic-labs-web3-ai [profondeur: 1]
+-- /quadratic-room [profondeur: 1]
```

## Fonctionnement

Le scraper utilise une approche de parcours en largeur (BFS) :

1. Commence par l'URL de base (profondeur 0)
2. Extrait tous les liens de la page
3. Filtre les liens pour ne garder que ceux du même domaine
4. Track la relation parent-enfant pour chaque lien découvert
5. Visite chaque nouveau lien trouvé niveau par niveau
6. Enregistre la profondeur de chaque page
7. S'arrête après avoir visité le nombre maximum de pages

Cette approche permet de construire une arborescence complète du site en préservant les relations hiérarchiques entre les pages.

## Gestion des erreurs

Le scraper gère automatiquement :
- ❌ Erreurs de connexion (timeout, DNS, etc.)
- ❌ Erreurs HTTP (404, 500, etc.)
- ❌ Pages invalides ou inaccessibles

Les erreurs sont loggées mais n'interrompent pas le processus de scraping.

## Bonnes pratiques

- ⏱️ Délai entre les requêtes pour ne pas surcharger le serveur
- 🔍 User-Agent configuré pour identifier le scraper
- 📝 Normalisation des URLs pour éviter les doublons
- 🔒 Filtrage par domaine pour rester sur le site cible

## Dépendances

- `requests` : Pour les requêtes HTTP
- `beautifulsoup4` : Pour le parsing HTML
- `lxml` : Parser rapide pour BeautifulSoup
- `colorama` : Support multi-plateforme des couleurs ANSI (Windows, Linux, macOS)

## Licence

Ce projet est fourni tel quel, pour usage éducatif et professionnel.

## Issues GitHub

Ce projet répond aux issues suivantes :
- Issue #1 : [Créer un programme Python pour scraper quadratic-labs.com](https://github.com/xavier-quadratic/test_claude/issues/1)
- Issue #3 : [Ajouter la visualisation de l'arborescence du site](https://github.com/xavier-quadratic/test_claude/issues/3)
- Issue #5 : [Ajouter de la couleur à l'affichage de l'arborescence](https://github.com/xavier-quadratic/test_claude/issues/5)
