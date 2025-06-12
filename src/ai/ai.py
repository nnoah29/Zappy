import logging
import time
import random
from typing import Optional, Tuple
from core.client import ZappyClient
from core.protocol import ZappyProtocol
from managers.resource_manager import ResourceManager
from managers.movement_manager import MovementManager
from managers.vision_manager import VisionManager
from models.player import Player
from models.map import Map

class AI:
    """Classe principale de l'IA."""
    
    ELEVATION_REQUIREMENTS = {
        1: {'players': 1, 'linemate': 1, 'deraumere': 0, 'sibur': 0, 'mendiane': 0, 'phiras': 0, 'thystame': 0},
        2: {'players': 2, 'linemate': 1, 'deraumere': 1, 'sibur': 1, 'mendiane': 0, 'phiras': 0, 'thystame': 0},
        3: {'players': 2, 'linemate': 2, 'deraumere': 0, 'sibur': 1, 'mendiane': 0, 'phiras': 2, 'thystame': 0},
        4: {'players': 4, 'linemate': 1, 'deraumere': 1, 'sibur': 2, 'mendiane': 0, 'phiras': 1, 'thystame': 0},
        5: {'players': 4, 'linemate': 1, 'deraumere': 2, 'sibur': 1, 'mendiane': 3, 'phiras': 0, 'thystame': 0},
        6: {'players': 6, 'linemate': 1, 'deraumere': 2, 'sibur': 3, 'mendiane': 0, 'phiras': 1, 'thystame': 0},
        7: {'players': 6, 'linemate': 2, 'deraumere': 2, 'sibur': 2, 'mendiane': 2, 'phiras': 2, 'thystame': 1}
    }

    def __init__(self, client: ZappyClient):
        """Initialise l'IA.
        
        Args:
            client (ZappyClient): Client connecté au serveur
        """
        self.client = client
        self.protocol = ZappyProtocol(client)
        self.vision_manager = VisionManager(self.protocol)
        self.movement_manager = MovementManager(self.protocol, self.vision_manager)
        self.resource_manager = ResourceManager(self.protocol)
        self.logger = logging.getLogger(__name__)
        self.level = 1
        self.target_position: Optional[Tuple[int, int]] = None
        self.last_update = 0
        self.update_cooldown = 0.1
        self.min_food = 5

        # Initialisation du joueur et de la carte avec les informations du client
        self.player = Player(
            self.client.client_num,
            self.client.team_name,
            self.client.map_size[0] // 2,  # Position initiale au centre
            self.client.map_size[1] // 2
        )
        self.map = Map(self.client.map_size[0], self.client.map_size[1])
        
        self.logger.info(f"Joueur initialisé: ID={self.client.client_num}, Équipe={self.client.team_name}, Position=({self.client.map_size[0]//2}, {self.client.map_size[1]//2})")
        self.logger.info(f"Carte initialisée: {self.client.map_size[0]}x{self.client.map_size[1]}")

    def update(self) -> None:
        """Met à jour l'état de l'IA."""
        try:
            current_time = time.time()
            if current_time - self.last_update < self.update_cooldown:
                return
                
            self.last_update = current_time

            if self.vision_manager.can_update_vision():
                self.vision_manager.update_vision()
                self._update_map_from_vision()

            self.resource_manager.update_inventory()

            if self.resource_manager.get_food_count() < self.min_food:
                self._collect_food()
                return

            if self.movement_manager.handle_collision():
                return

            if self.resource_manager.need_resources(self.level):
                resource = self.resource_manager.get_needed_resource(self.level)
                if resource:
                    self._collect_resource(resource)
                    return

            if self.resource_manager.can_level_up(self.level):
                self._try_elevation()
            else:
                self._explore()

        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour: {str(e)}")
            raise

    def _update_map_from_vision(self) -> None:
        """Met à jour la carte à partir de la vision."""
        vision_data = self.vision_manager.vision_data
        if not vision_data:
            return

        # Met à jour la case du joueur
        current_tile = self.map.get_tile(self.player.x, self.player.y)
        current_tile.players = [self.player.id]

        # Met à jour les cases visibles
        for i, case_str in enumerate(vision_data):
            if not case_str:
                continue

            # Parse la chaîne de caractères en ressources
            resources = {}
            items = case_str.split()
            for item in items:
                if item != 'player':
                    resources[item] = resources.get(item, 0) + 1

            # Calcule la position relative à partir de l'index
            x, y = self._get_relative_position(i)
            
            # Applique la position relative à la position actuelle du joueur
            # en tenant compte du monde torique
            target_x = (self.player.x + x) % self.map.width
            target_y = (self.player.y + y) % self.map.height
            
            # Met à jour la case
            tile = self.map.get_tile(target_x, target_y)
            tile.resources = resources

    def _get_relative_position(self, index: int) -> Tuple[int, int]:
        """Calcule la position relative à partir de l'index de vision.
        
        Args:
            index (int): Index dans la vision
            
        Returns:
            Tuple[int, int]: Position relative (x, y)
        """
        
        if index == 0:
            return (0, 0)
        
        positions = [
            (0, 0),
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1)
        ]
        
        return positions[index]

    def _collect_food(self) -> None:
        """Tente de collecter de la nourriture."""
        target = self.vision_manager.find_nearest_object("food")
        if target:
            self.target_position = target
            self.logger.debug(f"Cible nourriture définie: {self.target_position}")
            
            if (self.player.x, self.player.y) == target:
                self.protocol.take("food")
                self.resource_manager.update_inventory()
                self.logger.debug("Nourriture prise")
                self.target_position = None
            else:
                if not self.movement_manager.move_to_target(target):
                    self.logger.debug("Impossible d'atteindre la nourriture, nouvelle cible...")
                    self._explore()
        else:
            self.logger.debug("Aucune nourriture trouvée, exploration...")
            self._explore()

    def _collect_resource(self, resource: str) -> None:
        """Tente de collecter une ressource spécifique.
        
        Args:
            resource (str): Type de ressource à collecter
        """
        target = self.vision_manager.find_nearest_object(resource)
        if target:
            self.target_position = target
            self.logger.debug(f"Cible {resource} définie: {self.target_position}")
            
            if (self.player.x, self.player.y) == target:
                self.protocol.take(resource)
                self.resource_manager.update_inventory()
                self.logger.debug(f"{resource} pris")
                self.target_position = None
            else:
                if not self.movement_manager.move_to_target(target):
                    self.logger.debug(f"Impossible d'atteindre {resource}, nouvelle cible...")
                    self._explore()
        else:
            self.logger.debug(f"Aucune {resource} trouvée, exploration...")
            self._explore()

    def _explore(self) -> None:
        """Explore la carte pour trouver des ressources."""
        # Cherche la ressource la plus proche
        resources = ["food", "linemate", "deraumere", "sibur", "mendiane", "phiras", "thystame"]
        nearest_target = None
        min_distance = float('inf')

        for resource in resources:
            target = self.vision_manager.find_nearest_object(resource)
            if target:
                distance = abs(target[0] - self.player.x) + abs(target[1] - self.player.y)
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = target

        if nearest_target:
            self.target_position = nearest_target
            self.logger.debug(f"Cible exploration définie: {self.target_position}")
            if not self.movement_manager.move_to_target(self.target_position):
                self.logger.debug("Impossible d'atteindre la cible, nouvelle cible...")
                self._generate_new_exploration_target()
        else:
            self._generate_new_exploration_target()

    def _generate_new_exploration_target(self) -> None:
        """Génère une nouvelle cible d'exploration aléatoire."""
        # Génère une position aléatoire dans un rayon de 5 cases
        max_radius = 5
        while True:
            x = random.randint(-max_radius, max_radius)
            y = random.randint(-max_radius, max_radius)
            # Évite de revenir à la position actuelle
            if (x, y) != (0, 0):
                # Applique la position relative à la position actuelle du joueur
                target_x = (self.player.x + x) % self.map.width
                target_y = (self.player.y + y) % self.map.height
                self.target_position = (target_x, target_y)
                self.logger.debug(f"Nouvelle cible d'exploration aléatoire: {self.target_position}")
                self.movement_manager.move_to_target(self.target_position)
                break

    def _try_elevation(self) -> None:
        """Tente de monter de niveau."""
        result = self.protocol.incantation()
        if result > 0:
            self.level = result
            self.vision_manager.set_level(result)
            self.logger.debug(f"Niveau {self.level} atteint")
        else:
            self.logger.debug("Échec de l'incantation")
            self._explore()