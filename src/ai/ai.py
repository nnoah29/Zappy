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
        self.state = "EMERGENCY_FOOD_SEARCH"
        self.target_resource = None
        self.target_position = None
        
        self.update_cooldown = 1
        
        self.FOOD_CRITICAL_LEVEL = 5
        self.FOOD_SAFE_LEVEL = 15
        
        self.vision_manager = VisionManager(protocol, player, map, logger)
        self.inventory_manager = InventoryManager(protocol, player, logger)
        self.movement_manager = MovementManager(protocol, player, map, self.vision_manager, logger)
        self.elevation_manager = ElevationManager(protocol, self.vision_manager, self.movement_manager, logger)
        self.communicator = PlayerCommunicator(protocol, player, logger)
        self.reproduction_manager = ReproductionManager(protocol, logger)
        
        self.last_update = 0

        self.elevation_in_progress = False
        self.elevation_start_time = 0

        self.team_status = {}
        self.team_leader_id = None
        self.current_ritual_target = None
        self.ritual_participants_needed = 0
        self.target_resource = None

    def update(self) -> bool:
        """Met à jour l'IA et exécute une action.
        
        Returns:
            bool: True si l'IA continue de fonctionner
        """
        try:
            current_time = time.time()
            
            if self.state == "EMERGENCY_FOOD_SEARCH":
                cooldown = 0.1
            else:
                cooldown = self.update_cooldown
            
            if current_time - self.last_update < cooldown:
                return True
            
            self.last_update = current_time
            
            if not self.vision_manager.update_vision():
                self.logger.warning("Échec de la mise à jour de la vision")
                return True
            
            if not self.inventory_manager.update_inventory():
                self.logger.warning("Échec de la mise à jour de l'inventaire")
                return True
            
            if self.inventory_manager.inventory['food'] <= 0:
                self.logger.error("Le joueur est mort de faim")
                return False
            
            self._update_state()
            
            return self._execute_action()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'IA: {str(e)}")
            return True

    def _update_state(self) -> None:
        """Met à jour l'état de l'IA."""
        try:
            if self.inventory_manager.inventory['food'] < 5:
                self.logger.debug("État changé: EMERGENCY_FOOD_SEARCH (critique)")
                self.state = "EMERGENCY_FOOD_SEARCH"
                return
                
            if self.elevation_manager.can_elevate():
                self.logger.debug("État changé: ELEVATING")
                self.state = "ELEVATING"
                return
                
            needed_resources = self.elevation_manager.get_needed_resources()
            if needed_resources:
                prioritized_resources = self._prioritize_resources(needed_resources)
                self.logger.debug(f"État changé: GATHERING_RESOURCES {prioritized_resources[0]} (priorité)")
                self.state = "GATHERING_RESOURCES"
                self.target_resource = prioritized_resources[0]
                return
                
            if self.inventory_manager.inventory['food'] < 10:
                self.logger.debug("État changé: SURVIVAL_BUFFERING (maintenance)")
                self.state = "SURVIVAL_BUFFERING"
                return
                
            self.logger.debug("NORMAL_OPERATIONS")
            self.state = "NORMAL_OPERATIONS"
            self.target_resource = None
            
            if not self.target_position:
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
            food_level = self.inventory_manager.inventory['food']

            if food_level < self.FOOD_CRITICAL_LEVEL:
                self.state = "EMERGENCY_FOOD_SEARCH"
                self.logger.critical("🚨🚨 MODE URGENCE : Survie. Refresh de la vision immédiat.")
                self.vision_manager.force_update_vision()

                target = self.vision_manager.find_nearest_object("food")
                
                if target:
                    if target == (0, 0):
                        self.logger.critical("🚨 NOURRITURE SUR MA CASE (confirmé), COLLECTE IMMÉDIATE")
                        if self._collect_resource_intensively("food"):
                            self.logger.critical("✅ NOURRITURE COLLECTÉE EN MODE URGENCE")
                        else:
                            self.logger.critical("❌ ÉCHEC DE LA COLLECTE EN MODE URGENCE")
                    else:
                        self.logger.critical(f"🚨 NOURRITURE TROUVÉE À {target} (confirmé), DÉPLACEMENT URGENT")
                        if self.movement_manager.move_to(target):
                            self.logger.critical("✅ DÉPLACEMENT URGENT RÉUSSI, VÉRIFICATION FINALE...")
                            
                            self.vision_manager.force_update_vision()
                            current_tile = self.vision_manager.vision_data[0]
                            if 'food' in current_tile:
                                self.logger.critical("✅ NOURRITURE CONFIRMÉE, COLLECTE IMMÉDIATE")
                                if self._collect_resource_intensively("food"):
                                    self.logger.critical("✅ NOURRITURE COLLECTÉE EN MODE URGENCE")
                                else:
                                    self.logger.critical("❌ ÉCHEC DE LA COLLECTE (Post-vérification)")
                            else:
                                self.logger.warning("❌ La nourriture a disparu juste avant la collecte !")
                else:
                    self.logger.critical("🚨 AUCUNE NOURRITURE EN VUE (confirmé), EXPLORATION D'URGENCE")
                    exploration_target = self._generate_emergency_exploration_target()
                    if exploration_target:
                        self.logger.critical(f"🚨 EXPLORATION D'URGENCE VERS {exploration_target}")
                        if self.movement_manager.move_to(exploration_target):
                            self.vision_manager.force_update_vision()
                            if self._collect_available_resources():
                                self.logger.critical("✅ RESSOURCES TROUVÉES EN EXPLORATION D'URGENCE")
                    else:
                        self.logger.critical("🚨 MOUVEMENT ALÉATOIRE D'URGENCE")
                        random_direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                        if self.movement_manager.move_to(random_direction):
                            self.vision_manager.force_update_vision()
                            if self._collect_available_resources():
                                self.logger.critical("✅ RESSOURCES TROUVÉES EN MOUVEMENT ALÉATOIRE")
                
                return True  # On a géré le tour en mode urgence, on s'arrête là.

            if food_level < self.FOOD_SAFE_LEVEL:
                self.state = "SURVIVAL_BUFFERING"
                self.logger.warning(f"⚠️ MODE SÉCURITÉ : Constitution des réserves (actuel: {food_level}/{self.FOOD_SAFE_LEVEL}). Objectifs secondaires suspendus.")
                
                target = self.vision_manager.find_nearest_object("food")
                if target:
                    if target == (0, 0):
                        self.logger.info("🎯 Nourriture sur ma case, collecte directe.")
                        if self._collect_resource_intensively("food"):
                            self.logger.info("✅ Nourriture collectée pour les réserves")
                        else:
                            self.logger.warning("❌ Échec de la collecte de sécurité")
                    else:
                        self.logger.info(f"🎯 Cible de sécurité : nourriture à {target}.")
                        if self.movement_manager.move_to(target):
                            self.logger.info("✅ Déplacement réussi, vérification finale...")
                            
                            self.vision_manager.force_update_vision()
                            current_tile = self.vision_manager.vision_data[0]
                            if 'food' in current_tile:
                                self.logger.info("✅ Nourriture confirmée, collecte...")
                                if self._collect_resource_intensively("food"):
                                    self.logger.info("✅ Nourriture collectée pour les réserves")
                                else:
                                    self.logger.warning("❌ Échec de la collecte (Post-vérification)")
                            else:
                                self.logger.warning("❌ La nourriture a disparu juste avant la collecte !")
                else:
                    self.logger.info("🔍 Pas de nourriture en vue, exploration pour les réserves...")
                    self._explore_for_food()
                
                return True  # On ne fait RIEN d'autre ce tour-ci.

            self.logger.info(f"✅ Niveau de nourriture sécurisé ({food_level}/{self.FOOD_SAFE_LEVEL}). Reprise des opérations normales.")
            
            self._update_state_when_safe()

            if self.state == "ELEVATING":
                self.logger.info("🌟 Élévation en cours...")
                
                if self.elevation_in_progress:
                    elapsed_time = time.time() - self.elevation_start_time
                    if elapsed_time > 10.0:
                        self.logger.warning("⏰ Timeout de l'élévation, retour aux opérations normales")
                        self.elevation_in_progress = False
                        self.state = "NORMAL_OPERATIONS"
                        return True
                    
                    response = self.protocol.receive_message()
                    if response:
                        if "Current level:" in response:
                            new_level = int(response.split(":")[1].strip())
                            self.player.level = new_level
                            self.logger.info(f"🎉 Élévation réussie ! Nouveau niveau : {new_level}")
                            self.elevation_in_progress = False
                            self.state = "NORMAL_OPERATIONS"
                            return True
                        elif "ko" in response:
                            self.logger.warning("❌ Élévation échouée")
                            self.elevation_in_progress = False
                            self.state = "NORMAL_OPERATIONS"
                            return True
                
                return True
            
            if self.state == "JOINING_RITUAL":
                self.logger.info("🤝 Rejoindre un rituel d'équipe...")
                
                if self.ritual_target_position:
                    if self.movement_manager.move_to(self.ritual_target_position):
                        self.logger.info("✅ Arrivé au point de rituel, attente...")
                        self.state = "WAITING_FOR_RITUAL_PARTNER"
                    else:
                        self.logger.warning("❌ Impossible d'atteindre le point de rituel")
                        self.state = "NORMAL_OPERATIONS"
                        self.ritual_target_position = None
                else:
                    self.logger.warning("❌ Aucune position de rituel définie")
                    self.state = "NORMAL_OPERATIONS"
                return True
            
            if self.state == "WAITING_FOR_RITUAL_PARTNER":
                self.logger.info("⏳ En attente d'un partenaire pour le rituel niveau 3...")
                
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
            
            if self.state == "AWAITING_PARTICIPANTS":
                self.logger.info(f"⏳ En attente des participants pour le rituel (besoin: {self.ritual_participants_needed})...")
                
                current_tile_content = self.vision_manager.vision_data[0] if self.vision_manager.vision_data else []
                player_count = current_tile_content.count('player')
                
                if player_count >= self.ritual_participants_needed:
                    self.logger.info(f"👥 Participants suffisants détectés ({player_count}/{self.ritual_participants_needed}) ! Lancement du rituel !")
                    response = self.protocol.incantation()
                    
                    if response == "ko":
                        self.logger.error("❌ Échec de l'incantation de groupe")
                        self.state = "NORMAL_OPERATIONS"
                        self.ritual_participants_needed = 0
                    elif response == "Elevation underway":
                        self.logger.info("🌟 Élévation de groupe en cours ! Attente du résultat...")
                        self.elevation_in_progress = True
                        self.elevation_start_time = time.time()
                        self.state = "ELEVATING"
                        self.ritual_participants_needed = 0
                    else:
                        self.logger.warning(f"⚠️ Réponse inattendue lors de l'incantation de groupe: {response}")
                        self.state = "NORMAL_OPERATIONS"
                        self.ritual_participants_needed = 0
                else:
                    self.logger.debug(f"⏳ Toujours en attente... ({player_count}/{self.ritual_participants_needed} joueurs)")
                
                return True
            
            if self.state == "GATHERING_RESOURCES":
                if not hasattr(self, 'target_resource') or not self.target_resource:
                    self.logger.warning("❌ Aucune ressource cible définie pour la collecte d'équipe")
                    self.state = "NORMAL_OPERATIONS"
                    return True
                
                self.logger.info(f"🔍 Collecte de {self.target_resource} pour l'équipe...")
                
                target = self.vision_manager.find_nearest_object(self.target_resource)
                if target:
                    self.logger.info(f"🎯 {self.target_resource} trouvé à {target}, déplacement...")
                    if self.movement_manager.move_to(target):
                        if self._collect_resource_intensively(self.target_resource):
                            self.logger.info(f"✅ {self.target_resource} collecté pour l'équipe")
                            
                            if self.player.level > 1 and self.team_leader_id != str(self.player.id):
                                self.communicator.send_team_message("RESOURCE_FOUND", f"{self.target_resource}:{self.player.x},{self.player.y}")
                            
                            self.state = "NORMAL_OPERATIONS"
                            self.target_resource = None
                        else:
                            self.logger.warning(f"❌ Échec de la collecte de {self.target_resource}")
                else:
                    self.logger.info(f"🔍 Aucun {self.target_resource} en vue, exploration...")
                    exploration_target = self._generate_smart_exploration_target()
                    if exploration_target:
                        self.logger.info(f"🎯 Exploration vers {exploration_target} pour trouver du {self.target_resource}")
                        if self.movement_manager.move_to(exploration_target):
                            self.logger.info("✅ Déplacement d'exploration réussi")
                
                return True
            
            if self.state == "FOLLOWING_ORDERS":
                self.logger.info("🤖 Mode suiveur : j'attends les ordres du leader...")
                
                self._explore()
                return True
            
            self.state = "NORMAL_OPERATIONS"
            self._explore()
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de l'action: {str(e)}")
            return False

    def _update_map_from_vision(self) -> None:
        """Met à jour la carte avec les données de vision."""
        try:
            if not self.vision_manager.vision_data:
                return
            
            current_tile = self.vision_manager.vision_data[0]
            self.map.update_tile(self.player.x, self.player.y, current_tile)
            
            for i, tile_content in enumerate(self.vision_manager.vision_data[1:], 1):
                relative_pos = self._get_relative_position(i)
                if relative_pos:
                    abs_x = (self.player.x + relative_pos[0]) % self.map.width
                    abs_y = (self.player.y + relative_pos[1]) % self.map.height
                    self.map.update_tile(abs_x, abs_y, tile_content)
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la carte: {str(e)}")

    def _get_relative_position(self, index: int) -> Tuple[int, int]:
        """Calcule la position relative d'une case dans la vision.
        
        Args:
            index (int): Index de la case dans la vision
            
        Returns:
            Tuple[int, int]: Position relative (x, y)
        """
        try:
            if index == 0:
                return (0, 0)
            
            circle = 1
            while index > circle * 8:
                index -= circle * 8
                circle += 1
            
            pos_in_circle = (index - 1) % (circle * 8)
            segment = pos_in_circle // circle
            
            if segment == 0:
                return (0, -circle)
            elif segment == 1:
                return (circle, -circle)
            elif segment == 2:
                return (circle, 0)
            elif segment == 3:
                return (circle, circle)
            elif segment == 4:
                return (0, circle)
            elif segment == 5:
                return (-circle, circle)
            elif segment == 6:
                return (-circle, 0)
            else:
                return (-circle, -circle)
                
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de la position relative: {str(e)}")
            return (0, 0)

    def _explore(self) -> None:
        """Exploration intelligente de la carte."""
        try:
            target = self._generate_smart_exploration_target()
            if target:
                self.logger.debug(f"🎯 Exploration vers {target}")
                if self.movement_manager.move_to(target):
                    self.logger.debug("✅ Déplacement d'exploration réussi")
                    self._collect_available_resources()
                else:
                    self.logger.debug("❌ Échec du déplacement d'exploration")
            else:
                self.logger.debug("🔍 Aucune cible d'exploration trouvée")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exploration: {str(e)}")

    def _generate_smart_exploration_target(self) -> Tuple[int, int]:
        """Génère une cible d'exploration intelligente.
        
        Returns:
            Tuple[int, int]: Coordonnées de la cible d'exploration
        """
        try:
            unexplored_target = self._find_unexplored_target()
            if unexplored_target:
                return unexplored_target
            
            rare_resource_target = self._find_rare_resource_target()
            if rare_resource_target:
                return rare_resource_target
            
            return self._generate_random_exploration_target()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de cible d'exploration: {str(e)}")
            return (0, 0)

    def _find_unexplored_target(self) -> Optional[Tuple[int, int]]:
        """Trouve une cible inexplorée.
        
        Returns:
            Optional[Tuple[int, int]]: Coordonnées de la cible ou None
        """
        try:
            for radius in range(1, 6):
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if abs(dx) + abs(dy) == radius:
                            target_x = (self.player.x + dx) % self.map.width
                            target_y = (self.player.y + dy) % self.map.height
                            
                            if not self.map.is_explored(target_x, target_y):
                                return (target_x, target_y)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de cible inexplorée: {str(e)}")
            return None

    def _find_rare_resource_target(self) -> Optional[Tuple[int, int]]:
        """Trouve une cible avec des ressources rares.
        
        Returns:
            Optional[Tuple[int, int]]: Coordonnées de la cible ou None
        """
        try:
            rare_resources = ['thystame', 'phiras', 'mendiane']
            
            for radius in range(1, 4):
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if abs(dx) + abs(dy) == radius:
                            target_x = (self.player.x + dx) % self.map.width
                            target_y = (self.player.y + dy) % self.map.height
                            
                            tile_content = self.map.get_tile_content(target_x, target_y)
                            if tile_content:
                                for resource in rare_resources:
                                    if resource in tile_content:
                                        return (target_x, target_y)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de ressources rares: {str(e)}")
            return None

    def _generate_random_exploration_target(self) -> Tuple[int, int]:
        """Génère une cible d'exploration aléatoire.
        
        Returns:
            Tuple[int, int]: Coordonnées de la cible
        """
        try:
            import random
            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            distance = random.randint(2, 5)
            
            target_x = (self.player.x + direction[0] * distance) % self.map.width
            target_y = (self.player.y + direction[1] * distance) % self.map.height
            
            return (target_x, target_y)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de cible aléatoire: {str(e)}")
            return (0, 0)

    def _collect_available_resources(self) -> bool:
        """Collecte toutes les ressources disponibles sur la case actuelle.
        
        Returns:
            bool: True si au moins une ressource a été collectée
        """
        try:
            if not self.vision_manager.vision_data:
                return False
            
            current_tile = self.vision_manager.vision_data[0]
            collected = False
            
            if 'food' in current_tile:
                if self.protocol.take('food'):
                    self.logger.debug("🍎 Nourriture collectée")
                    collected = True
            
            resources = ['linemate', 'deraumere', 'sibur', 'mendiane', 'phiras', 'thystame']
            for resource in resources:
                if resource in current_tile:
                    if self.protocol.take(resource):
                        self.logger.debug(f"💎 {resource} collecté")
                        collected = True
            
            return collected
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte de ressources: {str(e)}")
            return False

    def _collect_resource_intensively(self, resource: str) -> bool:
        """Collecte intensivement une ressource spécifique.
        
        Args:
            resource (str): Nom de la ressource à collecter
            
        Returns:
            bool: True si la ressource a été collectée
        """
        try:
            if not self.vision_manager.vision_data:
                return False
            
            current_tile = self.vision_manager.vision_data[0]
            
            if resource in current_tile:
                success = self.protocol.take(resource)
                if success:
                    self.logger.info(f"✅ {resource} collecté avec succès")
                    return True
                else:
                    self.logger.warning(f"❌ Échec de la collecte de {resource}")
                    return False
            else:
                self.logger.debug(f"🔍 {resource} non trouvé sur la case actuelle")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte intensive de {resource}: {str(e)}")
            return False

    def _generate_emergency_exploration_target(self) -> Tuple[int, int]:
        """Génère une cible d'exploration d'urgence pour la survie.
        
        Returns:
            Tuple[int, int]: Coordonnées de la cible d'urgence
        """
        try:
            import random
            
            for radius in range(1, 4):
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if abs(dx) + abs(dy) == radius:
                            target_x = (self.player.x + dx) % self.map.width
                            target_y = (self.player.y + dy) % self.map.height
                            
                            tile_content = self.map.get_tile_content(target_x, target_y)
                            if tile_content and 'food' in tile_content:
                                return (target_x, target_y)
            
            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            distance = random.randint(3, 8)
            
            target_x = (self.player.x + direction[0] * distance) % self.map.width
            target_y = (self.player.y + direction[1] * distance) % self.map.height
            
            return (target_x, target_y)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de cible d'urgence: {str(e)}")
            return (0, 0)

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
            
            sender_id = message.get("sender_id", "unknown")
            self._update_team_status(sender_id, action, data)
            
            if action == "RITUAL_CALL":
                try:
                    parts = data.split(":")
                    target_level = int(parts[0])
                    initiator_id = parts[1]
                    coords_str = parts[2]
                    
                    if (self.player.level == target_level - 1 and 
                        self.state in ["NORMAL_OPERATIONS", "FOLLOWING_ORDERS"]):
                        
                        self.logger.info(f"🤝 Appel au rituel niveau {target_level} par {initiator_id} ! Je réponds.")
                        
                        coords = tuple(map(int, coords_str.split(',')))
                        self.target_position = coords
                        self.state = "JOINING_RITUAL"
                        self.current_ritual_target = target_level
                        
                        self.communicator.send_team_message("RITUAL_JOIN", f"{target_level}:{self.player.id}")
                        return True
                    else:
                        self.logger.info(f"⚠️ Je suis niveau {self.player.level}, je ne peux pas participer au rituel niveau {target_level}")
                        return False
                        
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"❌ Format de message RITUAL_CALL invalide: {data}")
                    return False
                    
            elif action == "RITUAL_JOIN":
                try:
                    parts = data.split(":")
                    target_level = int(parts[0])
                    participant_id = parts[1]
                    
                    self.logger.info(f"👥 {participant_id} rejoint le rituel niveau {target_level}")
                    return False
                    
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"❌ Format de message RITUAL_JOIN invalide: {data}")
                    return False
                    
            elif action == "GATHER_REQUEST":
                resource_name = data.strip()
                
                if (self.state in ["NORMAL_OPERATIONS", "FOLLOWING_ORDERS"] and 
                    self.inventory_manager.inventory.get(resource_name, 0) == 0):
                    
                    self.logger.info(f"🔍 L'équipe a besoin de {resource_name}. Je vais en chercher.")
                    self.state = "GATHERING_RESOURCES"
                    self.target_resource = resource_name
                    return True
                    
            elif action == "RESOURCE_FOUND":
                try:
                    parts = data.split(":")
                    resource_name = parts[0]
                    coords_str = parts[1]
                    
                    if self.state == "GATHERING_RESOURCES" and self.target_resource == resource_name:
                        coords = tuple(map(int, coords_str.split(',')))
                        self.target_position = coords
                        self.logger.info(f"🎯 {resource_name} trouvé par l'équipe à {coords}. Je m'y dirige.")
                        return True
                        
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"❌ Format de message RESOURCE_FOUND invalide: {data}")
                    return False
                    
            elif action == "EGG_LAID":
                try:
                    coords = tuple(map(int, data.split(',')))
                    self.logger.info(f"🥚 Un coéquipier a pondu un œuf à {coords}")
                    return False
                    
                except ValueError as e:
                    self.logger.warning(f"❌ Format de message EGG_LAID invalide: {data}")
                    return False
                    
            elif action == "LEADER_ANNOUNCEMENT":
                try:
                    parts = data.split(":")
                    leader_id = parts[0]
                    leader_level = int(parts[1])
                    
                    if leader_level > self.player.level:
                        self.team_leader_id = leader_id
                        self.logger.info(f"👑 {leader_id} (niveau {leader_level}) est le nouveau leader de l'équipe")
                        
                        if self.state in ["NORMAL_OPERATIONS"]:
                            self.state = "FOLLOWING_ORDERS"
                            self.logger.info("🤖 Je passe en mode suiveur")
                            return True
                            
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"❌ Format de message LEADER_ANNOUNCEMENT invalide: {data}")
                    return False
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement des messages d'équipe: {str(e)}")
            return False

    def _update_team_status(self, player_id: str, action: str, data: str) -> None:
        """Met à jour le statut de l'équipe avec les informations reçues.
        
        Args:
            player_id (str): ID du joueur qui a envoyé le message
            action (str): Action effectuée
            data (str): Données du message
        """
        try:
            current_time = time.time()
            
            if player_id not in self.team_status:
                self.team_status[player_id] = {
                    'level': 1,
                    'task': 'unknown',
                    'last_seen': current_time,
                    'position': None
                }
            
            self.team_status[player_id]['last_seen'] = current_time
            
            if action == "RITUAL_CALL":
                self.team_status[player_id]['task'] = 'initiating_ritual'
                try:
                    parts = data.split(":")
                    self.team_status[player_id]['level'] = int(parts[0])
                    coords_str = parts[2]
                    coords = tuple(map(int, coords_str.split(',')))
                    self.team_status[player_id]['position'] = coords
                except:
                    pass
                    
            elif action == "RITUAL_JOIN":
                self.team_status[player_id]['task'] = 'joining_ritual'
                
            elif action == "GATHER_REQUEST":
                self.team_status[player_id]['task'] = 'gathering_resources'
                
            elif action == "LEADER_ANNOUNCEMENT":
                try:
                    parts = data.split(":")
                    self.team_status[player_id]['level'] = int(parts[1])
                    self.team_status[player_id]['task'] = 'leading_team'
                except:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du statut d'équipe: {str(e)}")

    def _announce_leadership(self) -> None:
        """Annonce sa position de leader si elle est la plus haute de l'équipe."""
        try:
            my_level = self.player.level
            is_highest = True
            
            for player_id, status in self.team_status.items():
                if player_id != str(self.player.id) and status.get('level', 0) >= my_level:
                    is_highest = False
                    break
            
            if is_highest and self.team_leader_id != str(self.player.id):
                self.team_leader_id = str(self.player.id)
                self.communicator.send_team_message("LEADER_ANNOUNCEMENT", f"{self.player.id}:{my_level}")
                self.logger.info(f"👑 J'annonce ma position de leader (niveau {my_level})")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'annonce de leadership: {str(e)}")

    def _detect_and_counter_enemy_rituals(self) -> bool:
        """Détecte et contrecarre les rituels ennemis.
        
        Returns:
            bool: True si une action de contre-mesure a été effectuée
        """
        try:
            if not self.vision_manager.vision_data:
                return False
            
            current_tile_content = self.vision_manager.vision_data[0]
            
            player_count = current_tile_content.count('player')
            stone_count = sum(current_tile_content.count(stone) for stone in ['linemate', 'deraumere', 'sibur', 'mendiane', 'phiras', 'thystame'])
            
            if player_count >= 2 and stone_count >= 2:
                self.logger.warning(f"🚨 Rituel ennemi potentiel détecté ! {player_count} joueurs, {stone_count} pierres")
                
                success = self.protocol.eject()
                if success:
                    self.logger.info("💨 Eject lancé pour contrer le rituel ennemi")
                    return True
                else:
                    self.logger.debug("❌ Eject échoué (probablement pas d'ennemis sur la case)")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la détection de rituels ennemis: {str(e)}")
            return False

    def _should_fork_emergency(self) -> bool:
        """Détermine si une reproduction d'urgence est nécessaire.
        
        Returns:
            bool: True si une reproduction d'urgence est nécessaire
        """
        try:
            current_time = time.time()
            active_players = 0
            
            for player_id, status in self.team_status.items():
                if current_time - status.get('last_seen', 0) < 30:
                    active_players += 1
            
            active_players += 1
            
            if active_players < 6 and self.inventory_manager.inventory.get('food', 0) > 15:
                self.logger.warning(f"🚨 Équipe en sous-effectif ({active_players}/6). Reproduction d'urgence nécessaire.")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation de la reproduction d'urgence: {str(e)}")
            return False

    def _explore_for_food(self):
        """Fonction d'exploration spécifiquement pour trouver de la nourriture."""
        self.logger.info("🗺 Exploration ciblée pour la nourriture...")
        exploration_target = self._generate_emergency_exploration_target()
        if exploration_target:
            self.logger.info(f"🎯 Exploration vers {exploration_target} pour trouver de la nourriture")
            if self.movement_manager.move_to(exploration_target):
                self.vision_manager.force_update_vision()
                if self._collect_available_resources():
                    self.logger.info("✅ Ressources trouvées lors de l'exploration de sécurité")
        else:
            random_direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            if self.movement_manager.move_to(random_direction):
                self.vision_manager.force_update_vision()
                if self._collect_available_resources():
                    self.logger.info("✅ Ressources trouvées lors du mouvement aléatoire")

    def _update_state_when_safe(self) -> None:
        """Met à jour l'état de l'IA uniquement quand la survie est assurée."""
        try:
            if self._handle_team_messages():
                return
            
            if self._detect_and_counter_enemy_rituals():
                return
            
            if self._should_fork_emergency():
                self.logger.warning("🥚 Reproduction d'urgence pour maintenir l'effectif de l'équipe")
                if self.reproduction_manager.reproduce():
                    self.communicator.send_team_message("EGG_LAID", f"{self.player.x},{self.player.y}")
                return
            
            if 1 <= self.player.level <= 7:
                next_level = self.player.level + 1
                self.logger.info(f"🎯 Objectif : Préparer l'élévation pour le niveau {next_level}.")
                
                if self.player.level >= 4:
                    self.logger.info("👑 Mode Reine : Je reste sur place et coordonne l'équipe")
                    
                    self._announce_leadership()
                    
                    requirements = self.elevation_manager.ELEVATION_REQUIREMENTS.get(next_level, {})
                    for res, count in requirements.items():
                        if res != "players" and self.inventory_manager.inventory.get(res, 0) < count:
                            needed = count - self.inventory_manager.inventory.get(res, 0)
                            self.logger.info(f"📢 Demande à l'équipe : {needed} {res}")
                            self.communicator.send_team_message("GATHER_REQUEST", res)
                    
                    if self.reproduction_manager.can_fork() and self.inventory_manager.inventory['food'] > 25:
                        self.logger.info("🥚 Reproduction royale pour maintenir l'effectif")
                        if self.reproduction_manager.reproduce():
                            self.communicator.send_team_message("EGG_LAID", f"{self.player.x},{self.player.y}")
                    return
                    
                else:
                    self.logger.info("🔨 Mode Ouvrière : Je collecte activement et aide aux rituels")
                    
                    if self.player.level >= 3:
                        self._announce_leadership()
                    
                    requirements = self.elevation_manager.ELEVATION_REQUIREMENTS.get(next_level, {})
                    needed = []
                    for res, count in requirements.items():
                        if res != "players" and self.inventory_manager.inventory.get(res, 0) < count:
                            needed.extend([res] * (count - self.inventory_manager.inventory.get(res, 0)))
                    
                    if needed:
                        target_resource = self._prioritize_resources(list(set(needed)))[0]
                        self.logger.info(f"🔍 Ressources manquantes pour niveau {next_level} : {needed}. Recherche de {target_resource}...")
                        
                        if self.team_leader_id == str(self.player.id):
                            self.communicator.send_team_message("GATHER_REQUEST", target_resource)
                        
                        target = self.vision_manager.find_nearest_object(target_resource)
                        if target:
                            self.logger.info(f"🎯 {target_resource} trouvé à {target}, déplacement...")
                            if self.movement_manager.move_to(target):
                                if self._collect_resource_intensively(target_resource):
                                    self.logger.info(f"✅ {target_resource} collecté avec succès")
                                    
                                    if self.team_leader_id != str(self.player.id):
                                        self.communicator.send_team_message("RESOURCE_FOUND", f"{target_resource}:{self.player.x},{self.player.y}")
                            else:
                                self.logger.info(f"🔍 Aucun {target_resource} en vue, exploration...")
                                exploration_target = self._generate_smart_exploration_target()
                                if exploration_target:
                                    self.logger.info(f"🎯 Exploration vers {exploration_target} pour trouver du {target_resource}")
                                    if self.movement_manager.move_to(exploration_target):
                                        self.logger.info("✅ Déplacement d'exploration réussi")
                        return
                    
                    current_tile_content = self.vision_manager.vision_data[0] if self.vision_manager.vision_data else []
                    player_count = current_tile_content.count('player')
                    required_players = self.elevation_manager._get_required_players(next_level)
                    
                    if player_count < required_players:
                        if self.player.level > 1:
                            self.logger.info(f"👥 Pas assez de joueurs pour le rituel niveau {next_level} ({player_count}/{required_players}). J'appelle à l'aide.")
                            self.communicator.send_team_message("RITUAL_CALL", f"{next_level}:{self.player.id}:{self.player.x},{self.player.y}")
                            self.state = "AWAITING_PARTICIPANTS"
                            self.ritual_participants_needed = required_players
                            return
                        else:
                            self.logger.info(f"👥 Pas assez de joueurs pour le rituel niveau {next_level} ({player_count}/{required_players}). Je continue à chercher des ressources.")
                            return
                    
                    resources_deposited = False
                    for res, count in requirements.items():
                        if res == "players":
                            continue
                        for _ in range(count):
                            if self.inventory_manager.inventory.get(res, 0) > 0:
                                if self.protocol.set(res):
                                    self.logger.info(f"✅ {res} déposé sur la case")
                                    resources_deposited = True
                                else:
                                    self.logger.warning(f"❌ Échec du dépôt de {res}")
                    
                    if resources_deposited:
                        current_tile_content = self.vision_manager.vision_data[0] if self.vision_manager.vision_data else []
                        ready = True
                        for res, count in requirements.items():
                            if res != "players" and current_tile_content.count(res) < count:
                                ready = False
                                break
                        
                        if ready and player_count >= required_players:
                            self.logger.info(f"✨ Conditions parfaites ! Lancement de l'incantation pour le niveau {next_level} !")
                            response = self.protocol.incantation()
                            
                            if response == "Elevation underway":
                                self.logger.info("🌟 Élévation en cours ! Attente du résultat...")
                                self.elevation_in_progress = True
                                self.elevation_start_time = time.time()
                                self.state = "ELEVATING"
                                return
                            elif response == "ko":
                                self.logger.error("❌ Échec de l'incantation")
                                return
                            else:
                                self.logger.warning(f"⚠️ Réponse inattendue lors de l'incantation: {response}")
                                return
                    
                    return
            
            # Logique pour le niveau maximum (8)
            elif self.player.level == 8:
                self.logger.info("🏆 Niveau maximum atteint ! Je me concentre sur la reproduction et l'aide à l'équipe.")
                
                if self.reproduction_manager.can_fork() and self.inventory_manager.inventory['food'] > 20:
                    self.logger.info("🥚 Conditions optimales pour la reproduction.")
                    if self.reproduction_manager.reproduce():
                        self.communicator.send_team_message("EGG_LAID", f"{self.player.x},{self.player.y}")
                    return
                
                if self.team_status:
                    for player_id, status in self.team_status.items():
                        if status.get('task') == 'gathering_resources':
                            self.logger.info("🤝 Aide à l'équipe en cherchant des ressources")
                            self._explore()
                            return
                
                return
            
            # Reproduction normale si conditions réunies
            if self.reproduction_manager.can_fork() and self.inventory_manager.inventory['food'] > 20:
                self.logger.info("🥚 Conditions optimales pour la reproduction.")
                if self.reproduction_manager.reproduce():
                    self.communicator.send_team_message("EGG_LAID", f"{self.player.x},{self.player.y}")
                return
            
            # État par défaut : exploration
            self.logger.debug("Aucune action spécifique, exploration par défaut.")
            self._explore()
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'état: {str(e)}")
            self.state = "NORMAL_OPERATIONS"