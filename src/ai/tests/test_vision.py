#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from vision import Vision
from protocol import ZappyProtocol
from client import ZappyClient

class TestVision(unittest.TestCase):
    """Tests pour la classe Vision."""

    def setUp(self):
        """Initialise les objets nécessaires pour les tests."""
        self.client = ZappyClient("localhost", 3000, "test_team")
        self.protocol = ZappyProtocol(self.client)
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

    def test_get_case_position(self):
        """Teste le calcul des positions des cases."""
        # Test de la position du joueur
        self.assertEqual(self.vision.get_case_position(0), (0, 0))
        
        # Test des positions de la première ligne
        self.assertEqual(self.vision.get_case_position(1), (-1, 1))
        self.assertEqual(self.vision.get_case_position(2), (0, 1))
        self.assertEqual(self.vision.get_case_position(3), (1, 1))
        
        # Test des positions de la deuxième ligne
        self.assertEqual(self.vision.get_case_position(4), (-2, 2))
        self.assertEqual(self.vision.get_case_position(5), (-1, 2))
        self.assertEqual(self.vision.get_case_position(6), (0, 2))
        self.assertEqual(self.vision.get_case_position(7), (1, 2))
        self.assertEqual(self.vision.get_case_position(8), (2, 2))
        
    def test_get_case_index(self):
        """Teste le calcul des indices des cases."""
        # Test de la position du joueur
        self.assertEqual(self.vision.get_case_index(0, 0), 0)
        
        # Test des positions de la première ligne
        self.assertEqual(self.vision.get_case_index(-1, 1), 1)
        self.assertEqual(self.vision.get_case_index(0, 1), 2)
        self.assertEqual(self.vision.get_case_index(1, 1), 3)
        
        # Test des positions de la deuxième ligne
        self.assertEqual(self.vision.get_case_index(-2, 2), 4)
        self.assertEqual(self.vision.get_case_index(-1, 2), 5)
        self.assertEqual(self.vision.get_case_index(0, 2), 6)
        self.assertEqual(self.vision.get_case_index(1, 2), 7)
        self.assertEqual(self.vision.get_case_index(2, 2), 8)

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

    def test_analyze_environment(self):
        """Teste l'analyse de l'environnement."""
        # Simule une réponse de vision
        vision_response = "[player, food, linemate, player deraumere, food food, ]"
        self.vision.vision_data = self.protocol.parse_look_response(vision_response)
        
        # Analyse l'environnement
        env = self.vision.analyze_environment()
        
        # Vérifie les résultats
        self.assertEqual(len(env["players"]), 2)  # Un joueur sur la case 0 et un sur la case 3
        self.assertEqual(len(env["food"]), 3)  # Un food sur la case 1 et deux sur la case 4
        self.assertEqual(len(env["linemate"]), 1)  # Un linemate sur la case 2
        self.assertEqual(len(env["deraumere"]), 1)  # Un deraumere sur la case 3

    def test_find_nearest_object(self):
        """Teste la recherche de l'objet le plus proche."""
        # Simule une réponse de vision
        vision_response = "[player, food, linemate, player deraumere, food food, ]"
        self.vision.vision_data = self.protocol.parse_look_response(vision_response)
        
        # Test de la recherche de nourriture
        food_pos = self.vision.find_nearest_object("food")
        self.assertEqual(food_pos, (0, 1))  # La nourriture la plus proche est sur la case 1
        
        # Test de la recherche de linemate
        linemate_pos = self.vision.find_nearest_object("linemate")
        self.assertEqual(linemate_pos, (1, 1))  # Le linemate est sur la case 2

    def test_get_best_food_path(self):
        """Teste le calcul du meilleur chemin vers la nourriture."""
        # Simule une réponse de vision
        vision_response = "[player, food, linemate, player deraumere, food food, ]"
        self.vision.vision_data = self.protocol.parse_look_response(vision_response)
        
        # Calcule le chemin vers la nourriture
        path = self.vision.get_best_food_path()
        
        # Vérifie le chemin
        self.assertEqual(len(path), 1)  # Un seul mouvement nécessaire
        self.assertEqual(path[0], (0, 1))  # Déplacement vers la case 1

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
            self.vision.set_case_level(-1)
        
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