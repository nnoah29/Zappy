import logging
import time
import random
from typing import Optional, Tuple, List
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
                self.logger.debug("État changé: collecting food (critique)")
                self.state = "collecting"
                self.target_resource = "food"
                return
                te():
                self.logger.debug("État changé: elevating")
                self.state = "elevating"
                return
                
            needed_resources = self.elevation_manager.get_needed_resources()
            if needed_resources:
                prioritized_resources = self._prioritize_resources(needed_resources)
                self.logger.debug(f"État changé: collecting {prioritized_resources[0]} (priorité)")
                self.state = "collecting"
                self.target_resource = prioritized_resources[0]
                return
                
            if self.inventory_manager.inventory['food'] < 10:
                self.logger.debug("État changé: collecting food (maintenance)")
                self.state = "collecting"
                self.target_resource = "food"
                return
                
            self.logger.debug("Exploration intelligente")
            self.state = "exploring"
            self.target_resource = None
            
            if not self.target_position:
                best_target = self._find_best_exploration_target()
                if best_target:
                    self.target_position = best_target
                    self.logger.debug(f"Cible d'exploration intelligente: {self.target_position}")
                else:
                    self.target_position = self._generate_smart_exploration_target()
                    self.logger.debug(f"Nouvelle cible d'exploration aléatoire: {self.target_position}")
                
            if not self.movement_manager.move_to(self.target_position):
                self.target_position = None
                return True
                
            self.target_position = None
            return True
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'état: {str(e)}")
            self.state = "exploring"

    def _prioritize_resources(self, resources: List[str]) -> List[str]:
        """Priorise les ressources selon leur importance et rareté.
        
        Args:
            resources (List[str]): Liste des ressources nécessaires
            
        Returns:
            List[str]: Liste des ressources priorisées
        """
        priority_order = [
            'thystame',
            'phiras',
            'mendiane',
            'sibur',
            'deraumere',
            'linemate',
            'food'
        ]
        
        prioritized = []
        for resource in priority_order:
            if resource in resources:
                prioritized.append(resource)
                
        for resource in resources:
            if resource not in prioritized:
                prioritized.append(resource)
                
        return prioritized

    def _execute_action(self) -> bool:
        """Exécute l'action correspondante à l'état actuel.
        
        Returns:
            bool: True si l'action a réussi
        """
        try:
            # DÉSACTIVATION TEMPORAIRE DES COLLISIONS POUR PERMETTRE LE DÉPLACEMENT
            # Vérifie d'abord s'il y a des collisions à gérer (limité à 2 tentatives)
            # if not hasattr(self, '_ejection_attempts'):
            #     self._ejection_attempts = 0
            #     
            # if self.movement_manager.collision_manager.check_collision() and self._ejection_attempts < 2:
            #     self.logger.debug("Collision détectée dans la boucle principale, tentative de résolution")
            #     if self.movement_manager.collision_manager.eject_other_players():
            #         self.logger.debug("Éjection réussie dans la boucle principale")
            #         self._ejection_attempts += 1
            #         return True
            #     else:
            #         self.logger.debug("Éjection échouée dans la boucle principale")
            #         self._ejection_attempts += 1
            # else:
            #     # Reset le compteur d'éjection si pas de collision
            #     self._ejection_attempts = 0
            
            if self._collect_available_resources():
                self.logger.debug("Ressources disponibles ramassées")
                return True
            
            if self._move_to_nearest_resource():
                self.logger.debug("Déplacement vers la ressource la plus proche")
                if self._collect_available_resources():
                    self.logger.debug("Ressources collectées après déplacement")
                return True
            
            if self.inventory_manager.inventory['linemate'] < 1:
                self.logger.info("🔍 Recherche spécifique de linemate pour l'élévation")
                target = self.vision_manager.find_nearest_object("linemate")
                if target:
                    self.logger.info(f"🎯 Linemate trouvé à {target}, déplacement en cours...")
                    if self.movement_manager.move_to(target):
                        if self._collect_available_resources():
                            self.logger.info("✅ Linemate collecté après déplacement")
                        return True
            else:
                self.logger.info("🚀 Tentative d'élévation avec le linemate disponible")
                if self.elevation_manager.can_elevate():
                    self.logger.info("✅ Conditions d'élévation remplies, démarrage de l'élévation")
                    return self.elevation_manager.start_elevation()
                else:
                    self.logger.info("❌ Conditions d'élévation non remplies, collecte d'autres ressources")
            
            if self.inventory_manager.inventory['food'] < 10:
                self.logger.debug("Niveau de nourriture critique, recherche de nourriture")
                target = self.vision_manager.find_nearest_object("food")
                if target:
                    if target == (0, 0):
                        self.logger.debug("Nourriture trouvée sur la case actuelle, tentative de ramassage")
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
                
                if target == (0, 0):
                    self.logger.debug(f"{self.target_resource} trouvé sur la case actuelle, tentative de ramassage")
                    if not self.protocol.take(self.target_resource):
                        self.logger.debug(f"Impossible de prendre {self.target_resource}")
                        return False
                    self.logger.debug(f"{self.target_resource} ramassé avec succès")
                    if not self.inventory_manager.update_inventory():
                        self.logger.debug("Erreur lors de la mise à jour de l'inventaire")
                        return False
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

    def _collect_resource(self, resource: str) -> bool:
        """Collecte une ressource spécifique."""
        try:
            position = self.player.get_position()
            self.logger.debug(f"Tentative de collecte de {resource} à la position {position}")
            success = self.protocol.take(resource)
            
            if success:
                self.logger.info(f"✅ Ressource {resource} collectée avec succès à la position {position}")
                self.inventory_manager.inventory[resource] += 1
                self.logger.info(f"📦 Inventaire après collecte: {self.inventory_manager.inventory}")
                return True
            else:
                self.logger.debug(f"❌ Échec de la collecte de {resource} à la position {position}")
                return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte de {resource}: {str(e)}")
            return False

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

    def _find_best_exploration_target(self) -> Optional[Tuple[int, int]]:
        """Trouve la meilleure cible d'exploration dans la vision.
        
        Returns:
            Optional[Tuple[int, int]]: Meilleure cible d'exploration
        """
        try:
            best_target = None
            best_score = -1
            
            resource_priority = {
                'thystame': 100,
                'phiras': 80,
                'mendiane': 60,
                'sibur': 40,
                'deraumere': 20,
                'linemate': 10,
                'food': 5
            }
            
            for y in range(-self.vision_manager.level, self.vision_manager.level + 1):
                for x in range(-self.vision_manager.level, self.vision_manager.level + 1):
                    if (x, y) == (0, 0):
                        continue
                        
                    case_content = self.vision_manager.get_case_content(x, y)
                    if not case_content:
                        continue
                        
                    score = 0
                    for resource in case_content:
                        if resource in resource_priority:
                            score += resource_priority[resource]
                            
                    distance = abs(x) + abs(y)
                    score = score / (distance + 1)
                    
                    if score > best_score:
                        best_score = score
                        best_target = (x, y)
                        
            return best_target
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de cible d'exploration: {str(e)}")
            return None

    def _generate_smart_exploration_target(self) -> Tuple[int, int]:
        """Génère une cible d'exploration aléatoire intelligente.
        
        Returns:
            Tuple[int, int]: Cible d'exploration
        """
        try:
            max_radius = min(5, self.vision_manager.level + 2)
            
            directions = [
                (1, 0),
                (0, -1),
                (-1, 0),
                (0, 1),
                (1, 1),
                (-1, 1),
                (1, -1),
                (-1, -1)
            ]
            
            random.shuffle(directions)
            
            for dx, dy in directions:
                radius = random.randint(1, max_radius)
                x = dx * radius
                y = dy * radius
                
                if abs(x) <= max_radius and abs(y) <= max_radius:
                    return (x, y)
                    
            x = random.randint(-max_radius, max_radius)
            y = random.randint(-max_radius, max_radius)
            if (x, y) == (0, 0):
                x, y = 1, 0
                
            return (x, y)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de cible d'exploration: {str(e)}")
            return (1, 0)
    def _collect_available_resources(self) -> bool:
        """Collecte toutes les ressources disponibles sur la case actuelle."""
        try:
            vision_data = self.vision_manager.vision_data
            if not vision_data or len(vision_data) == 0:
                return False
                
            current_case = vision_data[0]
            if not current_case:
                return False
                
            if isinstance(current_case, list):
                items = current_case
            else:
                items = current_case.split()
                
            resources_to_collect = []
            
            for item in items:
                if item != 'player' and item in ['food', 'linemate', 'deraumere', 'sibur', 'mendiane', 'phiras', 'thystame']:
                    resources_to_collect.append(item)
            
            collected = False
            for resource in resources_to_collect:
                if self._collect_resource(resource):
                    collected = True
                    self.logger.debug(f"Ressource {resource} collectée depuis la case actuelle")
            
            return collected
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte des ressources: {str(e)}")
            return False

    def _move_to_nearest_resource(self) -> bool:
        """Déplace le joueur vers la ressource la plus proche."""
        try:
            self.logger.debug("Recherche de la ressource la plus proche...")
            resources = ["linemate", "food", "deraumere", "sibur", "mendiane", "phiras", "thystame"]
            nearest_target = None
            min_distance = float('inf')
            nearest_resource = None

            for resource in resources:
                target = self.vision_manager.find_nearest_object(resource)
                if target:
                    distance = abs(target[0]) + abs(target[1])
                    self.logger.debug(f"Ressource {resource} trouvée à {target} (distance: {distance})")
                    if distance < min_distance:
                        min_distance = distance
                        nearest_target = target
                        nearest_resource = resource
                        self.logger.debug(f"Nouvelle ressource la plus proche: {resource} à {target}")

            if nearest_target:
                current_pos = self.player.get_position()
                self.logger.info(f"🎯 Déplacement vers {nearest_resource} à {nearest_target} depuis {current_pos}")
                success = self.movement_manager.move_to(nearest_target)
                if success:
                    new_pos = self.player.get_position()
                    self.logger.info(f"✅ Déplacement réussi vers {nearest_resource}: {current_pos} → {new_pos}")
                else:
                    self.logger.warning(f"❌ Échec du déplacement vers {nearest_resource} à {nearest_target}")
                return success
            else:
                self.logger.debug("Aucune ressource trouvée, exploration...")
                self._explore()
                return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de ressource: {str(e)}")
            return False