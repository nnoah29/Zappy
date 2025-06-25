import logging
from typing import Tuple, Dict
from core.protocol import ZappyProtocol
from managers.inventory_manager import InventoryManager

class Player:
    """Représente un joueur dans le jeu."""

    def __init__(self, id: int, team: str, x: int, y: int, protocol: ZappyProtocol, logger: logging.Logger):
        """Initialise un joueur.
        
        Args:
            id (int): Identifiant du joueur
            team (str): Nom de l'équipe
            x (int): Position X initiale
            y (int): Position Y initiale
            protocol (ZappyProtocol): Protocole de communication
            logger (Logger): Logger pour les messages
        """
        self.id = id
        self.team = team
        self.position = (x, y)
        self.direction = 0
        self.level = 1
        self.inventory = InventoryManager(protocol, self, logger)
        self.logger = logger
        # self.logger.info(f"player {id} created on team {team} at {self.position}")

    @property
    def x(self) -> int:
        """Récupère la coordonnée X de la position.
        
        Returns:
            int: Coordonnée X
        """
        return self.position[0]

    @property
    def y(self) -> int:
        """Récupère la coordonnée Y de la position.
        
        Returns:
            int: Coordonnée Y
        """
        return self.position[1]

    def get_position(self) -> Tuple[int, int]:
        """Récupère la position actuelle du joueur.
        
        Returns:
            Tuple[int, int]: Position (x, y)
        """
        return self.position

    def set_position(self, x: int, y: int) -> None:
        """Met à jour la position du joueur.
        
        Args:
            x (int): Nouvelle position X
            y (int): Nouvelle position Y
        """
        self.position = (x, y)
        self.logger.debug(f"Position mise à jour: {self.position}")

    def get_direction(self) -> int:
        """Récupère la direction actuelle du joueur.
        
        Returns:
            int: Direction (0: Nord, 1: Est, 2: Sud, 3: Ouest)
        """
        return self.direction

    def set_direction(self, direction: int) -> None:
        """Met à jour la direction du joueur.
        
        Args:
            direction (int): Nouvelle direction
        """
        self.direction = direction % 4
        self.logger.debug(f"Direction mise à jour: {self.direction}")

    def get_level(self) -> int:
        """Récupère le niveau actuel du joueur.
        
        Returns:
            int: Niveau
        """
        return self.level

    def set_level(self, level: int) -> None:
        """Met à jour le niveau du joueur.
        
        Args:
            level (int): Nouveau niveau
        """
        self.level = level
        self.logger.info(f"Niveau mis à jour: {self.level}")

    def get_inventory(self) -> Dict[str, int]:
        """Récupère l'inventaire du joueur.
        
        Returns:
            Dict[str, int]: Inventaire
        """
        return self.inventory

    def set_inventory(self, inventory: Dict[str, int]) -> None:
        """Met à jour l'inventaire du joueur.
        
        Args:
            inventory (Dict[str, int]): Nouvel inventaire
        """
        self.inventory = inventory
        self.logger.debug(f"Inventaire mis à jour: {self.inventory}")

    def get_resource_count(self, resource: str) -> int:
        """Récupère le nombre d'une ressource.
        
        Args:
            resource (str): Type de ressource
            
        Returns:
            int: Nombre de ressources
        """
        return self.inventory.get(resource, 0)

    def add_resource(self, resource: str, count: int = 1) -> None:
        """Ajoute des ressources à l'inventaire.
        
        Args:
            resource (str): Type de ressource
            count (int): Nombre à ajouter
        """
        self.inventory[resource] = self.inventory.get(resource, 0) + count
        self.logger.debug(f"Ressource ajoutée: {resource} x{count}")

    def remove_resource(self, resource: str, count: int = 1) -> bool:
        """Retire des ressources de l'inventaire.
        
        Args:
            resource (str): Type de ressource
            count (int): Nombre à retirer
            
        Returns:
            bool: True si les ressources ont été retirées
        """
        if self.inventory.get(resource, 0) >= count:
            self.inventory[resource] -= count
            self.logger.debug(f"Ressource retirée: {resource} x{count}")
            return True
        return False

    def move_forward(self, map_width, map_height):
        if self.direction == 0:
            self.position = (self.position[0], (self.position[1] - 1) % map_height)
        elif self.direction == 2:
            self.position = (self.position[0], (self.position[1] + 1) % map_height)
        elif self.direction == 1:
            self.position = ((self.position[0] + 1) % map_width, self.position[1])
        elif self.direction == 3:
            self.position = ((self.position[0] - 1) % map_width, self.position[1])
        self.logger.info(f"player {self.id} moved from {self.position} to {self.position} facing {self.direction}")
