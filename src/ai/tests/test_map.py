#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, MagicMock
import logging
import sys
import os
import time

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.map import Map, Tile

class TestTile(unittest.TestCase):
    """Tests pour la classe Tile."""
    
    def setUp(self):
        """Initialise les tests."""
        self.tile = Tile(5, 10)
    
    def test_tile_initialization(self):
        """Test l'initialisation d'une tuile."""
        self.assertEqual(self.tile.x, 5)
        self.assertEqual(self.tile.y, 10)
        self.assertEqual(self.tile.resources, {
            "food": 0,
            "linemate": 0,
            "deraumere": 0,
            "sibur": 0,
            "mendiane": 0,
            "phiras": 0,
            "thystame": 0,
        })
        self.assertEqual(self.tile.players, [])
        self.assertIsNone(self.tile.last_updated)
        self.assertFalse(self.tile.is_explored)

class TestMap(unittest.TestCase):
    """Tests pour la classe Map."""
    
    def setUp(self):
        """Initialise les tests."""
        self.logger = logging.getLogger(__name__)
        self.map = Map(10, 8)
    
    def test_map_initialization(self):
        """Test l'initialisation de la carte."""
        self.assertEqual(self.map.width, 10)
        self.assertEqual(self.map.height, 8)
        self.assertEqual(len(self.map.grid), 8)
        self.assertEqual(len(self.map.grid[0]), 10)
        
        # Vérifier que toutes les tuiles sont initialisées
        for y in range(8):
            for x in range(10):
                tile = self.map.grid[y][x]
                self.assertIsInstance(tile, Tile)
                self.assertEqual(tile.x, x)
                self.assertEqual(tile.y, y)
    
    def test_get_tile(self):
        """Test la récupération d'une tuile."""
        tile = self.map.get_tile(5, 3)
        self.assertIsInstance(tile, Tile)
        self.assertEqual(tile.x, 5)
        self.assertEqual(tile.y, 3)
    
    def test_get_tile_wrapping(self):
        """Test la récupération d'une tuile avec wrapping."""
        # Test wrapping X
        tile = self.map.get_tile(15, 3)
        self.assertEqual(tile.x, 5)  # 15 % 10 = 5
        
        # Test wrapping Y
        tile = self.map.get_tile(5, 11)
        self.assertEqual(tile.y, 3)  # 11 % 8 = 3
        
        # Test wrapping négatif
        tile = self.map.get_tile(-3, -2)
        self.assertEqual(tile.x, 7)  # -3 % 10 = 7
        self.assertEqual(tile.y, 6)  # -2 % 8 = 6
    
    def test_is_explored(self):
        """Test la vérification d'exploration d'une tuile."""
        # Tuile non explorée par défaut
        self.assertFalse(self.map.is_explored(5, 3))
        
        # Marquer comme explorée
        self.map.grid[3][5].is_explored = True
        self.assertTrue(self.map.is_explored(5, 3))
    
    def test_is_explored_invalid_coordinates(self):
        """Test la vérification d'exploration avec coordonnées invalides."""
        # Test avec des coordonnées très grandes
        self.assertFalse(self.map.is_explored(1000, 1000))
    
    def test_get_tile_content(self):
        """Test la récupération du contenu d'une tuile."""
        # Préparer une tuile avec du contenu
        tile = self.map.grid[3][5]
        tile.resources['food'] = 3
        tile.resources['linemate'] = 1
        tile.players = ['player1', 'player2']
        tile.is_explored = True
        
        content = self.map.get_tile_content(5, 3)
        
        self.assertEqual(content['resources']['food'], 3)
        self.assertEqual(content['resources']['linemate'], 1)
        self.assertEqual(content['players'], ['player1', 'player2'])
        self.assertTrue(content['is_explored'])
    
    def test_update_tile(self):
        """Test la mise à jour du contenu d'une tuile."""
        content = ['food', 'food', 'linemate', 'player']
        
        self.map.update_tile(5, 3, content)
        
        tile = self.map.grid[3][5]
        self.assertEqual(tile.resources['food'], 2)
        self.assertEqual(tile.resources['linemate'], 1)
        self.assertTrue(tile.is_explored)
        self.assertIsNotNone(tile.last_updated)
    
    def test_update_tile_clears_previous_content(self):
        """Test que la mise à jour efface le contenu précédent."""
        # Ajouter du contenu initial
        tile = self.map.grid[3][5]
        tile.resources['food'] = 5
        tile.resources['deraumere'] = 2
        
        # Mettre à jour avec nouveau contenu
        content = ['food', 'linemate']
        self.map.update_tile(5, 3, content)
        
        # Vérifier que l'ancien contenu a été effacé
        self.assertEqual(tile.resources['food'], 1)
        self.assertEqual(tile.resources['deraumere'], 0)
        self.assertEqual(tile.resources['linemate'], 1)
    
    def test_mark_as_explored(self):
        """Test le marquage d'une tuile comme explorée."""
        tile = self.map.grid[3][5]
        self.assertFalse(tile.is_explored)
        
        self.map.mark_as_explored(5, 3)
        
        self.assertTrue(tile.is_explored)
        self.assertIsNotNone(tile.last_updated)
    
    def test_get_unexplored_tiles(self):
        """Test la récupération des tuiles non explorées."""
        # Marquer quelques tuiles comme explorées
        self.map.grid[0][0].is_explored = True
        self.map.grid[1][1].is_explored = True
        
        unexplored = self.map.get_unexplored_tiles()
        
        # Devrait y avoir 78 tuiles non explorées (10*8 - 2)
        self.assertEqual(len(unexplored), 78)
        
        # Vérifier que les tuiles explorées ne sont pas dans la liste
        self.assertNotIn((0, 0), unexplored)
        self.assertNotIn((1, 1), unexplored)
        
        # Vérifier que des tuiles non explorées sont dans la liste
        self.assertIn((2, 2), unexplored)
        self.assertIn((5, 3), unexplored)
    
    def test_get_tiles_with_resource(self):
        """Test la récupération des tuiles contenant une ressource."""
        # Ajouter des ressources à quelques tuiles
        self.map.grid[0][0].resources['food'] = 3
        self.map.grid[1][1].resources['food'] = 1
        self.map.grid[2][2].resources['linemate'] = 2
        
        food_tiles = self.map.get_tiles_with_resource('food')
        linemate_tiles = self.map.get_tiles_with_resource('linemate')
        empty_tiles = self.map.get_tiles_with_resource('deraumere')
        
        self.assertEqual(len(food_tiles), 2)
        self.assertIn((0, 0), food_tiles)
        self.assertIn((1, 1), food_tiles)
        
        self.assertEqual(len(linemate_tiles), 1)
        self.assertIn((2, 2), linemate_tiles)
        
        self.assertEqual(len(empty_tiles), 0)
    
    def test_get_tiles_with_resource_nonexistent(self):
        """Test la récupération des tuiles avec une ressource inexistante."""
        tiles = self.map.get_tiles_with_resource('nonexistent_resource')
        self.assertEqual(len(tiles), 0)
    
    def test_map_edge_cases(self):
        """Test les cas limites de la carte."""
        # Carte de taille 1x1
        small_map = Map(1, 1)
        self.assertEqual(small_map.width, 1)
        self.assertEqual(small_map.height, 1)
        
        tile = small_map.get_tile(0, 0)
        self.assertIsInstance(tile, Tile)
        
        # Test wrapping sur carte 1x1
        tile = small_map.get_tile(5, 5)
        self.assertEqual(tile.x, 0)
        self.assertEqual(tile.y, 0)

if __name__ == '__main__':
    unittest.main() 