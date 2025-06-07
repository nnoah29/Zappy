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
