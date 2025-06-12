import logging
import time
from typing import Optional, Tuple
from core.client import ZappyClient
from core.protocol import ZappyProtocol
from managers.resource_manager import ResourceManager
from managers.movement_manager import MovementManager
from managers.vision_manager import VisionManager

class AI:
    """Classe principale de l'IA."""
    
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
        self.update_cooldown = 0.1  # Temps entre chaque mise à jour
        self.min_food = 5  # Niveau minimum de nourriture à maintenir

    def update(self) -> None:
        """Met à jour l'état de l'IA."""
        try:
            current_time = time.time()
            if current_time - self.last_update < self.update_cooldown:
                return
                
            self.last_update = current_time

            # Mise à jour de la vision si possible
            if self.vision_manager.can_update_vision():
                self.vision_manager.update_vision()

            # Mettre à jour l'inventaire
            self.resource_manager.update_inventory()

            # Vérifier la nourriture
            if self.resource_manager.get_food_count() < self.min_food:
                self._collect_food()
                return

            # Vérifier les collisions
            if self.movement_manager.handle_collision():
                return

            # Vérifier les ressources nécessaires
            if self.resource_manager.need_resources(self.level):
                resource = self.resource_manager.get_needed_resource(self.level)
                if resource:
                    self._collect_resource(resource)
                    return

            # Si on a toutes les ressources, on peut monter de niveau
            if self.resource_manager.can_level_up(self.level):
                self._try_elevation()
            else:
                self._explore()

        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour: {str(e)}")
            raise

    def _collect_food(self) -> None:
        """Tente de collecter de la nourriture."""
        target = self.vision_manager.find_nearest_object("food")
        if target:
            self.target_position = target
            self.logger.debug(f"Cible nourriture définie: {self.target_position}")
            if self.movement_manager.move_to_target(self.target_position):
                self.protocol.take("food")
                self.resource_manager.update_inventory()
                self.logger.debug("Nourriture prise")
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
            if self.movement_manager.move_to_target(self.target_position):
                self.protocol.take(resource)
                self.resource_manager.update_inventory()
                self.logger.debug(f"{resource} pris")
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
                distance = abs(target[0]) + abs(target[1])
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = target

        if nearest_target:
            self.target_position = nearest_target
            self.logger.debug(f"Cible exploration définie: {self.target_position}")
            self.movement_manager.move_to_target(self.target_position)
        else:
            # Si aucune ressource n'est visible, avance dans une direction aléatoire
            self.movement_manager.move_to_target((1, 0))

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