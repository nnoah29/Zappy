import unittest
from unittest.mock import Mock, patch, MagicMock
import socket
import sys
import os

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client import ZappyClient

class TestZappyClient(unittest.TestCase):
    def setUp(self):
        """Initialise le client pour les tests."""
        self.client = ZappyClient("localhost", 4242, "team1")

    @patch('socket.socket')
    def test_connect(self, mock_socket):
        """Test de la connexion au serveur."""
        # Configuration du mock
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.side_effect = [
            b"WELCOME\n",
            b"1\n",
            b"10 10\n"
        ]
        mock_socket_instance.fileno.return_value = 1

        # Test de la connexion
        self.client.connect()
        
        # Vérifie que le socket a été configuré correctement
        mock_socket_instance.connect.assert_called_once_with(("localhost", 4242))
        mock_socket_instance.send.assert_called_once_with(b"team1\n")

    @patch('socket.socket')
    def test_connect_invalid_welcome(self, mock_socket):
        """Test de la connexion avec un message de bienvenue invalide."""
        # Configuration du mock
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.return_value = b"INVALID\n"
        mock_socket_instance.fileno.return_value = 1

        # Test de la connexion
        with self.assertRaises(Exception) as context:
            self.client.connect()
        
        self.assertIn("Message de bienvenue invalide", str(context.exception))

    def test_send_receive(self):
        """Test des méthodes d'envoi et de réception."""
        with patch.object(self.client, 'socket') as mock_socket:
            # Configuration du mock
            mock_socket.fileno.return_value = 1
            mock_socket.recv.return_value = b"response"
            
            # Test d'envoi
            message = "test message"
            self.client._send(message)
            mock_socket.send.assert_called_once_with(message.encode())
            
            # Test de réception
            response = self.client._receive()
            self.assertEqual(response, "response")

    def test_send_error(self):
        """Test de la gestion des erreurs d'envoi."""
        with patch.object(self.client, 'socket') as mock_socket:
            mock_socket.fileno.return_value = 1
            mock_socket.send.side_effect = socket.error("Erreur de connexion")
            
            with self.assertRaises(socket.error) as context:
                self.client._send("test")
            
            self.assertIn("Erreur d'envoi", str(context.exception))

    def test_receive_error(self):
        """Test de la gestion des erreurs de réception."""
        with patch.object(self.client, 'socket') as mock_socket:
            mock_socket.fileno.return_value = 1
            mock_socket.recv.side_effect = socket.error("Erreur de connexion")
            
            with self.assertRaises(socket.error) as context:
                self.client._receive()
            
            self.assertIn("Erreur de réception", str(context.exception))

if __name__ == '__main__':
    unittest.main() 