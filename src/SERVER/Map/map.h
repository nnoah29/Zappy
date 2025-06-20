/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** map.h
*/

#ifndef MAP_H
    #define MAP_H
    #define NB_RESOURCES 7

// Déclarations anticipées pour éviter les dépendances circulaires
typedef struct session_client_s session_client_t;
typedef struct server server_t;
typedef struct configServer config_server_t;

// Énumérations et Structures
typedef enum {
    FOOD,
    LINEMATE,
    DERAUMERE,
    SIBUR,
    MENDIANE,
    PHIRAS,
    THYSTAME
} resource_t;

typedef struct entity_on_tile_s {
    session_client_t *entity;
    struct entity_on_tile_s *next;
} entity_on_tile_t;

typedef struct tile_s {
    int resources[NB_RESOURCES];
    entity_on_tile_t *entities;
} tile_t;


// --- Fonctions de map_management.c ---
tile_t **map_create(int width, int height);
void map_destroy(tile_t **map, int width, int height);
void map_spawn_resources(server_t *server);


// --- Fonctions de map_entities.c ---
void map_add_entity(tile_t *tile, session_client_t *entity);
int map_detach_entity(tile_t *tile, session_client_t *entity);
void map_move_entity(tile_t **map, session_client_t *entity,
    int new_x, int new_y);


#endif //MAP_H
