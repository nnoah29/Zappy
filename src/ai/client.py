import socket
import logging
from typing import Tuple

class ZappyClient:
    def __init__(self, hostname: str, port: int, team_name: str):
        self.hostname = hostname
        self.port = port
        self.team_name = team_name
        self.socket = None
        self.logger = logging.getLogger(__name__)
        self.map_size = (0, 0)
        self.client_num = 0

    def connect(self) -> None:
        """Établit la connexion avec le serveur et effectue le protocole d'authentification."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.hostname, self.port))
            self._handle_welcome()
            self._send_team_name()
            self._handle_connection_info()
        except Exception as e:
            self.logger.error(f"Erreur de connexion: {e}")
            raise

    def _handle_welcome(self) -> None:
        """Gère le message de bienvenue du serveur."""
        response = self._receive()
        if response != "WELCOME\n":
            raise Exception("Message de bienvenue invalide")

    def _send_team_name(self) -> None:
        """Envoie le nom de l'équipe au serveur."""
        self._send(f"{self.team_name}\n")

    def _handle_connection_info(self) -> None:
        """Gère les informations de connexion (client_num et dimensions de la map)."""
        self.client_num = int(self._receive().strip())
        map_info = self._receive().strip().split()
        self.map_size = (int(map_info[0]), int(map_info[1]))

    def _send(self, message: str) -> None:
        """Envoie un message au serveur."""
        try:
            self.socket.send(message.encode())
        except Exception as e:
            self.logger.error(f"Erreur d'envoi: {e}")
            raise

    def _receive(self) -> str:
        """Reçoit un message du serveur."""
        try:
            return self.socket.recv(1024).decode()
        except Exception as e:
            self.logger.error(f"Erreur de réception: {e}")
            raise

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
            self.socket.close() 