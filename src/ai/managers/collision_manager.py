from typing import Tuple, Optional, Any
import logging
from core.protocol import ZappyProtocol
from managers.vision_manager import VisionManager
import time
import random

class CollisionManager:
    """Gère les collisions et les interactions entre joueurs."""
    
    def __init__(self, protocol: ZappyProtocol, vision_manager: VisionManager, movement_manager: Any, logger: logging.Logger):
        """Initialise le gestionnaire de collision.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            vision_manager (VisionManager): Gestionnaire de vision
            movement_manager (Any): Gestionnaire de déplacement
            logger (Logger): Logger pour les messages
        """
        self.protocol = protocol
        self.vision_manager = vision_manager
        self.movement_manager = movement_manager
        self.logger = logger
        self.collision_count = 0
        self.last_collision_pos: Optional[Tuple[int, int]] = None
        self.escape_attempts = 0
        self.max_escape_attempts = 3
        self.stuck_count = 0
        self.max_stuck_count = 3
        self.position_history_size = 5
        self.last_collision_time = 0
        self.collision_cooldown = 7  # Temps entre chaque vérification de collision

    def check_collision(self) -> bool:
        """Vérifie s'il y a une collision avec un autre joueur.
        
        Returns:
            bool: True si une collision est détectée
        """
        try:
            # Vérifie le cooldown
            if time.time() - self.last_collision_time < self.collision_cooldown:
                return False
                
            # Récupère les joueurs dans la vision
            players = self.vision_manager.get_players_in_vision()
            if not players:
                return False
                
            # Vérifie si un joueur est sur la même case
            for player_pos in players:
                if player_pos == (0, 0):  # Même case que le joueur
                    self.last_collision_time = time.time()
                    return True
                    
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification des collisions: {str(e)}")
            return False

    def avoid_collision(self) -> bool:
        """Évite une collision en se déplaçant.
        
        Returns:
            bool: True si l'évitement a réussi
        """
        try:
            # Vérifie le cooldown
            if not self.can_check_collision():
                return False
                
            # Récupère les joueurs dans la vision
            players = self.vision_manager.get_players_in_vision()
            if not players:
                return False
                
            # Trouve une direction libre
            directions = [0, 1, 2, 3]  # Nord, Est, Sud, Ouest
            random.shuffle(directions)  # Mélange les directions pour plus de variété
            
            for direction in directions:
                # Tourne dans la direction
                current_direction = self.vision_manager.player.get_direction()
                diff = (direction - current_direction) % 4
                
                if diff == 1 or diff == 2:
                    if not self.movement_manager.turn_right():
                        continue
                elif diff == 3:
                    if not self.movement_manager.turn_left():
                        continue
                        
                # Vérifie si la case devant est libre
                case = self.vision_manager.get_case_content(1, 0)
                if "player" not in case:
                    if self.movement_manager.move_forward():
                        self.logger.debug(f"Collision évitée en se déplaçant vers {direction}")
                        return True
                        
            # Si aucune direction n'est libre, essaie de reculer
            self.logger.debug("Aucune direction libre, tentative de recul")
            if not self.movement_manager.turn_right():
                return False
            if not self.movement_manager.turn_right():
                return False
            return self.movement_manager.move_forward()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évitement de collision: {str(e)}")
            return False

    def can_check_collision(self) -> bool:
        """Vérifie si on peut vérifier les collisions.
        
        Returns:
            bool: True si on peut vérifier les collisions
        """
        return time.time() - self.last_collision_time >= self.collision_cooldown

    def handle_collision(self) -> bool:
        """Gère une collision détectée.
        
        Returns:
            bool: True si la collision a été résolue
        """
        if not self.check_collision():
            self.escape_attempts = 0  # Réinitialise les tentatives si pas de collision
            return True

        # Si trop de tentatives d'évasion, on essaie une autre stratégie
        if self.escape_attempts >= self.max_escape_attempts:
            success = self._handle_severe_collision()
            if success:
                self.escape_attempts = 0  # Réinitialise les tentatives si succès
            return success

        # Stratégie d'évasion basique
        self.escape_attempts += 1
        success = self._basic_escape_strategy()
        if success:
            self.escape_attempts = 0  # Réinitialise les tentatives si succès
        return success

    def _basic_escape_strategy(self) -> bool:
        """Stratégie basique d'évasion de collision.
        
        Returns:
            bool: True si l'évasion a réussi
        """
        # Tourne à droite et avance
        if not self.protocol.right():
            return False
        if not self.protocol.forward():
            return False

        # Vérifie si la collision persiste
        if not self.check_collision():
            return True

        # Si toujours bloqué, essaie de tourner à gauche
        if not self.protocol.left():
            return False
        if not self.protocol.left():
            return False
        if not self.protocol.forward():
            return False

        return not self.check_collision()

    def _handle_severe_collision(self) -> bool:
        """Gère une collision sévère (après plusieurs tentatives d'évasion).
        
        Returns:
            bool: True si la collision a été résolue
        """
        # Essaie de se déplacer dans une direction aléatoire
        for _ in range(4):  # Essaie les 4 directions
            if not self.protocol.right():
                return False
            if not self.protocol.forward():
                return False
            if not self.check_collision():
                return True

        return False

    def reset(self) -> None:
        """Réinitialise l'état du gestionnaire de collisions."""
        self.collision_count = 0
        self.last_collision_pos = None
        self.escape_attempts = 0
        self.stuck_count = 0
        self.position_history_size = 5

    def get_stuck_count(self) -> int:
        """Récupère le nombre de fois que le joueur est resté bloqué.
        
        Returns:
            int: Nombre de blocages
        """
        return self.stuck_count

    def is_severely_stuck(self) -> bool:
        """Vérifie si le joueur est sévèrement bloqué.
        
        Returns:
            bool: True si le joueur est sévèrement bloqué
        """
        return self.stuck_count > self.max_stuck_count 