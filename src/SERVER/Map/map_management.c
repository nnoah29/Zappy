/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** map_management.c
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "map.h"
#include "../my.h"

// Libère la mémoire d'une liste chaînée d'entités
static void free_entity_list(entity_on_tile_t *current)
{
    entity_on_tile_t *next = NULL;

    while (current) {
        next = current->next;
        free(current);
        current = next;
    }
}

// Créer une map dans le jeux
tile_t **map_create(int width, int height)
{
    tile_t **map = malloc(sizeof(tile_t *) * height);

    LOG(LOG_INFO, "Configuration de la map...");
    if (!map)
        exit_error("malloc map rows", 84);
    for (int y = 0; y < height; y++) {
        map[y] = malloc(sizeof(tile_t) * width);
        if (!map[y])
            exit_error("malloc map columns", 84);
        for (int x = 0; x < width; x++) {
            memset(map[y][x].resources, 0, sizeof(int) * NB_RESOURCES);
            map[y][x].entities = NULL;
        }
    }
    LOG(LOG_INFO, "Map de dimensions %d x %d créée.", width, height);
    return map;
}

/// Détruire la map
void map_destroy(tile_t **map, int width, int height)
{
    if (!map)
        return;
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            free_entity_list(map[y][x].entities);
        }
        free(map[y]);
    }
    free(map);
}

/// Repartager les ressources sur la Map
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
    LOG(LOG_DEBUG, "Ressources ont été générées sur la carte.");
    mct_f(server);
}
