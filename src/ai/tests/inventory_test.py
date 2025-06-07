from src.ai.inventory import Inventory
from src.ai.player import Player


def test_inventory_get():
    player = Player("mongol", "teams paiya", 5, 0)
    assert player.inventory.get("sibur") == 0
    assert player.inventory.get("food") == 0
    assert player.inventory.get("linemate") == 0
    assert player.inventory.get("mendiane") == 0
    assert player.inventory.get("phiras") == 0
    assert player.inventory.get("thystame") == 0



def test_inventory_add():
    player = Player("mongol", "teams paiya", 5, 0)
    player.inventory.add("sibur", 1)
    player.inventory.add("food", 1)
    player.inventory.add("linemate", 1)
    player.inventory.add("deraumere", 1)
    player.inventory.add("mendiane", 1)
    player.inventory.add("phiras", 1)
    player.inventory.add("thystame", 1)
    assert player.inventory.get("sibur") == 1
    assert player.inventory.get("food") == 1
    assert player.inventory.get("linemate") == 1
    assert player.inventory.get("deraumere") == 1
    assert player.inventory.get("mendiane") == 1
    assert player.inventory.get("phiras") == 1
    assert player.inventory.get("thystame") == 1


def test_inventory_remove():
    player = Player("mongol", "teams paiya", 5, 0)
    player.inventory.remove("sibur", 1)
    player.inventory.remove("food", 1)
    player.inventory.remove("linemate", 1)
    player.inventory.remove("mendiane", 1)
    player.inventory.remove("phiras", 1)
    player.inventory.remove("thystame", 1)
    player.inventory.remove("sibur", 1)
    assert player.inventory.get("sibur") == 0
    assert player.inventory.get("food") == 0
    assert player.inventory.get("linemate") == 0
    assert player.inventory.get("mendiane") == 0
    assert player.inventory.get("phiras") == 0
    assert player.inventory.get("thystame") == 0
