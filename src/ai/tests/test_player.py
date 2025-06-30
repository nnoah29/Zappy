 #!/usr/bin/env python3

import unittest
from unittest.mock import Mock, MagicMock
import logging
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.player import Player
from core.protocol import ZappyProtocol
from managers.inventory_manager import InventoryManager

class TestPlayer(unittest.TestCase):
    """Tests pour la classe Player."""
    
    def setUp(self):
        """Initialise les tests."""
        self.logger = logging.getLogger(__name__)
        self.protocol_mock = Mock(spec=ZappyProtocol)
        self.player = Player(
            id=1,
            team="test_team",
            x=5,
            y=5,
            protocol=self.protocol_mock,
            logger=self.logger
        )
    
    def test_player_initialization(self):
        """Test l'initialisation d'un joueur."""
        self.assertEqual(self.player.id, 1)
        self.assertEqual(self.player.team, "test_team")
        self.assertEqual(self.player.position, (5, 5))
        self.assertEqual(self.player.direction, 0)
        self.assertEqual(self.player.level, 1)
        self.assertIsInstance(self.player.inventory, InventoryManager)
    
    def test_x_property(self):
        """Test la propriété x."""
        self.assertEqual(self.player.x, 5)
        self.player.position = (10, 5)
        self.assertEqual(self.player.x, 10)
    
    def test_y_property(self):
        """Test la propriété y."""
        self.assertEqual(self.player.y, 5)
        self.player.position = (5, 10)
        self.assertEqual(self.player.y, 10)
    
    def test_get_position(self):
        """Test la récupération de la position."""
        position = self.player.get_position()
        self.assertEqual(position, (5, 5))
    
    def test_set_position(self):
        """Test la mise à jour de la position."""
        self.player.set_position(10, 15)
        self.assertEqual(self.player.position, (10, 15))
    
    def test_get_direction(self):
        """Test la récupération de la direction."""
        direction = self.player.get_direction()
        self.assertEqual(direction, 0)
    
    def test_set_direction(self):
        """Test la mise à jour de la direction."""
        self.player.set_direction(2)
        self.assertEqual(self.player.direction, 2)
        
        # Test avec une direction négative
        self.player.set_direction(-1)
        self.assertEqual(self.player.direction, 3)
        
        # Test avec une direction > 3
        self.player.set_direction(5)
        self.assertEqual(self.player.direction, 1)
    
    def test_get_level(self):
        """Test la récupération du niveau."""
        level = self.player.get_level()
        self.assertEqual(level, 1)
    
    def test_set_level(self):
        """Test la mise à jour du niveau."""
        self.player.set_level(3)
        self.assertEqual(self.player.level, 3)
    
    def test_get_inventory(self):
        """Test la récupération de l'inventaire."""
        inventory = self.player.get_inventory()
        self.assertIsInstance(inventory, InventoryManager)
    
    def test_set_inventory(self):
        """Test la mise à jour de l'inventaire."""
        new_inventory = {'food': 5, 'linemate': 2}
        self.player.set_inventory(new_inventory)
        self.assertEqual(self.player.inventory, new_inventory)
    
    def test_get_resource_count(self):
        """Test la récupération du nombre d'une ressource."""
        # Simuler un inventaire
        self.player.inventory = {'food': 5, 'linemate': 2}
        self.assertEqual(self.player.get_resource_count('food'), 5)
        self.assertEqual(self.player.get_resource_count('linemate'), 2)
        self.assertEqual(self.player.get_resource_count('nonexistent'), 0)
    
    def test_add_resource(self):
        """Test l'ajout de ressources."""
        self.player.inventory = {'food': 3}
        self.player.add_resource('food', 2)
        self.assertEqual(self.player.inventory['food'], 5)
        
        # Test ajout d'une nouvelle ressource
        self.player.add_resource('linemate', 1)
        self.assertEqual(self.player.inventory['linemate'], 1)
    
    def test_remove_resource(self):
        """Test le retrait de ressources."""
        self.player.inventory = {'food': 5, 'linemate': 2}
        
        # Test retrait réussi
        result = self.player.remove_resource('food', 3)
        self.assertTrue(result)
        self.assertEqual(self.player.inventory['food'], 2)
        
        # Test retrait impossible (pas assez de ressources)
        result = self.player.remove_resource('linemate', 5)
        self.assertFalse(result)
        self.assertEqual(self.player.inventory['linemate'], 2)
        
        # Test retrait de ressource inexistante
        result = self.player.remove_resource('nonexistent', 1)
        self.assertFalse(result)
    
    def test_move_forward_north(self):
        """Test le mouvement vers le nord."""
        self.player.direction = 0
        self.player.move_forward(10, 10)
        self.assertEqual(self.player.position, (5, 4))
    
    def test_move_forward_south(self):
        """Test le mouvement vers le sud."""
        self.player.direction = 2
        self.player.move_forward(10, 10)
        self.assertEqual(self.player.position, (5, 6))
    
    def test_move_forward_east(self):
        """Test le mouvement vers l'est."""
        self.player.direction = 1
        self.player.move_forward(10, 10)
        self.assertEqual(self.player.position, (6, 5))
    
    def test_move_forward_west(self):
        """Test le mouvement vers l'ouest."""
        self.player.direction = 3
        self.player.move_forward(10, 10)
        self.assertEqual(self.player.position, (4, 5))
    
    def test_move_forward_wrapping(self):
        """Test le wrapping des coordonnées."""
        # Test wrapping nord
        self.player.position = (5, 0)
        self.player.direction = 0
        self.player.move_forward(10, 10)
        self.assertEqual(self.player.position, (5, 9))
        
        # Test wrapping sud
        self.player.position = (5, 9)
        self.player.direction = 2
        self.player.move_forward(10, 10)
        self.assertEqual(self.player.position, (5, 0))
        
        # Test wrapping est
        self.player.position = (9, 5)
        self.player.direction = 1
        self.player.move_forward(10, 10)
        self.assertEqual(self.player.position, (0, 5))
        
        # Test wrapping ouest
        self.player.position = (0, 5)
        self.player.direction = 3
        self.player.move_forward(10, 10)
        self.assertEqual(self.player.position, (9, 5))

if __name__ == '__main__':
    unittest.main()