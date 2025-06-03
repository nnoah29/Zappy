class ZappyProtocol:
    def __init__(self, client):
        """Initialise le protocole avec un client."""
        self.client = client

    def _handle_response(self, response: str) -> bool:
        """Gère la réponse du serveur.
        
        Args:
            response (str): Réponse du serveur
            
        Returns:
            bool: True si la commande a réussi, False sinon
        """
        if response == "ok":
            return True
        elif response == "ko":
            return False
        else:
            raise ValueError(f"Réponse invalide du serveur: {response}")

    def forward(self) -> bool:
        """Avance d'une case.
        
        Returns:
            bool: True si le mouvement a réussi, False sinon
        """
        self.client._send("Forward\n")
        response = self.client._receive().strip()
        return self._handle_response(response)

    def right(self) -> bool:
        """Tourne à droite.
        
        Returns:
            bool: True si la rotation a réussi, False sinon
        """
        self.client._send("Right\n")
        response = self.client._receive().strip()
        return self._handle_response(response)

    def left(self) -> bool:
        """Tourne à gauche.
        
        Returns:
            bool: True si la rotation a réussi, False sinon
        """
        self.client._send("Left\n")
        response = self.client._receive().strip()
        return self._handle_response(response)

    def look(self) -> str:
        """Regarde autour du joueur.
        
        Returns:
            str: Réponse brute du serveur
        """
        self.client._send("Look\n")
        return self.client._receive().strip()

    def inventory(self) -> str:
        """Consulte l'inventaire.
        
        Returns:
            str: Réponse brute du serveur
        """
        self.client._send("Inventory\n")
        return self.client._receive().strip()

    def broadcast(self, message: str) -> bool:
        """Envoie un message à tous les joueurs.
        
        Args:
            message (str): Message à envoyer
            
        Returns:
            bool: True si le message a été envoyé, False sinon
        """
        self.client._send(f"Broadcast {message}\n")
        response = self.client._receive().strip()
        return self._handle_response(response)

    def connect_nbr(self) -> int:
        """Demande le nombre de places disponibles dans l'équipe.
        
        Returns:
            int: Nombre de places disponibles
        """
        self.client._send("Connect_nbr\n")
        response = self.client._receive().strip()
        return int(response)

    def fork(self) -> bool:
        """Pond un œuf.
        
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        self.client._send("Fork\n")
        response = self.client._receive().strip()
        return self._handle_response(response)

    def eject(self) -> bool:
        """Expulse les joueurs de la case.
        
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        self.client._send("Eject\n")
        response = self.client._receive().strip()
        return self._handle_response(response)

    def take(self, object_name: str) -> bool:
        """Prend un objet.
        
        Args:
            object_name (str): Nom de l'objet à prendre
            
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        self.client._send(f"Take {object_name}\n")
        response = self.client._receive().strip()
        return self._handle_response(response)

    def set(self, object_name: str) -> bool:
        """Pose un objet.
        
        Args:
            object_name (str): Nom de l'objet à poser
            
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        self.client._send(f"Set {object_name}\n")
        response = self.client._receive().strip()
        return self._handle_response(response)

    def incantation(self) -> int:
        """Commence un rituel d'élévation.
        
        Returns:
            int: Niveau atteint après l'élévation, -1 si échec
        """
        self.client._send("Incantation\n")
        response = self.client._receive().strip()
        if response != "Elevation underway":
            return -1
        level_response = self.client._receive().strip()
        return int(level_response.split(": ")[1]) 