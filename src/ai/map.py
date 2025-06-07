class Tile:
    def __init__(self):
        self.resources = {
            "food": 0,
            "linemate": 0,
            "deraumere": 0,
            "sibur": 0,
            "mendiane": 0,
            "phiras": 0,
            "thystame": 0,
        }
        self.players = []  # Liste des IDs de joueurs

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile() for _ in range(width)] for _ in range(height)]

    def get_tile(self, x, y):
        # gestion du monde sphérique (tore)
        return self.grid[y % self.height][x % self.width]
