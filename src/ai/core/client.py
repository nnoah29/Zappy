import socket
import logging
from typing import Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ZappyClient:
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
        self.ai = None
        self.server_disconnected = False

    def connect(self):
        """Établit la connexion avec le serveur et effectue le protocole d'authentification."""
        try:
            self.logger.info(f"Tentative de connexion à {self.hostname}:{self.port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(7.0)
            self.socket.connect((self.hostname, self.port))
            self.logger.info("Socket connecté avec succès")

            self.logger.info("En attente du message de bienvenue...")
            welcome = self._receive()
            self.logger.info(f"Message reçu: {welcome}")
            if welcome != "WELCOME":
                raise Exception(f"Message de bienvenue invalide: {welcome}")

            self.logger.info(f"Envoi du nom d'équipe: {self.team_name}")
            self._send(self.team_name + "\n")

            self.logger.info("En attente de la réponse du serveur...")
            response = self._receive()
            self.logger.info(f"Réponse reçue: {response}")
            lines = response.strip().split('\n')

            try:
                self.client_num = int(lines[0])
                self.logger.info(f"Numéro de client reçu: {self.client_num}")
            except ValueError:
                raise Exception(f"Numéro de client invalide: {lines[0]}")

            if len(lines) > 1:
                map_size = lines[1]
                self.logger.info(f"Dimensions de la carte reçues dans la même réponse: {map_size}")
            else:
                self.logger.info("En attente des dimensions de la carte...")
                map_size = self._receive()
                self.logger.info(f"Dimensions de la carte reçues: {map_size}")

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
            raise

    def is_connected(self) -> bool:
        """Vérifie si la connexion au serveur est toujours active.
        
        Returns:
            bool: True si la connexion est active, False sinon
        """
        if self.server_disconnected:
            return False
            
        if not self.socket:
            return False
            
        try:
            # Test de la connexion en envoyant un ping (0 octet)
            self.socket.send(b'')
            return True
        except (socket.error, OSError, ConnectionError):
            self.logger.warning("🔌 Connexion au serveur perdue")
            self.server_disconnected = True
            return False

    def _get_timeout(self, command: str) -> float:
        """Récupère le timeout pour une commande donnée.
        
        Args:
            command (str): Nom de la commande
            
        Returns:
            float: Timeout en secondes
        """
        cmd_name = command.split()[0]
        return self.TIMEOUTS.get(cmd_name, 7.0)

    def _send(self, message: str):
        """Envoie un message au serveur.
        
        Args:
            message (str): Message à envoyer
            
        Raises:
            socket.error: Si l'envoi échoue
            TimeoutError: Si le timeout est dépassé
            ConnectionError: Si la connexion est perdue
        """
        if not self.socket:
            raise ConnectionError("Non connecté au serveur")
            
        if self.server_disconnected:
            raise ConnectionError("Connexion au serveur perdue")
            
        try:
            timeout = self._get_timeout(message)
            self.socket.settimeout(timeout)
            
            self.socket.send(message.encode())
            self.logger.debug(f"Envoyé ({timeout}s): {message.strip()}")
            
        except socket.timeout:
            error_msg = f"Timeout d'envoi après {timeout}s pour: {message.strip()}"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg)
        except (socket.error, OSError, ConnectionError) as e:
            error_msg = f"Erreur d'envoi: {str(e)}"
            self.logger.error(error_msg)
            self.server_disconnected = True
            raise ConnectionError(error_msg)
        finally:
            self.socket.settimeout(None)

    def _receive(self) -> str:
        """Reçoit une réponse du serveur."""
        if not self.socket:
            raise Exception("Socket non connecté")
            
        if self.server_disconnected:
            raise ConnectionError("Connexion au serveur perdue")
        
        try:
            self.logger.debug("En attente de données du serveur...")
            data = self.socket.recv(4096)
            if not data:
                self.logger.warning("🔌 Serveur a fermé la connexion")
                self.server_disconnected = True
                raise ConnectionError("Connexion fermée par le serveur")
            
            response = data.decode('utf-8').strip()
            self.logger.debug(f"Données reçues: {response}")
            
            # Vérifier si c'est le message "dead"
            if response == "dead":
                self.logger.critical("💀 Message 'dead' reçu du serveur - le joueur est mort !")
                self.server_disconnected = True
                raise ConnectionError("Joueur mort - connexion fermée par le serveur")
            
            return response
        except socket.timeout:
            self.logger.error("Timeout lors de la réception des données")
            raise
        except (socket.error, OSError, ConnectionError) as e:
            self.logger.error(f"Erreur lors de la réception: {e}")
            self.server_disconnected = True
            raise ConnectionError("Erreur de réception")
        except Exception as e:
            self.logger.error(f"Erreur lors de la réception: {e}")
            raise

    def run(self) -> bool:
        """Exécute une itération de l'IA.
        
        Returns:
            bool: True si l'IA continue de fonctionner, False si elle doit s'arrêter
        """
        try:
            # Vérifier la connexion avant d'exécuter l'IA
            if not self.is_connected():
                self.logger.error("🔌 Connexion au serveur perdue, arrêt de l'IA")
                return False
                
            return self.ai.update()
        except ConnectionError as e:
            self.logger.error(f"🔌 Erreur de connexion dans l'exécution de l'IA: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur dans l'exécution de l'IA: {e}")
            return False

    def close(self):
        """Ferme la connexion avec le serveur."""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.server_disconnected = True

    def check_for_messages(self) -> Optional[str]:
        """Vérifie s'il y a des messages en attente du serveur.
        
        Returns:
            str: Message reçu, ou None s'il n'y en a pas
        """
        if not self.socket or self.server_disconnected:
            return None
            
        try:
            self.socket.settimeout(0.001)
            data = self.socket.recv(4096)
            if data:
                message = data.decode('utf-8').strip()
                self.logger.debug(f"Message reçu: {message}")
                
                # Vérifier si c'est le message "dead"
                if message == "dead":
                    self.logger.critical("💀 Message 'dead' reçu du serveur - le joueur est mort !")
                    self.server_disconnected = True
                
                return message
        except socket.timeout:
            pass
        except (socket.error, OSError, ConnectionError) as e:
            self.logger.error(f"Erreur lors de la vérification des messages: {e}")
            self.server_disconnected = True
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification des messages: {e}")
        finally:
            self.socket.settimeout(None)
            
        return None