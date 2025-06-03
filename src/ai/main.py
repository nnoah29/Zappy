#!/usr/bin/env python3

import argparse
import logging
from client import ZappyClient

def parse_args():
    parser = argparse.ArgumentParser(description='Zappy AI Client')
    parser.add_argument('-p', '--port', type=int, required=True,
                      help='Port de connexion')
    parser.add_argument('-n', '--name', type=str, required=True,
                      help='Nom de l\'équipe')
    parser.add_argument('-h', '--hostname', type=str, default='localhost',
                      help='Hostname du serveur (default: localhost)')
    return parser.parse_args()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    args = parse_args()
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        client = ZappyClient(args.hostname, args.port, args.name)
        client.connect()
        client.run()
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return 84

if __name__ == "__main__":
    exit(main()) 