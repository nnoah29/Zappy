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
from models.playerCommunicator import PlayerCommunicator
from managers.reproduction_manager import ReproductionManager

class AI:
    """Classe principale de l'IA."""
    
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
        self.state = "EMERGENCY_FOOD_SEARCH"  # État initial : recherche d'urgence de nourriture
        self.target_resource = None
        self.target_position = None
        self.level = 1
        
        # Réduction drastique du cooldown pour réactivité maximale
        self.update_cooldown = 1  # Réduit de 7 à 1 seconde
        
        # Seuils de nourriture pour le mode urgence
        self.FOOD_CRITICAL_LEVEL = 10  # Seuil critique pour le mode urgence
        self.FOOD_SAFE_LEVEL = 12      # Niveau de sécurité pour désactiver le mode urgence (abaissé de 25 à 13)
        
        # Initialisation des gestionnaires
        self.vision_manager = VisionManager(protocol, player, map, logger)
        self.inventory_manager = InventoryManager(protocol, player, logger)
        self.movement_manager = MovementManager(protocol, player, map, self.vision_manager, logger)
        self.elevation_manager = ElevationManager(protocol, self.vision_manager, self.movement_manager, logger)
        self.communicator = PlayerCommunicator(protocol, player, logger)
        self.reproduction_manager = ReproductionManager(protocol, logger)
        
        self.last_update = 0

        # État spécial pour l'élévation en cours
        self.elevation_in_progress = False
        self.elevation_start_time = 0

        self.logger.info(f"Joueur initialisé: ID={player.id}, Équipe={player.team}, Position={player.position}")
        self.logger.info(f"Carte initialisée: {map.width}x{map.height}")
        self.logger.info("IA initialisée avec succès")

    def update(self) -> bool:
        """Met à jour l'IA et exécute une action.
        
        Returns:
            bool: True si l'IA continue de fonctionner
        """
        try:
            current_time = time.time()
            
            # Cooldown dynamique : plus rapide en mode urgence
            if self.state == "EMERGENCY_FOOD_SEARCH":
                # En mode urgence, pas de cooldown pour une réactivité maximale
                cooldown = 0.1
            else:
                cooldown = self.update_cooldown
            
            if current_time - self.last_update < cooldown:
                return True
            
            self.last_update = current_time
            
            # Mise à jour de la vision
            if not self.vision_manager.update_vision():
                self.logger.warning("Échec de la mise à jour de la vision")
                return True
            
            # Mise à jour de l'inventaire
            if not self.inventory_manager.update_inventory():
                self.logger.warning("Échec de la mise à jour de l'inventaire")
                return True
            
            # Vérification de la mort
            if self.inventory_manager.inventory['food'] <= 0:
                self.logger.error("Le joueur est mort de faim")
                return False
            
            # Mise à jour de l'état
            self._update_state()
            
            # Exécution de l'action
            return self._execute_action()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'IA: {str(e)}")
            return True

    def _update_state(self) -> None:
        """Met à jour l'état de l'IA."""
        try:
            if self.inventory_manager.inventory['food'] < 5:
                self.logger.debug("État changé: collecting food (critique)")
                self.state = "collecting"
                self.target_resource = "food"
                return
                
            if self.elevation_manager.can_elevate():
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
            'food',
            'thystame',
            'phiras',
            'mendiane',
            'sibur',
            'deraumere',
            'linemate'
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
        """Exécute l'action appropriée selon l'état actuel."""
        try:
            # Gestion spéciale de l'état d'élévation
            if self.state == "ELEVATING":
                self.logger.info("⏳ En attente du résultat de l'élévation...")
                # Pendant l'élévation, on ne fait rien d'autre
                # Le résultat sera géré par la boucle principale
                return True
            
            # Gestion spéciale de l'état de participation à un rituel
            if self.state == "JOINING_RITUAL":
                self.logger.info("🤝 En route pour rejoindre un rituel d'équipe...")
                if self.target_position:
                    if self.movement_manager.move_to(self.target_position):
                        self.logger.info("✅ Déplacement vers le rituel réussi")
                        # Une fois arrivé, on revient à l'état normal
                        self.state = "NORMAL_OPERATIONS"
                        self.target_position = None
                    else:
                        self.logger.warning("❌ Impossible d'atteindre le rituel")
                        self.state = "NORMAL_OPERATIONS"
                        self.target_position = None
                return True
            
            # Gestion spéciale de l'état d'attente d'un partenaire pour le rituel
            if self.state == "WAITING_FOR_RITUAL_PARTNER":
                self.logger.info("⏳ En attente d'un partenaire pour le rituel niveau 3...")
                
                # Vérifier s'il y a un autre joueur sur la case
                current_tile_content = self.vision_manager.vision_data[0] if self.vision_manager.vision_data else []
                player_count = current_tile_content.count('player')
                
                if player_count >= 2:
                    self.logger.info("👥 Partenaire détecté ! Lancement du rituel niveau 3 !")
                    response = self.protocol.incantation()
                    
                    if response == "ko":
                        self.logger.error("❌ Échec de l'incantation de groupe")
                        self.state = "NORMAL_OPERATIONS"
                    elif response == "Elevation underway":
                        self.logger.info("🌟 Élévation de groupe en cours ! Attente du résultat...")
                        self.elevation_in_progress = True
                        self.elevation_start_time = time.time()
                        self.state = "ELEVATING"
                    else:
                        self.logger.warning(f"⚠️ Réponse inattendue lors de l'incantation de groupe: {response}")
                        self.state = "NORMAL_OPERATIONS"
                else:
                    self.logger.debug(f"⏳ Toujours en attente... ({player_count} joueur(s) sur la case)")
                
                return True
            
            food_level = self.inventory_manager.inventory['food']
            
            if food_level < 10:
                self.state = "EMERGENCY_FOOD_SEARCH"
                self.logger.critical("🚨🚨 MODE URGENCE : Survie immédiate prioritaire.")
                
                self.logger.critical("🚨 MODE URGENCE : Recherche prioritaire de nourriture")
                target = self.vision_manager.find_nearest_object("food")
                if target:
                    self.logger.critical(f"🚨 NOURRITURE TROUVÉE À {target}, DÉPLACEMENT URGENT")
                    if self.movement_manager.move_to(target):
                        self.logger.critical("✅ DÉPLACEMENT URGENT RÉUSSI, COLLECTE IMMÉDIATE")
                        if self._collect_resource_intensively("food"):
                            self.logger.critical("✅ NOURRITURE COLLECTÉE EN MODE URGENCE")
                        else:
                            self.logger.critical("❌ ÉCHEC DE LA COLLECTE EN MODE URGENCE")
                        return True
                else:
                    self.logger.critical("🚨 AUCUNE NOURRITURE EN VUE, EXPLORATION D'URGENCE")
                    exploration_target = self._generate_emergency_exploration_target()
                    if exploration_target:
                        self.logger.critical(f"🚨 EXPLORATION D'URGENCE VERS {exploration_target}")
                        if self.movement_manager.move_to(exploration_target):
                            self.vision_manager.force_update_vision()
                            if self._collect_available_resources():
                                self.logger.critical("✅ RESSOURCES TROUVÉES EN EXPLORATION D'URGENCE")
                            return True
                    else:
                        self.logger.critical("🚨 MOUVEMENT ALÉATOIRE D'URGENCE")
                        random_direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                        if self.movement_manager.move_to(random_direction):
                            self.vision_manager.force_update_vision()
                            if self._collect_available_resources():
                                self.logger.critical("✅ RESSOURCES TROUVÉES EN MOUVEMENT ALÉATOIRE")
                            return True
                
                return True
            
            if food_level < 12:
                self.state = "SURVIVAL_BUFFERING"
                self.logger.warning(f"⚠️ MODE SÉCURITÉ : Constitution des réserves de nourriture (actuel: {food_level}). Objectifs secondaires suspendus.")
                
                target = self.vision_manager.find_nearest_object("food")
                if target:
                    self.logger.info(f"🎯 Cible de sécurité : nourriture à {target}.")
                    if self.movement_manager.move_to(target):
                        if self._collect_resource_intensively("food"):
                            self.logger.info("✅ Nourriture collectée pour les réserves")
                        else:
                            self.logger.warning("❌ Échec de la collecte de sécurité")
                        return True
                else:
                    self.logger.info("🔍 Exploration ciblée pour la nourriture.")
                    exploration_target = self._generate_emergency_exploration_target()
                    if exploration_target:
                        self.logger.info(f"🎯 Exploration vers {exploration_target} pour trouver de la nourriture")
                        if self.movement_manager.move_to(exploration_target):
                            self.vision_manager.force_update_vision()
                            if self._collect_available_resources():
                                self.logger.info("✅ Ressources trouvées lors de l'exploration de sécurité")
                            return True
                
                return True
            
            self.logger.info(f"✅ Niveau de nourriture sécurisé ({food_level}). Objectif : Élévation.")
            self.state = "NORMAL_OPERATIONS"
            
            # Vérification des messages d'équipe en priorité
            if self._handle_team_messages():
                return True  # Un message a été traité, on attend le prochain cycle
            
            current_tile_content = self.vision_manager.vision_data[0] if self.vision_manager.vision_data else []
            player_count = current_tile_content.count('player')
            linemate_on_tile = current_tile_content.count('linemate')
            linemate_in_inventory = self.inventory_manager.inventory.get('linemate', 0)
            
            # DÉCISION 1 : Lancer l'incantation si TOUT est prêt.
            if player_count == 1 and linemate_on_tile >= 1:
                self.logger.info("✨ Conditions parfaites ! Lancement de l'incantation pour le niveau 2 !")
                response = self.protocol.incantation()
                
                if response == "Elevation underway":
                    self.logger.info("🌟 Élévation en cours ! Attente du résultat...")
                    self.elevation_in_progress = True
                    self.elevation_start_time = time.time()
                    self.state = "ELEVATING"
                    return True
                elif response == "ko":
                    self.logger.error("❌ Échec de l'incantation")
                    return True
                else:
                    self.logger.warning(f"⚠️ Réponse inattendue lors de l'incantation: {response}")
                    return True
            
            if linemate_in_inventory >= 1 and player_count == 1:
                self.logger.info("📦 Case prête et pierre en main. Je dépose la pierre.")
                if self.protocol.set("linemate"):
                    self.logger.info("✅ Linemate déposé sur la case")
                else:
                    self.logger.error("❌ Échec du dépôt de linemate")
                return True
            
            if linemate_in_inventory >= 1 and player_count > 1:
                self.logger.warning(f"⚠️ J'ai la pierre mais il y a {player_count} joueurs ici. Je bouge.")
                random_direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                if self.movement_manager.move_to(random_direction):
                    self.logger.info("✅ Déplacement vers une case plus calme")
                return True
            
            if linemate_in_inventory == 0 and linemate_on_tile == 0:
                self.logger.info("🔍 Objectif : Trouver une pierre de linemate.")
                target = self.vision_manager.find_nearest_object("linemate")
                if target:
                    self.logger.info(f"🎯 Linemate trouvé à {target}, déplacement...")
                    if self.movement_manager.move_to(target):
                        if self._collect_resource_intensively("linemate"):
                            self.logger.info("✅ Linemate collecté avec succès")
                        else:
                            self.logger.warning("❌ Échec de la collecte de linemate")
                else:
                    self.logger.info("🔍 Aucune linemate en vue, exploration...")
                    exploration_target = self._generate_linemate_exploration_target()
                    if exploration_target:
                        self.logger.info(f"🎯 Exploration vers {exploration_target} pour trouver du linemate")
                        if self.movement_manager.move_to(exploration_target):
                            self.logger.info("✅ Déplacement d'exploration réussi")
                return True
            
            self.logger.debug("Situation d'élévation non couverte, exploration par défaut.")
            self._explore()
            
            if self.reproduction_manager.can_fork() and food_level > 20:
                self.logger.info("🥚 Conditions optimales pour la reproduction.")
                if self.reproduction_manager.reproduce():
                    self.communicator.send_team_message("EGG_LAID", f"{self.player.x},{self.player.y}")
                return True
            
            if self.player.level == 2:
                if self._has_resources_for_level(3) and food_level > 15:
                    self.logger.info("📢 J'ai les ressources pour le niveau 3. J'appelle à l'aide !")
                    self.communicator.send_team_message("RITUAL_LVL3_START", f"{self.player.x},{self.player.y}")
                    
                    self.logger.info("📦 Je pose les pierres pour le rituel niveau 3...")
                    if self.protocol.set("linemate"):
                        self.logger.info("✅ Linemate posé")
                    if self.protocol.set("deraumere"):
                        self.logger.info("✅ Deraumere posé")
                    if self.protocol.set("sibur"):
                        self.logger.info("✅ Sibur posé")
                    
                    self.state = "WAITING_FOR_RITUAL_PARTNER"
                    return True
            
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
                self.inventory_manager.take_object("food")
                self.inventory_manager.update_inventory()
                self.logger.debug("Nourriture prise")
                self.target_position = None
            else:
                if not self.movement_manager.move_to(target):
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
            success = self.inventory_manager.take_object(resource)
            
            if success:
                self.logger.info(f"✅ Ressource {resource} collectée avec succès à la position {position}")
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
            if not self.movement_manager.move_to(self.target_position):
                self.logger.debug("Impossible d'atteindre la cible, nouvelle cible...")
                self.target_position = self._generate_smart_exploration_target()
        else:
            self.target_position = self._generate_smart_exploration_target()

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

    def _generate_smart_exploration_target(self) -> Tuple[int, int]:
        """Génère une cible d'exploration intelligente.
        
        Returns:
            Tuple[int, int]: Cible d'exploration
        """
        try:
            if self.elevation_manager.get_needed_resources() and 'linemate' in self.elevation_manager.get_needed_resources():
                self.logger.debug("🎯 Génération de cible d'exploration prioritaire pour linemate")
                max_radius = 5
                x = random.randint(-max_radius, max_radius)
                y = random.randint(-max_radius, max_radius)
                if (x, y) == (0, 0):
                    x, y = 1, 0
                return (x, y)
            
            # Exploration intelligente basée sur la vision
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

    def _generate_linemate_exploration_target(self) -> Optional[Tuple[int, int]]:
        """Génère une cible d'exploration spécifique pour trouver du linemate."""
        try:
            max_radius = 5
            x = random.randint(-max_radius, max_radius)
            y = random.randint(-max_radius, max_radius)
            if (x, y) == (0, 0):
                x, y = 1, 0
            return (x, y)
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de cible d'exploration spécifique: {str(e)}")
            return None

    def _collect_available_resources(self) -> bool:
        """Collecte toutes les ressources disponibles sur la case actuelle.
        
        Returns:
            bool: True si au moins une ressource a été collectée
        """
        try:
            position = self.player.get_position()
            self.logger.debug(f"🔍 Collecte de toutes les ressources à la position {position}")
            
            collected_anything = False
            resources_to_collect = ["food", "linemate", "deraumere", "sibur", "mendiane", "phiras", "thystame"]
            
            if self.state == "EMERGENCY_FOOD_SEARCH":
                resources_to_collect = ["food"] + [r for r in resources_to_collect if r != "food"]
            
            for resource in resources_to_collect:
                if self.inventory_manager.take_object(resource):
                    self.logger.info(f"✅ {resource} collecté(e)")
                    collected_anything = True
                    
                    if self.state == "EMERGENCY_FOOD_SEARCH":
                        self.vision_manager.force_update_vision()
                    
                    time.sleep(0.1)
            
            if collected_anything:
                self.logger.info(f"📦 Collecte terminée à {position}")
            else:
                self.logger.debug(f"❌ Aucune ressource trouvée à {position}")
            
            return collected_anything
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte de ressources: {str(e)}")
            return False

    def _move_to_nearest_resource(self) -> bool:
        """Déplace le joueur vers la ressource la plus proche."""
        try:
            self.logger.debug("Recherche de la ressource la plus proche...")
            
            if self.inventory_manager.inventory['food'] < 20:
                self.logger.warning("🚨 Nourriture critique, priorité absolue à la nourriture")
                resources = ["food"]
            elif self.inventory_manager.inventory['food'] < 25:
                self.logger.info("⚠️ Nourriture faible, priorité élevée")
                resources = ["food", "linemate", "deraumere", "sibur", "mendiane", "phiras", "thystame"]
            else:
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
                    
                    self.logger.debug("🔄 Mise à jour forcée de la vision après déplacement")
                    if not self.vision_manager.force_update_vision():
                        self.logger.warning("❌ Échec de la mise à jour de la vision après déplacement")
                    
                    if self._collect_available_resources():
                        self.logger.info(f"✅ Ressources collectées après déplacement vers {nearest_resource}")
                    else:
                        self.logger.warning(f"❌ Aucune ressource collectée après déplacement vers {nearest_resource}")
                        self.logger.info(f"🔄 Tentative de collecte directe de {nearest_resource}")
                        if self._collect_resource(nearest_resource):
                            self.logger.info(f"✅ {nearest_resource} collecté directement")
                        else:
                            self.logger.warning(f"❌ Échec de la collecte directe de {nearest_resource}")
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

    def _collect_resource_intensively(self, resource: str) -> bool:
        """Collecte intensivement une ressource spécifique jusqu'à ce qu'il n'y en ait plus.
        
        Args:
            resource (str): Type de ressource à collecter
            
        Returns:
            bool: True si au moins une ressource a été collectée
        """
        try:
            position = self.player.get_position()
            self.logger.info(f"🔄 Collecte intensive de {resource} à la position {position}")
            
            self.logger.info("🕵️ Vérification finale de la présence de la ressource...")
            self.vision_manager.force_update_vision()
            tile_content = self.vision_manager.vision_data[0] if self.vision_manager.vision_data else []
            if resource not in tile_content:
                self.logger.warning(f"❌ La ressource {resource} a disparu juste avant la collecte !")
                return False
            
            collected_count = 0
            
            while True:
                if self.inventory_manager.take_object(resource):
                    collected_count += 1
                    self.logger.info(f"✅ {resource} #{collected_count} collecté(e)")
                    
                    self.logger.info("🔄 Forçage de la mise à jour de la vision post-collecte.")
                    if not self.vision_manager.force_update_vision():
                        self.logger.warning("❌ Échec de la mise à jour de la vision post-collecte")
                    
                    time.sleep(0.1)
                else:
                    if collected_count > 0:
                        self.logger.info(f"📦 Collecte intensive terminée : {collected_count} {resource} collecté(s)")
                        self.logger.info(f"📦 Inventaire après collecte intensive : {self.inventory_manager.inventory}")
                    else:
                        self.logger.warning(f"❌ Aucun(e) {resource} trouvé(e) sur la case")
                    break
            
            return collected_count > 0
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte intensive de {resource}: {str(e)}")
            return False

    def _generate_emergency_exploration_target(self) -> Tuple[int, int]:
        """Génère une cible d'exploration d'urgence."""
        try:
            max_radius = 5
            x = random.randint(-max_radius, max_radius)
            y = random.randint(-max_radius, max_radius)
            if (x, y) == (0, 0):
                x, y = 1, 0
            return (x, y)
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de cible d'exploration d'urgence: {str(e)}")
            return (1, 0)

    def _handle_team_messages(self) -> bool:
        """Gère les messages de l'équipe reçus via broadcast.
        
        Returns:
            bool: True si un message a été traité, False sinon
        """
        try:
            message = self.communicator.receive_broadcast()
            if not message:
                return False
                
            if message.get("team") != self.player.team:
                return False
                
            action = message.get("action")
            data = message.get("data", "")
            
            if action == "RITUAL_LVL3_START":
                self.logger.info(f"🤝 Mon équipe a besoin d'aide pour un rituel niveau 3 ! Je réponds.")
                
                try:
                    coords = tuple(map(int, data.split(',')))
                    self.target_position = coords
                    self.state = "JOINING_RITUAL"
                    
                    self.communicator.send_team_message("COMING_FOR_RITUAL", f"{self.player.id}")
                    return True
                except ValueError:
                    self.logger.warning(f"❌ Coordonnées invalides dans le message: {data}")
                    return False
                    
            elif action == "EGG_LAID":
                self.logger.info(f"🥚 Un coéquipier a pondu un œuf à {data}")
                return False
                
            elif action == "COMING_FOR_RITUAL":
                self.logger.info(f"👥 Coéquipier {data} arrive pour le rituel")
                return False
                
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement des messages d'équipe: {str(e)}")
            return False

    def _has_resources_for_level(self, level: int) -> bool:
        """Vérifie si l'IA a les ressources nécessaires pour un niveau donné.
        
        Args:
            level (int): Niveau cible
            
        Returns:
            bool: True si l'IA a toutes les ressources nécessaires
        """
        try:
            requirements = {
                2: {"linemate": 1},
                3: {"linemate": 1, "deraumere": 1, "sibur": 1},
                4: {"linemate": 1, "deraumere": 1, "sibur": 2, "phiras": 1},
                5: {"linemate": 1, "deraumere": 2, "sibur": 1, "mendiane": 3},
                6: {"linemate": 1, "deraumere": 2, "sibur": 3, "phiras": 1},
                7: {"linemate": 2, "deraumere": 2, "sibur": 2, "mendiane": 2, "phiras": 2, "thystame": 1},
                8: {"linemate": 1, "deraumere": 1, "sibur": 2, "mendiane": 1, "phiras": 1, "thystame": 1}
            }
            
            if level not in requirements:
                self.logger.warning(f"Niveau {level} non supporté")
                return False
                
            needed = requirements[level]
            inventory = self.inventory_manager.inventory
            
            for resource, quantity in needed.items():
                if inventory.get(resource, 0) < quantity:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification des ressources pour le niveau {level}: {str(e)}")
            return False