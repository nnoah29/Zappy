/*
**  _                                              _      ___    ___  
** | |                                            | |    |__ \  / _ \
** | |_Created _       _ __   _ __    ___    __ _ | |__     ) || (_) |
** | '_ \ | | | |     | '_ \ | '_ \  / _ \  / _` || '_ \   / /  \__, |
** | |_) || |_| |     | | | || | | || (_) || (_| || | | | / /_    / / 
** |_.__/  \__, |     |_| |_||_| |_| \___/  \__,_||_| |_||____|  /_/ 
**          __/ |     on 18/06/25.                                          
**         |___/ 
*/


#include "map.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../my.h"

tile_t **map_create(int width, int height)
{
    tile_t **map = malloc(sizeof(tile_t *) * height);
    if (!map) exit_error("malloc map rows", 84);

    for (int y = 0; y < height; y++) {
        map[y] = malloc(sizeof(tile_t) * width);
        if (!map[y])
            exit_error("malloc map columns", 84);
        for (int x = 0; x < width; x++) {
            memset(map[y][x].resources, 0, sizeof(int) * NB_RESOURCES);
            map[y][x].entities = NULL;
        }
    }
    printf("Carte de %d x %d créée.\n", width, height);
    return map;
}

void map_destroy(tile_t **map, int width, int height)
{
    if (!map)
        return;
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            entity_on_tile_t *current = map[y][x].entities;
            while (current) {
                entity_on_tile_t *next = current->next;
                free(current);
                current = next;
            }
        }
        free(map[y]);
    }
    free(map);
    // TODO: implementer cette fonction
}

/**
 * @brief Ajoute une entité à une tuile de la carte
 * Cette fonction crée un nouveau nœud dans la liste chaînée des entités présentes
 * sur une tuile. L'entité est ajoutée en tête de liste.
 * @param tile   Pointeur vers la tuile où ajouter l'entité
 * @param entity Pointeur vers l'entité (session client) à ajouter
 * @note La fonction termine le programme avec un code d'erreur 84 si l'allocation
 *       mémoire échoue
 */
void map_add_entity(tile_t *tile, session_client_t *entity)
{
    entity_on_tile_t *new_node = malloc(sizeof(entity_on_tile_t));

    if (!new_node)
        exit_error("malloc new entity node", 84);
    new_node->entity = entity;
    new_node->next = tile->entities;
    tile->entities = new_node;
}

/**
 * @brief Détache une entité d'une tuile sans la supprimer
 * Cette fonction retire l'entité de la liste des entités présentes sur la tuile,
 * sans supprimer l'entité elle-même. Le nœud de la liste est libéré.
 * @param tile   Pointeur vers la tuile d'où détacher l'entité
 * @param entity Pointeur vers l'entité (session client) à détacher
 * @return 1 si l'entité a été trouvée et détachée, 0 sinon
 */
int map_detach_entity(tile_t *tile, session_client_t *entity)
{
    entity_on_tile_t *current = tile->entities;
    entity_on_tile_t *previous = NULL;

    while (current != NULL) {
        if (current->entity == entity) {
            if (previous == NULL)
                tile->entities = current->next;
            else
                previous->next = current->next;
            free(current);
            return 1;
        }
        previous = current;
        current = current->next;
    }
    return 0;
}

void map_move_entity(tile_t **map, session_client_t *entity, int new_x, int new_y)
{
    map_detach_entity(&map[entity->y][entity->x], entity);
    entity->x = new_x;
    entity->y = new_y;
    map_add_entity(&map[entity->y][entity->x], entity);
}

void map_spawn_resources(server_t *server)
{
    const double densities[] = {0.5, 0.3, 0.15, 0.1, 0.1, 0.08, 0.05};
    const int map_size = server->config->map_w * server->config->map_h;
    int quantity_to_spawn = 0;
    int x = 0;
    int y = 0;

    for (int res_idx = 0; res_idx < NB_RESOURCES; res_idx++) {
        quantity_to_spawn = map_size * densities[res_idx];
        for (int i = 0; i < quantity_to_spawn; i++) {
            x = (int)random() % server->config->map_w;
            y = (int)random() % server->config->map_h;
            server->map[y][x].resources[res_idx]++;
        }
    }
    printf("Ressources ont été générées sur la carte.\n");
    // TODO: Notifier le GUI de tous les changements avec bct !
}