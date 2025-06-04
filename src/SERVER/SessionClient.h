/*
**  _                                              _      ___    ___  
** | |                                            | |    |__ \  / _ \
** | |_Created _       _ __   _ __    ___    __ _ | |__     ) || (_) |
** | '_ \ | | | |     | '_ \ | '_ \  / _ \  / _` || '_ \   / /  \__, |
** | |_) || |_| |     | | | || | | || (_) || (_| || | | | / /_    / / 
** |_.__/  \__, |     |_| |_||_| |_| \___/  \__,_||_| |_||____|  /_/ 
**          __/ |     on 02/06/25.                                          
**         |___/ 
*/


#ifndef SESSIONCLIENT_H
#define SESSIONCLIENT_H
#include <stdbool.h>
#include <time.h>
#include "Commandes.h"


typedef enum {
    FOOD,
    LINEMATE,
    DERAUMERE,
    SIBUR,
    MENDIANE,
    PHIRAS,
    THYSTAME
} Resource;

typedef enum
{
    NORTH,
    EAST,
    SOUTH,
    WEST
} Orientation;


typedef struct {
    int x;
    int y;
    int fd;
    int id;
    int level;
    bool active;
    bool is_gui;
    char *team_name;
    int orientation;
    int inventory[7];
    long last_food_tick;
    bool is_elevating;
    CommandQueue *queue;
} SessionClient;

#endif //SESSIONCLIENT_H
