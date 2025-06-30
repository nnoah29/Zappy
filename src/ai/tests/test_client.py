#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
import sys
import os
import socket

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.client import ZappyClient

class TestZappyClient(unittest.TestCase):
    """Tests unitaires pour ZappyClient."""

    def setUp(self):
        """Initialise le client pour chaque test."""
        self.client = ZappyClient("localhost", 4242, "test_team")

    def test_initialization(self):
        """Test de l'initialisation du client."""
        self.assertEqual(self.client.hostname, "localhost")
        self.assertEqual(self.client.port, 4242)
        self.assertEqual(self.client.team_name, "test_team")
        self.assertIsNone(self.client.socket)
        self.assertFalse(self.client.server_disconnected)

    @patch('socket.socket')
    def test_connect_success(self, mock_socket):
        """Test de la connexion réussie."""
        mock_socket_instance = Mock()
        mock_socket.return_value = mock_socket_instance
        
        mock_socket_instance.recv.side_effect = [
            b"WELCOME\n",
            b"1\n10 10\n"
        ]
        
        self.client.connect()
        
        self.assertIsNotNone(self.client.socket)
        self.assertEqual(self.client.client_num, 1)
        self.assertEqual(self.client.map_size, (10, 10))
        mock_socket_instance.connect.assert_called_once_with(("localhost", 4242))

    @patch('socket.socket')
    def test_connect_invalid_welcome(self, mock_socket):
        """Test de la connexion avec message de bienvenue invalide."""
        mock_socket_instance = Mock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.return_value = b"INVALID\n"
        
        with self.assertRaises(Exception):
            self.client.connect()
        
        mock_socket_instance.close.assert_called_once()

    @patch('socket.socket')
    def test_connect_invalid_client_num(self, mock_socket):
        """Test de la connexion avec numéro de client invalide."""
        mock_socket_instance = Mock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.side_effect = [
            b"WELCOME\n",
            b"invalid\n"
        ]
        
        with self.assertRaises(Exception):
            self.client.connect()
        
        mock_socket_instance.close.assert_called_once()

    @patch('socket.socket')
    def test_connect_invalid_map_size(self, mock_socket):
        """Test de la connexion avec dimensions de carte invalides."""
        mock_socket_instance = Mock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.side_effect = [
            b"WELCOME\n",
            b"1\ninvalid\n"
        ]
        
        with self.assertRaises(Exception):
            self.client.connect()
        
        mock_socket_instance.close.assert_called_once()

    def test_is_connected_true(self):
        """Test de la vérification de connexion (connecté)."""
        self.client.socket = Mock()
        self.client.socket.send.return_value = 0
        
        result = self.client.is_connected()
        
        self.assertTrue(result)

    def test_is_connected_false_no_socket(self):
        """Test de la vérification de connexion (pas de socket)."""
        self.client.socket = None
        
        result = self.client.is_connected()
        
        self.assertFalse(result)

    def test_is_connected_false_server_disconnected(self):
        """Test de la vérification de connexion (serveur déconnecté)."""
        self.client.server_disconnected = True
        
        result = self.client.is_connected()
        
        self.assertFalse(result)

    def test_is_connected_false_socket_error(self):
        """Test de la vérification de connexion (erreur de socket)."""
        self.client.socket = Mock()
        self.client.socket.send.side_effect = socket.error("Connection error")
        
        result = self.client.is_connected()
        
        self.assertFalse(result)
        self.assertTrue(self.client.server_disconnected)

    def test_get_timeout_forward(self):
        """Test de la récupération du timeout pour Forward."""
        result = self.client._get_timeout("Forward")
        
        self.assertEqual(result, 7.0)

    def test_get_timeout_inventory(self):
        """Test de la récupération du timeout pour Inventory."""
        result = self.client._get_timeout("Inventory")
        
        self.assertEqual(result, 1.0)

    def test_get_timeout_unknown(self):
        """Test de la récupération du timeout pour une commande inconnue."""
        result = self.client._get_timeout("Unknown")
        
        self.assertEqual(result, 7.0)

    def test_send_success(self):
        """Test de l'envoi réussi."""
        self.client.socket = Mock()
        self.client.socket.send.return_value = 10
        
        self.client._send("test message")
        
        self.client.socket.send.assert_called_once_with(b"test message")

    def test_send_no_socket(self):
        """Test de l'envoi sans socket."""
        self.client.socket = None
        
        with self.assertRaises(ConnectionError):
            self.client._send("test message")

    def test_send_server_disconnected(self):
        """Test de l'envoi avec serveur déconnecté."""
        self.client.server_disconnected = True
        
        with self.assertRaises(ConnectionError):
            self.client._send("test message")

    def test_send_socket_error(self):
        """Test de l'envoi avec erreur de socket."""
        self.client.socket = Mock()
        self.client.socket.send.side_effect = socket.error("Send error")
        
        with self.assertRaises(ConnectionError):
            self.client._send("test message")
        
        self.assertTrue(self.client.server_disconnected)

    def test_send_timeout(self):
        """Test de l'envoi avec timeout."""
        self.client.socket = Mock()
        self.client.socket.send.side_effect = socket.timeout("Timeout")
        
        with self.assertRaises(TimeoutError):
            self.client._send("Forward")

    def test_receive_success(self):
        """Test de la réception réussie."""
        self.client.socket = Mock()
        self.client.socket.recv.return_value = b"test response\n"
        
        result = self.client._receive()
        
        self.assertEqual(result, "test response")

    def test_receive_no_socket(self):
        """Test de la réception sans socket."""
        self.client.socket = None
        
        with self.assertRaises(Exception):
            self.client._receive()

    def test_receive_empty_data(self):
        """Test de la réception de données vides."""
        self.client.socket = Mock()
        self.client.socket.recv.return_value = b""
        
        with self.assertRaises(ConnectionError):
            self.client._receive()
        
        self.assertTrue(self.client.server_disconnected)

    def test_receive_dead_message(self):
        """Test de la réception du message 'dead'."""
        self.client.socket = Mock()
        self.client.socket.recv.return_value = b"dead\n"
        
        with self.assertRaises(ConnectionError):
            self.client._receive()
        
        self.assertTrue(self.client.server_disconnected)

    def test_receive_socket_error(self):
        """Test de la réception avec erreur de socket."""
        self.client.socket = Mock()
        self.client.socket.recv.side_effect = socket.error("Receive error")
        
        with self.assertRaises(ConnectionError):
            self.client._receive()
        
        self.assertTrue(self.client.server_disconnected)

    def test_receive_timeout(self):
        """Test de la réception avec timeout."""
        self.client.socket = Mock()
        self.client.socket.recv.side_effect = socket.timeout("Timeout")
        
        with self.assertRaises(socket.timeout):
            self.client._receive()

    def test_run_failure(self):
        """Test de l'exécution en échec."""
        self.client.ai = Mock()
        self.client.ai.run.return_value = False
        
        result = self.client.run()
        
        self.assertFalse(result)

    def test_close_no_socket(self):
        """Test de la fermeture sans socket."""
        self.client.socket = None
        
        self.client.close()

    def test_check_for_messages(self):
        """Test de la vérification de messages."""
        self.client.socket = Mock()
        self.client.socket.recv.return_value = b"test message\n"
        
        result = self.client.check_for_messages()
        
        self.assertEqual(result, "test message")

    def test_check_for_messages_no_data(self):
        """Test de la vérification de messages sans données."""
        self.client.socket = Mock()
        self.client.socket.recv.return_value = b""
        
        result = self.client.check_for_messages()
        
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main() 