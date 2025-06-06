# Documentation du Gestionnaire de Collisions

## Vue d'ensemble
Le gestionnaire de collisions (`CollisionManager`) est responsable de la détection et de la résolution des situations où le joueur est bloqué. Il utilise un système de suivi des positions et de comptage des blocages pour prendre des décisions appropriées.

## Fonctionnalités principales

### Détection de collision
- Suivi des positions récentes
- Détection des blocages répétés
- Comptage des tentatives de déblocage

### Résolution de collision
- Tentatives de déplacement latéral
- Changement de direction en cas de blocage prolongé
- Réinitialisation de l'état

## Détails techniques

### Variables d'état
- `last_positions`: Liste des dernières positions (max 5)
- `stuck_count`: Nombre de blocages consécutifs
- `max_stuck_count`: Seuil de blocage sévère (3)
- `position_history_size`: Taille de l'historique (5)

### Méthodes principales

#### check_collision
```python
def check_collision(self) -> bool:
    """Vérifie si le joueur est bloqué.
    
    Returns:
        bool: True si le joueur est bloqué
    """
```
- Vérifie les 3 dernières positions
- Incrémente le compteur de blocage si nécessaire
- Retourne True si un blocage est détecté

#### handle_collision
```python
def handle_collision(self) -> None:
    """Gère une collision en essayant de se débloquer."""
```
- Change de direction si blocage sévère
- Tente un déplacement latéral sinon
- Réinitialise l'état si nécessaire

#### reset
```python
def reset(self) -> None:
    """Réinitialise l'état du gestionnaire."""
```
- Remet à zéro le compteur de blocage
- Vide l'historique des positions

## Stratégies de déblocage

### Blocage normal
1. Tourne à droite
2. Avance
3. Incrémente le compteur

### Blocage sévère
1. Tourne de 180 degrés
2. Réinitialise l'état
3. Change de direction

## Bonnes pratiques

### Détection
- Maintenir un historique suffisant
- Vérifier les positions consécutives
- Éviter les faux positifs

### Résolution
- Essayer des solutions simples d'abord
- Changer de stratégie si nécessaire
- Réinitialiser l'état au bon moment

### Performance
- Limiter la taille de l'historique
- Optimiser les calculs de position
- Éviter les opérations redondantes

## Exemples d'utilisation

### Détection de blocage
```python
if collision_manager.check_collision():
    collision_manager.handle_collision()
```

### Réinitialisation
```python
# Après un déplacement réussi
collision_manager.reset()
```

### Vérification d'état
```python
if collision_manager.is_severely_stuck():
    # Changer de stratégie
```

## Dépannage

### Problèmes courants
1. **Fausses détections**
   - Vérifier la taille de l'historique
   - Ajuster les seuils
   - Améliorer la précision

2. **Déblocage inefficace**
   - Vérifier les stratégies
   - Ajuster les paramètres
   - Ajouter des logs

3. **Performance**
   - Optimiser les calculs
   - Réduire la taille de l'historique
   - Améliorer l'algorithme

### Solutions
- Ajouter des logs détaillés
- Ajuster les paramètres
- Implémenter des stratégies alternatives 