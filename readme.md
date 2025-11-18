# Quadratic Labs Web Scraper

Programme Python pour scraper le site web quadratic-labs.com et retourner la liste des pages trouvées.

## Fonctionnalités

- ✅ Scraping automatique du site quadratic-labs.com
- ✅ Récupération de toutes les pages accessibles
- ✅ Export des résultats en JSON et TXT
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
3. Sauvegarder les résultats dans deux fichiers :
   - `quadratic_labs_pages.json` (format JSON structuré)
   - `quadratic_labs_pages.txt` (liste simple d'URLs)

### Utilisation avancée (en tant que module)

```python
from scraper import QuadraticLabsScraper

# Créer une instance du scraper
scraper = QuadraticLabsScraper()

# Lancer le scraping (max 100 pages, délai de 0.5s entre requêtes)
pages = scraper.scrape(max_pages=100, delay=0.5)

# Afficher les résultats
print(f"Pages trouvées: {len(pages)}")
for page in pages:
    print(page)

# Sauvegarder les résultats
scraper.save_to_json("my_results.json")
scraper.save_to_txt("my_results.txt")
```

## Configuration

Vous pouvez modifier les paramètres dans le fichier [scraper.py](scraper.py) :

- `max_pages` : Nombre maximum de pages à scraper (défaut: 100)
- `delay` : Délai en secondes entre chaque requête (défaut: 0.5)
- `base_url` : URL de base à scraper (défaut: "https://quadratic-labs.com")

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

## Fonctionnement

Le scraper utilise une approche de parcours en largeur (BFS) :

1. Commence par l'URL de base
2. Extrait tous les liens de la page
3. Filtre les liens pour ne garder que ceux du même domaine
4. Visite récursivement chaque nouveau lien trouvé
5. S'arrête après avoir visité le nombre maximum de pages

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

## Licence

Ce projet est fourni tel quel, pour usage éducatif et professionnel.

## Issue GitHub

Ce projet répond à l'issue #1 : [Créer un programme Python pour scraper quadratic-labs.com](https://github.com/xavier-quadratic/test_claude/issues/1)
