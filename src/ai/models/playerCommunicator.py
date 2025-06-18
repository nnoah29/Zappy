import logging
from typing import Optional, Dict, Any
from core.protocol import ZappyProtocol

class PlayerCommunicator:
    """
    Gère la communication entre joueurs (broadcast, réception, parsing).
    Utilise le protocole du projet pour envoyer et recevoir des messages.
    """

    def __init__(self, protocol: ZappyProtocol, player, logger: Optional[logging.Logger] = None):
        """
        Args:
            protocol: Instance du protocole de communication (ex: ZappyProtocol)
            player: Instance du joueur courant
            logger: Logger optionnel
        """
        self.protocol = protocol
        self.player = player
        self.logger = logger or logging.getLogger(__name__)

    def broadcast(self, message: str) -> bool:
        """
        Envoie un message à tous les joueurs via le protocole broadcast.

        Args:
            message (str): Message à envoyer

        Retour type:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            response = self.protocol.broadcast(message)
            if response == "ok":
                self.logger.info(f"Broadcast envoyé: {message}")
                return True
            else:
                self.logger.warning(f"Broadcast échoué: {response}")
                return False
        except Exception as e:
            self.logger.error(f"Erreur lors du broadcast: {e}")
            return False

    def receive_broadcast(self) -> Optional[Dict[str, Any]]:
        """
        Récupère et parse un message broadcast reçu via le protocole (si disponible).

        Retour type:
            dict: Dictionnaire contenant les informations du message, ou None si aucun message
        """
        try:
            # Supposons que le protocole a une méthode pour récupérer le dernier broadcast reçu
            response = self.protocol.get_last_broadcast()
            if response:
                parsed = self.parse_message(response)
                self.logger.info(f"Message reçu: {parsed}")
                return parsed
            return None
        except Exception as e:
            self.logger.error(f"Erreur lors de la réception du message: {e}")
            return None

    def parse_message(self, raw_message: str) -> Dict[str, Any]:
        """
        Parse un message brut reçu (format: "team:action:data" ou JSON).

        Arguments:
            raw_message (str): Message brut

        Retour type:
            dict: Dictionnaire avec les champs extraits
        """
        try:
            if raw_message.startswith("{") and raw_message.endswith("}"):
                # Format JSON
                import json
                return json.loads(raw_message)
            else:
                # Format string: "team:action:data"
                parts = raw_message.split(":", 2)
                if len(parts) == 3:
                    return {"team": parts[0], "action": parts[1], "data": parts[2]}
                elif len(parts) == 2:
                    return {"team": parts[0], "action": parts[1], "data": ""}
                else:
                    return {"raw": raw_message}
        except Exception as e:
            self.logger.error(f"Erreur lors du parsing du message: {e}")
            return {"raw": raw_message}

    def send_team_message(self, action: str, data: str = "") -> bool:
        """
        Envoie un message structuré à l'équipe (format: "team:action:data").

        Args:
            action (str): Action à communiquer
            data (str): Données additionnelles

        Returns:
            bool: True si succès, False sinon
        """
        team = getattr(self.player, "team", "unknown")
        message = f"{team}:{action}:{data}"
        return self.broadcast(message)

    def handle_incoming_messages(self, callback=None):
        """
        Vérifie s'il y a un message reçu et exécute un callback si besoin.

        Args:
            callback (callable): Fonction à appeler avec le message parsé
        """
        msg = self.receive_broadcast()
        if msg and callback:
            callback(msg)