#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, MagicMock, patch
import logging
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.protocol import ZappyProtocol
from core.client import ZappyClient

class TestZappyProtocol(unittest.TestCase):
    """Tests unitaires pour ZappyProtocol."""

    def setUp(self):
        """Initialise les mocks et le protocole pour chaque test."""
        self.client_mock = Mock(spec=ZappyClient)
        self.protocol = ZappyProtocol(self.client_mock)

    def test_initialization(self):
        """Test de l'initialisation du protocole."""
        self.assertIsNotNone(self.protocol)
        self.assertEqual(self.protocol.client, self.client_mock)
        self.assertIsNone(self.protocol.last_response)
        self.assertIsNone(self.protocol.last_error)

    def test_check_connection_success(self):
        """Test de la vérification de connexion réussie."""
        self.client_mock.is_connected.return_value = True
        
        # Ne devrait pas lever d'exception
        self.protocol._check_connection()

    def test_check_connection_failure(self):
        """Test de la vérification de connexion échouée."""
        self.client_mock.is_connected.return_value = False
        
        with self.assertRaises(ConnectionError):
            self.protocol._check_connection()

    def test_handle_response_ok(self):
        """Test de la gestion de réponse 'ok'."""
        result = self.protocol._handle_response("ok")
        
        self.assertTrue(result)
        self.assertEqual(self.protocol.last_response, "ok")
        self.assertIsNone(self.protocol.last_error)

    def test_handle_response_ko(self):
        """Test de la gestion de réponse 'ko'."""
        result = self.protocol._handle_response("ko")
        
        self.assertFalse(result)
        self.assertEqual(self.protocol.last_response, "ko")
        self.assertEqual(self.protocol.last_error, "Commande refusée par le serveur")

    def test_handle_response_invalid(self):
        """Test de la gestion de réponse invalide."""
        with self.assertRaises(ValueError):
            self.protocol._handle_response("invalid")

    def test_forward_success(self):
        """Test de l'avancement réussi."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "ok"
        
        result = self.protocol.forward()
        
        self.assertTrue(result)
        self.client_mock._send.assert_called_once_with("Forward\n")
        self.client_mock._receive.assert_called_once()

    def test_forward_failure(self):
        """Test de l'avancement en échec."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "ko"
        
        result = self.protocol.forward()
        
        self.assertFalse(result)

    def test_forward_connection_error(self):
        """Test de l'avancement avec erreur de connexion."""
        self.client_mock.is_connected.return_value = False
        
        with self.assertRaises(ConnectionError):
            self.protocol.forward()

    def test_right_success(self):
        """Test de la rotation à droite réussie."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "ok"
        
        result = self.protocol.right()
        
        self.assertTrue(result)
        self.client_mock._send.assert_called_once_with("Right\n")

    def test_left_success(self):
        """Test de la rotation à gauche réussie."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "ok"
        
        result = self.protocol.left()
        
        self.assertTrue(result)
        self.client_mock._send.assert_called_once_with("Left\n")

    def test_look_success(self):
        """Test de la vision réussie."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "[player, food]"
        
        result = self.protocol.look()
        
        self.assertEqual(result, "[player, food]")
        self.assertEqual(self.protocol.last_response, "[player, food]")
        self.client_mock._send.assert_called_once_with("Look\n")

    def test_inventory_success(self):
        """Test de la consultation d'inventaire réussie."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "[food 5, linemate 2]"
        
        result = self.protocol.inventory()
        
        self.assertEqual(result, "[food 5, linemate 2]")
        self.assertEqual(self.protocol.last_response, "[food 5, linemate 2]")
        self.client_mock._send.assert_called_once_with("Inventory\n")

    def test_broadcast_success(self):
        """Test de l'envoi de message réussi."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "ok"
        
        result = self.protocol.broadcast("test message")
        
        self.assertTrue(result)
        self.client_mock._send.assert_called_once_with("Broadcast test message\n")

    def test_connect_nbr_success(self):
        """Test de la demande de places disponibles réussie."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "5"
        
        result = self.protocol.connect_nbr()
        
        self.assertEqual(result, 5)
        self.assertEqual(self.protocol.last_response, "5")
        self.client_mock._send.assert_called_once_with("Connect_nbr\n")

    def test_connect_nbr_invalid_response(self):
        """Test de la demande de places avec réponse invalide."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "invalid"
        
        with self.assertRaises(ValueError):
            self.protocol.connect_nbr()

    def test_fork_success(self):
        """Test de la ponte réussie."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "ok"
        
        result = self.protocol.fork()
        
        self.assertTrue(result)
        self.client_mock._send.assert_called_once_with("Fork\n")

    def test_eject_success(self):
        """Test de l'éjection réussie."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "ok"
        
        result = self.protocol.eject()
        
        self.assertTrue(result)
        self.client_mock._send.assert_called_once_with("Eject\n")

    def test_take_success(self):
        """Test de la prise d'objet réussie."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "ok"
        
        result = self.protocol.take("food")
        
        self.assertTrue(result)
        self.client_mock._send.assert_called_once_with("Take food\n")

    def test_set_success(self):
        """Test du dépôt d'objet réussi."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "ok"
        
        result = self.protocol.set("food")
        
        self.assertTrue(result)
        self.client_mock._send.assert_called_once_with("Set food\n")

    def test_incantation_success(self):
        """Test de l'incantation réussie."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "Elevation underway"
        
        result = self.protocol.incantation()
        
        self.assertTrue(result)
        self.client_mock._send.assert_called_once_with("Incantation\n")

    def test_incantation_failure(self):
        """Test de l'incantation en échec."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._receive.return_value = "ko"
        
        result = self.protocol.incantation()
        
        self.assertFalse(result)

    def test_parse_look_response(self):
        """Test du parsing de réponse de vision."""
        response = "[player, food, linemate]"
        
        result = self.protocol.parse_look_response(response)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_parse_inventory_response(self):
        """Test du parsing de réponse d'inventaire."""
        response = "[food 5, linemate 2, deraumere 1]"
        
        result = self.protocol.parse_inventory_response(response)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('food'), 5)

    def test_forward_exception(self):
        """Test de l'avancement avec exception."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._send.side_effect = Exception("Test error")
        
        with self.assertRaises(Exception):
            self.protocol.forward()
        
        self.assertIn("Erreur lors du déplacement", self.protocol.last_error)

    def test_look_exception(self):
        """Test de la vision avec exception."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._send.side_effect = Exception("Test error")
        
        with self.assertRaises(Exception):
            self.protocol.look()
        
        self.assertIn("Erreur lors de la vision", self.protocol.last_error)

    def test_broadcast_exception(self):
        """Test du broadcast avec exception."""
        self.client_mock.is_connected.return_value = True
        self.client_mock._send.side_effect = Exception("Test error")
        
        with self.assertRaises(Exception):
            self.protocol.broadcast("test")
        
        self.assertIn("Erreur lors de l'envoi du message", self.protocol.last_error)

if __name__ == '__main__':
    unittest.main() 