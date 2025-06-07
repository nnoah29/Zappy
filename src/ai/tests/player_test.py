import pytest
from src.ai.player import Player

def test_player_init():
    player = Player("mongol", "team paiya", 5, 0)
    assert player.id == "mongol"
    assert player.team == "team paiya"
    assert player.x == 5
    assert player.y == 0
    assert player.orientation == "N"


def test_player_North_move():
    player = Player("momo", "MTN", 0, 0)
    player.orientation = "N"
    player.move_forward(10, 10)
    assert player.x == 0
    assert player.y == 9

def test_player_South_move():
    player = Player("momo2", "MTN", 0, 0)
    player.orientation = "S"
    player.move_forward(10, 10)
    assert player.x == 0
    assert player.y == 1

def test_player_East_move():
    player = Player("momo3", "MTN", 0, 0)
    player.orientation = "E"
    player.move_forward(10, 10)
    assert player.x == 1
    assert player.y == 0

def test_player_West_move():
    player = Player("momo4", "MTN", 0, 0)
    player.orientation = "W"
    player.move_forward(10, 10)
    assert player.x == 9

