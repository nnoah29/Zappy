class ZappyProtocol:
    def __init__(self, client):
        """Initialise le protocole avec un client."""
        self.client = client

    def forward(self) -> bool:
        """Avance d'une case."""
        self.client._send("Forward\n")
        return self.client._receive().strip() == "ok"

    def right(self) -> bool:
        """Tourne à droite."""
        self.client._send("Right\n")
        return self.client._receive().strip() == "ok"

    def left(self) -> bool:
        """Tourne à gauche."""
        self.client._send("Left\n")
        return self.client._receive().strip() == "ok"

    def look(self) -> str:
        """Regarde autour du joueur."""
        self.client._send("Look\n")
        return self.client._receive().strip()

    def inventory(self) -> str:
        """Consulte l'inventaire."""
        self.client._send("Inventory\n")
        return self.client._receive().strip()

    def broadcast(self, message: str) -> bool:
        """Envoie un message à tous les joueurs."""
        self.client._send(f"Broadcast {message}\n")
        return self.client._receive().strip() == "ok"

    def connect_nbr(self) -> int:
        """Demande le nombre de places disponibles dans l'équipe."""
        self.client._send("Connect_nbr\n")
        return int(self.client._receive().strip())

    def fork(self) -> bool:
        """Pond un œuf."""
        self.client._send("Fork\n")
        return self.client._receive().strip() == "ok"

    def eject(self) -> bool:
        """Expulse les joueurs de la case."""
        self.client._send("Eject\n")
        return self.client._receive().strip() == "ok"

    def take(self, object_name: str) -> bool:
        """Prend un objet."""
        self.client._send(f"Take {object_name}\n")
        return self.client._receive().strip() == "ok"

    def set(self, object_name: str) -> bool:
        """Pose un objet."""
        self.client._send(f"Set {object_name}\n")
        return self.client._receive().strip() == "ok"

    def incantation(self) -> int:
        """Commence un rituel d'élévation."""
        self.client._send("Incantation\n")
        response = self.client._receive().strip()
        if response != "Elevation underway":
            return -1
        level_response = self.client._receive().strip()
        return int(level_response.split(": ")[1]) 