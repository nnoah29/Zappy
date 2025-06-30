#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
import logging
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from managers.inventory_manager import InventoryManager
from core.protocol import ZappyProtocol

class TestInventoryManager(unittest.TestCase):
    """Tests unitaires pour InventoryManager."""

    def setUp(self):
        """Initialise les mocks et le InventoryManager pour chaque test."""
        self.protocol_mock = Mock(spec=ZappyProtocol)
        self.logger_mock = Mock()
        self.player_mock = Mock()
        
        self.inventory_manager = InventoryManager(
            self.protocol_mock,
            self.player_mock,
            self.logger_mock
        )

    def test_initialization(self):
        """Test de l'initialisation du InventoryManager."""
        self.assertIsNotNone(self.inventory_manager)
        self.assertIsInstance(self.inventory_manager.inventory, dict)
        self.assertEqual(self.inventory_manager.inventory['food'], 0)
        self.assertEqual(self.inventory_manager.inventory['linemate'], 0)

    def test_take_object_success(self):
        """Test de la prise d'objet avec succès."""
        self.protocol_mock.take.return_value = True
        self.protocol_mock.inventory.return_value = "[food 1, linemate 0]"
        
        result = self.inventory_manager.take_object("food")
        
        self.assertTrue(result)
        self.protocol_mock.take.assert_called_once_with("food")

    def test_take_object_failure(self):
        """Test de la prise d'objet en échec."""
        self.protocol_mock.take.return_value = False
        
        result = self.inventory_manager.take_object("food")
        
        self.assertFalse(result)

    def test_take_object_connection_error(self):
        """Test de la prise d'objet avec erreur de connexion."""
        self.protocol_mock.take.side_effect = ConnectionError("Connexion perdue")
        
        result = self.inventory_manager.take_object("food")
        
        self.assertFalse(result)
        self.logger_mock.error.assert_called()

    def test_drop_object_success(self):
        """Test du dépôt d'objet avec succès."""
        self.inventory_manager.inventory['food'] = 5
        self.protocol_mock.set.return_value = True
        
        result = self.inventory_manager.drop_object("food")
        
        self.assertTrue(result)
        self.protocol_mock.set.assert_called_once_with("food")
        self.assertEqual(self.inventory_manager.inventory['food'], 4)

    def test_drop_object_failure(self):
        """Test du dépôt d'objet en échec."""
        self.inventory_manager.inventory['food'] = 5
        self.protocol_mock.set.return_value = False
        
        result = self.inventory_manager.drop_object("food")
        
        self.assertFalse(result)
        self.assertEqual(self.inventory_manager.inventory['food'], 5)  # Ne change pas

    def test_drop_object_connection_error(self):
        """Test du dépôt d'objet avec erreur de connexion."""
        self.inventory_manager.inventory['food'] = 5
        self.protocol_mock.set.side_effect = ConnectionError("Connexion perdue")
        
        result = self.inventory_manager.drop_object("food")
        
        self.assertFalse(result)
        self.logger_mock.error.assert_called()

    def test_update_inventory_success(self):
        """Test de la mise à jour d'inventaire avec succès."""
        self.protocol_mock.inventory.return_value = "[food 5, linemate 2]"
        
        result = self.inventory_manager.update_inventory()
        
        self.assertTrue(result)
        self.assertEqual(self.inventory_manager.inventory['food'], 5)
        self.assertEqual(self.inventory_manager.inventory['linemate'], 2)

    def test_update_inventory_connection_error(self):
        """Test de la mise à jour d'inventaire avec erreur de connexion."""
        self.protocol_mock.inventory.side_effect = ConnectionError("Connexion perdue")
        
        result = self.inventory_manager.update_inventory()
        
        self.assertFalse(result)
        self.logger_mock.error.assert_called()

    def test_update_inventory_invalid_response(self):
        """Test de la mise à jour d'inventaire avec réponse invalide."""
        self.protocol_mock.inventory.return_value = "invalid"
        
        result = self.inventory_manager.update_inventory()
        
        self.assertFalse(result)

    def test_update_inventory_empty_response(self):
        """Test de la mise à jour d'inventaire avec réponse vide."""
        self.protocol_mock.inventory.return_value = ""
        
        result = self.inventory_manager.update_inventory()
        
        self.assertFalse(result)

    def test_force_update_inventory_success(self):
        """Test de la mise à jour forcée d'inventaire avec succès."""
        self.protocol_mock.inventory.return_value = "[food 3, deraumere 1]"
        
        result = self.inventory_manager.force_update_inventory()
        
        self.assertTrue(result)
        self.assertEqual(self.inventory_manager.inventory['food'], 3)
        self.assertEqual(self.inventory_manager.inventory['deraumere'], 1)

    def test_force_update_inventory_connection_error(self):
        """Test de la mise à jour forcée d'inventaire avec erreur de connexion."""
        self.protocol_mock.inventory.side_effect = ConnectionError("Connexion perdue")
        
        result = self.inventory_manager.force_update_inventory()
        
        self.assertFalse(result)
        self.logger_mock.error.assert_called()

    def test_update_inventory_with_invalid_item_format(self):
        """Test de la mise à jour d'inventaire avec format d'item invalide."""
        self.protocol_mock.inventory.return_value = "[food 5, invalid_item, linemate 2]"
        
        result = self.inventory_manager.update_inventory()
        
        self.assertTrue(result)  # Continue malgré l'erreur
        self.assertEqual(self.inventory_manager.inventory['food'], 5)
        self.assertEqual(self.inventory_manager.inventory['linemate'], 2)

    def test_update_inventory_with_unknown_item(self):
        """Test de la mise à jour d'inventaire avec item inconnu."""
        self.protocol_mock.inventory.return_value = "[food 5, unknown_item 3, linemate 2]"
        
        result = self.inventory_manager.update_inventory()
        
        self.assertTrue(result)  # Continue malgré l'item inconnu
        self.assertEqual(self.inventory_manager.inventory['food'], 5)
        self.assertEqual(self.inventory_manager.inventory['linemate'], 2)

    def test_update_inventory_with_empty_items(self):
        """Test de la mise à jour d'inventaire avec items vides."""
        self.protocol_mock.inventory.return_value = "[food 5, , linemate 2]"
        
        result = self.inventory_manager.update_inventory()
        
        self.assertTrue(result)  # Ignore les items vides
        self.assertEqual(self.inventory_manager.inventory['food'], 5)
        self.assertEqual(self.inventory_manager.inventory['linemate'], 2)

if __name__ == '__main__':
    unittest.main() 