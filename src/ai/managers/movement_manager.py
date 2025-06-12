from typing import Tuple, Optional
import logging
import time
from core.protocol import ZappyProtocol
from managers.vision_manager import VisionManager
from managers.collision_manager import CollisionManager
from managers.movement import Movement

class MovementManager:
    """Gère les déplacements et les collisions du joueur."""

    def __init__(self, protocol: ZappyProtocol, vision_manager: VisionManager):
        """Initialise le gestionnaire de mouvement.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            vision_manager (VisionManager): Gestionnaire de vision
        """
        self.protocol = protocol
        self.vision_manager = vision_manager
        self.movement = Movement(protocol, vision_manager)
        self.collision_manager = CollisionManager(protocol, vision_manager, self.movement)
        self.logger = logging.getLogger(__name__)
        self.last_move_time = 0
        self.move_cooldown = 7  # Temps entre chaque mouvement
        self.current_direction = 0  # 0: Nord, 1: Est, 2: Sud, 3: Ouest
        self.target_position: Optional[Tuple[int, int]] = None
        self.stuck_count = 0
        self.max_stuck_count = 3
        self.last_position: Optional[Tuple[int, int]] = None
        self.position_history = []
        self.position_history_size = 5

    def set_target(self, target: Tuple[int, int]) -> None:
        """Définit la position cible.
        
        Args:
            target (Tuple[int, int]): Position cible (x, y)
        """
        self.target_position = target
        self.logger.debug(f"Cible définie: {target}")

    def move_to_target(self, target_position: Optional[Tuple[int, int]] = None) -> bool:
        """Déplace le joueur vers la cible.
        
        Args:
            target_position (Optional[Tuple[int, int]]): Position cible optionnelle.
                Si non fournie, utilise self.target_position.
                
        Returns:
            bool: True si le mouvement a réussi
        """
        if target_position is not None:
            self.set_target(target_position)
            
        if not self.target_position:
            return False

        # Vérifie le cooldown
        current_time = time.time()
        if current_time - self.last_move_time < self.move_cooldown:
            return False

        # Vérifie si on est bloqué
        current_pos = self.vision_manager.get_current_position()
        if self._is_stuck(current_pos):
            self._handle_stuck_situation()
            return True

        # Calcule la direction vers la cible
        target_direction = self._calculate_direction_to_target()
        if target_direction is None:
            return False

        # Tourne vers la cible si nécessaire
        if not self._face_target(target_direction):
            return False

        # Avance vers la cible
        if not self.protocol.forward():
            return False

        self.last_move_time = current_time
        self.last_position = current_pos
        self._update_position_history(current_pos)
        return True

    def _calculate_direction_to_target(self) -> Optional[int]:
        """Calcule la direction vers la cible.
        
        Returns:
            Optional[int]: Direction (0-3) ou None si la cible est atteinte
        """
        if not self.target_position:
            return None

        current_pos = self.vision_manager.get_current_position()
        dx = self.target_position[0] - current_pos[0]
        dy = self.target_position[1] - current_pos[1]

        # Si on est sur la cible
        if dx == 0 and dy == 0:
            return None

        # Priorité au déplacement vertical
        if dy != 0:
            return 0 if dy < 0 else 2
        # Puis horizontal
        return 1 if dx > 0 else 3

    def _face_target(self, target_direction: int) -> bool:
        """Tourne le joueur vers la cible.
        
        Args:
            target_direction (int): Direction cible (0-3)
            
        Returns:
            bool: True si le joueur est face à la cible
        """
        while self.current_direction != target_direction:
            if not self.protocol.right():
                return False
            self.current_direction = (self.current_direction + 1) % 4
        return True

    def _is_stuck(self, current_pos: Tuple[int, int]) -> bool:
        """Vérifie si le joueur est bloqué.
        
        Args:
            current_pos (Tuple[int, int]): Position actuelle
            
        Returns:
            bool: True si le joueur est bloqué
        """
        if not self.last_position:
            return False

        if current_pos == self.last_position:
            self.stuck_count += 1
        else:
            self.stuck_count = 0

        return self.stuck_count >= self.max_stuck_count

    def _handle_stuck_situation(self) -> None:
        """Gère une situation de blocage."""
        # Essaie de se débloquer en tournant à droite et avançant
        if not self.protocol.right():
            return
        if not self.protocol.forward():
            return
        self.current_direction = (self.current_direction + 1) % 4
        self.stuck_count = 0

    def _update_position_history(self, position: Tuple[int, int]) -> None:
        """Met à jour l'historique des positions.
        
        Args:
            position (Tuple[int, int]): Nouvelle position
        """
        self.position_history.append(position)
        if len(self.position_history) > self.position_history_size:
            self.position_history.pop(0)

    def explore(self) -> None:
        """Explore la carte en évitant les collisions."""
        if not self.target_position:
            return

        # Vérifie les collisions
        if self.collision_manager.check_collision():
            self.collision_manager.handle_collision()
            return

        # Avance dans une direction aléatoire
        self.protocol.forward()

    def handle_collision(self) -> None:
        """Gère les collisions avec d'autres joueurs."""
        if self.collision_manager.check_collision():
            self.collision_manager.handle_collision()
            time.sleep(0.1)  # Attendre un peu après une collision

    def reset(self) -> None:
        """Réinitialise l'état du gestionnaire."""
        self.last_move_time = 0
        self.current_direction = 0
        self.target_position = None
        self.stuck_count = 0
        self.last_position = None
        self.position_history = []
        self.collision_manager.reset() 