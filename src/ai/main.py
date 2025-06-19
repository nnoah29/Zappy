#!/usr/bin/env python3

import sys
import argparse
import logging
import signal
import time
from typing import Optional
from core.client import ZappyClient
from core.protocol import ZappyProtocol
from models.player import Player
from models.map import Map
from ai import AI

def setup_logging():
    """Configure le système de logging."""
    file_handler = logging.FileHandler('zappy.log', mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    loggers = ['core.client', 'core.protocol', 'models.player', 'models.map', 'managers.vision_manager', 
              'managers.movement_manager', 'managers.inventory_manager', 'managers.elevation_manager']
              
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True
        
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.propagate = True
    
    logger.debug("Configuration du logging terminée. Fichier zappy.log créé.")
    logger.info("Niveau de logging configuré à DEBUG pour tous les modules.")
    
    return logger

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
        args = parse_args()
        logger = setup_logging()
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        
        client = ZappyClient(args.host, args.port, args.name)
        try:
            client.connect()
            
            protocol = ZappyProtocol(client)
            
            player = Player(
                id=client.client_num,
                team=client.team_name,
                x=client.map_size[0] // 2,
                y=client.map_size[1] // 2,
                protocol=protocol,
                logger=logger
            )
            game_map = Map(client.map_size[0], client.map_size[1])
            
            client.ai = AI(protocol, player, game_map, logger)
            
        except Exception as e:
            logger.error(f"Échec de la connexion au serveur: {e}")
            return 84

        while True:
            try:
                if not client.run():
                    logger.info("Arrêt de l'IA.")
                    break
                
                if hasattr(client.ai, 'state') and client.ai.state == "EMERGENCY_FOOD_SEARCH":
                    time.sleep(0.1)
                else:
                    time.sleep(0.2)
                    
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