#!/usr/bin/env python3
"""
Script principal pour scraper les annonces d'administrateurs judiciaires

Ce script orchestre les 3 phases du scraping:
1. Extraction des administrateurs judiciaires en Île-de-France
2. Analyse des sites web pour trouver les pages d'annonces
3. Extraction et filtrage des annonces par secteur
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

from scraper_annuaire import AnnuaireScraper
from scraper_sites import SiteAnalyzer
from scraper_annonces import AnnonceScraper
from filters import AnnonceFilter
from config import OUTPUT_DIR, TARGET_REGION, TARGET_SECTORS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AJScraperPipeline:
    """
    Pipeline complet de scraping d'annonces d'administrateurs judiciaires
    """

    def __init__(self, use_selenium: bool = False, skip_phase1: bool = False, skip_phase2: bool = False):
        """
        Initialise le pipeline

        Args:
            use_selenium: Utiliser Selenium pour le scraping
            skip_phase1: Passer la phase 1 (utilise les données existantes)
            skip_phase2: Passer la phase 2 (utilise les données existantes)
        """
        self.use_selenium = use_selenium
        self.skip_phase1 = skip_phase1
        self.skip_phase2 = skip_phase2

        self.administrateurs = []
        self.sites_analysis = []
        self.annonces = []
        self.filtered_annonces = []

    def phase1_extract_administrateurs(self):
        """
        Phase 1: Extrait les administrateurs judiciaires de l'annuaire
        """
        print("\n" + "="*60)
        print("PHASE 1: EXTRACTION DES ADMINISTRATEURS JUDICIAIRES")
        print("="*60)

        if self.skip_phase1:
            logger.info("Phase 1 ignorée, chargement des données existantes...")
            scraper = AnnuaireScraper(use_selenium=self.use_selenium)
            self.administrateurs = scraper.load_results()

            if not self.administrateurs:
                logger.error("Aucune donnée existante trouvée. Lancez sans --skip-phase1")
                sys.exit(1)

            return

        scraper = AnnuaireScraper(use_selenium=self.use_selenium)
        self.administrateurs = scraper.scrape_all_pages()

        if not self.administrateurs:
            logger.error("Aucun administrateur trouvé. Le site nécessite peut-être Selenium.")
            logger.info("Essayez avec l'option --selenium")
            sys.exit(1)

        scraper.save_results()

        print(f"\n✓ Phase 1 terminée: {len(self.administrateurs)} administrateurs trouvés")
        self._print_phase1_summary()

    def _print_phase1_summary(self):
        """Affiche un résumé de la phase 1"""
        with_website = sum(1 for a in self.administrateurs if a.get('site_web'))

        print("\nRésumé:")
        print(f"  - Total: {len(self.administrateurs)}")
        print(f"  - Avec site web: {with_website}")

        if with_website > 0:
            print("\nExemples d'administrateurs avec site web:")
            count = 0
            for admin in self.administrateurs:
                if admin.get('site_web') and count < 5:
                    print(f"  - {admin.get('nom', 'N/A')}")
                    print(f"    Site: {admin['site_web']}")
                    count += 1

    def phase2_analyze_sites(self):
        """
        Phase 2: Analyse les sites web pour trouver les pages d'annonces
        """
        print("\n" + "="*60)
        print("PHASE 2: ANALYSE DES SITES WEB")
        print("="*60)

        # Extrait les sites web
        sites = [a['site_web'] for a in self.administrateurs if a.get('site_web')]

        if not sites:
            logger.error("Aucun site web trouvé dans les données des administrateurs")
            sys.exit(1)

        print(f"\n{len(sites)} sites à analyser")

        if self.skip_phase2:
            logger.info("Phase 2 ignorée, chargement des données existantes...")
            analysis_file = os.path.join(OUTPUT_DIR, 'sites_analysis.json')

            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    self.sites_analysis = json.load(f)
                logger.info(f"Analyse chargée: {len(self.sites_analysis)} sites")
            except FileNotFoundError:
                logger.error("Aucune analyse existante trouvée. Lancez sans --skip-phase2")
                sys.exit(1)

            return

        analyzer = SiteAnalyzer()
        self.sites_analysis = analyzer.analyze_multiple_sites(sites)
        analyzer.save_analysis(self.sites_analysis)

        print(f"\n✓ Phase 2 terminée")
        self._print_phase2_summary()

    def _print_phase2_summary(self):
        """Affiche un résumé de la phase 2"""
        accessible = sum(1 for s in self.sites_analysis if s.get('accessible'))
        with_annonces = sum(1 for s in self.sites_analysis if s.get('pages_annonces'))

        print("\nRésumé:")
        print(f"  - Sites accessibles: {accessible}/{len(self.sites_analysis)}")
        print(f"  - Sites avec pages d'annonces: {with_annonces}")

        if with_annonces > 0:
            print("\nExemples de pages d'annonces trouvées:")
            count = 0
            for site in self.sites_analysis:
                if site.get('pages_annonces') and count < 5:
                    print(f"\n  {site['base_url']}:")
                    for page in site['pages_annonces'][:3]:
                        print(f"    - {page}")
                    count += 1

    def phase3_extract_and_filter_annonces(self):
        """
        Phase 3: Extrait et filtre les annonces
        """
        print("\n" + "="*60)
        print("PHASE 3: EXTRACTION ET FILTRAGE DES ANNONCES")
        print("="*60)

        # Collecte toutes les pages d'annonces
        all_annonce_pages = []
        for site in self.sites_analysis:
            if site.get('pages_annonces'):
                all_annonce_pages.extend(site['pages_annonces'])

        if not all_annonce_pages:
            logger.warning("Aucune page d'annonces trouvée")
            return

        print(f"\n{len(all_annonce_pages)} pages d'annonces à scraper")

        # Extrait les annonces
        scraper = AnnonceScraper()
        self.annonces = scraper.extract_annonces_from_multiple_pages(all_annonce_pages)

        if not self.annonces:
            logger.warning("Aucune annonce extraite")
            return

        scraper.save_annonces(self.annonces, 'annonces_brutes.json')

        # Applique les filtres
        filtre = AnnonceFilter()
        self.filtered_annonces = filtre.apply_all_filters(
            self.annonces,
            filter_sector=True,
            filter_location=True
        )

        # Sauvegarde les résultats filtrés
        scraper.save_annonces(self.filtered_annonces, 'annonces_filtrees.json')
        scraper.export_to_csv(self.filtered_annonces, 'annonces_filtrees.csv')

        print(f"\n✓ Phase 3 terminée")
        self._print_phase3_summary(filtre)

    def _print_phase3_summary(self, filtre: AnnonceFilter):
        """Affiche un résumé de la phase 3"""
        print("\nRésumé:")
        print(f"  - Annonces brutes: {len(self.annonces)}")
        print(f"  - Annonces filtrées: {len(self.filtered_annonces)}")

        if self.filtered_annonces:
            stats = filtre.get_statistics(self.filtered_annonces)

            print(f"\nStatistiques des annonces filtrées:")
            print(f"  - Avec prix: {stats['with_price']}")
            print(f"  - Avec localisation: {stats['with_location']}")
            print(f"  - Avec contact: {stats['with_contact']}")

            if stats['sectors']:
                print(f"\n  Secteurs détectés:")
                for sector, count in sorted(stats['sectors'].items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    - {sector}: {count}")

            if stats['departments']:
                print(f"\n  Départements:")
                for dept, count in sorted(stats['departments'].items(), key=lambda x: x[1], reverse=True):
                    print(f"    - {dept}: {count}")

            print(f"\n  Exemples d'annonces retenues:")
            for annonce in self.filtered_annonces[:3]:
                print(f"\n    Titre: {annonce.get('titre', 'N/A')}")
                print(f"    Description: {annonce.get('description', 'N/A')[:100]}...")
                print(f"    Localisation: {annonce.get('localisation', 'N/A')}")
                print(f"    Prix: {annonce.get('prix', 'N/A')}")

    def run(self):
        """
        Exécute le pipeline complet
        """
        start_time = datetime.now()

        print("\n" + "="*60)
        print("SCRAPER D'ANNONCES D'ADMINISTRATEURS JUDICIAIRES")
        print("="*60)
        print(f"Région cible: {TARGET_REGION}")
        print(f"Secteurs cibles: {', '.join(TARGET_SECTORS[:5])}...")
        print(f"Mode: {'Selenium' if self.use_selenium else 'Requests'}")

        try:
            # Phase 1
            if not self.skip_phase1:
                self.phase1_extract_administrateurs()

            # Phase 2
            if not self.skip_phase2:
                self.phase2_analyze_sites()

            # Phase 3
            self.phase3_extract_and_filter_annonces()

            # Résumé final
            end_time = datetime.now()
            duration = end_time - start_time

            print("\n" + "="*60)
            print("RÉSUMÉ FINAL")
            print("="*60)
            print(f"Durée totale: {duration}")
            print(f"Administrateurs: {len(self.administrateurs)}")
            print(f"Sites analysés: {len(self.sites_analysis)}")
            print(f"Annonces brutes: {len(self.annonces)}")
            print(f"Annonces filtrées: {len(self.filtered_annonces)}")

            print("\nFichiers générés:")
            print(f"  - {OUTPUT_DIR}/administrateurs_idf.json")
            print(f"  - {OUTPUT_DIR}/sites_analysis.json")
            print(f"  - {OUTPUT_DIR}/annonces_brutes.json")
            print(f"  - {OUTPUT_DIR}/annonces_filtrees.json")
            print(f"  - {OUTPUT_DIR}/annonces_filtrees.csv")

        except KeyboardInterrupt:
            print("\n\nArrêt demandé par l'utilisateur")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Scraper d'annonces d'administrateurs judiciaires en Île-de-France"
    )

    parser.add_argument(
        '--selenium',
        action='store_true',
        help="Utiliser Selenium au lieu de requests (pour contourner les protections anti-scraping)"
    )

    parser.add_argument(
        '--skip-phase1',
        action='store_true',
        help="Ignorer la phase 1 (utilise les données existantes)"
    )

    parser.add_argument(
        '--skip-phase2',
        action='store_true',
        help="Ignorer la phase 2 (utilise les données existantes)"
    )

    parser.add_argument(
        '--phase',
        type=int,
        choices=[1, 2, 3],
        help="Exécuter uniquement une phase spécifique"
    )

    args = parser.parse_args()

    # Crée le répertoire de sortie
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Exécute le pipeline
    pipeline = AJScraperPipeline(
        use_selenium=args.selenium,
        skip_phase1=args.skip_phase1 or (args.phase in [2, 3]),
        skip_phase2=args.skip_phase2 or (args.phase == 3)
    )

    if args.phase == 1:
        pipeline.phase1_extract_administrateurs()
    elif args.phase == 2:
        pipeline.phase1_extract_administrateurs()
        pipeline.phase2_analyze_sites()
    elif args.phase == 3:
        pipeline.phase1_extract_administrateurs()
        pipeline.phase2_analyze_sites()
        pipeline.phase3_extract_and_filter_annonces()
    else:
        pipeline.run()


if __name__ == "__main__":
    main()
