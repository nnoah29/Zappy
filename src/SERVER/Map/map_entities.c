/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** map_entities.c
*/

#include <stdio.h>
#include <stdlib.h>
#include "map.h"
#include "../my.h" // Pour exit_error

/// Retire un maillon de la liste chaînée d'entités sur une tuile.
static int unlink_entity_from_tile(entity_on_tile_t *current,
    entity_on_tile_t *previous, tile_t *tile)
{
    if (previous == NULL)
        tile->entities = current->next;
    else
        previous->next = current->next;
    free(current);
    return 1;
}

/// Ajoute une entité à une tuile de la carte
void map_add_entity(tile_t *tile, session_client_t *entity)
{
    entity_on_tile_t *new_node = malloc(sizeof(entity_on_tile_t));

    if (!new_node)
        exit_error("malloc new entity node", 84);
    new_node->entity = entity;
    new_node->next = tile->entities;
    tile->entities = new_node;
}

/// Détache une entité d'une tuile sans la supprimer
int map_detach_entity(tile_t *tile, session_client_t *entity)
{
    entity_on_tile_t *current = tile->entities;
    entity_on_tile_t *previous = NULL;

    while (current != NULL) {
        if (current->entity == entity)
            return unlink_entity_from_tile(current, previous, tile);
        previous = current;
        current = current->next;
    }
    return 0;
}

/// Déplacer une entité sur la map
void map_move_entity(tile_t **map, session_client_t *entity,
    int new_x, int new_y)
{
    map_detach_entity(&map[entity->y][entity->x], entity);
    entity->x = new_x;
    entity->y = new_y;
    map_add_entity(&map[entity->y][entity->x], entity);
}
