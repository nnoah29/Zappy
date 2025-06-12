from typing import Tuple, Optional
import logging
import time
import random
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
        self.target: Optional[Tuple[int, int]] = None
        self.stuck_counter = 0
        self.max_stuck = 3
        self.exploration_radius = 5

    def set_target(self, target: Tuple[int, int]) -> None:
        """Définit la cible de mouvement.
        
        Args:
            target (Tuple[int, int]): Position cible (x, y)
        """
        self.target = target
        self.logger.debug(f"Cible définie: {target}")

    def get_random_exploration_target(self) -> Tuple[int, int]:
        """Génère une cible aléatoire pour l'exploration.
        
        Returns:
            Tuple[int, int]: Position cible (x, y)
        """
        x = random.randint(-self.exploration_radius, self.exploration_radius)
        y = random.randint(-self.exploration_radius, self.exploration_radius)
        return (x, y)

    def move_to_target(self, target_position: Optional[Tuple[int, int]] = None) -> bool:
        """Déplace le joueur vers sa cible.
        
        Args:
            target_position (Optional[Tuple[int, int]]): Position cible optionnelle.
                Si non fournie, utilise self.target.
                
        Returns:
            bool: True si le joueur a atteint sa cible
        """
        if target_position is not None:
            self.set_target(target_position)
            
        if not self.target:
            return True

        # Vérifie si le joueur est bloqué
        if self.last_position == self.target:
            self.stuck_counter += 1
            if self.stuck_counter >= self.max_stuck:
                self.logger.debug("Joueur bloqué, nouvelle cible aléatoire")
                self.target = self.get_random_exploration_target()
                self.stuck_counter = 0
        else:
            self.stuck_counter = 0

        # Calcule la direction vers la cible
        dx = self.target[0]
        dy = self.target[1]

        # Tourne vers la cible
        if dx > 0 and self.current_direction != 1:
            self.turn_right()
            return False
        elif dx < 0 and self.current_direction != 3:
            self.turn_left()
            return False
        elif dy > 0 and self.current_direction != 2:
            self.turn_right()
            return False
        elif dy < 0 and self.current_direction != 0:
            self.turn_left()
            return False

        # Avance si la case devant est libre
        if self.can_move_forward():
            self.forward()
            self.last_position = self.target
            return True

        # Si bloqué, change de direction
        self.turn_right()
        return False

    def can_move_forward(self) -> bool:
        """Vérifie si le joueur peut avancer.
        
        Returns:
            bool: True si le joueur peut avancer
        """
        # Vérifie la case devant
        front_case = self.vision_manager.get_case_content(0, 1)
        return not any(item in front_case for item in ['player', 'wall'])

    def forward(self) -> None:
        """Fait avancer le joueur."""
        try:
            response = self.protocol.forward()
            if response == "ok":
                # Met à jour la position en fonction de la direction
                if self.current_direction == 0:  # Nord
                    self.last_position = (self.last_position[0], self.last_position[1] - 1)
                elif self.current_direction == 1:  # Est
                    self.last_position = (self.last_position[0] + 1, self.last_position[1])
                elif self.current_direction == 2:  # Sud
                    self.last_position = (self.last_position[0], self.last_position[1] + 1)
                else:  # Ouest
                    self.last_position = (self.last_position[0] - 1, self.last_position[1])
        except Exception as e:
            self.logger.error(f"Erreur lors de l'avancée: {str(e)}")

    def turn_right(self) -> None:
        """Fait tourner le joueur vers la droite."""
        try:
            response = self.protocol.right()
            if response == "ok":
                self.current_direction = (self.current_direction + 1) % 4
        except Exception as e:
            self.logger.error(f"Erreur lors de la rotation droite: {str(e)}")

    def turn_left(self) -> None:
        """Fait tourner le joueur vers la gauche."""
        try:
            response = self.protocol.left()
            if response == "ok":
                self.current_direction = (self.current_direction - 1) % 4
        except Exception as e:
            self.logger.error(f"Erreur lors de la rotation gauche: {str(e)}")

    def update(self) -> None:
        """Met à jour l'état du mouvement."""
        if not self.target:
            self.target = self.get_random_exploration_target()
        self.move_to_target()

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