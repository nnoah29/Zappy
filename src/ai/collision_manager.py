from typing import List, Tuple, Optional
import logging
from protocol import ZappyProtocol
from vision import Vision

class CollisionManager:
    """Gère la détection et la résolution des collisions."""
    
    def __init__(self, protocol: ZappyProtocol, vision: Vision):
        """Initialise le gestionnaire de collisions.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            vision (Vision): Système de vision
        """
        self.protocol = protocol
        self.vision = vision
        self.logger = logging.getLogger(__name__)
        self.last_positions: List[Tuple[int, int]] = []
        self.stuck_count = 0
        self.max_stuck_count = 3
        self.position_history_size = 5

    def check_collision(self) -> bool:
        """Vérifie si le joueur est bloqué (collision).
        
        Returns:
            bool: True si le joueur est bloqué
        """
        current_pos = self.vision.get_case_position(0)  # Position actuelle (case 0)
        
        # Ajoute la position actuelle à l'historique
        self.last_positions.append(current_pos)
        
        # Garde seulement les N dernières positions
        if len(self.last_positions) > self.position_history_size:
            self.last_positions.pop(0)
            
        # Vérifie si on est bloqué au même endroit
        if len(self.last_positions) >= 3:
            if all(pos == current_pos for pos in self.last_positions[-3:]):
                # Ne pas incrémenter si on est déjà bloqué
                if not self.is_severely_stuck() and self.stuck_count == 0:
                    self.stuck_count += 1
                return True
                
        return False

    def handle_collision(self) -> None:
        """Gère une collision en essayant de se débloquer."""
        if self.stuck_count > self.max_stuck_count:
            # Si on est bloqué depuis trop longtemps, on essaie une autre direction
            self.logger.warning("Bloqué depuis trop longtemps, changement de direction")
            self.protocol.right()
            self.protocol.right()  # Tourne de 180 degrés
            self.reset()
        else:
            # Essaie de se déplacer sur le côté
            self.protocol.right()
            self.protocol.forward()

    def reset(self) -> None:
        """Réinitialise l'état du gestionnaire de collisions."""
        self.stuck_count = 0
        self.last_positions.clear()

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