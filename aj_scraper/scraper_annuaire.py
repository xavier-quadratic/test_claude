"""
Module pour scraper l'annuaire des administrateurs judiciaires
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

from config import (
    ANNUAIRE_URL, DEFAULT_HEADERS, TARGET_REGION, TARGET_DEPARTMENTS,
    REQUEST_TIMEOUT, DELAY_BETWEEN_REQUESTS, MAX_RETRIES
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnnuaireScraper:
    """
    Scraper pour l'annuaire des administrateurs judiciaires

    Ce scraper extrait la liste des administrateurs judiciaires en Île-de-France
    avec leurs coordonnées et sites web.
    """

    def __init__(self, use_selenium: bool = False):
        """
        Initialise le scraper

        Args:
            use_selenium: Si True, utilise Selenium au lieu de requests
        """
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.administrateurs = []

    def _get_page_with_requests(self, url: str) -> Optional[str]:
        """Récupère une page avec requests"""
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Tentative {attempt + 1}/{MAX_RETRIES} pour {url}")
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la récupération de {url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(DELAY_BETWEEN_REQUESTS * (attempt + 1))
                continue

        return None

    def _get_page_with_selenium(self, url: str) -> Optional[str]:
        """Récupère une page avec Selenium"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from config import SELENIUM_OPTIONS

            options = Options()
            for option in SELENIUM_OPTIONS:
                options.add_argument(option)

            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(3)  # Attend le chargement JavaScript

            page_source = driver.page_source
            driver.quit()

            return page_source

        except Exception as e:
            logger.error(f"Erreur Selenium pour {url}: {e}")
            return None

    def get_page(self, url: str) -> Optional[str]:
        """
        Récupère le contenu d'une page

        Args:
            url: URL à récupérer

        Returns:
            Contenu HTML ou None en cas d'échec
        """
        if self.use_selenium:
            return self._get_page_with_selenium(url)
        else:
            return self._get_page_with_requests(url)

    def parse_annuaire_page(self, html: str) -> List[Dict]:
        """
        Parse une page de l'annuaire pour extraire les administrateurs

        Args:
            html: Contenu HTML de la page

        Returns:
            Liste des administrateurs trouvés

        Note:
            Cette méthode doit être adaptée selon la structure réelle du site.
            Actuellement, elle contient un exemple générique.
        """
        soup = BeautifulSoup(html, 'html.parser')
        administrateurs = []

        # ATTENTION: Cette partie doit être adaptée selon la structure réelle du site
        # Voici plusieurs possibilités courantes :

        # Possibilité 1: Liste dans des <div class="entry"> ou similaire
        entries = soup.find_all('div', class_=['entry', 'result', 'item', 'card'])

        # Possibilité 2: Table avec des lignes <tr>
        if not entries:
            entries = soup.find_all('tr')[1:]  # Ignore l'en-tête

        # Possibilité 3: Liste <li>
        if not entries:
            entries = soup.find_all('li', class_=['entry', 'result', 'item'])

        logger.info(f"Trouvé {len(entries)} entrées potentielles")

        for entry in entries:
            try:
                admin_data = self._extract_admin_data(entry)
                if admin_data and self._is_in_target_region(admin_data):
                    administrateurs.append(admin_data)
                    logger.info(f"Administrateur trouvé: {admin_data.get('nom', 'N/A')}")
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction d'une entrée: {e}")
                continue

        return administrateurs

    def _extract_admin_data(self, entry) -> Optional[Dict]:
        """
        Extrait les données d'un administrateur depuis un élément HTML

        Args:
            entry: Élément BeautifulSoup contenant les données

        Returns:
            Dictionnaire avec les données ou None

        Note:
            Cette méthode doit être adaptée selon la structure réelle du site.
        """
        try:
            # Exemple générique - À ADAPTER selon la structure réelle
            data = {}

            # Nom (plusieurs possibilités)
            nom = entry.find(['h2', 'h3', 'strong', 'b'])
            if nom:
                data['nom'] = nom.get_text(strip=True)

            # Lien vers la fiche détaillée
            link = entry.find('a', href=True)
            if link:
                data['url_fiche'] = urljoin(ANNUAIRE_URL, link['href'])

            # Adresse
            address_elem = entry.find(['address', 'div'], class_=['address', 'adresse'])
            if address_elem:
                data['adresse'] = address_elem.get_text(strip=True)
            else:
                # Cherche dans le texte brut
                text = entry.get_text()
                data['adresse'] = text

            # Téléphone
            tel_elem = entry.find(string=lambda s: s and ('Tel' in s or 'Tél' in s))
            if tel_elem:
                data['telephone'] = tel_elem.strip()

            # Email
            email = entry.find('a', href=lambda h: h and h.startswith('mailto:'))
            if email:
                data['email'] = email['href'].replace('mailto:', '')

            # Site web
            website = entry.find('a', href=lambda h: h and (h.startswith('http://') or h.startswith('https://')))
            if website:
                data['site_web'] = website['href']

            # Extrait le département depuis l'adresse
            data['departement'] = self._extract_department(data.get('adresse', ''))

            return data if data.get('nom') else None

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données: {e}")
            return None

    def _extract_department(self, address: str) -> Optional[str]:
        """Extrait le numéro de département depuis une adresse"""
        import re

        # Recherche un code postal (75XXX, 92XXX, etc.)
        match = re.search(r'\b(75|77|78|91|92|93|94|95)\d{3}\b', address)
        if match:
            return match.group(1)

        # Recherche des noms de départements
        dept_names = {
            'paris': '75',
            'seine-et-marne': '77',
            'yvelines': '78',
            'essonne': '91',
            'hauts-de-seine': '92',
            'seine-saint-denis': '93',
            'val-de-marne': '94',
            'val-d\'oise': '95'
        }

        address_lower = address.lower()
        for name, code in dept_names.items():
            if name in address_lower:
                return code

        return None

    def _is_in_target_region(self, admin_data: Dict) -> bool:
        """Vérifie si l'administrateur est dans la région cible"""
        dept = admin_data.get('departement')
        if dept and dept in TARGET_DEPARTMENTS:
            return True

        # Vérification alternative par le texte de l'adresse
        address = admin_data.get('adresse', '').lower()
        region_keywords = ['paris', 'île-de-france', 'ile-de-france'] + \
                         [d for d in TARGET_DEPARTMENTS]

        return any(keyword in address for keyword in region_keywords)

    def scrape_all_pages(self) -> List[Dict]:
        """
        Scrappe toutes les pages de l'annuaire

        Returns:
            Liste de tous les administrateurs trouvés en Île-de-France
        """
        logger.info("Début du scraping de l'annuaire")

        # Récupère la première page
        html = self.get_page(ANNUAIRE_URL)
        if not html:
            logger.error("Impossible de récupérer la page de l'annuaire")
            return []

        # Parse la première page
        self.administrateurs.extend(self.parse_annuaire_page(html))

        # Recherche des pages suivantes (pagination)
        soup = BeautifulSoup(html, 'html.parser')
        pagination_links = self._find_pagination_links(soup)

        # Scrappe les pages suivantes
        for page_url in pagination_links:
            logger.info(f"Scraping de la page: {page_url}")
            time.sleep(DELAY_BETWEEN_REQUESTS)

            page_html = self.get_page(page_url)
            if page_html:
                self.administrateurs.extend(self.parse_annuaire_page(page_html))

        logger.info(f"Scraping terminé. {len(self.administrateurs)} administrateurs trouvés en {TARGET_REGION}")
        return self.administrateurs

    def _find_pagination_links(self, soup) -> List[str]:
        """
        Trouve les liens de pagination

        Returns:
            Liste des URLs des pages suivantes
        """
        pagination_links = []

        # Possibilité 1: Liens "Page suivante" ou "Next"
        next_links = soup.find_all('a', string=lambda s: s and ('suivant' in s.lower() or 'next' in s.lower()))

        # Possibilité 2: Liens numérotés
        page_links = soup.find_all('a', class_=['page', 'pagination', 'page-link'])

        # Possibilité 3: Recherche dans un élément de pagination
        pagination = soup.find(['div', 'nav', 'ul'], class_=['pagination', 'pages'])
        if pagination:
            page_links.extend(pagination.find_all('a', href=True))

        # Collecte les URLs uniques
        seen = set()
        for link in next_links + page_links:
            href = link.get('href')
            if href:
                full_url = urljoin(ANNUAIRE_URL, href)
                if full_url not in seen and full_url != ANNUAIRE_URL:
                    seen.add(full_url)
                    pagination_links.append(full_url)

        logger.info(f"Trouvé {len(pagination_links)} pages de pagination")
        return pagination_links

    def save_results(self, filename: str = 'administrateurs_idf.json'):
        """Sauvegarde les résultats dans un fichier JSON"""
        import os
        from config import OUTPUT_DIR

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, filename)

        data = {
            'region': TARGET_REGION,
            'total': len(self.administrateurs),
            'administrateurs': self.administrateurs
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Résultats sauvegardés dans {filepath}")

    def load_results(self, filename: str = 'administrateurs_idf.json') -> List[Dict]:
        """Charge les résultats depuis un fichier JSON"""
        import os
        from config import OUTPUT_DIR

        filepath = os.path.join(OUTPUT_DIR, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.administrateurs = data.get('administrateurs', [])
                logger.info(f"{len(self.administrateurs)} administrateurs chargés depuis {filepath}")
                return self.administrateurs
        except FileNotFoundError:
            logger.warning(f"Fichier {filepath} non trouvé")
            return []


if __name__ == "__main__":
    # Test du scraper
    scraper = AnnuaireScraper(use_selenium=False)

    # Tente de scraper
    administrateurs = scraper.scrape_all_pages()

    if administrateurs:
        scraper.save_results()
        print(f"\n✓ {len(administrateurs)} administrateurs judiciaires trouvés en Île-de-France")

        # Affiche quelques exemples
        print("\nExemples:")
        for admin in administrateurs[:3]:
            print(f"  - {admin.get('nom', 'N/A')}")
            if admin.get('site_web'):
                print(f"    Site web: {admin['site_web']}")
    else:
        print("\n⚠ Aucun administrateur trouvé. Le site nécessite probablement Selenium.")
        print("Essayez: scraper = AnnuaireScraper(use_selenium=True)")
