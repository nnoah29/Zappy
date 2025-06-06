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
        # Niveau 1 : 4 cases
        self.vision.set_level(1)
        self.assertEqual(self.vision.get_expected_vision_size(), 4)

        # Niveau 2 : 9 cases
        self.vision.set_level(2)
        self.assertEqual(self.vision.get_expected_vision_size(), 9)

        # Niveau 3 : 16 cases
        self.vision.set_level(3)
        self.assertEqual(self.vision.get_expected_vision_size(), 16)

    def test_get_case_position_level_1(self):
        """Test du calcul de position pour un joueur de niveau 1"""
        self.vision.set_level(1)
        
        # Case 0: Position du joueur
        self.assertEqual(self.vision.get_case_position(0), (0, 0))
        
        # Cases 1, 2, 3: Ligne y=1
        self.assertEqual(self.vision.get_case_position(1), (-1, 1))  # Gauche
        self.assertEqual(self.vision.get_case_position(2), (0, 1))   # Centre
        self.assertEqual(self.vision.get_case_position(3), (1, 1))   # Droite

    def test_get_case_position_level_2(self):
        """Test du calcul de position pour un joueur de niveau 2"""
        self.vision.set_level(2)
        
        # Case 0: Position du joueur
        self.assertEqual(self.vision.get_case_position(0), (0, 0))
        
        # Cases 1, 2, 3: Ligne y=1
        self.assertEqual(self.vision.get_case_position(1), (-1, 1))
        self.assertEqual(self.vision.get_case_position(2), (0, 1))
        self.assertEqual(self.vision.get_case_position(3), (1, 1))
        
        # Cases 4, 5, 6, 7, 8: Ligne y=2
        self.assertEqual(self.vision.get_case_position(4), (-2, 2))
        self.assertEqual(self.vision.get_case_position(5), (-1, 2))
        self.assertEqual(self.vision.get_case_position(6), (0, 2))
        self.assertEqual(self.vision.get_case_position(7), (1, 2))
        self.assertEqual(self.vision.get_case_position(8), (2, 2))

    def test_get_case_position_level_3(self):
        """Test du calcul de position pour un joueur de niveau 3"""
        self.vision.set_level(3)
        
        # Case 0: Position du joueur
        self.assertEqual(self.vision.get_case_position(0), (0, 0))
        
        # Cases 1, 2, 3: Ligne y=1
        self.assertEqual(self.vision.get_case_position(1), (-1, 1))
        self.assertEqual(self.vision.get_case_position(2), (0, 1))
        self.assertEqual(self.vision.get_case_position(3), (1, 1))
        
        # Cases 4, 5, 6, 7, 8: Ligne y=2
        self.assertEqual(self.vision.get_case_position(4), (-2, 2))
        self.assertEqual(self.vision.get_case_position(5), (-1, 2))
        self.assertEqual(self.vision.get_case_position(6), (0, 2))
        self.assertEqual(self.vision.get_case_position(7), (1, 2))
        self.assertEqual(self.vision.get_case_position(8), (2, 2))
        
        # Cases 9-15: Ligne y=3
        self.assertEqual(self.vision.get_case_position(9), (-3, 3))
        self.assertEqual(self.vision.get_case_position(10), (-2, 3))
        self.assertEqual(self.vision.get_case_position(11), (-1, 3))
        self.assertEqual(self.vision.get_case_position(12), (0, 3))
        self.assertEqual(self.vision.get_case_position(13), (1, 3))
        self.assertEqual(self.vision.get_case_position(14), (2, 3))
        self.assertEqual(self.vision.get_case_position(15), (3, 3))

    def test_get_case_position_invalid_index(self):
        """Test avec des index invalides."""
        self.vision.set_level(1)
        
        # Index négatif
        self.assertEqual(self.vision.get_case_position(-1), (-1, -1))
        
        # Index trop grand
        self.assertEqual(self.vision.get_case_position(4), (-1, -1))
        
        # Index limite valide
        self.assertEqual(self.vision.get_case_position(3), (1, 1))

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

    def test_parse_vision_multiple_same_objects(self):
        """Test du parsing avec plusieurs objets identiques dans une case."""
        self.protocol.look.return_value = "[player food food, deraumere deraumere deraumere]"
        result = self.vision.look()
        expected = [
            {"player": 1, "food": 2},
            {"deraumere": 3}
        ]
        self.assertEqual(result, expected)

    def test_find_nearest_object_level_1(self):
        """Test de la recherche de l'objet le plus proche niveau 1."""
        self.vision.set_level(1)
        # [player, food, , deraumere] correspond aux cases 0,1,2,3
        self.protocol.look.return_value = "[player, food, , deraumere]"
        
        # L'objet food est à la case 1 -> position (-1, 1)
        pos = self.vision.find_nearest_object("food")
        self.assertEqual(pos, (-1, 1))
        
        # L'objet deraumere est à la case 3 -> position (1, 1)
        pos = self.vision.find_nearest_object("deraumere")
        self.assertEqual(pos, (1, 1))
        
        # Objet inexistant
        pos = self.vision.find_nearest_object("linemate")
        self.assertEqual(pos, (-1, -1))

    def test_find_nearest_object_level_2(self):
        """Test de la recherche de l'objet le plus proche niveau 2."""
        self.vision.set_level(2)
        # Vision avec 9 cases: player à 0, food à 1, deraumere à 6
        self.protocol.look.return_value = "[player, food, , , , , deraumere, , ]"
        
        # L'objet food est à la case 1 -> position (-1, 1), distance = 2
        # L'objet deraumere est à la case 6 -> position (0, 2), distance = 2
        # Les deux sont à égale distance, food devrait être retourné (trouvé en premier)
        pos = self.vision.find_nearest_object("food")
        self.assertEqual(pos, (-1, 1))

    def test_get_players_in_vision_level_1(self):
        """Test de la détection des joueurs dans la vision (niveau 1)."""
        self.vision.set_level(1)
        # [player, player food, , player deraumere] - joueurs aux cases 0, 1, 3
        self.protocol.look.return_value = "[player, player food, , player deraumere]"
        players = self.vision.get_players_in_vision()
        expected = [(0, 0), (-1, 1), (1, 1)]  # Positions des 3 joueurs
        self.assertEqual(sorted(players), sorted(expected))

    def test_get_players_in_vision_multiple_same_case(self):
        """Test avec plusieurs joueurs dans la même case."""
        self.vision.set_level(1)
        # Deux joueurs dans la case 1
        self.protocol.look.return_value = "[player, player player, , ]"
        players = self.vision.get_players_in_vision()
        expected = [(0, 0), (-1, 1), (-1, 1)]  # 1 joueur à (0,0), 2 à (-1,1)
        self.assertEqual(sorted(players), sorted(expected))

    def test_get_players_in_vision_no_other_players(self):
        """Test quand il n'y a que le joueur courant."""
        self.vision.set_level(1)
        self.protocol.look.return_value = "[player, food, , deraumere]"
        players = self.vision.get_players_in_vision()
        expected = [(0, 0)]  # Seulement le joueur courant
        self.assertEqual(players, expected)

    def test_set_level_invalid(self):
        """Test de validation du niveau."""
        with self.assertRaises(ValueError):
            self.vision.set_level(0)
        
        with self.assertRaises(ValueError):
            self.vision.set_level(-1)
        
        # Niveau valide
        self.vision.set_level(1)
        self.assertEqual(self.vision.level, 1)

    def test_is_case_in_front(self):
        """Test de la vérification si une case est devant le joueur."""
        self.vision.set_level(2)
        
        # Case 0: joueur -> pas devant
        self.assertFalse(self.vision.is_case_in_front(0))
        
        # Case 2: position (0, 1) -> devant le joueur
        self.assertTrue(self.vision.is_case_in_front(2))
        
        # Case 6: position (0, 2) -> devant le joueur
        self.assertTrue(self.vision.is_case_in_front(6))
        
        # Case 1: position (-1, 1) -> pas devant (sur le côté)
        self.assertFalse(self.vision.is_case_in_front(1))

    def test_get_case_content(self):
        """Test de récupération du contenu d'une case par position."""
        self.vision.set_level(1)
        self.protocol.look.return_value = "[player, food, , deraumere]"
        
        # Position du joueur (0, 0) -> case 0
        content = self.vision.get_case_content(0, 0)
        self.assertEqual(content, {"player": 1})
        
        # Position (-1, 1) -> case 1
        content = self.vision.get_case_content(-1, 1)
        self.assertEqual(content, {"food": 1})
        
        # Position (1, 1) -> case 3
        content = self.vision.get_case_content(1, 1)
        self.assertEqual(content, {"deraumere": 1})
        
        # Position inexistante
        content = self.vision.get_case_content(5, 5)
        self.assertEqual(content, {})

if __name__ == '__main__':
    unittest.main()