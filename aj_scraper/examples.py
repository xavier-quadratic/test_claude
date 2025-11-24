"""
Exemples d'utilisation des différents modules du scraper
"""

def exemple_1_scraper_annuaire():
    """Exemple 1: Utilisation du scraper d'annuaire"""
    print("\n" + "="*60)
    print("EXEMPLE 1: Scraper d'annuaire")
    print("="*60)

    from scraper_annuaire import AnnuaireScraper

    # Création du scraper
    scraper = AnnuaireScraper(use_selenium=False)

    # Option 1: Scraping complet
    administrateurs = scraper.scrape_all_pages()

    # Affiche les résultats
    print(f"\n✓ {len(administrateurs)} administrateurs trouvés")

    # Sauvegarde
    scraper.save_results('mon_annuaire.json')

    # Affiche quelques exemples
    if administrateurs:
        print("\nPremiers résultats:")
        for admin in administrateurs[:3]:
            print(f"  - {admin.get('nom', 'N/A')}")
            if admin.get('site_web'):
                print(f"    Site: {admin['site_web']}")


def exemple_2_analyser_site():
    """Exemple 2: Analyse d'un site web"""
    print("\n" + "="*60)
    print("EXEMPLE 2: Analyse d'un site web")
    print("="*60)

    from scraper_sites import SiteAnalyzer

    # Sites à analyser
    test_sites = [
        "https://www.example-aj1.fr",
        "https://www.example-aj2.fr",
    ]

    # Création de l'analyseur
    analyzer = SiteAnalyzer(max_pages_per_site=30)

    # Analyse les sites
    for site in test_sites:
        print(f"\nAnalyse de {site}...")
        result = analyzer.analyze_site(site)

        print(f"  Accessible: {result['accessible']}")
        print(f"  Pages d'annonces trouvées: {len(result['pages_annonces'])}")

        if result['pages_annonces']:
            print("  URLs:")
            for page in result['pages_annonces']:
                print(f"    - {page}")


def exemple_3_extraire_annonces():
    """Exemple 3: Extraction d'annonces depuis une page"""
    print("\n" + "="*60)
    print("EXEMPLE 3: Extraction d'annonces")
    print("="*60)

    from scraper_annonces import AnnonceScraper

    # Page à scraper
    test_url = "https://www.example-aj.fr/annonces"

    # Création du scraper
    scraper = AnnonceScraper()

    # Extraction des annonces
    annonces = scraper.extract_annonces_from_page(test_url)

    print(f"\n✓ {len(annonces)} annonces extraites")

    # Affiche les détails
    if annonces:
        print("\nPremière annonce:")
        for key, value in annonces[0].items():
            print(f"  {key}: {value}")

        # Sauvegarde
        scraper.save_annonces(annonces, 'mes_annonces.json')
        scraper.export_to_csv(annonces, 'mes_annonces.csv')


def exemple_4_filtrer_annonces():
    """Exemple 4: Filtrage des annonces"""
    print("\n" + "="*60)
    print("EXEMPLE 4: Filtrage des annonces")
    print("="*60)

    from filters import AnnonceFilter

    # Annonces de test
    test_annonces = [
        {
            'titre': 'Société de développement web',
            'description': 'Entreprise spécialisée en développement web et applications mobiles avec 10 développeurs',
            'localisation': '75008 Paris',
            'prix': '250000',
            'secteur': 'Informatique'
        },
        {
            'titre': 'Cabinet de conseil en data',
            'description': 'Cabinet expert en data science, machine learning et intelligence artificielle',
            'localisation': '92100 Boulogne-Billancourt',
            'prix': '400000',
            'secteur': 'Conseil'
        },
        {
            'titre': 'Restaurant traditionnel',
            'description': 'Restaurant gastronomique avec clientèle fidèle',
            'localisation': '75015 Paris',
            'prix': '150000',
            'secteur': 'Restauration'
        },
        {
            'titre': 'Startup SaaS',
            'description': 'Plateforme SaaS de gestion cloud avec 50 clients',
            'localisation': '93100 Montreuil',
            'prix': '500000',
            'secteur': 'Technologie'
        },
        {
            'titre': 'Agence de communication',
            'description': 'Agence de communication traditionnelle',
            'localisation': '13001 Marseille',
            'prix': '120000',
            'secteur': 'Communication'
        }
    ]

    # Création du filtre
    filtre = AnnonceFilter()

    print(f"\nNombre total d'annonces: {len(test_annonces)}")

    # Filtre par secteur uniquement
    print("\n--- Filtre par secteur ---")
    filtered_sector = filtre.filter_by_sector(test_annonces)
    print(f"Annonces retenues: {len(filtered_sector)}")
    for annonce in filtered_sector:
        print(f"  ✓ {annonce['titre']}")

    # Filtre par localisation uniquement
    print("\n--- Filtre par localisation ---")
    filtered_location = filtre.filter_by_location(test_annonces)
    print(f"Annonces retenues: {len(filtered_location)}")
    for annonce in filtered_location:
        print(f"  ✓ {annonce['titre']} ({annonce['localisation']})")

    # Filtre par prix
    print("\n--- Filtre par prix (100k-300k) ---")
    filtered_price = filtre.filter_by_price(test_annonces, min_price=100000, max_price=300000)
    print(f"Annonces retenues: {len(filtered_price)}")
    for annonce in filtered_price:
        print(f"  ✓ {annonce['titre']} - {annonce['prix']}€")

    # Application de tous les filtres
    print("\n--- Application de TOUS les filtres ---")
    filtered_all = filtre.apply_all_filters(
        test_annonces,
        filter_sector=True,
        filter_location=True,
        min_price=100000,
        max_price=400000
    )

    print(f"\n✓ Résultat final: {len(filtered_all)}/{len(test_annonces)} annonces retenues")

    print("\nAnnonces finales:")
    for annonce in filtered_all:
        print(f"\n  Titre: {annonce['titre']}")
        print(f"  Secteur: {annonce['secteur']}")
        print(f"  Localisation: {annonce['localisation']}")
        print(f"  Prix: {annonce['prix']}€")

    # Statistiques
    print("\n--- Statistiques ---")
    stats = filtre.get_statistics(filtered_all)
    print(f"Total: {stats['total']}")
    print(f"Avec prix: {stats['with_price']}")
    print(f"Avec localisation: {stats['with_location']}")

    if stats['sectors']:
        print("\nSecteurs détectés:")
        for sector, count in stats['sectors'].items():
            print(f"  - {sector}: {count}")


def exemple_5_pipeline_complet():
    """Exemple 5: Pipeline complet avec données de test"""
    print("\n" + "="*60)
    print("EXEMPLE 5: Pipeline complet")
    print("="*60)

    import json
    import os
    from config import OUTPUT_DIR

    # Crée des données de test
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Crée une liste d'administrateurs de test
    test_admins = {
        'region': 'Île-de-France',
        'total': 2,
        'administrateurs': [
            {
                'nom': 'Cabinet Test 1',
                'site_web': 'https://www.example-aj1.fr',
                'adresse': '75008 Paris',
                'departement': '75'
            },
            {
                'nom': 'Cabinet Test 2',
                'site_web': 'https://www.example-aj2.fr',
                'adresse': '92100 Boulogne',
                'departement': '92'
            }
        ]
    }

    # Sauvegarde
    admin_file = os.path.join(OUTPUT_DIR, 'administrateurs_test.json')
    with open(admin_file, 'w', encoding='utf-8') as f:
        json.dump(test_admins, f, indent=2, ensure_ascii=False)

    print(f"✓ Données de test créées dans {admin_file}")
    print("\nPour tester le pipeline complet:")
    print("  python main.py --skip-phase1")


def exemple_6_personnalisation():
    """Exemple 6: Personnalisation des filtres"""
    print("\n" + "="*60)
    print("EXEMPLE 6: Personnalisation des filtres")
    print("="*60)

    from filters import AnnonceFilter

    # Création avec secteurs personnalisés
    custom_sectors = [
        'saas',
        'cloud',
        'intelligence artificielle',
        'fintech',
        'healthtech'
    ]

    custom_departments = ['75', '92']  # Seulement Paris et Hauts-de-Seine

    filtre = AnnonceFilter(
        target_sectors=custom_sectors,
        target_departments=custom_departments
    )

    # Annonces de test
    annonces = [
        {
            'titre': 'Plateforme SaaS de gestion',
            'description': 'SaaS cloud pour la gestion d\'entreprise',
            'localisation': '75002 Paris'
        },
        {
            'titre': 'Startup IA',
            'description': 'Solution d\'intelligence artificielle pour le retail',
            'localisation': '92200 Neuilly'
        }
    ]

    filtered = filtre.apply_all_filters(annonces)

    print(f"\n✓ {len(filtered)} annonces correspondent à vos critères personnalisés")
    for annonce in filtered:
        print(f"  - {annonce['titre']}")


def main():
    """Lance tous les exemples"""
    print("\n" + "="*60)
    print("EXEMPLES D'UTILISATION DU SCRAPER AJ")
    print("="*60)

    exemples = [
        ("Scraper d'annuaire", exemple_1_scraper_annuaire),
        ("Analyse de sites", exemple_2_analyser_site),
        ("Extraction d'annonces", exemple_3_extraire_annonces),
        ("Filtrage d'annonces", exemple_4_filtrer_annonces),
        ("Pipeline complet", exemple_5_pipeline_complet),
        ("Personnalisation", exemple_6_personnalisation),
    ]

    print("\nExemples disponibles:")
    for i, (nom, _) in enumerate(exemples, 1):
        print(f"  {i}. {nom}")

    print("\n" + "-"*60)

    # Exécute les exemples qui ne nécessitent pas de réseau
    print("\nExécution des exemples de démonstration...")

    # Exemple 4: Filtrage (ne nécessite pas de réseau)
    exemple_4_filtrer_annonces()

    # Exemple 5: Pipeline (création de données de test)
    exemple_5_pipeline_complet()

    # Exemple 6: Personnalisation
    exemple_6_personnalisation()

    print("\n" + "="*60)
    print("Pour tester les exemples avec scraping réel:")
    print("  - Exemple 1: exemple_1_scraper_annuaire()")
    print("  - Exemple 2: exemple_2_analyser_site()")
    print("  - Exemple 3: exemple_3_extraire_annonces()")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
