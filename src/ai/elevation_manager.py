from typing import Dict, List, Tuple, Optional
from protocol import ZappyProtocol
from vision import Vision
from movement import Movement

class ElevationManager:
    """Gère la logique d'élévation et les rituels."""

    def __init__(self, protocol: ZappyProtocol, vision: Vision, movement: Movement):
        """Initialise le gestionnaire d'élévation.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            vision (Vision): Système de vision
            movement (Movement): Gestionnaire de mouvement
        """
        self.protocol = protocol
        self.vision = vision
        self.movement = movement
        self.current_level = 1
        self.ritual_in_progress = False
        self.ritual_participants: List[Tuple[int, int]] = []
        
        # Conditions d'élévation par niveau selon les spécifications
        self.elevation_requirements = {
            1: {"player": 1, "linemate": 1, "deraumere": 0, "sibur": 0, "mendiane": 0, "phiras": 0, "thystame": 0},
            2: {"player": 2, "linemate": 1, "deraumere": 1, "sibur": 1, "mendiane": 0, "phiras": 0, "thystame": 0},
            3: {"player": 2, "linemate": 2, "deraumere": 0, "sibur": 1, "mendiane": 0, "phiras": 2, "thystame": 0},
            4: {"player": 4, "linemate": 1, "deraumere": 1, "sibur": 2, "mendiane": 0, "phiras": 1, "thystame": 0},
            5: {"player": 4, "linemate": 1, "deraumere": 2, "sibur": 1, "mendiane": 3, "phiras": 0, "thystame": 0},
            6: {"player": 6, "linemate": 1, "deraumere": 2, "sibur": 3, "mendiane": 1, "phiras": 0, "thystame": 0},
            7: {"player": 6, "linemate": 2, "deraumere": 2, "sibur": 2, "mendiane": 2, "phiras": 2, "thystame": 1}
        }

    def check_elevation_conditions(self) -> bool:
        """Vérifie si les conditions d'élévation sont remplies.
        
        Returns:
            bool: True si les conditions sont remplies
        """
        if self.current_level >= 8:  # Niveau maximum
            return False

        requirements = self.elevation_requirements[self.current_level]
        vision = self.vision.look()
        if not vision:
            return False

        # Vérifie le nombre de joueurs du même niveau
        player_count = sum(1 for case in vision if "player" in case)
        if player_count < requirements["player"]:
            return False

        # Vérifie les ressources sur la case
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

        # Vérifie les conditions avant de démarrer
        if not self.check_elevation_conditions():
            return False

        # Démarre le rituel
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

        # Vérifie si les conditions sont toujours remplies
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

        # Vérifie les conditions une dernière fois avant la fin
        if not self.check_elevation_conditions():
            self.ritual_in_progress = False
            return False

        # Vérifie si l'élévation a réussi
        response = self.protocol.incantation()
        if response:
            self.current_level += 1
            self.ritual_in_progress = False
            return True

        return False

    def get_current_level(self) -> int:
        """Récupère le niveau actuel.
        
        Returns:
            int: Niveau actuel du joueur
        """
        return self.current_level

    def get_requirements(self) -> Dict[str, int]:
        """Récupère les conditions d'élévation pour le niveau actuel.
        
        Returns:
            Dict[str, int]: Conditions d'élévation
        """
        return self.elevation_requirements[self.current_level].copy()

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