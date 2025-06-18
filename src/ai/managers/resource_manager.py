from typing import Dict, Optional
import logging
from core.protocol import ZappyProtocol
from managers.inventory_manager import InventoryManager
import time
from models.player import Player
from models.map import Map

class ResourceManager:
    """Gère les ressources et l'inventaire du joueur."""
    
    ELEVATION_REQUIREMENTS = {
        1: {'players': 1, 'linemate': 1, 'deraumere': 0, 'sibur': 0, 'mendiane': 0, 'phiras': 0, 'thystame': 0},
        2: {'players': 2, 'linemate': 1, 'deraumere': 1, 'sibur': 1, 'mendiane': 0, 'phiras': 0, 'thystame': 0},
        3: {'players': 2, 'linemate': 2, 'deraumere': 0, 'sibur': 1, 'mendiane': 0, 'phiras': 2, 'thystame': 0},
        4: {'players': 4, 'linemate': 1, 'deraumere': 1, 'sibur': 2, 'mendiane': 0, 'phiras': 1, 'thystame': 0},
        5: {'players': 4, 'linemate': 1, 'deraumere': 2, 'sibur': 1, 'mendiane': 3, 'phiras': 0, 'thystame': 0},
        6: {'players': 6, 'linemate': 1, 'deraumere': 2, 'sibur': 3, 'mendiane': 0, 'phiras': 1, 'thystame': 0},
        7: {'players': 6, 'linemate': 2, 'deraumere': 2, 'sibur': 2, 'mendiane': 2, 'phiras': 2, 'thystame': 1}
    }

    def __init__(self, protocol: ZappyProtocol, player: Player, map: Map, logger: logging.Logger):
        """Initialise le gestionnaire de ressources.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            player (Player): Joueur contrôlé
            map (Map): Carte du jeu
            logger (Logger): Logger pour les messages
        """
        self.protocol = protocol
        self.player = player
        self.map = map
        self.logger = logger
        self.inventory = InventoryManager(protocol, player, logger)
        self.food_time = 126
        self.last_food_time = 0
        self.resources = {
            'food': 0,
            'linemate': 0,
            'deraumere': 0,
            'sibur': 0,
            'mendiane': 0,
            'phiras': 0,
            'thystame': 0
        }
        self.last_inventory_update = 0
        self.inventory_cooldown = 1  # Temps entre chaque mise à jour de l'inventaire

    def update_inventory(self) -> bool:
        """Met à jour l'inventaire du joueur.
        
        Returns:
            bool: True si la mise à jour a réussi
        """
        try:
            response = self.protocol.inventory()
            self.resources = self._parse_inventory(response)
            self.last_inventory_update = time.time()
            self.logger.debug(f"Inventaire mis à jour: {self.resources}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'inventaire: {str(e)}")
            return False

    def _parse_inventory(self, response: str) -> Dict[str, int]:
        """Parse la réponse de la commande Inventory.
        
        Format: [food n, linemate n, deraumere n, sibur n, mendiane n, phiras n, thystame n]
        
        Args:
            response (str): Réponse du serveur
            
        Returns:
            Dict[str, int]: Inventaire du joueur
        """
        try:
            response = response.strip('[]')
            resources = response.split(',')
            
            inventory = {}
            for resource in resources:
                name, count = resource.strip().split()
                inventory[name] = int(count)
                
            return inventory
        except Exception as e:
            self.logger.error(f"Erreur lors du parsing de l'inventaire: {str(e)}")
            raise

    def get_food_count(self) -> int:
        """Récupère le nombre de nourriture dans l'inventaire.
        
        Returns:
            int: Nombre de nourriture
        """
        return self.inventory.get('food')

    def get_resource_count(self, resource_type: str) -> int:
        """Récupère le nombre d'une ressource.
        
        Args:
            resource_type (str): Type de ressource
            
        Returns:
            int: Nombre de ressources
        """
        return self.resources.get(resource_type, 0)

    def get_needed_resource(self, level: int) -> Optional[str]:
        """Retourne la ressource la plus prioritaire à collecter.
        
        Args:
            level (int): Niveau actuel du joueur
            
        Returns:
            Optional[str]: Nom de la ressource à collecter, None si aucune n'est nécessaire
        """
        if level >= 8:
            return None

        if self.inventory.get('food') < 5:
            return "food"
            
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
        if level >= 8:
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
        if self.inventory.get('food') < 5:
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

    def has_resources_for_elevation(self, level: int) -> bool:
        """Vérifie si le joueur a les ressources nécessaires pour l'élévation.
        
        Args:
            level (int): Niveau actuel
            
        Returns:
            bool: True si le joueur a les ressources nécessaires
        """
        
        if level not in self.ELEVATION_REQUIREMENTS:
            return False
            
        for resource, count in self.ELEVATION_REQUIREMENTS[level].items():
            if self.get_resource_count(resource) < count:
                return False
                
        return True

    def can_update_inventory(self) -> bool:
        """Vérifie si l'inventaire peut être mis à jour.
        
        Returns:
            bool: True si l'inventaire peut être mis à jour
        """
        return time.time() - self.last_inventory_update >= self.inventory_cooldown 