/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.h
*/

#ifndef SESSIONCLIENT_H
    #define SESSIONCLIENT_H
    #include <stdbool.h>
    #include <time.h>
    #include "../Commandes/commandes.h"

typedef enum {
    FOOD,
    LINEMATE,
    DERAUMERE,
    SIBUR,
    MENDIANE,
    PHIRAS,
    THYSTAME
} resource_t;

typedef enum {
    NORTH,
    EAST,
    SOUTH,
    WEST
} orientation_t;

typedef struct {
    int x;
    int y;
    int fd;
    int id;
    int level;
    bool active;
    bool is_gui;
    bool is_egg;
    int team_idx;
    int orientation;
    int inventory[7];
    long last_food_tick;
    bool is_elevating;
    command_queue_t *queue;
} session_client_t;

#endif //SESSIONCLIENT_H
