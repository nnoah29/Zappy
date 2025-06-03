import socket
import logging
from typing import Tuple

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ZappyClient:
    def __init__(self, hostname: str, port: int, team_name: str):
        """Initialise le client Zappy.
        
        Args:
            hostname (str): Nom d'hôte du serveur
            port (int): Port du serveur
            team_name (str): Nom de l'équipe
        """
        self.hostname = hostname
        self.port = port
        self.team_name = team_name
        self.socket = None
        self.logger = logging.getLogger(__name__)
        self.map_size = None
        self.client_num = None

    def connect(self):
        """Établit la connexion avec le serveur et effectue le protocole d'authentification."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.hostname, self.port))
            
            # Réception du message de bienvenue
            welcome = self._receive()
            if welcome != "WELCOME":
                raise Exception("Message de bienvenue invalide")
            
            # Envoi du nom d'équipe
            self._send(self.team_name)
            
            # Réception du numéro de client
            self.client_num = int(self._receive())
            
            # Réception de la taille de la carte
            map_size = self._receive().split()
            self.map_size = (int(map_size[0]), int(map_size[1]))
        except Exception as e:
            self.logger.error(f"Erreur de connexion: {e}")
            raise

    def _send(self, message: str):
        """Envoie un message au serveur.
        
        Args:
            message (str): Message à envoyer
        """
        try:
            self.socket.send(message.encode())
        except socket.error as e:
            error_msg = f"Erreur d'envoi: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def _receive(self) -> str:
        """Reçoit un message du serveur.
        
        Returns:
            str: Message reçu
        """
        try:
            data = self.socket.recv(1024)
            if not data:
                raise Exception("Connexion fermée par le serveur")
            return data.decode().strip()
        except socket.error as e:
            error_msg = f"Erreur de réception: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def run(self) -> None:
        """Boucle principale du client."""
        try:
            while True:
                # TODO: Implémenter la logique de jeu
                pass
        except Exception as e:
            self.logger.error(f"Erreur dans la boucle principale: {e}")
            raise
        finally:
            self.close()

    def close(self):
        """Ferme la connexion avec le serveur."""
        if self.socket:
            self.socket.close()
            self.socket = None