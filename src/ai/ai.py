import logging
from typing import Dict, Optional, Tuple, List
from client import ZappyClient
from protocol import ZappyProtocol
from vision import Vision
from collision_manager import CollisionManager

class AI:
    def __init__(self, client: ZappyClient):
        """Initialise l'IA.
        
        Args:
            client (ZappyClient): Client connecté au serveur
        """
        self.client = client
        self.protocol = ZappyProtocol(client)
        self.vision = Vision()
        self.collision_manager = CollisionManager(self.protocol, self.vision)
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
            look_response = self.protocol.look()
            self.vision.update(look_response)
            
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
            # Format: "[nourriture X, linemate Y, deraumere Z, ...]"
            items = inventory_str.strip("[]").split(", ")
            self.inventory = {}
            for item in items:
                name, count = item.split(" ")
                self.inventory[name] = int(count)
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
        target = self.vision.find_nearest_resource()
        if target:
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
        direction = self.vision.get_direction_to_target(self.target_position)
        
        # Tourne si nécessaire
        if direction == "right":
            self.protocol.right()
        elif direction == "left":
            self.protocol.left()
        else:
            # Avance vers la cible
            self.protocol.forward()
            
            # Vérifie si on a atteint la cible
            if self.vision.is_at_target(self.target_position):
                self.target_position = None
                self.collision_manager.reset()

    def _explore(self) -> None:
        """Explore la carte en évitant les collisions."""
        # Vérifie les collisions
        if self.collision_manager.check_collision():
            self.collision_manager.handle_collision()
            return

        # Avance dans une direction aléatoire
        self.protocol.forward()