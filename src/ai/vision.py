from typing import List, Dict, Tuple
from protocol import ZappyProtocol

class Vision:
    """Gère la vision et l'analyse de l'environnement du joueur."""

    def __init__(self, protocol: ZappyProtocol):
        """Initialise la vision avec le protocole de communication."""
        self.protocol = protocol
        self.level = 1

    def look(self) -> List[Dict[str, int]]:
        """Envoie la commande look et analyse la réponse."""
        vision_data = self.protocol.look()
        return self.parse_vision(vision_data)

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

    def get_case_position(self, index: int) -> Tuple[int, int]:
        """
        Calcule la position relative d'une case par rapport au joueur.
        """
        if index < 0 or index >= self.get_expected_vision_size():
            return (-1, -1)
        
        if index == 0:
            return (0, 0)  # Position du joueur
        
        # Trouve dans quelle ligne de vision se trouve l'index
        
        remaining_index = index
        y = 0
        
        while remaining_index > 0:
            y += 1
            line_size = 2 * y + 1
            if remaining_index <= line_size:
                # L'index est dans cette ligne
                pos_in_line = remaining_index - 1
                # La position x va de -y à +y
                x = pos_in_line - y
                return (x, y)
            remaining_index -= line_size
        
        return (-1, -1)

    def find_nearest_object(self, object_type: str) -> Tuple[int, int]:
        """Trouve l'objet le plus proche du type spécifié."""
        vision = self.look()
        min_distance = float('inf')
        nearest_pos = (-1, -1)
        
        for i, case in enumerate(vision):
            if object_type in case:
                pos = self.get_case_position(i)
                if pos != (-1, -1):
                    # Calcul de la distance Manhattan
                    distance = abs(pos[0]) + abs(pos[1])
                    if distance < min_distance:
                        min_distance = distance
                        nearest_pos = pos
        
        return nearest_pos

    def get_players_in_vision(self) -> List[Tuple[int, int]]:
        """Retourne la liste des positions des joueurs dans le champ de vision."""
        vision = self.look()
        players = []
        for i, case in enumerate(vision):
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

    def get_case_content(self, x: int, y: int) -> Dict[str, int]:
        """Retourne le contenu d'une case à une position relative donnée."""
        vision = self.look()
        for i, case in enumerate(vision):
            pos = self.get_case_position(i)
            if pos == (x, y):
                return case
        return {}