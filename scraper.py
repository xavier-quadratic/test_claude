"""
Web Scraper pour quadratic-labs.com
Ce script scrappe le site web quadratic-labs.com et retourne la liste des pages trouvées.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict, Optional
import json
import time
import logging
from colorama import Fore, Style, init

# Initialise colorama pour le support Windows
init(autoreset=True)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuadraticLabsScraper:
    """Scraper pour le site quadratic-labs.com"""

    def __init__(self, base_url: str = "https://quadratic-labs.com", use_colors: bool = True):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls: Set[str] = set()
        self.found_urls: Set[str] = set()
        self.url_hierarchy: Dict[str, Dict] = {}  # Stocke la hiérarchie parent-enfant
        self.url_depth: Dict[str, int] = {}  # Stocke la profondeur de chaque URL
        self.use_colors = use_colors  # Active/désactive la colorisation
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
        # Format: (url, parent_url, depth)
        to_visit = [(self.base_url, None, 0)]

        # Initialise la racine
        self.url_depth[self.base_url] = 0
        self.url_hierarchy[self.base_url] = {
            'parent': None,
            'children': [],
            'depth': 0
        }

        while to_visit and len(self.visited_urls) < max_pages:
            # Prend une URL à visiter (avec son parent et profondeur)
            current_url, parent_url, depth = to_visit.pop(0)

            # Si déjà visitée, passe à la suivante
            if current_url in self.visited_urls:
                continue

            # Marque comme visitée
            self.visited_urls.add(current_url)
            self.found_urls.add(current_url)

            # Stocke la profondeur
            if current_url not in self.url_depth:
                self.url_depth[current_url] = depth

            # Initialise la hiérarchie si nécessaire
            if current_url not in self.url_hierarchy:
                self.url_hierarchy[current_url] = {
                    'parent': parent_url,
                    'children': [],
                    'depth': depth
                }

            # Ajoute l'enfant au parent
            if parent_url and parent_url in self.url_hierarchy:
                if current_url not in self.url_hierarchy[parent_url]['children']:
                    self.url_hierarchy[parent_url]['children'].append(current_url)

            # Extrait les liens de la page
            links = self.get_links_from_page(current_url)

            # Ajoute les nouveaux liens à visiter
            for link in links:
                if link not in self.visited_urls:
                    to_visit.append((link, current_url, depth + 1))
                    self.found_urls.add(link)

                    # Initialise la hiérarchie pour le nouveau lien
                    if link not in self.url_hierarchy:
                        self.url_hierarchy[link] = {
                            'parent': current_url,
                            'children': [],
                            'depth': depth + 1
                        }

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

    def _build_tree_dict(self, url: str) -> Dict:
        """Construit un dictionnaire hiérarchique récursif pour une URL"""
        if url not in self.url_hierarchy:
            return {}

        node = {
            'url': url,
            'depth': self.url_hierarchy[url]['depth'],
            'children': []
        }

        for child_url in sorted(self.url_hierarchy[url]['children']):
            node['children'].append(self._build_tree_dict(child_url))

        return node

    def save_tree_to_json(self, filename: str = "quadratic_labs_tree.json"):
        """Sauvegarde l'arborescence hiérarchique dans un fichier JSON"""
        tree = self._build_tree_dict(self.base_url)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)

        logger.info(f"Arborescence sauvegardée dans {filename}")

    def _get_color_for_depth(self, depth: int) -> str:
        """Retourne la couleur appropriée selon la profondeur"""
        if not self.use_colors:
            return ""

        # Palette de couleurs par profondeur
        color_map = {
            0: Fore.CYAN + Style.BRIGHT,      # Racine : Cyan brillant
            1: Fore.GREEN,                     # Niveau 1 : Vert
            2: Fore.YELLOW,                    # Niveau 2 : Jaune
            3: Fore.MAGENTA,                   # Niveau 3 : Magenta
        }

        # Pour les profondeurs > 3, utilise rouge
        return color_map.get(depth, Fore.RED)

    def _print_tree_recursive(self, url: str, prefix: str = "", is_last: bool = True):
        """Affiche récursivement l'arborescence en format ASCII avec couleurs"""
        if url not in self.url_hierarchy:
            return

        depth = self.url_hierarchy[url]['depth']
        color = self._get_color_for_depth(depth)
        connector_color = Style.DIM if self.use_colors else ""
        depth_color = Style.DIM if self.use_colors else ""
        reset = Style.RESET_ALL if self.use_colors else ""

        # Affiche l'URL courante
        connector = "+-- " if is_last else "+-- "
        if url == self.base_url:
            # Pour la racine, affiche juste l'URL
            print(f"{color}{url} (racine){reset}")
        else:
            # Simplifie l'affichage en montrant juste le chemin
            path = urlparse(url).path or '/'
            if urlparse(url).query:
                path += f"?{urlparse(url).query}"
            depth_info = f" {depth_color}[profondeur: {depth}]{reset}"
            print(f"{connector_color}{prefix}{connector}{reset}{color}{path}{depth_info}")

        # Prépare le préfixe pour les enfants
        if url != self.base_url:
            extension = "    " if is_last else "|   "
            new_prefix = prefix + extension
        else:
            new_prefix = ""

        # Affiche les enfants
        children = sorted(self.url_hierarchy[url]['children'])
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            self._print_tree_recursive(child, new_prefix, is_last_child)

    def print_tree(self):
        """Affiche l'arborescence du site dans le terminal"""
        print(f"\n{'='*60}")
        print(f"ARBORESCENCE DU SITE")
        print(f"{'='*60}\n")

        if not self.url_hierarchy:
            print("Aucune arborescence disponible. Lancez d'abord le scraping.")
            return

        self._print_tree_recursive(self.base_url)
        print()

    def get_tree_stats(self) -> Dict:
        """Retourne des statistiques sur l'arborescence"""
        max_depth = max(self.url_depth.values()) if self.url_depth else 0

        # Compte les pages par profondeur
        pages_by_depth = {}
        for url, depth in self.url_depth.items():
            pages_by_depth[depth] = pages_by_depth.get(depth, 0) + 1

        return {
            'total_pages': len(self.found_urls),
            'max_depth': max_depth,
            'pages_by_depth': pages_by_depth
        }


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

    # Affiche l'arborescence
    scraper.print_tree()

    # Affiche les statistiques
    stats = scraper.get_tree_stats()
    print(f"{'='*60}")
    print(f"STATISTIQUES DE L'ARBORESCENCE")
    print(f"{'='*60}")
    print(f"Profondeur maximale: {stats['max_depth']}")
    print(f"\nRépartition des pages par profondeur:")
    for depth in sorted(stats['pages_by_depth'].keys()):
        count = stats['pages_by_depth'][depth]
        print(f"  Niveau {depth}: {count} page(s)")
    print()

    # Sauvegarde les résultats
    scraper.save_to_json()
    scraper.save_to_txt()
    scraper.save_tree_to_json()

    print(f"{'='*60}")
    print(f"Résultats sauvegardés dans:")
    print(f"  - quadratic_labs_pages.json (liste simple)")
    print(f"  - quadratic_labs_pages.txt (liste texte)")
    print(f"  - quadratic_labs_tree.json (arborescence hiérarchique)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
