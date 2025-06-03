import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from protocol import ZappyProtocol

class TestZappyProtocol(unittest.TestCase):
    def setUp(self):
        """Configuration initiale pour chaque test."""
        self.client = MagicMock()
        self.protocol = ZappyProtocol(self.client)

    def test_forward(self):
        """Test de la commande Forward."""
        self.client._send.return_value = None
        self.client._receive.return_value = "ok\n"
        
        result = self.protocol.forward()
        
        self.client._send.assert_called_once_with("Forward\n")
        self.client._receive.assert_called_once()
        self.assertTrue(result)

    def test_right(self):
        """Test de la commande Right."""
        self.client._send.return_value = None
        self.client._receive.return_value = "ok\n"
        
        result = self.protocol.right()
        
        self.client._send.assert_called_once_with("Right\n")
        self.client._receive.assert_called_once()
        self.assertTrue(result)

    def test_left(self):
        """Test de la commande Left."""
        self.client._send.return_value = None
        self.client._receive.return_value = "ok\n"
        
        result = self.protocol.left()
        
        self.client._send.assert_called_once_with("Left\n")
        self.client._receive.assert_called_once()
        self.assertTrue(result)

    def test_look(self):
        """Test de la commande Look."""
        expected_response = "[player food, food linemate, , player deraumere]\n"
        self.client._send.return_value = None
        self.client._receive.return_value = expected_response
        
        result = self.protocol.look()
        
        self.client._send.assert_called_once_with("Look\n")
        self.client._receive.assert_called_once()
        self.assertEqual(result, expected_response.strip())

    def test_inventory(self):
        """Test de la commande Inventory."""
        expected_response = "[food 2, linemate 1, sibur 0, mendiane 0, phiras 0, thystame 0]\n"
        self.client._send.return_value = None
        self.client._receive.return_value = expected_response
        
        result = self.protocol.inventory()
        
        self.client._send.assert_called_once_with("Inventory\n")
        self.client._receive.assert_called_once()
        self.assertEqual(result, expected_response.strip())

    def test_broadcast(self):
        """Test de la commande Broadcast."""
        message = "Hello team!"
        self.client._send.return_value = None
        self.client._receive.return_value = "ok\n"
        
        result = self.protocol.broadcast(message)
        
        self.client._send.assert_called_once_with(f"Broadcast {message}\n")
        self.client._receive.assert_called_once()
        self.assertTrue(result)

    def test_connect_nbr(self):
        """Test de la commande Connect_nbr."""
        self.client._send.return_value = None
        self.client._receive.return_value = "2\n"
        
        result = self.protocol.connect_nbr()
        
        self.client._send.assert_called_once_with("Connect_nbr\n")
        self.client._receive.assert_called_once()
        self.assertEqual(result, 2)

    def test_fork(self):
        """Test de la commande Fork."""
        self.client._send.return_value = None
        self.client._receive.return_value = "ok\n"
        
        result = self.protocol.fork()
        
        self.client._send.assert_called_once_with("Fork\n")
        self.client._receive.assert_called_once()
        self.assertTrue(result)

    def test_eject(self):
        """Test de la commande Eject."""
        self.client._send.return_value = None
        self.client._receive.return_value = "ok\n"
        
        result = self.protocol.eject()
        
        self.client._send.assert_called_once_with("Eject\n")
        self.client._receive.assert_called_once()
        self.assertTrue(result)

    def test_take(self):
        """Test de la commande Take."""
        object_name = "food"
        self.client._send.return_value = None
        self.client._receive.return_value = "ok\n"
        
        result = self.protocol.take(object_name)
        
        self.client._send.assert_called_once_with(f"Take {object_name}\n")
        self.client._receive.assert_called_once()
        self.assertTrue(result)

    def test_set(self):
        """Test de la commande Set."""
        object_name = "linemate"
        self.client._send.return_value = None
        self.client._receive.return_value = "ok\n"
        
        result = self.protocol.set(object_name)
        
        self.client._send.assert_called_once_with(f"Set {object_name}\n")
        self.client._receive.assert_called_once()
        self.assertTrue(result)

    def test_incantation(self):
        """Test de la commande Incantation."""
        self.client._send.return_value = None
        self.client._receive.side_effect = [
            "Elevation underway\n",
            "Current level: 2\n"
        ]
        
        result = self.protocol.incantation()
        
        self.client._send.assert_called_once_with("Incantation\n")
        self.assertEqual(self.client._receive.call_count, 2)
        self.assertEqual(result, 2)

if __name__ == '__main__':
    unittest.main() 