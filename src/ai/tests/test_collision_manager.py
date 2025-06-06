#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from collision_manager import CollisionManager
from protocol import ZappyProtocol
from vision import Vision
from movement import Movement

class TestCollisionManager(unittest.TestCase):
    """Tests pour la classe CollisionManager."""

    def setUp(self):
        """Initialise les tests."""
        self.protocol = Mock(spec=ZappyProtocol)
        self.vision = Mock(spec=Vision)
        self.movement = Mock(spec=Movement)
        self.collision_manager = CollisionManager(self.protocol, self.vision, self.movement)

    def test_check_collision_detection(self):
        """Test de la détection de collision."""
        self.vision.get_players_in_vision.return_value = [(0, 1)]  # Joueur devant
        self.vision.is_case_in_front.return_value = True

        result = self.collision_manager.check_collision()
        self.assertTrue(result)
        self.assertEqual(self.collision_manager.collision_count, 1)
        self.assertEqual(self.collision_manager.last_collision_pos, (0, 1))

    def test_check_collision_no_collision(self):
        """Test quand il n'y a pas de collision."""
        self.vision.get_players_in_vision.return_value = []  # Pas de joueurs

        result = self.collision_manager.check_collision()
        self.assertFalse(result)
        self.assertEqual(self.collision_manager.collision_count, 0)
        self.assertIsNone(self.collision_manager.last_collision_pos)

    def test_handle_collision_normal(self):
        """Test de la gestion d'une collision normale."""
        self.vision.get_players_in_vision.return_value = [(0, 1)]
        self.vision.is_case_in_front.return_value = True
        self.protocol.right.return_value = True
        self.protocol.forward.return_value = True

        # Simule une collision puis sa résolution
        self.collision_manager.check_collision()
        self.vision.is_case_in_front.return_value = False  # Plus de collision après évasion
        result = self.collision_manager.handle_collision()

        self.assertTrue(result)
        self.assertEqual(self.collision_manager.escape_attempts, 0)

    def test_handle_collision_severe(self):
        """Test de la gestion d'une collision sévère."""
        self.vision.get_players_in_vision.return_value = [(0, 1)]
        self.vision.is_case_in_front.return_value = True
        self.protocol.right.return_value = True
        self.protocol.forward.return_value = True

        # Simule plusieurs tentatives d'évasion
        for _ in range(self.collision_manager.max_escape_attempts):
            self.collision_manager.handle_collision()

        # La prochaine tentative devrait utiliser la stratégie sévère
        self.vision.is_case_in_front.return_value = False  # Plus de collision après évasion
        result = self.collision_manager.handle_collision()

        self.assertTrue(result)
        self.assertEqual(self.collision_manager.escape_attempts, 0)

    def test_reset(self):
        """Test de la réinitialisation."""
        # Configure un état de collision
        self.collision_manager.collision_count = 5
        self.collision_manager.last_collision_pos = (1, 1)
        self.collision_manager.escape_attempts = 3

        # Réinitialise
        self.collision_manager.reset()

        # Vérifie l'état réinitialisé
        self.assertEqual(self.collision_manager.collision_count, 0)
        self.assertIsNone(self.collision_manager.last_collision_pos)
        self.assertEqual(self.collision_manager.escape_attempts, 0)

if __name__ == '__main__':
    unittest.main() 