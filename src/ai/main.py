#!/usr/bin/env python3

import sys
import argparse
import logging
import signal
import time
from typing import Optional
from client import ZappyClient
from protocol import ZappyProtocol
from ai import AI

def setup_logging() -> None:
    """Configure le système de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('zappy.log')
        ]
    )

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