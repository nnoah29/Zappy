# Système d'Élévation

## Description
Le système d'élévation permet aux joueurs de monter en niveau en effectuant des rituels. Ces rituels nécessitent la présence d'un certain nombre de joueurs du même niveau et de ressources spécifiques sur la même case.

## Conditions d'Élévation

### Niveau 1 → 2
- 1 joueur
- 1 linemate
- 0 deraumere
- 0 sibur
- 0 mendiane
- 0 phiras
- 0 thystame

### Niveau 2 → 3
- 2 joueurs
- 1 linemate
- 1 deraumere
- 1 sibur
- 0 mendiane
- 0 phiras
- 0 thystame

### Niveau 3 → 4
- 2 joueurs
- 2 linemate
- 0 deraumere
- 1 sibur
- 0 mendiane
- 2 phiras
- 0 thystame

### Niveau 4 → 5
- 4 joueurs
- 1 linemate
- 1 deraumere
- 2 sibur
- 0 mendiane
- 1 phiras
- 0 thystame

### Niveau 5 → 6
- 4 joueurs
- 1 linemate
- 2 deraumere
- 1 sibur
- 3 mendiane
- 0 phiras
- 0 thystame

### Niveau 6 → 7
- 6 joueurs
- 1 linemate
- 2 deraumere
- 3 sibur
- 1 mendiane
- 0 phiras
- 0 thystame

### Niveau 7 → 8
- 6 joueurs
- 2 linemate
- 2 deraumere
- 2 sibur
- 2 mendiane
- 2 phiras
- 1 thystame

## Fonctionnement du Rituel

1. **Démarrage du Rituel**
   - Un joueur initie l'incantation
   - Les conditions sont vérifiées (nombre de joueurs et ressources)
   - Si les conditions sont remplies, le rituel commence

2. **Pendant le Rituel**
   - Les joueurs sont gelés (ne peuvent pas effectuer d'autres actions)
   - Les conditions sont vérifiées en continu
   - Si les conditions ne sont plus remplies, le rituel échoue

3. **Fin du Rituel**
   - Les conditions sont vérifiées une dernière fois
   - Si les conditions sont toujours remplies, l'élévation réussit
   - Les pierres sont retirées de la case
   - Tous les joueurs participants montent de niveau

## Utilisation de la Classe ElevationManager

```python
# Initialisation
elevation_manager = ElevationManager(protocol, vision, movement)

# Vérifier les conditions d'élévation
if elevation_manager.check_elevation_conditions():
    # Démarrer le rituel
    if elevation_manager.start_ritual():
        # Vérifier le statut pendant le rituel
        while elevation_manager.check_ritual_status():
            # Attendre la fin du rituel
            pass
        
        # Terminer le rituel
        if elevation_manager.complete_ritual():
            print(f"Niveau actuel : {elevation_manager.get_current_level()}")
```

## Méthodes Principales

### `check_elevation_conditions()`
Vérifie si les conditions d'élévation sont remplies pour le niveau actuel.

### `start_ritual()`
Démarre le rituel d'élévation si les conditions sont remplies.

### `check_ritual_status()`
Vérifie si le rituel est toujours en cours et si les conditions sont toujours remplies.

### `complete_ritual()`
Termine le rituel et effectue l'élévation si les conditions sont toujours remplies.

### `get_current_level()`
Récupère le niveau actuel du joueur.

### `get_requirements()`
Récupère les conditions d'élévation pour le niveau actuel.

### `reset()`
Réinitialise l'état du gestionnaire d'élévation.

### `is_ritual_in_progress()`
Vérifie si un rituel est en cours.

## Notes Importantes

1. Les joueurs n'ont pas besoin d'être de la même équipe pour participer à un rituel
2. Tous les joueurs participants montent de niveau si le rituel réussit
3. Les pierres sont retirées de la case après un rituel réussi
4. Les joueurs sont gelés pendant toute la durée du rituel
5. Les conditions sont vérifiées au début et à la fin du rituel 