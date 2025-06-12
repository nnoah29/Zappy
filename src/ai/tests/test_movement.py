#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from ai.movement import Movement
from protocol import ZappyProtocol
from vision import Vision

class TestMovement(unittest.TestCase):
    """Tests pour la classe Movement."""

    def setUp(self):
        """Initialise les tests."""
        self.protocol = Mock(spec=ZappyProtocol)
        self.vision = Mock(spec=Vision)
        self.movement = Movement(self.protocol, self.vision)

    def test_move_to_position_success(self):
        """Test d'un déplacement réussi."""
        # Configure les mocks
        self.vision.look.return_value = [
            {"player": 1},  # Position du joueur
            {},            # Case accessible
            {"player": 1}, # Case bloquée
            {}            # Case accessible
        ]
        self.vision.get_case_position.side_effect = [
            (0, 0),   # Position du joueur
            (1, 0),   # Case à droite
            (0, 1),   # Case en haut
            (-1, 0)   # Case à gauche
        ]
        self.protocol.forward.return_value = True
        self.protocol.right.return_value = True
        self.protocol.left.return_value = True

        # Test le déplacement
        result = self.movement.move_to_position((1, 0))
        self.assertTrue(result)
        self.protocol.right.assert_called_once()
        self.protocol.forward.assert_called_once()

    def test_move_to_position_blocked(self):
        """Test d'un déplacement bloqué."""
        # Configure les mocks
        self.vision.look.return_value = [
            {"player": 1},  # Position du joueur
            {"player": 1}, # Case bloquée
            {},            # Case accessible
            {}            # Case accessible
        ]
        self.vision.get_case_position.side_effect = [
            (0, 0),   # Position du joueur
            (1, 0),   # Case à droite
            (0, 1),   # Case en haut
            (-1, 0)   # Case à gauche
        ]

        # Test le déplacement
        result = self.movement.move_to_position((1, 0))
        self.assertFalse(result)

    def test_rotate_to_direction(self):
        """Test des rotations."""
        # Test rotation à droite
        commands = self.movement._rotate_to_direction(1)  # Est
        self.assertEqual(commands, ["right"])
        self.assertEqual(self.movement.current_direction, 1)

        # Test rotation à gauche
        commands = self.movement._rotate_to_direction(0)  # Nord
        self.assertEqual(commands, ["left"])
        self.assertEqual(self.movement.current_direction, 0)

        # Test rotation de 180 degrés
        commands = self.movement._rotate_to_direction(2)  # Sud
        self.assertEqual(commands, ["right", "right"])
        self.assertEqual(self.movement.current_direction, 2)

    def test_is_stuck(self):
        """Test de la détection de blocage."""
        # Simule un joueur bloqué en ajoutant la même position plusieurs fois
        for _ in range(5):
            self.movement.last_positions.append((0, 0))
        
        # Vérifie que le joueur est considéré comme bloqué
        self.assertTrue(self.movement._is_stuck())
        self.assertEqual(self.movement.stuck_count, 1)

    def test_reset_stuck_counter(self):
        """Test de la réinitialisation du compteur de blocage."""
        # Simule un joueur bloqué
        for _ in range(5):
            self.movement.last_positions.append((0, 0))
        
        # Réinitialise le compteur
        self.movement.reset_stuck_counter()
        
        self.assertEqual(self.movement.stuck_count, 0)
        self.assertEqual(len(self.movement.last_positions), 0)

if __name__ == '__main__':
    unittest.main() 