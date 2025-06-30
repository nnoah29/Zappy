#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch, MagicMock
import logging
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from managers.reproduction_manager import ReproductionManager
from core.protocol import ZappyProtocol

class TestReproductionManager(unittest.TestCase):
    """Tests pour le ReproductionManager."""

    def setUp(self):
        """Initialise les mocks et le ReproductionManager pour chaque test."""
        self.protocol_mock = Mock(spec=ZappyProtocol)
        self.logger_mock = Mock(spec=logging.Logger)
        
        self.reproduction_manager = ReproductionManager(
            self.protocol_mock,
            self.logger_mock
        )

    def test_initialization(self):
        """Test de l'initialisation du ReproductionManager."""
        self.assertIsNotNone(self.reproduction_manager)
        self.assertEqual(self.reproduction_manager.cooldown, 42)
        self.assertEqual(self.reproduction_manager.last_fork_time, 0)

    def test_can_fork_true(self):
        """Test de la vérification si le fork est possible (vrai)."""
        # Simuler un temps suffisant depuis le dernier fork
        self.reproduction_manager.last_fork_time = 0
        
        result = self.reproduction_manager.can_fork()
        
        self.assertTrue(result)

    def test_can_fork_false(self):
        """Test de la vérification si le fork est possible (faux)."""
        # Simuler un fork récent
        import time
        self.reproduction_manager.last_fork_time = time.time()
        
        result = self.reproduction_manager.can_fork()
        
        self.assertFalse(result)

    def test_reproduce_success(self):
        """Test de la reproduction réussie."""
        self.protocol_mock.connect_nbr.return_value = 5
        self.protocol_mock.fork.return_value = True
        
        result = self.reproduction_manager.reproduce()
        
        self.assertTrue(result)
        self.protocol_mock.connect_nbr.assert_called_once()
        self.protocol_mock.fork.assert_called_once()

    def test_reproduce_no_slots(self):
        """Test de la reproduction sans slots disponibles."""
        self.protocol_mock.connect_nbr.return_value = 0
        
        result = self.reproduction_manager.reproduce()
        
        self.assertFalse(result)
        self.protocol_mock.connect_nbr.assert_called_once()
        self.protocol_mock.fork.assert_not_called()

    def test_reproduce_fork_failure(self):
        """Test de la reproduction avec échec du fork."""
        self.protocol_mock.connect_nbr.return_value = 5
        self.protocol_mock.fork.return_value = False
        
        result = self.reproduction_manager.reproduce()
        
        self.assertFalse(result)
        self.protocol_mock.fork.assert_called_once()

    def test_reproduce_cooldown_active(self):
        """Test de la reproduction avec cooldown actif."""
        import time
        self.reproduction_manager.last_fork_time = time.time()
        
        result = self.reproduction_manager.reproduce()
        
        self.assertFalse(result)
        self.protocol_mock.connect_nbr.assert_not_called()
        self.protocol_mock.fork.assert_not_called()

    def test_reproduce_exception(self):
        """Test de la reproduction avec exception."""
        self.protocol_mock.connect_nbr.side_effect = Exception("Erreur générale")
        
        result = self.reproduction_manager.reproduce()
        
        self.assertFalse(result)
        self.logger_mock.error.assert_called()

    def test_reproduce_connection_error(self):
        """Test de la reproduction avec erreur de connexion."""
        self.protocol_mock.connect_nbr.side_effect = ConnectionError("Connexion perdue")
        
        result = self.reproduction_manager.reproduce()
        
        self.assertFalse(result)
        self.logger_mock.error.assert_called()

    def test_reproduce_multiple_attempts(self):
        """Test de plusieurs tentatives de reproduction."""
        # Première tentative réussie
        self.protocol_mock.connect_nbr.return_value = 5
        self.protocol_mock.fork.return_value = True
        
        result1 = self.reproduction_manager.reproduce()
        
        self.assertTrue(result1)
        
        # Deuxième tentative avec cooldown
        result2 = self.reproduction_manager.reproduce()
        
        self.assertFalse(result2)

    def test_reproduce_with_conditions(self):
        """Test de la reproduction avec conditions spécifiques."""
        # Simuler une reproduction réussie
        self.protocol_mock.connect_nbr.return_value = 3
        self.protocol_mock.fork.return_value = True
        
        result = self.reproduction_manager.reproduce()
        
        self.assertTrue(result)

    def test_reproduce_logging(self):
        """Test du logging lors de la reproduction."""
        # Configurer un mock pour le logger
        logger_mock = Mock(spec=logging.Logger)
        reproduction_manager = ReproductionManager(self.protocol_mock, logger_mock)
        
        # Reproduction réussie
        self.protocol_mock.connect_nbr.return_value = 5
        self.protocol_mock.fork.return_value = True
        
        result = reproduction_manager.reproduce()
        
        self.assertTrue(result)
        logger_mock.info.assert_called()

    def test_reproduce_protocol_integration(self):
        """Test de l'intégration avec le protocole."""
        # Vérifier que le protocole est correctement utilisé
        self.protocol_mock.connect_nbr.return_value = 5
        self.protocol_mock.fork.return_value = True
        
        self.reproduction_manager.reproduce()
        
        self.protocol_mock.connect_nbr.assert_called_once()
        self.protocol_mock.fork.assert_called_once()

    def test_reproduce_return_value_consistency(self):
        """Test de la cohérence des valeurs de retour."""
        # Test avec True
        self.protocol_mock.connect_nbr.return_value = 5
        self.protocol_mock.fork.return_value = True
        result = self.reproduction_manager.reproduce()
        self.assertTrue(result)
        
        # Test avec False
        self.protocol_mock.fork.return_value = False
        result = self.reproduction_manager.reproduce()
        self.assertFalse(result)

    def test_reproduce_method_signature(self):
        """Test de la signature de la méthode reproduce."""
        # Vérifier que la méthode existe et peut être appelée sans paramètres
        self.assertTrue(hasattr(self.reproduction_manager, 'reproduce'))
        
        # Vérifier que la méthode retourne un booléen
        self.protocol_mock.connect_nbr.return_value = 5
        self.protocol_mock.fork.return_value = True
        result = self.reproduction_manager.reproduce()
        self.assertIsInstance(result, bool)

    def test_reproduction_manager_methods(self):
        """Test des méthodes du ReproductionManager."""
        # Vérifier que les méthodes existent
        self.assertTrue(hasattr(self.reproduction_manager, 'can_fork'))
        self.assertTrue(hasattr(self.reproduction_manager, 'reproduce'))
        
        # Vérifier que les méthodes retournent des booléens
        self.assertIsInstance(self.reproduction_manager.can_fork(), bool)

    def test_should_fork_true(self):
        """Test de la décision de reproduction (vrai)."""
        # Simuler des conditions favorables pour la reproduction
        self.protocol_mock.connect_nbr.return_value = 5
        self.protocol_mock.fork.return_value = True
        
        result = self.reproduction_manager.reproduce()
        
        self.assertTrue(result)

    def test_should_fork_false(self):
        """Test de la décision de reproduction (faux)."""
        # Simuler des conditions défavorables pour la reproduction
        self.protocol_mock.connect_nbr.return_value = 0
        
        result = self.reproduction_manager.reproduce()
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main() 