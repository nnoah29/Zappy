from src.ai.player import Player

def test_player_logs_creation(caplog):
    with caplog.at_level("INFO"):
        player = Player("logtest01", "LogTeam", 1, 1)

    assert "player logtest01 created on team LogTeam at (1, 1)" in caplog.text
