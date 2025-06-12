#!/usr/bin/env python3

import sys
import argparse
import logging
import signal
import time
from typing import Optional
from core.client import ZappyClient
from ai import AI

def setup_logging() -> None:
    """Configure le système de logging."""
    # Configuration du logging pour tous les modules
    for logger_name in ['root', 'client', 'ai', 'protocol', 'vision']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # Supprime les handlers existants pour éviter les doublons
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Ajoute les handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler pour le fichier
        file_handler = logging.FileHandler('zappy.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logging.debug("Configuration du logging terminée. Fichier zappy.log créé.")
    logging.info("Niveau de logging configuré à DEBUG pour tous les modules.")

def parse_args() -> argparse.Namespace:
    """Parse les arguments en ligne de commande.
    
    Returns:
        argparse.Namespace: Arguments parsés
    """
    parser = argparse.ArgumentParser(description='Zappy AI Client', add_help=False)
    parser.add_argument('-p', '--port', type=int, required=True, help='Port number')
    parser.add_argument('-n', '--name', type=str, required=True, help='Team name')
    parser.add_argument('-h', '--host', type=str, default="localhost", help='Machine name')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    if len(sys.argv) == 2 and sys.argv[1] == "-help":
        print("USAGE: ./zappy_ai -p port -n name -h machine")
        sys.exit(0)
    if len(sys.argv) == 1:
        print("Type ./zappy_ai -help for usage")
        sys.exit(84)
    return parser.parse_args()

def handle_signal(signum: int, frame: Optional[object]) -> None:
    """Gère les signaux système.
    
    Args:
        signum (int): Numéro du signal
        frame (Optional[object]): Frame d'exécution
    """
    logging.info(f"Signal {signum} reçu, arrêt du programme...")
    sys.exit(0)

def main() -> int:
    """Point d'entrée principal du programme.
    
    Returns:
        int: Code de sortie
    """
    try:
        # Configuration
        args = parse_args()
        setup_logging()
        logger = logging.getLogger(__name__)
        
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        
        client = ZappyClient(args.host, args.port, args.name)
        
        try:
            client.connect()
        except Exception as e:
            logger.error(f"Échec de la connexion au serveur: {e}")
            return 84
        
        ai = AI(client)
        
        while True:
            try:
                ai.update()
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle principale: {e}")
                break
                
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        return 84
    finally:
        if 'client' in locals():
            client.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())