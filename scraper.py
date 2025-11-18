"""
Web Scraper pour quadratic-labs.com
Ce script scrappe le site web quadratic-labs.com et retourne la liste des pages trouvées.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List
import json
import time
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuadraticLabsScraper:
    """Scraper pour le site quadratic-labs.com"""

    def __init__(self, base_url: str = "https://quadratic-labs.com"):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls: Set[str] = set()
        self.found_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def is_valid_url(self, url: str) -> bool:
        """Vérifie si l'URL appartient au même domaine"""
        parsed = urlparse(url)
        return parsed.netloc == self.domain or parsed.netloc == ''

    def normalize_url(self, url: str) -> str:
        """Normalise l'URL en supprimant les fragments et paramètres inutiles"""
        parsed = urlparse(url)
        # Supprime le fragment (#)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized.rstrip('/')

    def get_links_from_page(self, url: str) -> Set[str]:
        """Extrait tous les liens d'une page"""
        links = set()

        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Trouve tous les liens <a href="...">
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Convertit les URLs relatives en absolues
                absolute_url = urljoin(url, href)

                # Vérifie si l'URL est valide et appartient au domaine
                if self.is_valid_url(absolute_url):
                    normalized = self.normalize_url(absolute_url)
                    links.add(normalized)

            return links

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors du scraping de {url}: {e}")
            return set()

    def scrape(self, max_pages: int = 100, delay: float = 0.5) -> List[str]:
        """
        Scrappe le site web et retourne la liste des pages trouvées

        Args:
            max_pages: Nombre maximum de pages à scraper
            delay: Délai en secondes entre chaque requête

        Returns:
            Liste des URLs trouvées
        """
        logger.info(f"Début du scraping de {self.base_url}")

        # Ajoute l'URL de base à la liste des URLs à visiter
        to_visit = {self.base_url}

        while to_visit and len(self.visited_urls) < max_pages:
            # Prend une URL à visiter
            current_url = to_visit.pop()

            # Si déjà visitée, passe à la suivante
            if current_url in self.visited_urls:
                continue

            # Marque comme visitée
            self.visited_urls.add(current_url)
            self.found_urls.add(current_url)

            # Extrait les liens de la page
            links = self.get_links_from_page(current_url)

            # Ajoute les nouveaux liens à visiter
            for link in links:
                if link not in self.visited_urls:
                    to_visit.add(link)
                    self.found_urls.add(link)

            # Délai pour ne pas surcharger le serveur
            time.sleep(delay)

        logger.info(f"Scraping terminé. {len(self.found_urls)} pages trouvées.")
        return sorted(list(self.found_urls))

    def save_to_json(self, filename: str = "quadratic_labs_pages.json"):
        """Sauvegarde les URLs trouvées dans un fichier JSON"""
        data = {
            "base_url": self.base_url,
            "total_pages": len(self.found_urls),
            "pages": sorted(list(self.found_urls))
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Résultats sauvegardés dans {filename}")

    def save_to_txt(self, filename: str = "quadratic_labs_pages.txt"):
        """Sauvegarde les URLs trouvées dans un fichier texte"""
        with open(filename, 'w', encoding='utf-8') as f:
            for url in sorted(self.found_urls):
                f.write(f"{url}\n")

        logger.info(f"Résultats sauvegardés dans {filename}")


def main():
    """Fonction principale"""
    # Crée le scraper
    scraper = QuadraticLabsScraper()

    # Lance le scraping
    pages = scraper.scrape(max_pages=100, delay=0.5)

    # Affiche les résultats
    print(f"\n{'='*60}")
    print(f"RÉSULTATS DU SCRAPING")
    print(f"{'='*60}")
    print(f"Nombre total de pages trouvées: {len(pages)}")
    print(f"\nListe des pages:")
    for i, page in enumerate(pages, 1):
        print(f"{i}. {page}")

    # Sauvegarde les résultats
    scraper.save_to_json()
    scraper.save_to_txt()

    print(f"\n{'='*60}")
    print(f"Résultats sauvegardés dans:")
    print(f"  - quadratic_labs_pages.json")
    print(f"  - quadratic_labs_pages.txt")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
