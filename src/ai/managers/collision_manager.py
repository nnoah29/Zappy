from typing import Tuple, Optional
import logging
from core.protocol import ZappyProtocol
from managers.vision_manager import VisionManager
from managers.movement import Movement

class CollisionManager:
    """Gère la détection et la résolution des collisions."""
    
    def __init__(self, protocol: ZappyProtocol, vision_manager: VisionManager, movement: Movement):
        """Initialise le gestionnaire de collisions.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            vision_manager (VisionManager): Gestionnaire de vision
            movement (Movement): Gestionnaire de mouvement
        """
        self.protocol = protocol
        self.vision_manager = vision_manager
        self.movement = movement
        self.logger = logging.getLogger(__name__)
        self.collision_count = 0
        self.last_collision_pos: Optional[Tuple[int, int]] = None
        self.escape_attempts = 0
        self.max_escape_attempts = 3
        self.stuck_count = 0
        self.max_stuck_count = 3
        self.position_history_size = 5

    def check_collision(self) -> bool:
        """Vérifie s'il y a une collision.
        
        Returns:
            bool: True si une collision est détectée
        """
        # Vérifie les joueurs dans le champ de vision
        players = self.vision_manager.get_players_in_range(1)  # Vérifie seulement les joueurs à distance 1
        if not players:
            return False

        # Vérifie si un joueur est directement devant
        for player_pos in players:
            if self.vision_manager.is_case_in_front(self.vision_manager.get_case_index(player_pos[0], player_pos[1])):
                self.collision_count += 1
                self.last_collision_pos = player_pos
                return True

        return False

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