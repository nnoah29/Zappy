import logging

class Inventory:
    def __init__(self):
        self.items = {
            "food": 0,
            "linemate": 0,
            "deraumere": 0,
            "sibur": 0,
            "mendiane": 0,
            "phiras": 0,
            "thystame": 0,
        }
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"inventory created: {self.items}")

    def add(self, item, quantity=1):
        if item in self.items:
            self.items[item] += quantity
        self.logger.info(f"inventory updated: {self.items} adding {item}")

    def get(self, item):
        return self.items.get(item, 0)

    def remove(self, item, quantity=1):
        if item in self.items and self.items[item] >= quantity:
            self.items[item] -= quantity
            return True
        self.logger.info(f"inventory updated: {self.items} removing {item}")
        return False
