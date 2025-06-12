#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from elevation_manager import ElevationManager
from protocol import ZappyProtocol
from vision import Vision
from ai.movement import Movement

class TestElevationManager(unittest.TestCase):
    """Tests pour la classe ElevationManager."""

    def setUp(self):
        """Initialise les tests."""
        self.protocol = Mock(spec=ZappyProtocol)
        self.vision = Mock(spec=Vision)
        self.movement = Mock(spec=Movement)
        self.elevation_manager = ElevationManager(self.protocol, self.vision, self.movement)

    def test_check_elevation_conditions_level_1(self):
        """Test des conditions d'élévation pour le niveau 1."""
        # Configure les mocks
        self.vision.look.return_value = [
            ["player", "linemate"],  # Case actuelle
            ["player"],
            ["food"]
        ]

        # Test les conditions
        result = self.elevation_manager.check_elevation_conditions()
        self.assertTrue(result)

    def test_check_elevation_conditions_level_2(self):
        """Test des conditions d'élévation pour le niveau 2."""
        # Configure les mocks
        self.elevation_manager.current_level = 2
        self.vision.look.return_value = [
            ["player", "player", "linemate", "deraumere", "sibur"],  # Case actuelle
            ["player"],
            ["food"]
        ]

        # Test les conditions
        result = self.elevation_manager.check_elevation_conditions()
        self.assertTrue(result)

    def test_check_elevation_conditions_insufficient_players(self):
        """Test des conditions d'élévation avec joueurs insuffisants."""
        # Configure les mocks
        self.elevation_manager.current_level = 2
        self.vision.look.return_value = [
            ["player", "linemate", "deraumere", "sibur"],  # Case actuelle
            ["food"]
        ]

        # Test les conditions
        result = self.elevation_manager.check_elevation_conditions()
        self.assertFalse(result)

    def test_check_elevation_conditions_insufficient_resources(self):
        """Test des conditions d'élévation avec ressources insuffisantes."""
        # Configure les mocks
        self.elevation_manager.current_level = 2
        self.vision.look.return_value = [
            ["player", "player", "linemate"],  # Case actuelle
            ["food"]
        ]

        # Test les conditions
        result = self.elevation_manager.check_elevation_conditions()
        self.assertFalse(result)

    def test_start_ritual(self):
        """Test du démarrage du rituel."""
        # Configure les mocks
        self.vision.look.return_value = [
            ["player", "linemate"],  # Case actuelle
            ["player"],
            ["food"]
        ]
        self.protocol.incantation.return_value = True

        # Test le démarrage
        result = self.elevation_manager.start_ritual()
        self.assertTrue(result)
        self.assertTrue(self.elevation_manager.ritual_in_progress)

    def test_check_ritual_status(self):
        """Test de la vérification du statut du rituel."""
        # Configure les mocks
        self.elevation_manager.ritual_in_progress = True
        self.vision.look.return_value = [
            ["player", "linemate"],  # Case actuelle
            ["player"],
            ["food"]
        ]

        # Test le statut
        result = self.elevation_manager.check_ritual_status()
        self.assertTrue(result)

    def test_complete_ritual(self):
        """Test de la complétion du rituel."""
        # Configure les mocks
        self.elevation_manager.ritual_in_progress = True
        self.vision.look.return_value = [
            ["player", "linemate"],  # Case actuelle
            ["player"],
            ["food"]
        ]
        self.protocol.incantation.return_value = True

        # Test la complétion
        result = self.elevation_manager.complete_ritual()
        self.assertTrue(result)
        self.assertEqual(self.elevation_manager.current_level, 2)
        self.assertFalse(self.elevation_manager.ritual_in_progress)

    def test_complete_ritual_conditions_not_met(self):
        """Test de la complétion du rituel quand les conditions ne sont plus remplies."""
        # Configure les mocks
        self.elevation_manager.ritual_in_progress = True
        self.vision.look.return_value = [
            ["player"],  # Case actuelle sans ressources
            ["food"]
        ]

        # Test la complétion
        result = self.elevation_manager.complete_ritual()
        self.assertFalse(result)
        self.assertFalse(self.elevation_manager.ritual_in_progress)

    def test_get_requirements(self):
        """Test de la récupération des conditions d'élévation."""
        # Test les conditions
        requirements = self.elevation_manager.get_requirements()
        self.assertEqual(requirements["player"], 1)
        self.assertEqual(requirements["linemate"], 1)
        self.assertEqual(requirements["deraumere"], 0)

    def test_reset(self):
        """Test de la réinitialisation."""
        # Configure l'état
        self.elevation_manager.ritual_in_progress = True
        self.elevation_manager.ritual_participants = [(1, 1), (2, 2)]

        # Test la réinitialisation
        self.elevation_manager.reset()
        self.assertFalse(self.elevation_manager.ritual_in_progress)
        self.assertEqual(len(self.elevation_manager.ritual_participants), 0)

    def test_is_ritual_in_progress(self):
        """Test de la vérification du statut du rituel."""
        # Test quand aucun rituel n'est en cours
        self.assertFalse(self.elevation_manager.is_ritual_in_progress())

        # Test quand un rituel est en cours
        self.elevation_manager.ritual_in_progress = True
        self.assertTrue(self.elevation_manager.is_ritual_in_progress())

if __name__ == '__main__':
    unittest.main()