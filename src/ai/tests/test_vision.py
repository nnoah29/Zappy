#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from vision import Vision
from protocol import ZappyProtocol

class TestVision(unittest.TestCase):
    """Tests pour la classe Vision."""

    def setUp(self):
        """Initialise les tests."""
        self.protocol = Mock(spec=ZappyProtocol)
        self.vision = Vision(self.protocol)

    def test_get_expected_vision_size(self):
        """Test du calcul de la taille attendue de la vision."""
        # Niveau 1 : 4 cases (2x2)
        self.vision.set_level(1)
        self.assertEqual(self.vision.get_expected_vision_size(), 4)

        # Niveau 2 : 16 cases (4x4)
        self.vision.set_level(2)
        self.assertEqual(self.vision.get_expected_vision_size(), 16)

        # Niveau 3 : 36 cases (6x6)
        self.vision.set_level(3)
        self.assertEqual(self.vision.get_expected_vision_size(), 36)

    def test_get_case_position_level_1(self):
        """Test du calcul de position pour un joueur de niveau 1."""
        self.vision.set_level(1)
        
        # Test de la position du joueur
        self.assertEqual(self.vision.get_case_position(0), (0, 0))
        
        # Test des positions autour du joueur (2x2)
        self.assertEqual(self.vision.get_case_position(1), (-1, -1))  # Haut gauche
        self.assertEqual(self.vision.get_case_position(2), (0, -1))   # Haut droite
        self.assertEqual(self.vision.get_case_position(3), (-1, 0))   # Bas gauche
        self.assertEqual(self.vision.get_case_position(4), (0, 0))    # Bas droite

    def test_get_case_position_level_2(self):
        """Test du calcul de position pour un joueur de niveau 2."""
        self.vision.set_level(2)
        
        # Test de la position du joueur
        self.assertEqual(self.vision.get_case_position(0), (0, 0))
        
        # Test des positions autour du joueur (4x4)
        # Première ligne
        self.assertEqual(self.vision.get_case_position(1), (-2, -2))  # Coin haut gauche
        self.assertEqual(self.vision.get_case_position(2), (-1, -2))  # Haut gauche
        self.assertEqual(self.vision.get_case_position(3), (0, -2))   # Haut centre
        self.assertEqual(self.vision.get_case_position(4), (1, -2))   # Haut droite
        
        # Deuxième ligne
        self.assertEqual(self.vision.get_case_position(5), (-2, -1))  # Milieu gauche
        self.assertEqual(self.vision.get_case_position(6), (-1, -1))  # Milieu haut gauche
        self.assertEqual(self.vision.get_case_position(7), (0, -1))   # Milieu haut
        self.assertEqual(self.vision.get_case_position(8), (1, -1))   # Milieu haut droite
        
        # Troisième ligne
        self.assertEqual(self.vision.get_case_position(9), (-2, 0))   # Centre gauche
        self.assertEqual(self.vision.get_case_position(10), (-1, 0))  # Centre haut gauche
        self.assertEqual(self.vision.get_case_position(11), (0, 0))   # Centre
        self.assertEqual(self.vision.get_case_position(12), (1, 0))   # Centre haut droite
        
        # Quatrième ligne
        self.assertEqual(self.vision.get_case_position(13), (-2, 1))  # Bas gauche
        self.assertEqual(self.vision.get_case_position(14), (-1, 1))  # Bas haut gauche
        self.assertEqual(self.vision.get_case_position(15), (0, 1))   # Bas centre
        self.assertEqual(self.vision.get_case_position(16), (1, 1))   # Bas droite

    def test_parse_vision_empty(self):
        """Test du parsing d'une vision vide."""
        self.protocol.look.return_value = "[]"
        result = self.vision.look()
        self.assertEqual(result, [])

    def test_parse_vision_single_case(self):
        """Test du parsing d'une vision avec une seule case."""
        self.protocol.look.return_value = "[player]"
        result = self.vision.look()
        self.assertEqual(result, [{"player": 1}])

    def test_parse_vision_multiple_cases(self):
        """Test du parsing d'une vision avec plusieurs cases."""
        self.protocol.look.return_value = "[player, food, , player deraumere]"
        result = self.vision.look()
        expected = [
            {"player": 1},
            {"food": 1},
            {},
            {"player": 1, "deraumere": 1}
        ]
        self.assertEqual(result, expected)

    def test_find_nearest_object(self):
        """Test de la recherche de l'objet le plus proche."""
        self.protocol.look.return_value = "[player, food, , player deraumere]"
        pos = self.vision.find_nearest_object("food")
        self.assertEqual(pos, (-1, -1))  # Position de la case 1 dans la grille 2x2

    def test_get_players_in_vision_level_1(self):
        """Test de la détection des joueurs dans la vision (niveau 1)."""
        self.vision.set_level(1)
        self.protocol.look.return_value = "[player, player food, , player deraumere]"
        players = self.vision.get_players_in_vision()
        expected = [(0, 0), (-1, -1)]  # Positions des joueurs dans la grille 2x2
        self.assertEqual(players, expected)

    def test_get_players_in_vision_level_2(self):
        """Test de la détection des joueurs dans la vision (niveau 2)."""
        self.vision.set_level(2)
        self.protocol.look.return_value = "[player, player food, , player deraumere]"
        players = self.vision.get_players_in_vision()
        expected = [(0, 0), (-1, -1)]  # Positions des joueurs dans la grille 4x4
        self.assertEqual(players, expected)

if __name__ == '__main__':
    unittest.main()