# Scraper d'Annonces d'Administrateurs Judiciaires

Système automatisé de scraping et filtrage des annonces d'entreprises à céder publiées par les administrateurs judiciaires en Île-de-France.

## 🎯 Objectif

Ce projet permet de :
1. **Extraire** la liste des administrateurs judiciaires en Île-de-France depuis l'annuaire officiel
2. **Analyser** leurs sites web pour identifier les pages contenant des annonces de vente
3. **Collecter** et **filtrer** automatiquement les annonces pertinentes selon :
   - **Secteur** : informatique, data, conseil, numérique, etc.
   - **Région** : Île-de-France (départements 75, 77, 78, 91, 92, 93, 94, 95)

## 🚀 Démarrage rapide

```bash
# Installation
cd aj_scraper
pip install -r requirements.txt

# Lancement
python main.py

# Si le site bloque (erreur 403)
python main.py --selenium
```

## 📂 Structure du projet

```
test_claude/
├── aj_scraper/              # Système de scraping (code principal)
│   ├── main.py             # Script principal
│   ├── scraper_annuaire.py # Phase 1: Extraction des administrateurs
│   ├── scraper_sites.py    # Phase 2: Analyse des sites web
│   ├── scraper_annonces.py # Phase 3: Extraction des annonces
│   ├── filters.py          # Filtrage intelligent
│   ├── config.py           # Configuration
│   ├── examples.py         # Exemples d'utilisation
│   ├── README.md           # Documentation détaillée
│   ├── QUICKSTART.md       # Guide de démarrage rapide
│   └── output/             # Résultats (JSON, CSV)
└── PROJECT_SUMMARY.md      # Vue d'ensemble du projet

```

## 📊 Résultats

Les annonces filtrées sont exportées dans `aj_scraper/output/` :
- **annonces_filtrees.json** : Format JSON structuré
- **annonces_filtrees.csv** : Format Excel/Sheets
- **administrateurs_idf.json** : Liste des administrateurs en IDF
- **sites_analysis.json** : Analyse des sites web

## 📖 Documentation complète

Pour plus de détails, consultez :
- **[aj_scraper/README.md](aj_scraper/README.md)** : Documentation complète du système
- **[aj_scraper/QUICKSTART.md](aj_scraper/QUICKSTART.md)** : Guide de démarrage rapide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** : Vue d'ensemble du projet
- **[aj_scraper/examples.py](aj_scraper/examples.py)** : Exemples d'utilisation

## ⚙️ Fonctionnalités

✅ Scraping automatique de l'annuaire des administrateurs judiciaires
✅ Détection intelligente des pages d'annonces sur chaque site
✅ Extraction adaptative selon la structure HTML
✅ Filtrage multi-critères (secteur, région, prix)
✅ Export JSON et CSV
✅ Gestion robuste des erreurs et retry automatique
✅ Support Selenium pour contourner les protections anti-scraping
✅ Configuration centralisée et personnalisable
✅ Documentation complète et exemples testés

## 🔧 Configuration

Personnalisez les paramètres dans `aj_scraper/config.py` :
```python
# Région et départements cibles
TARGET_REGION = "Île-de-France"
TARGET_DEPARTMENTS = ["75", "77", "78", "91", "92", "93", "94", "95"]

# Secteurs d'activité recherchés
TARGET_SECTORS = [
    "informatique",
    "data",
    "conseil",
    "numérique",
    "digital",
    # ... ajoutez vos secteurs
]

# Paramètres de scraping
DELAY_BETWEEN_REQUESTS = 1.0  # secondes
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
```

## 💡 Exemples d'utilisation

### Pipeline complet
```bash
python aj_scraper/main.py
```

### Exécution par phase
```bash
# Phase 1 seulement (extraction des administrateurs)
python aj_scraper/main.py --phase 1

# Phases 1 et 2 (+ analyse des sites)
python aj_scraper/main.py --phase 2

# Phase 3 seulement (extraction des annonces)
python aj_scraper/main.py --skip-phase1 --skip-phase2
```

### Avec Selenium
```bash
# Si le site bloque les requêtes HTTP
python aj_scraper/main.py --selenium
```

### Tests et exemples
```bash
# Lancer les exemples de démonstration
python aj_scraper/examples.py
```

## 🐛 Dépannage

### Erreur 403 Forbidden
Le site de l'annuaire bloque les requêtes automatiques. Solutions :
```bash
# Solution 1: Utiliser Selenium
python aj_scraper/main.py --selenium

# Solution 2: Créer une liste manuelle (voir QUICKSTART.md)
python aj_scraper/main.py --skip-phase1
```

### Module non trouvé
```bash
cd aj_scraper
pip install -r requirements.txt
```

### ChromeDriver introuvable
```bash
# Linux (Debian/Ubuntu)
sudo apt-get install chromium-browser chromium-driver

# macOS
brew install --cask chromedriver
```

## 📝 Architecture

Le système est organisé en 3 phases :

### Phase 1 : Extraction de l'annuaire
- Module : `scraper_annuaire.py`
- Source : https://www.cnajmj.fr/annuaire/
- Résultat : Liste des administrateurs en Île-de-France avec leurs sites web

### Phase 2 : Analyse des sites
- Module : `scraper_sites.py`
- Détection automatique des pages contenant des annonces
- 3 stratégies : navigation, mots-clés, crawling

### Phase 3 : Extraction et filtrage
- Modules : `scraper_annonces.py` + `filters.py`
- Extraction des annonces depuis les pages identifiées
- Filtrage intelligent par secteur et région

## 🔐 Considérations légales

⚠️ **Important** :
- Les données d'annuaires et annonces sont publiques
- Respectez les délais entre requêtes (configurés par défaut)
- Vérifiez les conditions d'utilisation de chaque site
- Usage recommandé : recherche légitime d'opportunités business

## 🤝 Contribution

Pour améliorer ce projet :
1. Testez avec différents sites d'administrateurs judiciaires
2. Signalez les bugs et structures HTML non supportées
3. Proposez des améliorations pour la détection automatique

## 📄 Licence

Ce projet est fourni tel quel, pour usage éducatif et professionnel.

---

**Pour commencer, consultez [aj_scraper/QUICKSTART.md](aj_scraper/QUICKSTART.md)** 🚀
