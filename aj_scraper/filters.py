"""
Module de filtrage des annonces par secteur et région
"""

import logging
from typing import List, Dict, Set
import re

from config import TARGET_SECTORS, TARGET_DEPARTMENTS, TARGET_REGION

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnnonceFilter:
    """
    Filtre les annonces selon différents critères

    Permet de filtrer par:
    - Secteur d'activité (informatique, data, conseil, etc.)
    - Région/département
    - Mots-clés personnalisés
    """

    def __init__(self, target_sectors: List[str] = None, target_departments: List[str] = None):
        """
        Initialise le filtre

        Args:
            target_sectors: Liste des secteurs cibles (utilise config par défaut si None)
            target_departments: Liste des départements cibles (utilise config par défaut si None)
        """
        self.target_sectors = target_sectors or TARGET_SECTORS
        self.target_departments = target_departments or TARGET_DEPARTMENTS

        # Normalise les secteurs en minuscules pour la comparaison
        self.target_sectors_lower = [s.lower() for s in self.target_sectors]

    def filter_by_sector(self, annonces: List[Dict]) -> List[Dict]:
        """
        Filtre les annonces par secteur d'activité

        Args:
            annonces: Liste des annonces à filtrer

        Returns:
            Liste des annonces correspondant aux secteurs cibles
        """
        filtered = []

        for annonce in annonces:
            if self._matches_sector(annonce):
                filtered.append(annonce)
                logger.debug(f"✓ Annonce retenue: {annonce.get('titre', 'N/A')}")

        logger.info(f"Filtrage par secteur: {len(filtered)}/{len(annonces)} annonces retenues")
        return filtered

    def _matches_sector(self, annonce: Dict) -> bool:
        """
        Vérifie si une annonce correspond aux secteurs cibles

        Args:
            annonce: Dictionnaire de l'annonce

        Returns:
            True si l'annonce correspond
        """
        # Construit un texte de recherche à partir de l'annonce
        search_text = " ".join([
            str(annonce.get('titre', '')),
            str(annonce.get('description', '')),
            str(annonce.get('secteur', '')),
            str(annonce.get('entreprise', ''))
        ]).lower()

        # Vérifie si un des secteurs cibles est présent
        for sector in self.target_sectors_lower:
            if sector in search_text:
                logger.debug(f"  Secteur trouvé: {sector}")
                return True

        # Vérification par mots-clés additionnels
        tech_keywords = [
            'it', 'tech', 'logiciel', 'software', 'application',
            'site web', 'webapp', 'plateforme', 'api', 'erp', 'crm',
            'saas', 'paas', 'cloud', 'database', 'développeur',
            'programmer', 'data scientist', 'analyste'
        ]

        for keyword in tech_keywords:
            if keyword in search_text:
                logger.debug(f"  Mot-clé tech trouvé: {keyword}")
                return True

        return False

    def filter_by_location(self, annonces: List[Dict]) -> List[Dict]:
        """
        Filtre les annonces par localisation (région/département)

        Args:
            annonces: Liste des annonces à filtrer

        Returns:
            Liste des annonces dans la région cible
        """
        filtered = []

        for annonce in annonces:
            if self._matches_location(annonce):
                filtered.append(annonce)
                logger.debug(f"✓ Localisation OK: {annonce.get('titre', 'N/A')}")

        logger.info(f"Filtrage par localisation: {len(filtered)}/{len(annonces)} annonces retenues")
        return filtered

    def _matches_location(self, annonce: Dict) -> bool:
        """
        Vérifie si une annonce est dans la région cible

        Args:
            annonce: Dictionnaire de l'annonce

        Returns:
            True si l'annonce est dans la région
        """
        location = str(annonce.get('localisation', '')).lower()

        # Vérifie les codes postaux des départements IDF
        for dept in self.target_departments:
            # Cherche des codes postaux commençant par le numéro du département
            if re.search(rf'\b{dept}\d{{3}}\b', location):
                logger.debug(f"  Code postal trouvé: {dept}xxx")
                return True

        # Vérifie les noms de région/département
        region_keywords = [
            'paris', 'île-de-france', 'ile-de-france', 'idf',
            'seine-et-marne', 'yvelines', 'essonne',
            'hauts-de-seine', 'seine-saint-denis',
            'val-de-marne', 'val-d\'oise'
        ]

        for keyword in region_keywords:
            if keyword in location:
                logger.debug(f"  Région trouvée: {keyword}")
                return True

        # Si pas de localisation spécifiée, on garde l'annonce par défaut
        # (car elle vient déjà d'un administrateur judiciaire en IDF)
        if not location or location == 'none':
            return True

        return False

    def filter_by_keywords(self, annonces: List[Dict], keywords: List[str], exclude: bool = False) -> List[Dict]:
        """
        Filtre les annonces par mots-clés personnalisés

        Args:
            annonces: Liste des annonces à filtrer
            keywords: Liste des mots-clés
            exclude: Si True, exclut les annonces contenant ces mots-clés

        Returns:
            Liste des annonces filtrées
        """
        filtered = []
        keywords_lower = [k.lower() for k in keywords]

        for annonce in annonces:
            search_text = " ".join([
                str(annonce.get('titre', '')),
                str(annonce.get('description', ''))
            ]).lower()

            has_keyword = any(keyword in search_text for keyword in keywords_lower)

            if (has_keyword and not exclude) or (not has_keyword and exclude):
                filtered.append(annonce)

        action = "exclu" if exclude else "inclus"
        logger.info(f"Filtrage par mots-clés ({action}): {len(filtered)}/{len(annonces)} annonces retenues")
        return filtered

    def filter_by_price(self, annonces: List[Dict], min_price: int = None, max_price: int = None) -> List[Dict]:
        """
        Filtre les annonces par prix

        Args:
            annonces: Liste des annonces à filtrer
            min_price: Prix minimum
            max_price: Prix maximum

        Returns:
            Liste des annonces dans la fourchette de prix
        """
        filtered = []

        for annonce in annonces:
            prix_str = annonce.get('prix')
            if not prix_str:
                # Si pas de prix, on garde l'annonce
                filtered.append(annonce)
                continue

            try:
                # Convertit le prix en nombre
                prix = int(re.sub(r'[^\d]', '', str(prix_str)))

                if min_price and prix < min_price:
                    continue
                if max_price and prix > max_price:
                    continue

                filtered.append(annonce)

            except (ValueError, TypeError):
                # Si conversion échoue, garde l'annonce
                filtered.append(annonce)
                continue

        logger.info(f"Filtrage par prix: {len(filtered)}/{len(annonces)} annonces retenues")
        return filtered

    def apply_all_filters(self, annonces: List[Dict],
                         filter_sector: bool = True,
                         filter_location: bool = True,
                         custom_keywords: List[str] = None,
                         exclude_keywords: List[str] = None,
                         min_price: int = None,
                         max_price: int = None) -> List[Dict]:
        """
        Applique tous les filtres en cascade

        Args:
            annonces: Liste des annonces à filtrer
            filter_sector: Appliquer le filtre par secteur
            filter_location: Appliquer le filtre par localisation
            custom_keywords: Mots-clés additionnels à inclure
            exclude_keywords: Mots-clés à exclure
            min_price: Prix minimum
            max_price: Prix maximum

        Returns:
            Liste des annonces filtrées
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"APPLICATION DES FILTRES")
        logger.info(f"{'='*60}")
        logger.info(f"Nombre initial d'annonces: {len(annonces)}")

        result = annonces

        # Filtre par secteur
        if filter_sector:
            result = self.filter_by_sector(result)

        # Filtre par localisation
        if filter_location:
            result = self.filter_by_location(result)

        # Filtre par mots-clés personnalisés
        if custom_keywords:
            result = self.filter_by_keywords(result, custom_keywords, exclude=False)

        # Exclusion par mots-clés
        if exclude_keywords:
            result = self.filter_by_keywords(result, exclude_keywords, exclude=True)

        # Filtre par prix
        if min_price or max_price:
            result = self.filter_by_price(result, min_price, max_price)

        logger.info(f"\n{'='*60}")
        logger.info(f"RÉSULTAT FINAL: {len(result)}/{len(annonces)} annonces retenues")
        logger.info(f"{'='*60}\n")

        return result

    def get_statistics(self, annonces: List[Dict]) -> Dict:
        """
        Calcule des statistiques sur les annonces

        Args:
            annonces: Liste des annonces

        Returns:
            Dictionnaire de statistiques
        """
        stats = {
            'total': len(annonces),
            'with_price': 0,
            'with_location': 0,
            'with_contact': 0,
            'sectors': {},
            'departments': {}
        }

        for annonce in annonces:
            if annonce.get('prix'):
                stats['with_price'] += 1

            if annonce.get('localisation'):
                stats['with_location'] += 1

            if annonce.get('contact'):
                stats['with_contact'] += 1

            # Compte les secteurs détectés
            for sector in self.target_sectors_lower:
                search_text = str(annonce.get('description', '')).lower()
                if sector in search_text:
                    stats['sectors'][sector] = stats['sectors'].get(sector, 0) + 1

            # Compte les départements
            location = str(annonce.get('localisation', ''))
            for dept in self.target_departments:
                if dept in location:
                    stats['departments'][dept] = stats['departments'].get(dept, 0) + 1

        return stats


if __name__ == "__main__":
    # Test avec des annonces d'exemple
    test_annonces = [
        {
            'titre': 'Entreprise de développement web à céder',
            'description': 'Société spécialisée en développement web et mobile, 5 développeurs',
            'localisation': '75008 Paris',
            'prix': '150000'
        },
        {
            'titre': 'Cabinet de conseil en stratégie',
            'description': 'Cabinet de conseil en transformation digitale et data',
            'localisation': '92100 Boulogne-Billancourt',
            'prix': '300000'
        },
        {
            'titre': 'Boulangerie artisanale',
            'description': 'Boulangerie traditionnelle, clientèle fidèle',
            'localisation': '13001 Marseille',
            'prix': '80000'
        },
    ]

    filtre = AnnonceFilter()

    print("Test du système de filtrage")
    print("=" * 60)

    # Applique les filtres
    filtered = filtre.apply_all_filters(
        test_annonces,
        filter_sector=True,
        filter_location=True
    )

    print("\nAnnonces retenues:")
    for annonce in filtered:
        print(f"  - {annonce['titre']}")
        print(f"    Localisation: {annonce['localisation']}")
        print(f"    Prix: {annonce['prix']}€")

    # Statistiques
    stats = filtre.get_statistics(filtered)
    print("\nStatistiques:")
    print(f"  Total: {stats['total']}")
    print(f"  Avec prix: {stats['with_price']}")
    print(f"  Avec localisation: {stats['with_location']}")
