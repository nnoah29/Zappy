from typing import Tuple, Optional
import logging
import time
import random
from managers.vision_manager import VisionManager
from managers.collision_manager import CollisionManager
from core.protocol import ZappyProtocol
from models.player import Player
from models.map import Map

class MovementManager:
    """Gère les déplacements et les collisions du joueur."""

    def __init__(self, protocol: ZappyProtocol, player: Player, map: Map, vision_manager: VisionManager, logger: logging.Logger):
        """Initialise le gestionnaire de mouvement.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            player (Player): Joueur à déplacer
            map (Map): Carte du jeu
            vision_manager (VisionManager): Gestionnaire de vision
            logger (Logger): Logger pour les messages
        """
        self.protocol = protocol
        self.player = player
        self.map = map
        self.vision_manager = vision_manager
        self.collision_manager = CollisionManager(protocol, vision_manager, self, logger)
        self.logger = logger
        self.last_move_time = 0
        self.move_cooldown = 0.1
        self.current_direction = 0
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

    def move_to(self, target: Tuple[int, int]) -> bool:
        """Déplace le joueur vers une position cible de manière itérative.
        
        Args:
            target (Tuple[int, int]): Position cible relative
            
        Returns:
            bool: True si le déplacement a réussi
        """
        try:
            current_x, current_y = self.player.get_position()
            target_x = (current_x + target[0]) % self.map.width
            target_y = (current_y + target[1]) % self.map.height
            
            self.logger.debug(f"🎯 Déplacement itératif vers ({target_x}, {target_y}) depuis ({current_x}, {current_y})")
            
            return self.move_to_absolute(target_x, target_y)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du déplacement vers la cible: {str(e)}")
            return False

    def move_to_absolute(self, target_x: int, target_y: int) -> bool:
        """Déplace le joueur vers des coordonnées absolues de manière itérative.
        
        Args:
            target_x (int): Coordonnée X absolue de la cible
            target_y (int): Coordonnée Y absolue de la cible
            
        Returns:
            bool: True si le déplacement a réussi
        """
        try:
            max_attempts = 10
            attempts = 0
            
            while attempts < max_attempts:
                current_x, current_y = self.player.get_position()
                
                if (current_x, current_y) == (target_x, target_y):
                    self.logger.info(f"✅ Arrivé à la destination ({target_x}, {target_y})")
                    return True
                
                if self._is_stuck():
                    self.logger.warning("Joueur bloqué pendant le déplacement.")
                    self._handle_stuck()
                    return False
                
                if not self.can_move():
                    self.logger.debug("Cooldown de déplacement actif, attente...")
                    time.sleep(0.1)
                    attempts += 1
                    continue
                
                if self.collision_manager.check_collision():
                    self.logger.debug("Collision détectée, tentative d'éjection")
                    if self.collision_manager.eject_other_players():
                        self.logger.debug("Éjection réussie, tentative de déplacement")
                        time.sleep(0.1)
                    else:
                        self.logger.debug("Éjection échouée, tentative d'évitement")
                        if not self.collision_manager.avoid_collision():
                            self.logger.debug("Impossible d'éviter la collision")
                            return False
                
                rel_x, rel_y = self._calculate_shortest_path(current_x, current_y, target_x, target_y)
                
                self.logger.debug(f"Position actuelle: ({current_x}, {current_y}), Cible: ({target_x}, {target_y}), Relatif: ({rel_x}, {rel_y})")
                
                if rel_x == 0 and rel_y == 0:
                    self.logger.info(f"✅ Arrivé à la destination ({target_x}, {target_y})")
                    return True
                
                current_direction = self.player.get_direction()
                target_direction = -1
                
                if rel_y < 0:
                    target_direction = 0
                elif rel_y > 0:
                    target_direction = 2
                elif rel_x < 0:
                    target_direction = 3
                elif rel_x > 0:
                    target_direction = 1
                
                if target_direction == -1:
                    self.logger.info(f"✅ Arrivé à la destination ({target_x}, {target_y})")
                    return True
                
                if current_direction != target_direction:
                    if not self.orient_towards(target_direction):
                        self.logger.debug("Échec de l'orientation")
                        return False
                
                if not self.move_forward():
                    self.logger.debug("Échec de l'avancement, un obstacle est probablement apparu.")
                    return False
                
                if self._check_for_better_opportunities(target_x, target_y):
                    self.logger.info("🎯 Meilleure opportunité détectée, changement de cap !")
                    return True
                
                time.sleep(0.1)
                attempts += 1
            
            self.logger.warning(f"Nombre maximum de tentatives atteint ({max_attempts})")
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur lors du déplacement itératif: {str(e)}")
            return False

    def _calculate_shortest_path(self, current_x: int, current_y: int, target_x: int, target_y: int) -> Tuple[int, int]:
        """Calcule le chemin le plus court sur un monde torique.
        
        Args:
            current_x (int): Position X actuelle
            current_y (int): Position Y actuelle
            target_x (int): Position X cible
            target_y (int): Position Y cible
            
        Returns:
            Tuple[int, int]: Vecteur relatif (dx, dy) vers la cible
        """
        dx = target_x - current_x
        dy = target_y - current_y
        
        if abs(dx) > self.map.width // 2:
            dx = dx - self.map.width if dx > 0 else dx + self.map.width
        
        if abs(dy) > self.map.height // 2:
            dy = dy - self.map.height if dy > 0 else dy + self.map.height
        
        return dx, dy

    def _get_direction_to_target(self, dx: int, dy: int) -> int:
        """Calcule la direction vers une cible.
        
        Args:
            dx (int): Différence en X
            dy (int): Différence en Y
            
        Returns:
            int: Direction (0: Nord, 1: Est, 2: Sud, 3: Ouest)
        """
        if abs(dx) > abs(dy):
            return 1 if dx > 0 else 3
        else:
            return 0 if dy < 0 else 2

    def _is_stuck(self) -> bool:
        """Vérifie si le joueur est bloqué.
        
        Returns:
            bool: True si le joueur est bloqué
        """
        current_pos = self.player.get_position()
        
        self.position_history.append(current_pos)
        if len(self.position_history) > self.position_history_size:
            self.position_history.pop(0)
            
        if len(self.position_history) == self.position_history_size:
            if all(pos == current_pos for pos in self.position_history):
                return True
                
        return False

    def _handle_stuck(self) -> None:
        """Gère le blocage du joueur."""
        self.stuck_count += 1
        if self.stuck_count >= self.max_stuck_count:
            self.logger.debug("Joueur sévèrement bloqué, réinitialisation")
            self.reset()
        else:
            self.logger.warning(f"Joueur bloqué (tentative {self.stuck_count}/{self.max_stuck_count}). Tentative de déblocage.")
            
            actions = [
                lambda: self.turn_right(),
                lambda: self.turn_left(),
                lambda: self.turn_right() and self.turn_right(),
                lambda: self.turn_left() and self.turn_left(),
                lambda: self.turn_right() and self.move_forward(),
                lambda: self.turn_left() and self.move_forward()
            ]
            
            random.shuffle(actions)
            
            for action in actions:
                try:
                    if action():
                        self.logger.info("Déblocage réussi")
                        self.position_history = []
                        self.stuck_count = 0
                        return
                except Exception as e:
                    self.logger.debug(f"Action de déblocage échouée: {e}")
                    continue
            
            self.position_history = []
            self.logger.error("Impossible de se débloquer après plusieurs tentatives")

    def can_move(self) -> bool:
        """Vérifie si le joueur peut se déplacer.
        
        Returns:
            bool: True si le joueur peut se déplacer
        """
        return time.time() - self.last_move_time >= self.move_cooldown

    def move_forward(self) -> bool:
        """Fait avancer le joueur d'une case.
        
        Returns:
            bool: True si le déplacement a réussi
        """
        try:
            response = self.protocol.forward()
            if response:
                x, y = self.player.get_position()
                direction = self.player.get_direction()
                
                if direction == 0:
                    y = (y - 1) % self.map.height
                elif direction == 1:
                    x = (x + 1) % self.map.width
                elif direction == 2:
                    y = (y + 1) % self.map.height
                else:
                    x = (x - 1) % self.map.width
                    
                self.player.set_position(x, y)
                self.last_move_time = time.time()
                self.logger.debug(f"Déplacement vers {self.player.get_position()}")
                return True
            self.logger.debug(f"Échec de l'avancement")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors du déplacement: {str(e)}")
            return False

    def turn_left(self) -> bool:
        """Fait tourner le joueur vers la gauche.
        
        Returns:
            bool: True si la rotation a réussi
        """
        try:
            response = self.protocol.left()
            if response:
                direction = (self.player.get_direction() - 1) % 4
                self.player.set_direction(direction)
                self.last_move_time = time.time()
                self.logger.debug(f"Rotation vers la gauche: {direction}")
                return True
            self.logger.debug(f"Échec de la rotation gauche")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la rotation: {str(e)}")
            return False

    def turn_right(self) -> bool:
        """Fait tourner le joueur vers la droite.
        
        Returns:
            bool: True si la rotation a réussi
        """
        try:
            response = self.protocol.right()
            if response:
                direction = (self.player.get_direction() + 1) % 4
                self.player.set_direction(direction)
                self.last_move_time = time.time()
                self.logger.debug(f"Rotation vers la droite: {direction}")
                return True
            self.logger.debug(f"Échec de la rotation droite")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la rotation: {str(e)}")
            return False

    def reset(self) -> None:
        """Réinitialise l'état du gestionnaire."""
        self.last_move_time = 0
        self.current_direction = 0
        self.target_position = None
        self.stuck_count = 0
        self.last_position = None
        self.position_history = []
        self.collision_manager.reset()

    def orient_towards(self, target_direction: int) -> bool:
        """Oriente le joueur vers une direction spécifique de manière optimale.
        
        Args:
            target_direction (int): Direction cible (0: Nord, 1: Est, 2: Sud, 3: Ouest)
            
        Returns:
            bool: True si l'orientation a réussi
        """
        try:
            current_direction = self.player.get_direction()
            
            if current_direction == target_direction:
                return True
            
            diff = (target_direction - current_direction) % 4
            
            if diff == 1 or diff == 2:
                if not self.turn_right():
                    return False
            elif diff == 3:
                if not self.turn_left():
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'orientation: {str(e)}")
            return False

    def _check_for_better_opportunities(self, target_x: int, target_y: int) -> bool:
        """Vérifie s'il y a de meilleures opportunités (ressources plus proches) après un déplacement.
        
        Args:
            target_x (int): Coordonnée X de la cible actuelle
            target_y (int): Coordonnée Y de la cible actuelle
            
        Returns:
            bool: True si une meilleure opportunité a été détectée
        """
        try:
            if not self.vision_manager.force_update_vision():
                return False
            
            current_x, current_y = self.player.get_position()
            current_distance = abs(target_x - current_x) + abs(target_y - current_y)
            
            for y in range(-self.vision_manager.level, self.vision_manager.level + 1):
                for x in range(-self.vision_manager.level, self.vision_manager.level + 1):
                    case_content = self.vision_manager.get_case_content(x, y)
                    
                    if 'food' in case_content:
                        food_distance = abs(x) + abs(y)
                        
                        if food_distance < current_distance:
                            self.logger.info(f"🎯 Nourriture trouvée à ({x}, {y}) - distance {food_distance} vs {current_distance}")
                            return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification des opportunités: {str(e)}")
            return False
