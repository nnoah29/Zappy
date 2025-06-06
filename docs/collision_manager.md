# Documentation Technique - Module CollisionManager

## Vue d'ensemble
Le module `CollisionManager` est responsable de la détection et de la résolution des collisions entre joueurs dans le jeu Zappy. Il implémente des stratégies d'évasion pour permettre aux joueurs de se déplacer efficacement même en présence d'autres joueurs.

## Structure du Code

### Classe CollisionManager

#### Initialisation
```python
def __init__(self, protocol: ZappyProtocol, vision: Vision, movement: Movement)
```
- **Paramètres**:
  - `protocol`: Instance de ZappyProtocol pour la communication
  - `vision`: Instance de Vision pour la perception
  - `movement`: Instance de Movement pour les déplacements
- **Attributs**:
  - `collision_count`: Nombre de collisions détectées
  - `last_collision_pos`: Position du dernier joueur en collision
  - `escape_attempts`: Nombre de tentatives d'évasion
  - `max_escape_attempts`: Nombre maximum de tentatives avant stratégie sévère

#### Méthodes Principales

##### check_collision()
```python
def check_collision() -> bool
```
Vérifie s'il y a une collision avec un autre joueur.
- **Retourne**: True si une collision est détectée
- **Comportement**:
  - Vérifie les joueurs dans le champ de vision
  - Détecte les joueurs directement devant
  - Met à jour les compteurs et positions

##### handle_collision()
```python
def handle_collision() -> bool
```
Gère une collision détectée en utilisant différentes stratégies.
- **Retourne**: True si la collision a été résolue
- **Stratégies**:
  1. Stratégie basique (moins de 3 tentatives)
  2. Stratégie sévère (3 tentatives ou plus)

##### _basic_escape_strategy()
```python
def _basic_escape_strategy() -> bool
```
Stratégie basique d'évasion de collision.
- **Retourne**: True si l'évasion a réussi
- **Séquence**:
  1. Tourne à droite
  2. Avance
  3. Si bloqué, tourne à gauche deux fois
  4. Avance à nouveau

##### _handle_severe_collision()
```python
def _handle_severe_collision() -> bool
```
Gère une collision sévère après plusieurs tentatives.
- **Retourne**: True si la collision a été résolue
- **Stratégie**:
  - Essaie les 4 directions successivement
  - Tourne et avance dans chaque direction
  - S'arrête dès qu'une direction fonctionne

##### reset()
```python
def reset() -> None
```
Réinitialise l'état du gestionnaire.
- **Effets**:
  - Réinitialise le compteur de collisions
  - Efface la dernière position de collision
  - Réinitialise les tentatives d'évasion

## Stratégies de Gestion des Collisions

### Stratégie Basique
1. Détection de collision
2. Tentative d'évasion à droite
3. Si échec, tentative d'évasion à gauche
4. Maximum 3 tentatives

### Stratégie Sévère
1. Déclenchée après 3 échecs
2. Exploration systématique des 4 directions
3. Priorité à la première direction libre
4. Réinitialisation après succès

## Gestion des États

### Compteurs
- `collision_count`: Suivi du nombre total de collisions
- `escape_attempts`: Suivi des tentatives d'évasion
- `max_escape_attempts`: Limite pour la stratégie sévère

### Positions
- `last_collision_pos`: Mémorisation de la dernière collision
- Utilisé pour éviter les zones problématiques

## Bonnes Pratiques

### Détection
- Vérification régulière des collisions
- Utilisation du champ de vision
- Détection proactive

### Évasion
- Stratégies progressives
- Réinitialisation après succès
- Gestion des échecs

### Performance
- Limitation des tentatives
- Stratégies optimisées
- Évitation des boucles infinies

## Exemples d'Utilisation

### Détection Simple
```python
if collision_manager.check_collision():
    collision_manager.handle_collision()
```

### Gestion Avancée
```python
if collision_manager.check_collision():
    if not collision_manager.handle_collision():
        # Stratégie de secours
        collision_manager.reset()
        # Nouvelle tentative
```

## Dépannage

### Problèmes Courants
1. **Collisions répétées**
   - Vérifier la stratégie d'évasion
   - Augmenter max_escape_attempts
   - Améliorer la détection

2. **Échecs d'évasion**
   - Vérifier les commandes de mouvement
   - Ajuster les stratégies
   - Implémenter des stratégies alternatives

3. **Performances**
   - Optimiser les vérifications
   - Réduire les tentatives inutiles
   - Améliorer la prise de décision

### Solutions
- Logs détaillés
- Tests unitaires
- Stratégies alternatives
- Ajustement des paramètres 