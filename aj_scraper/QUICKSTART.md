# Guide de Démarrage Rapide

## Installation en 3 étapes

```bash
# 1. Aller dans le dossier
cd aj_scraper

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer le scraping
python main.py
```

## Premier test

Si le site bloque vos requêtes (erreur 403), essayez avec Selenium :

```bash
# Installer Chrome/Chromium d'abord
sudo apt-get install chromium-browser chromium-driver  # Linux
brew install --cask chromedriver  # macOS

# Puis lancer avec Selenium
python main.py --selenium
```

## Résultats

Les résultats sont dans le dossier `output/` :
- `annonces_filtrees.csv` : À ouvrir dans Excel/Google Sheets
- `annonces_filtrees.json` : Format structuré pour analyse

## Personnalisation

Éditez `config.py` pour modifier :
- Les secteurs ciblés (ligne 24)
- Les départements (ligne 20)
- Les mots-clés de recherche (ligne 48)

## Test rapide d'un module

```python
# Test du filtre
python filters.py

# Test de l'analyse de sites
python scraper_sites.py

# Test de l'extraction d'annonces
python scraper_annonces.py
```

## Problèmes courants

### "ModuleNotFoundError: No module named 'cloudscraper'"
```bash
pip install -r requirements.txt
```

### "Aucun administrateur trouvé"
Le site https://www.cnajmj.fr/annuaire/ a des protections anti-scraping.
Solutions :
1. Utilisez `--selenium`
2. Inspectez manuellement le site et adaptez le code dans `scraper_annuaire.py`
3. Créez un fichier `output/administrateurs_idf.json` manuellement avec quelques URLs de test

### Exemple de fichier manuel pour tester

Créez `output/administrateurs_idf.json` :

```json
{
  "region": "Île-de-France",
  "total": 3,
  "administrateurs": [
    {
      "nom": "Test AJ 1",
      "site_web": "https://example1-aj.fr",
      "adresse": "75008 Paris",
      "departement": "75"
    },
    {
      "nom": "Test AJ 2",
      "site_web": "https://example2-aj.fr",
      "adresse": "92100 Boulogne",
      "departement": "92"
    }
  ]
}
```

Puis lancez :
```bash
python main.py --skip-phase1
```

## Workflow recommandé

1. **Première fois** : Comprendre la structure du site de l'annuaire
   ```bash
   # Visitez https://www.cnajmj.fr/annuaire/ dans votre navigateur
   # Inspectez le HTML (F12) pour voir la structure
   # Adaptez scraper_annuaire.py si nécessaire
   ```

2. **Test avec quelques sites** : Créer manuellement la liste des AJ
   ```bash
   # Créez output/administrateurs_idf.json avec 2-3 sites
   python main.py --skip-phase1
   ```

3. **Affinage** : Tester et améliorer les filtres
   ```bash
   # Éditez config.py pour ajuster les secteurs/mots-clés
   python main.py --skip-phase1 --skip-phase2
   ```

4. **Production** : Automatiser complètement
   ```bash
   python main.py
   ```

## Exécution périodique (quotidienne)

```bash
# Ajouter au crontab (Linux/macOS)
crontab -e

# Ajouter cette ligne pour exécuter tous les jours à 9h
0 9 * * * cd /path/to/aj_scraper && /usr/bin/python3 main.py --skip-phase1 >> logs/cron.log 2>&1
```

## Prochaines étapes

Une fois que vous avez des résultats :
1. Analysez les annonces dans `output/annonces_filtrees.csv`
2. Ajustez les filtres dans `config.py` si nécessaire
3. Contactez les administrateurs judiciaires pour les annonces intéressantes

---

Pour plus de détails, consultez [README.md](README.md)
