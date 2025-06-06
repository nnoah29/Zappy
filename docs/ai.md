# Documentation de l'IA Zappy

## Vue d'ensemble
L'IA Zappy est le cerveau du joueur. Elle gère la prise de décision, la navigation, la collecte de ressources et l'évolution du joueur. Elle utilise plusieurs composants (vision, protocole, collision) pour prendre des décisions optimales.

## Fonctionnalités principales

### Gestion d'état
- Suivi du niveau
- Gestion de l'inventaire
- Suivi des positions
- Détection des collisions

### Prise de décision
- Évaluation des besoins
- Recherche de ressources
- Navigation vers les objectifs
- Gestion des priorités

### Évolution
- Vérification des conditions de niveau
- Gestion des incantations
- Collecte des ressources nécessaires
- Coordination avec l'équipe

## Détails techniques

### Variables d'état
- `level`: Niveau actuel du joueur
- `inventory`: Contenu de l'inventaire
- `current_action`: Action en cours
- `target_position`: Position cible
- `last_positions`: Historique des positions
- `stuck_count`: Compteur de blocages

### Méthodes principales

#### update
```python
def update(self) -> None:
    """Met à jour l'état de l'IA et prend une décision."""
```
- Met à jour la vision
- Met à jour l'inventaire
- Prend une décision

#### _make_decision
```python
def _make_decision(self) -> None:
    """Prend une décision basée sur l'état actuel."""
```
- Vérifie les conditions de niveau
- Cherche des ressources
- Explore la carte
- Se déplace vers l'objectif

#### _can_level_up
```python
def _can_level_up(self) -> bool:
    """Vérifie si le joueur peut monter de niveau."""
```
- Vérifie les ressources nécessaires
- Vérifie le niveau actuel
- Retourne True si possible

## Stratégies

### Collecte de ressources
1. Vérifie les besoins
2. Cherche les ressources proches
3. Se déplace vers la ressource
4. Collecte la ressource

### Navigation
1. Calcule la direction vers l'objectif
2. Gère les collisions
3. Se déplace progressivement
4. Vérifie l'arrivée

### Exploration
1. Avance dans une direction
2. Évite les collisions
3. Découvre de nouvelles zones
4. Collecte les ressources trouvées

## Conditions de niveau

### Niveau 1
- 1 linemate

### Niveau 2
- 1 linemate
- 1 deraumere
- 1 sibur

### Niveau 3
- 2 linemate
- 1 sibur
- 2 phiras

### Niveau 4
- 1 linemate
- 1 deraumere
- 2 sibur
- 1 phiras

### Niveau 5
- 1 linemate
- 2 deraumere
- 1 sibur
- 3 mendiane

### Niveau 6
- 1 linemate
- 2 deraumere
- 3 sibur
- 1 phiras

### Niveau 7
- 2 linemate
- 2 deraumere
- 2 sibur
- 2 mendiane
- 2 phiras
- 1 thystame

## Bonnes pratiques

### Gestion des ressources
- Maintenir un stock de nourriture
- Collecter les ressources rares
- Optimiser les déplacements

### Navigation
- Éviter les collisions
- Optimiser les chemins
- Gérer les impasses

### Évolution
- Vérifier les conditions
- Coordonner les actions
- Gérer les échecs

## Exemples d'utilisation

### Mise à jour de l'IA
```python
try:
    ai.update()
except Exception as e:
    logger.error(f"Erreur: {e}")
```

### Vérification de niveau
```python
if ai._can_level_up():
    ai._start_level_up()
```

### Recherche de ressources
```python
if ai._need_resources():
    ai._find_resources()
```

## Dépannage

### Problèmes courants
1. **Blocages fréquents**
   - Vérifier la gestion des collisions
   - Améliorer la navigation
   - Ajuster les stratégies

2. **Ressources manquantes**
   - Améliorer la détection
   - Optimiser les chemins
   - Ajuster les priorités

3. **Échecs d'incantation**
   - Vérifier les conditions
   - Améliorer la coordination
   - Gérer les timeouts

### Solutions
- Ajouter des logs détaillés
- Implémenter des stratégies alternatives
- Améliorer la robustesse 