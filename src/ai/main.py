#!/usr/bin/env python3

import sys
import argparse
from client import ZappyClient
from protocol import ZappyProtocol

def parse_args():
    """Passe les arguments en ligne de commande"""
    parser = argparse.ArgumentParser(description='Zappy AI Client', add_help=False)
    parser.add_argument('-p', '--port', type=int, required=True, help='Port number')
    parser.add_argument('-n', '--name', type=str, required=True, help='Team name')
    parser.add_argument('-h', '--host', type=str, default="localhost", help='Machine name')
    
    if (len(sys.argv) == 2 and sys.argv[1] == "-help"):
        print("USAGE: ./zappy_ai -p port -n name -h machine")
        sys.exit(0)
    if (len(sys.argv) == 1):
        print("Type ./zappy_ai -help for usage")
        sys.exit(84)
    return parser.parse_args()

def main():
    try:
        args = parse_args()
        
        # Création du client et du protocal
        client = ZappyClient(args.host, args.port, args.name)
        protocol = ZappyProtocol(client)
        
        # Connection au serveur
        client.connect()
        
        # Envoi du nom d'équipe
        client.send(args.name)
        
        
        # gardons la connexion en ligne pour ne pas la perdre
        while True:
            response = client.receive()
            if not response:
                break
            print(f"Received: {response}")
            
    except Exception as e:
        sys.exit(84)
    finally:
        if 'client' in locals():
            client.close()
    return 0

if __name__ == "__main__":
    main()