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

    def add(self, item, quantity=1):
        if item in self.items:
            self.items[item] += quantity

    def remove(self, item, quantity=1):
        if item in self.items and self.items[item] >= quantity:
            self.items[item] -= quantity
            return True
        return False
