# Scraper d'Annonces d'Administrateurs Judiciaires

Système complet pour scraper et filtrer les annonces d'entreprises à céder publiées par les administrateurs judiciaires en Île-de-France, spécialisé dans les secteurs de l'informatique, data et conseil.

## 🎯 Objectif

Ce projet permet de :
1. **Extraire** la liste des administrateurs judiciaires en Île-de-France depuis l'annuaire officiel
2. **Analyser** leurs sites web pour identifier les pages contenant des annonces de vente
3. **Collecter** et **filtrer** automatiquement les annonces pertinentes selon :
   - **Secteur** : informatique, data, conseil, numérique, etc.
   - **Région** : Île-de-France (départements 75, 77, 78, 91, 92, 93, 94, 95)

## 📋 Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone <votre-repo>
cd test_claude/aj_scraper
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration (optionnelle)

Vous pouvez modifier les paramètres dans `config.py` :

```python
# Région cible
TARGET_REGION = "Île-de-France"
TARGET_DEPARTMENTS = ["75", "77", "78", "91", "92", "93", "94", "95"]

# Secteurs d'activité
TARGET_SECTORS = [
    "informatique",
    "data",
    "conseil",
    "numérique",
    # ... ajoutez vos secteurs
]

# Paramètres de scraping
DELAY_BETWEEN_REQUESTS = 1.0  # secondes
MAX_RETRIES = 3
```

## 💻 Utilisation

### Mode simple (pipeline complet)

```bash
python main.py
```

Cette commande exécute les 3 phases automatiquement :
1. Extraction des administrateurs judiciaires
2. Analyse des sites web
3. Extraction et filtrage des annonces

### Mode avec Selenium

Si le site bloque les requêtes HTTP classiques, utilisez Selenium :

```bash
python main.py --selenium
```

> ⚠️ **Note** : Selenium nécessite Chrome/Chromium installé sur votre système.

### Exécution phase par phase

```bash
# Phase 1 uniquement (extraction des administrateurs)
python main.py --phase 1

# Phase 2 uniquement (analyse des sites)
python main.py --phase 2

# Phase 3 uniquement (extraction des annonces)
python main.py --phase 3
```

### Reprendre depuis une phase

Pour éviter de re-scraper les données déjà collectées :

```bash
# Ignorer la phase 1, utiliser les données existantes
python main.py --skip-phase1

# Ignorer les phases 1 et 2
python main.py --skip-phase1 --skip-phase2
```

## 📂 Structure du projet

```
aj_scraper/
├── config.py                  # Configuration centrale
├── scraper_annuaire.py       # Phase 1: Scraping de l'annuaire
├── scraper_sites.py          # Phase 2: Analyse des sites
├── scraper_annonces.py       # Phase 3: Extraction des annonces
├── filters.py                # Filtrage par secteur et région
├── main.py                   # Script principal
├── requirements.txt          # Dépendances Python
├── README.md                 # Cette documentation
├── data/                     # Données temporaires
├── output/                   # Résultats (JSON, CSV)
└── logs/                     # Logs d'exécution
```

## 📊 Fichiers de sortie

Tous les résultats sont sauvegardés dans le dossier `output/` :

### 1. `administrateurs_idf.json`
Liste des administrateurs judiciaires en Île-de-France avec leurs coordonnées et sites web.

```json
{
  "region": "Île-de-France",
  "total": 125,
  "administrateurs": [
    {
      "nom": "Cabinet Example",
      "adresse": "75008 Paris",
      "site_web": "https://example.fr",
      "telephone": "01 23 45 67 89",
      "email": "contact@example.fr",
      "departement": "75"
    }
  ]
}
```

### 2. `sites_analysis.json`
Analyse des sites web et pages d'annonces détectées.

```json
[
  {
    "base_url": "https://example.fr",
    "accessible": true,
    "pages_annonces": [
      "https://example.fr/annonces",
      "https://example.fr/ventes"
    ],
    "structure_detected": {
      "has_table": true,
      "item_tag": "tr",
      "pagination": true
    }
  }
]
```

### 3. `annonces_brutes.json`
Toutes les annonces extraites avant filtrage.

### 4. `annonces_filtrees.json` et `annonces_filtrees.csv`
Annonces filtrées selon vos critères (secteur, région).

```json
{
  "total": 42,
  "extracted_at": "2025-11-24T10:00:00",
  "annonces": [
    {
      "titre": "Entreprise de développement web",
      "description": "Société spécialisée en développement web...",
      "secteur": "Informatique",
      "localisation": "75008 Paris",
      "prix": "150000",
      "date_publication": "01/11/2025",
      "reference": "AJ-2025-001",
      "url_details": "https://example.fr/annonce/001",
      "contact": "contact@example.fr"
    }
  ]
}
```

## 🔧 Architecture des modules

### 1. `scraper_annuaire.py` - Extraction de l'annuaire

```python
from scraper_annuaire import AnnuaireScraper

# Utilisation basique
scraper = AnnuaireScraper()
administrateurs = scraper.scrape_all_pages()
scraper.save_results()

# Avec Selenium
scraper = AnnuaireScraper(use_selenium=True)
administrateurs = scraper.scrape_all_pages()
```

**Fonctionnalités** :
- Scraping de l'annuaire https://www.cnajmj.fr/annuaire/
- Filtrage automatique par région (Île-de-France)
- Gestion de la pagination
- Support requests + Selenium
- Extraction : nom, adresse, site web, téléphone, email

### 2. `scraper_sites.py` - Analyse des sites

```python
from scraper_sites import SiteAnalyzer

analyzer = SiteAnalyzer()
results = analyzer.analyze_site("https://example-aj.fr")

# Résultat
{
  "accessible": True,
  "pages_annonces": ["https://example-aj.fr/annonces"],
  "structure_detected": {...}
}
```

**Fonctionnalités** :
- Détection automatique des pages d'annonces
- 3 stratégies de recherche :
  1. Analyse du menu de navigation
  2. Recherche par mots-clés dans le contenu
  3. Crawling intelligent du site
- Détection de la structure des pages (tables, listes, cartes)

### 3. `scraper_annonces.py` - Extraction des annonces

```python
from scraper_annonces import AnnonceScraper

scraper = AnnonceScraper()
annonces = scraper.extract_annonces_from_page(url)

# Sauvegarde
scraper.save_annonces(annonces)
scraper.export_to_csv(annonces)
```

**Fonctionnalités** :
- Extraction adaptative selon la structure détectée
- Parsing de tables, listes, cartes HTML
- Extraction : titre, description, prix, localisation, contact, dates
- Export JSON et CSV

### 4. `filters.py` - Filtrage intelligent

```python
from filters import AnnonceFilter

filtre = AnnonceFilter()

# Filtrage complet
filtered = filtre.apply_all_filters(
    annonces,
    filter_sector=True,        # Filtre par secteur
    filter_location=True,       # Filtre par région
    min_price=50000,           # Prix minimum
    max_price=500000,          # Prix maximum
    custom_keywords=["saas"],  # Mots-clés additionnels
    exclude_keywords=["restaurant"]  # Exclusions
)

# Statistiques
stats = filtre.get_statistics(filtered)
```

**Fonctionnalités** :
- Filtrage par secteur d'activité (avec mots-clés étendus)
- Filtrage par localisation (codes postaux + noms)
- Filtrage par prix
- Filtrage par mots-clés personnalisés
- Statistiques détaillées

## 🎨 Exemples d'utilisation

### Exemple 1 : Recherche ciblée

```python
from main import AJScraperPipeline
from filters import AnnonceFilter

# Exécute le pipeline
pipeline = AJScraperPipeline()
pipeline.run()

# Filtre supplémentaire pour des mots-clés spécifiques
filtre = AnnonceFilter()
annonces_saas = filtre.filter_by_keywords(
    pipeline.filtered_annonces,
    keywords=["saas", "cloud", "api"]
)

print(f"Annonces SaaS trouvées: {len(annonces_saas)}")
```

### Exemple 2 : Analyse d'un seul site

```python
from scraper_sites import SiteAnalyzer
from scraper_annonces import AnnonceScraper

# Analyse
analyzer = SiteAnalyzer()
result = analyzer.analyze_site("https://example-aj.fr")

# Extraction si des annonces sont trouvées
if result['pages_annonces']:
    scraper = AnnonceScraper()
    annonces = scraper.extract_annonces_from_multiple_pages(
        result['pages_annonces']
    )
    print(f"Trouvé {len(annonces)} annonces")
```

### Exemple 3 : Scraping périodique

```bash
# Script cron pour exécuter chaque jour
0 9 * * * cd /path/to/aj_scraper && python main.py --skip-phase1 --skip-phase2
```

Ce script ré-extrait uniquement les nouvelles annonces chaque jour.

## ⚠️ Limitations et adaptations nécessaires

### 1. Structure du site de l'annuaire

Le module `scraper_annuaire.py` contient des **heuristiques génériques**. Vous devrez probablement adapter les méthodes suivantes après avoir inspecté le HTML réel du site :

```python
# Dans scraper_annuaire.py, ligne 142
def parse_annuaire_page(self, html: str) -> List[Dict]:
    # À ADAPTER selon la structure réelle du site
    entries = soup.find_all('div', class_=['entry', 'result', ...])
```

### 2. Protection anti-scraping

Si vous rencontrez des erreurs 403 ou des blocages :
- Utilisez l'option `--selenium`
- Installez Chrome/Chromium : `apt-get install chromium-browser chromium-driver`
- Augmentez les délais dans `config.py`
- Utilisez des proxies ou un service comme ScraperAPI

### 3. Structure des pages d'annonces

Les sites d'administrateurs judiciaires ont tous des structures différentes. Le système utilise des heuristiques pour s'adapter, mais vous pourriez devoir :
- Inspecter manuellement quelques sites
- Adapter les sélecteurs CSS dans `scraper_annonces.py`

## 🐛 Dépannage

### Erreur 403 Forbidden

```bash
# Solution 1: Utiliser Selenium
python main.py --selenium

# Solution 2: Augmenter le délai
# Dans config.py: DELAY_BETWEEN_REQUESTS = 2.0
```

### ChromeDriver introuvable

```bash
# Linux (Debian/Ubuntu)
sudo apt-get install chromium-browser chromium-driver

# macOS
brew install --cask chromedriver

# Windows
# Téléchargez depuis https://chromedriver.chromium.org/
```

### Aucune annonce trouvée

1. Vérifiez que les sites sont accessibles
2. Inspectez `output/sites_analysis.json` pour voir les pages détectées
3. Testez manuellement un site :

```python
from scraper_sites import SiteAnalyzer
analyzer = SiteAnalyzer()
result = analyzer.analyze_site("https://example-aj.fr")
print(result)
```

## 📝 Logs et debugging

Les logs détaillés sont affichés en temps réel. Pour sauvegarder dans un fichier :

```bash
python main.py 2>&1 | tee output.log
```

Pour plus de détails, modifiez le niveau de log dans chaque module :

```python
logging.basicConfig(level=logging.DEBUG)  # Au lieu de INFO
```

## 🔐 Considérations légales

⚠️ **Important** :
- Respectez les conditions d'utilisation des sites scrapés
- Respectez les délais entre requêtes (configurés par défaut)
- Les données extraites sont publiques mais vérifiez leur utilisation autorisée
- Certains sites peuvent interdire le scraping automatique dans leurs CGU

## 🤝 Contribution

Pour améliorer ce projet :
1. Testez avec différents sites d'administrateurs judiciaires
2. Signalez les bugs et structures non supportées
3. Proposez des améliorations pour la détection automatique

## 📄 Licence

Ce projet est fourni tel quel, pour usage éducatif et professionnel.

## 🆘 Support

En cas de problème :
1. Vérifiez la section Dépannage
2. Consultez les logs détaillés
3. Testez chaque module indépendamment
4. Inspectez les fichiers HTML sauvegardés

## 🗺️ Roadmap

Améliorations futures possibles :
- [ ] Support d'autres régions
- [ ] Interface web pour visualiser les résultats
- [ ] Notifications par email des nouvelles annonces
- [ ] Base de données pour historiser les annonces
- [ ] API REST pour interroger les données
- [ ] Dashboard avec statistiques en temps réel

---

**Bon scraping ! 🚀**
