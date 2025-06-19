# reproduction_manager.py
import time
import logging
from core.protocol import ZappyProtocol

class ReproductionManager:
    """Gère la logique de reproduction (fork) du joueur."""

    def __init__(self, protocol: ZappyProtocol, logger: logging.Logger):
        """
        Args:
            protocol (ZappyProtocol): Protocole de communication avec le serveur
            logger (Logger): Logger pour le debug
        """
        self.protocol = protocol
        self.logger = logger
        self.last_fork_time = 0
        self.cooldown = 42  # 42/f où f = 100 par défaut

    def can_fork(self) -> bool:
        """Vérifie si le joueur peut exécuter un fork maintenant.
        Returns:
            bool: True si la commande Fork est autorisée
        """
        return time.time() - self.last_fork_time > self.cooldown

    def reproduce(self) -> bool:
        """Effectue une commande Fork si possible.
        Retour type:
            bool: True si le fork a réussi, False sinon
        """
        if not self.can_fork():
            self.logger.debug("Cooldown actif, fork non autorisé pour le moment.")
            return False
        try:
            self.logger.info("Tentative de fork (reproduction)")
            success = self.protocol.fork()
            if success:
                self.last_fork_time = time.time()
                self.logger.info("🥚 Fork réussi (œuf pondu)")
                return True
            else:
                self.logger.warning("❌ Fork échoué")
                return False
        except Exception as e:
            self.logger.error(f"Erreur lors du fork: {str(e)}")
            return False
