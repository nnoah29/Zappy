# Documentation Technique - Module Movement

## Vue d'ensemble
Le module `Movement` gère les déplacements du joueur dans le jeu Zappy. Il implémente un système de navigation qui permet de calculer et d'exécuter des chemins vers des positions cibles, tout en gérant les blocages potentiels.

## Structure du Code

### Classe Movement

#### Initialisation
```python
def __init__(self, protocol: ZappyProtocol, vision: Vision)
```
- **Paramètres**:
  - `protocol`: Instance de ZappyProtocol pour la communication
  - `vision`: Instance de Vision pour la perception
- **Attributs**:
  - `current_direction`: Direction actuelle (0: Nord, 1: Est, 2: Sud, 3: Ouest)
  - `last_positions`: Historique des dernières positions
  - `stuck_count`: Compteur de blocages

#### Méthodes Principales

##### move_to_position()
```python
def move_to_position(target_pos: Tuple[int, int]) -> bool
```
Déplace le joueur vers une position cible.
- **Paramètres**:
  - `target_pos`: Position cible (x, y)
- **Retourne**: True si le mouvement a réussi
- **Séquence**:
  1. Vérifie l'accessibilité
  2. Calcule le chemin
  3. Exécute le chemin

##### _is_position_accessible()
```python
def _is_position_accessible(pos: Tuple[int, int]) -> bool
```
Vérifie si une position est accessible.
- **Paramètres**:
  - `pos`: Position à vérifier
- **Retourne**: True si la position est accessible
- **Vérifications**:
  - Position dans le champ de vision
  - Absence d'obstacles

##### _calculate_path()
```python
def _calculate_path(target_pos: Tuple[int, int]) -> List[str]
```
Calcule le chemin vers la cible.
- **Paramètres**:
  - `target_pos`: Position cible
- **Retourne**: Liste des commandes à exécuter
- **Stratégie**:
  1. Calcul des différences X/Y
  2. Rotation vers la bonne direction
  3. Déplacement en ligne droite

##### _rotate_to_direction()
```python
def _rotate_to_direction(target_direction: int) -> List[str]
```
Calcule les rotations nécessaires.
- **Paramètres**:
  - `target_direction`: Direction cible
- **Retourne**: Liste des commandes de rotation
- **Logique**:
  - Calcul de la différence de direction
  - Choix du chemin le plus court

##### _execute_path()
```python
def _execute_path(path: List[str]) -> bool
```
Exécute une séquence de commandes.
- **Paramètres**:
  - `path`: Liste des commandes
- **Retourne**: True si exécution réussie
- **Vérifications**:
  - Exécution des commandes
  - Détection de blocage

##### _is_stuck()
```python
def _is_stuck() -> bool
```
Vérifie si le joueur est bloqué.
- **Retourne**: True si le joueur est bloqué
- **Critères**:
  - Même position 3 fois de suite
  - Historique des 5 dernières positions

##### reset_stuck_counter()
```python
def reset_stuck_counter() -> None
```
Réinitialise le compteur de blocage.
- **Effets**:
  - Remise à zéro du compteur
  - Vidage de l'historique

## Système de Navigation

### Directions
- 0: Nord
- 1: Est
- 2: Sud
- 3: Ouest

### Calcul de Chemin
1. **Analyse de la Position**
   - Position actuelle (0,0)
   - Position cible (x,y)
   - Différences dx, dy

2. **Planification**
   - Déplacement en X d'abord
   - Déplacement en Y ensuite
   - Rotations minimales

3. **Exécution**
   - Commandes séquentielles
   - Vérification de blocage
   - Gestion des erreurs

## Gestion des Blocages

### Détection
- Historique de 5 positions
- Détection de répétition
- Compteur de blocages

### Prévention
- Vérification d'accessibilité
- Calcul de chemins alternatifs
- Réinitialisation du compteur

## Bonnes Pratiques

### Navigation
- Vérification préalable
- Chemins optimisés
- Gestion des erreurs

### Performance
- Historique limité
- Calculs optimisés
- Détection proactive

### Sécurité
- Vérification des obstacles
- Gestion des blocages
- Réinitialisation appropriée

## Exemples d'Utilisation

### Déplacement Simple
```python
if movement.move_to_position((2, 3)):
    print("Déplacement réussi")
else:
    print("Échec du déplacement")
```

### Gestion des Blocages
```python
if movement._is_stuck():
    movement.reset_stuck_counter()
    # Nouvelle tentative
```

## Dépannage

### Problèmes Courants
1. **Blocages répétés**
   - Vérifier l'accessibilité
   - Ajuster la stratégie
   - Augmenter la tolérance

2. **Chemins inefficaces**
   - Optimiser le calcul
   - Réduire les rotations
   - Améliorer la planification

3. **Erreurs d'exécution**
   - Vérifier les commandes
   - Gérer les timeouts
   - Implémenter des retries

### Solutions
- Logs détaillés
- Tests unitaires
- Stratégies alternatives
- Ajustement des paramètres 