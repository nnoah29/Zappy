import logging
import time
from typing import Optional, List, Dict, Any
from .client import ZappyClient

class ZappyProtocol:
    def __init__(self, client: ZappyClient):
        """Initialise le protocole avec un client.
        
        Args:
            client (ZappyClient): Client connecté au serveur
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.last_response: Optional[str] = None
        self.last_error: Optional[str] = None

    def _handle_response(self, response: str) -> bool:
        """Gère la réponse du serveur.
        
        Args:
            response (str): Réponse du serveur
            
        Returns:
            bool: True si la commande a réussi, False sinon
        """
        self.last_response = response
        if response == "ok":
            self.last_error = None
            return True
        elif response == "ko":
            self.last_error = "Commande refusée par le serveur"
            return False
        else:
            self.last_error = f"Réponse invalide du serveur: {response}"
            raise ValueError(self.last_error)

    def forward(self) -> bool:
        """Avance d'une case.
        
        Returns:
            bool: True si le mouvement a réussi, False sinon
        """
        try:
            self.client._send("Forward\n")
            response = self.client._receive().strip()
            return self._handle_response(response)
        except Exception as e:
            self.last_error = f"Erreur lors du déplacement: {e}"
            raise

    def right(self) -> bool:
        """Tourne à droite.
        
        Returns:
            bool: True si la rotation a réussi, False sinon
        """
        try:
            self.client._send("Right\n")
            response = self.client._receive().strip()
            return self._handle_response(response)
        except Exception as e:
            self.last_error = f"Erreur lors de la rotation: {e}"
            raise

    def left(self) -> bool:
        """Tourne à gauche.
        
        Returns:
            bool: True si la rotation a réussi, False sinon
        """
        try:
            self.client._send("Left\n")
            response = self.client._receive().strip()
            return self._handle_response(response)
        except Exception as e:
            self.last_error = f"Erreur lors de la rotation: {e}"
            raise

    def look(self) -> str:
        """Regarde autour du joueur.
        
        Returns:
            str: Réponse brute du serveur
        """
        try:
            self.client._send("Look\n")
            response = self.client._receive().strip()
            self.last_response = response
            return response
        except Exception as e:
            self.last_error = f"Erreur lors de la vision: {e}"
            raise

    def inventory(self) -> str:
        """Consulte l'inventaire.
        
        Returns:
            str: Réponse brute du serveur
        """
        try:
            self.client._send("Inventory\n")
            response = self.client._receive().strip()
            self.last_response = response
            return response
        except Exception as e:
            self.last_error = f"Erreur lors de la consultation de l'inventaire: {e}"
            raise

    def broadcast(self, message: str) -> bool:
        """Envoie un message à tous les joueurs.
        
        Args:
            message (str): Message à envoyer
            
        Returns:
            bool: True si le message a été envoyé, False sinon
        """
        try:
            self.client._send(f"Broadcast {message}\n")
            response = self.client._receive().strip()
            return self._handle_response(response)
        except Exception as e:
            self.last_error = f"Erreur lors de l'envoi du message: {e}"
            raise

    def connect_nbr(self) -> int:
        """Demande le nombre de places disponibles dans l'équipe.
        
        Returns:
            int: Nombre de places disponibles
        """
        try:
            self.client._send("Connect_nbr\n")
            response = self.client._receive().strip()
            self.last_response = response
            return int(response)
        except Exception as e:
            self.last_error = f"Erreur lors de la demande de places: {e}"
            raise

    def fork(self) -> bool:
        """Pond un œuf.
        
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        try:
            self.client._send("Fork\n")
            response = self.client._receive().strip()
            return self._handle_response(response)
        except Exception as e:
            self.last_error = f"Erreur lors de la ponte: {e}"
            raise

    def eject(self) -> bool:
        """Expulse les joueurs de la case.
        
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        try:
            self.client._send("Eject\n")
            response = self.client._receive().strip()
            return self._handle_response(response)
        except Exception as e:
            self.last_error = f"Erreur lors de l'expulsion: {e}"
            raise

    def take(self, object_name: str) -> bool:
        """Prend un objet.
        
        Args:
            object_name (str): Nom de l'objet à prendre
            
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        try:
            self.client._send(f"Take {object_name}\n")
            response = self.client._receive().strip()
            return self._handle_response(response)
        except Exception as e:
            self.last_error = f"Erreur lors de la prise d'objet: {e}"
            raise

    def set(self, object_name: str) -> bool:
        """Pose un objet.
        
        Args:
            object_name (str): Nom de l'objet à poser
            
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        try:
            self.client._send(f"Set {object_name}\n")
            response = self.client._receive().strip()
            return self._handle_response(response)
        except Exception as e:
            self.last_error = f"Erreur lors du dépôt d'objet: {e}"
            raise

    def incantation(self) -> str:
        """Commence un rituel d'élévation.
        
        Returns:
            str: Réponse du serveur ("elevation underway", "ko", etc.)
        """
        try:
            self.client._send("Incantation\n")
            response = self.client._receive().strip()
            self.last_response = response
            return response
        except Exception as e:
            self.last_error = f"Erreur lors de l'élévation: {e}"
            raise

    def parse_look_response(self, response: str) -> list:
        """Parse la réponse de la commande Look.
        
        Args:
            response (str): Réponse brute du serveur
            
        Returns:
            list: Liste des cases vues avec leurs objets
        """
        try:
            # Enlève les crochets et sépare les cases
            response = response.strip('[]')
            cases = [case.strip() for case in response.split(',')]
            return cases
        except Exception as e:
            self.last_error = f"Erreur lors du parsing de la vision: {e}"
            raise

    def parse_inventory_response(self, response: str) -> dict:
        """Parse la réponse de la commande Inventory.
        
        Args:
            response (str): Réponse brute du serveur
            
        Returns:
            dict: Inventaire avec les quantités
        """
        try:
            # Enlève les crochets et sépare les objets
            response = response.strip('[]')
            items = [item.strip() for item in response.split(',')]
            inventory = {}
            for item in items:
                if item:
                    name, quantity = item.split()
                    inventory[name] = int(quantity)
            return inventory
        except Exception as e:
            self.last_error = f"Erreur lors du parsing de l'inventaire: {e}"
            raise

    def parse_broadcast_response(self, response: str) -> tuple:
        """Parse la réponse d'un broadcast.
        
        Args:
            response (str): Réponse brute du serveur
            
        Returns:
            tuple: (direction, message)
        """
        try:
            # Format: "message K, text"
            parts = response.split(',', 1)
            direction = int(parts[0].split()[1])
            message = parts[1].strip()
            return (direction, message)
        except Exception as e:
            self.last_error = f"Erreur lors du parsing du broadcast: {e}"
            raise

    def parse_eject_response(self, response: str) -> int:
        """Parse la réponse d'un eject.
        
        Args:
            response (str): Réponse brute du serveur
            
        Returns:
            int: Direction de l'éjection
        """
        try:
            # Format: "eject: K"
            return int(response.split(':')[1].strip())
        except Exception as e:
            self.last_error = f"Erreur lors du parsing de l'éjection: {e}"
            raise