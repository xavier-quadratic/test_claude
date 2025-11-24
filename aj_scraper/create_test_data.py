#!/usr/bin/env python3
"""
Script pour créer des données de test réalistes
Simule un scraping réussi des 4 sites d'administrateurs judiciaires
"""

import json
import os

# Données de test réalistes pour simuler un scraping réussi
sites_analysis = [
    {
        "base_url": "http://arva.fr/",
        "accessible": True,
        "pages_annonces": [
            "http://arva.fr/ventes-en-cours",
            "http://arva.fr/annonces"
        ],
        "structure_detected": {
            "url": "http://arva.fr/ventes-en-cours",
            "has_list": False,
            "has_table": True,
            "has_cards": False,
            "container_class": None,
            "item_tag": "tr",
            "pagination": True
        },
        "error": None
    },
    {
        "base_url": "https://aj-2m.com/",
        "accessible": True,
        "pages_annonces": [
            "https://aj-2m.com/annonces",
            "https://aj-2m.com/ventes-entreprises"
        ],
        "structure_detected": {
            "url": "https://aj-2m.com/annonces",
            "has_list": False,
            "has_table": False,
            "has_cards": True,
            "container_class": "annonce-card",
            "item_tag": "div",
            "pagination": False
        },
        "error": None
    },
    {
        "base_url": "https://ihdf.aillink.fr/accueil",
        "accessible": True,
        "pages_annonces": [
            "https://ihdf.aillink.fr/annonces-judiciaires",
            "https://ihdf.aillink.fr/cessions"
        ],
        "structure_detected": {
            "url": "https://ihdf.aillink.fr/annonces-judiciaires",
            "has_list": True,
            "has_table": False,
            "has_cards": False,
            "container_class": None,
            "item_tag": "li",
            "pagination": True
        },
        "error": None
    },
    {
        "base_url": "https://www.actismj.fr/accueil",
        "accessible": True,
        "pages_annonces": [
            "https://www.actismj.fr/ventes",
            "https://www.actismj.fr/liquidations"
        ],
        "structure_detected": {
            "url": "https://www.actismj.fr/ventes",
            "has_list": False,
            "has_table": True,
            "has_cards": False,
            "container_class": None,
            "item_tag": "tr",
            "pagination": False
        },
        "error": None
    }
]

# Annonces de test réalistes
annonces_brutes = [
    {
        "titre": "Société de développement web et applications mobiles",
        "description": "Cession d'une société spécialisée dans le développement web et mobile. Équipe de 8 développeurs. Portfolio clients prestigieux. Technologies : React, Node.js, React Native. CA annuel : 850K€. Située à Paris 8ème.",
        "entreprise": "WebTech Solutions SAS",
        "secteur": "Informatique",
        "localisation": "75008 Paris",
        "prix": "420000",
        "date_publication": "15/11/2025",
        "date_limite": "15/12/2025",
        "reference": "AJ-2025-4782",
        "url_details": "https://aj-2m.com/annonces/4782",
        "contact": "aj2m@administrateur.fr",
        "scraped_at": "2025-11-24T11:00:00"
    },
    {
        "titre": "Cabinet de conseil en data science et IA",
        "description": "Cabinet expert en data science, machine learning et intelligence artificielle. Équipe de 5 data scientists. Clients grands comptes. Spécialités : BI, prédictif, NLP. CA : 600K€.",
        "entreprise": "Data Insights SARL",
        "secteur": "Conseil / Data",
        "localisation": "92100 Boulogne-Billancourt",
        "prix": "350000",
        "date_publication": "18/11/2025",
        "date_limite": "18/12/2025",
        "reference": "AJ-2025-4801",
        "url_details": "http://arva.fr/ventes-en-cours/4801",
        "contact": "01 45 67 89 12",
        "scraped_at": "2025-11-24T11:05:00"
    },
    {
        "titre": "Plateforme SaaS de gestion de projet",
        "description": "Éditeur de logiciel SaaS B2B pour la gestion de projets et collaboration d'équipe. 150 clients actifs. MRR : 25K€. Stack technique moderne (Vue.js, Python, PostgreSQL). Locaux à Montreuil.",
        "entreprise": "ProjectHub SAS",
        "secteur": "Technologie / SaaS",
        "localisation": "93100 Montreuil",
        "prix": "580000",
        "date_publication": "20/11/2025",
        "date_limite": "20/01/2026",
        "reference": "IH-2025-1523",
        "url_details": "https://ihdf.aillink.fr/annonces-judiciaires/1523",
        "contact": "contact@ihdf-aj.fr",
        "scraped_at": "2025-11-24T11:10:00"
    },
    {
        "titre": "Agence de conseil en transformation digitale",
        "description": "Cabinet de conseil spécialisé en transformation digitale et innovation. Accompagnement de PME et ETI. Équipe de 12 consultants seniors. Bureaux Paris 17ème. CA : 1.2M€.",
        "entreprise": "Digital Transform Consulting",
        "secteur": "Conseil",
        "localisation": "75017 Paris",
        "prix": "680000",
        "date_publication": "22/11/2025",
        "date_limite": "22/12/2025",
        "reference": "ACT-2025-9341",
        "url_details": "https://www.actismj.fr/ventes/9341",
        "contact": "actismj@notaires.fr",
        "scraped_at": "2025-11-24T11:15:00"
    },
    {
        "titre": "Start-up fintech - plateforme de paiement",
        "description": "Solution fintech de paiement en ligne pour e-commerce. API moderne, SDK multi-langages. Base de 80 marchands actifs. Technologies : Node.js, Stripe, AWS. Équipe de 6 personnes.",
        "entreprise": "PayFlow Tech",
        "secteur": "Fintech / Technologie",
        "localisation": "92200 Neuilly-sur-Seine",
        "prix": "450000",
        "date_publication": "10/11/2025",
        "date_limite": "10/12/2025",
        "reference": "AJ-2025-4690",
        "url_details": "https://aj-2m.com/annonces/4690",
        "contact": "admin@aj-2m.fr",
        "scraped_at": "2025-11-24T11:20:00"
    },
    {
        "titre": "Restaurant gastronomique",
        "description": "Restaurant traditionnel 80 couverts, clientèle fidèle, cuisine française.",
        "entreprise": "Le Gourmet",
        "secteur": "Restauration",
        "localisation": "75015 Paris",
        "prix": "180000",
        "date_publication": "05/11/2025",
        "reference": "AJ-2025-4512",
        "url_details": "http://arva.fr/ventes-en-cours/4512",
        "contact": "arva@aj.fr",
        "scraped_at": "2025-11-24T11:25:00"
    },
    {
        "titre": "Agence immobilière traditionnelle",
        "description": "Agence immobilière établie depuis 15 ans, portefeuille de 200 biens.",
        "entreprise": "Immo Plus",
        "secteur": "Immobilier",
        "localisation": "13001 Marseille",
        "prix": "220000",
        "date_publication": "12/11/2025",
        "reference": "EXT-2025-3301",
        "url_details": "http://externe.fr/annonces/3301",
        "contact": "externe@aj.fr",
        "scraped_at": "2025-11-24T11:30:00"
    }
]

def create_test_data():
    """Crée les fichiers de test dans le dossier output"""

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Sauvegarde sites_analysis
    with open(os.path.join(output_dir, "sites_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(sites_analysis, f, indent=2, ensure_ascii=False)
    print(f"✓ Créé: {output_dir}/sites_analysis.json")

    # Sauvegarde annonces_brutes
    data_brutes = {
        "total": len(annonces_brutes),
        "extracted_at": "2025-11-24T11:00:00",
        "annonces": annonces_brutes
    }
    with open(os.path.join(output_dir, "annonces_brutes.json"), "w", encoding="utf-8") as f:
        json.dump(data_brutes, f, indent=2, ensure_ascii=False)
    print(f"✓ Créé: {output_dir}/annonces_brutes.json")

    print("\n" + "="*60)
    print("DONNÉES DE TEST CRÉÉES")
    print("="*60)
    print(f"\nNombre de sites analysés: {len(sites_analysis)}")
    print(f"Sites accessibles: {sum(1 for s in sites_analysis if s['accessible'])}")
    print(f"Pages d'annonces trouvées: {sum(len(s['pages_annonces']) for s in sites_analysis)}")
    print(f"\nNombre d'annonces: {len(annonces_brutes)}")
    print(f"  - Secteur tech/data/conseil: {sum(1 for a in annonces_brutes if any(k in a['description'].lower() for k in ['développement', 'data', 'conseil', 'saas', 'digital', 'tech']))}")
    print(f"  - Autres secteurs: {sum(1 for a in annonces_brutes if not any(k in a['description'].lower() for k in ['développement', 'data', 'conseil', 'saas', 'digital', 'tech']))}")

    print("\nLancez maintenant la phase 3 de filtrage:")
    print("  python main.py --skip-phase1 --skip-phase2")
    print()

if __name__ == "__main__":
    create_test_data()
