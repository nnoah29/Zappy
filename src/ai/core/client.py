import socket
import logging
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
            # Création et connexion du socket
            self.logger.info(f"Tentative de connexion à {self.hostname}:{self.port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(7.0)  # Timeout pour la connexion initiale
            self.socket.connect((self.hostname, self.port))
            self.logger.info("Socket connecté avec succès")

            # Réception du message de bienvenue
            self.logger.info("En attente du message de bienvenue...")
            welcome = self._receive()
            self.logger.info(f"Message reçu: {welcome}")
            if welcome != "WELCOME":
                raise Exception(f"Message de bienvenue invalide: {welcome}")

            # Envoi du nom d'équipe
            self.logger.info(f"Envoi du nom d'équipe: {self.team_name}")
            self._send(self.team_name + "\n")

            # Réception de la réponse du serveur (peut contenir plusieurs lignes)
            self.logger.info("En attente de la réponse du serveur...")
            response = self._receive()
            self.logger.info(f"Réponse reçue: {response}")
            lines = response.strip().split('\n')

            # Lecture du numéro de client
            try:
                self.client_num = int(lines[0])
                self.logger.info(f"Numéro de client reçu: {self.client_num}")
            except ValueError:
                raise Exception(f"Numéro de client invalide: {lines[0]}")

            # Si la map est déjà présente dans la même réponse
            if len(lines) > 1:
                map_size = lines[1]
                self.logger.info(f"Dimensions de la carte reçues dans la même réponse: {map_size}")
            else:
                self.logger.info("En attente des dimensions de la carte...")
                map_size = self._receive()
                self.logger.info(f"Dimensions de la carte reçues: {map_size}")

            # Lecture des dimensions de la carte
            try:
                dimensions = map_size.strip().split()
                if len(dimensions) != 2:
                    raise Exception(f"Format de dimensions invalide: {map_size}")
                self.map_size = (int(dimensions[0]), int(dimensions[1]))
                self.logger.info(f"Dimensions de la carte parsées: {self.map_size}")
            except ValueError:
                raise Exception(f"Dimensions invalides: {map_size}")

            self.logger.info(f"Connecté au serveur. Client #{self.client_num}, Carte: {self.map_size[0]}x{self.map_size[1]}")

        except Exception as e:
            self.logger.error(f"Erreur de connexion: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            raise  # Propager l'erreur pour une meilleure gestion en amont

    def _get_timeout(self, command: str) -> float:
        """Récupère le timeout pour une commande donnée.
        
        Args:
            command (str): Nom de la commande
            
        Returns:
            float: Timeout en secondes
        """
        # Extrait le nom de la commande (sans les arguments)
        cmd_name = command.split()[0]
        return self.TIMEOUTS.get(cmd_name, 7.0)  # Timeout par défaut de 7 secondes

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
        """Reçoit une réponse du serveur."""
        if not self.socket:
            raise Exception("Socket non connecté")
        
        try:
            self.logger.debug("En attente de données du serveur...")
            data = self.socket.recv(4096)
            if not data:
                raise Exception("Connexion fermée par le serveur")
            
            response = data.decode('utf-8').strip()
            self.logger.debug(f"Données reçues: {response}")
            return response
        except socket.timeout:
            self.logger.error("Timeout lors de la réception des données")
            raise
        except socket.error as e:
            self.logger.error(f"Erreur lors de la réception: {e}")
            raise socket.error("Erreur de réception")
        except Exception as e:
            self.logger.error(f"Erreur lors de la réception: {e}")
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
            self.close()

    def close(self):
        """Ferme la connexion avec le serveur."""
        if self.socket:
            self.socket.close()
            self.socket = None