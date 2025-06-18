import logging
import time
import random
from typing import Optional, Tuple
from core.protocol import ZappyProtocol
from managers.movement_manager import MovementManager
from managers.vision_manager import VisionManager
from models.player import Player
from models.map import Map
from managers.elevation_manager import ElevationManager
from managers.inventory_manager import InventoryManager

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

    def __init__(self, protocol: ZappyProtocol, player: Player, map: Map, logger: logging.Logger):
        """Initialise l'IA.
        
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
        
        self.vision_manager = VisionManager(protocol, player, map, logger)
        self.movement_manager = MovementManager(protocol, player, map, self.vision_manager, logger)
        self.inventory_manager = InventoryManager(protocol, player, logger)
        self.elevation_manager = ElevationManager(protocol, self.vision_manager, self.movement_manager, logger)
        
        self.state = "exploring"
        self.target_position: Optional[Tuple[int, int]] = None
        self.target_resource: Optional[str] = None
        self.last_update = 0
        self.update_cooldown = 7

        self.logger.info(f"Joueur initialisé: ID={player.id}, Équipe={player.team}, Position={player.position}")
        self.logger.info(f"Carte initialisée: {map.width}x{map.height}")
        self.logger.info("IA initialisée avec succès")

    def update(self) -> bool:
        """Met à jour l'état de l'IA.
        
        Returns:
            bool: True si la mise à jour a réussi
        """
        try:
            if time.time() - self.last_update < self.update_cooldown:
                return True
                
            if not self.vision_manager.update_vision():
                return False
            
            if not self.inventory_manager.update_inventory():
                return False
                
            if self.inventory_manager.inventory['food'] <= 0:
                self.logger.error("Le joueur est mort de faim")
                return False
                
            self._update_state()
            
            if not self._execute_action():
                return False
                
            self.last_update = time.time()
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour: {str(e)}")
            return False

    def _update_state(self) -> None:
        """Met à jour l'état de l'IA."""
        try:
            if self.inventory_manager.inventory['food'] < 5:
                self.logger.debug("État changé: collecting food")
                self.state = "collecting"
                self.target_resource = "food"
                return
                
            if self.elevation_manager.can_elevate():
                self.logger.debug("État changé: elevating")
                self.state = "elevating"
                return
                
            needed_resources = self.elevation_manager.get_needed_resources()
            if needed_resources:
                self.logger.debug(f"État changé: collecting {needed_resources[0]}")
                self.state = "collecting"
                self.target_resource = needed_resources[0]
                return
                
            self.logger.debug("État changé: exploring")
            self.state = "exploring"
            self.target_resource = None
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'état: {str(e)}")
            self.state = "exploring"

    def _execute_action(self) -> bool:
        """Exécute l'action correspondante à l'état actuel.
        
        Returns:
            bool: True si l'action a réussi
        """
        try:
            if self.movement_manager.collision_manager.check_collision():
                self.logger.debug("Collision détectée dans la boucle principale, tentative de résolution")
                if self.movement_manager.collision_manager.eject_other_players():
                    self.logger.debug("Éjection réussie dans la boucle principale")
                    return True
                else:
                    self.logger.debug("Éjection échouée dans la boucle principale")
            
            if self.inventory_manager.inventory['food'] < 10:
                self.logger.debug("Niveau de nourriture critique, recherche de nourriture")
                target = self.vision_manager.find_nearest_object("food")
                if target:
                    if target == (0, 0):
                        if not self.protocol.take("food"):
                            self.logger.debug("Impossible de prendre la nourriture")
                            return False
                        self.logger.debug("Nourriture prise avec succès")
                        if not self.inventory_manager.update_inventory():
                            self.logger.debug("Erreur lors de la mise à jour de l'inventaire")
                            return False
                        if self.inventory_manager.inventory['food'] < 10:
                            return self._execute_action()
                        return True
                    if not self.movement_manager.move_to(target):
                        self.logger.debug("Impossible d'atteindre la nourriture, tentative de déplacement aléatoire")
                        if self.inventory_manager.inventory['food'] < 5:
                            self.logger.debug("Nourriture très basse, déplacement aléatoire forcé")
                            for _ in range(3):
                                x = random.randint(-1, 1)
                                y = random.randint(-1, 1)
                                if (x, y) != (0, 0):
                                    if self.movement_manager.move_to((x, y)):
                                        self.logger.debug("Déplacement aléatoire réussi")
                                        return True
                        else:
                            x = random.randint(-1, 1)
                            y = random.randint(-1, 1)
                            if (x, y) != (0, 0):
                                if not self.movement_manager.move_to((x, y)):
                                    self.logger.debug("Impossible de se déplacer aléatoirement")
                                    return False
                        return True
                    return True
                else:
                    self.logger.debug("Pas de nourriture en vue, exploration")
                    self.state = "exploring"
                    return True

            if self.elevation_manager.can_elevate():
                self.logger.debug("Démarrage de l'élévation")
                return self.elevation_manager.start_elevation()
                
            needed_resources = self.elevation_manager.get_needed_resources()
            if needed_resources:
                self.logger.debug(f"Recherche de {needed_resources[0]}")
                self.state = "collecting"
                self.target_resource = needed_resources[0]
                
                target = self.vision_manager.find_nearest_object(self.target_resource)
                if not target:
                    self.logger.debug(f"Pas de {self.target_resource} en vue, exploration")
                    self.state = "exploring"
                    return True
                    
                if not self.movement_manager.move_to(target):
                    self.logger.debug(f"Impossible d'atteindre {self.target_resource}, exploration")
                    self.state = "exploring"
                    return True
                    
                if not self.protocol.take(self.target_resource):
                    self.logger.debug(f"Impossible de prendre {self.target_resource}")
                    return False

                self.logger.debug(f"{self.target_resource} ramassé avec succès")
                if not self.inventory_manager.update_inventory():
                    self.logger.debug("Erreur lors de la mise à jour de l'inventaire")
                    return False
                return True

            self.logger.debug("Exploration")
            self.state = "exploring"
            self.target_resource = None
            
            if not self.target_position:
                x = random.randint(-1, 1)
                y = random.randint(-1, 1)
                if (x, y) != (0, 0):
                    self.target_position = (x, y)
                    self.logger.debug(f"Nouvelle cible d'exploration: {self.target_position}")
                
            if not self.movement_manager.move_to(self.target_position):
                self.target_position = None
                return True
                
            self.target_position = None
            return True
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de l'action: {str(e)}")
            return False

    def _update_map_from_vision(self) -> None:
        """Met à jour la carte à partir de la vision."""
        vision_data = self.vision_manager.vision_data
        if not vision_data:
            return

        current_tile = self.map.get_tile(self.player.x, self.player.y)
        current_tile.players = [self.player.id]

        for i, case_str in enumerate(vision_data):
            if not case_str:
                continue

            resources = {}
            items = case_str.split()
            for item in items:
                if item != 'player':
                    resources[item] = resources.get(item, 0) + 1

            x, y = self._get_relative_position(i)
            
            target_x = (self.player.x + x) % self.map.width
            target_y = (self.player.y + y) % self.map.height
            
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
                self.inventory_manager.update_inventory()
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
                self.inventory_manager.update_inventory()
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
        max_radius = 5
        while True:
            x = random.randint(-max_radius, max_radius)
            y = random.randint(-max_radius, max_radius)
            if (x, y) != (0, 0):
                target_x = (self.player.x + x) % self.map.width
                target_y = (self.player.y + y) % self.map.height
                self.target_position = (target_x, target_y)
                self.logger.debug(f"Nouvelle cible d'exploration aléatoire: {self.target_position}")
                if self.movement_manager.move_to_target(self.target_position):
                    break
                continue

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