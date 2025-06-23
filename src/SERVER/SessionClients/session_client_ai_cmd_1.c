/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.c
*/

#include "session_client.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void forward_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    int x = client->x;
    int y = client->y;

    switch (client->orientation) {
    case NORTH:
        y = (y - 1 + server->config->map_h) % server->config->map_h;
        break;
    case EAST:
        x = (x + 1) % server->config->map_w;
        break;
    case SOUTH:
        y = (y + 1) % server->config->map_h;
        break;
    case WEST:
        x = (x - 1 + server->config->map_w) % server->config->map_w;
        break;
    }
    map_move_entity(server->map, client, x, y);
    ppo_f(server, client);
    (void)cmd;
}

void right_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    client->orientation = (client->orientation + 1) % 4;
    ppo_f(server, client);
    printf("right\n");
    (void)cmd;
}

void left_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    client->orientation = (client->orientation - 1 + 4) % 4;
    ppo_f(server, client);
    printf("left\n");
    (void)cmd;
}

void look_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    char *response = calloc(4096, sizeof(char));
    char tile_buffer[512] = {0};
    int_pair_t rel = {0, 0};

    response[0] = '[';
    for (int forward = 0; forward <= client->level; forward++) {
        for (int side = -forward; side <= forward; side++) {
            rel.x = side;
            rel.y = forward;
            add_semicolon(response, side, forward);
            memset(tile_buffer, 0, 512);
            get_tile_content(server, client, rel, tile_buffer);
            strcat(response, tile_buffer);
        }
    }
    strcat(response, "]\n\0");
    send(client->fd, response, strlen(response), 0);
    printf("look\n");
    free(response);
    (void)cmd;
}

void inventory_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    (void)server;
    (void)cmd;
    dprintf(client->fd, "[food %d, linemate %d, deraumere %d, sibur %d, "
        "mendiane %d, phiras %d, thystame %d]\n",
        client->inventory[FOOD], client->inventory[LINEMATE],
        client->inventory[DERAUMERE], client->inventory[SIBUR],
        client->inventory[MENDIANE], client->inventory[PHIRAS],
        client->inventory[THYSTAME]);
    printf("inventory\n");
}
