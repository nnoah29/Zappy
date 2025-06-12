import logging

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
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"map tile created: {self.resources} {self.players}")

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile(x, y) for x in range(width)] for y in range(height)]

    def get_tile(self, x, y):
        return self.grid[y % self.height][x % self.width]
