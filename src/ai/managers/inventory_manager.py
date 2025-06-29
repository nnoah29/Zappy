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
                
            if not response.startswith('[') or not response.endswith(']'):
                self.logger.warning(f"Réponse d'inventaire invalide: {response}")
                return False
                
            items = response.strip('[]').split(',')
            for item in items:
                item = item.strip()
                if not item:
                    continue
                    
                try:
                    parts = item.split()
                    if len(parts) != 2:
                        self.logger.warning(f"Format d'item invalide: '{item}' dans la réponse: {response}")
                        continue
                        
                    name, count = parts
                    if name in self.inventory:
                        self.inventory[name] = int(count)
                    else:
                        self.logger.warning(f"Type d'objet inconnu: {name}")
                        
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Erreur de parsing pour l'item '{item}': {e}")
                    continue
                
            self.logger.debug(f"Inventaire mis à jour: {self.inventory}")
            return True
        except ConnectionError as e:
            self.logger.error(f"🔌 Erreur de connexion lors de la mise à jour de l'inventaire: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'inventaire: {str(e)}")
            return False

    def force_update_inventory(self) -> bool:
        """Force la mise à jour de l'inventaire en ignorant les cooldowns.
        
        Returns:
            bool: True si la mise à jour a réussi
        """
        try:
            self.logger.debug("🔄 Mise à jour forcée de l'inventaire")
            return self.update_inventory()
        except ConnectionError as e:
            self.logger.error(f"🔌 Erreur de connexion lors de la mise à jour forcée de l'inventaire: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour forcée de l'inventaire: {str(e)}")
            return False

    def take_object(self, object_type: str) -> bool:
        """Prend un objet.
        
        Args:
            object_type (str): Type d'objet à prendre
            
        Returns:
            bool: True si l'objet a été pris
        """
        try:
            success = self.protocol.take(object_type)
            if success:
                if not self.update_inventory():
                    self.logger.error("Erreur lors de la mise à jour de l'inventaire après prise")
                    return False
                self.logger.debug(f"✅ {object_type} pris avec succès, inventaire: {self.inventory}")
                return True
            self.logger.debug(f"❌ Impossible de prendre {object_type}: échec de la commande")
            return False
        except ConnectionError as e:
            self.logger.error(f"🔌 Erreur de connexion lors de la prise d'objet: {e}")
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
            success = self.protocol.set(object_type)
            if success:
                self.inventory[object_type] -= 1
                return True
            return False
        except ConnectionError as e:
            self.logger.error(f"🔌 Erreur de connexion lors du dépôt d'objet: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors du dépôt d'objet: {str(e)}")
            return False 