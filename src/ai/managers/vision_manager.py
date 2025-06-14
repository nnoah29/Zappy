from typing import Dict, List, Tuple, Optional
import logging
from core.protocol import ZappyProtocol
from core.vision import Vision
import time
from models.player import Player
from models.map import Map

class VisionManager:
    """Gère la vision du joueur selon les règles du jeu."""

    def __init__(self, protocol: ZappyProtocol, player: Player, map: Map, logger: logging.Logger):
        """Initialise le gestionnaire de vision.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            player (Player): Joueur contrôlé
            map (Map): Carte du jeu
            logger (Logger): Logger pour les messages
        """
        self.protocol = protocol
        self.player = player
        self.map = map
        self.logger = logger
        self.vision = []
        self.vision_data = []  # Données de vision actuelles
        self.level = 1  # Niveau initial
        self.last_vision_update = 0
        self.vision_cooldown = 7  # Temps entre chaque mise à jour de la vision

    def update_vision(self) -> bool:
        """Met à jour la vision du joueur.
        
        Returns:
            bool: True si la mise à jour a réussi
        """
        try:
            response = self.protocol.look()
            self.vision = self._parse_vision(response)
            self.vision_data = self.vision  # Mise à jour des données de vision
            self.last_vision_update = time.time()
            self.logger.debug(f"Vision mise à jour: {self.vision}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la vision: {str(e)}")
            return False

    def _parse_vision(self, response: str) -> List[List[str]]:
        """Parse la réponse de la commande Look.
        
        Format: [player, object-on-tile1, ..., object-on-tileP,...]
        Les objets sur une même case sont séparés par un espace.
        Les cases sont séparées par une virgule.
        
        Args:
            response (str): Réponse du serveur
            
        Returns:
            List[List[str]]: Liste des cases vues
        """
        try:
            # Enlève les crochets et sépare les cases
            response = response.strip('[]')
            cases = response.split(',')
            
            # Parse chaque case
            vision = []
            for case in cases:
                items = case.strip().split()
                vision.append(items)
                
            return vision
        except Exception as e:
            self.logger.error(f"Erreur lors du parsing de la vision: {str(e)}")
            raise

    def get_case_content(self, x: int, y: int) -> List[str]:
        """Récupère le contenu d'une case dans la vision.
        
        Args:
            x (int): Position X relative
            y (int): Position Y relative
            
        Returns:
            List[str]: Contenu de la case
        """
        try:
            # Calcule l'index dans la vision
            index = self._get_vision_index(x, y)
            if 0 <= index < len(self.vision):
                return self.vision[index]
            return []
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du contenu de la case: {str(e)}")
            return []

    def _get_vision_index(self, x: int, y: int) -> int:
        """Calcule l'index dans la vision pour une position relative.
        
        Pour le niveau 1, la vision est de 1 case dans chaque direction.
        Format: [0, 1, 2, 3, 4, 5, 6, 7, 8]
        Où 0 est la case du joueur, et les autres sont autour dans le sens horaire:
        7 0 1
        6   2
        5 4 3
        
        Args:
            x (int): Position X relative
            y (int): Position Y relative
            
        Returns:
            int: Index dans la vision
        """
        if x == 0 and y == 0:
            return 0  # Case du joueur
            
        # Calcule l'index selon la position relative
        if x == 1 and y == 0:
            return 1  # Droite
        elif x == 1 and y == 1:
            return 2  # Diagonale bas-droite
        elif x == 0 and y == 1:
            return 3  # Bas
        elif x == -1 and y == 1:
            return 4  # Diagonale bas-gauche
        elif x == -1 and y == 0:
            return 5  # Gauche
        elif x == -1 and y == -1:
            return 6  # Diagonale haut-gauche
        elif x == 0 and y == -1:
            return 7  # Haut
        elif x == 1 and y == -1:
            return 8  # Diagonale haut-droite
            
        return -1  # Position invalide

    def find_nearest_object(self, object_type: str) -> Optional[Tuple[int, int]]:
        """Trouve l'objet le plus proche d'un type donné.
        
        Args:
            object_type (str): Type d'objet à chercher (food, linemate, deraumere, etc.)
            
        Returns:
            Optional[Tuple[int, int]]: Position relative de l'objet le plus proche
        """
        try:
            nearest = None
            min_distance = float('inf')
            
            # Parcourt toutes les cases visibles
            for y in range(-self.level, self.level + 1):
                for x in range(-self.level, self.level + 1):
                    case = self.get_case_content(x, y)
                    if object_type in case:
                        distance = abs(x) + abs(y)
                        if distance < min_distance:
                            min_distance = distance
                            nearest = (x, y)
                            
            return nearest
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche d'objet: {str(e)}")
            return None

    def get_players_in_vision(self) -> List[Tuple[int, int]]:
        """Récupère la liste des joueurs visibles.
        
        Returns:
            List[Tuple[int, int]]: Liste des positions relatives des joueurs
        """
        players = []
        for y in range(-self.level, self.level + 1):
            for x in range(-self.level, self.level + 1):
                case = self.get_case_content(x, y)
                if "player" in case:
                    players.append((x, y))
        return players

    def get_vision_range(self) -> int:
        """Retourne la portée de vision selon le niveau.
        
        Returns:
            int: Portée de vision
        """
        return self.level

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
                
        pos = self.find_nearest_object(resource_type)
        return pos if pos != (-1, -1) else None

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
        pos = self.get_case_position(index)
        
        # Vérifie la position en fonction de la direction
        if self.current_direction == 0:  # Nord
            return pos[1] < 0
        elif self.current_direction == 1:  # Est
            return pos[0] > 0
        elif self.current_direction == 2:  # Sud
            return pos[1] > 0
        else:  # Ouest
            return pos[0] < 0

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
            bool: True si la vision peut être mise à jour
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

    def set_level(self, level: int) -> None:
        """Met à jour le niveau du joueur.
        
        Args:
            level (int): Nouveau niveau
        """
        self.level = level
        self.vision.set_level(level)
        self.vision_range = self.vision.get_vision_range()

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

    def get_players_in_range(self, range: int) -> List[Tuple[int, int]]:
        """Récupère la liste des joueurs dans un certain rayon.
        
        Args:
            range (int): Rayon de recherche
            
        Returns:
            List[Tuple[int, int]]: Liste des positions des joueurs
        """
        players = []
        for i, case in enumerate(self.vision):
            if "player" in case:
                pos = self.get_case_position(i)
                if abs(pos[0]) + abs(pos[1]) <= range:
                    players.append(pos)
        return players

    def set_level(self, level: int) -> None:
        """Définit le niveau du joueur.
        
        Args:
            level (int): Niveau du joueur
        """
        self.vision.set_level(level) 