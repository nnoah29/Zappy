import socket
import logging
import select
from typing import Tuple, Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ZappyClient:
    # Timeouts en secondes pour chaque commande
    TIMEOUTS = {
        "Forward": 7,
        "Right": 7,
        "Left": 7,
        "Look": 7,
        "Inventory": 1,
        "Broadcast": 7,
        "Connect_nbr": 42,
        "Fork": 42,
        "Eject": 7,
        "Take": 7,
        "Set": 7,
        "Incantation": 300
    }

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
            self._send(self.team_name + "\n")
            
            # Réception du numéro de client
            self.client_num = int(self._receive())
            
            # Réception de la taille de la carte
            map_size = self._receive().split()
            self.map_size = (int(map_size[0]), int(map_size[1]))
        except Exception as e:
            self.logger.error(f"Erreur de connexion: {e}")
            raise

    def _get_timeout(self, command: str) -> float:
        """Récupère le timeout pour une commande donnée.
        
        Args:
            command (str): Nom de la commande
            
        Returns:
            float: Timeout en secondes
        """
        # Extrait le nom de la commande (sans les arguments)
        cmd_name = command.split()[0]
        return self.TIMEOUTS.get(cmd_name, 7.0)

    def _send(self, message: str):
        """Envoie un message au serveur.
        
        Args:
            message (str): Message à envoyer
            
        Raises:
            socket.error: Si l'envoi échoue
            TimeoutError: Si le timeout est dépassé
        """
        if not self.socket:
            raise ConnectionError("Non connecté au serveur")
            
        try:
            # Configure le timeout pour l'envoi
            timeout = self._get_timeout(message)
            self.socket.settimeout(timeout)
            
            # Envoie le message
            self.socket.send(message.encode())
            self.logger.debug(f"Envoyé ({timeout}s): {message.strip()}")
            
        except socket.timeout:
            error_msg = f"Timeout d'envoi après {timeout}s pour: {message.strip()}"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg)
        except socket.error as e:
            error_msg = f"Erreur d'envoi: {str(e)}"
            self.logger.error(error_msg)
            raise socket.error(error_msg)
        finally:
            self.socket.settimeout(None)

    def _receive(self) -> str:
        """Reçoit un message du serveur.
        
        Returns:
            str: Message reçu
            
        Raises:
            socket.error: Si la réception échoue
            TimeoutError: Si le timeout est dépassé
        """
        if not self.socket:
            raise ConnectionError("Non connecté au serveur")
            
        try:
            # Configure le timeout pour la réception
            self.socket.settimeout(7.0)  # Timeout par défaut pour la réception
            
            # Attend les données avec select
            ready = select.select([self.socket], [], [], 7.0)
            if not ready[0]:
                raise TimeoutError("Timeout de réception après 7s")
                
            data = self.socket.recv(4096)
            if not data:
                raise ConnectionError("Connexion fermée par le serveur")
                
            message = data.decode().strip()
            self.logger.debug(f"Reçu: {message}")
            return message
            
        except socket.timeout:
            error_msg = "Timeout de réception après 7s"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg)
        except socket.error as e:
            error_msg = f"Erreur de réception: {str(e)}"
            self.logger.error(error_msg)
            raise socket.error(error_msg)
        finally:
            # Réinitialise le timeout
            self.socket.settimeout(None)

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