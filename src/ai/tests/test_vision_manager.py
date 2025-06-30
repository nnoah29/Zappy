#!/usr/bin/env python3

import unittest
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from managers.vision_manager import VisionManager
from core.protocol import ZappyProtocol
from models.player import Player
from models.map import Map

class TestVisionManager(unittest.TestCase):
    """Tests unitaires pour VisionManager."""

    def setUp(self):
        """Initialise les mocks et le VisionManager pour chaque test."""
        self.protocol_mock = Mock(spec=ZappyProtocol)
        self.player_mock = Mock(spec=Player)
        self.map_mock = Mock(spec=Map)
        self.logger_mock = Mock()
        
        self.map_mock.width = 10
        self.map_mock.height = 10
        self.player_mock.get_position.return_value = (5, 5)
        
        self.vision_manager = VisionManager(
            self.protocol_mock,
            self.player_mock,
            self.map_mock,
            self.logger_mock
        )

    def test_initialization(self):
        """Test de l'initialisation du VisionManager."""
        self.assertIsNotNone(self.vision_manager)
        self.assertEqual(self.vision_manager.level, 1)
        self.assertEqual(self.vision_manager.vision_cooldown, 7)

    def test_update_vision_success(self):
        """Test de la mise à jour de vision avec succès."""
        self.protocol_mock.look.return_value = "[player, food, linemate]"
        
        result = self.vision_manager.update_vision()
        
        self.assertTrue(result)
        self.assertEqual(len(self.vision_manager.vision), 3)

    def test_update_vision_connection_error(self):
        """Test de la mise à jour de vision avec erreur de connexion."""
        self.protocol_mock.look.side_effect = ConnectionError("Connexion perdue")
        
        result = self.vision_manager.update_vision()
        
        self.assertFalse(result)

    def test_update_vision_invalid_response(self):
        """Test de la mise à jour de vision avec réponse invalide."""
        self.protocol_mock.look.return_value = "invalid"
        
        result = self.vision_manager.update_vision()
        
        self.assertTrue(result)

    def test_force_update_vision_success(self):
        """Test de la mise à jour forcée de vision avec succès."""
        self.protocol_mock.look.return_value = "[player, food]"
        
        result = self.vision_manager.force_update_vision()
        
        self.assertTrue(result)
        self.assertEqual(len(self.vision_manager.vision), 2)

    def test_parse_vision_valid(self):
        """Test du parsing de vision valide."""
        response = "[player, food, linemate]"
        
        result = self.vision_manager._parse_vision(response)
        
        self.assertEqual(result, [['player'], ['food'], ['linemate']])

    def test_parse_vision_empty(self):
        """Test du parsing de vision vide."""
        response = "[]"
        
        result = self.vision_manager._parse_vision(response)
        
        self.assertEqual(result, [[]])

    def test_parse_vision_complex(self):
        """Test du parsing de vision complexe."""
        response = "[player food, linemate deraumere, sibur]"
        
        result = self.vision_manager._parse_vision(response)
        
        self.assertEqual(result, [['player', 'food'], ['linemate', 'deraumere'], ['sibur']])

    def test_get_case_content_valid(self):
        """Test de la récupération du contenu d'une case valide."""
        self.vision_manager.vision = [['player'], ['food'], ['linemate']]
        
        result = self.vision_manager.get_case_content(0, 0)
        
        self.assertEqual(result, ['player'])

    def test_get_case_content_invalid_index(self):
        """Test de la récupération du contenu d'une case avec index invalide."""
        self.vision_manager.vision = [['player'], ['food']]
        
        result = self.vision_manager.get_case_content(999, 999)
        
        self.assertEqual(result, [])

    def test_get_case_content_none_vision(self):
        """Test de la récupération du contenu d'une case sans vision."""
        self.vision_manager.vision = None
        
        result = self.vision_manager.get_case_content(0, 0)
        
        self.assertEqual(result, [])

    def test_get_vision_index_center(self):
        """Test du calcul d'index pour la case centrale."""
        index = self.vision_manager._get_vision_index(0, 0)
        
        self.assertEqual(index, 0)

    def test_get_vision_index_north(self):
        """Test du calcul d'index pour la case au nord."""
        index = self.vision_manager._get_vision_index(0, -1)
        
        self.assertEqual(index, 7)

    def test_get_vision_index_east(self):
        """Test du calcul d'index pour la case à l'est."""
        index = self.vision_manager._get_vision_index(1, 0)
        
        self.assertEqual(index, 1)

    def test_get_vision_index_south(self):
        """Test du calcul d'index pour la case au sud."""
        index = self.vision_manager._get_vision_index(0, 1)
        
        self.assertEqual(index, 3)

    def test_get_vision_index_west(self):
        """Test du calcul d'index pour la case à l'ouest."""
        index = self.vision_manager._get_vision_index(-1, 0)
        
        self.assertEqual(index, 5)

    def test_find_nearest_object_found(self):
        """Test de la recherche d'objet le plus proche trouvé."""
        self.vision_manager.vision = [['player'], ['food'], ['linemate']]
        
        result = self.vision_manager.find_nearest_object('food')
        
        self.assertEqual(result, (1, 0))

    def test_find_nearest_object_not_found(self):
        """Test de la recherche d'objet le plus proche non trouvé."""
        self.vision_manager.vision = [['player'], ['linemate']]
        
        result = self.vision_manager.find_nearest_object('food')
        
        self.assertIsNone(result)

    def test_find_nearest_resource_not_found(self):
        """Test de la recherche de ressource la plus proche non trouvée."""
        self.vision_manager.vision = [['player'], ['linemate']]
        
        result = self.vision_manager.find_nearest_resource('food')
        
        self.assertIsNone(result)

    def test_get_players_in_vision(self):
        """Test de la récupération des joueurs dans la vision."""
        self.vision_manager.vision = [['player'], ['player'], ['food']]
        
        result = self.vision_manager.get_players_in_vision()
        
        self.assertEqual(len(result), 2)

    def test_get_players_in_vision_no_players(self):
        """Test de la récupération des joueurs dans la vision sans joueurs."""
        self.vision_manager.vision = [['food'], ['linemate']]
        
        result = self.vision_manager.get_players_in_vision()
        
        self.assertEqual(len(result), 0)

    def test_get_vision_range(self):
        """Test de la récupération de la portée de vision."""
        result = self.vision_manager.get_vision_range()
        
        self.assertEqual(result, 1)

    def test_can_update_vision(self):
        """Test de la vérification si la vision peut être mise à jour."""
        result = self.vision_manager.can_update_vision()
        
        self.assertIsInstance(result, bool)

    def test_set_level(self):
        """Test de la définition du niveau."""
        self.vision_manager.set_level(3)
        
        self.assertEqual(self.vision_manager.level, 3)

    def test_get_resources_in_range(self):
        """Test de la récupération des ressources dans une portée."""
        self.vision_manager.vision = [['food'], ['linemate'], ['deraumere']]
        
        result = self.vision_manager.get_resources_in_range(2)
        
        self.assertIsInstance(result, dict)

    def test_is_position_safe(self):
        """Test de la vérification si une position est sûre."""
        result = self.vision_manager.is_position_safe((5, 5))
        
        self.assertIsInstance(result, bool)

    def test_get_best_path_to_resource(self):
        """Test de la récupération du meilleur chemin vers une ressource."""
        self.vision_manager.vision = [['player'], ['food'], ['linemate']]
        
        result = self.vision_manager.get_best_path_to_resource('food')
        
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()