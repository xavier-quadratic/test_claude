"""
Configuration pour le scraper d'administrateurs judiciaires
"""

import os

# Répertoires
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# URLs
ANNUAIRE_URL = "https://www.cnajmj.fr/annuaire/"

# Paramètres de scraping
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
REQUEST_TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 1.0  # secondes
MAX_RETRIES = 3

# Filtres
TARGET_REGION = "Île-de-France"
TARGET_DEPARTMENTS = ["75", "77", "78", "91", "92", "93", "94", "95"]  # Départements IDF

TARGET_SECTORS = [
    "informatique",
    "data",
    "conseil",
    "numérique",
    "digital",
    "technologie",
    "software",
    "saas",
    "intelligence artificielle",
    "ia",
    "machine learning",
    "développement",
    "web",
    "cloud",
    "cybersécurité",
    "analyse",
    "consulting"
]

# Mots-clés pour identifier les pages d'annonces
ANNONCE_KEYWORDS = [
    "vente",
    "cession",
    "liquidation",
    "annonce",
    "offre",
    "entreprise à céder",
    "fonds de commerce",
    "actif",
    "enchère"
]

# Headers HTTP
DEFAULT_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Options Selenium (si nécessaire)
SELENIUM_OPTIONS = [
    '--headless',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-blink-features=AutomationControlled',
    f'user-agent={USER_AGENT}'
]
