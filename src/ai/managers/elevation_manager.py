from typing import Dict, List
from managers.inventory_manager import InventoryManager
from core.protocol import ZappyProtocol
import logging
import time
from managers.vision_manager import VisionManager

class ElevationManager:
    """Gère la logique d'élévation et les rituels."""

    def __init__(self, protocol: ZappyProtocol, vision_manager: VisionManager, inventory_manager: InventoryManager, logger: logging.Logger):
        """Initialise le gestionnaire d'élévation.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            vision_manager (VisionManager): Gestionnaire de vision
            logger (logging.Logger): Logger
        """
        self.protocol = protocol
        self.vision_manager = vision_manager
        self.inventory_manager = inventory_manager
        self.logger = logger
        self.last_elevation_time = 0
        self.elevation_cooldown = 300
        self.ELEVATION_REQUIREMENTS = {
            1: {'players': 1, 'linemate': 1, 'deraumere': 0, 'sibur': 0, 'mendiane': 0, 'phiras': 0, 'thystame': 0},
            2: {'players': 2, 'linemate': 1, 'deraumere': 1, 'sibur': 1, 'mendiane': 0, 'phiras': 0, 'thystame': 0},
            3: {'players': 2, 'linemate': 2, 'deraumere': 0, 'sibur': 1, 'mendiane': 0, 'phiras': 2, 'thystame': 0},
            4: {'players': 4, 'linemate': 1, 'deraumere': 1, 'sibur': 2, 'mendiane': 0, 'phiras': 1, 'thystame': 0},
            5: {'players': 4, 'linemate': 1, 'deraumere': 2, 'sibur': 1, 'mendiane': 3, 'phiras': 0, 'thystame': 0},
            6: {'players': 6, 'linemate': 1, 'deraumere': 2, 'sibur': 3, 'mendiane': 0, 'phiras': 1, 'thystame': 0},
            7: {'players': 6, 'linemate': 2, 'deraumere': 2, 'sibur': 2, 'mendiane': 2, 'phiras': 2, 'thystame': 1}
        }
        self.ritual_in_progress = False
        

    def can_elevate(self) -> bool:
        """
        Vérifie si les conditions sont réunies POUR COMMENCER le processus d'élévation.
        Cela signifie : avoir les ressources dans l'inventaire et le bon nombre de joueurs sur la case.
        """
        try:
            current_level = self.vision_manager.player.level
            if current_level >= 8:
                return False
                
            requirements = self.ELEVATION_REQUIREMENTS.get(current_level)
            if not requirements:
                self.logger.error(f"Aucun prérequis défini pour le niveau {current_level}")
                return False
                
            for resource, count in requirements.items():
                if resource == 'players':
                    continue
                if self.inventory_manager.inventory.get(resource, 0) < count:
                    self.logger.debug(f"Pas assez de {resource} dans l'inventaire pour l'élévation (j'ai {self.inventory_manager.inventory.get(resource, 0)}, besoin de {count})")
                    return False
            
            current_tile = self.vision_manager.get_case_content(0, 0)
            if not current_tile:
                return False
                
            required_players = requirements.get('players', 1)
            player_count = current_tile.count('player')
            # L'IA se compte elle-même
            total_players = player_count + 1
            
            if total_players < required_players:
                self.logger.debug(f"Pas assez de joueurs sur la case ({total_players}/{required_players})")
                return False
            
                
            self.logger.info(f"✅ Toutes les conditions sont remplies pour INITIET le rituel du niveau {current_level}.")
            return True
                
        except Exception as e:
            self.logger.error(f"Erreur dans can_elevate: {str(e)}", exc_info=True)
            return False

    def start_elevation(self) -> bool:
        """Démarre une élévation en suivant le plan stratégique.
        
        Returns:
            bool: True si l'élévation a réussi
        """
        try:
            current_level = self.vision_manager.player.level
            next_level = current_level + 1
            
            self.logger.info(f"🚀 Démarrage de l'élévation au niveau {next_level}")
            
            if not self.can_elevate():
                self.logger.debug("❌ Conditions d'élévation non remplies")
                return False
            
            requirements = self.ELEVATION_REQUIREMENTS[next_level]
            self.logger.info(f"📦 Préparation du rituel : pose des pierres sur la case")
            
            for resource, count in requirements.items():
                if resource == 'players':
                    continue
                for _ in range(count):
                    if not self.protocol.set(resource):
                        self.logger.error(f"❌ Erreur lors du dépôt de {resource}")
                        return False
                    self.logger.debug(f"✅ {resource} déposé sur la case")
                    time.sleep(0.1)
            
            self.vision_manager.force_update_vision()
            current_tile = self.vision_manager.get_case_content(0, 0)
            self.logger.info(f"🔍 Vérification finale : case contient {current_tile}")
            
            self.logger.info("🌟 Lancement de l'incantation...")
            response = self.protocol.incantation()
            
            if response == "ko":
                self.logger.error("❌ Échec de l'incantation")
                return False
                
            self.logger.info(f"✅ Incantation lancée: {response}")
            
            if response == "Elevation underway":
                self.logger.info("⏳ Rituel en cours... (300 secondes)")
                time.sleep(300 / 1000)
                
                final_response = self.protocol.look()
                if final_response and "player" in final_response:
                    self.vision_manager.player.level = next_level
                    self.vision_manager.set_level(next_level)
                    self.last_elevation_time = time.time()
                    self.logger.info(f"🎉 Élévation réussie au niveau {next_level}!")
                    return True
                else:
                    self.logger.error("❌ Échec de l'élévation après l'incantation")
                    return False
            else:
                self.logger.error(f"❌ Réponse inattendue lors de l'incantation: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'élévation: {str(e)}")
            return False

    def _get_required_players(self, level: int) -> int:
        """Récupère le nombre de joueurs requis pour l'élévation.
        
        Args:
            level (int): Niveau actuel
            
        Returns:
            int: Nombre de joueurs requis
        """
        requirements = {
            1: 1,
            2: 2,
            3: 2,
            4: 4,
            5: 4,
            6: 6,
            7: 6
        }
        return requirements.get(level, 0)

    def get_needed_resources(self) -> List[str]:
        """Récupère la liste des ressources nécessaires pour l'élévation."""
        try:
            current_level = self.vision_manager.player.level
            
            if current_level not in self.ELEVATION_REQUIREMENTS:
                return []
                
            needed = []
            requirements = self.ELEVATION_REQUIREMENTS[current_level]
            for resource, count in requirements.items():
                if resource != 'players' and self.inventory_manager.inventory.get(resource, 0) < count:
                    needed.append(resource)
            return needed
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des ressources nécessaires: {str(e)}")
            return []

    def check_elevation_conditions(self) -> bool:
        """Vérifie si les conditions d'élévation sont remplies.
        
        Returns:
            bool: True si les conditions sont remplies
        """
        if self.vision_manager.player.level >= 7:
            return False

        requirements = self.ELEVATION_REQUIREMENTS[self.vision_manager.player.level]
        vision = self.vision_manager.look()
        if not vision:
            return False

        player_count = sum(1 for case in vision if "player" in case)
        if player_count < self._get_required_players(self.vision_manager.player.level):
            return False

        current_case = vision[0]
        for resource, count in requirements.items():
            if resource == "player":
                continue
            if current_case.count(resource) < count:
                return False

        return True

    def start_ritual(self) -> bool:
        """Démarre le rituel d'élévation.
        
        Returns:
            bool: True si le rituel a démarré avec succès
        """
        if self.ritual_in_progress:
            return False

        if not self.check_elevation_conditions():
            return False

        if not self.protocol.incantation():
            return False

        self.ritual_in_progress = True
        return True

    def check_ritual_status(self) -> bool:
        """Vérifie le statut du rituel en cours.
        
        Returns:
            bool: True si le rituel est toujours en cours
        """
        if not self.ritual_in_progress:
            return False

        if not self.check_elevation_conditions():
            self.ritual_in_progress = False
            return False

        return True

    def complete_ritual(self) -> bool:
        """Termine le rituel d'élévation.
        
        Returns:
            bool: True si le rituel a été complété avec succès
        """
        if not self.ritual_in_progress:
            return False

        if not self.check_elevation_conditions():
            self.ritual_in_progress = False
            return False

        response = self.protocol.incantation()
        if response:
            self.vision_manager.player.level += 1
            self.ritual_in_progress = False
            return True

        return False

    def get_current_level(self) -> int:
        """Récupère le niveau actuel.
        
        Returns:
            int: Niveau actuel du joueur
        """
        return self.vision_manager.player.level

    def get_requirements(self) -> Dict[str, int]:
        """Récupère les conditions d'élévation pour le niveau actuel.
        
        Returns:
            Dict[str, int]: Conditions d'élévation
        """
        return self.ELEVATION_REQUIREMENTS[self.vision_manager.player.level].copy()

    def reset(self) -> None:
        """Réinitialise l'état du gestionnaire."""
        self.ritual_in_progress = False
        self.ritual_participants.clear()

    def is_ritual_in_progress(self) -> bool:
        """Vérifie si un rituel est en cours.
        
        Returns:
            bool: True si un rituel est en cours
        """
        return self.ritual_in_progress 