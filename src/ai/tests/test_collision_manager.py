#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch, MagicMock
import logging
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from managers.collision_manager import CollisionManager
from managers.vision_manager import VisionManager
from managers.movement_manager import MovementManager
from core.protocol import ZappyProtocol

class TestCollisionManager(unittest.TestCase):
    """Tests unitaires pour CollisionManager."""

    def setUp(self):
        """Initialise les mocks et le CollisionManager pour chaque test."""
        self.protocol_mock = Mock(spec=ZappyProtocol)
        self.vision_manager_mock = Mock(spec=VisionManager)
        self.movement_manager_mock = Mock(spec=MovementManager)
        self.logger_mock = Mock()
        
        self.player_mock = Mock()
        self.vision_manager_mock.player = self.player_mock
        
        self.collision_manager = CollisionManager(
            self.protocol_mock,
            self.vision_manager_mock,
            self.movement_manager_mock,
            self.logger_mock
        )

    def test_initialization(self):
        """Test de l'initialisation du CollisionManager."""
        self.assertIsNotNone(self.collision_manager)
        self.assertEqual(self.collision_manager.collision_count, 0)
        self.assertEqual(self.collision_manager.max_escape_attempts, 3)

    def test_check_collision_no_players(self):
        """Test de la vérification de collision sans joueurs."""
        self.vision_manager_mock.get_players_in_vision.return_value = []
        
        result = self.collision_manager.check_collision()
        
        self.assertFalse(result)

    def test_check_collision_with_players(self):
        """Test de la vérification de collision avec joueurs."""
        self.vision_manager_mock.get_players_in_vision.return_value = [(0, 0), (1, 0)]
        
        result = self.collision_manager.check_collision()
        
        self.assertTrue(result)

    def test_check_collision_players_not_on_same_tile(self):
        """Test de la vérification de collision avec joueurs sur des cases différentes."""
        self.vision_manager_mock.get_players_in_vision.return_value = [(1, 0), (0, 1)]
        
        result = self.collision_manager.check_collision()
        
        self.assertFalse(result)

    def test_eject_other_players_success(self):
        """Test de l'éjection d'autres joueurs avec succès."""
        self.vision_manager_mock.vision_data = [['player', 'player']]
        self.protocol_mock.eject.return_value = True
        
        result = self.collision_manager.eject_other_players()
        
        self.assertTrue(result)
        self.protocol_mock.eject.assert_called_once()

    def test_eject_other_players_failure(self):
        """Test de l'éjection d'autres joueurs en échec."""
        self.vision_manager_mock.vision_data = [['player', 'player']]
        self.protocol_mock.eject.return_value = False
        
        result = self.collision_manager.eject_other_players()
        
        self.assertFalse(result)

    def test_eject_other_players_no_other_players(self):
        """Test de l'éjection sans autres joueurs."""
        self.vision_manager_mock.vision_data = [['player']]
        
        result = self.collision_manager.eject_other_players()
        
        self.assertTrue(result)
        self.protocol_mock.eject.assert_not_called()

    def test_eject_other_players_empty_vision(self):
        """Test de l'éjection avec vision vide."""
        self.vision_manager_mock.vision_data = []
        
        result = self.collision_manager.eject_other_players()
        
        self.assertFalse(result)

    def test_avoid_collision_success(self):
        """Test de l'évitement de collision avec succès."""
        self.vision_manager_mock.get_players_in_vision.return_value = [(0, 0)]
        self.player_mock.get_direction.return_value = 0
        self.vision_manager_mock.get_case_content.return_value = ['food']
        self.movement_manager_mock.turn_right.return_value = True
        self.movement_manager_mock.move_forward.return_value = True
        
        result = self.collision_manager.avoid_collision()
        
        self.assertTrue(result)

    def test_avoid_collision_no_players(self):
        """Test de l'évitement de collision sans joueurs."""
        self.vision_manager_mock.get_players_in_vision.return_value = []
        
        result = self.collision_manager.avoid_collision()
        
        self.assertFalse(result)

    def test_avoid_collision_all_directions_blocked(self):
        """Test de l'évitement de collision avec toutes les directions bloquées."""
        self.vision_manager_mock.get_players_in_vision.return_value = [(0, 0)]
        self.player_mock.get_direction.return_value = 0
        self.vision_manager_mock.get_case_content.return_value = ['player']
        self.movement_manager_mock.turn_right.return_value = True
        self.movement_manager_mock.move_forward.return_value = False
        
        result = self.collision_manager.avoid_collision()
        
        self.assertFalse(result)

    def test_can_check_collision_true(self):
        """Test de la vérification si on peut vérifier les collisions (vrai)."""
        # Forcer le temps à être supérieur au cooldown
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000
            self.collision_manager.last_collision_time = 990
            
            result = self.collision_manager.can_check_collision()
            
            self.assertTrue(result)

    def test_can_check_collision_false(self):
        """Test de la vérification si on peut vérifier les collisions (faux)."""
        # Forcer le temps à être inférieur au cooldown
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000
            self.collision_manager.last_collision_time = 995
            
            result = self.collision_manager.can_check_collision()
            
            self.assertFalse(result)

    def test_handle_collision_no_collision(self):
        """Test de la gestion de collision sans collision."""
        self.collision_manager.check_collision = Mock(return_value=False)
        
        result = self.collision_manager.handle_collision()
        
        self.assertTrue(result)
        self.assertEqual(self.collision_manager.escape_attempts, 0)

    def test_handle_collision_avoided(self):
        """Test de la gestion de collision évitée."""
        self.collision_manager.check_collision = Mock(return_value=True)
        self.collision_manager.avoid_collision = Mock(return_value=True)
        
        result = self.collision_manager.handle_collision()
        
        self.assertTrue(result)
        self.assertEqual(self.collision_manager.escape_attempts, 0)

    def test_handle_collision_not_avoided(self):
        """Test de la gestion de collision non évitée."""
        self.collision_manager.check_collision = Mock(return_value=True)
        self.collision_manager.avoid_collision = Mock(return_value=False)
        initial_attempts = self.collision_manager.escape_attempts
        
        result = self.collision_manager.handle_collision()
        
        self.assertFalse(result)
        self.assertEqual(self.collision_manager.escape_attempts, initial_attempts + 1)

    def test_reset(self):
        """Test de la réinitialisation."""
        self.collision_manager.collision_count = 5
        self.collision_manager.escape_attempts = 3
        self.collision_manager.stuck_count = 2
        
        self.collision_manager.reset()
        
        self.assertEqual(self.collision_manager.collision_count, 0)
        self.assertEqual(self.collision_manager.escape_attempts, 0)
        self.assertEqual(self.collision_manager.stuck_count, 0)

    def test_get_stuck_count(self):
        """Test de la récupération du nombre de blocages."""
        self.collision_manager.stuck_count = 3
        
        result = self.collision_manager.get_stuck_count()
        
        self.assertEqual(result, 3)

    def test_is_severely_stuck_true(self):
        """Test de la vérification si le joueur est sévèrement bloqué (vrai)."""
        self.collision_manager.stuck_count = 4
        self.collision_manager.max_stuck_count = 3
        
        result = self.collision_manager.is_severely_stuck()
        
        self.assertTrue(result)

    def test_is_severely_stuck_false(self):
        """Test de la vérification si le joueur est sévèrement bloqué (faux)."""
        self.collision_manager.stuck_count = 2
        self.collision_manager.max_stuck_count = 3
        
        result = self.collision_manager.is_severely_stuck()
        
        self.assertFalse(result)

    def test_check_collision_exception(self):
        """Test de la vérification de collision avec exception."""
        self.vision_manager_mock.get_players_in_vision.side_effect = Exception("Test error")
        
        result = self.collision_manager.check_collision()
        
        self.assertFalse(result)
        self.logger_mock.error.assert_called()

    def test_eject_other_players_exception(self):
        """Test de l'éjection d'autres joueurs avec exception."""
        self.vision_manager_mock.vision_data = [['player', 'player']]
        self.protocol_mock.eject.side_effect = Exception("Test error")
        
        result = self.collision_manager.eject_other_players()
        
        self.assertFalse(result)
        self.logger_mock.error.assert_called()

    def test_avoid_collision_exception(self):
        """Test de l'évitement de collision avec exception."""
        self.vision_manager_mock.get_players_in_vision.side_effect = Exception("Test error")
        
        result = self.collision_manager.avoid_collision()
        
        self.assertFalse(result)
        self.logger_mock.error.assert_called()

if __name__ == '__main__':
    unittest.main() 