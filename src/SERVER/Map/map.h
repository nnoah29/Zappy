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


#ifndef MAP_H
    #define MAP_H
    #define NB_RESOURCES 7

typedef struct session_client_s session_client_t;
typedef struct server server_t;

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

// Structure d'une tuile
typedef struct tile_s {
    int resources[NB_RESOURCES];
    entity_on_tile_t *entities;
} tile_t;

tile_t **map_create(int width, int height);
void map_spawn_resources(server_t *server);
void map_move_entity(tile_t **map, session_client_t *entity, int new_x, int new_y);
void map_add_entity(tile_t *tile, session_client_t *entity);
int map_detach_entity(tile_t *tile, session_client_t *entity);

#endif //MAP_H
