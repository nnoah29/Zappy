import logging
from typing import Dict, Optional, Tuple, List
from client import ZappyClient
from protocol import ZappyProtocol
from vision import Vision
from collision_manager import CollisionManager
from movement import Movement

class AI:
    def __init__(self, client: ZappyClient):
        """Initialise l'IA.
        
        Args:
            client (ZappyClient): Client connecté au serveur
        """
        self.client = client
        self.protocol = ZappyProtocol(client)
        self.vision = Vision(self.protocol)
        self.movement = Movement(self.protocol, self.vision)
        self.collision_manager = CollisionManager(self.protocol, self.vision, self.movement)
        self.logger = logging.getLogger(__name__)
        self.level = 1
        self.inventory: Dict[str, int] = {}
        self.current_action = None
        self.target_position: Optional[Tuple[int, int]] = None
        self.last_positions: List[Tuple[int, int]] = []  # Pour détecter les collisions
        self.stuck_count = 0  # Compteur de blocages

    def update(self) -> None:
        """Met à jour l'état de l'IA et prend une décision."""
        try:
            # Met à jour la vision
            self.vision.look()  # La vision est mise à jour automatiquement lors de l'appel à look()
            
            # Met à jour l'inventaire
            inventory_response = self.protocol.inventory()
            self._update_inventory(inventory_response)
            
            # Prend une décision
            self._make_decision()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour: {e}")
            raise

    def _update_inventory(self, inventory_str: str) -> None:
        """Met à jour l'inventaire à partir de la réponse du serveur.
        
        Args:
            inventory_str (str): Réponse du serveur pour l'inventaire
        """
        try:
            self.logger.debug(f"Réponse brute de l'inventaire: {inventory_str}")
            # Format: "[nourriture X, linemate Y, deraumere Z, ...]"
            items = inventory_str.strip("[]").split(", ")
            self.logger.debug(f"Items après split: {items}")
            self.inventory = {}
            for item in items:
                self.logger.debug(f"Traitement de l'item: {item}")
                parts = item.split(" ")
                self.logger.debug(f"Parts après split: {parts}")
                if len(parts) != 2:
                    raise Exception(f"Format d'item invalide: {item}")
                name, count = parts
                self.inventory[name] = int(count)
            self.logger.debug(f"Inventaire mis à jour: {self.inventory}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'inventaire: {e}")
            raise

    def _make_decision(self) -> None:
        """Prend une décision basée sur l'état actuel."""
        # Vérifie si on peut monter de niveau
        if self._can_level_up():
            self._start_level_up()
            return

        # Cherche des ressources
        if self._need_resources():
            self._find_resources()
            return

        # Explore si pas d'objectif
        if not self.target_position:
            self._explore()
            return

        # Continue vers l'objectif
        self._move_to_target()

    def _can_level_up(self) -> bool:
        """Vérifie si le joueur peut monter de niveau.
        
        Returns:
            bool: True si le joueur peut monter de niveau
        """
        # Vérifie les conditions de niveau
        required_items = {
            1: {"linemate": 1},
            2: {"linemate": 1, "deraumere": 1, "sibur": 1},
            3: {"linemate": 2, "sibur": 1, "phiras": 2},
            4: {"linemate": 1, "deraumere": 1, "sibur": 2, "phiras": 1},
            5: {"linemate": 1, "deraumere": 2, "sibur": 1, "mendiane": 3},
            6: {"linemate": 1, "deraumere": 2, "sibur": 3, "phiras": 1},
            7: {"linemate": 2, "deraumere": 2, "sibur": 2, "mendiane": 2, "phiras": 2, "thystame": 1}
        }

        if self.level >= 8:
            return False

        required = required_items[self.level]
        for item, count in required.items():
            if self.inventory.get(item, 0) < count:
                return False
        return True

    def _start_level_up(self) -> None:
        """Démarre le rituel d'élévation."""
        try:
            result = self.protocol.incantation()
            if result > 0:
                self.level = result
                self.logger.info(f"Niveau {self.level} atteint!")
            else:
                self.logger.warning("Échec de l'élévation")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'élévation: {e}")

    def _need_resources(self) -> bool:
        """Vérifie si le joueur a besoin de ressources.
        
        Returns:
            bool: True si le joueur a besoin de ressources
        """
        # Vérifie la nourriture
        if self.inventory.get("nourriture", 0) < 5:
            return True

        # Vérifie les ressources pour le niveau suivant
        required_items = {
            1: {"linemate": 1},
            2: {"linemate": 1, "deraumere": 1, "sibur": 1},
            3: {"linemate": 2, "sibur": 1, "phiras": 2},
            4: {"linemate": 1, "deraumere": 1, "sibur": 2, "phiras": 1},
            5: {"linemate": 1, "deraumere": 2, "sibur": 1, "mendiane": 3},
            6: {"linemate": 1, "deraumere": 2, "sibur": 3, "phiras": 1},
            7: {"linemate": 2, "deraumere": 2, "sibur": 2, "mendiane": 2, "phiras": 2, "thystame": 1}
        }

        if self.level >= 8:
            return False

        required = required_items[self.level]
        for item, count in required.items():
            if self.inventory.get(item, 0) < count:
                return True
        return False

    def _find_resources(self) -> None:
        """Trouve et collecte des ressources."""
        # Cherche la ressource la plus proche
        target = self.vision.find_nearest_object("food")  # On commence par chercher de la nourriture
        if target == (-1, -1):  # Si pas de nourriture, on cherche d'autres ressources
            for resource in ["linemate", "deraumere", "sibur", "mendiane", "phiras", "thystame"]:
                target = self.vision.find_nearest_object(resource)
                if target != (-1, -1):
                    break
        
        if target != (-1, -1):
            self.target_position = target
            self._move_to_target()
        else:
            self._explore()

    def _check_collision(self) -> bool:
        """Vérifie si le joueur est bloqué (collision).
        
        Returns:
            bool: True si le joueur est bloqué
        """
        current_pos = self.vision.get_current_position()
        
        # Ajoute la position actuelle à l'historique
        self.last_positions.append(current_pos)
        
        # Garde seulement les 5 dernières positions
        if len(self.last_positions) > 5:
            self.last_positions.pop(0)
            
        # Vérifie si on est bloqué au même endroit
        if len(self.last_positions) >= 3:
            if all(pos == current_pos for pos in self.last_positions[-3:]):
                self.stuck_count += 1
                return True
                
        return False

    def _handle_collision(self) -> None:
        """Gère une collision en essayant de se débloquer."""
        if self.stuck_count > 3:
            # Si on est bloqué depuis trop longtemps, on essaie une autre direction
            self.logger.warning("Bloqué depuis trop longtemps, changement de direction")
            self.protocol.right()
            self.protocol.right()  # Tourne de 180 degrés
            self.stuck_count = 0
            self.last_positions.clear()
        else:
            # Essaie de se déplacer sur le côté
            self.protocol.right()
            self.protocol.forward()

    def _move_to_target(self) -> None:
        """Se déplace vers la position cible en gérant les collisions."""
        if not self.target_position:
            return

        # Vérifie les collisions
        if self.collision_manager.check_collision():
            self.collision_manager.handle_collision()
            return

        # Calcule la direction vers la cible
        current_pos = (0, 0)  # Position du joueur
        target_x, target_y = self.target_position
        
        # Détermine la direction à prendre
        if target_x > 0:
            self.protocol.right()
        elif target_x < 0:
            self.protocol.left()
        elif target_y > 0:
            self.protocol.forward()
            
            # Vérifie si on a atteint la cible
            vision = self.vision.look()
            for i, case in enumerate(vision):
                pos = self.vision.get_case_position(i)
                if pos == self.target_position:
                    self.target_position = None
                    self.collision_manager.reset()
                    break

    def _explore(self) -> None:
        """Explore la carte en évitant les collisions."""
        # Vérifie les collisions
        if self.collision_manager.check_collision():
            self.collision_manager.handle_collision()
            return

        # Avance dans une direction aléatoire
        self.protocol.forward()