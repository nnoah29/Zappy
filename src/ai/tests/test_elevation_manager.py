#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
import logging
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from managers.elevation_manager import ElevationManager
from core.protocol import ZappyProtocol
from managers.vision_manager import VisionManager
from managers.inventory_manager import InventoryManager
from models.player import Player

class TestElevationManager(unittest.TestCase):
    """Tests unitaires pour ElevationManager."""

    def setUp(self):
        """Initialise les mocks et le ElevationManager pour chaque test."""
        self.protocol_mock = Mock(spec=ZappyProtocol)
        self.vision_manager_mock = Mock(spec=VisionManager)
        self.inventory_manager_mock = Mock(spec=InventoryManager)
        self.logger_mock = Mock()
        
        # Configuration des mocks
        self.player_mock = Mock()
        self.player_mock.level = 1
        self.player_mock.inventory = self.inventory_manager_mock
        self.vision_manager_mock.player = self.player_mock
        self.vision_manager_mock.get_case_content.return_value = ['player']
        
        self.inventory_manager_mock.inventory = {
            'food': 5,
            'linemate': 1,
            'deraumere': 0,
            'sibur': 0,
            'mendiane': 0,
            'phiras': 0,
            'thystame': 0
        }
        
        self.elevation_manager = ElevationManager(
            self.protocol_mock,
            self.vision_manager_mock,
            self.inventory_manager_mock,
            self.logger_mock
        )

    def test_initialization(self):
        """Test de l'initialisation du ElevationManager."""
        self.assertIsNotNone(self.elevation_manager)
        self.assertEqual(self.elevation_manager.elevation_cooldown, 300)
        self.assertFalse(self.elevation_manager.ritual_in_progress)

    def test_can_elevate_true(self):
        """Test de la vérification si l'élévation est possible (vrai)."""
        self.player_mock.level = 1
        self.inventory_manager_mock.inventory['linemate'] = 1
        self.vision_manager_mock.get_case_content.return_value = ['player']
        
        result = self.elevation_manager.can_elevate()
        
        self.assertTrue(result)

    def test_can_elevate_false_missing_resources(self):
        """Test de la vérification si l'élévation est possible (faux - ressources manquantes)."""
        self.player_mock.level = 1
        self.inventory_manager_mock.inventory['linemate'] = 0
        self.vision_manager_mock.get_case_content.return_value = ['player']
        
        result = self.elevation_manager.can_elevate()
        
        self.assertFalse(result)

    def test_can_elevate_false_missing_players(self):
        """Test de la vérification si l'élévation est possible (faux - joueurs manquants)."""
        self.player_mock.level = 2
        self.inventory_manager_mock.inventory['linemate'] = 1
        self.inventory_manager_mock.inventory['deraumere'] = 1
        self.inventory_manager_mock.inventory['sibur'] = 1
        self.vision_manager_mock.get_case_content.return_value = ['player']  # Seulement 1 joueur
        
        result = self.elevation_manager.can_elevate()
        
        self.assertFalse(result)

    def test_can_elevate_max_level(self):
        """Test de la vérification si l'élévation est possible au niveau maximum."""
        self.player_mock.level = 8
        
        result = self.elevation_manager.can_elevate()
        
        self.assertFalse(result)

    def test_start_elevation_success(self):
        """Test du démarrage d'élévation avec succès."""
        self.player_mock.level = 1
        self.inventory_manager_mock.inventory['linemate'] = 1
        self.vision_manager_mock.get_case_content.return_value = ['player']
        self.protocol_mock.set.return_value = True
        self.protocol_mock.incantation.return_value = "Elevation underway"
        self.protocol_mock.look.return_value = "[player]"
        self.vision_manager_mock.force_update_vision.return_value = True
        
        result = self.elevation_manager.start_elevation()
        
        self.assertTrue(result)
        self.protocol_mock.set.assert_called()
        self.protocol_mock.incantation.assert_called_once()

    def test_start_elevation_cannot_elevate(self):
        """Test du démarrage d'élévation impossible."""
        self.player_mock.level = 1
        self.inventory_manager_mock.inventory['linemate'] = 0
        
        result = self.elevation_manager.start_elevation()
        
        self.assertFalse(result)

    def test_start_elevation_set_failure(self):
        """Test du démarrage d'élévation avec échec de dépôt."""
        self.player_mock.level = 1
        self.inventory_manager_mock.inventory['linemate'] = 1
        self.vision_manager_mock.get_case_content.return_value = ['player']
        self.protocol_mock.set.return_value = False
        
        result = self.elevation_manager.start_elevation()
        
        self.assertFalse(result)

    def test_start_elevation_incantation_failure(self):
        """Test du démarrage d'élévation avec échec d'incantation."""
        self.player_mock.level = 1
        self.inventory_manager_mock.inventory['linemate'] = 1
        self.vision_manager_mock.get_case_content.return_value = ['player']
        self.protocol_mock.set.return_value = True
        self.protocol_mock.incantation.return_value = "ko"
        
        result = self.elevation_manager.start_elevation()
        
        self.assertFalse(result)

    def test_get_required_players_level_1(self):
        """Test de la récupération du nombre de joueurs requis pour le niveau 1."""
        result = self.elevation_manager._get_required_players(1)
        
        self.assertEqual(result, 1)

    def test_get_required_players_level_2(self):
        """Test de la récupération du nombre de joueurs requis pour le niveau 2."""
        result = self.elevation_manager._get_required_players(2)
        
        self.assertEqual(result, 2)

    def test_get_required_players_level_4(self):
        """Test de la récupération du nombre de joueurs requis pour le niveau 4."""
        result = self.elevation_manager._get_required_players(4)
        
        self.assertEqual(result, 4)

    def test_get_required_players_invalid_level(self):
        """Test de la récupération du nombre de joueurs requis pour un niveau invalide."""
        result = self.elevation_manager._get_required_players(999)
        
        self.assertEqual(result, 0)

    def test_get_needed_resources_all_available(self):
        """Test de la récupération des ressources nécessaires (toutes disponibles)."""
        self.player_mock.level = 1
        self.inventory_manager_mock.inventory['linemate'] = 1
        
        result = self.elevation_manager.get_needed_resources()
        
        self.assertEqual(result, [])

    def test_get_needed_resources_missing(self):
        """Test de la récupération des ressources nécessaires (manquantes)."""
        self.player_mock.level = 1
        self.inventory_manager_mock.inventory['linemate'] = 0
        
        result = self.elevation_manager.get_needed_resources()
        
        self.assertIn('linemate', result)

    def test_get_needed_resources_invalid_level(self):
        """Test de la récupération des ressources nécessaires pour un niveau invalide."""
        self.player_mock.level = 999
        
        result = self.elevation_manager.get_needed_resources()
        
        self.assertEqual(result, [])

    def test_get_current_level(self):
        """Test de la récupération du niveau actuel."""
        self.player_mock.level = 3
        
        result = self.elevation_manager.get_current_level()
        
        self.assertEqual(result, 3)

    def test_get_requirements(self):
        """Test de la récupération des prérequis."""
        self.player_mock.level = 1
        
        result = self.elevation_manager.get_requirements()
        
        self.assertIsInstance(result, dict)
        self.assertIn('linemate', result)

    def test_is_ritual_in_progress(self):
        """Test de la vérification si un rituel est en cours."""
        self.elevation_manager.ritual_in_progress = True
        
        result = self.elevation_manager.is_ritual_in_progress()
        
        self.assertTrue(result)

    def test_is_ritual_not_in_progress(self):
        """Test de la vérification si aucun rituel n'est en cours."""
        self.elevation_manager.ritual_in_progress = False
        
        result = self.elevation_manager.is_ritual_in_progress()
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main() 