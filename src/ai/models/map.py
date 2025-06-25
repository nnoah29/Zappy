import logging
import time

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.resources = {
            "food": 0,
            "linemate": 0,
            "deraumere": 0,
            "sibur": 0,
            "mendiane": 0,
            "phiras": 0,
            "thystame": 0,
        }
        self.players = []
        self.last_updated = None  # Timestamp de la dernière mise à jour
        self.is_explored = False  # Indique si la tuile a été explorée
        self.logger = logging.getLogger(__name__)
        # self.logger.info(f"map tile created: {self.resources} {self.players}")

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile(x, y) for x in range(width)] for y in range(height)]
        self.logger = logging.getLogger(__name__)

    def get_tile(self, x, y):
        """Récupère une tuile aux coordonnées données."""
        return self.grid[y % self.height][x % self.width]

    def is_explored(self, x: int, y: int) -> bool:
        """Vérifie si une tuile a déjà été explorée.
        
        Args:
            x (int): Coordonnée X
            y (int): Coordonnée Y
            
        Returns:
            bool: True si la tuile a été explorée, False sinon
        """
        try:
            tile = self.get_tile(x, y)
            return tile.is_explored
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification d'exploration de ({x}, {y}): {e}")
            return False

    def get_tile_content(self, x: int, y: int) -> dict:
        """Retourne le contenu d'une tuile.
        
        Args:
            x (int): Coordonnée X
            y (int): Coordonnée Y
            
        Returns:
            dict: Contenu de la tuile (ressources et joueurs)
        """
        try:
            tile = self.get_tile(x, y)
            return {
                'resources': tile.resources.copy(),
                'players': tile.players.copy(),
                'is_explored': tile.is_explored
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du contenu de ({x}, {y}): {e}")
            return {'resources': {}, 'players': [], 'is_explored': False}

    def update_tile(self, x: int, y: int, content: list):
        """Met à jour le contenu d'une tuile.
        
        Args:
            x (int): Coordonnée X
            y (int): Coordonnée Y
            content (list): Contenu de la tuile (liste d'objets)
        """
        try:
            tile = self.get_tile(x, y)
            
            # Réinitialiser les ressources
            for resource in tile.resources:
                tile.resources[resource] = 0
            
            # Compter les ressources dans le contenu
            for item in content:
                if item in tile.resources:
                    tile.resources[item] += 1
            
            # Marquer la tuile comme explorée
            tile.is_explored = True
            tile.last_updated = time.time()
            
            self.logger.debug(f"Tuile ({x},{y}) mise à jour : {tile.resources}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la tuile ({x}, {y}): {e}")

    def mark_as_explored(self, x: int, y: int):
        """Marque une tuile comme explorée.
        
        Args:
            x (int): Coordonnée X
            y (int): Coordonnée Y
        """
        try:
            tile = self.get_tile(x, y)
            tile.is_explored = True
            tile.last_updated = time.time()
        except Exception as e:
            self.logger.error(f"Erreur lors du marquage d'exploration de ({x}, {y}): {e}")

    def get_unexplored_tiles(self) -> list:
        """Récupère la liste des tuiles non explorées.
        
        Returns:
            list: Liste des coordonnées (x, y) des tuiles non explorées
        """
        unexplored = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_explored(x, y):
                    unexplored.append((x, y))
        return unexplored

    def get_tiles_with_resource(self, resource: str) -> list:
        """Récupère la liste des tuiles contenant une ressource spécifique.
        
        Args:
            resource (str): Nom de la ressource
            
        Returns:
            list: Liste des coordonnées (x, y) des tuiles contenant la ressource
        """
        tiles_with_resource = []
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile(x, y)
                if tile.resources.get(resource, 0) > 0:
                    tiles_with_resource.append((x, y))
        return tiles_with_resource
