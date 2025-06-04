# Documentation Technique - Module ZappyClient

## Vue d'ensemble
Le module `ZappyClient` est responsable de la gestion de la connexion réseau avec le serveur Zappy. Il gère l'établissement de la connexion, l'authentification et la communication de base avec le serveur. Ce module est le fondement de la communication entre l'agent et le serveur de jeu.

## Structure du Code

### Classe ZappyClient

#### Initialisation
```python
def __init__(self, hostname: str, port: int, team_name: str)
```
- **Paramètres**:
  - `hostname`: Nom d'hôte du serveur
  - `port`: Port du serveur
  - `team_name`: Nom de l'équipe
- **Attributs**:
  - `self.hostname`: Nom d'hôte du serveur
  - `self.port`: Port du serveur
  - `self.team_name`: Nom de l'équipe
  - `self.socket`: Socket de connexion
  - `self.logger`: Logger pour les messages de debug
  - `self.map_size`: Taille de la carte
  - `self.client_num`: Numéro du client

#### Méthodes Principales

##### connect()
```python
def connect() -> None
```
Établit la connexion avec le serveur et effectue le protocole d'authentification.
- **Comportement**:
  - Création du socket
  - Connexion au serveur
  - Réception du message de bienvenue
  - Envoi du nom d'équipe
  - Réception du numéro de client
  - Réception de la taille de la carte
- **Exceptions**:
  - `ConnectionError`: Si la connexion échoue
  - `Exception`: Si le protocole d'authentification échoue

##### _send()
```python
def _send(message: str) -> None
```
Envoie un message au serveur.
- **Paramètres**:
  - `message`: Message à envoyer
- **Exceptions**:
  - `socket.error`: Si l'envoi échoue

##### _receive()
```python
def _receive() -> str
```
Reçoit un message du serveur.
- **Retourne**: Message reçu
- **Exceptions**:
  - `socket.error`: Si la réception échoue
  - `Exception`: Si la connexion est fermée

##### run()
```python
def run() -> None
```
Boucle principale du client.
- **Comportement**:
  - Boucle infinie de communication
  - Gestion des messages
  - Gestion des erreurs
- **Exceptions**:
  - `Exception`: En cas d'erreur dans la boucle

##### close()
```python
def close() -> None
```
Ferme la connexion avec le serveur.
- **Comportement**:
  - Fermeture du socket
  - Réinitialisation des attributs

## Gestion des Erreurs

### Logging
- Configuration du logging avec format détaillé
- Niveau de log: INFO
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### Types d'Erreurs
- Erreurs de connexion
- Erreurs d'envoi/réception
- Erreurs de protocole
- Déconnexions inattendues

## Protocole d'Authentification
1. Connexion au serveur
2. Réception de "WELCOME"
3. Envoi du nom d'équipe
4. Réception du numéro de client
5. Réception de la taille de la carte

## Tests
Les tests unitaires couvrent :
- Connexion au serveur
- Authentification
- Envoi de messages
- Réception de messages
- Gestion des erreurs
- Fermeture de connexion

## Dépendances
- `socket`: Pour la communication réseau
- `logging`: Pour la gestion des logs
- `typing`: Pour les annotations de type 