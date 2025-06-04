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
        """Calcule la position relative d'une case par rapport au joueur (logique Zappy carré)."""
        size = 2 * self.level
        if index < 0 or index >= 4 * self.level * self.level:
            return (-1, -1)
            
        # Calcul de la position dans la grille
        row = index // size
        col = index % size
        
        # Conversion en coordonnées relatives au joueur
        # Le joueur est au centre de la grille
        x = col - (size // 2)
        y = row - (size // 2)
        
        return (x, y)

    def find_nearest_object(self, object_type: str) -> Tuple[int, int]:
        """Trouve l'objet le plus proche du type spécifié."""
        vision = self.look()
        for i, case in enumerate(vision):
            if object_type in case:
                return self.get_case_position(i)
        return (-1, -1)

    def get_players_in_vision(self) -> List[Tuple[int, int]]:
        """Retourne la liste des positions des joueurs dans le champ de vision."""
        vision = self.look()
        players = []
        for i, case in enumerate(vision):
            if "player" in case:
                pos = self.get_case_position(i)
                if pos != (-1, -1):
                    players.append(pos)
        return players

    def set_level(self, level: int) -> None:
        """Met à jour le niveau du joueur."""
        self.level = level

    def get_expected_vision_size(self) -> int:
        """Retourne le nombre de cases attendues pour le niveau actuel (logique Zappy)."""
        return 4 * self.level * self.level