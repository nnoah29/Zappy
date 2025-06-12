from typing import Dict, Optional
import logging
from core.protocol import ZappyProtocol
from managers.inventory import Inventory

class ResourceManager:
    """Gère les ressources et l'inventaire du joueur."""
    
    # Ressources nécessaires pour chaque niveau
    ELEVATION_REQUIREMENTS = {
        1: {'players': 1, 'linemate': 1, 'deraumere': 0, 'sibur': 0, 'mendiane': 0, 'phiras': 0, 'thystame': 0},
        2: {'players': 2, 'linemate': 1, 'deraumere': 1, 'sibur': 1, 'mendiane': 0, 'phiras': 0, 'thystame': 0},
        3: {'players': 2, 'linemate': 2, 'deraumere': 0, 'sibur': 1, 'mendiane': 0, 'phiras': 2, 'thystame': 0},
        4: {'players': 4, 'linemate': 1, 'deraumere': 1, 'sibur': 2, 'mendiane': 0, 'phiras': 1, 'thystame': 0},
        5: {'players': 4, 'linemate': 1, 'deraumere': 2, 'sibur': 1, 'mendiane': 3, 'phiras': 0, 'thystame': 0},
        6: {'players': 6, 'linemate': 1, 'deraumere': 2, 'sibur': 3, 'mendiane': 0, 'phiras': 1, 'thystame': 0},
        7: {'players': 6, 'linemate': 2, 'deraumere': 2, 'sibur': 2, 'mendiane': 2, 'phiras': 2, 'thystame': 1}
    }

    def __init__(self, protocol: ZappyProtocol):
        """Initialise le gestionnaire de ressources.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
        """
        self.protocol = protocol
        self.logger = logging.getLogger(__name__)
        self.inventory = Inventory()
        self.food_time = 126
        self.last_food_time = 0

    def update_inventory(self) -> None:
        """Met à jour l'inventaire du joueur."""
        try:
            response = self.protocol.inventory()
            if response:
                # Parse la réponse du serveur
                items = response.strip('[]').split(',')
                for item in items:
                    if item.strip():
                        name, count = item.strip().split()
                        self.inventory.items[name] = int(count)
                self.logger.debug(f"Inventaire mis à jour: {self.inventory.items}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'inventaire: {str(e)}")

    def get_food_count(self) -> int:
        """Récupère le nombre de nourriture dans l'inventaire.
        
        Returns:
            int: Nombre de nourriture
        """
        return self.inventory.get('food')

    def get_resource_count(self, resource: str) -> int:
        """Récupère le nombre d'une ressource spécifique.
        
        Args:
            resource (str): Nom de la ressource
            
        Returns:
            int: Nombre de la ressource
        """
        return self.inventory.get(resource)

    def get_needed_resource(self, level: int) -> Optional[str]:
        """Retourne la ressource la plus prioritaire à collecter.
        
        Args:
            level (int): Niveau actuel du joueur
            
        Returns:
            Optional[str]: Nom de la ressource à collecter, None si aucune n'est nécessaire
        """
        if level >= 8:
            return None

        # Priorité : nourriture si moins de 5 unités
        if self.inventory.get('food') < 5:
            return "food"
            
        # Ensuite, priorité aux ressources manquantes
        requirements = self.ELEVATION_REQUIREMENTS[level]
        for resource in ['linemate', 'deraumere', 'sibur', 'mendiane', 'phiras', 'thystame']:
            if self.inventory.get(resource) < requirements[resource]:
                return resource
        return None

    def need_resources(self, level: int) -> bool:
        """Vérifie si des ressources sont nécessaires pour le niveau actuel.
        
        Args:
            level (int): Niveau actuel du joueur
            
        Returns:
            bool: True si des ressources sont nécessaires
        """
        if level >= 8:  # Niveau maximum
            return False

        requirements = self.ELEVATION_REQUIREMENTS[level]
        for resource, count in requirements.items():
            if resource == 'players':
                continue
            if self.inventory.get(resource) < count:
                return True
        return False

    def can_level_up(self, level: int) -> bool:
        """Vérifie si le joueur peut monter de niveau.
        
        Args:
            level (int): Niveau actuel du joueur
            
        Returns:
            bool: True si le joueur peut monter de niveau
        """
        if level >= 8:
            return False

        requirements = self.ELEVATION_REQUIREMENTS[level]
        for resource, count in requirements.items():
            if resource == 'players':
                continue
            if self.inventory.get(resource) < count:
                return False
        # Vérifier la nourriture
        if self.inventory.get('food') < 5:  # Garder une réserve de nourriture
            return False
        return True

    def update_food(self, current_time: float) -> bool:
        """Met à jour l'état de la nourriture.
        
        Args:
            current_time (float): Temps actuel
            
        Returns:
            bool: True si le joueur est toujours en vie
        """
        if current_time - self.last_food_time >= self.food_time:
            if not self.inventory.remove('food'):
                self.logger.error("Plus de nourriture, mort du joueur")
                return False
            self.last_food_time = current_time
        return True

    def add_food(self, amount: int = 1) -> None:
        """Ajoute de la nourriture à l'inventaire.
        
        Args:
            amount (int): Quantité de nourriture à ajouter
        """
        self.inventory.add('food', amount)
        self.logger.debug(f"Nourriture ajoutée, unités: {self.inventory.get('food')}")

    def get_elevation_requirements(self, level: int) -> Dict[str, int]:
        """Retourne les conditions d'élévation pour le niveau actuel.
        
        Args:
            level (int): Niveau actuel du joueur
            
        Returns:
            Dict[str, int]: Conditions d'élévation
        """
        return self.ELEVATION_REQUIREMENTS[level] 