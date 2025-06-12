from src.ai.inventory import Inventory
from src.ai.logger import logger

class Player:
    def __init__(self, player_id, team, x, y):
        self.id = player_id
        self.team = team
        self.x = x
        self.y = y
        self.level = 1
        self.orientation = "N"  # N, E, S, W
        self.inventory = Inventory()
        logger.info(f"player {self.id} created on team {self.team} at ({self.x}, {self.y})")


    def move_forward(self, map_width, map_height):
        if self.orientation == "N":
            self.y = (self.y - 1) % map_height
        elif self.orientation == "S":
            self.y = (self.y + 1) % map_height
        elif self.orientation == "E":
            self.x = (self.x + 1) % map_width
        elif self.orientation == "W":
            self.x = (self.x - 1) % map_width
        logger.info(f"player {self.id} moved from ({self.x}, {self.y}) to ({self.x}, {self.y}) facing {self.orientation}")
