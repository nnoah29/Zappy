from typing import Tuple, List, Optional
from protocol import ZappyProtocol
from vision import Vision

class Movement:
    """Gère les déplacements du joueur."""

    def __init__(self, protocol: ZappyProtocol, vision: Vision):
        """Initialise le gestionnaire de mouvement.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            vision (Vision): Système de vision
        """
        self.protocol = protocol
        self.vision = vision
        self.current_direction = 0  # 0: Nord, 1: Est, 2: Sud, 3: Ouest
        self.last_positions: List[Tuple[int, int]] = []
        self.stuck_count = 0

    def move_to_position(self, target_pos: Tuple[int, int]) -> bool:
        """Déplace le joueur vers une position cible.
        
        Args:
            target_pos (Tuple[int, int]): Position cible (x, y)
            
        Returns:
            bool: True si le mouvement a réussi
        """
        # Vérifie si la position est accessible
        if not self._is_position_accessible(target_pos):
            return False

        # Calcule le chemin vers la cible
        path = self._calculate_path(target_pos)
        if not path:
            return False

        # Exécute le chemin
        return self._execute_path(path)

    def _is_position_accessible(self, pos: Tuple[int, int]) -> bool:
        """Vérifie si une position est accessible.
        
        Args:
            pos (Tuple[int, int]): Position à vérifier
            
        Returns:
            bool: True si la position est accessible
        """
        # Vérifie si la position est dans le champ de vision
        vision = self.vision.look()
        for i, case in enumerate(vision):
            case_pos = self.vision.get_case_position(i)
            if case_pos == pos:
                # Vérifie s'il n'y a pas d'obstacle
                return "player" not in case
        return False

    def _calculate_path(self, target_pos: Tuple[int, int]) -> List[str]:
        """Calcule le chemin vers la cible.
        
        Args:
            target_pos (Tuple[int, int]): Position cible
            
        Returns:
            List[str]: Liste des commandes à exécuter
        """
        commands = []
        current_pos = (0, 0)  # Position relative du joueur

        # Calcule les différences de position
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]

        # Ajuste la direction pour le déplacement en X
        if dx != 0:
            target_direction = 1 if dx > 0 else 3  # Est ou Ouest
            commands.extend(self._rotate_to_direction(target_direction))
            for _ in range(abs(dx)):
                commands.append("forward")

        # Ajuste la direction pour le déplacement en Y
        if dy != 0:
            target_direction = 0 if dy > 0 else 2  # Nord ou Sud
            commands.extend(self._rotate_to_direction(target_direction))
            for _ in range(abs(dy)):
                commands.append("forward")

        return commands

    def _rotate_to_direction(self, target_direction: int) -> List[str]:
        """Calcule les rotations nécessaires pour atteindre une direction.
        
        Args:
            target_direction (int): Direction cible (0: Nord, 1: Est, 2: Sud, 3: Ouest)
            
        Returns:
            List[str]: Liste des commandes de rotation
        """
        commands = []
        diff = (target_direction - self.current_direction) % 4

        if diff == 1:
            commands.append("right")
        elif diff == 2:
            commands.extend(["right", "right"])
        elif diff == 3:
            commands.append("left")

        self.current_direction = target_direction
        return commands

    def _execute_path(self, path: List[str]) -> bool:
        """Exécute une séquence de commandes de mouvement.
        
        Args:
            path (List[str]): Liste des commandes à exécuter
            
        Returns:
            bool: True si le chemin a été exécuté avec succès
        """
        for command in path:
            if command == "forward":
                if not self.protocol.forward():
                    return False
            elif command == "right":
                if not self.protocol.right():
                    return False
            elif command == "left":
                if not self.protocol.left():
                    return False

            # Vérifie si le joueur est bloqué
            if self._is_stuck():
                return False

        return True

    def _is_stuck(self) -> bool:
        """Vérifie si le joueur est bloqué.
        
        Returns:
            bool: True si le joueur est bloqué
        """
        current_pos = (0, 0)  # Position relative du joueur
        self.last_positions.append(current_pos)

        # Garde seulement les 5 dernières positions
        if len(self.last_positions) > 5:
            self.last_positions.pop(0)

        # Vérifie si le joueur est bloqué (même position 3 fois de suite)
        if len(self.last_positions) >= 3:
            last_three = self.last_positions[-3:]
            if all(pos == current_pos for pos in last_three):
                self.stuck_count += 1
                return True

        return False

    def reset_stuck_counter(self) -> None:
        """Réinitialise le compteur de blocage."""
        self.stuck_count = 0
        self.last_positions.clear() 