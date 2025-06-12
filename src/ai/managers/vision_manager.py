from typing import Dict, List, Tuple, Optional
import logging
from core.protocol import ZappyProtocol
from core.vision import Vision
import time

class VisionManager:
    """Gère la vision et la détection d'objets du joueur."""

    def __init__(self, protocol: ZappyProtocol):
        """Initialise le gestionnaire de vision.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication avec le serveur
        """
        self.protocol = protocol
        self.vision = Vision(protocol)
        self.logger = logging.getLogger(__name__)
        self.last_vision_update = 0
        self.vision_cooldown = 7  # Temps entre chaque mise à jour de la vision
        self.vision_data = None  # Données de vision actuelles
        self.level = 1  # Niveau actuel du joueur
        self.vision_range = self.vision.get_vision_range()

    def get_vision_range(self) -> int:
        """Retourne la portée de vision selon le niveau.
        
        Returns:
            int: Portée de vision
        """
        return self.vision.get_vision_range()

    def get_current_position(self) -> Tuple[int, int]:
        """Retourne la position actuelle du joueur.
        
        Returns:
            Tuple[int, int]: Position (x, y)
        """
        return self.vision.get_current_position()

    def find_nearest_resource(self, resource_type: str) -> Optional[Tuple[int, int]]:
        """Trouve la ressource la plus proche d'un type donné.
        
        Args:
            resource_type (str): Type de ressource à chercher
            
        Returns:
            Optional[Tuple[int, int]]: Position de la ressource la plus proche
        """
        if not self.vision_data:
            if not self.update_vision():
                return None
                
        pos = self.vision.find_nearest_object(resource_type)
        return pos if pos != (-1, -1) else None

    def get_case_content(self, x: int, y: int) -> Dict[str, int]:
        """Récupère le contenu d'une case.
        
        Args:
            x (int): Position X
            y (int): Position Y
            
        Returns:
            Dict[str, int]: Contenu de la case
        """
        return self.vision.get_case_content(x, y)

    def get_players_in_vision(self) -> List[Tuple[int, int]]:
        """Récupère la liste des joueurs dans le champ de vision.
        
        Returns:
            List[Tuple[int, int]]: Liste des positions des joueurs
        """
        return self.vision.get_players_in_vision()

    def is_case_in_front(self, x: int, y: int) -> bool:
        """Vérifie si une case est devant le joueur.
        
        Args:
            x (int): Position X
            y (int): Position Y
            
        Returns:
            bool: True si la case est devant
        """
        return self.vision.is_case_in_front(x, y)

    def set_level(self, level: int) -> None:
        """Met à jour le niveau du joueur.
        
        Args:
            level (int): Nouveau niveau
        """
        self.level = level
        self.vision.set_level(level)
        self.vision_range = self.vision.get_vision_range()

    def update_vision(self) -> bool:
        """Met à jour la vision du joueur.
        
        Returns:
            bool: True si la vision a été mise à jour, False sinon
        """
        try:
            look_response = self.protocol.look()
            self.vision_data = self.protocol.parse_look_response(look_response)
            self.last_vision_update = time.time()
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la vision: {e}")
            return False

    def get_resources_in_range(self, max_distance: int = 2) -> Dict[str, List[Tuple[int, int]]]:
        """Récupère toutes les ressources dans un rayon donné.
        
        Args:
            max_distance (int): Distance maximale de recherche
            
        Returns:
            Dict[str, List[Tuple[int, int]]]: Dictionnaire des ressources et leurs positions
        """
        if not self.vision_data:
            if not self.update_vision():
                return {}
                
        env = self.vision.analyze_environment()
        resources = {}
        
        for resource_type in ["food", "linemate", "deraumere", "sibur", "mendiane", "phiras", "thystame"]:
            resources[resource_type] = [
                pos for pos in env[resource_type]
                if abs(pos[0]) + abs(pos[1]) <= max_distance
            ]
            
        return resources

    def is_position_safe(self, position: Tuple[int, int]) -> bool:
        """Vérifie si une position est sûre (pas de joueurs hostiles).
        
        Args:
            position (Tuple[int, int]): Position à vérifier
            
        Returns:
            bool: True si la position est sûre, False sinon
        """
        if not self.vision_data:
            if not self.update_vision():
                return False
                
        index = self.vision.get_case_index(position[0], position[1])
        return self.vision.is_case_safe(index)

    def get_best_path_to_resource(self, resource_type: str) -> List[Tuple[int, int]]:
        """Trouve le meilleur chemin vers une ressource.
        
        Args:
            resource_type (str): Type de ressource à atteindre
            
        Returns:
            List[Tuple[int, int]]: Liste des positions à suivre
        """
        if not self.vision_data:
            if not self.update_vision():
                return []
                
        target = self.find_nearest_resource(resource_type)
        if not target:
            return []
            
        # Implémentation simple du chemin
        path = []
        current_x, current_y = 0, 0
        target_x, target_y = target
        
        # Déplacement horizontal
        while current_x != target_x:
            if current_x < target_x:
                current_x += 1
            else:
                current_x -= 1
            path.append((current_x, current_y))
            
        # Déplacement vertical
        while current_y != target_y:
            if current_y < target_y:
                current_y += 1
            else:
                current_y -= 1
            path.append((current_x, current_y))
            
        return path

    def get_players_in_range(self, max_distance: int = 2) -> List[Tuple[int, int]]:
        """Trouve tous les joueurs dans un rayon donné.
        
        Args:
            max_distance (int): Distance maximale de recherche
            
        Returns:
            List[Tuple[int, int]]: Liste des positions des joueurs
        """
        if not self.vision_data:
            if not self.update_vision():
                return []
                
        return self.vision.get_players_in_range(max_distance)

    def can_update_vision(self) -> bool:
        """Vérifie si la vision peut être mise à jour.
        
        Returns:
            bool: True si la vision peut être mise à jour, False sinon
        """
        return time.time() - self.last_vision_update >= self.vision_cooldown

    def get_case_position(self, index: int) -> Tuple[int, int]:
        """
        Récupère la position d'une case à partir de son index.
        
        Args:
            index (int): Index de la case
            
        Returns:
            Tuple[int, int]: Position (x, y) de la case
        """
        return self.vision.get_case_position(index)

    def get_case_index(self, x: int, y: int) -> int:
        """
        Récupère l'index d'une case à partir de sa position.
        
        Args:
            x (int): Position X
            y (int): Position Y
            
        Returns:
            int: Index de la case
        """
        return self.vision.get_case_index(x, y)

    def get_expected_vision_size(self) -> int:
        """
        Calcule la taille attendue du champ de vision.
        
        Returns:
            int: Nombre de cases visibles
        """
        return self.vision.get_expected_vision_size()

    def is_case_in_front(self, index: int) -> bool:
        """
        Vérifie si une case est devant le joueur.
        
        Args:
            index (int): Index de la case
            
        Returns:
            bool: True si la case est devant, False sinon
        """
        return self.vision.is_case_in_front(index)

    def get_case_content(self, x: int, y: int) -> Dict[str, int]:
        """
        Récupère le contenu d'une case à une position donnée.
        
        Args:
            x (int): Position X
            y (int): Position Y
            
        Returns:
            Dict[str, int]: Contenu de la case
        """
        index = self.get_case_index(x, y)
        if index == -1:
            return {}
        content = self.vision.get_case_content(index)
        return {item: content.count(item) for item in content if item != "player"} 