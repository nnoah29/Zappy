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
        
        self.FOOD_CRITICAL_LEVEL = 3
        self.FOOD_SAFE_LEVEL = 5
        
        self.vision_manager = VisionManager(protocol, player, map, logger)
        self.inventory_manager = InventoryManager(protocol, player, logger)
        self.movement_manager = MovementManager(protocol, player, map, self.vision_manager, logger)
        self.elevation_manager = ElevationManager(protocol, self.vision_manager, self.inventory_manager, logger)
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
        
        # Variables pour rejoindre les rituels
        self.ritual_target = None

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
            
            if not self.protocol.client.is_connected():
                self.logger.error("🔌 Connexion au serveur perdue, arrêt de l'IA")
                return False
            
            if self.elevation_in_progress:
                elevation_timeout = 60
                if current_time - self.elevation_start_time > elevation_timeout:
                    self.logger.warning(f"⏰ Timeout de l'élévation ({elevation_timeout}s), reprise des opérations normales")
                    self.elevation_in_progress = False
                    self.state = "NORMAL_OPERATIONS"
            
            if not self.vision_manager.update_vision():
                self.logger.warning("Échec de la mise à jour de la vision")
                return True
            
            if not self.inventory_manager.update_inventory():
                self.logger.warning("Échec de la mise à jour de l'inventaire")
                return True
            
            if self.inventory_manager.inventory['food'] <= 0:
                self.logger.critical("🚨🚨 NOURRITURE CRITIQUE (0) - Le serveur va probablement nous tuer ! 🚨🚨")
                self.state = "EMERGENCY_FOOD_SEARCH"
            
            self._update_state()
            
            return self._execute_action()
            
        except ConnectionError as e:
            self.logger.error(f"🔌 Erreur de connexion dans l'IA: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'IA: {str(e)}")
            return True

    def _update_state(self) -> None:
        """Met à jour l'état de l'IA."""
        try:
            # Vérifier si on peut s'élever (ressources + joueurs)
            if self.elevation_manager.can_elevate():
                self.logger.debug("État changé: ELEVATING (priorité absolue)")
                self.state = "ELEVATING"
                return
            
            if self.inventory_manager.inventory['food'] < 5:
                self.logger.debug("État changé: EMERGENCY_FOOD_SEARCH (critique)")
                self.state = "EMERGENCY_FOOD_SEARCH"
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

            self._collect_available_resources()

            if self.state == "ELEVATING":
                if self.elevation_in_progress:
                    self.logger.debug("⏳ Élévation en cours, attente du résultat...")
                    return True
                else:
                    self.logger.info("🚀 LANCEMENT DE L'ÉLÉVATION !")
                    success = self._handle_elevation()
                    if not success:
                        self.logger.warning("❌ Échec de l'élévation, retour aux opérations normales")
                        self.state = "NORMAL_OPERATIONS"
                        self.elevation_in_progress = False
                    return True

            if food_level < self.FOOD_SAFE_LEVEL:
                self.handle_survival()
                return True

            self.logger.info(f"✅ Nourriture sécurisée ({food_level}). Reprise des opérations.")
            self._update_state_when_safe()

            # Vérifier à nouveau l'état après _update_state_when_safe
            if self.state == "ELEVATING":
                if self.elevation_in_progress:
                    self.logger.debug("⏳ Élévation en cours, attente du résultat...")
                    return True
                else:
                    self.logger.info("🚀 LANCEMENT DE L'ÉLÉVATION !")
                    success = self._handle_elevation()
                    if not success:
                        self.logger.warning("❌ Échec de l'élévation, retour aux opérations normales")
                        self.state = "NORMAL_OPERATIONS"
                        self.elevation_in_progress = False
                    return True
            
            elif self.state == "GATHERING_RESOURCES":
                self._handle_gathering_resources()
            
            elif self.state == "AWAITING_PARTICIPANTS":
                self.logger.info(f"👥 Appel à l'aide pour le rituel niveau {self.player.level + 1}. Besoin de {self.ritual_participants_needed} joueurs.")
                self.communicator.send_team_message("RITUAL_CALL", f"{self.player.level + 1}:{self.player.id}:{self.player.x},{self.player.y}")
                time.sleep(1)
            
            elif self.state == "JOINING_RITUAL":
                if self.ritual_target:
                    self.logger.info(f"🎯 Rejoindre le rituel à la position {self.ritual_target}")
                    if self.movement_manager.move_to(self.ritual_target):
                        self.logger.info("✅ Arrivé à la position du rituel !")
                        # Une fois arrivé, on peut s'élever si les conditions sont remplies
                        if self.elevation_manager.can_elevate():
                            self.logger.info("✨ Conditions d'élévation remplies, lancement du rituel !")
                            self.state = "ELEVATING"
                        else:
                            self.logger.info("⏳ En attente que les conditions d'élévation soient remplies...")
                            self.state = "AWAITING_PARTICIPANTS"
                    else:
                        self.logger.warning("❌ Impossible d'atteindre la position du rituel")
                        self.state = "NORMAL_OPERATIONS"
                else:
                    self.logger.warning("❌ Pas de cible de rituel définie")
                    self.state = "NORMAL_OPERATIONS"

            else:
                self._explore()
                
            return True
                
        except Exception as e:
            self.logger.error(f"Erreur dans _execute_action: {e}", exc_info=True)
            return True

    def handle_survival(self):
        """Gère les états EMERGENCY_FOOD_SEARCH et SURVIVAL_BUFFERING."""
        if self.inventory_manager.inventory['food'] < self.FOOD_CRITICAL_LEVEL:
            self.logger.critical("🚨🚨 MODE URGENCE CRITIQUE.")
        else:
            self.logger.warning(f"⚠️ MODE SÉCURITÉ : Remplissage des réserves.")

        self.vision_manager.force_update_vision()
        target = self.vision_manager.find_nearest_object("food")
        
        if target:
            if self.movement_manager.move_to(target):
                self._collect_resource_intensively("food")
        else:
            self._explore_locally_for_food()

    def _handle_gathering_resources(self):
        """Gère la collecte de la ressource cible."""
        if not self.target_resource:
            self.state = "NORMAL_OPERATIONS"
            return

        self.logger.info(f"🔍 Recherche de {self.target_resource}.")
        target = self.vision_manager.find_nearest_object(self.target_resource)
        
        if target:
            if self.movement_manager.move_to(target):
                if self._collect_resource_intensively(self.target_resource):
                    self.vision_manager.force_update_vision()
        else:
            self._explore()

    def _handle_elevation(self) -> bool:
        """Gère le processus d'élévation, de la pose des pierres à l'incantation."""
        try:
            next_level = self.player.level + 1
            current_level = self.player.level
            requirements = self.elevation_manager.ELEVATION_REQUIREMENTS.get(current_level, {})
            
            self.logger.info(f"🎯 Préparation de l'élévation niveau {current_level} → {next_level}")
            self.logger.info(f"📋 Exigences : {requirements}")
            
            # Envoyer un broadcast pour tous les niveaux qui nécessitent plusieurs joueurs
            required_players = requirements.get('players', 1)
            if required_players > 1:
                self.logger.info(f"🔊 Envoi du broadcast pour rituel niveau {next_level} (besoin de {required_players} joueurs)")
                self.communicator.send_team_message(
                    "RITUAL_CALL", 
                    f"{next_level}:{self.player.id}:{self.player.x},{self.player.y}"
                )
                time.sleep(1)  # Petit délai pour éviter le spam
                
            for resource, count in requirements.items():
                if resource == "players":
                    continue
                on_tile = self.vision_manager.vision_data[0].count(resource) if self.vision_manager.vision_data else 0
                needed_on_tile = count - on_tile
                
                to_set = min(self.inventory_manager.inventory.get(resource, 0), needed_on_tile)
                
                if to_set > 0:
                    self.logger.info(f"📦 Dépose {to_set} {resource} pour le rituel (déjà {on_tile} sur la case, besoin de {count})")
                    for _ in range(to_set):
                        self.protocol.set(resource)
                        time.sleep(0.1)

            self.vision_manager.force_update_vision()
            
            if self.elevation_manager.can_elevate():
                self.logger.info(f"✨ Conditions parfaites ! Lancement de l'incantation pour le niveau {next_level} !")
                success = self.protocol.incantation()
                
                if success:
                    self.logger.info("🌟 Élévation en cours ! Attente du résultat...")
                    self.elevation_in_progress = True
                    self.elevation_start_time = time.time()
                    self.state = "ELEVATING"
                    return True
                else:
                    self.logger.error("❌ Échec de l'incantation")
                    return False
            else:
                current_tile_content = self.vision_manager.vision_data[0] if self.vision_manager.vision_data else []
                player_count = current_tile_content.count('player')
                # L'IA se compte elle-même
                total_players = player_count + 1
                required_players = requirements.get('players', 1)
                
                if total_players < required_players:
                    self.logger.info(f"👥 Pas assez de joueurs pour le rituel niveau {current_level} ({total_players}/{required_players}). J'appelle à l'aide.")
                    self.communicator.send_team_message("RITUAL_CALL", f"{next_level}:{self.player.id}:{self.player.x},{self.player.y}")
                    self.state = "AWAITING_PARTICIPANTS"
                    self.ritual_participants_needed = required_players
                    return True
                
                self.logger.warning("❌ Conditions d'élévation non remplies après pose des pierres")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion de l'élévation: {str(e)}")
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
            
            self.logger.info(f"🔍 Contenu de la case actuelle : {current_tile}")
            
            # Collecter TOUTES les ressources disponibles, pas seulement la nourriture
            all_resources = ['food', 'linemate', 'deraumere', 'sibur', 'mendiane', 'phiras', 'thystame']
            
            for resource in all_resources:
                if resource in current_tile:
                    self.logger.info(f"🎯 Tentative de collecte de {resource}...")
                    if self.protocol.take(resource):
                        self.logger.info(f"✅ {resource} collecté avec succès")
                        collected = True
                    else:
                        self.logger.warning(f"❌ Échec de la collecte de {resource}")
            
            if collected:
                self.logger.info("📦 Collecte terminée, mise à jour de l'inventaire...")
                self.inventory_manager.force_update_inventory()
            
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
        """Gère les messages de l'équipe reçus via broadcast."""
        try:
            message = self.communicator.receive_broadcast()
            if not message:
                return False
                
            if message.get("team") != self.player.team:
                return False
                
            action = message.get("action")
            data = message.get("data", "")
            
            # Ajout pour gérer le message RITUAL_LVL3_START
            if action == "RITUAL_LVL3_START":
                if self.player.level == 2:
                    self.logger.info("🤝 Réception appel rituel niveau 3 - je me dirige vers l'initiateur")
                    coords = tuple(map(int, data.split(',')))
                    self.target_position = coords
                    self.state = "JOINING_RITUAL"
                    self.current_ritual_target = 3
                    return True
                else:
                    self.logger.info(f"⚠ Je suis niveau {self.player.level}, je ne peux pas participer")
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
                
                # Vérifier d'abord si on peut s'élever directement
                if self.elevation_manager.can_elevate():
                    self.logger.info("✨ Conditions d'élévation remplies !")
                    self.state = "ELEVATING"
                    return

                # Vérifier les ressources manquantes
                needed_resources = self.elevation_manager.get_needed_resources()
                if needed_resources:
                    self.logger.info(f"🔍 Ressources manquantes pour niveau {self.player.level} : {needed_resources}")
                    self.state = "GATHERING_RESOURCES"
                    self.target_resource = self._prioritize_resources(needed_resources)[0]
                    return

                # Si on a toutes les ressources, vérifier le nombre de joueurs
                required_players = self.elevation_manager.ELEVATION_REQUIREMENTS.get(self.player.level, {}).get("players", 1)
                player_count_on_tile = self.vision_manager.vision_data[0].count('player') if self.vision_manager.vision_data else 0
                # L'IA se compte elle-même
                total_players = player_count_on_tile + 1
                
                if total_players < required_players:
                    self.logger.info(f"👥 Pas assez de joueurs pour le rituel du niveau {self.player.level} ({total_players}/{required_players}). Appel à l'aide.")
                    # Envoyer un broadcast pour demander de l'aide
                    self.communicator.send_team_message("RITUAL_CALL", f"{next_level}:{self.player.id}:{self.player.x},{self.player.y}")
                    self.state = "AWAITING_PARTICIPANTS"
                    self.ritual_participants_needed = required_players
                    return

                self.state = "NORMAL_OPERATIONS"
                return
            
            elif self.player.level == 8:
                self.logger.info("🏆 Niveau maximum atteint ! Je me concentre sur la reproduction et l'aide à l'équipe.")
                self.state = "NORMAL_OPERATIONS"
                return
            
            self.logger.debug("Aucune action spécifique, exploration par défaut.")
            self.state = "NORMAL_OPERATIONS"
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'état: {str(e)}")
            self.state = "NORMAL_OPERATIONS"

    def _explore_locally_for_food(self):
        """Fait un pas en avant pour chercher de la nourriture à proximité."""
        self.logger.info("🗺️ Pas de nourriture en vue. Un pas en avant pour rafraîchir la vision.")
        if self.protocol.forward():
            self.logger.info("✅ Pas en avant effectué, vision rafraîchie")
        else:
            self.logger.warning("❌ Impossible de faire un pas en avant")