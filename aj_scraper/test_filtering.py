#!/usr/bin/env python3
"""
Test du système de filtrage avec les données de test
"""

import json
import os
from filters import AnnonceFilter
from scraper_annonces import AnnonceScraper

def test_filtering():
    """Teste le filtrage des annonces avec les données de test"""

    # Charge les annonces brutes
    with open('output/annonces_brutes.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        annonces_brutes = data['annonces']

    print("="*60)
    print("TEST DU SYSTÈME DE FILTRAGE")
    print("="*60)
    print(f"\nNombre d'annonces brutes: {len(annonces_brutes)}")

    # Affiche toutes les annonces
    print("\n--- ANNONCES BRUTES ---\n")
    for i, annonce in enumerate(annonces_brutes, 1):
        print(f"{i}. {annonce['titre']}")
        print(f"   Secteur: {annonce.get('secteur', 'N/A')}")
        print(f"   Localisation: {annonce.get('localisation', 'N/A')}")
        print(f"   Prix: {annonce.get('prix', 'N/A')}€")
        print()

    # Applique les filtres
    filtre = AnnonceFilter()
    annonces_filtrees = filtre.apply_all_filters(
        annonces_brutes,
        filter_sector=True,
        filter_location=True
    )

    print("\n" + "="*60)
    print("RÉSULTATS DU FILTRAGE")
    print("="*60)
    print(f"\nAnnonces retenues: {len(annonces_filtrees)}/{len(annonces_brutes)}")

    print("\n--- ANNONCES FILTRÉES (secteur tech/data/conseil en IDF) ---\n")
    for i, annonce in enumerate(annonces_filtrees, 1):
        print(f"{i}. {annonce['titre']}")
        print(f"   Description: {annonce['description'][:100]}...")
        print(f"   Secteur: {annonce.get('secteur', 'N/A')}")
        print(f"   Localisation: {annonce.get('localisation', 'N/A')}")
        print(f"   Prix: {annonce.get('prix', 'N/A')}€")
        print(f"   Contact: {annonce.get('contact', 'N/A')}")
        print(f"   URL: {annonce.get('url_details', 'N/A')}")
        print()

    # Sauvegarde les résultats
    scraper = AnnonceScraper()
    scraper.save_annonces(annonces_filtrees, 'annonces_filtrees.json')
    scraper.export_to_csv(annonces_filtrees, 'annonces_filtrees.csv')

    # Statistiques
    stats = filtre.get_statistics(annonces_filtrees)
    print("="*60)
    print("STATISTIQUES")
    print("="*60)
    print(f"Total: {stats['total']}")
    print(f"Avec prix: {stats['with_price']}")
    print(f"Avec localisation: {stats['with_location']}")
    print(f"Avec contact: {stats['with_contact']}")

    if stats['sectors']:
        print(f"\nSecteurs détectés:")
        for sector, count in sorted(stats['sectors'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {sector}: {count}")

    if stats['departments']:
        print(f"\nDépartements:")
        for dept, count in sorted(stats['departments'].items()):
            print(f"  - {dept}: {count}")

    print("\n✓ Résultats sauvegardés dans:")
    print("  - output/annonces_filtrees.json")
    print("  - output/annonces_filtrees.csv")
    print()

if __name__ == "__main__":
    test_filtering()
