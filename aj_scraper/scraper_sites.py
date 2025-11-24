"""
Module pour analyser les sites web des administrateurs judiciaires
et identifier les pages contenant des annonces de vente
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
from typing import List, Dict, Set, Optional
from urllib.parse import urljoin, urlparse
import re

from config import (
    DEFAULT_HEADERS, REQUEST_TIMEOUT, DELAY_BETWEEN_REQUESTS,
    MAX_RETRIES, ANNONCE_KEYWORDS
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SiteAnalyzer:
    """
    Analyseur de sites web d'administrateurs judiciaires

    Ce module parcourt les sites web et identifie les pages
    contenant des annonces de vente d'entreprises.
    """

    def __init__(self, max_pages_per_site: int = 50):
        """
        Initialise l'analyseur

        Args:
            max_pages_per_site: Nombre maximum de pages à analyser par site
        """
        self.max_pages_per_site = max_pages_per_site
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def analyze_site(self, base_url: str) -> Dict:
        """
        Analyse un site web pour trouver les pages d'annonces

        Args:
            base_url: URL du site à analyser

        Returns:
            Dictionnaire avec les résultats de l'analyse
        """
        logger.info(f"Analyse du site: {base_url}")

        result = {
            'base_url': base_url,
            'accessible': False,
            'pages_annonces': [],
            'structure_detected': None,
            'error': None
        }

        try:
            # Teste l'accessibilité
            response = self.session.get(base_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            result['accessible'] = True

            # Parse la page d'accueil
            soup = BeautifulSoup(response.content, 'html.parser')

            # Stratégie 1: Recherche dans la navigation
            annonce_links = self._find_annonce_links_in_nav(soup, base_url)

            # Stratégie 2: Recherche dans le contenu
            if not annonce_links:
                annonce_links = self._find_annonce_links_in_content(soup, base_url)

            # Stratégie 3: Crawl du site (si rien trouvé)
            if not annonce_links:
                annonce_links = self._crawl_site(base_url, max_pages=20)

            # Analyse la structure des pages trouvées
            if annonce_links:
                result['pages_annonces'] = list(annonce_links)
                result['structure_detected'] = self._detect_structure(
                    list(annonce_links)[0] if annonce_links else None
                )

            logger.info(f"✓ Analyse terminée: {len(annonce_links)} page(s) d'annonces trouvée(s)")

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'accès à {base_url}: {e}")
            result['error'] = str(e)

        return result

    def _find_annonce_links_in_nav(self, soup, base_url: str) -> Set[str]:
        """
        Recherche les liens vers les annonces dans le menu de navigation

        Args:
            soup: BeautifulSoup object
            base_url: URL de base du site

        Returns:
            Set d'URLs trouvées
        """
        annonce_links = set()

        # Recherche dans les menus de navigation
        nav_elements = soup.find_all(['nav', 'header', 'div'], class_=lambda c: c and ('menu' in c.lower() or 'nav' in c.lower()))

        for nav in nav_elements:
            links = nav.find_all('a', href=True)
            for link in links:
                link_text = link.get_text(strip=True).lower()
                link_href = link['href']

                # Vérifie si le lien contient des mots-clés
                if any(keyword in link_text for keyword in ANNONCE_KEYWORDS):
                    full_url = urljoin(base_url, link_href)
                    annonce_links.add(full_url)
                    logger.info(f"  Lien trouvé dans nav: {link_text} -> {full_url}")

        return annonce_links

    def _find_annonce_links_in_content(self, soup, base_url: str) -> Set[str]:
        """
        Recherche les liens vers les annonces dans le contenu de la page

        Args:
            soup: BeautifulSoup object
            base_url: URL de base du site

        Returns:
            Set d'URLs trouvées
        """
        annonce_links = set()

        # Recherche tous les liens
        all_links = soup.find_all('a', href=True)

        for link in all_links:
            link_text = link.get_text(strip=True).lower()
            link_href = link['href']

            # Vérifie le texte du lien
            if any(keyword in link_text for keyword in ANNONCE_KEYWORDS):
                full_url = urljoin(base_url, link_href)
                annonce_links.add(full_url)
                logger.info(f"  Lien trouvé dans contenu: {link_text} -> {full_url}")

            # Vérifie aussi l'URL elle-même
            elif any(keyword in link_href.lower() for keyword in ANNONCE_KEYWORDS):
                full_url = urljoin(base_url, link_href)
                annonce_links.add(full_url)
                logger.info(f"  URL trouvée avec mot-clé: {full_url}")

        return annonce_links

    def _crawl_site(self, base_url: str, max_pages: int = 20) -> Set[str]:
        """
        Crawle le site pour trouver les pages d'annonces

        Args:
            base_url: URL de base du site
            max_pages: Nombre maximum de pages à crawler

        Returns:
            Set d'URLs de pages d'annonces
        """
        logger.info(f"  Crawling du site (max {max_pages} pages)...")

        domain = urlparse(base_url).netloc
        visited = set()
        to_visit = [base_url]
        annonce_pages = set()

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)

            if url in visited:
                continue

            visited.add(url)

            try:
                time.sleep(DELAY_BETWEEN_REQUESTS)
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Vérifie si cette page contient des annonces
                if self._page_contains_annonces(soup):
                    annonce_pages.add(url)
                    logger.info(f"  ✓ Page d'annonces trouvée: {url}")

                # Récupère les liens pour continuer le crawl
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)

                    # Reste sur le même domaine
                    if urlparse(full_url).netloc == domain:
                        if full_url not in visited and full_url not in to_visit:
                            to_visit.append(full_url)

            except Exception as e:
                logger.error(f"  Erreur lors du crawl de {url}: {e}")
                continue

        return annonce_pages

    def _page_contains_annonces(self, soup) -> bool:
        """
        Vérifie si une page contient des annonces

        Args:
            soup: BeautifulSoup object

        Returns:
            True si la page contient des annonces
        """
        page_text = soup.get_text().lower()

        # Compte les occurrences de mots-clés
        keyword_count = sum(
            page_text.count(keyword.lower())
            for keyword in ANNONCE_KEYWORDS
        )

        # Si au moins 3 mots-clés présents, considère comme une page d'annonces
        return keyword_count >= 3

    def _detect_structure(self, url: Optional[str]) -> Optional[Dict]:
        """
        Détecte la structure d'une page d'annonces

        Args:
            url: URL de la page à analyser

        Returns:
            Dictionnaire décrivant la structure ou None
        """
        if not url:
            return None

        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            structure = {
                'url': url,
                'has_list': False,
                'has_table': False,
                'has_cards': False,
                'container_class': None,
                'item_tag': None,
                'pagination': False
            }

            # Détecte les tables
            tables = soup.find_all('table')
            if tables:
                structure['has_table'] = True
                structure['item_tag'] = 'tr'

            # Détecte les listes
            lists = soup.find_all(['ul', 'ol'], class_=lambda c: c and ('list' in c.lower() or 'annonce' in c.lower()))
            if lists:
                structure['has_list'] = True
                structure['item_tag'] = 'li'

            # Détecte les cartes/blocs
            cards = soup.find_all(['div', 'article'], class_=lambda c: c and ('card' in c.lower() or 'item' in c.lower() or 'annonce' in c.lower()))
            if cards:
                structure['has_cards'] = True
                structure['item_tag'] = 'div'
                if cards[0].get('class'):
                    structure['container_class'] = ' '.join(cards[0]['class'])

            # Détecte la pagination
            pagination = soup.find(['div', 'nav', 'ul'], class_=lambda c: c and 'pagination' in c.lower())
            if pagination:
                structure['pagination'] = True

            return structure

        except Exception as e:
            logger.error(f"Erreur lors de la détection de structure: {e}")
            return None

    def analyze_multiple_sites(self, sites: List[str]) -> List[Dict]:
        """
        Analyse plusieurs sites

        Args:
            sites: Liste des URLs à analyser

        Returns:
            Liste des résultats d'analyse
        """
        results = []

        for i, site_url in enumerate(sites, 1):
            logger.info(f"\n[{i}/{len(sites)}] Analyse de {site_url}")
            result = self.analyze_site(site_url)
            results.append(result)

            # Délai entre chaque site
            if i < len(sites):
                time.sleep(DELAY_BETWEEN_REQUESTS * 2)

        return results

    def save_analysis(self, results: List[Dict], filename: str = 'sites_analysis.json'):
        """Sauvegarde les résultats de l'analyse"""
        import json
        import os
        from config import OUTPUT_DIR

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Analyse sauvegardée dans {filepath}")


if __name__ == "__main__":
    # Test avec quelques sites d'exemple
    test_sites = [
        "https://example-aj1.fr",
        "https://example-aj2.fr",
    ]

    analyzer = SiteAnalyzer(max_pages_per_site=30)

    print("Analyse des sites d'administrateurs judiciaires...")
    print("=" * 60)

    results = analyzer.analyze_multiple_sites(test_sites)

    # Affiche un résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DE L'ANALYSE")
    print("=" * 60)

    accessible = sum(1 for r in results if r['accessible'])
    with_annonces = sum(1 for r in results if r['pages_annonces'])

    print(f"Sites accessibles: {accessible}/{len(results)}")
    print(f"Sites avec annonces: {with_annonces}/{len(results)}")

    print("\nDétails:")
    for result in results:
        print(f"\n{result['base_url']}:")
        print(f"  Accessible: {result['accessible']}")
        print(f"  Pages d'annonces: {len(result['pages_annonces'])}")
        if result['pages_annonces']:
            for page in result['pages_annonces']:
                print(f"    - {page}")

    analyzer.save_analysis(results)
