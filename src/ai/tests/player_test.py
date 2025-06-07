import pytest
from src.ai.player import Player

def test_player_init():
    player = Player("mongol", "team paiya", 5, 0)
    assert player.id == "mongol"
    assert player.team == "team paiya"
    assert player.x == 5
    assert player.y == 0
    assert player.orientation == "N"

