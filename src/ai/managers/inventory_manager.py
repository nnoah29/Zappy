from typing import Any
from core.protocol import ZappyProtocol
import logging

class InventoryManager:
    """Gère l'inventaire du joueur."""

    def __init__(self, protocol: ZappyProtocol, player: Any, logger: logging.Logger):
        """Initialise le gestionnaire d'inventaire.
        
        Args:
            protocol (ZappyProtocol): Protocole de communication
            player (Any): Joueur contrôlé
            logger (Logger): Logger pour les messages
        """
        self.protocol = protocol
        self.player = player
        self.logger = logger
        self.inventory = {
            'food': 0,
            'linemate': 0,
            'deraumere': 0,
            'sibur': 0,
            'mendiane': 0,
            'phiras': 0,
            'thystame': 0
        }
        self.logger.info(f"inventory created: {self.inventory}")

    def update_inventory(self) -> bool:
        """Met à jour l'inventaire.
        
        Returns:
            bool: True si la mise à jour a réussi
        """
        try:
            response = self.protocol.inventory()
            if not response:
                self.logger.error("Pas de réponse du serveur pour l'inventaire")
                return False
                
            items = response.strip('[]').split(',')
            for item in items:
                name, count = item.strip().split()
                self.inventory[name] = int(count)
                
            self.logger.debug(f"Inventaire mis à jour: {self.inventory}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'inventaire: {str(e)}")
            return False

    def take_object(self, object_type: str) -> bool:
        """Prend un objet.
        
        Args:
            object_type (str): Type d'objet à prendre
            
        Returns:
            bool: True si l'objet a été pris
        """
        try:
            response = self.protocol.take(object_type)
            if response == "ok":
                if not self.update_inventory():
                    self.logger.error("Erreur lors de la mise à jour de l'inventaire après prise")
                    return False
                self.logger.debug(f"{object_type} pris avec succès, inventaire: {self.inventory}")
                return True
            self.logger.debug(f"Impossible de prendre {object_type}: {response}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la prise d'objet: {str(e)}")
            return False

    def drop_object(self, object_type: str) -> bool:
        """Pose un objet.
        
        Args:
            object_type (str): Type d'objet à poser
            
        Returns:
            bool: True si l'objet a été posé
        """
        try:
            response = self.protocol.set(object_type)
            if response == "ok":
                self.inventory[object_type] -= 1
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors du dépôt d'objet: {str(e)}")
            return False 