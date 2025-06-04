# Documentation Technique - Module Vision

## Vue d'ensemble
Le module `Vision` est responsable de la perception et de l'analyse de l'environnement du joueur dans le jeu Zappy. Il traite les données de vision reçues du serveur et les convertit en informations exploitables par l'IA pour la prise de décision.

## Structure du Code

### Classe Vision

#### Initialisation
```python
def __init__(self, protocol: ZappyProtocol)
```
- **Paramètres**:
  - `protocol`: Instance de ZappyProtocol pour la communication
- **Attributs**:
  - `self.protocol`: Protocole de communication
  - `self.level`: Niveau actuel du joueur (défaut: 1)

#### Méthodes Principales

##### look()
```python
def look() -> List[Dict[str, int]]
```
Envoie la commande look au serveur et analyse la réponse.
- **Retourne**: Liste de dictionnaires représentant le contenu de chaque case
- **Format de retour**: `[{"player": 1}, {"food": 1}, {}, ...]`

##### parse_vision()
```python
def parse_vision(vision_data: str) -> List[Dict[str, int]]
```
Parse les données de vision brutes reçues du serveur.
- **Paramètres**:
  - `vision_data`: Chaîne de caractères au format "[case1, case2, ...]"
- **Retourne**: Liste de dictionnaires représentant le contenu de chaque case

##### get_case_position()
```python
def get_case_position(index: int) -> Tuple[int, int]
```
Calcule la position relative d'une case par rapport au joueur.
- **Paramètres**:
  - `index`: Index de la case dans la grille
- **Retourne**: Tuple (x, y) représentant la position relative
- **Logique**:
  - Grille carrée de taille 2*level × 2*level
  - Le joueur est au centre de la grille
  - Coordonnées relatives au joueur

##### find_nearest_object()
```python
def find_nearest_object(object_type: str) -> Tuple[int, int]
```
Trouve l'objet le plus proche du type spécifié.
- **Paramètres**:
  - `object_type`: Type d'objet à rechercher
- **Retourne**: Position (x, y) de l'objet le plus proche ou (-1, -1) si non trouvé

##### get_players_in_vision()
```python
def get_players_in_vision() -> List[Tuple[int, int]]
```
Retourne la liste des positions des joueurs dans le champ de vision.
- **Retourne**: Liste de tuples (x, y) représentant les positions des joueurs

##### set_level()
```python
def set_level(level: int) -> None
```
Met à jour le niveau du joueur.
- **Paramètres**:
  - `level`: Nouveau niveau du joueur

##### get_expected_vision_size()
```python
def get_expected_vision_size() -> int
```
Calcule le nombre de cases attendues pour le niveau actuel.
- **Retourne**: Nombre de cases (4 × level²)

## Format des Données

### Vision
- Format brut: `"[case1, case2, case3, ...]"`
- Format parsé: Liste de dictionnaires
- Exemple: `[{"player": 1}, {"food": 1}, {}, {"player": 1, "deraumere": 1}]`

### Positions
- Format: Tuple (x, y)
- Origine: Position du joueur (0, 0)
- Axes:
  - x: positif vers la droite
  - y: positif vers le bas

## Logique de la Grille

### Niveau 1 (2×2)
```
(-1,-1) (0,-1)
(-1,0)  (0,0)  <- Joueur
```

### Niveau 2 (4×4)
```
(-2,-2) (-1,-2) (0,-2)  (1,-2)
(-2,-1) (-1,-1) (0,-1)  (1,-1)
(-2,0)  (-1,0)  (0,0)   (1,0)   <- Joueur
(-2,1)  (-1,1)  (0,1)   (1,1)
```

## Tests
Les tests unitaires couvrent :
- Calcul de la taille de vision
- Calcul des positions des cases
- Parsing des données de vision
- Recherche d'objets
- Détection des joueurs

## Dépendances
- `typing`: Pour les annotations de type
- `protocol`: Module ZappyProtocol pour la communication 