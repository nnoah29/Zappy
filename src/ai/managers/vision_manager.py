from typing import Dict, List, Tuple, Optional
import logging
from core.protocol import ZappyProtocol
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
        self.vision_data = []
        self.level = 1
        self.last_vision_update = 0
        self.vision_cooldown = 7
        self.vision_cache = {}
        self.cache_duration = 30

    def update_vision(self) -> bool:
        """Met à jour la vision du joueur.
        
        Returns:
            bool: True si la mise à jour a réussi
        """
        try:
            if time.time() - self.last_vision_update < self.vision_cooldown:
                return True
                
            response = self.protocol.look()
            self.vision = self._parse_vision(response)
            self.vision_data = self.vision
            self.last_vision_update = time.time()
            
            self._update_vision_cache()
            
            self.logger.debug(f"Vision mise à jour: {self.vision}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la vision: {str(e)}")
            return False

    def force_update_vision(self) -> bool:
        """Force la mise à jour de la vision en ignorant le cooldown.
        
        Returns:
            bool: True si la mise à jour a réussi
        """
        try:
            self.logger.debug("🔄 Mise à jour forcée de la vision (ignorant le cooldown)")
            response = self.protocol.look()
            self.vision = self._parse_vision(response)
            self.vision_data = self.vision
            self.last_vision_update = time.time()
            
            self._update_vision_cache()
            
            self.logger.debug(f"Vision forcée mise à jour: {self.vision}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour forcée de la vision: {str(e)}")
            return False

    def _update_vision_cache(self) -> None:
        """Met à jour le cache de vision."""
        try:
            current_time = time.time()
            player_pos = self.player.get_position()
            
            expired_keys = []
            for key, (timestamp, _) in self.vision_cache.items():
                if current_time - timestamp > self.cache_duration:
                    expired_keys.append(key)
                    
            for key in expired_keys:
                del self.vision_cache[key]
                
            for y in range(-self.level, self.level + 1):
                for x in range(-self.level, self.level + 1):
                    case_content = self.get_case_content(x, y)
                    if case_content:
                        cache_x = (player_pos[0] + x) % self.map.width
                        cache_y = (player_pos[1] + y) % self.map.height
                        cache_key = (cache_x, cache_y)
                        self.vision_cache[cache_key] = (current_time, case_content)
                        
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du cache: {str(e)}")

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
            response = response.strip('[]')
            cases = response.split(',')
            
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
            return 0
            
        if x == 1 and y == 0:
            return 1
        elif x == 1 and y == 1:
            return 2
        elif x == 0 and y == 1:
            return 3
        elif x == -1 and y == 1:
            return 4
        elif x == -1 and y == 0:
            return 5
        elif x == -1 and y == -1:
            return 6
        elif x == 0 and y == -1:
            return 7
        elif x == 1 and y == -1:
            return 8
            
        return -1

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
            
            for y in range(-self.level, self.level + 1):
                for x in range(-self.level, self.level + 1):
                    case = self.get_case_content(x, y)
                    if object_type in case:
                        distance = abs(x) + abs(y)
                        if distance < min_distance:
                            min_distance = distance
                            nearest = (x, y)
                            
            if not nearest:
                nearest = self._find_in_cache(object_type)
                            
            return nearest
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche d'objet: {str(e)}")
            return None

    def _find_in_cache(self, object_type: str) -> Optional[Tuple[int, int]]:
        """Trouve un objet dans le cache de vision.
        
        Args:
            object_type (str): Type d'objet à chercher
            
        Returns:
            Optional[Tuple[int, int]]: Position relative de l'objet
        """
        try:
            player_pos = self.player.get_position()
            nearest = None
            min_distance = float('inf')
            
            for (cache_x, cache_y), (timestamp, case_content) in self.vision_cache.items():
                if object_type in case_content:
                    rel_x = (cache_x - player_pos[0]) % self.map.width
                    rel_y = (cache_y - player_pos[1]) % self.map.height
                    
                    if rel_x > self.map.width // 2:
                        rel_x -= self.map.width
                    if rel_y > self.map.height // 2:
                        rel_y -= self.map.height
                        
                    distance = abs(rel_x) + abs(rel_y)
                    if distance < min_distance:
                        min_distance = distance
                        nearest = (rel_x, rel_y)
                        
            return nearest
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche dans le cache: {str(e)}")
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
        
        if self.current_direction == 0:
            return pos[1] < 0
        elif self.current_direction == 1:
            return pos[0] > 0
        elif self.current_direction == 2:
            return pos[1] > 0
        else:
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
        self.logger.info(f"Niveau de vision mis à jour: {self.level}")

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
                
        resources = {}
        
        for resource_type in ["food", "linemate", "deraumere", "sibur", "mendiane", "phiras", "thystame"]:
            resources[resource_type] = []
            for y in range(-self.level, self.level + 1):
                for x in range(-self.level, self.level + 1):
                    if abs(x) + abs(y) <= max_distance:
                        case_content = self.get_case_content(x, y)
                        if resource_type in case_content:
                            resources[resource_type].append((x, y))
            
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
                
        case_content = self.get_case_content(position[0], position[1])
        return "player" not in case_content

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
            
        path = []
        current_x, current_y = 0, 0
        target_x, target_y = target
        
        while current_x != target_x:
            if current_x < target_x:
                current_x += 1
            else:
                current_x -= 1
            path.append((current_x, current_y))
            
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
        for y in range(-self.level, self.level + 1):
            for x in range(-self.level, self.level + 1):
                if abs(x) + abs(y) <= range:
                    case_content = self.get_case_content(x, y)
                    if "player" in case_content:
                        players.append((x, y))
        return players 