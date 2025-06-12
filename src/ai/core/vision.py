from typing import List, Dict, Tuple, Optional
from .protocol import ZappyProtocol

class Vision:
    """Gère la vision et l'analyse de l'environnement du joueur."""

    def __init__(self, protocol: ZappyProtocol):
        """Initialise la vision avec le protocole de communication."""
        self.protocol = protocol
        self.level = 1
        self.vision_data = None

    def look(self) -> List[Dict[str, int]]:
        """Envoie la commande look et analyse la réponse."""
        vision_data = self.protocol.look()
        self.vision_data = self.parse_vision(vision_data)
        return self.vision_data

    def parse_vision(self, vision_data: str) -> List[Dict[str, int]]:
        """Parse les données de vision reçues du serveur."""
        if vision_data == "[]":
            return []
           
        # Enlève les crochets et divise par les virgules
        cases = vision_data.strip("[]").split(",")
        result = []
       
        for case in cases:
            case = case.strip()
            if not case:  # Case vide
                result.append({})
                continue
               
            # Compte les objets dans la case
            objects = {}
            for item in case.split():
                if item in objects:
                    objects[item] += 1
                else:
                    objects[item] = 1
            result.append(objects)
           
        return result

    def get_current_position(self) -> Tuple[int, int]:
        """Retourne la position actuelle du joueur.
        
        Returns:
            Tuple[int, int]: Position actuelle (x, y)
        """
        # D'après les spécifications, la position actuelle est toujours (0, 0)
        # car le monde est relatif au joueur et la première case (index 0) est toujours la position du joueur
        return (0, 0)

    def get_case_position(self, index: int) -> Tuple[int, int]:
        """
        Calcule la position relative d'une case par rapport au joueur.
        La numérotation suit le schéma suivant:
        - Case 0: position du joueur
        - Cases 1-3: ligne devant le joueur (y=1)
        - Cases 4-8: ligne suivante (y=2)
        - Et ainsi de suite...
        
        Args:
            index (int): Index de la case dans le champ de vision
            
        Returns:
            Tuple[int, int]: Position (x, y) relative au joueur
        """
        if index < 0:
            return (-1, -1)
        
        if index == 0:
            return (0, 0)  # Position du joueur
        
        # Calcul de la ligne (y) et de la position dans la ligne
        y = 1
        remaining_index = index
        line_size = 3  # Taille de la première ligne
        
        while remaining_index > line_size:
            remaining_index -= line_size
            y += 1
            line_size = 2 * y + 1
            
        # Calcul de la position x dans la ligne
        x = remaining_index - (line_size // 2 + 1)
        
        return (x, y)

    def find_nearest_object(self, object_type: str) -> Tuple[int, int]:
        """
        Trouve la position de l'objet le plus proche d'un type spécifique.
        
        Args:
            object_type (str): Type d'objet à chercher
            
        Returns:
            Tuple[int, int]: Position de l'objet le plus proche, ou (-1, -1) si non trouvé
        """
        if object_type not in ["food", "linemate", "deraumere", "sibur", "mendiane", "phiras", "thystame"]:
            return (-1, -1)
            
        environment = self.analyze_environment()
        if not environment[object_type]:
            return (-1, -1)
            
        # Trouve l'objet le plus proche en utilisant la distance de Manhattan
        nearest_pos = min(environment[object_type], 
                         key=lambda pos: abs(pos[0]) + abs(pos[1]))
        return nearest_pos

    def get_players_in_vision(self) -> List[Tuple[int, int]]:
        """Retourne la liste des positions des joueurs dans le champ de vision."""
        if not self.vision_data:
            self.look()
        players = []
        for i, case in enumerate(self.vision_data):
            if "player" in case:
                pos = self.get_case_position(i)
                if pos != (-1, -1):
                    # Ajoute autant de positions qu'il y a de joueurs dans la case
                    for _ in range(case["player"]):
                        players.append(pos)
        return players

    def set_level(self, level: int) -> None:
        """Met à jour le niveau du joueur."""
        if level < 1:
            raise ValueError("Le niveau doit être >= 1")
        self.level = level

    def get_expected_vision_size(self) -> int:
        """
        Retourne le nombre de cases attendues pour le niveau actuel.
        
        """
        return (self.level + 1) ** 2

    def is_case_in_front(self, index: int) -> bool:
        """Vérifie si une case est directement devant le joueur."""
        pos = self.get_case_position(index)
        return pos[0] == 0 and pos[1] > 0

    def get_case_content(self, index: int) -> List[str]:
        """
        Récupère le contenu d'une case spécifique.
        
        Args:
            index (int): Index de la case
            
        Returns:
            List[str]: Liste des objets présents sur la case
        """
        if not self.vision_data:
            self.look()
        if index < 0 or index >= len(self.vision_data):
            return []
        return [item for item, count in self.vision_data[index].items() for _ in range(count)]

    def count_objects_in_case(self, index: int, object_type: str) -> int:
        """
        Compte le nombre d'objets d'un type spécifique sur une case.
        
        Args:
            index (int): Index de la case
            object_type (str): Type d'objet à compter
            
        Returns:
            int: Nombre d'objets du type spécifié
        """
        if not self.vision_data:
            self.look()
        if index < 0 or index >= len(self.vision_data):
            return 0
        return self.vision_data[index].get(object_type, 0)

    def get_case_resources(self, index: int) -> Dict[str, int]:
        """
        Récupère tous les objets présents sur une case avec leur quantité.
        
        Args:
            index (int): Index de la case
            
        Returns:
            Dict[str, int]: Dictionnaire des objets et leur quantité
        """
        if not self.vision_data:
            self.look()
        if index < 0 or index >= len(self.vision_data):
            return {}
        return {k: v for k, v in self.vision_data[index].items() if k != "player"}

    def analyze_environment(self) -> Dict[str, List[Tuple[int, int]]]:
        """
        Analyse l'environnement complet et retourne la position de tous les objets visibles.
        
        Returns:
            Dict[str, List[Tuple[int, int]]]: Dictionnaire des objets et leurs positions
        """
        if not self.vision_data:
            self.look()
            
        environment = {
            "food": [],
            "linemate": [],
            "deraumere": [],
            "sibur": [],
            "mendiane": [],
            "phiras": [],
            "thystame": []
        }
        
        for i, case in enumerate(self.vision_data):
            pos = self.get_case_position(i)
            if pos != (-1, -1):
                for item, count in case.items():
                    if item != "player":
                        for _ in range(count):
                            environment[item].append(pos)
                            
        return environment

    def get_players_in_range(self, max_distance: int = 1) -> List[Tuple[int, int]]:
        """
        Trouve tous les joueurs dans un rayon donné.
        
        Args:
            max_distance (int): Distance maximale de recherche
            
        Returns:
            List[Tuple[int, int]]: Liste des positions des joueurs
        """
        if not self.vision_data:
            self.look()
            
        players = []
        for i, case in enumerate(self.vision_data):
            if "player" in case:
                pos = self.get_case_position(i)
                if pos != (-1, -1) and abs(pos[0]) + abs(pos[1]) <= max_distance:
                    for _ in range(case["player"]):
                        players.append(pos)
        return players

    def is_case_safe(self, index: int) -> bool:
        """
        Vérifie si une case est sûre (pas de joueurs hostiles).
        
        Args:
            index (int): Index de la case
            
        Returns:
            bool: True si la case est sûre
        """
        if not self.vision_data:
            self.look()
            
        if index < 0 or index >= len(self.vision_data):
            return False
            
        return "player" not in self.vision_data[index]

    def get_best_food_path(self) -> List[Tuple[int, int]]:
        """
        Trouve le meilleur chemin vers la nourriture la plus proche.
        
        Returns:
            List[Tuple[int, int]]: Liste des positions à suivre
        """
        if not self.vision_data:
            self.look()
            
        food_pos = self.find_nearest_object("food")
        if food_pos == (-1, -1):
            return []
            
        # Implémentation simple du chemin
        path = []
        current_x, current_y = 0, 0
        target_x, target_y = food_pos
        
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

    def get_vision_range(self) -> int:
        """
        Retourne la portée de vision actuelle.
        
        Returns:
            int: Portée de vision
        """
        return self.level

    def get_case_index(self, x: int, y: int) -> int:
        """
        Calcule l'index d'une case à partir de sa position.
        
        Args:
            x (int): Position X
            y (int): Position Y
            
        Returns:
            int: Index de la case, ou -1 si hors champ de vision
        """
        if y < 0 or abs(x) > y:
            return -1
            
        # Calcul de l'index
        index = 0
        for i in range(y):
            index += 2 * i + 1
            
        index += x + y
        return index