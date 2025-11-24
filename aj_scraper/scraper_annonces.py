"""
Module pour extraire les annonces de vente d'entreprises
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin
import re
from datetime import datetime

from config import DEFAULT_HEADERS, REQUEST_TIMEOUT, DELAY_BETWEEN_REQUESTS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnnonceScraper:
    """
    Extracteur d'annonces de vente d'entreprises

    Ce module extrait les informations des annonces présentes sur les pages
    identifiées précédemment.
    """

    def __init__(self):
        """Initialise l'extracteur"""
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def extract_annonces_from_page(self, url: str, structure: Optional[Dict] = None) -> List[Dict]:
        """
        Extrait les annonces d'une page

        Args:
            url: URL de la page à scraper
            structure: Structure détectée (optionnelle)

        Returns:
            Liste des annonces extraites
        """
        logger.info(f"Extraction des annonces depuis: {url}")

        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Si on connaît la structure, utilise-la
            if structure:
                return self._extract_with_structure(soup, url, structure)
            else:
                # Sinon, essaie différentes méthodes
                return self._extract_with_heuristics(soup, url)

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction depuis {url}: {e}")
            return []

    def _extract_with_structure(self, soup, base_url: str, structure: Dict) -> List[Dict]:
        """
        Extrait les annonces en utilisant une structure connue

        Args:
            soup: BeautifulSoup object
            base_url: URL de base
            structure: Structure détectée

        Returns:
            Liste des annonces
        """
        annonces = []
        item_tag = structure.get('item_tag', 'div')

        # Trouve les conteneurs d'annonces
        if structure.get('has_table'):
            items = soup.find_all('tr')[1:]  # Ignore l'en-tête
        elif structure.get('container_class'):
            items = soup.find_all(item_tag, class_=structure['container_class'])
        else:
            items = soup.find_all(item_tag)

        for item in items:
            annonce = self._extract_annonce_data(item, base_url)
            if annonce:
                annonces.append(annonce)

        return annonces

    def _extract_with_heuristics(self, soup, base_url: str) -> List[Dict]:
        """
        Extrait les annonces en utilisant des heuristiques

        Args:
            soup: BeautifulSoup object
            base_url: URL de base

        Returns:
            Liste des annonces
        """
        annonces = []

        # Stratégie 1: Cherche des tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')[1:]  # Ignore l'en-tête
            for row in rows:
                annonce = self._extract_annonce_data(row, base_url)
                if annonce and self._is_valid_annonce(annonce):
                    annonces.append(annonce)

        # Stratégie 2: Cherche des divs/articles avec classes pertinentes
        if not annonces:
            containers = soup.find_all(
                ['div', 'article', 'li'],
                class_=lambda c: c and any(
                    keyword in c.lower()
                    for keyword in ['annonce', 'item', 'card', 'entry', 'offer']
                )
            )

            for container in containers:
                annonce = self._extract_annonce_data(container, base_url)
                if annonce and self._is_valid_annonce(annonce):
                    annonces.append(annonce)

        return annonces

    def _extract_annonce_data(self, element, base_url: str) -> Optional[Dict]:
        """
        Extrait les données d'une annonce depuis un élément HTML

        Args:
            element: Élément BeautifulSoup
            base_url: URL de base

        Returns:
            Dictionnaire avec les données de l'annonce
        """
        try:
            annonce = {
                'titre': None,
                'description': None,
                'entreprise': None,
                'secteur': None,
                'localisation': None,
                'prix': None,
                'date_publication': None,
                'date_limite': None,
                'reference': None,
                'url_details': None,
                'contact': None,
                'scraped_at': datetime.now().isoformat()
            }

            # Titre (h1, h2, h3, strong, ou premier lien)
            titre = element.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
            if titre:
                annonce['titre'] = titre.get_text(strip=True)
            else:
                # Essaie de trouver un lien
                link = element.find('a')
                if link:
                    annonce['titre'] = link.get_text(strip=True)
                    annonce['url_details'] = urljoin(base_url, link['href'])

            # Description
            desc = element.find(['p', 'div'], class_=lambda c: c and 'desc' in c.lower())
            if desc:
                annonce['description'] = desc.get_text(strip=True)
            else:
                # Prend le texte de l'élément
                annonce['description'] = element.get_text(strip=True)[:500]

            # Cherche des informations structurées
            text = element.get_text()

            # Localisation (codes postaux ou noms de villes)
            location_match = re.search(r'\b(\d{5})\b|\b([A-Z][a-zà-ÿ]+(?:\s+[A-Z][a-zà-ÿ]+)*)\b', text)
            if location_match:
                annonce['localisation'] = location_match.group(0)

            # Prix (cherche des montants en euros)
            price_patterns = [
                r'(\d+[\s\xa0]?\d*)\s*(?:€|euros?)',
                r'Prix\s*:?\s*(\d+[\s\xa0]?\d*)',
                r'Montant\s*:?\s*(\d+[\s\xa0]?\d*)'
            ]
            for pattern in price_patterns:
                price_match = re.search(pattern, text, re.IGNORECASE)
                if price_match:
                    annonce['prix'] = price_match.group(1).replace('\xa0', '').replace(' ', '')
                    break

            # Référence
            ref_match = re.search(r'R[ée]f[ée]rence\s*:?\s*([A-Z0-9\-]+)', text, re.IGNORECASE)
            if ref_match:
                annonce['reference'] = ref_match.group(1)

            # Date
            date_patterns = [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4})'
            ]
            for pattern in date_patterns:
                date_match = re.search(pattern, text, re.IGNORECASE)
                if date_match:
                    annonce['date_publication'] = date_match.group(1)
                    break

            # URL de détails (si pas déjà trouvée)
            if not annonce['url_details']:
                link = element.find('a', href=True)
                if link:
                    annonce['url_details'] = urljoin(base_url, link['href'])

            # Contact (email ou téléphone)
            email = element.find('a', href=lambda h: h and h.startswith('mailto:'))
            if email:
                annonce['contact'] = email['href'].replace('mailto:', '')
            else:
                tel_match = re.search(r'(\d{2}[\s.]?\d{2}[\s.]?\d{2}[\s.]?\d{2}[\s.]?\d{2})', text)
                if tel_match:
                    annonce['contact'] = tel_match.group(1)

            return annonce if annonce['titre'] else None

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction d'une annonce: {e}")
            return None

    def _is_valid_annonce(self, annonce: Dict) -> bool:
        """
        Vérifie si une annonce est valide

        Args:
            annonce: Dictionnaire de l'annonce

        Returns:
            True si l'annonce est valide
        """
        # Une annonce valide doit avoir au moins un titre et une description non vide
        return (
            annonce.get('titre') and
            len(annonce.get('titre', '')) > 5 and
            annonce.get('description') and
            len(annonce.get('description', '')) > 20
        )

    def extract_annonces_from_multiple_pages(self, pages: List[str], structures: Optional[Dict] = None) -> List[Dict]:
        """
        Extrait les annonces de plusieurs pages

        Args:
            pages: Liste des URLs à scraper
            structures: Dictionnaire URL -> structure

        Returns:
            Liste de toutes les annonces extraites
        """
        all_annonces = []

        for i, page_url in enumerate(pages, 1):
            logger.info(f"[{i}/{len(pages)}] Scraping de {page_url}")

            structure = structures.get(page_url) if structures else None
            annonces = self.extract_annonces_from_page(page_url, structure)

            logger.info(f"  → {len(annonces)} annonce(s) extraite(s)")
            all_annonces.extend(annonces)

            # Délai entre chaque page
            if i < len(pages):
                time.sleep(DELAY_BETWEEN_REQUESTS)

        logger.info(f"\n✓ Total: {len(all_annonces)} annonces extraites")
        return all_annonces

    def save_annonces(self, annonces: List[Dict], filename: str = 'annonces.json'):
        """Sauvegarde les annonces dans un fichier JSON"""
        import json
        import os
        from config import OUTPUT_DIR

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, filename)

        data = {
            'total': len(annonces),
            'extracted_at': datetime.now().isoformat(),
            'annonces': annonces
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Annonces sauvegardées dans {filepath}")

    def export_to_csv(self, annonces: List[Dict], filename: str = 'annonces.csv'):
        """Exporte les annonces en CSV"""
        import csv
        import os
        from config import OUTPUT_DIR

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, filename)

        if not annonces:
            logger.warning("Aucune annonce à exporter")
            return

        # Récupère toutes les clés possibles
        all_keys = set()
        for annonce in annonces:
            all_keys.update(annonce.keys())

        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(annonces)

        logger.info(f"Annonces exportées en CSV: {filepath}")


if __name__ == "__main__":
    # Test avec une URL d'exemple
    test_url = "https://example-aj.fr/annonces"

    scraper = AnnonceScraper()

    print("Extraction des annonces...")
    print("=" * 60)

    annonces = scraper.extract_annonces_from_page(test_url)

    print(f"\n✓ {len(annonces)} annonces extraites")

    if annonces:
        print("\nExemple d'annonce:")
        print(annonces[0])

        scraper.save_annonces(annonces)
        scraper.export_to_csv(annonces)
