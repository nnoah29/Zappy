# Documentation Technique - Module Protocol

## Vue d'ensemble
Le module `Protocol` gère la communication entre le client et le serveur Zappy. Il implémente toutes les commandes du protocole de communication et gère les réponses du serveur. Ce module est essentiel pour assurer une communication fiable et robuste avec le serveur de jeu.

## Structure du Code

### Classe ZappyProtocol

#### Initialisation
```python
def __init__(self, client)
```
- **Paramètres**:
  - `client`: Instance du client Zappy
- **Attributs**:
  - `self.client`: Client Zappy pour la communication

#### Méthodes de Communication

##### forward()
```python
def forward() -> bool
```
Avance d'une case.
- **Retourne**: True si le mouvement a réussi
- **Comportement**:
  - Envoie la commande "Forward"
  - Attend la réponse du serveur
  - Retourne True si "ok", False si "ko"

##### right()
```python
def right() -> bool
```
Tourne à droite.
- **Retourne**: True si la rotation a réussi
- **Comportement**:
  - Envoie la commande "Right"
  - Attend la réponse du serveur
  - Retourne True si "ok", False si "ko"

##### left()
```python
def left() -> bool
```
Tourne à gauche.
- **Retourne**: True si la rotation a réussi
- **Comportement**:
  - Envoie la commande "Left"
  - Attend la réponse du serveur
  - Retourne True si "ok", False si "ko"

##### look()
```python
def look() -> str
```
Regarde autour du joueur.
- **Retourne**: Description des cases visibles
- **Format**: "[case1, case2, case3, ...]"

##### inventory()
```python
def inventory() -> str
```
Vérifie l'inventaire.
- **Retourne**: Contenu de l'inventaire
- **Format**: "[nourriture X, linemate Y, ...]"

##### take()
```python
def take(object_name: str) -> bool
```
Prend un objet.
- **Paramètres**:
  - `object_name`: Type d'objet à prendre
- **Retourne**: True si la prise a réussi

##### set()
```python
def set(object_name: str) -> bool
```
Pose un objet.
- **Paramètres**:
  - `object_name`: Type d'objet à poser
- **Retourne**: True si le dépôt a réussi

##### broadcast()
```python
def broadcast(message: str) -> bool
```
Envoie un message à tous les joueurs.
- **Paramètres**:
  - `message`: Message à envoyer
- **Retourne**: True si l'envoi a réussi

##### incantation()
```python
def incantation() -> int
```
Démarre une incantation.
- **Retourne**: Niveau atteint après l'élévation, -1 si échec

##### fork()
```python
def fork() -> bool
```
Fork un nouveau joueur.
- **Retourne**: True si le fork a réussi

##### connect_nbr()
```python
def connect_nbr() -> int
```
Demande le nombre de slots disponibles.
- **Retourne**: Nombre de slots disponibles

## Format des Messages

### Commandes
- Format: `commande\n`
- Exemples:
  - `forward\n`
  - `take food\n`
  - `broadcast message\n`

### Réponses
- Format: `réponse\n`
- Exemples:
  - `ok\n`
  - `ko\n`
  - `[player, food, , player deraumere]\n`

## Gestion des Erreurs
- Timeout: 5 secondes par défaut
- Reconnexion automatique en cas d'erreur
- Buffer pour les messages partiels

## Tests
Les tests unitaires couvrent :
- Connexion/Déconnexion
- Envoi/Réception de commandes
- Gestion des erreurs
- Parsing des réponses

## Dépendances
- `socket`: Pour la communication réseau
- `typing`: Pour les annotations de type 