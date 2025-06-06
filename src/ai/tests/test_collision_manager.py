import unittest
from unittest.mock import Mock, patch
from collision_manager import CollisionManager
from protocol import ZappyProtocol
from vision import Vision

class TestCollisionManager(unittest.TestCase):
    def setUp(self):
        """Initialise les mocks et le gestionnaire de collisions."""
        self.protocol_mock = Mock(spec=ZappyProtocol)
        self.vision_mock = Mock(spec=Vision)
        self.collision_manager = CollisionManager(self.protocol_mock, self.vision_mock)

    def test_initial_state(self):
        """Teste l'état initial du gestionnaire de collisions."""
        self.assertEqual(self.collision_manager.stuck_count, 0)
        self.assertEqual(len(self.collision_manager.last_positions), 0)
        self.assertEqual(self.collision_manager.max_stuck_count, 3)
        self.assertEqual(self.collision_manager.position_history_size, 5)

    def test_check_collision_no_collision(self):
        """Teste la détection de collision quand il n'y en a pas."""
        self.vision_mock.get_case_position.return_value = (0, 0)
        self.assertFalse(self.collision_manager.check_collision())
        self.assertEqual(self.collision_manager.stuck_count, 0)

    def test_check_collision_detection(self):
        """Teste la détection d'une collision."""
        # Simule le joueur bloqué au même endroit
        self.vision_mock.get_case_position.return_value = (0, 0)
        
        # Vérifie 3 fois la même position
        for _ in range(3):
            self.collision_manager.check_collision()
            
        # La quatrième vérification devrait détecter la collision
        self.assertTrue(self.collision_manager.check_collision())
        self.assertEqual(self.collision_manager.stuck_count, 1)

    def test_handle_collision_normal(self):
        """Teste la gestion d'une collision normale."""
        self.collision_manager.stuck_count = 1
        self.collision_manager.handle_collision()
        
        # Vérifie que le protocole a été appelé correctement
        self.protocol_mock.right.assert_called_once()
        self.protocol_mock.forward.assert_called_once()

    def test_handle_collision_severe(self):
        """Teste la gestion d'une collision sévère."""
        self.collision_manager.stuck_count = 4
        self.collision_manager.handle_collision()
        
        # Vérifie que le protocole a été appelé correctement
        self.assertEqual(self.protocol_mock.right.call_count, 2)
        self.assertEqual(self.collision_manager.stuck_count, 0)

    def test_reset(self):
        """Teste la réinitialisation du gestionnaire."""
        # Simule un état bloqué
        self.collision_manager.stuck_count = 5
        self.collision_manager.last_positions = [(0, 0), (0, 0), (0, 0)]
        
        self.collision_manager.reset()
        
        self.assertEqual(self.collision_manager.stuck_count, 0)
        self.assertEqual(len(self.collision_manager.last_positions), 0)

    def test_is_severely_stuck(self):
        """Teste la détection d'un blocage sévère."""
        self.collision_manager.stuck_count = 4
        self.assertTrue(self.collision_manager.is_severely_stuck())
        
        self.collision_manager.stuck_count = 3
        self.assertFalse(self.collision_manager.is_severely_stuck())

if __name__ == '__main__':
    unittest.main() 